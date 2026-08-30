// Idempotent-ish bootstrap for the VOrigin Directus content model.
// Run after Directus is healthy: node services/directus/bootstrap.mjs
const BASE=(process.env.DIRECTUS_URL||'http://127.0.0.1:8055').replace(/\/$/,'');
const email=process.env.DIRECTUS_ADMIN_EMAIL;
const password=process.env.DIRECTUS_ADMIN_PASSWORD;
if(!email||!password){console.error('DIRECTUS_ADMIN_EMAIL and DIRECTUS_ADMIN_PASSWORD are required');process.exit(1)}
const j=async(url,opts={})=>{const r=await fetch(BASE+url,{...opts,headers:{'Content-Type':'application/json',...(opts.headers||{})}});const txt=await r.text();let body={};try{body=txt?JSON.parse(txt):{}}catch{};if(!r.ok)throw new Error(`${r.status} ${url} ${txt.slice(0,300)}`);return body};
const login=await j('/auth/login',{method:'POST',body:JSON.stringify({email,password})});
const token=login.data.access_token; const H={Authorization:`Bearer ${token}`};
async function exists(name){try{await j('/collections/'+name,{headers:H});return true}catch{return false}}
async function collection(name,note){if(await exists(name))return;await j('/collections',{method:'POST',headers:H,body:JSON.stringify({collection:name,meta:{note,hidden:false},schema:{name}})});}
async function field(col,field,type,extra={}){try{await j(`/fields/${col}/${field}`,{headers:H});return}catch{};await j(`/fields/${col}`,{method:'POST',headers:H,body:JSON.stringify({field,type,...extra})});}
for (const [c,n] of [['brands','VOrigin brand portfolio'],['products','Products and SKUs'],['pages','Managed page copy'],['insights','Editorial content'],['claims','Verified product/business claims'],['leads','Inbound website leads']]) await collection(c,n);
for (const c of ['brands','products','pages','insights','claims','leads']) await field(c,'id','uuid',{meta:{hidden:true,readonly:true},schema:{is_primary_key:true}});
const statusMeta={meta:{interface:'select-dropdown',options:{choices:[{text:'Draft',value:'draft'},{text:'Review',value:'review'},{text:'Published',value:'published'}]}},schema:{default_value:'draft'}};
await field('brands','status','string',statusMeta); await field('brands','slug','string'); await field('brands','name','string'); await field('brands','category','string'); await field('brands','summary_vi','text'); await field('brands','summary_en','text'); await field('brands','source_url','string');
await field('products','status','string',statusMeta); await field('products','slug','string'); await field('products','brand_slug','string'); await field('products','name','string'); await field('products','flavor','string'); await field('products','pack','string'); await field('products','source_url','string'); await field('products','vn_claims_approved','boolean',{schema:{default_value:false}});
await field('pages','status','string',statusMeta); await field('pages','slug','string'); await field('pages','title_vi','string'); await field('pages','title_en','string'); await field('pages','body_vi','text'); await field('pages','body_en','text');
await field('insights','status','string',statusMeta); await field('insights','slug','string'); await field('insights','date','date'); await field('insights','title_vi','string'); await field('insights','title_en','string'); await field('insights','excerpt_vi','text'); await field('insights','excerpt_en','text'); await field('insights','body_vi','text'); await field('insights','body_en','text');
await field('claims','status','string',statusMeta); await field('claims','key','string'); await field('claims','statement','text'); await field('claims','source','string'); await field('claims','verified_public','boolean'); await field('claims','approved_vn','boolean');
for(const f of [['created_at','timestamp'],['form_type','string'],['name','string'],['email','string'],['company','string'],['country','string'],['website','string'],['inquiry_type','string'],['message','text'],['source_path','string'],['ip_hash','string']]) await field('leads',f[0],f[1]);
console.log('VOrigin Directus collections/fields bootstrapped. Configure roles/permissions in Admin UI: editors cannot publish; reviewers can move review→published; lead token can CREATE leads only; build token can READ published content only.');
