# VOweb Execution Tasks

**Plan:** `.ai/MASTER_PLAN.md` revision 9  
**Active workstream:** Premium Production Closure  
**Runner:** agy (`gemini-3.8-flash-high`)  
**Controller/reviewer:** Mika  
**Rule:** This file contains unfinished executable work only.

---

## 0. Execution protocol

For every task:

1. Mika re-reads current repo state and task dependencies.
2. Mika delegates **one bounded task** to agy.
3. agy implements only the stated scope and returns:
   - files changed;
   - commands run;
   - test/build results;
   - residual risk/blocker.
4. Mika reviews:
   - diff;
   - generated output;
   - relevant browser/QA evidence.
5. If needed, Mika:
   - asks agy for rework; or
   - requests one focused independent review.
6. Mika alone:
   - marks task status;
   - edits this file;
   - commits/pushes;
   - prepares release/deploy approval.

agy must never:
- edit `.ai/MASTER_PLAN.md` or `tasks.md`;
- commit/push/deploy;
- mutate Cloudflare/DNS;
- expose secrets;
- stage `Doc/` or `.tmp/`;
- broaden scope.

Stop after two repeats of the same failure without new evidence.

---

# Premium Production Closure

## [#P3M2T01] `capture_current_baseline_and_bind_scope()`

**Status:** `[x]`  
**Owner:** Mika  
**Runner:** agy  
**Depends on:** none  
**Parallel-safe:** no

### Goal
Bind the upgrade to the actual current repo/public baseline before changing code.

### agy scope
1. Read:
   - `git status --short --branch`;
   - `HEAD`;
   - `origin/main`;
   - current production pointer if locally readable without mutation.
2. Run current production build/QA commands already defined by repo.
3. Record:
   - direct heavy image call sites;
   - current responsive-image helpers/policies;
   - current Contact form state;
   - current Partners section structure.
4. Do not change source files.

### Mika check
- no private/secret content printed;
- no mutation occurred;
- baseline SHA and dirty state are explicit;
- current worktree changes, if any, are preserved.

### Definition of Done
A concise baseline is available for all following tasks and every later diff can be compared to it.

---

## [#P3M2T02] `replace_branded_logistics_with_owner_nologo_sources()`

**Status:** `[x]`  
**Owner:** Mika  
**Runner:** agy  
**Depends on:** `P3M2T01`  
**Parallel-safe:** no

### Goal
Remove the B2B trust risk from fictional/branded logistics assets.

### Private source inputs
```text
/home/pi5/projects/VOweb/Doc/Marigold pics/Container1-nologo.png
/home/pi5/projects/VOweb/Doc/Marigold pics/tau1-nologo.png
```

### agy scope
1. Confirm the two source files exist.
2. Copy/create canonical public assets under `public/assets/` using names that make the no-logo replacement unambiguous.
3. Update `build.py` references for:
   - homepage B2B/container visual;
   - Partners hero/ship visual.
4. Update alt text so it describes the scene, not “VOrigin-branded” physical assets.
5. Ensure `Doc/` is not staged.
6. Do not yet refactor the general responsive pipeline beyond what is necessary to make the replacement path explicit.

### Mika check
- visually compare new images with intended sections;
- verify no VOrigin logo/tagline remains on ship/container;
- grep generated HTML for old misleading alt/reference strings;
- verify `git status` contains no `Doc/`.

### Definition of Done
Public/generated pages use only approved no-logo logistics imagery and no longer imply VOrigin owns/operates a ship/container fleet.

---

## [#P3M2T03] `wire_existing_responsive_image_infrastructure_to_heavy_assets()`

**Status:** `[x]`  
**Owner:** Mika  
**Runner:** agy  
**Depends on:** `P3M2T02`  
**Parallel-safe:** no

### Goal
Use the responsive system already in the repo instead of building a parallel one.

### agy scope
1. Audit:
   - `responsive_picture()`;
   - `ImagePolicy`;
   - `RESPONSIVE_POLICIES`;
   - existing responsive specs/variants.
2. Identify hardcoded heavy call sites for:
   - homepage hero;
   - MARIGOLD lineup/featured visual;
   - no-logo container visual;
   - no-logo Partners hero.
3. Generate only missing WebP/AVIF/size variants supported by the existing pipeline.
4. Replace hardcoded heavy `<img>` calls with the existing helper/policy contract.
5. Preserve:
   - width/height;
   - loading/eager/lazy intent;
   - alt text;
   - focal point/art direction.
6. Do not delete old helpers/assets yet unless they are proven unused.

### Mika check
- inspect generated `<picture>`/`srcset`;
- verify only the intended LCP image is eager/high priority;
- verify desktop/tablet/mobile render;
- compare asset sizes;
- verify no missing local asset.

### Definition of Done
The main heavy images use the existing responsive pipeline and no critical LCP surface depends on a raw multi-MB PNG path when an optimized variant is available.

---

