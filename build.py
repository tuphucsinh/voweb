#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, html
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote
from scripts.optimize_images import RESPONSIVE_SPECS

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
CONTACT_FORMS_ENABLED = bool(SITE.get('contact_forms_enabled', False))
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


def render_b2b_picture(css_class, alt_text, loading='lazy'):
    """Render the shared responsive B2B image contract."""
    if loading not in {'lazy', 'eager'}:
        raise ValueError(f'unsupported image loading mode: {loading}')
    sizes = '(max-width: 820px) 100vw, 58vw'
    priority = ' fetchpriority="high"' if loading == 'eager' else ''
    return (
        f'<picture class="b2b-picture {e(css_class)}">'
        f'<source type="image/webp" '
        f'srcset="/assets/b2b-vorigin-partner-640w.webp 640w, '
        f'/assets/b2b-vorigin-partner-1020w.webp 1020w" sizes="{sizes}">'
        f'<img class="{e(css_class)}" '
        f'src="/assets/b2b-vorigin-partner-1020w.webp" '
        f'alt="{e(alt_text)}" width="1020" height="818" '
        f'loading="{loading}" decoding="async"{priority}>'
        '</picture>'
    )


def render_market_visual(locale):
    """Render canonical visual for homepage international brands market section."""
    alt = 'Thùng container mang thương hiệu VOrigin tại cảng biển lúc bình minh' if locale == 'vi' else 'VOrigin branded container at a port at sunrise'
    return f'<img class="market-visual-image" src="/assets/Container1.png" alt="{e(alt)}" width="1672" height="941" loading="lazy" decoding="async">'


@dataclass(frozen=True)
class ImagePolicy:
    widths: tuple[int, ...]
    sizes: str
    loading: str = 'lazy'
    fetchpriority: str = 'auto'
    css_class: str = ''


RESPONSIVE_POLICIES = {
    'home_hero': ImagePolicy((480, 768), '(max-width: 820px) 100vw, 52vw', 'eager', 'high', 'hero-responsive'),
    'lineup': ImagePolicy((480, 768), '(max-width: 820px) 100vw, 72vw', 'lazy', 'auto', 'lineup-responsive'),
    'marigold_hero': ImagePolicy((480, 768), '(max-width: 820px) 100vw, 64vw', 'eager', 'high', 'marigold-lineup-responsive'),
    'product_hero': ImagePolicy((390, 640), '(max-width: 820px) 100vw, 54vw', 'eager', 'high', 'product-responsive'),
    'flavor_card': ImagePolicy((390, 640), '(max-width: 580px) 80vw, 25vw', 'lazy', 'auto', 'flavor-responsive'),
    'mini_flavor': ImagePolicy((390, 640), '(max-width: 580px) 74vw, 30vw', 'lazy', 'auto', 'mini-flavor-responsive'),
}


