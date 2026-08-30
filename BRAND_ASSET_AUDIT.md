# VOrigin Brand Asset Audit — Vector Production v4

## Source reviewed
`VORIGIN_Vector_Production_v4.zip` supplied by the owner.

The package contains vector masters in SVG/EPS plus RGB/CMYK PDF and PNG previews. The SVG masters are outlined paths and therefore have no runtime font dependency.

## Important finding
The **Full** lockups in v4 still contain the former tagline **“PURE SOURCE. DEFINED GOALS.”**. The current approved VOrigin slogan for the website is **“From Origins to Value”**.

Therefore the website MUST NOT use these full/tagline variants as-is:

- `01_VORIGIN_Full_Stacked_FullColor.svg`
- `03_VORIGIN_Full_Horizontal_FullColor.svg`
- `07_VORIGIN_Full_Horizontal_Black.svg`
- `08_VORIGIN_Full_Horizontal_White.svg`
- `09_VORIGIN_Full_Horizontal_Bronze.svg`
- matching PDF/EPS/PNG variants that embed the old tagline

## Approved web mapping in rc2

### Header
Source: `04_VORIGIN_Primary_Horizontal_NoTagline_FullColor.svg`

Published as:
`/assets/vorigin-logo-primary.svg`

The approved slogan **FROM ORIGINS TO VALUE** is rendered as live HTML text below the vector lockup. This prevents the old tagline from re-entering the website and keeps the slogan crisp/responsive.

### Footer
Derived from the same no-tagline vector geometry and normalized to VOrigin bronze.

Published as:
`/assets/vorigin-logo-footer-bronze.svg`

The approved slogan is again rendered as live HTML text.

### Favicon / app icon
Source: `05_VORIGIN_Icon_FullColor.svg`

Published as:
- `/assets/favicon.svg`
- `/assets/favicon-32.png`
- `/assets/apple-touch-icon.png`
- `/assets/vorigin-icon.svg`

### Bronze brand mark
Source: `12_VORIGIN_Icon_Bronze.svg`

Published as:
`/assets/vorigin-icon-bronze.svg`

Reserved for brand accents/decorative applications where the complete VOrigin mark is semantically appropriate.

## What this package does NOT contain
This is a **brand logo/mark package**, not the website semantic icon system. It does not contain dedicated icons for:

- Origin / Nature / Craft / Value
- Trusted Partner / Local Expertise / Long-term Value / Premium Approach / Grow Together
- Market Entry / Import & Compliance / Distribution / Localization / Trade Marketing

Do not reuse the VOrigin logo mark to represent those concepts. A dedicated consistent SVG UI icon system is still required for the Premium MAX pass.

## Result
The previous raster logo crops (`logo-light.webp`, `logo-dark.webp`) have been removed from the web build. The website now uses vector brand assets from the supplied production package and no longer depends on screenshot-derived logo crops.
