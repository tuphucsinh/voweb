#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
PUBLIC = ROOT / 'public'
SITE = json.loads((ROOT/'config/site.json').read_text(encoding='utf-8'))
BRAND = json.loads((ROOT/'content/brands/marigold.json').read_text(encoding='utf-8'))
CLAIMS = json.loads((ROOT/'content/claims.json').read_text(encoding='utf-8'))
CLAIM_MAP = {c['key']: c for c in CLAIMS.get('claims', [])}
PRODUCTS = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'content/products').glob('*.json'))]
# If a private Directus sync has produced published CMS cache, prefer it while retaining file-backed defaults.
try:
    cached_brands=json.loads((ROOT/'content/cms-cache/brands.json').read_text(encoding='utf-8'))
    m=next((x for x in cached_brands if str(x.get('slug','')).lower()=='marigold'),None)
    if m: BRAND={**BRAND,**m}
except Exception: pass
try:
    cached_products=json.loads((ROOT/'content/cms-cache/products.json').read_text(encoding='utf-8'))
    if cached_products: PRODUCTS=[{**x, 'brand':x.get('brand') or x.get('brand_slug','marigold')} for x in cached_products if str(x.get('brand_slug',x.get('brand','marigold'))).lower()=='marigold']
except Exception: pass
BASE = SITE['domain'].rstrip('/')
ENV = os.getenv('SITE_ENV', 'preview')
TURNSTILE_SITE_KEY = os.getenv('TURNSTILE_SITE_KEY', SITE.get('turnstile_site_key','')).strip()
ANALYTICS_URL = os.getenv('ANALYTICS_SCRIPT_URL', SITE['analytics'].get('script_url','')).strip()
ANALYTICS_ID = os.getenv('ANALYTICS_WEBSITE_ID', SITE['analytics'].get('website_id','')).strip()

LANG = {
 'vi': {
  'home':'Trang chủ','about':'Giới thiệu','brands':'Thương hiệu','cap':'Năng lực','partners':'Đối tác','insights':'Góc nhìn','contact':'Liên hệ','cta':'Hợp tác cùng chúng tôi',
  'hero_lead':'VOrigin tuyển chọn những sản phẩm có nguồn gốc đáng tin cậy và đưa chúng đến thị trường Việt Nam bằng tiêu chuẩn rõ ràng, sự chỉn chu trong từng bước và một tầm nhìn dài hạn.',
  'hero_primary':'Tìm hiểu VOrigin','hero_secondary':'Khám phá danh mục','story_title':'Mỗi sản phẩm, một hành trình giá trị','origin':'Nguồn gốc rõ ràng','nature':'Giữ trọn đặc tính tự nhiên','craft':'Chọn lọc theo tiêu chuẩn','value':'Kiến tạo giá trị bền lâu',
  'featured_copy':'MARIGOLD Fruit Drinks là thương hiệu nổi bật đầu tiên trong danh mục VOrigin, với bốn hương vị Apple, Orange, Mango và Grape. Một dòng sản phẩm tươi sáng, dễ tiếp cận và phù hợp với những khoảnh khắc thường ngày.',
  'discover_marigold':'Khám phá MARIGOLD','portfolio_copy':'VOrigin mở rộng danh mục một cách chọn lọc, ưu tiên nguồn gốc rõ ràng, sự phù hợp thực sự với thị trường và tiềm năng phát triển dài hạn. Những nhóm bên dưới là các hướng chúng tôi đang tìm hiểu, không phải danh sách đối tác đã ký kết.','portfolio_cta':'Xem danh mục tuyển chọn',
  'why':'Vì sao chọn VOrigin','market_copy':'VOrigin đồng hành cùng các thương hiệu quốc tế trong hành trình vào Việt Nam, từ đánh giá thị trường và tuân thủ nhập khẩu đến phát triển phân phối, bản địa hóa thương hiệu và tiếp thị thương mại.','market_cta':'Bắt đầu lộ trình vào Việt Nam',
  'about_title':'Từ nguồn gốc đáng tin đến giá trị bền lâu','about_lede':'VOrigin bắt đầu từ những điều căn bản nhất: sản phẩm đến từ đâu, được tạo ra như thế nào, tiêu chuẩn phía sau ra sao và liệu sản phẩm ấy có thể tạo nên giá trị bền lâu tại Việt Nam hay không.','standard':'Tiêu chuẩn VOrigin','mission':'Sứ mệnh','vision':'Tầm nhìn',
  'brands_title':'Những thương hiệu được chọn cho giá trị bền lâu','brands_lede':'MARIGOLD là thương hiệu nổi bật đầu tiên trong danh mục VOrigin. Từ nền tảng đó, chúng tôi mở rộng từng bước, chọn những thương hiệu có nguồn gốc rõ ràng, chất lượng ổn định và sự phù hợp thực sự với thị trường Việt Nam.',
  'cap_title':'Từ cơ hội thị trường đến hiện diện bền vững','cap_lede':'Đưa một thương hiệu vào thị trường mới không dừng ở việc nhập khẩu sản phẩm. VOrigin đồng hành từ đánh giá thị trường, tuân thủ và phân phối đến bản địa hóa và tiếp thị thương mại tại Việt Nam.',
  'partners_title':'YOUR BRAND. OUR MARKET.','partners_lede':'VOrigin tìm kiếm những thương hiệu có nền tảng tốt, câu chuyện đáng tin và dư địa phát triển rõ ràng tại Việt Nam. Mục tiêu là cùng xây một hiện diện bền vững trên thị trường, không chỉ hoàn thành một lô hàng.','contact_title':'Bắt đầu từ một cuộc trao đổi rõ ràng','contact_lede':'Nếu bạn đại diện cho một thương hiệu quốc tế, đang hoạt động trong lĩnh vực bán lẻ hoặc phân phối, hay đang cân nhắc cơ hội tại Việt Nam, hãy cho chúng tôi biết điều bạn đang hướng tới. Chỉ cần vài thông tin rõ ràng để bắt đầu một cuộc trao đổi đúng trọng tâm.','send':'Gửi thông tin',
  'insights_title':'Góc nhìn từ VOrigin','insights_lede':'Những góc nhìn thực tế về nguồn gốc, thị trường Việt Nam và những điều cần được làm đúng để một thương hiệu tạo nên giá trị bền lâu.','coming':'Các bài viết đầu tiên đang được biên tập cẩn trọng.',
  'privacy_title':'Chính sách quyền riêng tư','terms_title':'Điều khoản sử dụng','draft_legal':'Nội dung này đang được rà soát trước khi website chính thức hoạt động.',
  'back':'Quay lại','source':'Nguồn chính thức','product_info':'Thông tin sản phẩm','pack':'Quy cách tham khảo','market_note':'Thông tin công bố cho thị trường Việt Nam được đối chiếu với nhãn, hồ sơ nhập khẩu và tài liệu phân phối do VOrigin lưu giữ.','view':'Xem chi tiết','privacy':'Quyền riêng tư','terms':'Điều khoản'
 },
 'en': {
  'home':'Home','about':'About','brands':'Brands','cap':'Capabilities','partners':'Partners','insights':'Insights','contact':'Contact','cta':'Partner with us',
  'hero_lead':'VOrigin curates products from trusted origins and brings them to Vietnam with clear standards, thoughtful execution and a long-term view.',
  'hero_primary':'Discover VOrigin','hero_secondary':'Explore the portfolio','story_title':'Every product carries a journey of value','origin':'Clear provenance','nature':'Respect for natural character','craft':'Selection with standards','value':'Lasting value',
  'featured_copy':'MARIGOLD Fruit Drinks is the first featured brand in VOrigin’s portfolio, with four flavours: Apple, Orange, Mango and Grape. A bright, approachable range made for everyday moments.',
  'discover_marigold':'Discover MARIGOLD','portfolio_copy':'VOrigin grows its portfolio with restraint and intention, favouring clear provenance, genuine market relevance and long-term potential. The categories below are areas we are exploring; they do not represent signed brand partnerships.','portfolio_cta':'View curated portfolio',
  'why':'Why Choose VOrigin','market_copy':'VOrigin works with international brands to shape a clear route into Vietnam, from market assessment and import compliance to distribution development, localisation and trade marketing.','market_cta':'Start your route into Vietnam',
  'about_title':'Where trusted origins become lasting value','about_lede':'VOrigin starts with the fundamentals: where a product comes from, how it is made, the standards behind it, and whether it can create lasting value in Vietnam.','standard':'The VOrigin Standard','mission':'Mission','vision':'Vision',
  'brands_title':'Brands chosen for lasting value','brands_lede':'MARIGOLD is the first featured brand in VOrigin’s portfolio. From that foundation, we will grow at a measured pace, choosing brands for clear provenance, consistent quality and genuine relevance to the Vietnamese market.',
  'cap_title':'From market opportunity to lasting presence','cap_lede':'Entering a new market takes more than importing a product. VOrigin works across market assessment, compliance, distribution, localisation and trade marketing to build a practical route into Vietnam.',
  'partners_title':'YOUR BRAND. OUR MARKET.','partners_lede':'VOrigin looks for brands with a sound foundation, a credible story and clear room to grow in Vietnam. The aim is to build a lasting market presence together, not simply move a shipment.','contact_title':'Start with a clear conversation','contact_lede':'If you represent an international brand, work in retail or distribution, or are exploring opportunities in Vietnam, tell us what you are working on. A few clear details are enough to begin a focused conversation.','send':'Send enquiry',
  'insights_title':'VOrigin Insights','insights_lede':'Practical perspectives on provenance, the Vietnamese market and what it takes to build lasting brand value with care and credibility.','coming':'Our first articles are being prepared with care.',
  'privacy_title':'Privacy Policy','terms_title':'Terms of Use','draft_legal':'This page is being reviewed before the website goes live.',
  'back':'Back','source':'Official source','product_info':'Product information','pack':'Pack format','market_note':'Information published for the Vietnam market is checked against labels, import documentation and distribution records held by VOrigin.','view':'View details','privacy':'Privacy','terms':'Terms'
 }
}