def responsive_picture(asset_key: str, alt: str, policy: ImagePolicy) -> str:
    """Render one deterministic responsive picture contract for a managed asset."""
    spec = RESPONSIVE_SPECS.get(asset_key)
    if spec is None:
        raise KeyError(f'unknown responsive asset: {asset_key}')
    available = {variant.width: variant.filename for variant in spec.variants}
    if any(width not in available for width in policy.widths):
        raise ValueError(f'policy widths not generated for {asset_key}: {policy.widths}')
    if policy.loading not in {'lazy', 'eager'}:
        raise ValueError(f'unsupported image loading mode: {policy.loading}')
    srcset = ', '.join(f'/assets/{available[width]} {width}w' for width in policy.widths)
    srcset += f', /assets/{spec.source_filename} {spec.source_size[0]}w'
    priority = f' fetchpriority="{e(policy.fetchpriority)}"' if policy.fetchpriority in {'high', 'low'} else ''
    css_class = e(policy.css_class)
    return (
        f'<picture class="responsive-picture {css_class}">'
        f'<source type="image/webp" srcset="{srcset}" sizes="{e(policy.sizes)}">'
        f'<img class="{css_class}" src="/assets/{spec.source_filename}" '
        f'alt="{e(alt)}" width="{spec.source_size[0]}" height="{spec.source_size[1]}" '
        f'loading="{policy.loading}" decoding="async"{priority}>'
        '</picture>'
    )


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
    email=contact.get('email','')
    phone=contact.get('phone','')
    digits=''.join(c for c in phone if c.isdigit())
    phone_tel=f'+{digits}' if digits else ''
    address=contact.get('address_vi' if locale=='vi' else 'address_en','')
    city=contact.get('city_vi' if locale=='vi' else 'city_en','')
    story_label='Câu chuyện thương hiệu' if locale=='vi' else 'Our story'
    portfolio_label='Danh mục tuyển chọn' if locale=='vi' else 'Curated portfolio'
    market_label='Gia nhập thị trường' if locale=='vi' else 'Market Entry'
    compliance_label='Nhập khẩu &amp; tuân thủ' if locale=='vi' else 'Import &amp; Compliance'
    distribution_label='Phát triển phân phối' if locale=='vi' else 'Distribution Development'
    partner_label='Dành cho thương hiệu quốc tế' if locale=='vi' else 'For international brands'
    return f'''<footer class="site-footer" id="footer"><div class="shell footer-grid">
<div class="footer-brand"><div class="footer-logo-lockup"><img src="/assets/vorigin-logo-footer-bronze.svg" alt="VOrigin" width="700" height="173" loading="lazy"><span>FROM ORIGINS TO VALUE</span></div><strong>{e(SITE['legal_name'])}</strong><p>VORIGIN Corp</p><div class="footer-contact"><div class="footer-contact__item"><a href="https://vorigin.vn">VOrigin.vn</a></div><div class="footer-contact__item"><a href="mailto:{e(email)}">{e(email)}</a></div><div class="footer-contact__item"><a href="tel:{phone_tel}">{e(phone)}</a></div><div class="footer-contact__address"><span>{e(address)}</span><span>{e(city)}</span></div></div></div>
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
    head = f'''<!doctype html><html lang="{lang_attr}" data-contact-forms="{'enabled' if CONTACT_FORMS_ENABLED else 'disabled'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#f3eee4"><meta name="robots" content="{robots}">
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
    benefits=''.join(
      f'<article class="why-value-row reveal" role="listitem"><div class="why-value-meta"><span class="why-value-number">0{i+1}</span><span class="why-value-icon" aria-hidden="true">{icon_img(icon, "why-value-icon-svg")}</span></div><div class="why-value-copy"><h3>{e(a)}</h3><p>{e(b)}</p></div></article>'
      for i,(icon,(a,b)) in enumerate(zip(['trusted-partner','local-expertise','long-term-value','premium-approach','grow-together'],partner_copy))
    )
    hero_eyebrow='NGUỒN GỐC ĐÁNG TIN. GIÁ TRỊ BỀN LÂU.' if vi else 'TRUSTED ORIGINS. LASTING VALUE.'
    story_eyebrow='TUYỂN CHỌN BỞI VORIGIN' if vi else 'CURATED BY VORIGIN'
    featured_label='THƯƠNG HIỆU NỔI BẬT' if vi else 'FEATURED BRAND'
    portfolio_label='DANH MỤC THƯƠNG HIỆU' if vi else 'OUR PORTFOLIO'
    portfolio_title='Danh mục chọn lọc,<br>lớn lên từng bước' if vi else 'A growing portfolio<br>of carefully chosen brands'
    global_label='DÀNH CHO THƯƠNG HIỆU QUỐC TẾ' if vi else 'FOR INTERNATIONAL BRANDS'
    services=[('market-entry','Gia nhập<br>thị trường' if vi else 'Market Entry'),('import-compliance','Nhập khẩu &amp;<br>tuân thủ' if vi else 'Import &amp;<br>Compliance'),('distribution-development','Phát triển<br>phân phối' if vi else 'Distribution<br>Development'),('brand-localization','Bản địa hóa<br>thương hiệu' if vi else 'Brand<br>Localisation'),('trade-marketing','Tiếp thị<br>thương mại' if vi else 'Trade<br>Marketing')]
    service_html=''.join(f'<span><i class="service-icon">{icon_img(ic,"service-icon-svg")}</i><small>{label}</small></span>' for ic,label in services)
    body=f'''<section class="hero section-light"><div class="hero-grid"><div class="hero-copy reveal"><div class="hero-copy-inner"><p class="eyebrow">{hero_eyebrow}</p><h1><span class="hero-title-line">From Origins</span> <span class="hero-title-line hero-title-accent">to Value.</span></h1><p class="hero-lead">{e(t['hero_lead'])}</p><div class="hero-actions"><a href="{r['about']}" class="button button-solid">{e(t['hero_primary'])}<span>→</span></a><a href="{r['brands']}" class="text-action"><span class="play">{icon_img("play-circle","play-icon-svg")}</span>{e(t['hero_secondary'])}</a></div></div></div><figure class="hero-visual reveal"><figcaption class="visual-label">{featured_label} — MARIGOLD</figcaption><img src="/assets/Hero1.png" alt="MARIGOLD Orange Fruit Drink" width="1672" height="941" loading="eager" decoding="async" fetchpriority="high"></figure></div></section>
<section class="story section-light" id="story" aria-labelledby="story-title"><div class="shell"><div class="section-heading story-heading reveal"><p class="eyebrow">{story_eyebrow}</p><h2 id="story-title">{e(t['story_title'])}</h2><i class="bronze-rule"></i></div><div class="story-grid">
{story_card('story-origin.png','Nguồn gốc' if vi else 'Origin',t['origin'],'origin','01','story-card-origin')}{story_card('story-nature.png','Tự nhiên' if vi else 'Nature',t['nature'],'nature','02','story-card-nature')}{story_card('story-craft.png','Tiêu chuẩn' if vi else 'Craft',t['craft'],'craft','03','story-card-craft')}{story_card('story-value.png','Giá trị' if vi else 'Value',t['value'],'value','04','story-card-value')}</div></div></section>
<section class="featured section-soft" id="brands"><div class="shell featured-grid"><div class="featured-copy reveal"><div class="featured-copy-inner"><p class="eyebrow">{featured_label}</p><h2>MARIGOLD</h2><p>{e(t['featured_copy'])}</p><div class="featured-trust">{marigold_trust_chips(locale, True)}</div><a href="{r['marigold']}" class="button button-outline">{e(t['discover_marigold'])}<span>→</span></a></div></div><figure class="lineup reveal"><div class="lineup-surface"><img class="lineup-image" src="/assets/Brand1.png" alt="MARIGOLD Fruit Drink Apple, Orange, Mango and Grape" width="1672" height="941" loading="lazy" decoding="async"></div></figure></div></section>
<section class="portfolio section-light"><div class="shell portfolio-grid"><div class="portfolio-copy reveal"><div class="portfolio-copy-header"><p class="eyebrow">{portfolio_label}</p><h2>{portfolio_title}</h2></div><div class="portfolio-copy-meta"><p>{e(t['portfolio_copy'])}</p><a class="button button-outline" href="{r['brands']}">{e(t['portfolio_cta'])}<span>→</span></a></div></div><div class="portfolio-cards" role="list">{portfolio_cards(locale)}</div></div></section>
<section class="why-partner section-light" id="partners" aria-labelledby="why-title"><div class="shell why-value-index"><div class="why-value-intro reveal"><h2 id="why-title">{e(t['why'])}</h2><i class="bronze-rule transition-rule"></i></div><div class="why-value-list" role="list">{benefits}</div></div></section>
<section class="market section-dark" id="market"><div class="shell market-grid"><figure class="market-visual reveal">{render_market_visual(locale)}</figure><div class="market-copy reveal"><p class="eyebrow">{global_label}</p><h2>YOUR BRAND<br>OUR MARKET</h2><p>{e(t['market_copy'])}</p><div class="services">{service_html}</div><a class="button button-gold" href="{r['partners']}">{e(t['market_cta'])}<span>→</span></a></div></div></section>'''
    return base_page(locale,'VOrigin — From Origins to Value',t['hero_lead'],'home',body)

def story_card(img,title,copy,icon,index='01',modifier=''):
    if not modifier:
        modifier = f'story-card-{icon}'
    dimensions = {
        'story-origin.png': (1774, 887),
        'story-nature.png': (1774, 887),
        'story-craft.png': (1774, 887),
        'story-value.png': (1774, 887),
        'story-origin.webp': (210, 132),
        'story-nature.webp': (210, 132),
        'story-craft.webp': (210, 132),
        'story-value.webp': (215, 132),
    }
    width, height = dimensions.get(img, (1774, 887))
    return (
        f'<article class="story-card {e(modifier)} reveal">'
        f'<div class="story-media">'
        f'<img src="/assets/{img}" alt="{e(title)}" width="{width}" height="{height}" loading="lazy" decoding="async">'
        f'</div>'
        f'<div class="story-body">'
        f'<div class="story-meta">'
        f'<span class="story-index">{e(index)}</span>'
        f'<span class="story-hairline" aria-hidden="true"></span>'
        f'<span class="story-icon" aria-hidden="true">{icon_img(icon, "story-icon-svg")}</span>'
        f'</div>'
        f'<h3 class="story-title">{e(title)}</h3>'
        f'<p class="story-copy">{e(copy)}</p>'
        f'</div>'
        f'</article>'
    )