## [#P3M2T04] `finish_contact_experience_when_forms_are_disabled()`

**Status:** `[x]`  
**Owner:** Mika  
**Runner:** agy  
**Depends on:** `P3M2T01`  
**Parallel-safe:** no

### Goal
Make Contact look intentionally complete while `contact_forms_enabled=false`.

### agy scope
1. Preserve `contact_forms_enabled=false`.
2. In `contact()`:
   - do not render a disabled form;
   - do not render “Tạm thời chưa nhận liên hệ trực tuyến” or equivalent.
3. Render a finished contact block using verified existing:
   - email;
   - phone;
   - legal/company identity;
   - direct CTA (`mailto:` / `tel:` as appropriate).
4. Apply approved VI/EN Contact copy from Master Plan.
5. Do not enable Turnstile, Lead API public flow or CMS.

### Mika check
- VI/EN rendered Contact pages;
- no dead form controls;
- no fake “coming soon” state;
- mail/tel links valid;
- forms remain disabled in config.

### Definition of Done
Contact is production-complete without pretending the deferred online form exists.

---

## [#P3M2T05] `apply_homepage_and_about_copy_v2()`

**Status:** `[x]`  
**Owner:** Mika  
**Runner:** agy  
**Depends on:** `P3M2T01`  
**Parallel-safe:** no

### Goal
Apply the approved premium bilingual voice to the two pages that define brand perception.

### agy scope
Apply exact Master Plan copy for:
- Homepage hero/CTA;
- Story section/cards;
- Featured MARIGOLD copy;
- Portfolio title/body;
- Why VOrigin labels/copy;
- International Brands copy;
- About hero;
- VOrigin Standard;
- Vision -> How We Work reframe.

Do not:
- invent alternate copy;
- change product claims;
- translate sentence-by-sentence beyond the approved text.

### Mika check
1. Render VI and EN.
2. Review line breaks and text density.
3. Read VI aloud.
4. Read EN independently.
5. Flag only actual awkwardness/repetition for rework; do not restart the copy project.

### Definition of Done
Homepage/About use approved V2 copy and pass first human/native review.

---

## [#P3M2T06] `simplify_partners_and_make_capabilities_process_canonical()`

**Status:** `[x]`  
**Owner:** Mika  
**Runner:** agy  
**Depends on:** `P3M2T05`  
**Parallel-safe:** no

### Goal
Remove Partners module bloat and eliminate repeated five-step process content.

### Target Partners structure
```text
Hero
What We Look For
How We Approach the Market
How Partnership Begins
```

### agy scope
1. Merge current Core Values + Ideal Partner into **What We Look For**.
2. Replace repeated full route-to-market block with three high-level steps:
   - Assess the fit;
   - Prepare the market route;
   - Build the commercial presence.
3. Link to Capabilities for the full five-stage process.
4. Merge partnership principles + final CTA into **How Partnership Begins**.
5. Ensure Capabilities remains the canonical detailed five-stage page.
6. Apply approved VI/EN text from Master Plan.
7. Remove CSS only for modules that no longer exist, after confirming selectors are unused.

### Mika check
- Partners has exactly four semantic modules;
- visual breathing room improves;
- Capabilities still contains full process;
- no duplicate five-step explanation across pages;
- desktop/mobile browser review.

### Definition of Done
Partners reads as an editorial B2B partnership page rather than a repeated premium deck.

---

## [#P3M2T07] `apply_remaining_copy_and_factual_source_framing()`

**Status:** `[x]`  
**Owner:** Mika  
**Runner:** agy  
**Depends on:** `P3M2T05`, `P3M2T06`  
**Parallel-safe:** no

### Goal
Finish approved copy changes without touching factual claim meaning.

### agy scope
Apply Master Plan text to:
- Brands;
- Capabilities;
- Insights;
- Contact supporting text;
- footer navigation labels;
- MARIGOLD assurance/source labels;
- Product assurance/source labels.

MARIGOLD:
- delete or factual-repurpose the repetitive closing editorial block.

Guardrails:
- do not add Proof of Execution;
- do not create case-study metrics;
- do not add health/nutrition benefits beyond approved claims;
- do not change exclusivity visibility.

### Mika check
- claim diff review;
- VI/EN consistency;
- portfolio direction cards still state they are directions, not signed partnerships;
- product/source pages remain evidence-first.

### Definition of Done
All public copy aligns with Revision 9 while factual/legal claim meaning is preserved.

---

## [#P3M2T08] `polish_mobile_accessibility_and_navigation()`

**Status:** `[ ]`  
**Owner:** Mika  
**Runner:** agy  
**Depends on:** `P3M2T03`, `P3M2T06`  
**Parallel-safe:** no

### Goal
Close high-value UI/UX defects without redesign.

### agy scope
1. Partners hero:
   - mobile portrait crop/art direction;
   - use `object-fit: cover`;
   - avoid tiny contained 16:9 strip.
