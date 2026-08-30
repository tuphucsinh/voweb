# Production QA checklist

## Automated in this package
- HTML metadata / canonical / h1 checks
- local asset existence
- internal-link checks
- guard against unconfirmed placeholder brands
- guard against Turnstile placeholder in production
- syntax checks for Python/Node scripts
- Nginx config syntax checked in the build environment

## Device / browser matrix before go-live
Viewport targets: 320, 360, 390, 430, 768, 1024, 1280, 1440, 1920 px.
Browsers: current Chrome/Edge/Safari/Firefox; iOS Safari and Android Chrome on at least one real phone each.

Check:
- no horizontal overflow
- header/menu keyboard/touch behavior
- touch targets around 44px or larger
- typography does not clip in VI or EN
- 5-column Why Partner becomes usable on tablet/mobile
- B2B services remain readable and scroll/stack cleanly
- focus states visible
- 200% zoom usable
- `prefers-reduced-motion` works
- contact form errors/status are perceivable
- Turnstile works on real domain
- Privacy/Terms links are final

## Performance targets
- Lighthouse Performance ≥ 90 mobile, ≥95 desktop
- Accessibility ≥95
- Best Practices ≥95
- SEO near 100
- LCP < 2.5s
- CLS < 0.1
- INP < 200ms

The public build is intentionally small (roughly hundreds of KB before CDN compression) and has no public application framework runtime.
