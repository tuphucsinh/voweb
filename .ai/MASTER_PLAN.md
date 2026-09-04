# VOweb Master Plan

**Revision:** 9  
**Last reviewed:** 2026-09-04  
**Status:** Public static site is live; Premium Production Closure is the active workstream. Admin/lead/CMS remains deferred.  
**Recorded production baseline:** `d93a44fe6ca74614d6d19f6599f9a546099f323b` from Revision 8. Mika must re-read `HEAD`, `origin/main` and `/srv/vorigin/current` before execution and bind all new evidence to the actual current SHA.  
**Confidence:** CAO after closure gates pass.

---

## 1. Goal

Keep the approved VOrigin visual system and close the remaining gap between **premium concept** and **premium production**.

Target perception:

> A refined, trustworthy international trade business with judgement, restraint, commercial intelligence and evidence discipline.

Core rule:

> **Subtraction before decoration. Trust before polish. Reuse before rebuild.**

The upgrade must improve:
- bilingual copy and brand voice;
- trust/credibility;
- image performance and LCP;
- Partners information architecture;
- mobile art direction;
- accessibility and navigation completeness;
- governance consistency.

No redesign is required.

---

## 2. Current architecture and invariants

```text
public visitor
  -> Cloudflare HTTPS/WAF
  -> Cloudflare Tunnel
  -> Nginx 127.0.0.1:8080
  -> /srv/vorigin/current

local staging
  -> Nginx 127.0.0.1:8081
  -> /srv/vorigin/staging/current

deferred admin
  -> Cloudflare Access
  -> Cloudflare Tunnel
  -> Directus 127.0.0.1:8055
```

Invariants:
- no router port forwarding;
- no public DB/Directus/lead-api listener;
- `Doc/`, `.tmp/`, secrets and private source material never enter a release;
- production deploy uses manifest/checksum evidence and preserves rollback;
- claims remain source-gated;
- no public visual may imply ownership of assets VOrigin does not own/operate.

---

## 3. Execution control

### Mika — controller/reviewer
Mika owns:
- reading current repo state;
- selecting/delegating one bounded task at a time;
- acceptance criteria;
- task status in `tasks.md`;
- diff/evidence review;
- requesting rework or independent review when needed;
- commits/pushes;
- staging/production approval preparation.

### agy — implementation runner
Runner: **agy (`gemini-3.8-flash-high`)**

agy may:
- inspect allowed repo files;
- implement the delegated task;
- run bounded local tests/builds;
- return exact changed files, commands, results and residual risk.

agy must not:
- edit `.ai/MASTER_PLAN.md` or `tasks.md`;
- commit, push or deploy;
- mutate Cloudflare/DNS;
- read/print/persist secrets;
- stage `Doc/` or private artifacts;
- broaden scope beyond the delegated task.

### Mika verification loop

```text
Mika reads state
  -> delegates one task to agy
  -> agy implements + reports evidence
  -> Mika checks diff + tests + rendered result
  -> if needed: Mika asks agy to rework or asks for a focused review
  -> Mika marks task complete
  -> Mika commits/pushes only after acceptance
```

---

## 4. Scope priorities

### P0 — hard gates

1. **Trust imagery**
   - replace/remove misleading VOrigin-branded ship/container imagery.

2. **Performance**
   - reuse the existing responsive-image infrastructure;
   - remove hardcoded multi-MB LCP PNG delivery.

3. **Contact production state**
   - never show a disabled/incomplete form experience.

4. **Core copy**
   - apply approved V2 copy to Homepage and About;
   - render and review VI/EN immediately.

5. **Partners architecture**
   - reduce repeated semantic modules;
   - do not duplicate the full Capabilities process.

6. **Functional accessibility**
   - fix primary CTA contrast.

### P1 — premium completion

- Brands/Capabilities/Insights/Contact copy;
- mobile-specific art direction;
- active nav + keyboard essentials;
- readable micro-typography;
- governance/source-of-truth sync;
- old audit supersession;
- dead-code/CSS cleanup after proof.

### P2 — optional/closure polish

- MARIGOLD closing-section cleanup;
- dedicated OG artwork;
- verified Organization schema enrichment;
- advanced semantic tooling.

