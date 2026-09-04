#!/usr/bin/env node
import fs from 'node:fs/promises';
import http from 'node:http';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import {spawn} from 'node:child_process';

const args = new Map();
for (let i = 2; i < process.argv.length; i += 1) {
  const value = process.argv[i];
  if (value.startsWith('--')) args.set(value, process.argv[i + 1]);
}
const base = (args.get('--base-url') || 'http://127.0.0.1:8080').replace(/\/$/, '');
const evidence = args.get('--evidence-dir') || '/home/pi5/hermes-artifacts/browser-evidence/VOweb/browser-matrix';
const routes = [
  ['vi-home', '/vi/', 'vi', null], ['en-home', '/en/', 'en', null],
  ['vi-about', '/vi/gioi-thieu/', 'vi', '/vi/gioi-thieu/'], ['en-about', '/en/about/', 'en', '/en/about/'],
  ['vi-brands', '/vi/thuong-hieu/', 'vi', '/vi/thuong-hieu/'], ['en-brands', '/en/brands/', 'en', '/en/brands/'],
  ['vi-marigold', '/vi/thuong-hieu/marigold/', 'vi', '/vi/thuong-hieu/'], ['en-marigold', '/en/brands/marigold/', 'en', '/en/brands/'],
  ['vi-product', '/vi/san-pham/marigold-orange/', 'vi', '/vi/thuong-hieu/'], ['en-product', '/en/products/marigold-orange/', 'en', '/en/brands/'],
  ['vi-capabilities', '/vi/nang-luc/', 'vi', '/vi/nang-luc/'], ['en-capabilities', '/en/capabilities/', 'en', '/en/capabilities/'],
  ['vi-partners', '/vi/doi-tac/', 'vi', '/vi/doi-tac/'], ['en-partners', '/en/partners/', 'en', '/en/partners/'],
  ['vi-insights', '/vi/goc-nhin/', 'vi', '/vi/goc-nhin/'], ['en-insights', '/en/insights/', 'en', '/en/insights/'],
  ['vi-contact', '/vi/lien-he/', 'vi', '/vi/lien-he/'], ['en-contact', '/en/contact/', 'en', '/en/contact/'],
];
const routeStart = Number(args.get('--route-start') || 0);
const routeEnd = Number(args.get('--route-end') || routes.length);
const selectedRoutes = routes.slice(routeStart, routeEnd);
const allViewports = [[390, 844], [430, 900], [768, 1024], [1024, 900], [1440, 900], [1920, 1080]];
const requestedViewportWidths = args.get('--viewports')?.split(',').map(value => Number(value)).filter(Number.isFinite);
const viewports = requestedViewportWidths?.length
  ? allViewports.filter(([width]) => requestedViewportWidths.includes(width))
  : allViewports;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const isKnownExternalCspWarning = message => message.includes('https://static.cloudflareinsights.com/beacon.min.js/') && message.includes('Content Security Policy directive');

function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
  });
}

async function jsonGet(url) {
  return new Promise((resolve, reject) => {
    http.get(url, response => {
      let data = '';
      response.setEncoding('utf8');
      response.on('data', chunk => { data += chunk; });
      response.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (error) { reject(error); }
      });
    }).on('error', reject);
  });
}

async function waitForTarget(port) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    try {
      const targets = await jsonGet(`http://127.0.0.1:${port}/json/list`);
      const target = targets.find(item => item.type === 'page');
      if (target) return target;
    } catch {}
    await sleep(150);
  }
  throw new Error('Chrome CDP target did not become ready');
}

class CdpClient {
  constructor(url) {
    this.ws = new WebSocket(url);
    this.nextId = 0;
    this.pending = new Map();
    this.events = new Map();
    this.ready = new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });
    this.ws.onmessage = event => {
      const message = JSON.parse(event.data);
      if (message.id && this.pending.has(message.id)) {
        const {resolve, reject, timer} = this.pending.get(message.id);
        clearTimeout(timer);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(message.error.message));
        else resolve(message.result || {});
      } else if (message.method) {
        for (const handler of this.events.get(message.method) || []) handler(message.params || {});
      }
    };
  }
  on(method, handler) {
    const handlers = this.events.get(method) || [];
    handlers.push(handler);
    this.events.set(method, handlers);
  }
  async send(method, params = {}) {
    await this.ready;
    const id = ++this.nextId;
    return new Promise((resolve, reject) => {
      const timeoutMs = method === 'Runtime.evaluate' ? 45000 : 15000;
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`CDP timeout: ${method}`));
      }, timeoutMs);
      this.pending.set(id, {resolve, reject, timer});
      this.ws.send(JSON.stringify({id, method, params}));
    });
  }
  close() { this.ws.close(); }
}

async function evaluate(cdp, expression) {
  const result = await cdp.send('Runtime.evaluate', {expression, awaitPromise: true, returnByValue: true});
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'Runtime evaluation failed');
  return result.result?.value;
}

