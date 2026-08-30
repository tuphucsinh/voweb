// Optional CMS → local content sync. Static site remains on last-known-good content if this fails.
import fs from 'node:fs/promises';
import path from 'node:path';
const ROOT=new URL('../',import.meta.url).pathname;
const BASE=(process.env.DIRECTUS_URL||'http://127.0.0.1:8055').replace(/\/$/,'');
const TOKEN=process.env.DIRECTUS_READ_TOKEN||'';
if(!TOKEN){console.error('DIRECTUS_READ_TOKEN missing');process.exit(2)}
async function get(collection){const u=new URL(`${BASE}/items/${collection}`);u.searchParams.set('limit','-1');u.searchParams.set('filter[status][_eq]','published');const r=await fetch(u,{headers:{Authorization:`Bearer ${TOKEN}`},signal:AbortSignal.timeout(8000)});if(!r.ok)throw new Error(`${collection}: HTTP ${r.status}`);return (await r.json()).data||[]}
const brands=await get('brands'); const products=await get('products'); const insights=await get('insights');
await fs.mkdir(path.join(ROOT,'content','cms-cache'),{recursive:true});
await fs.writeFile(path.join(ROOT,'content','cms-cache','brands.json'),JSON.stringify(brands,null,2));
await fs.writeFile(path.join(ROOT,'content','cms-cache','products.json'),JSON.stringify(products,null,2));
await fs.writeFile(path.join(ROOT,'content','cms-cache','insights.json'),JSON.stringify(insights,null,2));
console.log(`Synced Directus: ${brands.length} brands, ${products.length} products, ${insights.length} insights`);