---

## 5. Explicit non-goals

### No Proof of Execution section yet

There is currently **no verified public-safe execution data** for:
- number of outlets;
- distribution footprint;
- shipment milestones;
- penetration/growth metrics;
- case-study performance.

Therefore:
- do not create a Track Record / Proof of Execution block;
- do not invent, infer or pad metrics;
- reopen only when verified data exists and is approved for public use.

### No mandatory CRM migration

Lead API may remain if it is the simplest reliable approved path. The hard requirement is a finished Contact UX, not a specific vendor.

### No Insights CMS refactor now

Keep current architecture until actual publishing volume creates a real operational need.

---

## 6. Owner-provided replacement logistics sources

Private source files:

```text
/home/pi5/projects/VOweb/Doc/Marigold pics/Container1-nologo.png
/home/pi5/projects/VOweb/Doc/Marigold pics/tau1-nologo.png
```

Contract:
- treat them as private source inputs;
- never stage/commit `Doc/`;
- create approved public/optimized derivatives under `public/assets/`;
- update code/alt text to the no-logo versions;
- after verification, ensure generated production HTML no longer references misleading branded ship/container assets.

---

## 7. Approved copy contract

The text below is the implementation source-of-truth. VI and EN preserve intent, not sentence structure.

### 7.1 Homepage

#### Hero

VI eyebrow:
> **NGUỒN GỐC ĐÁNG TIN. LỰA CHỌN CÓ CƠ SỞ.**

EN eyebrow:
> **TRUSTED ORIGINS. CONSIDERED CHOICES.**

H1:
> **From Origins to Value.**

VI lead:
> **VOrigin tìm kiếm những sản phẩm có nền tảng đáng tin, bản sắc rõ nét và tiềm năng thực sự tại Việt Nam. Từ lựa chọn ban đầu đến cách thương hiệu bước vào thị trường, mỗi quyết định đều được cân nhắc với một tầm nhìn dài hơn.**

EN lead:
> **VOrigin identifies distinctive international brands with credible foundations and genuine relevance to Vietnam, then shapes a considered route from first entry to enduring market presence.**

CTA:
- VI: **Khám phá VOrigin** / **Danh mục thương hiệu**
- EN: **Discover VOrigin** / **Explore our portfolio**

#### Story

VI eyebrow:
> **CÁCH VORIGIN LỰA CHỌN**

EN eyebrow:
> **HOW WE CHOOSE**

VI title:
> **Giá trị được định hình từ những lựa chọn đầu tiên.**

EN title:
> **Value is shaped long before a product reaches the market.**

Cards:

1. **Nguồn gốc đáng tin**  
   Nơi sản phẩm bắt đầu cũng là nơi niềm tin bắt đầu.

   **Trusted Origin**  
   Where a product begins matters to how confidently it can be represented.

2. **Bản sắc sản phẩm**  
   Những đặc tính đủ rõ để tạo nên một lý do lựa chọn.

   **Product Character**  
   Distinctive qualities that give people a genuine reason to choose it.

3. **Tiêu chuẩn lựa chọn**  
   Chất lượng, tính nhất quán và những gì có thể kiểm chứng.

   **Selection Standards**  
   Consistency, substance and information that can stand up to scrutiny.

4. **Giá trị thị trường**  
   Khả năng tìm được một vị trí phù hợp và phát triển theo thời gian.

   **Market Potential**  
   A credible place to build, not simply a product to place on shelf.

#### Featured MARIGOLD

VI:
> **MARIGOLD Fruit Drinks mở đầu danh mục VOrigin với bốn hương vị Apple, Orange, Mango và Grape. Dòng sản phẩm phản ánh những điều chúng tôi coi trọng ở một thương hiệu: nền tảng đáng tin, thông tin có thể đối chiếu và một đề xuất sản phẩm dễ được hiểu trên thị trường.**

EN:
> **MARIGOLD Fruit Drinks opens the VOrigin portfolio with four flavours: Apple, Orange, Mango and Grape. It reflects what we value in a brand: a credible foundation, verifiable product information and a proposition people can readily understand.**

#### Portfolio

VI title:
> **Một danh mục được xây dựng có chủ đích.**