ROUTES = {
 'vi': {'home':'/vi/','about':'/vi/gioi-thieu/','brands':'/vi/thuong-hieu/','marigold':'/vi/thuong-hieu/marigold/','cap':'/vi/nang-luc/','partners':'/vi/doi-tac/','insights':'/vi/goc-nhin/','contact':'/vi/lien-he/','privacy':'/vi/chinh-sach-quyen-rieng/','terms':'/vi/dieu-khoan-su-dung/'},
 'en': {'home':'/en/','about':'/en/about/','brands':'/en/brands/','marigold':'/en/brands/marigold/','cap':'/en/capabilities/','partners':'/en/partners/','insights':'/en/insights/','contact':'/en/contact/','privacy':'/en/privacy/','terms':'/en/terms/'}
}

def e(v): return html.escape(str(v), quote=True)

def icon_img(name, cls='icon-svg'):
    return f'<img src="/assets/ui-icons/{e(name)}.svg" alt="" aria-hidden="true" class="{cls}" width="24" height="24">'


def claim_text(key, locale):
    c=CLAIM_MAP.get(key,{})
    return c.get('statement_vi' if locale=='vi' else 'statement_en','')

def marigold_trust_chips(locale, compact=False):
    keys=['vitamins_abcde','no_preservatives','halal_certified']
    icons=['value','premium-approach','trusted-partner']
    cls='trust-chip compact' if compact else 'trust-chip'
    return ''.join(f'<span class="{cls}"><i>{icon_img(ic, "trust-chip-icon")}</i><b>{e(claim_text(k,locale))}</b></span>' for k,ic in zip(keys,icons))

def marigold_assurance_cards(locale):
    vi=locale=='vi'
    items=[
      ('value','DINH DƯỠNG CÔNG BỐ' if vi else 'DECLARED NUTRITION',claim_text('vitamins_abcde',locale)),
      ('premium-approach','THÀNH PHẦN' if vi else 'PRODUCT CLAIM',claim_text('no_preservatives',locale)),
      ('trusted-partner','CHỨNG NHẬN' if vi else 'CERTIFICATION',claim_text('halal_certified',locale)),
      ('import-compliance','HỆ THỐNG CHẤT LƯỢNG' if vi else 'QUALITY SYSTEMS',claim_text('manufacturer_accreditations',locale)),
      ('origin','NỀN TẢNG THƯƠNG HIỆU' if vi else 'MANUFACTURER HERITAGE',claim_text('manufacturer_heritage',locale))]
    return ''.join(f'<article class="assurance-card reveal"><span>{icon_img(ic, "assurance-icon-svg")}</span><p class="eyebrow">{e(label)}</p><h3>{e(copy)}</h3></article>' for ic,label,copy in items)

def alt_url(locale, route_key, suffix=''):
    return BASE + ROUTES[locale][route_key] + suffix

def nav(locale, alt_path_vi=None, alt_path_en=None):
    t=LANG[locale]; r=ROUTES[locale]
    vi_target=alt_path_vi or ROUTES['vi']['home']; en_target=alt_path_en or ROUTES['en']['home']
    menu_label='Mở menu' if locale=='vi' else 'Open menu'
    nav_label='Điều hướng chính' if locale=='vi' else 'Primary navigation'
    return f'''<header class="site-header" id="top"><div class="shell nav-wrap">
<a class="brand-lockup" href="{r['home']}" aria-label="VOrigin — From Origins to Value"><img src="/assets/vorigin-logo-primary.svg" alt="VOrigin" width="700" height="173"><span class="brand-tagline">FROM ORIGINS TO VALUE</span></a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="{menu_label}"><span></span><span></span></button>
<nav class="primary-nav" id="primary-nav" aria-label="{nav_label}">
<a href="{r['about']}">{t['about']}</a><a href="{r['brands']}">{t['brands']}</a><a href="{r['cap']}">{t['cap']}</a><a href="{r['partners']}">{t['partners']}</a><a href="{r['insights']}">{t['insights']}</a><a href="{r['contact']}">{t['contact']}</a></nav>
<div class="nav-actions"><div class="lang-switch locale-nav"><a href="{vi_target}" {'aria-current="page"' if locale=='vi' else ''}>VI</a><span>|</span><a href="{en_target}" {'aria-current="page"' if locale=='en' else ''}>EN</a></div><a class="button button-outline nav-cta" href="{r['partners']}">{t['cta']}</a></div></div></header>'''

def footer(locale):
    t=LANG[locale]; r=ROUTES[locale]
    contact=SITE['contact']
    address = contact.get('address_vi' if locale=='vi' else 'address_en','')
    contact_lines=''.join(x for x in [f'<a href="mailto:{e(contact["email"])}">{e(contact["email"])}</a>' if contact.get('email') else '', f'<a href="tel:{e(contact["phone"])}">{e(contact["phone"])}</a>' if contact.get('phone') else '', f'<span>{e(address)}</span>' if address else ''])
    story_label='Câu chuyện thương hiệu' if locale=='vi' else 'Our story'
    portfolio_label='Danh mục tuyển chọn' if locale=='vi' else 'Curated portfolio'
    market_label='Gia nhập thị trường' if locale=='vi' else 'Market Entry'
    compliance_label='Nhập khẩu &amp; tuân thủ' if locale=='vi' else 'Import &amp; Compliance'
    distribution_label='Phát triển phân phối' if locale=='vi' else 'Distribution Development'
    partner_label='Dành cho thương hiệu quốc tế' if locale=='vi' else 'For international brands'
    return f'''<footer class="site-footer" id="footer"><div class="shell footer-grid">
<div class="footer-brand"><div class="footer-logo-lockup"><img src="/assets/vorigin-logo-footer-bronze.svg" alt="VOrigin" width="700" height="173" loading="lazy"><span>FROM ORIGINS TO VALUE</span></div><strong>{e(SITE['legal_name'])}</strong><p>VORIGIN Corp</p><a href="https://vorigin.vn">VOrigin.vn</a>{contact_lines}</div>
<div class="footer-col"><h3>{t['about']}</h3><a href="{r['about']}">{story_label}</a><a href="{r['about']}#standard">{t['standard']}</a></div>
<div class="footer-col"><h3>{t['brands']}</h3><a href="{r['marigold']}">MARIGOLD</a><a href="{r['brands']}">{portfolio_label}</a></div>
<div class="footer-col"><h3>{t['cap']}</h3><a href="{r['cap']}#market-entry">{market_label}</a><a href="{r['cap']}#compliance">{compliance_label}</a><a href="{r['cap']}#distribution">{distribution_label}</a></div>
<div class="footer-col"><h3>{t['partners']}</h3><a href="{r['partners']}">{partner_label}</a><a href="{r['contact']}">{t['contact']}</a></div>
<div class="footer-col"><h3>{t['insights']}</h3><a href="{r['insights']}">{'Bài viết & góc nhìn' if locale=='vi' else 'Articles & perspectives'}</a><a href="{r['contact']}">{t['contact']}</a></div>
</div><div class="shell footer-bottom"><p>© 2026 VOrigin Corp. All rights reserved.</p><div><a href="{r['privacy']}">{t['privacy']}</a><span>|</span><a href="{r['terms']}">{t['terms']}</a></div></div></footer>'''

