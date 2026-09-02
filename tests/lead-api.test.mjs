import test from 'node:test';
import assert from 'node:assert/strict';
import { createLeadServer, postOptionalSink } from '../services/lead-api/server.mjs';

function makeFetch() {
  const state = { turnstile: 'success', sinkStatus: 202, calls: [] };
  const fetchImpl = async (url, options = {}) => {
    state.calls.push({ url, options });
    if (url.includes('challenges.cloudflare.com')) {
      if (state.turnstile === 'throw') throw new Error('network');
      return { ok: true, status: 200, json: async () => ({ success: state.turnstile === 'success' }) };
    }
    return { ok: state.sinkStatus >= 200 && state.sinkStatus < 300, status: state.sinkStatus, json: async () => ({}) };
  };
  return { fetchImpl, state };
}

async function start(config = {}) {
  const persisted = [];
  const fetchState = makeFetch();
  const server = createLeadServer({
    host: '127.0.0.1',
    port: 0,
    trustedHosts: ['localhost', '127.0.0.1'],
    turnstileSecretKey: 'test-only',
    leadStore: '/tmp/test-leads.ndjson',
    ...config
  }, {
    fetch: fetchState.fetchImpl,
    fs: { mkdir: async () => {}, appendFile: async (_file, line) => persisted.push(JSON.parse(line)) },
    randomUUID: () => '12345678-1234-4123-8123-123456789abc',
    now: () => Date.UTC(2026, 7, 31, 1, 2, 3)
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  return { server, url: `http://127.0.0.1:${address.port}`, persisted, ...fetchState };
}

async function stop(server) {
  await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
}

function headers(ip = '192.0.2.10', contentType = 'application/json') {
  return { host: 'localhost', 'content-type': contentType, 'cf-connecting-ip': ip };
}

function validPayload(extra = {}) {
  return {
    name: 'Nguyen Van A',
    email: 'a@example.com',
    company: 'Example Co',
    message: 'We would like to discuss a distribution partnership.',
    'cf-turnstile-response': 'test-token',
    ...extra
  };
}

test('health and request guards are explicit', async t => {
  const ctx = await start();
  t.after(() => stop(ctx.server));
  const health = await fetch(`${ctx.url}/healthz`);
  assert.equal(health.status, 200);
  assert.deepEqual(await health.json(), { ok: true });

  const blocked = await start({ trustedHosts: ['other.example'] });
  t.after(() => stop(blocked.server));
  const forbidden = await fetch(`${blocked.url}/api/lead`, { method: 'POST', headers: headers(), body: '{}' });
  assert.equal(forbidden.status, 403);
  const wrongType = await fetch(`${ctx.url}/api/lead`, { method: 'POST', headers: headers('192.0.2.11', 'text/plain'), body: '{}' });
  assert.equal(wrongType.status, 415);
});

test('valid lead is persisted locally even when optional sinks return non-2xx', async t => {
  const ctx = await start({ directusUrl: 'https://directus.example', directusToken: 'token-not-real', leadWebhookUrl: 'https://hooks.example' });
  t.after(() => stop(ctx.server));
  ctx.state.sinkStatus = 503;
  const response = await fetch(`${ctx.url}/api/lead`, { method: 'POST', headers: { ...headers(), referer: 'https://vorigin.vn/en/contact/' }, body: JSON.stringify(validPayload()) });
  assert.equal(response.status, 201);
  assert.deepEqual(await response.json(), { ok: true, reference: '12345678' });
  assert.equal(ctx.persisted.length, 1);
  assert.equal(ctx.persisted[0].email, 'a@example.com');
  assert.equal(ctx.persisted[0].source_path, 'https://vorigin.vn/en/contact/');
  assert.equal(ctx.state.calls.filter(call => call.url.includes('siteverify')).length, 1);
});

test('invalid fields, failed verification, and unavailable verification fail closed', async t => {
  const ctx = await start();
  t.after(() => stop(ctx.server));
  let response = await fetch(`${ctx.url}/api/lead`, { method: 'POST', headers: headers(), body: JSON.stringify(validPayload({ email: 'bad', message: 'short' })) });
  assert.equal(response.status, 422);

  ctx.state.turnstile = 'failed';
  response = await fetch(`${ctx.url}/api/lead`, { method: 'POST', headers: headers('192.0.2.12'), body: JSON.stringify(validPayload()) });
  assert.equal(response.status, 403);

  ctx.state.turnstile = 'throw';
  response = await fetch(`${ctx.url}/api/lead`, { method: 'POST', headers: headers('192.0.2.13'), body: JSON.stringify(validPayload()) });
  assert.equal(response.status, 503);
  assert.equal(ctx.persisted.length, 0);
});

test('body size and rate limits are enforced', async t => {
  const ctx = await start({ maxBody: 128, rateLimit: 2 });
  t.after(() => stop(ctx.server));
  let response = await fetch(`${ctx.url}/api/lead`, { method: 'POST', headers: headers('192.0.2.20'), body: JSON.stringify({ message: 'x'.repeat(300) }) });
  assert.equal(response.status, 413);
  response = await fetch(`${ctx.url}/api/lead`, { method: 'POST', headers: headers('192.0.2.21'), body: '{}' });
  assert.equal(response.status, 422);
  response = await fetch(`${ctx.url}/api/lead`, { method: 'POST', headers: headers('192.0.2.21'), body: '{}' });
  assert.equal(response.status, 422);
  response = await fetch(`${ctx.url}/api/lead`, { method: 'POST', headers: headers('192.0.2.21'), body: '{}' });
  assert.equal(response.status, 429);
});

test('optional sink helper rejects non-2xx without exposing payload', async () => {
  await assert.rejects(
    () => postOptionalSink('https://sink.example', { email: 'redacted-in-test@example.com' }, { fetch: async () => ({ ok: false, status: 502 }) }),
    error => error.code === 'optional_sink_http_502'
  );
});