VI body:
> **VOrigin không mở rộng danh mục để chạy theo số lượng. Mỗi hướng mới chỉ đáng theo đuổi khi sản phẩm có nền tảng phù hợp với tiêu chuẩn của chúng tôi và một khoảng trống đủ rõ để tạo dựng tại Việt Nam. Các nhóm bên dưới là những định hướng đang được nghiên cứu, không phải danh sách đối tác đã ký kết.**

EN title:
> **A portfolio built with intent.**

EN body:
> **We would rather build the right portfolio slowly than a large one quickly. New categories are explored only where there is a credible product case and a meaningful place to build in Vietnam. The areas below are directions under consideration, not signed brand partnerships.**

#### Why VOrigin

Section:
- VI: **Điều định hình cách VOrigin làm việc.**
- EN: **What shapes the way we work.**

Items:
1. **Minh bạch trong cam kết / Clarity in commitments**
2. **Am hiểu thị trường / Local judgement**
3. **Góc nhìn dài hơn / A longer view**
4. **Kỷ luật trong thực thi / Disciplined execution**
5. **Hợp tác thay vì giao dịch / Partnership over transaction**

#### International brands

H2:
> **YOUR BRAND. OUR MARKET.**

VI:
> **VOrigin hỗ trợ các thương hiệu quốc tế xây dựng lộ trình vào Việt Nam — từ đánh giá cơ hội, tuân thủ nhập khẩu và phát triển phân phối đến bản địa hóa thương hiệu và tiếp thị thương mại.**

EN:
> **VOrigin helps international brands turn market ambition into a workable route through Vietnam — from assessment and compliance to distribution, localisation and trade marketing.**

Homepage only teases capabilities; it does not own the full process explanation.

---

### 7.2 About

VI H1:
> **Giá trị được định hình từ những lựa chọn ban đầu.**

VI lead:
> **Khởi Nguyên là điểm bắt đầu. Với VOrigin, đó cũng là một cách nhìn về giá trị: trước một thương hiệu luôn có một nguồn gốc; trước một quyết định thương mại luôn cần một lý do đủ vững chắc.**

EN H1:
> **Lasting value is shaped by the choices made at the start.**

EN lead:
> **Our Vietnamese name, Khởi Nguyên, speaks to beginnings — and to the belief that enduring value starts with what a business chooses to stand behind.**

VOrigin Standard:
- **Nguồn gốc / Origin** — Đủ rõ để kiểm chứng. / Traceable and credible.
- **Chất lượng / Quality** — Nhất quán và có cơ sở. / Consistent, with substance behind it.
- **Thị trường / Market** — Có một lý do thuyết phục để hiện diện. / A convincing reason to be here.
- **Bản sắc / Character** — Có điều riêng đủ để được ghi nhớ. / Something distinctive enough to remember.
- **Tiềm năng / Potential** — Có khả năng phát triển theo thời gian. / Room to build over time.

Replace generic Vision with:

VI eyebrow:
> **CÁCH VORIGIN LÀM VIỆC**

VI H2:
> **Được tin cậy bởi chất lượng của những lựa chọn và cách chúng tôi thực hiện chúng.**

EN eyebrow:
> **HOW WE WANT TO BE KNOWN**

EN H2:
> **For the quality of our judgement and the discipline of our execution.**

---

### 7.3 Brands

VI H1:
> **Một danh mục được xây dựng có chủ đích.**

VI lead:
> **MARIGOLD là điểm khởi đầu. Từ đó, VOrigin mở rộng theo một nguyên tắc đơn giản nhưng nghiêm ngặt: chỉ theo đuổi những thương hiệu có nền tảng đủ vững, bản sắc đủ rõ và một lý do thuyết phục để phát triển tại Việt Nam.**

EN H1:
> **A portfolio built with intent.**

EN lead:
> **MARIGOLD is where the portfolio begins. From there, VOrigin grows selectively, pursuing brands with credible foundations, distinctive character and a convincing reason to belong in Vietnam.**

Future portfolio:
- VI: **NHỮNG HƯỚNG TIẾP THEO** / **Mở rộng từng bước, với cùng một kỷ luật lựa chọn.**
- EN: **WHAT WE ARE EXPLORING NEXT** / **Selective growth, guided by the same discipline.**

