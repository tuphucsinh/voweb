import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const DEFAULT_PORT = 8787;
const DEFAULT_HOST = '0.0.0.0';
const DEFAULT_TRUSTED_HOSTS = ['vorigin.vn', 'www.vorigin.vn', 'localhost'];
const MAX_BODY = 32 * 1024;
const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_LIMIT = 5;
const BUCKET_CLEANUP_INTERVAL_MS = 60 * 1000;

const clean = (v, max = 500) => String(v ?? '').trim().replace(/[\u0000-\u001F\u007F]/g, ' ').slice(0, max);
const validEmail = v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) && v.length <= 160;
const validUrl = v => !v || /^https?:\/\/[A-Za-z0-9.-]+(?::\d+)?(?:[/?#].*)?$/.test(v);

function json(res, status, body) {
  const text = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(text),
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff'
  });
  res.end(text);
}

function safeSinkError(error) {
  const code = error?.code;
  return typeof code === 'string' && /^optional_sink_http_[0-9]{3}$/.test(code) ? code : 'request_failed';
}

export async function postOptionalSink(url, payload, options = {}) {
  const fetchImpl = options.fetch ?? fetch;
  const response = await fetchImpl(url, {
    method: 'POST',
    headers: options.headers ?? { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal: options.signal ?? AbortSignal.timeout(options.timeoutMs ?? 6000)
  });
  if (!response.ok) {
    const error = new Error(`optional sink returned HTTP ${response.status}`);
    error.code = `optional_sink_http_${response.status}`;
    throw error;
  }
  return response;
}

export function createLeadServer(config = {}, deps = {}) {
  const fetchImpl = deps.fetch ?? fetch;
  const fsImpl = deps.fs ?? fs;
  const now = deps.now ?? (() => Date.now());
  const randomUUID = deps.randomUUID ?? (() => crypto.randomUUID());
  const port = Number(config.port ?? DEFAULT_PORT);
  const host = config.host ?? DEFAULT_HOST;
  const turnstileSecretKey = config.turnstileSecretKey ?? '';
  const directusUrl = String(config.directusUrl ?? '').replace(/\/$/, '');
  const directusToken = config.directusToken ?? '';
  const leadWebhookUrl = config.leadWebhookUrl ?? '';
  const leadStore = config.leadStore ?? '/data/leads.ndjson';
  const trustedHosts = new Set(config.trustedHosts ?? DEFAULT_TRUSTED_HOSTS);
  const maxBody = Number(config.maxBody ?? MAX_BODY);
  const rateWindowMs = Number(config.rateWindowMs ?? RATE_WINDOW_MS);
  const rateLimit = Number(config.rateLimit ?? RATE_LIMIT);
  const buckets = new Map();
  let lastBucketCleanup = 0;

  function cleanupBuckets(timestamp) {
    if (timestamp - lastBucketCleanup < BUCKET_CLEANUP_INTERVAL_MS) return;
    for (const [ip, entries] of buckets) {
      const live = entries.filter(entry => timestamp - entry < rateWindowMs);
      if (live.length) buckets.set(ip, live);
      else buckets.delete(ip);
    }
    lastBucketCleanup = timestamp;
  }

  function rateOK(ip) {
    const timestamp = now();
    cleanupBuckets(timestamp);
    const entries = (buckets.get(ip) ?? []).filter(entry => timestamp - entry < rateWindowMs);
    if (entries.length >= rateLimit) {
      buckets.set(ip, entries);
      return false;
    }
    entries.push(timestamp);
    buckets.set(ip, entries);
    return true;
  }

  function ipOf(req) {
    return clean(req.headers['cf-connecting-ip'] || req.socket.remoteAddress || 'unknown', 80);
  }

  async function verifyTurnstile(token, ip) {
    if (!turnstileSecretKey) return { success: false, reason: 'turnstile_not_configured' };
    const body = new URLSearchParams({ secret: turnstileSecretKey, response: token || '', remoteip: ip });
    const response = await fetchImpl('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      body,
      signal: AbortSignal.timeout(8000)
    });
    if (!response.ok) return { success: false, reason: 'siteverify_http' };
    const data = await response.json();
    return { success: Boolean(data.success), reason: data['error-codes'] || null, hostname: data.hostname || null };
  }

  async function persistLead(lead) {
    await fsImpl.mkdir(path.dirname(leadStore), { recursive: true });
    await fsImpl.appendFile(leadStore, JSON.stringify(lead) + '\n', { encoding: 'utf8', mode: 0o600 });
    if (directusUrl && directusToken) {
      try {
        await postOptionalSink(`${directusUrl}/items/leads`, lead, {
          fetch: fetchImpl,
          headers: { Authorization: `Bearer ${directusToken}`, 'Content-Type': 'application/json' }
        });
      } catch (error) {
        console.error('directus lead sync failed', safeSinkError(error));
      }
    }
    if (leadWebhookUrl) {
      try {
        await postOptionalSink(leadWebhookUrl, lead, { fetch: fetchImpl });
      } catch (error) {
        console.error('lead webhook failed', safeSinkError(error));
      }
    }
  }

  const server = http.createServer(async (req, res) => {
    if (req.url === '/healthz' && req.method === 'GET') return json(res, 200, { ok: true });
    if (req.url !== '/api/lead' || req.method !== 'POST') return json(res, 404, { error: 'not_found' });

    const hostHeader = clean((req.headers.host || '').split(':')[0], 180).toLowerCase();
    if (!trustedHosts.has(hostHeader)) return json(res, 403, { error: 'forbidden' });
    if (!(req.headers['content-type'] || '').toLowerCase().startsWith('application/json')) return json(res, 415, { error: 'json_required' });

    const ip = ipOf(req);
    if (!rateOK(ip)) return json(res, 429, { error: 'rate_limited' });

    let raw = '';
    try {
      for await (const chunk of req) {
        raw += chunk;
        if (Buffer.byteLength(raw) > maxBody) return json(res, 413, { error: 'body_too_large' });
      }
    } catch {
      return json(res, 400, { error: 'body_read_failed' });
    }

    let data;
    try { data = JSON.parse(raw); } catch { return json(res, 400, { error: 'invalid_json' }); }
    if (clean(data.website_confirmation, 80)) return json(res, 200, { ok: true });

    const lead = {
      id: randomUUID(),
      created_at: new Date(now()).toISOString(),
      form_type: clean(data.form_type, 40) || 'contact',
      name: clean(data.name, 120),
      email: clean(data.email, 160).toLowerCase(),
      company: clean(data.company, 160),
      country: clean(data.country, 100),
      website: clean(data.website, 240),
      inquiry_type: clean(data.inquiry_type, 60),
      message: clean(data.message, 4000),
      source_path: clean(req.headers.referer || '', 500),
      ip_hash: crypto.createHash('sha256').update(ip + (config.ipHashSalt ?? 'change-me')).digest('hex').slice(0, 24)
    };

    if (lead.name.length < 2 || !validEmail(lead.email) || lead.message.length < 10 || !validUrl(lead.website)) {
      return json(res, 422, { error: 'invalid_fields' });
    }

    let verify;
    try { verify = await verifyTurnstile(clean(data['cf-turnstile-response'], 4096), ip); }
    catch { return json(res, 503, { error: 'verification_unavailable' }); }
    if (!verify.success) return json(res, 403, { error: 'verification_failed' });

    try { await persistLead(lead); }
    catch (error) { console.error('lead persist failed', error?.code || 'storage_error'); return json(res, 503, { error: 'storage_unavailable' }); }
    return json(res, 201, { ok: true, reference: lead.id.slice(0, 8) });
  });

  server.requestTimeout = 12000;
  server.headersTimeout = 8000;
  server.listenConfig = { port, host };
  return server;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const server = createLeadServer({
    port: process.env.PORT,
    host: process.env.HOST,
    turnstileSecretKey: process.env.TURNSTILE_SECRET_KEY,
    directusUrl: process.env.DIRECTUS_URL,
    directusToken: process.env.DIRECTUS_TOKEN,
    leadWebhookUrl: process.env.LEAD_WEBHOOK_URL,
    leadStore: process.env.LEAD_STORE,
    trustedHosts: (process.env.TRUSTED_HOSTS || DEFAULT_TRUSTED_HOSTS.join(',')).split(',').map(value => value.trim()).filter(Boolean),
    ipHashSalt: process.env.IP_HASH_SALT
  });
  const { port, host } = server.listenConfig;
  server.listen(port, host);
  server.on('listening', () => console.log(`VOrigin lead API listening on ${host}:${port}`));
}
