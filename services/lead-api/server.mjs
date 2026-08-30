import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

const PORT = Number(process.env.PORT || 8787);
const HOST = process.env.HOST || '0.0.0.0';
const TURNSTILE_SECRET_KEY = process.env.TURNSTILE_SECRET_KEY || '';
const DIRECTUS_URL = (process.env.DIRECTUS_URL || '').replace(/\/$/,'');
const DIRECTUS_TOKEN = process.env.DIRECTUS_TOKEN || '';
const LEAD_WEBHOOK_URL = process.env.LEAD_WEBHOOK_URL || '';
const LEAD_STORE = process.env.LEAD_STORE || '/data/leads.ndjson';
const TRUSTED_HOSTS = new Set((process.env.TRUSTED_HOSTS || 'vorigin.vn,www.vorigin.vn,localhost').split(',').map(s=>s.trim()).filter(Boolean));
const MAX_BODY = 32 * 1024;
const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_LIMIT = 5;
const buckets = new Map();

const clean = (v, max=500) => String(v ?? '').trim().replace(/[\u0000-\u001F\u007F]/g,' ').slice(0,max);
const validEmail = v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) && v.length <= 160;
const validUrl = v => !v || /^https?:\/\/[A-Za-z0-9.-]+(?::\d+)?(?:[/?#].*)?$/.test(v);

function json(res, status, body) {
  const text = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type':'application/json; charset=utf-8',
    'Content-Length':Buffer.byteLength(text),
    'Cache-Control':'no-store',
    'X-Content-Type-Options':'nosniff'
  });
  res.end(text);
}

function ipOf(req) {
  return clean(req.headers['cf-connecting-ip'] || req.socket.remoteAddress || 'unknown', 80);
}

function rateOK(ip) {
  const now = Date.now();
  const arr = (buckets.get(ip) || []).filter(ts => now-ts < RATE_WINDOW_MS);
  if (arr.length >= RATE_LIMIT) { buckets.set(ip, arr); return false; }
  arr.push(now); buckets.set(ip, arr); return true;
}

async function verifyTurnstile(token, ip) {
  if (!TURNSTILE_SECRET_KEY) return { success:false, reason:'turnstile_not_configured' };
  const body = new URLSearchParams({ secret:TURNSTILE_SECRET_KEY, response:token || '', remoteip:ip });
  const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {method:'POST', body, signal:AbortSignal.timeout(8000)});
  if (!r.ok) return {success:false, reason:'siteverify_http'};
  const data = await r.json();
  return {success:Boolean(data.success), reason:data['error-codes'] || null, hostname:data.hostname || null};
}

async function persistLead(lead) {
  await fs.mkdir(path.dirname(LEAD_STORE), {recursive:true});
  await fs.appendFile(LEAD_STORE, JSON.stringify(lead)+'\n', {encoding:'utf8', mode:0o600});
  if (DIRECTUS_URL && DIRECTUS_TOKEN) {
    try {
      await fetch(`${DIRECTUS_URL}/items/leads`, {method:'POST', headers:{'Authorization':`Bearer ${DIRECTUS_TOKEN}`,'Content-Type':'application/json'}, body:JSON.stringify(lead), signal:AbortSignal.timeout(6000)});
    } catch (e) { console.error('directus lead sync failed', e.message); }
  }
  if (LEAD_WEBHOOK_URL) {
    try {
      await fetch(LEAD_WEBHOOK_URL, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(lead), signal:AbortSignal.timeout(6000)});
    } catch (e) { console.error('lead webhook failed', e.message); }
  }
}

const server = http.createServer(async (req,res) => {
  if (req.url === '/healthz' && req.method === 'GET') return json(res,200,{ok:true});
  if (req.url !== '/api/lead' || req.method !== 'POST') return json(res,404,{error:'not_found'});

  const host = clean((req.headers.host || '').split(':')[0], 180).toLowerCase();
  if (!TRUSTED_HOSTS.has(host)) return json(res,403,{error:'forbidden'});
  if (!(req.headers['content-type'] || '').toLowerCase().startsWith('application/json')) return json(res,415,{error:'json_required'});

  const ip = ipOf(req);
  if (!rateOK(ip)) return json(res,429,{error:'rate_limited'});

  let raw='';
  try {
    for await (const chunk of req) {
      raw += chunk;
      if (Buffer.byteLength(raw) > MAX_BODY) { req.destroy(); return; }
    }
  } catch { return; }

  let data;
  try { data = JSON.parse(raw); } catch { return json(res,400,{error:'invalid_json'}); }
  if (clean(data.website_confirmation,80)) return json(res,200,{ok:true}); // honeypot: silent success

  const lead = {
    id: crypto.randomUUID(),
    created_at: new Date().toISOString(),
    form_type: clean(data.form_type,40) || 'contact',
    name: clean(data.name,120),
    email: clean(data.email,160).toLowerCase(),
    company: clean(data.company,160),
    country: clean(data.country,100),
    website: clean(data.website,240),
    inquiry_type: clean(data.inquiry_type,60),
    message: clean(data.message,4000),
    source_path: clean(req.headers.referer || '',500),
    ip_hash: crypto.createHash('sha256').update(ip + (process.env.IP_HASH_SALT || 'change-me')).digest('hex').slice(0,24)
  };

  if (lead.name.length < 2 || !validEmail(lead.email) || lead.message.length < 10 || !validUrl(lead.website)) return json(res,422,{error:'invalid_fields'});

  const token = clean(data['cf-turnstile-response'], 4096);
  let verify;
  try { verify = await verifyTurnstile(token, ip); } catch { return json(res,503,{error:'verification_unavailable'}); }
  if (!verify.success) return json(res,403,{error:'verification_failed'});

  try { await persistLead(lead); } catch (e) { console.error('lead persist failed', e); return json(res,503,{error:'storage_unavailable'}); }
  return json(res,201,{ok:true, reference:lead.id.slice(0,8)});
});

server.requestTimeout = 12000;
server.headersTimeout = 8000;
server.listen(PORT,HOST,()=>console.log(`VOrigin lead API listening on ${HOST}:${PORT}`));