Future category cards must remain visibly described as directions under consideration, not signed partnerships.

---

### 7.4 MARIGOLD / Products

Keep factual product claims source-gated.

Rename:
- `BẢO CHỨNG SẢN PHẨM` → **THÔNG TIN & NGUỒN THAM CHIẾU**
- `PRODUCT ASSURANCE` → **PRODUCT FACTS & SOURCES**

MARIGOLD assurance:
- VI: **Niềm tin đến từ những điều có thể đối chiếu.**
- EN: **Trust is stronger when the facts can be traced.**

Delete or repurpose the repetitive MARIGOLD closing editorial block; factual manufacturer context is acceptable.

---

### 7.5 Capabilities — canonical full process

Capabilities is the only page that owns the detailed five-stage Route to Market.

VI H1:
> **Từ quyết định gia nhập đến hiện diện trên thị trường.**

EN H1:
> **From market decision to market presence.**

Five stages:
1. **Gia nhập thị trường / Market Entry**
2. **Nhập khẩu & Tuân thủ / Import & Compliance**
3. **Phát triển phân phối / Distribution Development**
4. **Bản địa hóa thương hiệu / Brand Localisation**
5. **Tiếp thị thương mại / Trade Marketing**

Do not repeat the full five-stage explanation on Homepage or Partners.

---

### 7.6 Partners — four modules only

Target:

```text
Hero
What We Look For
How We Approach the Market
How Partnership Begins
```

Hero VI:
> **VOrigin tìm kiếm những thương hiệu có nền tảng đủ vững để xây dựng một vị trí lâu dài tại Việt Nam. Cách tiếp cận của chúng tôi có chọn lọc, có kỷ luật và luôn nhìn xa hơn lô hàng đầu tiên.**

Hero EN:
> **We work with brands built on substance — and with the ambition to establish a meaningful place in Vietnam. Our approach is selective, disciplined and designed to look beyond the first shipment.**

What We Look For:
1. **Nguồn gốc có thể kiểm chứng / Traceable origins**
2. **Chất lượng có tính nhất quán / Consistent quality**
3. **Một lý do thực sự để hiện diện / A genuine reason to be here**
4. **Dư địa để xây dựng thương hiệu / Room to build a brand**

High-level market approach only:
1. **Đánh giá sự phù hợp / Assess the fit**
2. **Chuẩn bị lộ trình vào thị trường / Prepare the market route**
3. **Xây dựng hiện diện thương mại / Build the commercial presence**

Link to Capabilities for full process.

Final module:
- VI: **CÁCH MỘT QUAN HỆ HỢP TÁC BẮT ĐẦU** / **Hiểu đúng trước khi cam kết.**
- EN: **HOW PARTNERSHIP BEGINS** / **Understand first. Commit second.**

---

### 7.7 Insights

VI H1:
> **Những gì đáng cân nhắc trước khi một thương hiệu bước vào thị trường.**

EN H1:
> **Perspectives on what makes a brand worth building in Vietnam.**

Topics:
- **Nhìn phía sau sản phẩm / Look behind the product**
- **Đọc thị trường Việt Nam / Read Vietnam beyond the headline numbers**
- **Từ sản phẩm nhập khẩu đến một thương hiệu được nhớ đến / From imported product to remembered brand**

Do not add a CMS or Proof of Execution content.

---

### 7.8 Contact

VI H1:
> **Bắt đầu bằng một cuộc trao đổi có trọng tâm.**

EN H1:
> **Start with a focused conversation.**

If forms are disabled:
- render no disabled form;
- render no “Tạm thời chưa nhận liên hệ trực tuyến” notice;
- show a complete minimal contact experience with verified email, phone, company identity and direct CTA.

If forms are later enabled:
- require real-domain Turnstile + backend evidence before changing the production flag.

---

## 8. Image/performance contract

The repo already contains responsive-image abstractions. Reuse them.

Required order:
1. audit `responsive_picture()`, `ImagePolicy`, `RESPONSIVE_POLICIES`;
2. map heavy call sites;
3. generate only missing variants;
4. replace hardcoded PNG calls;
5. verify crop and output HTML;
6. measure LCP;
7. remove dead duplicate helpers only after success.