def portfolio_cards(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    dirs=([('02','Đồ uống chọn lọc','PREMIUM BEVERAGES'),('03','Thực phẩm tuyển chọn','FINE FOODS'),('04','Tự nhiên & Sống khỏe','NATURAL & WELLNESS')] if vi else [('02','Premium Beverages','PREMIUM BEVERAGES'),('03','Fine Foods','FINE FOODS'),('04','Natural & Wellness','NATURAL & WELLNESS')])
    featured='THƯƠNG HIỆU NỔI BẬT' if vi else 'FEATURED BRAND'
    direction='ĐỊNH HƯỚNG DANH MỤC' if vi else 'PORTFOLIO DIRECTION'
    cards=f'''<a class="brand-card brand-card-featured reveal" role="listitem" aria-label="MARIGOLD — {featured}" href="{r['marigold']}"><div class="brand-card-top"><span class="brand-card-index">01</span><span class="brand-card-kicker">{featured}</span></div><div class="brand-card-content brand-card-identity"><img class="marigold-logo-img" src="/assets/marigold-logo-premium-transparent.png" alt="MARIGOLD" width="1600" height="531" loading="lazy" decoding="async"></div><div class="brand-card-bottom"><p class="brand-card-meta">Fruit Drinks</p><span class="brand-card-cta" aria-hidden="true">{e(t['discover_marigold'])} <span>→</span></span></div></a>'''
    for index,name,english in dirs:
        cards += f'<article class="brand-card brand-card-direction reveal" role="listitem"><div class="brand-card-top"><span class="brand-card-index">{index}</span><span class="brand-card-kicker">{english}</span></div><div class="brand-card-content"><h3>{e(name)}</h3></div><div class="brand-card-bottom"><p class="direction-label">{direction}</p></div></article>'
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
    body+=f'''<section class="brand-story-premium page-section"><div class="shell brand-story-grid"><div class="brand-story-statement reveal"><p class="eyebrow">FROM ORIGINS TO VALUE</p><h2>{e(lead)}</h2><p>{e(story)}</p></div><figure class="brand-story-visual reveal"><img src="/assets/story-origin.webp" alt="VOrigin origin landscape" width="210" height="132" loading="lazy"><figcaption>{'NGUỒN GỐC → CHỌN LỌC → GIÁ TRỊ' if vi else 'ORIGIN → SELECTION → VALUE'}</figcaption></figure></div></section>'''
    body+=f'''<section class="page-section alt" id="standard"><div class="shell"><div class="section-heading centered"><p class="eyebrow">{standard_eyebrow}</p><h2>{e(t['standard'])}</h2><i class="bronze-rule"></i></div><div class="standard-grid">{cards}</div></div></section>'''
    body+=f'''<section class="page-section"><div class="shell editorial-grid"><div><p class="eyebrow">{'TẦM NHÌN' if vi else 'VISION'}</p><h2>{e(t['vision'])}</h2></div><div class="content-block"><p>{e(vision_copy)}</p></div></div></section>'''
    return base_page(locale,f'{t["about"]} — VOrigin',t['about_lede'],'about',body,body_class='about-page')

def brands(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    page_label='DANH MỤC CHỌN LỌC' if vi else 'CURATED PORTFOLIO'; feature_label='THƯƠNG HIỆU NỔI BẬT' if vi else 'FEATURED BRAND'
    feature_copy='Thương hiệu nổi bật đầu tiên trong danh mục VOrigin, mở đầu cho một hành trình danh mục được xây dựng có chọn lọc.' if vi else 'The first featured brand in VOrigin’s portfolio, marking the beginning of a carefully built brand journey.'
    next_label='DANH MỤC ĐANG MỞ RỘNG' if vi else 'A GROWING PORTFOLIO'; next_title='Danh mục chọn lọc,<br>lớn lên từng bước' if vi else 'A growing portfolio<br>of carefully chosen brands'
    body=page_hero(locale,page_label,t['brands_title'],t['brands_lede'],f'<a href="{r["home"]}">{t["home"]}</a> / {t["brands"]}')
    body+=f'''<section class="featured section-soft"><div class="shell featured-grid"><div class="featured-copy reveal"><div class="featured-copy-inner"><p class="eyebrow">{feature_label}</p><h2>MARIGOLD</h2><p>{e(feature_copy)}</p><div class="featured-trust">{marigold_trust_chips(locale, True)}</div><a href="{r['marigold']}" class="button button-outline">{e(t['view'])}<span>→</span></a></div></div><figure class="lineup reveal"><div class="lineup-surface"><img class="lineup-image" src="/assets/Brand1.png" alt="MARIGOLD Fruit Drinks Apple, Orange, Mango and Grape" width="1672" height="941" loading="lazy" decoding="async"></div></figure></div></section>'''
    body+=f'''<section class="portfolio section-light"><div class="shell"><div class="section-heading centered"><p class="eyebrow">{next_label}</p><h2>{next_title}</h2><i class="bronze-rule"></i></div><div class="portfolio-cards" role="list">{portfolio_cards(locale)}</div></div></section>'''
    return base_page(locale,f'{t["brands"]} — VOrigin',t['brands_lede'],'brands',body,body_class='brands-page')

def marigold(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    summary=BRAND['summary_vi' if vi else 'summary_en']; note=BRAND['source_note_vi' if vi else 'source_note_en']
    flavors=[('apple','Apple','#8aa073'),('orange','Orange','#d88938'),('mango','Mango','#d5a237'),('grape','Grape','#765b7b')]
    pmap={p['slug']:p for p in PRODUCTS}; flavor_cards=''
    for slug,label,color in flavors:
        p=pmap.get(slug,{'pack':'250ml x 6'}); path=(f'/vi/san-pham/marigold-{slug}/' if vi else f'/en/products/marigold-{slug}/')
        flavor_cards+=f'''<a class="flavor-card flavor-{slug} reveal" href="{path}" style="--flavor:{color}"><div class="flavor-visual">{responsive_picture(f'marigold-{slug}-real', f'MARIGOLD {label} Fruit Drink', RESPONSIVE_POLICIES['flavor_card'])}</div><div class="flavor-copy"><p class="eyebrow">{e(p['pack'])}</p><h3>{label}</h3><span>{e(t['view'])} →</span></div></a>'''
    feature_label='THƯƠNG HIỆU NỔI BẬT' if vi else 'FEATURED BRAND'; flavour_label='KHÁM PHÁ HƯƠNG VỊ' if vi else 'EXPLORE THE FLAVOURS'
    flavour_title='Bốn hương vị, mỗi vị một nét riêng.' if vi else 'Four flavours, each with its own character.'; curated_label='TUYỂN CHỌN BỞI VORIGIN' if vi else 'CURATED BY VORIGIN'
    editorial_title='Một thương hiệu nổi bật. Khởi đầu cho một danh mục rộng hơn.' if vi else 'A featured brand. The beginning of a broader portfolio.'
    editorial_copy='MARIGOLD là thương hiệu nổi bật đầu tiên trong danh mục VOrigin. Dù danh mục mở rộng, nguyên tắc chọn lựa vẫn không đổi: nguồn gốc rõ ràng, tiêu chuẩn phù hợp và giá trị bền lâu.' if vi else 'MARIGOLD is the first featured brand in VOrigin’s portfolio. As the portfolio grows, the principles stay the same: clear provenance, relevant standards and lasting value.'
    body=f'''<section class="featured section-soft marigold-detail-featured"><div class="shell featured-grid"><div class="featured-copy marigold-hero-copy reveal"><div class="featured-copy-inner"><div class="breadcrumb"><a href="{r['home']}">{t['home']}</a> / <a href="{r['brands']}">{t['brands']}</a> / MARIGOLD</div><p class="eyebrow">{feature_label}</p><h1>MARIGOLD</h1><p class="lede">{e(summary)}</p><div class="featured-trust">{marigold_trust_chips(locale, True)}</div><a class="source-link" href="{e(BRAND['source_url'])}" rel="noopener noreferrer">{t['source']} ↗</a></div></div><figure class="lineup reveal"><div class="lineup-surface"><img class="lineup-image" src="/assets/Brand1.png" alt="MARIGOLD Fruit Drinks Apple, Orange, Mango and Grape" width="1672" height="941" loading="eager" decoding="async" fetchpriority="high"></div></figure></div></section>'''
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
        other_key=f'marigold-{other["slug"]}-real'; other_alt=f'MARIGOLD {other["flavor"]}'
        sibling+=f'<a href="{opath}" class="mini-flavor">{responsive_picture(other_key, other_alt, RESPONSIVE_POLICIES["mini_flavor"])}<span>{e(other["flavor"])}</span></a>'
    hero_label='MARIGOLD — THỨC UỐNG TRÁI CÂY' if vi else 'MARIGOLD FRUIT DRINK'; hero_lede='Một trong bốn hương vị của dòng MARIGOLD Fruit Drinks.' if vi else 'Part of the four-flavour MARIGOLD Fruit Drinks range.'
    category='Thức uống trái cây' if vi else 'Fruit Drink'; flavor_label='Hương vị' if vi else 'Flavour'; category_label='Nhóm sản phẩm' if vi else 'Category'
    product_info_label='THÔNG TIN SẢN PHẨM' if vi else 'PRODUCT INFORMATION'; explore_label='KHÁM PHÁ THÊM' if vi else 'EXPLORE MORE'; other_title='Các hương vị khác' if vi else 'Other flavours'
    body=f'''<section class="product-hero" style="--flavor:{accent}"><div class="shell product-hero-grid"><div class="product-hero-copy reveal"><div class="breadcrumb"><a href="{r['home']}">{t['home']}</a> / <a href="{r['marigold']}">MARIGOLD</a> / {e(p['flavor'])}</div><p class="eyebrow">{hero_label}</p><h1>{e(p['flavor'])}</h1><p class="lede">{e(hero_lede)}</p><div class="product-trust">{marigold_trust_chips(locale, True)}</div><div class="product-meta"><span>{e(p['pack'])}</span><span>{category}</span></div></div><figure class="product-hero-visual reveal">{responsive_picture(f'marigold-{slug}-real', e(p['name']), RESPONSIVE_POLICIES['product_hero'])}</figure></div></section>'''
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
    contact_href = f"{r['contact']}?type=partner"
    contact_cta = 'Bắt đầu trao đổi' if vi else 'Start a conversation'
    hero_eyebrow = 'DÀNH CHO THƯƠNG HIỆU QUỐC TẾ' if vi else 'FOR INTERNATIONAL BRANDS'
    hero_img_alt = 'Thùng container mang thương hiệu VOrigin tại cảng biển lúc bình minh' if vi else 'VOrigin branded container at a port at sunrise'

    # 1. Hero section
    hero_html = f'''<section class="partners-hero" aria-label="{e(t['partners'])}">
  <div class="shell partners-hero-grid">
    <div class="partners-hero-copy reveal">
      <div class="breadcrumb"><a href="{r['home']}">{t['home']}</a> / {t['partners']}</div>
      <p class="eyebrow">{e(hero_eyebrow)}</p>
      <h1 class="partners-hero-title"><span class="partners-hero-title-line partners-hero-title-line-1">YOUR BRAND</span><span class="partners-hero-title-line partners-hero-title-line-2">OUR MARKET</span></h1>
      <p class="lede partners-hero-lede">{e(t['partners_lede'])}</p>
      <div class="partners-hero-actions">
        <a class="button button-gold partners-cta" href="{contact_href}">{e(contact_cta)}<span>→</span></a>
      </div>
    </div>
    <figure class="partners-hero-visual reveal">
      <img class="partners-hero-image" src="/assets/Container1.png" alt="{e(hero_img_alt)}" width="1672" height="941" loading="eager" decoding="async" fetchpriority="high">
    </figure>
  </div>
</section>'''

    # 2. Value pillars section (Four pillars from source-gated criteria)
    pillars_eyebrow = 'GIÁ TRỊ CỐT LÕI' if vi else 'CORE VALUES'
    pillars_title = 'Nền tảng cho sự hợp tác bền vững' if vi else 'Foundations for a lasting partnership'
    pillars_data = [
        ('origin', 'Nguồn gốc rõ ràng' if vi else 'Clear Provenance', 'Nguồn gốc, nhà sản xuất và hồ sơ đủ rõ để kiểm chứng.' if vi else 'Provenance, manufacturer and documentation that can be clearly verified.'),
        ('premium-approach', 'Tiêu chuẩn rõ ràng' if vi else 'Defined Standards', 'Chất lượng ổn định và tiêu chuẩn đủ rõ để phát triển lâu dài.' if vi else 'Consistent quality and standards clear enough to support long-term growth.'),
        ('market-entry', 'Phù hợp thị trường' if vi else 'Market Relevance', 'Sản phẩm có sự phù hợp rõ ràng với người tiêu dùng và kênh bán tại Việt Nam.' if vi else 'A clear fit with Vietnamese consumers and the channels that serve them.'),
        ('long-term-value', 'Tiềm năng dài hạn' if vi else 'Long-term Potential', 'Tiềm năng xây dựng thương hiệu, không chỉ hoàn thành một lô hàng.' if vi else 'The potential to build a brand, not simply complete a shipment.')
    ]
    pillars_cards = ''.join(
        f'''<article class="partners-pillar-card reveal">
  <span class="partners-pillar-icon">{icon_img(ic, "pillar-icon-svg")}</span>
  <h3>{e(heading)}</h3>
  <p>{e(desc)}</p>
</article>'''
        for ic, heading, desc in pillars_data
    )
    pillars_html = f'''<section class="partners-pillars page-section" aria-labelledby="partners-pillars-heading">
  <div class="shell">
    <div class="section-heading centered reveal">
      <p class="eyebrow">{e(pillars_eyebrow)}</p>
      <h2 id="partners-pillars-heading">{e(pillars_title)}</h2>
      <i class="bronze-rule"></i>
    </div>
    <div class="partners-pillars-grid">
      {pillars_cards}
    </div>
  </div>
</section>'''

    # 3. Ideal partner section (Editorial split stating who VOrigin works with)
    ideal_eyebrow = 'ĐỐI TÁC PHÙ HỢP' if vi else 'IDEAL PARTNER'
    ideal_title = 'Những thương hiệu VOrigin đồng hành' if vi else 'Who we work with'
    ideal_lede = (
        'VOrigin tìm kiếm sự đồng điệu về tiêu chuẩn và tầm nhìn dài hạn. Chúng tôi đồng hành cùng các thương hiệu đáp ứng bốn tiêu chuẩn then chốt để phát triển bền vững tại Việt Nam.'
        if vi else
        'VOrigin partners with brand owners who share a commitment to standards and enduring value. We focus on brands meeting four essential qualifications for the Vietnam market.'
    )
    ideal_criteria = [
        ('Nguồn gốc minh bạch' if vi else 'Clear provenance',
         'Sản phẩm có nguồn gốc rõ ràng và hồ sơ đủ chi tiết để đối chiếu.'
         if vi else
         'Clear provenance and documentation that can be understood and verified.'),
        ('Tiêu chuẩn nhất quán' if vi else 'Consistent standards',
         'Tiêu chuẩn sản phẩm rõ ràng, nhất quán và phù hợp với định hướng phát triển dài hạn.'
         if vi else
         'Consistent standards that support a considered, long-term market presence.'),
        ('Phù hợp thị trường Việt Nam' if vi else 'Genuine market fit',
         'Sản phẩm có sự phù hợp rõ ràng với người tiêu dùng và các kênh bán tại Việt Nam.'
         if vi else
         'A genuine fit with Vietnamese consumers and the channels that serve them.'),
        ('Dư địa xây dựng thương hiệu' if vi else 'Room to build a lasting brand',
         'Có dư địa để cùng xây dựng một hiện diện bền vững trên thị trường.'
         if vi else
         'Room to build an enduring market presence together, beyond a single shipment.')
    ]
    ideal_list_items = ''.join(
        f'''<li class="partners-ideal-item reveal">
  <strong class="partners-ideal-item-title">{e(item_title)}</strong>
  <p class="partners-ideal-item-desc">{e(item_desc)}</p>
</li>'''
        for item_title, item_desc in ideal_criteria
    )
    ideal_html = f'''<section class="partners-ideal page-section alt" aria-labelledby="partners-ideal-heading">
  <div class="shell partners-ideal-grid editorial-grid">
    <div class="partners-ideal-header reveal">
      <p class="eyebrow">{e(ideal_eyebrow)}</p>
      <h2 id="partners-ideal-heading">{e(ideal_title)}</h2>
      <p class="partners-ideal-lede">{e(ideal_lede)}</p>
    </div>
    <div class="content-block partners-ideal-content">
      <ul class="partners-ideal-list" role="list">
        {ideal_list_items}
      </ul>
    </div>
  </div>
</section>'''

    # 4. How we build the market section (Ordered 5-step process using existing capability meanings and icons)
    process_eyebrow = 'LỘ TRÌNH PHÁT TRIỂN' if vi else 'ROUTE TO MARKET'
    process_title = 'Cách chúng tôi cùng xây dựng thị trường' if vi else 'How we build the market'
    process_steps = [
        ('market-entry',
         'Gia nhập thị trường' if vi else 'Market Assessment & Entry',
         'Đánh giá cơ hội, xác định định vị ban đầu và xây lộ trình vào thị trường phù hợp với năng lực sản phẩm.'
         if vi else
         'Assess market opportunity, define initial positioning, and shape a clear entry roadmap tailored to the product.'),
        ('import-compliance',
         'Nhập khẩu & Tuân thủ' if vi else 'Import & Compliance',
         'Rà soát hồ sơ, công bố, ghi nhãn và đáp ứng các yêu cầu nhập khẩu dựa trên thông tin kỹ thuật thực tế.'
         if vi else
         'Review dossiers, product declarations, labelling, and import regulatory requirements against technical specifications.'),
        ('distribution-development',
         'Phát triển phân phối' if vi else 'Distribution Development',
         'Phát triển các kênh bán phù hợp với ngành hàng, khách hàng mục tiêu và từng giai đoạn tăng trưởng thị trường.'
         if vi else
         'Develop targeted distribution channels aligned with the category, target consumers, and stages of growth.'),
        ('brand-localization',
         'Bản địa hóa thương hiệu' if vi else 'Brand Localisation',
         'Điều chỉnh thông điệp và vật liệu tiếp thị phù hợp văn hóa tiêu dùng Việt Nam mà vẫn gìn giữ bản sắc gốc của thương hiệu.'
         if vi else
         'Adapt brand messaging and sales materials for the Vietnamese market while safeguarding original brand identity.'),
        ('trade-marketing',
         'Tiếp thị thương mại' if vi else 'Trade Marketing',
         'Chuyển chiến lược thành hiện diện trực quan tại kênh phân phối và điểm bán lẻ để xây dựng nhận biết thương hiệu bền vững.'
         if vi else
         'Translate strategy into credible retail presence across sales channels and points of sale to foster brand awareness.')
    ]
    process_items = ''.join(
        f'''<li class="partners-process-step reveal">
  <div class="partners-process-step-top">
    <span class="partners-process-num" aria-hidden="true">0{i}</span>
    <span class="partners-process-icon">{icon_img(ic, "process-icon-svg")}</span>
  </div>
  <div class="partners-process-step-content">
    <h3>{e(step_title)}</h3>
    <p>{e(step_desc)}</p>
  </div>
</li>'''
        for i, (ic, step_title, step_desc) in enumerate(process_steps, 1)
    )
    process_html = f'''<section class="partners-process page-section" aria-labelledby="partners-process-heading">
  <div class="shell">
    <div class="section-heading centered reveal">
      <p class="eyebrow">{e(process_eyebrow)}</p>
      <h2 id="partners-process-heading">{e(process_title)}</h2>
      <i class="bronze-rule"></i>
    </div>
    <ol class="partners-process-list">
      {process_items}
    </ol>
  </div>
</section>'''

    # 5. Partnership expectations section (Three concise expectation points)
    expectations_eyebrow = 'NGUYÊN TẮC ĐỒNG HÀNH' if vi else 'PARTNERSHIP PRINCIPLES'
    expectations_title = 'Kỳ vọng trong quan hệ hợp tác' if vi else 'Partnership expectations'
    expectations_data = [
        ('trusted-partner',
         'Rõ ràng ngay từ đầu' if vi else 'Clarity from the start',
         'Bắt đầu bằng việc tìm hiểu kỹ sản phẩm, nguồn gốc và mục tiêu thực tế trước khi bàn đến các cam kết thương mại.'
         if vi else
         'We begin by thoroughly understanding the product, provenance, and realistic goals before discussing commercial steps.'),
        ('market-entry',
         'Lộ trình thị trường thực tế' if vi else 'A practical route to market',
         'Xây dựng kế hoạch gia nhập khả thi dựa trên nhịp vận hành của thị trường, năng lực tuân thủ và các kênh bán phù hợp.'
         if vi else
         'Shaping an actionable market route grounded in actual retail dynamics, regulatory compliance, and channel fit.'),
        ('grow-together',
         'Định hướng tăng trưởng dài hạn' if vi else 'Long-term growth orientation',
         'Ưu tiên nền tảng bền vững và sự ổn định của thương hiệu, hướng đến sự hiện diện lâu dài thay vì doanh số ngắn hạn.'
         if vi else
         'Prioritising lasting brand equity and steady growth over quick, transactional volume.')
    ]
    expectations_cards = ''.join(
        f'''<article class="partners-expectation-card reveal">
  <span class="partners-expectation-icon">{icon_img(ic, "expectation-icon-svg")}</span>
  <h3>{e(heading)}</h3>
  <p>{e(desc)}</p>
</article>'''
        for ic, heading, desc in expectations_data
    )
    expectations_html = f'''<section class="partners-expectations page-section alt" aria-labelledby="partners-expectations-heading">
  <div class="shell">
    <div class="section-heading centered reveal">
      <p class="eyebrow">{e(expectations_eyebrow)}</p>
      <h2 id="partners-expectations-heading">{e(expectations_title)}</h2>
      <i class="bronze-rule"></i>
    </div>
    <div class="partners-expectations-grid">
      {expectations_cards}
    </div>
  </div>
</section>'''

    # 6. Final CTA section (Localized invitation to start a focused conversation)
    cta_eyebrow = 'HỢP TÁC CÙNG VORIGIN' if vi else 'PARTNER WITH VORIGIN'
    cta_title = 'Bắt đầu từ một cuộc trao đổi rõ ràng' if vi else 'Start with a clear conversation'
    cta_lede = (
        'Nếu bạn đại diện cho một thương hiệu quốc tế đang tìm hiểu cơ hội phát triển bền vững tại Việt Nam, hãy kết nối cùng VOrigin để bắt đầu một cuộc trao đổi đúng trọng tâm.'
        if vi else
        'If you represent an international brand exploring sustainable growth in Vietnam, connect with VOrigin to begin a focused, practical conversation.'
    )
    cta_html = f'''<section class="partners-cta section-dark" aria-labelledby="partners-cta-heading">
  <div class="shell partners-cta-wrap reveal">
    <p class="eyebrow">{e(cta_eyebrow)}</p>
    <h2 id="partners-cta-heading">{e(cta_title)}</h2>
    <p class="partners-cta-lede">{e(cta_lede)}</p>
    <div class="partners-cta-actions">
      <a class="button button-gold partners-cta-button" href="{contact_href}">{e(contact_cta)}<span>→</span></a>
    </div>
  </div>
</section>'''

    body = f"{hero_html}\n{pillars_html}\n{ideal_html}\n{process_html}\n{expectations_html}\n{cta_html}"
    return base_page(locale, f'{t["partners"]} — VOrigin', t['partners_lede'], 'partners', body, body_class='partners-page')

def insights(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    topics=[('NGUỒN GỐC' if vi else 'ORIGINS','Nguồn gốc và tiêu chuẩn' if vi else 'Provenance & standards','Những điều đáng xem xét phía sau một nhãn hàng: xuất xứ, hồ sơ, tiêu chuẩn và tính nhất quán.' if vi else 'What sits behind a label: provenance, documentation, standards and consistency.'),('THỊ TRƯỜNG' if vi else 'MARKET','Thị trường Việt Nam' if vi else 'The Vietnam market','Từ khẩu vị, mức giá đến kênh bán: những yếu tố tạo nên sự phù hợp thật sự.' if vi else 'From taste and price to channels, these are the factors that shape genuine market relevance.'),('THƯƠNG HIỆU' if vi else 'BRAND','Xây dựng giá trị dài hạn' if vi else 'Building long-term value','Cách một sản phẩm nhập khẩu từng bước trở thành thương hiệu được nhớ đến.' if vi else 'How an imported product can earn a lasting place in people’s minds and in the market.')]
    cards=''.join(f'<article class="insight-card reveal"><p class="eyebrow">{e(cat)}</p><h3>{e(h)}</h3><p>{e(c)}</p><span>{e(t["coming"])}</span></article>' for cat,h,c in topics)
    body=page_hero(locale,'GÓC NHÌN' if vi else 'INSIGHTS',t['insights_title'],t['insights_lede'],f'<a href="{r["home"]}">{t["home"]}</a> / {t["insights"]}')
    body+=f'<section class="page-section"><div class="shell insight-grid">{cards}</div></section>'
    return base_page(locale,f'{t["insights"]} — VOrigin',t['insights_lede'],'insights',body,body_class='insights-page')

def contact(locale):
    t=LANG[locale]; r=ROUTES[locale]; vi=locale=='vi'
    email=SITE['contact'].get('email','contact@vorigin.vn')
    body=page_hero(locale,'LIÊN HỆ' if vi else 'CONTACT',t['contact_title'],t['contact_lede'],f'<a href="{r["home"]}">{t["home"]}</a> / {t["contact"]}')
    if not CONTACT_FORMS_ENABLED:
        form = f'''<div class="notice contact-disabled" role="status"><p>{'Tạm thời chưa nhận liên hệ trực tuyến.' if vi else 'Online enquiries are temporarily unavailable.'}</p><p>{'Vui lòng liên hệ trực tiếp qua email hoặc số điện thoại bên cạnh.' if vi else 'Please contact us directly by email or phone using the details beside this notice.'}</p></div>'''
        turnstile_head = ''
    else:
        sitekey = TURNSTILE_SITE_KEY or 'TURNSTILE_SITE_KEY_REQUIRED'
        turnstile_head='<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>' if TURNSTILE_SITE_KEY else ''
        disabled=' disabled' if not TURNSTILE_SITE_KEY else ''
        note='' if TURNSTILE_SITE_KEY else ('<div class="notice"><p>Biểu mẫu liên hệ sẽ được bật khi website đi vào vận hành.</p></div>' if vi else '<div class="notice"><p>The contact form will be enabled when the website goes live.</p></div>')
        labels = {'name':'Họ và tên' if vi else 'Name','email':'Email','company':'Công ty' if vi else 'Company','country':'Quốc gia' if vi else 'Country','website':'Website','type':'Nội dung trao đổi' if vi else 'Enquiry type','message':'Lời nhắn' if vi else 'Message'}
        options=[('general','Trao đổi chung' if vi else 'General enquiry'),('brand-owner','Chủ thương hiệu / Gia nhập thị trường' if vi else 'Brand owner / Market entry'),('retail','Bán lẻ / Phân phối' if vi else 'Retail / Distribution'),('media','Truyền thông' if vi else 'Media')]
        option_html=''.join(f'<option value="{value}">{label}</option>' for value,label in options)
        form=f'''{note}<form data-lead-form="contact" autocomplete="on"><div class="form-grid"><div class="field"><label>{labels['name']}</label><input name="name" required maxlength="120" autocomplete="name"></div><div class="field"><label>{labels['email']}</label><input name="email" type="email" required maxlength="160" autocomplete="email"></div><div class="field"><label>{labels['company']}</label><input name="company" maxlength="160" autocomplete="organization"></div><div class="field"><label>{labels['country']}</label><input name="country" maxlength="100" autocomplete="country-name"></div><div class="field full"><label>{labels['website']}</label><input name="website" maxlength="240" inputmode="url"></div><div class="field full"><label>{labels['type']}</label><select name="inquiry_type">{option_html}</select></div><div class="honeypot" aria-hidden="true"><label>Leave empty<input name="website_confirmation" tabindex="-1" autocomplete="off"></label></div><div class="field full"><label>{labels['message']}</label><textarea name="message" required minlength="10" maxlength="4000"></textarea></div><div class="field full"><div class="cf-turnstile" data-sitekey="{e(sitekey)}"></div><button class="button button-solid" type="submit"{disabled}>{e(t['send'])}<span>→</span></button><div class="form-status" role="status" aria-live="polite"></div></div></div></form>'''
    aside_title='Một mối quan hệ tốt thường bắt đầu từ sự rõ ràng.' if vi else 'Good partnerships often start with clarity.'
    aside_copy='Hãy cho chúng tôi biết về doanh nghiệp, sản phẩm và điều bạn kỳ vọng đạt được tại Việt Nam. Từ một cuộc trao đổi rõ ràng, những khả năng hợp tác đúng đắn mới có thể bắt đầu.' if vi else 'Tell us about your business, your product and what you hope to achieve in Vietnam. Clear conversations are often where the right partnerships begin.'
    body+=f'''<section class="page-section"><div class="shell contact-premium-grid"><div class="form-wrap reveal">{form}</div><aside class="contact-aside reveal"><p class="eyebrow">VORIGIN CORP</p><h2>{e(aside_title)}</h2><p>{e(aside_copy)}</p><a class="contact-method" href="mailto:{e(email)}"><span>{icon_img('email','contact-icon-svg')}</span><b>{e(email)}</b></a></aside></div></section>'''
    return base_page(locale,f'{t["contact"]} — VOrigin',t['contact_lede'],'contact',body,extra_head=turnstile_head,body_class='contact-page')

def legal(locale, kind):
    t=LANG[locale]; vi=locale=='vi'; title=t['privacy_title'] if kind=='privacy' else t['terms_title']
    draft_notice=('BẢN DỰ THẢO — Nội dung này được VOrigin tự soạn để hoàn thiện website và vẫn cần được rà soát, phê duyệt trước khi áp dụng chính thức.' if vi else 'DRAFT — This text was prepared by VOrigin to complete the website and still requires review and approval before it becomes effective.')
    lede=(('Trang này mô tả cách VOrigin dự kiến xử lý thông tin cá nhân khi website tiếp nhận yêu cầu liên hệ.' if kind=='privacy' else 'Các điều khoản này mô tả phạm vi sử dụng website, nội dung được công bố và cách VOrigin tiếp nhận yêu cầu hợp tác.') if vi else ('This page describes how VOrigin expects to handle personal information when the website receives contact enquiries.' if kind=='privacy' else 'These terms describe the scope of website use, published content and how VOrigin handles partnership enquiries.'))
    if kind=='privacy':
        sections=[
            ('Phạm vi áp dụng' if vi else 'Scope', ['Chính sách này áp dụng cho website VOrigin và các biểu mẫu, đường dẫn hoặc kênh liên hệ được website giới thiệu. Chính sách không tự động áp dụng cho website của bên thứ ba.' if vi else 'This policy applies to the VOrigin website and the forms, links or contact channels presented on it. It does not automatically apply to third-party websites.', 'Khi bạn chủ động liên hệ, website có thể nhận họ tên, email, công ty, quốc gia, website, nội dung trao đổi và lời nhắn bạn gửi.' if vi else 'When you contact us, the website may receive your name, email, company, country, website, enquiry type and message.']),
            ('Mục đích sử dụng' if vi else 'How we use information', ['Vorigin sử dụng thông tin để phản hồi yêu cầu, đánh giá khả năng hợp tác, duy trì an toàn website, xử lý lỗi và lưu hồ sơ trao đổi cần thiết.' if vi else 'VOrigin uses information to respond to enquiries, assess potential partnerships, maintain website security, troubleshoot errors and retain necessary correspondence records.', 'Vorigin không bán thông tin cá nhân và không dùng thông tin liên hệ cho hoạt động tiếp thị không liên quan nếu chưa có cơ sở phù hợp.' if vi else 'VOrigin does not sell personal information or use contact details for unrelated marketing without an appropriate basis.']),
            ('Bên cung cấp dịch vụ' if vi else 'Service providers', ['Thông tin có thể được xử lý bởi nhà cung cấp lưu trữ, bảo mật chống bot, email hoặc hạ tầng kỹ thuật cần thiết để vận hành website. Các nhà cung cấp này chỉ được sử dụng thông tin trong phạm vi dịch vụ tương ứng.' if vi else 'Information may be processed by hosting, anti-bot, email or technical infrastructure providers needed to operate the website. These providers may use information only for the relevant service.']),
            ('Lưu giữ và bảo vệ' if vi else 'Retention and protection', ['Vorigin chỉ lưu giữ thông tin trong thời gian cần thiết cho mục đích nêu trên hoặc theo yêu cầu pháp luật áp dụng. Chúng tôi áp dụng biện pháp hợp lý để hạn chế truy cập, mất mát hoặc sử dụng trái phép, nhưng không thể bảo đảm an toàn tuyệt đối cho mọi hệ thống truyền qua internet.' if vi else 'VOrigin retains information only as long as needed for the purposes above or as required by applicable law. We use reasonable safeguards to limit unauthorized access, loss or misuse, but no internet system can be guaranteed completely secure.']),
            ('Cookie và công cụ đo lường' if vi else 'Cookies and analytics', ['Website ưu tiên cookie cần thiết cho hoạt động cơ bản. Tại thời điểm soạn thảo, VOrigin không bật nhà cung cấp phân tích bên thứ ba. Nếu thay đổi, website sẽ cập nhật thông tin phù hợp trước khi áp dụng.' if vi else 'The website prioritizes cookies necessary for basic operation. At the time of drafting, VOrigin does not enable a third-party analytics provider. If this changes, the website will update the relevant information before implementation.']),
            ('Quyền và liên hệ' if vi else 'Your rights and contact', ['Tùy pháp luật áp dụng, bạn có thể yêu cầu biết, sửa, hạn chế hoặc xóa thông tin của mình, hoặc rút lại yêu cầu liên hệ. Gửi yêu cầu đến contact@vorigin.vn; chúng tôi có thể cần xác minh để bảo vệ dữ liệu.' if vi else 'Depending on applicable law, you may request access, correction, restriction or deletion of your information, or withdraw a contact enquiry. Contact contact@vorigin.vn; we may need to verify the request to protect data.']),
            ('Thay đổi chính sách' if vi else 'Policy changes', ['Vorigin có thể cập nhật chính sách khi cách vận hành website thay đổi. Phiên bản được công bố trên trang này là phiên bản tham khảo cho đến khi được phê duyệt chính thức.' if vi else 'VOrigin may update this policy when the website operation changes. The version published here is a draft reference until formally approved.'])]
    else:
        sections=[
            ('Phạm vi website' if vi else 'Website scope', ['Website cung cấp thông tin giới thiệu về VOrigin, thương hiệu, năng lực thị trường và kênh liên hệ. Nội dung website không tự động tạo thành báo giá, lời mời đầu tư, cam kết phân phối hoặc hợp đồng.' if vi else 'The website provides information about VOrigin, its brands, market capabilities and contact channels. Website content does not automatically constitute a quotation, investment offer, distribution commitment or contract.']),
            ('Sử dụng hợp lệ' if vi else 'Permitted use', ['Bạn được xem, lưu và chia sẻ liên kết website cho mục đích hợp pháp. Không được can thiệp, quét gây tải bất thường, truy cập trái phép, giả mạo danh tính hoặc sử dụng website để phát tán mã độc.' if vi else 'You may view, save and share website links for lawful purposes. You must not interfere with the website, create abnormal load, access it without authorization, impersonate another person or distribute malware.']),
            ('Nội dung và claims' if vi else 'Content and claims', ['Vorigin cố gắng giữ nội dung chính xác và cập nhật, nhưng thông tin sản phẩm, thị trường, bao bì, quy cách hoặc khả năng cung ứng có thể thay đổi. Chỉ các thông tin được xác nhận trong trao đổi chính thức mới dùng làm cơ sở giao dịch.' if vi else 'VOrigin aims to keep content accurate and current, but product, market, packaging, format or availability information may change. Only information confirmed in an official exchange should form the basis of a transaction.', 'Không được suy diễn từ nội dung website thành tuyên bố về sức khỏe, chứng nhận, nguồn gốc, độc quyền hoặc quyền phân phối nếu website không công bố rõ.' if vi else 'Do not infer health, certification, origin, exclusivity or distribution rights from website content unless expressly published.']),
            ('Sở hữu trí tuệ' if vi else 'Intellectual property', ['Tên, logo, hình ảnh, thiết kế, văn bản và cấu trúc website thuộc VOrigin hoặc bên cấp quyền tương ứng. Không sao chép, sửa đổi, thương mại hóa hoặc tái phân phối ngoài phạm vi pháp luật cho phép khi chưa có chấp thuận bằng văn bản.' if vi else 'Names, logos, images, designs, text and website structure belong to VOrigin or the relevant licensors. Do not copy, modify, commercialize or redistribute them beyond what applicable law permits without written consent.']),
            ('Yêu cầu liên hệ' if vi else 'Contact enquiries', ['Việc gửi biểu mẫu chỉ là yêu cầu trao đổi, không tạo nghĩa vụ VOrigin phải chấp nhận hợp tác. Bạn chịu trách nhiệm về tính chính xác và quyền cung cấp nội dung mình gửi.' if vi else 'Submitting a form is only a request for discussion and does not require VOrigin to accept a partnership. You are responsible for the accuracy of and your right to provide the content you submit.']),
            ('Liên kết và tính sẵn sàng' if vi else 'Links and availability', ['Website có thể dẫn đến dịch vụ bên ngoài. VOrigin không kiểm soát và không chịu trách nhiệm cho nội dung, bảo mật hoặc hoạt động của các website đó. Website cũng có thể tạm thời gián đoạn để bảo trì hoặc vì nguyên nhân ngoài kiểm soát.' if vi else 'The website may link to external services. VOrigin does not control and is not responsible for their content, security or operation. The website may also be temporarily unavailable for maintenance or reasons beyond its control.']),
            ('Giới hạn trách nhiệm' if vi else 'Limitation of liability', ['Trong phạm vi pháp luật cho phép, VOrigin không chịu trách nhiệm cho thiệt hại phát sinh chỉ từ việc sử dụng thông tin website hoặc việc website tạm thời không khả dụng. Điều khoản này không loại trừ trách nhiệm không thể loại trừ theo pháp luật áp dụng.' if vi else 'To the extent permitted by law, VOrigin is not liable for loss arising solely from use of website information or temporary unavailability. This does not exclude liability that cannot be excluded under applicable law.']),
            ('Luật áp dụng và thay đổi' if vi else 'Governing law and changes', ['Các điều khoản cuối cùng sẽ được VOrigin rà soát để xác định luật áp dụng và cơ chế giải quyết tranh chấp phù hợp. VOrigin có thể cập nhật điều khoản khi website thay đổi; bản được công bố hiện tại vẫn là bản dự thảo.' if vi else 'VOrigin will review the final terms to determine the applicable law and an appropriate dispute-resolution mechanism. VOrigin may update these terms when the website changes; the currently published text remains a draft.']),
            ('Liên hệ' if vi else 'Contact', ['Nếu có câu hỏi về website hoặc điều khoản, liên hệ contact@vorigin.vn hoặc số 84 913736233.' if vi else 'For questions about the website or these terms, contact contact@vorigin.vn or 84 913736233.'])]
    rendered=''.join(f'<section class="legal-section"><h2>{e(heading)}</h2>'+''.join(f'<p>{e(paragraph)}</p>' for paragraph in paragraphs)+ '</section>' for heading,paragraphs in sections)
    body=f'''<section class="page-hero"><div class="shell"><p class="eyebrow">{'PHÁP LÝ' if vi else 'LEGAL'}</p><h1>{e(title)}</h1><p class="lede">{e(lede)}</p></div></section><section class="page-section"><div class="shell legal-copy"><div class="notice"><p>{e(draft_notice)}</p></div>{rendered}</div></section>'''
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
