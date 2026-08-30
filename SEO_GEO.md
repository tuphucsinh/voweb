# SEO / GEO release checklist

Implemented in the static build:
- unique title + meta description per page
- canonical URLs
- `hreflang` for Vietnamese and English equivalents
- Open Graph metadata
- Organization JSON-LD and Product JSON-LD where applicable
- `sitemap.xml`
- `robots.txt` (`Disallow: /` in preview; indexable only in `SITE_ENV=production`)
- `llms.txt` with an explicit anti-hallucination note for product/business claims
- semantic headings, alt text and server-rendered/static HTML

After public launch:
1. Verify `https://vorigin.vn` in Google Search Console.
2. Submit `https://vorigin.vn/sitemap.xml`.
3. Add Bing Webmaster Tools.
4. Confirm canonical and hreflang in rendered HTML.
5. Monitor 404s, indexing coverage and Core Web Vitals.
6. Publish real Insights content only when it has useful, sourced substance; do not generate low-value SEO filler.
7. Keep company name, address, phone and domain consistent across first-party profiles and business listings.
8. Add structured data only for facts that are actually true; never fabricate ratings, reviews, offers or certifications.

GEO principle: make VOrigin easy to understand as an entity, not merely keyword-dense. Clear About/Brand/Product/Partner pages and verifiable facts matter more than AI-specific markup tricks.