Priority:
1. Homepage hero;
2. Partners hero/no-logo ship replacement;
3. MARIGOLD lineup;
4. homepage B2B/no-logo container replacement.

Targets:
- LCP < 2.5s
- CLS < 0.1
- INP < 200ms
- Lighthouse mobile >= 90
- desktop >= 95

---

## 9. UI/UX and accessibility contract

Keep:
- Cormorant Garamond + Manrope;
- ivory/cream/bronze/navy;
- restrained motion;
- subtle grain;
- editorial grids;
- current overall design language.

Do not add:
- glassmorphism;
- decorative gradients/blobs;
- animated counters;
- autoplay video;
- heavy parallax;
- new module bloat.

Accessibility:
- functional small-text CTA uses `#906630` or another verified AA-compliant treatment;
- light bronze remains decorative;
- increase or hide unreadable 5.5–6.5px tagline on mobile;
- add `aria-current="page"` to main nav;
- Escape closes mobile menu;
- focus returns to toggle;
- add only the focus containment/body-scroll behaviour the actual menu needs.

Mobile:
- Partners hero first priority;
- use portrait crop / `object-fit: cover`, not a tiny contained 16:9 strip;
- homepage/B2B imagery receives dedicated crop only where it materially improves focus;
- About mobile hero remains the benchmark.

---

## 10. Governance and cleanup

One canonical truth is required for:
- asset approval;
- claim approval;
- exclusivity visibility;
- contact state;
- production readiness.

Old self-audits such as `PREMIUM_MAX_AUDIT.md` / `COPY_AUDIT.md` must be marked `SUPERSEDED` or archived as historical evidence so agents do not treat old 9.x scores as current truth.

Clean unused helpers/CSS/assets only after Mika verifies the active replacement.

---

## 11. Editorial QA contract

After copy is rendered:

### Vocabulary audit
Review families:
- rõ ràng / clear;
- bền lâu / long-term / lasting;
- nguồn gốc / provenance;
- tiêu chuẩn / standards;
- giá trị / value;
- chọn lọc / curated;
- hành trình / journey.

### Rhetorical-pattern audit
Review repeated structures:
- `X thay vì Y`;
- `from X to Y`;
- `before X...`;
- `not simply X, but Y`;
- `built on...`;
- `shaped by...`;
- `considered...`.

### Human checks
- read VI aloud;
- read EN independently;
- apply the “20-company test”;
- check adjacent sections for semantic duplication.

Copy V2 is approved for implementation first; these checks are a post-render refinement gate, not a new rewrite project.

---

## 12. Acceptance and closure

Required before `VORIGIN PREMIUM OPTIMIZATION = CLOSED`:

- no misleading branded ship/container asset;
- no hardcoded multi-MB LCP delivery where responsive pipeline should apply;
- Homepage/About V2 applied;
- Partners reduced to four semantic modules;
- Capabilities owns the full five-stage process;
- no disabled Contact notice in production;
- functional CTA contrast passes;
- mobile critical hero art direction passes;
- governance flags are consistent;
- VI/EN editorial gates pass;
- production build/static/copy tests pass;
- browser matrix passes;
- Lighthouse/Web Vitals targets pass or any exception is explicitly documented;
- rollback evidence remains valid.

Visual QA automation must scroll and wait for lazy assets before calling an image broken.

---

## 13. Approval and release boundary

Mika may prepare and verify the release candidate.

Explicit owner approval is still required before:
- production deploy;
- Nginx production reload if required;
- Cloudflare mutation;
- changing deferred admin/form scope;
- rollback/cutover.

`admin.vorigin.vn`, CMS publishing and online form enablement remain deferred until separately approved.

---

## 14. Source of truth

- Strategic/acceptance contract: `.ai/MASTER_PLAN.md`
- Active executable work only: `tasks.md`
- Operational docs: `DEPLOY_PI5.md`, `OPERATIONS.md`, `ops/cloudflare/README.md`
- Historical evidence: `.ai/PHASE1_EXIT_REVIEW.md`, old audit files, Git history

Completed task specifications must not remain in `tasks.md`.