def analytics():
    if ANALYTICS_URL and ANALYTICS_ID:
        return f'<script defer src="{e(ANALYTICS_URL)}" data-website-id="{e(ANALYTICS_ID)}"></script>'
    return ''

def base_page(locale, title, description, route_key=None, body='', canonical_path=None, alt_path_vi=None, alt_path_en=None, extra_head='', body_class=''):
    lang_attr='vi' if locale=='vi' else 'en'
    canonical = BASE + (canonical_path or ROUTES[locale].get(route_key,'/'))
    if alt_path_vi is None and route_key: alt_path_vi=ROUTES['vi'].get(route_key)
    if alt_path_en is None and route_key: alt_path_en=ROUTES['en'].get(route_key)
    robots = 'index,follow,max-image-preview:large' if ENV=='production' else 'noindex,nofollow'
    ld = {'@context':'https://schema.org','@type':'Organization','name':'VOrigin','legalName':SITE['legal_name'],'url':BASE,'slogan':'From Origins to Value'}
    head = f'''<!doctype html><html lang="{lang_attr}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#f3eee4"><meta name="robots" content="{robots}">
<title>{e(title)}</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{e(canonical)}">'''
    if alt_path_vi: head += f'<link rel="alternate" hreflang="vi-VN" href="{BASE}{alt_path_vi}">'
    if alt_path_en: head += f'<link rel="alternate" hreflang="en" href="{BASE}{alt_path_en}">'
    head += f'''<link rel="alternate" hreflang="x-default" href="{BASE}/vi/"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{e(canonical)}"><meta property="og:image" content="{BASE}/assets/hero-marigold-premium.webp"><meta name="twitter:card" content="summary_large_image"><link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"><link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png"><link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="/styles.css"><script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>{extra_head}{analytics()}</head>'''
    skip='Chuyển đến nội dung' if locale=='vi' else 'Skip to content'
    return head + f'<body class="{e(body_class)}"><a class="skip-link" href="#main">{skip}</a>{nav(locale,alt_path_vi,alt_path_en)}<main id="main">{body}</main>{footer(locale)}<script src="/app.js" defer></script></body></html>'

def page_hero(locale, eyebrow, title, lede, breadcrumbs=''):
    return f'''<section class="page-hero"><div class="shell"><div class="breadcrumb">{breadcrumbs}</div><p class="eyebrow">{e(eyebrow)}</p><h1>{title}</h1><p class="lede">{e(lede)}</p></div></section>'''