const chromePort = await freePort();
const profile = await fs.mkdtemp(path.join(os.tmpdir(), 'voweb-browser-matrix-'));
const chrome = spawn('/usr/bin/google-chrome-stable', [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--remote-allow-origins=*',
  `--remote-debugging-port=${chromePort}`, `--user-data-dir=${profile}`, 'about:blank',
], {stdio: ['ignore', 'ignore', 'pipe']});
let chromeStderr = '';
chrome.stderr.on('data', chunk => { chromeStderr += chunk.toString(); });
const results = [];
let cdp;
try {
  const target = await waitForTarget(chromePort);
  cdp = new CdpClient(target.webSocketDebuggerUrl);
  await cdp.send('Runtime.enable');
  await cdp.send('Page.enable');
  await cdp.send('Network.enable');
  await cdp.send('Log.enable');
  const runtimeErrors = [];
  const networkFailures = [];
  const networkBadResponses = [];
  const requestUrls = new Map();
  cdp.on('Runtime.exceptionThrown', params => runtimeErrors.push(params.exceptionDetails?.text || 'Runtime exception'));
  cdp.on('Runtime.consoleAPICalled', params => {
    if (params.type === 'error') runtimeErrors.push('console.error');
  });
  cdp.on('Log.entryAdded', params => {
    if (params.entry?.level === 'error') runtimeErrors.push(params.entry.text || 'browser log error');
  });
  cdp.on('Network.requestWillBeSent', params => {
    requestUrls.set(params.requestId, params.request?.url || '');
  });
  cdp.on('Network.loadingFailed', params => {
    const url = requestUrls.get(params.requestId) || '';
    if (url.startsWith(base) && params.errorText && params.type !== 'Other') networkFailures.push(`${params.type}: ${params.errorText}: ${url}`);
  });
  cdp.on('Network.responseReceived', params => {
    const url = params.response?.url || '';
    if (url.startsWith(base) && params.response.status >= 400) networkBadResponses.push(`${params.response.status}: ${url}`);
  });

  for (const [name, route, locale, activeHref] of selectedRoutes) {
    for (const [width, height] of viewports) {
      runtimeErrors.length = 0;
      networkFailures.length = 0;
      networkBadResponses.length = 0;
      requestUrls.clear();
      await cdp.send('Emulation.setDeviceMetricsOverride', {width, height, deviceScaleFactor: 1, mobile: false});
      await cdp.send('Emulation.setEmulatedMedia', {features: []});
      await cdp.send('Page.navigate', {url: `${base}${route}`});
      await sleep(900);
      const state = await evaluate(cdp, `(async () => {
        const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
        for (const image of document.images) image.loading = 'eager';
        for (let y = 0; y <= Math.max(0, document.body.scrollHeight - innerHeight); y += Math.max(1, innerHeight)) {
          window.scrollTo(0, y);
          await wait(70);
        }
        window.scrollTo(0, Math.max(0, document.body.scrollHeight - innerHeight));
        await wait(500);
        const isFirstPartyUrl = value => {
          try { return new URL(value, location.href).origin === location.origin; }
          catch { return false; }
        };
        const localImages = [...document.images].filter(image => isFirstPartyUrl(image.currentSrc || image.src));
        const imageRecords = localImages.map(image => {
          const rect = image.getBoundingClientRect();
          const currentSrc = image.currentSrc || image.src;
          const candidate = currentSrc.match(/-(\\d+)w\\.webp(?:$|[?#])/);
          return {
            src: image.getAttribute('src'),
            currentSrc,
            renderedWidth: Math.round(rect.width),
            renderedHeight: Math.round(rect.height),
            naturalWidth: image.naturalWidth,
            naturalHeight: image.naturalHeight,
            devicePixelRatio,
            candidateWidth: candidate ? Number(candidate[1]) : null,
          };
        });
        const fidelityFailures = imageRecords.filter(image => {
          const deliveredWidth = image.candidateWidth ?? image.naturalWidth;
          return image.renderedWidth > 0 && deliveredWidth > 0 && deliveredWidth + 1 < image.renderedWidth * devicePixelRatio * 0.9;
        });
        const rectRight = Math.max(document.documentElement.clientWidth, ...[...document.querySelectorAll('*')].map(node => {
          const rect = node.getBoundingClientRect();
          return Number.isFinite(rect.right) ? rect.right : 0;
        }));
        const current = [...document.querySelectorAll('.primary-nav a[aria-current="page"]')].map(a => a.getAttribute('href'));
        const menu = document.querySelector('.menu-toggle');
        let keyboard = {ok: true, reason: ''};
        if (menu && innerWidth <= 768) {
          menu.click();
          await wait(80);
          const opened = menu.getAttribute('aria-expanded') === 'true' && document.querySelector('.primary-nav')?.classList.contains('is-open');
          document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
          await wait(80);
          keyboard = {ok: opened && menu.getAttribute('aria-expanded') === 'false' && document.activeElement === menu, reason: opened ? '' : 'menu did not open'};
        }
        const reveal = document.querySelector('.reveal');
        return {
          lang: document.documentElement.lang,
          docWidth: document.documentElement.scrollWidth,
          bodyWidth: document.body.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
          rectRight: Math.ceil(rectRight),
          badImages: localImages.filter(image => !image.complete || image.naturalWidth === 0).map(image => image.currentSrc || image.src),
          images: imageRecords,
          fidelityFailures,
          current,
          keyboard,
          formCount: document.querySelectorAll('form').length,
          hasPartnersHero: Boolean(document.querySelector('.partners-hero')),
        };
      })()`);
      const failures = [];
      if (state.lang !== locale) failures.push(`lang=${state.lang}`);
      if (state.docWidth > state.clientWidth || state.bodyWidth > state.clientWidth) failures.push(`overflow=${state.docWidth}/${state.bodyWidth}>${state.clientWidth}`);
      if (state.badImages.length) failures.push(`badImages=${state.badImages.join(',')}`);
      if (state.fidelityFailures.length) failures.push(`undersizedImages=${state.fidelityFailures.map(image => `${image.currentSrc} natural=${image.naturalWidth} rendered=${image.renderedWidth} dpr=${image.devicePixelRatio}`).join('|')}`);
      if (activeHref && (state.current.length !== 1 || state.current[0] !== activeHref)) failures.push(`aria-current=${JSON.stringify(state.current)} expected ${activeHref}`);
      if (!state.keyboard.ok) failures.push(`keyboard=${state.keyboard.reason || 'focus return failed'}`);
      if ((route.endsWith('/doi-tac/') || route.endsWith('/partners/')) && !state.hasPartnersHero) failures.push('missing .partners-hero');
      if ((route.endsWith('/lien-he/') || route.endsWith('/contact/')) && state.formCount !== 0) failures.push(`forms=${state.formCount}`);
      const knownExternalWarnings = runtimeErrors.filter(isKnownExternalCspWarning);
      const applicationRuntimeErrors = runtimeErrors.filter(error => !isKnownExternalCspWarning(error));
      if (applicationRuntimeErrors.length) failures.push(`jsErrors=${applicationRuntimeErrors.join('|')}`);
      if (networkFailures.length) failures.push(`networkFailures=${networkFailures.join('|')}`);
      if (networkBadResponses.length) failures.push(`networkHTTP=${networkBadResponses.join('|')}`);
      await cdp.send('Emulation.setEmulatedMedia', {features: [{name: 'prefers-reduced-motion', value: 'reduce'}]});
      const reducedMotion = await evaluate(cdp, `getComputedStyle(document.querySelector('.reveal') || document.body).transitionDuration`);
      if (!reducedMotion || reducedMotion.split(',').some(value => Number.parseFloat(value) > 0.00002)) failures.push(`reduced-motion-media=${reducedMotion}`);
      await cdp.send('Emulation.setEmulatedMedia', {features: []});
      await evaluate(cdp, 'window.scrollTo(0, 0)');
      const screenshot = await cdp.send('Page.captureScreenshot', {format: 'png'});
      await fs.mkdir(evidence, {recursive: true});
      await fs.writeFile(path.join(evidence, `${name}-${width}x${height}.png`), Buffer.from(screenshot.data, 'base64'));
      results.push({
        name,
        route,
        viewport: `${width}x${height}`,
        failures,
        knownExternalWarnings,
        applicationRuntimeErrors,
        firstPartyNetworkFailures: [...networkFailures, ...networkBadResponses],
        state,
      });
      const warningNote = knownExternalWarnings.length ? ` — KNOWN_EXTERNAL_WARNING=${knownExternalWarnings.length}` : '';
      console.log(`${failures.length ? 'FAIL' : 'PASS'} ${name} ${width}x${height}${failures.length ? ` — ${failures.join(', ')}` : ''}${warningNote}`);
    }
  }
} catch (error) {
  console.error(`BROWSER_MATRIX_ERROR: ${error.message}`);
  if (chromeStderr) console.error(chromeStderr.split('\n').slice(-10).join('\n'));
  process.exitCode = 2;
} finally {
  cdp?.close();
  chrome.kill('SIGTERM');
  await sleep(250);
  await fs.rm(profile, {recursive: true, force: true, maxRetries: 5, retryDelay: 100}).catch(() => {});
}
const failed = results.filter(result => result.failures.length).length;
const externalCspWarnings = results.reduce((total, result) => total + result.knownExternalWarnings.length, 0);
await fs.mkdir(evidence, {recursive: true});
await fs.writeFile(path.join(evidence, 'matrix-results.json'), JSON.stringify({
  cases: results.length,
  failures: failed,
  external_csp_warnings: externalCspWarnings,
  results,
}, null, 2));
console.log(JSON.stringify({cases: results.length, failures: failed, external_csp_warnings: externalCspWarnings, evidence}));
if (process.exitCode === undefined) process.exitCode = failed ? 1 : 0;