2. Homepage/B2B:
   - add mobile crop only where materially needed.
3. CTA:
   - use an AA-compliant deep-bronze treatment for small white text.
4. Typography:
   - increase or hide unreadable header tagline on mobile;
   - improve footer readability only where needed.
5. Navigation:
   - active main-nav `aria-current`;
   - subtle active visual state;
   - Escape closes menu;
   - focus returns to toggle;
   - only necessary body-scroll/focus containment.

Do not add new animation systems or visual effects.

### Mika check
- 390px/430px mobile;
- tablet;
- desktop;
- keyboard;
- reduced motion;
- contrast;
- no horizontal overflow.

### Definition of Done
Critical mobile, contrast and navigation completion issues are resolved with no design-language regression.

---

## [#P3M2T09] `reconcile_governance_and_remove_verified_dead_paths()`

**Status:** `[ ]`  
**Owner:** Mika  
**Runner:** agy  
**Depends on:** `P3M2T03`, `P3M2T07`, `P3M2T08`  
**Parallel-safe:** no

### Goal
Make the repo tell one consistent story after the upgrade.

### agy scope
1. Identify contradictions for:
   - asset verification;
   - claim approval;
   - contact state;
   - production readiness.
2. Propose the canonical source before changing duplicate flags.
3. Mark outdated self-audits such as old premium/copy score files as `SUPERSEDED` or archive them without deleting useful evidence.
4. Remove only verified-unused:
   - image helpers;
   - CSS selectors;
   - legacy public assets directly superseded by the new path.
5. Add QA note: automated visual audits must scroll/wait before declaring lazy images broken.

### Mika check
- no valid evidence/history lost;
- no active selector/helper removed;
- config/content flags agree;
- no secret/private scope touched.

### Definition of Done
Current repo state, governance flags and audit docs no longer contradict the implementation.

---

## [#P3M2T10] `run_premium_closure_gate()`

**Status:** `[ ]`  
**Owner:** Mika  
**Runner:** agy for bounded test execution; Mika owns verdict  
**Depends on:** `P3M2T02`–`P3M2T09`  
**Parallel-safe:** no

### Goal
Prove the candidate is better and production-safe before any deploy.

### agy test scope
Run repository-approved:
- build;
- static/copy/preflight tests;
- Python/Node syntax/tests;
- internal-link/local-asset checks;
- generated HTML checks.

Browser/visual matrix:
- VI/EN;
- Homepage;
- About;
- Brands;
- MARIGOLD;
- representative Product;
- Capabilities;
- Partners;
- Insights;
- Contact;
- 390/430/768/1024/1440/1920 as practical.

Performance:
- Lighthouse mobile/desktop;
- LCP/CLS/INP evidence where supported.

Editorial:
- vocabulary-family scan;
- rhetorical-pattern scan;
- no exact old-cliché regressions.

### Mika check
Mika independently verifies:
- no misleading ship/container branding;
- Contact complete with forms disabled;
- Partners four-module structure;
- Capabilities canonical five-step process;
- no broken/lazy-image false positives;
- no first-party JS/network failures;
- no overflow;
- focus/reduced-motion;
- claim safety;
- exact diff scope.

### Definition of Done
All hard gates pass or every residual exception is explicit, evidence-backed and accepted by Mika. No deploy occurs here.

---

## [#P3M2T11] `prepare_and_release_owner_approved_candidate()`

**Status:** `[BLOCKED — owner approval required after P3M2T10 PASS]`  
**Owner:** Mika  
**Runner:** none for deploy authority  
**Depends on:** `P3M2T10`  
**Parallel-safe:** no

### Goal
Commit/push/deploy only the independently verified Premium Closure candidate.

### Mika scope
1. Confirm clean intended diff.
2. Bind candidate to exact SHA.
3. Commit/push.
4. Re-run required candidate checks.
5. Present:
   - exact SHA;
   - changes;
   - QA verdict;
   - rollback path;
   - residual risk.
6. Obtain explicit owner approval before production deploy/cutover.
7. After approval:
   - deploy using approved wrapper;
   - verify public apex/www;
   - preserve rollback evidence.

### Definition of Done
Exact approved SHA is live, public verification passes and rollback remains available.

---

# Deferred post-launch scope

## [#P3M1T01] `enable_admin_route_lead_and_cms_after_static_launch()`

**Status:** `[DEFERRED — separate approval; not part of Premium Closure]`

### Scope
- `admin.vorigin.vn` -> Directus through Cloudflare Tunnel + Access;
- least-privilege Directus roles/tokens;
- Turnstile real-domain configuration;
- enable forms only after end-to-end evidence;
- CMS publishing/sync with rollback and monitoring.

### Constraints
No secret exposure, no real customer fixture, no schema migration or bypass of Premium Closure gates.

### Definition of Done
Admin route, Turnstile, lead/CMS path, monitoring and rollback are independently verified under a separate owner-approved phase.