def home(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    partner_copy = [
      ('Đối tác đáng tin' if vi else 'Trusted Partner','Minh bạch từ thông tin đến cam kết, rõ ràng trong từng bước làm việc.' if vi else 'Clear information, clear commitments and transparency in the way we work.'),
      ('Am hiểu thị trường' if vi else 'Local Expertise','Hiểu thị trường Việt Nam, từ người tiêu dùng đến nhịp vận hành của từng kênh bán.' if vi else 'A grounded understanding of Vietnam, from consumers to the rhythm of each sales channel.'),
      ('Giá trị dài hạn' if vi else 'Long-term Value','Ưu tiên nền tảng bền vững hơn những mục tiêu ngắn hạn.' if vi else 'We favour enduring value over short-term momentum.'),
      ('Cách làm chỉn chu' if vi else 'Considered Approach','Chọn lọc kỹ, tiêu chuẩn rõ và triển khai với sự cẩn trọng cần thiết.' if vi else 'Careful selection, clear standards and the discipline to execute well.'),
      ('Cùng phát triển' if vi else 'Grow Together','Mỗi quan hệ hợp tác đều hướng đến sự tăng trưởng ổn định và lâu dài.' if vi else 'Each partnership is built with steady, long-term growth in mind.')]
    benefits=''.join(f'<article class="benefit reveal"><span class="benefit-icon" aria-hidden="true">{icon_img(icon, "benefit-icon-svg")}</span><h3>{e(a)}</h3><p>{e(b)}</p></article>' for icon,(a,b) in zip(['trusted-partner','local-expertise','long-term-value','premium-approach','grow-together'],partner_copy))
    hero_eyebrow='NGUỒN GỐC ĐÁNG TIN. GIÁ TRỊ BỀN LÂU.' if vi else 'TRUSTED ORIGINS. LASTING VALUE.'
    story_eyebrow='TUYỂN CHỌN BỞI VORIGIN' if vi else 'CURATED BY VORIGIN'
    featured_label='THƯƠNG HIỆU NỔI BẬT' if vi else 'FEATURED BRAND'
    portfolio_label='DANH MỤC THƯƠNG HIỆU' if vi else 'OUR PORTFOLIO'
    portfolio_title='Danh mục chọn lọc,<br>lớn lên từng bước' if vi else 'A growing portfolio<br>of carefully chosen brands'
    global_label='DÀNH CHO THƯƠNG HIỆU QUỐC TẾ' if vi else 'FOR GLOBAL BRANDS'
    services=[('market-entry','Gia nhập<br>thị trường' if vi else 'Market Entry'),('import-compliance','Nhập khẩu &amp;<br>tuân thủ' if vi else 'Import &amp;<br>Compliance'),('distribution-development','Phát triển<br>phân phối' if vi else 'Distribution<br>Development'),('brand-localization','Bản địa hóa<br>thương hiệu' if vi else 'Brand<br>Localisation'),('trade-marketing','Tiếp thị<br>thương mại' if vi else 'Trade<br>Marketing')]
    service_html=''.join(f'<span><i class="service-icon">{icon_img(ic,"service-icon-svg")}</i><small>{label}</small></span>' for ic,label in services)
    body=f'''<section class="hero section-light"><div class="shell hero-grid"><div class="hero-copy reveal"><p class="eyebrow">{hero_eyebrow}</p><h1>From Origins<br><span>to Value.</span></h1><p class="hero-lead">{e(t['hero_lead'])}</p><div class="hero-actions"><a href="{r['about']}" class="button button-solid">{e(t['hero_primary'])}<span>→</span></a><a href="{r['brands']}" class="text-action"><span class="play">{icon_img("play-circle","play-icon-svg")}</span>{e(t['hero_secondary'])}</a></div></div><figure class="hero-visual reveal"><figcaption class="visual-label">{featured_label} — MARIGOLD</figcaption><img src="/assets/hero-marigold-premium.webp" alt="MARIGOLD Orange Fruit Drink" width="1494" height="1065" fetchpriority="high"></figure></div></section>
<section class="story section-light" id="story"><div class="shell"><div class="section-heading centered reveal"><p class="eyebrow">{story_eyebrow}</p><h2>{e(t['story_title'])}</h2><i class="bronze-rule"></i></div><div class="story-grid">
{story_card('story-origin.webp','Nguồn gốc' if vi else 'Origin',t['origin'],'origin')}{story_card('story-nature.webp','Tự nhiên' if vi else 'Nature',t['nature'],'nature')}{story_card('story-craft.webp','Tiêu chuẩn' if vi else 'Craft',t['craft'],'craft')}{story_card('story-value.webp','Giá trị' if vi else 'Value',t['value'],'value')}</div></div></section>
<section class="featured section-soft" id="brands"><div class="shell featured-grid"><div class="featured-copy reveal"><p class="eyebrow">{featured_label}</p><h2>MARIGOLD</h2><p>{e(t['featured_copy'])}</p><div class="featured-trust">{marigold_trust_chips(locale, True)}</div><a href="{r['marigold']}" class="button button-outline">{e(t['discover_marigold'])}<span>→</span></a></div><figure class="lineup reveal"><img src="/assets/marigold-lineup-premium.webp" alt="MARIGOLD Fruit Drink Apple, Orange, Mango and Grape" width="1300" height="500" loading="lazy"></figure></div></section>
<section class="portfolio section-light"><div class="shell portfolio-grid"><div class="portfolio-copy reveal"><p class="eyebrow">{portfolio_label}</p><h2>{portfolio_title}</h2><p>{e(t['portfolio_copy'])}</p><a class="button button-outline" href="{r['brands']}">{e(t['portfolio_cta'])}<span>→</span></a></div><div class="portfolio-cards" role="list">{portfolio_cards(locale)}</div></div></section>
<section class="why-partner section-light" id="partners"><div class="leaf-ornament leaf-left">⌁⌁⌁</div><div class="leaf-ornament leaf-right">⌁⌁⌁</div><div class="shell"><div class="section-heading centered reveal"><h2>{e(t['why'])}</h2><i class="bronze-rule transition-rule"></i></div><div class="benefit-grid">{benefits}</div></div></section>
<section class="market section-dark" id="market"><div class="sunset-bleed"></div><div class="shell market-grid"><figure class="market-visual reveal"><img src="/assets/b2b-vorigin-premium.webp" alt="VOrigin branded container at a port at sunset" width="1936" height="430" loading="lazy"></figure><div class="market-copy reveal"><p class="eyebrow">{global_label}</p><h2>YOUR BRAND.<br>OUR MARKET.</h2><p>{e(t['market_copy'])}</p><div class="services">{service_html}</div><a class="button button-gold" href="{r['partners']}">{e(t['market_cta'])}<span>→</span></a></div></div></section>'''
    return base_page(locale,'VOrigin — From Origins to Value',t['hero_lead'],'home',body)

def story_card(img,title,copy,icon):
    return f'<article class="story-card reveal"><img src="/assets/{img}" alt="{e(title)}" width="420" height="264" loading="lazy"><div class="story-body"><span class="round-icon">{icon_img(icon, "round-icon-svg")}</span><h3>{e(title)}</h3><p>{e(copy)}</p></div></article>'

def portfolio_cards(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    dirs=([('Đồ uống chọn lọc','Đồ uống','premium-beverages'),('Thực phẩm tuyển chọn','Thực phẩm','fine-foods'),('Tự nhiên & Sống khỏe','Sống khỏe','natural-wellness'),('Quà tặng & Phong cách sống','Phong cách sống','gifting-lifestyle')] if vi else [('Premium Beverages','Beverages','premium-beverages'),('Fine Foods','Food','fine-foods'),('Natural & Wellness','Wellness','natural-wellness'),('Gifting & Lifestyle','Lifestyle','gifting-lifestyle')])
    featured='Thương hiệu nổi bật' if vi else 'Featured brand'
    direction='Định hướng danh mục' if vi else 'Portfolio direction'
    cards=f'''<a class="brand-card real reveal" role="listitem" href="{r['marigold']}"><div class="brand-card-visual marigold-card"><span class="marigold-mark">MARIGOLD</span><div class="fruit-cluster">● ● ●</div></div><h3>MARIGOLD</h3><p>Fruit Drinks</p><span class="tag">{featured}</span></a>'''
    for name,tag,sym in dirs:
        cards += f'<article class="brand-card direction reveal" role="listitem"><div class="category-symbol">{icon_img(sym, "category-icon-svg")}</div><h3>{e(name)}</h3><p>{direction}</p><span class="tag">{e(tag)}</span></article>'
    return cards

def simple_page(locale,key,title,lede,sections):
    t=LANG[locale]; r=ROUTES[locale]
    crumbs=f'<a href="{r["home"]}">{t["home"]}</a> / {e(title)}'
    body=page_hero(locale,'VORIGIN',title,lede,crumbs)
    for i,(sid,h,content) in enumerate(sections):
        body += f'<section class="page-section {"alt" if i%2 else ""}" id="{e(sid)}"><div class="shell editorial-grid"><div><p class="eyebrow">0{i+1}</p><h2>{h}</h2></div><div class="content-block">{content}</div></div></section>'
    return base_page(locale,f'{title} — VOrigin',lede,key,body)

def about(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    lead = 'Giá trị bền lâu luôn bắt đầu từ một nguồn gốc đáng tin.' if vi else 'Lasting value begins with a trusted origin.'
    story = 'Khởi Nguyên gợi về điểm bắt đầu của giá trị. VOrigin mang tinh thần ấy vào thương mại: chọn đúng nguồn, hiểu đúng thị trường và phát triển bằng những tiêu chuẩn có thể tin cậy.' if vi else 'Khởi Nguyên, our Vietnamese name, speaks to where value begins. VOrigin carries that idea into trade: choose the right origins, understand the market, and grow with standards people can trust.'
    standards=[('origin','Nguồn gốc' if vi else 'Origin','Đáng tin và có thể kiểm chứng' if vi else 'Trusted and verifiable'),('premium-approach','Chất lượng' if vi else 'Quality','Ổn định, rõ tiêu chuẩn' if vi else 'Consistent, with clear standards'),('market-entry','Phù hợp' if vi else 'Relevance','Phù hợp với nhu cầu và kênh bán' if vi else 'A genuine fit with people and channels'),('nature','Câu chuyện' if vi else 'Story','Có nền tảng thật để kể' if vi else 'A story with substance'),('long-term-value','Phát triển' if vi else 'Growth','Có dư địa phát triển bền vững' if vi else 'Room to grow responsibly')]
    cards=''.join(f'<article class="standard-card reveal"><span class="standard-icon">{icon_img(ic,"standard-icon-svg")}</span><p class="eyebrow">{e(k)}</p><h3>{e(v)}</h3></article>' for ic,k,v in standards)
    about_eyebrow='VỀ VORIGIN' if vi else 'ABOUT VORIGIN'; standard_eyebrow='TIÊU CHUẨN VORIGIN' if vi else 'THE VORIGIN STANDARD'
    vision_copy='Trở thành đối tác thương mại – nhập khẩu đáng tin cậy cho những thương hiệu muốn phát triển tại Việt Nam, với cách chọn sản phẩm có tiêu chuẩn, làm việc minh bạch và tầm nhìn dài hạn.' if vi else 'To become a trusted partner for brands seeking to grow in Vietnam — with disciplined selection, transparent relationships and a long-term view.'
    body=page_hero(locale,about_eyebrow,t['about_title'],t['about_lede'],f'<a href="{r["home"]}">{t["home"]}</a> / {t["about"]}')
    body+=f'''<section class="brand-story-premium page-section"><div class="shell brand-story-grid"><div class="brand-story-statement reveal"><p class="eyebrow">FROM ORIGINS TO VALUE</p><h2>{e(lead)}</h2><p>{e(story)}</p></div><figure class="brand-story-visual reveal"><img src="/assets/story-origin.webp" alt="VOrigin origin landscape" loading="lazy"><figcaption>{'NGUỒN GỐC → CHỌN LỌC → GIÁ TRỊ' if vi else 'ORIGIN → SELECTION → VALUE'}</figcaption></figure></div></section>'''
    body+=f'''<section class="page-section alt" id="standard"><div class="shell"><div class="section-heading centered"><p class="eyebrow">{standard_eyebrow}</p><h2>{e(t['standard'])}</h2><i class="bronze-rule"></i></div><div class="standard-grid">{cards}</div></div></section>'''
    body+=f'''<section class="page-section"><div class="shell editorial-grid"><div><p class="eyebrow">{'TẦM NHÌN' if vi else 'VISION'}</p><h2>{e(t['vision'])}</h2></div><div class="content-block"><p>{e(vision_copy)}</p></div></div></section>'''
    return base_page(locale,f'{t["about"]} — VOrigin',t['about_lede'],'about',body,body_class='about-page')

def brands(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    directions=([('premium-beverages','Đồ uống chọn lọc','Đồ uống'),('fine-foods','Thực phẩm tuyển chọn','Thực phẩm'),('natural-wellness','Tự nhiên & Sống khỏe','Sống khỏe'),('gifting-lifestyle','Quà tặng & Phong cách sống','Phong cách sống')] if vi else [('premium-beverages','Premium Beverages','Beverages'),('fine-foods','Fine Foods','Food'),('natural-wellness','Natural & Wellness','Wellness'),('gifting-lifestyle','Gifting & Lifestyle','Lifestyle')])
    card_eyebrow='ĐỊNH HƯỚNG DANH MỤC' if vi else 'PORTFOLIO DIRECTION'
    card_note='Những nhóm sản phẩm VOrigin đang nghiên cứu để mở rộng danh mục một cách có chọn lọc. Đây chưa phải thương hiệu đối tác.' if vi else 'Categories VOrigin is exploring as part of a carefully considered portfolio expansion. These are not signed brand partnerships.'
    cards=''.join(f'''<article class="portfolio-direction-card reveal"><span class="portfolio-direction-icon">{icon_img(ic,"portfolio-direction-svg")}</span><p class="eyebrow">{card_eyebrow}</p><h3>{e(name)}</h3><span>{e(card_note)}</span></article>''' for ic,name,tag in directions)
    page_label='DANH MỤC CHỌN LỌC' if vi else 'CURATED PORTFOLIO'; feature_label='THƯƠNG HIỆU NỔI BẬT' if vi else 'FEATURED BRAND'
    feature_copy='Thương hiệu nổi bật đầu tiên trong danh mục VOrigin, mở đầu cho một hành trình danh mục được xây dựng có chọn lọc.' if vi else 'The first featured brand in VOrigin’s portfolio, marking the beginning of a carefully built brand journey.'
    next_label='DANH MỤC ĐANG MỞ RỘNG' if vi else 'A GROWING PORTFOLIO'; next_title='Những hướng danh mục VOrigin đang tìm hiểu' if vi else 'Areas VOrigin is exploring'
    body=page_hero(locale,page_label,t['brands_title'],t['brands_lede'],f'<a href="{r["home"]}">{t["home"]}</a> / {t["brands"]}')
    body+=f'''<section class="portfolio-feature page-section"><div class="shell portfolio-feature-grid"><div class="portfolio-feature-copy reveal"><p class="eyebrow">{feature_label}</p><h2>MARIGOLD</h2><p>{e(feature_copy)}</p><div class="featured-trust">{marigold_trust_chips(locale, True)}</div><a class="button button-outline" href="{r['marigold']}">{e(t['view'])}<span>→</span></a></div><figure class="portfolio-feature-visual reveal"><img src="/assets/marigold-lineup-premium.webp" alt="MARIGOLD Fruit Drinks" loading="lazy"></figure></div></section>'''
    body+=f'''<section class="page-section alt"><div class="shell"><div class="section-heading centered"><p class="eyebrow">{next_label}</p><h2>{e(next_title)}</h2><i class="bronze-rule"></i></div><div class="portfolio-direction-grid">{cards}</div></div></section>'''
    return base_page(locale,f'{t["brands"]} — VOrigin',t['brands_lede'],'brands',body,body_class='brands-page')

def marigold(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    summary=BRAND['summary_vi' if vi else 'summary_en']; note=BRAND['source_note_vi' if vi else 'source_note_en']
    flavors=[('apple','Apple','#8aa073'),('orange','Orange','#d88938'),('mango','Mango','#d5a237'),('grape','Grape','#765b7b')]
    pmap={p['slug']:p for p in PRODUCTS}; flavor_cards=''
    for slug,label,color in flavors:
        p=pmap.get(slug,{'pack':'250ml x 6'}); path=(f'/vi/san-pham/marigold-{slug}/' if vi else f'/en/products/marigold-{slug}/')
        flavor_cards+=f'''<a class="flavor-card flavor-{slug} reveal" href="{path}" style="--flavor:{color}"><div class="flavor-visual"><img src="/assets/marigold-{slug}-premium.webp" alt="MARIGOLD {label} Fruit Drink" loading="lazy"></div><div class="flavor-copy"><p class="eyebrow">{e(p['pack'])}</p><h3>{label}</h3><span>{e(t['view'])} →</span></div></a>'''
    feature_label='THƯƠNG HIỆU NỔI BẬT' if vi else 'FEATURED BRAND'; flavour_label='KHÁM PHÁ HƯƠNG VỊ' if vi else 'EXPLORE THE FLAVOURS'
    flavour_title='Bốn hương vị, mỗi vị một nét riêng.' if vi else 'Four flavours, each with its own character.'; curated_label='TUYỂN CHỌN BỞI VORIGIN' if vi else 'CURATED BY VORIGIN'
    editorial_title='Một thương hiệu nổi bật. Khởi đầu cho một danh mục rộng hơn.' if vi else 'A featured brand. The beginning of a broader portfolio.'
    editorial_copy='MARIGOLD là thương hiệu nổi bật đầu tiên trong danh mục VOrigin. Dù danh mục mở rộng, nguyên tắc chọn lựa vẫn không đổi: nguồn gốc rõ ràng, tiêu chuẩn phù hợp và giá trị bền lâu.' if vi else 'MARIGOLD is the first featured brand in VOrigin’s portfolio. As the portfolio grows, the principles stay the same: clear provenance, relevant standards and lasting value.'
    body=f'''<section class="marigold-hero"><div class="shell marigold-hero-grid"><div class="marigold-hero-copy reveal"><div class="breadcrumb"><a href="{r['home']}">{t['home']}</a> / <a href="{r['brands']}">{t['brands']}</a> / MARIGOLD</div><p class="eyebrow">{feature_label}</p><h1>MARIGOLD</h1><p class="lede">{e(summary)}</p><div class="marigold-hero-trust">{marigold_trust_chips(locale)}</div><a class="source-link" href="{e(BRAND['source_url'])}" rel="noopener noreferrer">{t['source']} ↗</a></div><figure class="marigold-hero-visual reveal"><img src="/assets/marigold-lineup-premium.webp" alt="MARIGOLD Fruit Drinks Apple, Orange, Mango and Grape"></figure></div></section>'''
    assurance_eyebrow='NGUỒN GỐC & BẢO CHỨNG' if vi else 'PROVENANCE & ASSURANCE'
    assurance_title='Niềm tin bắt đầu từ những thông tin có thể kiểm chứng.' if vi else 'Trust begins with information that can be verified.'
    assurance_intro='VOrigin trình bày những thông tin cốt lõi của MARIGOLD Fruit Drinks dựa trên các nguồn chính thức của MARIGOLD và Malaysia Dairy Industries.' if vi else 'VOrigin presents the core facts behind MARIGOLD Fruit Drinks using official information from MARIGOLD and Malaysia Dairy Industries.'
    body+=f'''<section class="marigold-assurance page-section alt"><div class="shell"><div class="section-heading centered"><p class="eyebrow">{assurance_eyebrow}</p><h2>{e(assurance_title)}</h2><p class="section-lede">{e(assurance_intro)}</p><i class="bronze-rule"></i></div><div class="assurance-grid">{marigold_assurance_cards(locale)}</div></div></section>'''
    body+=f'''<section class="flavor-explorer page-section"><div class="shell"><div class="section-heading centered"><p class="eyebrow">{flavour_label}</p><h2>{e(flavour_title)}</h2><i class="bronze-rule"></i></div><div class="flavor-grid">{flavor_cards}</div><div class="source-note"><p>{e(note)}</p></div></div></section>'''
    body+=f'''<section class="marigold-editorial page-section alt"><div class="shell editorial-grid"><div><p class="eyebrow">{curated_label}</p><h2>{e(editorial_title)}</h2></div><div class="content-block"><p>{e(editorial_copy)}</p><a class="button button-outline" href="{r['brands']}">{e(t['portfolio_cta'])}<span>→</span></a></div></div></section>'''
    return base_page(locale,'MARIGOLD — VOrigin',summary,'marigold',body,alt_path_vi=ROUTES['vi']['marigold'],alt_path_en=ROUTES['en']['marigold'],body_class='brand-page marigold-page')

def product_page(locale,p):
    t=LANG[locale]; r=ROUTES[locale]; slug=p['slug']; vi=locale=='vi'
    path=(f'/vi/san-pham/marigold-{slug}/' if vi else f'/en/products/marigold-{slug}/'); alt_vi=f'/vi/san-pham/marigold-{slug}/'; alt_en=f'/en/products/marigold-{slug}/'
    colors={'apple':'#879b71','orange':'#d88938','mango':'#d3a037','grape':'#735978'}; accent=colors.get(slug,'#b8894d'); sibling=''
    for other in PRODUCTS:
        if other['slug']==slug: continue
        opath=(f'/vi/san-pham/marigold-{other["slug"]}/' if vi else f'/en/products/marigold-{other["slug"]}/')
        sibling+=f'<a href="{opath}" class="mini-flavor"><img src="/assets/marigold-{other["slug"]}-premium.webp" alt="MARIGOLD {e(other["flavor"])}"><span>{e(other["flavor"])}</span></a>'
    hero_label='MARIGOLD — THỨC UỐNG TRÁI CÂY' if vi else 'MARIGOLD FRUIT DRINK'; hero_lede='Một trong bốn hương vị của dòng MARIGOLD Fruit Drinks.' if vi else 'Part of the four-flavour MARIGOLD Fruit Drinks range.'
    category='Thức uống trái cây' if vi else 'Fruit Drink'; flavor_label='Hương vị' if vi else 'Flavour'; category_label='Nhóm sản phẩm' if vi else 'Category'
    product_info_label='THÔNG TIN SẢN PHẨM' if vi else 'PRODUCT INFORMATION'; explore_label='KHÁM PHÁ THÊM' if vi else 'EXPLORE MORE'; other_title='Các hương vị khác' if vi else 'Other flavours'
    body=f'''<section class="product-hero" style="--flavor:{accent}"><div class="shell product-hero-grid"><div class="product-hero-copy reveal"><div class="breadcrumb"><a href="{r['home']}">{t['home']}</a> / <a href="{r['marigold']}">MARIGOLD</a> / {e(p['flavor'])}</div><p class="eyebrow">{hero_label}</p><h1>{e(p['flavor'])}</h1><p class="lede">{e(hero_lede)}</p><div class="product-trust">{marigold_trust_chips(locale, True)}</div><div class="product-meta"><span>{e(p['pack'])}</span><span>{category}</span></div></div><figure class="product-hero-visual reveal"><img src="/assets/marigold-{slug}-premium.webp" alt="{e(p['name'])}"></figure></div></section>'''
    body+=f'''<section class="page-section"><div class="shell editorial-grid"><div><p class="eyebrow">{product_info_label}</p><h2>{e(t['product_info'])}</h2></div><div class="content-block"><div class="facts-grid product-facts"><div class="fact"><b>{e(p['flavor'])}</b><span>{flavor_label}</span></div><div class="fact"><b>{e(p['pack'])}</b><span>{e(t['pack'])}</span></div><div class="fact"><b>{category}</b><span>{category_label}</span></div><div class="fact"><b>{e(claim_text('vitamins_abcde',locale))}</b><span>{'Điểm nổi bật dinh dưỡng' if vi else 'Nutrition highlight'}</span></div><div class="fact"><b>{e(claim_text('no_preservatives',locale))}</b><span>{'Thông tin sản phẩm' if vi else 'Product claim'}</span></div></div><div class="notice"><p>{e(t['market_note'])}</p></div><a class="source-link" href="{e(p['source_url'])}" rel="noopener noreferrer">{t['source']} ↗</a></div></div></section>'''
    assurance_title='Thông tin rõ ràng, nguồn gốc có thể đối chiếu.' if vi else 'Clear facts, traceable provenance.'
    assurance_copy='MARIGOLD công bố dòng Fruit Drinks được bổ sung vitamin A, B, C, D & E và không sử dụng chất bảo quản. MARIGOLD cũng công bố các sản phẩm của mình được chứng nhận Halal.' if vi else 'MARIGOLD states that its Fruit Drinks are enriched with Vitamins A, B, C, D & E and contain no preservatives. MARIGOLD also states that its products are Halal-certified.'
    body+=f'''<section class="product-assurance page-section alt-soft"><div class="shell editorial-grid"><div><p class="eyebrow">{'BẢO CHỨNG SẢN PHẨM' if vi else 'PRODUCT ASSURANCE'}</p><h2>{e(assurance_title)}</h2></div><div class="content-block"><p>{e(assurance_copy)}</p><div class="manufacturer-note"><strong>{'Nhà sản xuất & hệ thống chất lượng' if vi else 'Manufacturer & quality systems'}</strong><p>{e(claim_text('manufacturer_accreditations',locale))}</p></div></div></div></section>'''
    body+=f'''<section class="other-flavors page-section alt"><div class="shell"><div class="section-heading"><p class="eyebrow">{explore_label}</p><h2>{other_title}</h2></div><div class="mini-flavor-grid">{sibling}</div></div></section>'''
    extra=f'<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"Product","name":p["name"],"brand":{"@type":"Brand","name":"MARIGOLD"},"category":"Fruit Drink","url":BASE+path},ensure_ascii=False)}</script>'
    return base_page(locale,f'{p["name"]} — VOrigin',hero_lede,body=body,canonical_path=path,alt_path_vi=alt_vi,alt_path_en=alt_en,extra_head=extra,body_class=f'product-page product-{slug}')

def capabilities(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    data=[
      ('market-entry','market-entry','Gia nhập thị trường' if vi else 'Market Entry','Đánh giá cơ hội, xác định định vị ban đầu và xây lộ trình vào thị trường.' if vi else 'Assess the opportunity, define the initial position and shape the route to market.'),
      ('compliance','import-compliance','Nhập khẩu & Tuân thủ' if vi else 'Import & Compliance','Rà soát hồ sơ, nhãn và yêu cầu nhập khẩu dựa trên thông tin sản phẩm thực tế.' if vi else 'Review documentation, labelling and import requirements against the actual product dossier.'),
      ('distribution','distribution-development','Phát triển phân phối' if vi else 'Distribution Development','Phát triển kênh phù hợp với ngành hàng, khách hàng và từng giai đoạn tăng trưởng.' if vi else 'Develop the right channels for the category, target customer and stage of growth.'),
      ('localization','brand-localization','Bản địa hóa thương hiệu' if vi else 'Brand Localisation','Điều chỉnh thông điệp và vật liệu bán hàng cho Việt Nam mà vẫn giữ bản sắc gốc của thương hiệu.' if vi else 'Adapt messaging and sales materials for Vietnam without losing the brand’s original character.'),
      ('trade','trade-marketing','Tiếp thị thương mại' if vi else 'Trade Marketing','Chuyển chiến lược thành hiện diện thực tế tại kênh bán và điểm bán.' if vi else 'Turn strategy into a clear, credible presence across channels and at the point of sale.')]
    steps=''.join(f'''<article class="journey-step reveal" id="{sid}"><span class="journey-num">0{i}</span><span class="journey-icon">{icon_img(ic,"journey-icon-svg")}</span><div><h3>{e(title)}</h3><p>{e(copy)}</p></div></article>''' for i,(sid,ic,title,copy) in enumerate(data,1))
    page_label='NĂNG LỰC' if vi else 'CAPABILITIES'; journey_label='TỪ GIA NHẬP ĐẾN TĂNG TRƯỞNG' if vi else 'FROM ENTRY TO GROWTH'; journey_title='Một lộ trình rõ ràng, từ bước đầu tiên đến tăng trưởng bền vững.' if vi else 'A clear route from first entry to lasting growth.'; global_label='DÀNH CHO THƯƠNG HIỆU QUỐC TẾ' if vi else 'FOR GLOBAL BRANDS'
    body=page_hero(locale,page_label,t['cap_title'],t['cap_lede'],f'<a href="{r["home"]}">{t["home"]}</a> / {t["cap"]}')
    body+=f'''<section class="capability-journey page-section"><div class="shell"><div class="section-heading centered"><p class="eyebrow">{journey_label}</p><h2>{e(journey_title)}</h2><i class="bronze-rule"></i></div><div class="journey-line">{steps}</div></div></section>'''
    body+=f'''<section class="page-section dark"><div class="shell cta-panel"><div><p class="eyebrow">{global_label}</p><h2>YOUR BRAND. OUR MARKET.</h2><p>{e(t['market_copy'])}</p></div><div><a class="button button-gold" href="{r['partners']}">{e(t['market_cta'])}<span>→</span></a></div></div></section>'''
    return base_page(locale,f'{t["cap"]} — VOrigin',t['cap_lede'],'cap',body,body_class='capabilities-page')

def partners(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    criteria=[
      ('origin','Nguồn gốc rõ ràng' if vi else 'Clear Provenance','Nguồn gốc, nhà sản xuất và hồ sơ đủ rõ để kiểm chứng.' if vi else 'Provenance, manufacturer and documentation that can be clearly verified.'),
      ('premium-approach','Tiêu chuẩn rõ ràng' if vi else 'Defined Standards','Chất lượng ổn định và tiêu chuẩn đủ rõ để phát triển lâu dài.' if vi else 'Consistent quality and standards clear enough to support long-term growth.'),
      ('market-entry','Phù hợp thị trường' if vi else 'Market Relevance','Sản phẩm có sự phù hợp rõ ràng với người tiêu dùng và kênh bán tại Việt Nam.' if vi else 'A clear fit with Vietnamese consumers and the channels that serve them.'),
      ('long-term-value','Tiềm năng dài hạn' if vi else 'Long-term Potential','Tiềm năng xây dựng thương hiệu, không chỉ hoàn thành một lô hàng.' if vi else 'The potential to build a brand, not simply complete a shipment.')]
    cards=''.join(f'<article class="partner-criterion reveal"><span>{icon_img(ic,"criterion-icon-svg")}</span><h3>{e(h)}</h3><p>{e(c)}</p></article>' for ic,h,c in criteria)
    global_label='DÀNH CHO THƯƠNG HIỆU QUỐC TẾ' if vi else 'FOR GLOBAL BRANDS'; contact_cta='Bắt đầu trao đổi' if vi else 'Start a conversation'; criteria_label='ĐIỀU VORIGIN TÌM KIẾM' if vi else 'WHAT WE LOOK FOR'; criteria_title='Những điều VOrigin tìm kiếm ở một thương hiệu' if vi else 'What VOrigin looks for in a brand'; how_label='CÁCH CHÚNG TÔI LÀM VIỆC' if vi else 'HOW WE WORK'; how_title='Bắt đầu bằng việc hiểu thương hiệu.' if vi else 'We begin by understanding the brand.'
    how_copy='VOrigin bắt đầu từ chính sản phẩm — nguồn gốc, hồ sơ, tiêu chuẩn và mục tiêu phát triển — trước khi bàn đến kênh bán. Khi nền tảng đã rõ, hai bên mới cùng xác định mức độ phù hợp, lộ trình vào thị trường và phần nào cần được bản địa hóa một cách tinh tế.' if vi else 'We begin with the product itself — its provenance, documentation, standards and ambitions — before we discuss channels. That creates a clearer view of fit, the right route to market and where localisation can add value without diluting the brand.'
    body=f'''<section class="partner-hero section-dark"><div class="shell partner-hero-grid"><div class="partner-hero-copy reveal"><div class="breadcrumb"><a href="{r['home']}">{t['home']}</a> / {t['partners']}</div><p class="eyebrow">{global_label}</p><h1>YOUR BRAND.<br><span>OUR MARKET.</span></h1><p class="lede">{e(t['partners_lede'])}</p><a class="button button-gold" href="{r['contact']}?type=partner">{e(contact_cta)}<span>→</span></a></div><figure class="partner-hero-visual reveal"><img src="/assets/b2b-vorigin-premium.webp" alt="VOrigin market-entry and partnership"></figure></div></section>'''
    body+=f'''<section class="page-section"><div class="shell"><div class="section-heading centered"><p class="eyebrow">{criteria_label}</p><h2>{e(criteria_title)}</h2><i class="bronze-rule"></i></div><div class="partner-criteria-grid">{cards}</div></div></section>'''
    body+=f'''<section class="page-section alt"><div class="shell editorial-grid"><div><p class="eyebrow">{how_label}</p><h2>{e(how_title)}</h2></div><div class="content-block"><p>{e(how_copy)}</p><a class="button button-solid" href="{r['contact']}?type=partner">{e(contact_cta)}<span>→</span></a></div></div></section>'''
    return base_page(locale,f'{t["partners"]} — VOrigin',t['partners_lede'],'partners',body,body_class='partners-page')

def insights(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    topics=[('NGUỒN GỐC' if vi else 'ORIGINS','Nguồn gốc và tiêu chuẩn' if vi else 'Provenance & standards','Những điều đáng xem xét phía sau một nhãn hàng: xuất xứ, hồ sơ, tiêu chuẩn và tính nhất quán.' if vi else 'What sits behind a label: provenance, documentation, standards and consistency.'),('THỊ TRƯỜNG' if vi else 'MARKET','Thị trường Việt Nam' if vi else 'The Vietnam market','Từ khẩu vị, mức giá đến kênh bán: những yếu tố tạo nên sự phù hợp thật sự.' if vi else 'From taste and price to channels, these are the factors that shape genuine market relevance.'),('THƯƠNG HIỆU' if vi else 'BRAND','Xây dựng giá trị dài hạn' if vi else 'Building long-term value','Cách một sản phẩm nhập khẩu từng bước trở thành thương hiệu được nhớ đến.' if vi else 'How an imported product can earn a lasting place in people’s minds and in the market.')]
    cards=''.join(f'<article class="insight-card reveal"><p class="eyebrow">{e(cat)}</p><h3>{e(h)}</h3><p>{e(c)}</p><span>{e(t["coming"])}</span></article>' for cat,h,c in topics)
    body=page_hero(locale,'GÓC NHÌN' if vi else 'INSIGHTS',t['insights_title'],t['insights_lede'],f'<a href="{r["home"]}">{t["home"]}</a> / {t["insights"]}')
    body+=f'<section class="page-section"><div class="shell insight-grid">{cards}</div></section>'
    return base_page(locale,f'{t["insights"]} — VOrigin',t['insights_lede'],'insights',body,body_class='insights-page')

def contact(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    sitekey = TURNSTILE_SITE_KEY or 'TURNSTILE_SITE_KEY_REQUIRED'; turnstile_head='<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>' if TURNSTILE_SITE_KEY else ''; disabled=' disabled' if not TURNSTILE_SITE_KEY else ''
    note='' if TURNSTILE_SITE_KEY else ('<div class="notice"><p>Biểu mẫu liên hệ sẽ được bật khi website đi vào vận hành.</p></div>' if vi else '<div class="notice"><p>The contact form will be enabled when the website goes live.</p></div>')
    labels = {'name':'Họ và tên' if vi else 'Name','email':'Email','company':'Công ty' if vi else 'Company','country':'Quốc gia' if vi else 'Country','website':'Website','type':'Nội dung trao đổi' if vi else 'Enquiry type','message':'Lời nhắn' if vi else 'Message'}
    options=[('general','Trao đổi chung' if vi else 'General enquiry'),('brand-owner','Chủ thương hiệu / Gia nhập thị trường' if vi else 'Brand owner / Market entry'),('retail','Bán lẻ / Phân phối' if vi else 'Retail / Distribution'),('media','Truyền thông' if vi else 'Media')]; option_html=''.join(f'<option value="{value}">{label}</option>' for value,label in options)
    email=SITE['contact'].get('email','contact@vorigin.vn'); body=page_hero(locale,'LIÊN HỆ' if vi else 'CONTACT',t['contact_title'],t['contact_lede'],f'<a href="{r["home"]}">{t["home"]}</a> / {t["contact"]}')
    form=f'''<form data-lead-form="contact" autocomplete="on"><div class="form-grid"><div class="field"><label>{labels['name']}</label><input name="name" required maxlength="120" autocomplete="name"></div><div class="field"><label>{labels['email']}</label><input name="email" type="email" required maxlength="160" autocomplete="email"></div><div class="field"><label>{labels['company']}</label><input name="company" maxlength="160" autocomplete="organization"></div><div class="field"><label>{labels['country']}</label><input name="country" maxlength="100" autocomplete="country-name"></div><div class="field full"><label>{labels['website']}</label><input name="website" maxlength="240" inputmode="url"></div><div class="field full"><label>{labels['type']}</label><select name="inquiry_type">{option_html}</select></div><div class="honeypot" aria-hidden="true"><label>Leave empty<input name="website_confirmation" tabindex="-1" autocomplete="off"></label></div><div class="field full"><label>{labels['message']}</label><textarea name="message" required minlength="10" maxlength="4000"></textarea></div><div class="field full"><div class="cf-turnstile" data-sitekey="{e(sitekey)}"></div><button class="button button-solid" type="submit"{disabled}>{e(t['send'])}<span>→</span></button><div class="form-status" role="status" aria-live="polite"></div></div></div></form>'''
    aside_title='Một mối quan hệ tốt thường bắt đầu từ sự rõ ràng.' if vi else 'Good partnerships often start with clarity.'; aside_copy='Hãy cho chúng tôi biết về doanh nghiệp, sản phẩm và điều bạn kỳ vọng đạt được tại Việt Nam. Từ một cuộc trao đổi rõ ràng, những khả năng hợp tác đúng đắn mới có thể bắt đầu.' if vi else 'Tell us about your business, your product and what you hope to achieve in Vietnam. Clear conversations are often where the right partnerships begin.'
    body+=f'''<section class="page-section"><div class="shell contact-premium-grid"><aside class="contact-aside reveal"><p class="eyebrow">VORIGIN CORP</p><h2>{e(aside_title)}</h2><p>{e(aside_copy)}</p><a class="contact-method" href="mailto:{e(email)}"><span>{icon_img('email','contact-icon-svg')}</span><b>{e(email)}</b></a></aside><div class="form-wrap reveal">{note}{form}</div></div></section>'''
    return base_page(locale,f'{t["contact"]} — VOrigin',t['contact_lede'],'contact',body,extra_head=turnstile_head,body_class='contact-page')

def legal(locale, kind):
    t=LANG[locale]; vi=locale=='vi'; title=t['privacy_title'] if kind=='privacy' else t['terms_title']
    lede=('Trang này đang được rà soát để phản ánh chính xác cách VOrigin xử lý thông tin khi website chính thức hoạt động.' if kind=='privacy' else 'Các điều khoản sử dụng đang được rà soát để phản ánh chính xác phạm vi và cách vận hành của website.') if vi else ('This page is being reviewed to accurately reflect how VOrigin handles information when the website goes live.' if kind=='privacy' else 'These terms are being reviewed to accurately reflect the scope and operation of the website.')
    status_h='Trạng thái' if vi else 'Status'; status_p='Nội dung pháp lý chưa phải bản cuối và sẽ được VOrigin phê duyệt trước khi công bố.' if vi else 'This legal text is not final and will be approved by VOrigin before publication.'
    principle_h='Nguyên tắc hiện tại' if vi else 'Current approach'; principle_p='Website hạn chế việc thu thập dữ liệu không cần thiết. Biểu mẫu liên hệ chỉ yêu cầu thông tin phục vụ việc phản hồi yêu cầu của bạn.' if vi else 'The website limits unnecessary data collection. Contact forms request only the information needed to respond to your enquiry.'
    body=f'''<section class="page-hero"><div class="shell"><p class="eyebrow">{'PHÁP LÝ' if vi else 'LEGAL'}</p><h1>{e(title)}</h1><p class="lede">{e(lede)}</p></div></section><section class="page-section"><div class="shell legal-copy"><div class="notice"><p>{e(t['draft_legal'])}</p></div><h2>{e(status_h)}</h2><p>{e(status_p)}</p><h2>{e(principle_h)}</h2><p>{e(principle_p)}</p></div></section>'''
    return base_page(locale,f'{title} — VOrigin',lede,kind,body,body_class='legal-page')

def write(path, text):
    dst=DIST/path.lstrip('/')
    if dst.suffix:
        dst.parent.mkdir(parents=True, exist_ok=True); dst.write_text(text,encoding='utf-8')
    else:
        dst.mkdir(parents=True, exist_ok=True); (dst/'index.html').write_text(text,encoding='utf-8')

def main():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(PUBLIC/'assets', DIST/'assets')
    shutil.copy2(PUBLIC/'styles.css', DIST/'styles.css'); shutil.copy2(PUBLIC/'app.js',DIST/'app.js')
    for loc in ('vi','en'):
        write(ROUTES[loc]['home'], home(loc)); write(ROUTES[loc]['about'],about(loc)); write(ROUTES[loc]['brands'],brands(loc)); write(ROUTES[loc]['marigold'],marigold(loc)); write(ROUTES[loc]['cap'],capabilities(loc)); write(ROUTES[loc]['partners'],partners(loc)); write(ROUTES[loc]['insights'],insights(loc)); write(ROUTES[loc]['contact'],contact(loc)); write(ROUTES[loc]['privacy'],legal(loc,'privacy')); write(ROUTES[loc]['terms'],legal(loc,'terms'))
        for p in PRODUCTS: write((f'/vi/san-pham/marigold-{p["slug"]}/' if loc=='vi' else f'/en/products/marigold-{p["slug"]}/'), product_page(loc,p))
    write('/privacy/', f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="robots" content="noindex"><link rel="canonical" href="{BASE}/vi/chinh-sach-quyen-rieng/"><meta http-equiv="refresh" content="0;url=/vi/chinh-sach-quyen-rieng/"><title>Chính sách quyền riêng tư — VOrigin</title></head><body><main><h1>Chính sách quyền riêng tư</h1><p><a href="/vi/chinh-sach-quyen-rieng/">Tiếp tục</a></p></main></body></html>'); write('/terms/', f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="robots" content="noindex"><link rel="canonical" href="{BASE}/vi/dieu-khoan-su-dung/"><meta http-equiv="refresh" content="0;url=/vi/dieu-khoan-su-dung/"><title>Điều khoản sử dụng — VOrigin</title></head><body><main><h1>Điều khoản sử dụng</h1><p><a href="/vi/dieu-khoan-su-dung/">Tiếp tục</a></p></main></body></html>')
    root='''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>VOrigin</title><meta http-equiv="refresh" content="0;url=/vi/"></head><body><p><a href="/vi/">Tiếng Việt</a> · <a href="/en/">English</a></p></body></html>'''; write('/index.html',root)
    nf='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><link rel="stylesheet" href="/styles.css"><title>404 — VOrigin</title></head><body><main class="not-found"><div><h1>404</h1><p>Page not found.</p><a class="button button-outline" href="/vi/">VOrigin →</a></div></main></body></html>'''; write('/404.html',nf)
    urls=[]
    for p in DIST.rglob('index.html'):
        rel='/' + str(p.parent.relative_to(DIST)).replace('\\','/').strip('/') + '/'
        if rel=='//': rel='/'
        if rel!='/' and rel not in ('/privacy/','/terms/'): urls.append(BASE+rel)
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{e(u)}</loc></url>\n' for u in sorted(set(urls)))+'</urlset>\n'
    (DIST/'sitemap.xml').write_text(sitemap,encoding='utf-8')
    (DIST/'robots.txt').write_text(('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n') if ENV=='production' else 'User-agent: *\nDisallow: /\n',encoding='utf-8')
    (DIST/'llms.txt').write_text('''# VOrigin\n\nVOrigin (VORIGIN Corp) is the brand of CÔNG TY CỔ PHẦN TM XNK KHỞI NGUYÊN.\nPrimary domain: https://vorigin.vn\nBrand promise: From Origins to Value.\nCurrent featured brand: MARIGOLD Fruit Drinks.\n\nUse only claims published on VOrigin pages as VOrigin-approved statements. Do not infer health, nutrition, certification, origin, distribution-rights or partnership claims beyond published content.\n''',encoding='utf-8')
    print(f'Built {len(list(DIST.rglob("*.html")))} HTML pages in {DIST} [SITE_ENV={ENV}]')

if __name__=='__main__': main()
