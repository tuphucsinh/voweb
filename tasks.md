# VOweb Execution Tasks

**Plan:** `.ai/MASTER_PLAN.md` revision 8
**State:** Phase 1 foundation, Phase 2 static launch/apex-www edge and P3T05 MARIGOLD visual integration are verified. `admin.vorigin.vn` remains deferred Phase 3 scope.
**Rule:** Tasks below are unfinished executable work only. Mika owns verification, task status and commits; runners never edit this file, commit, push, deploy or use secrets.

## Completed foundation

- **Phase 1 / P1M1T01–P1M3T03:** `[x]` premium hardening, responsive assets, release integrity, browser matrix, lead API reliability and fail-closed preflight are complete for candidate `b9d39f92cc16c02a1e8e095d2a1455123db6ceed`.
- Evidence: `.ai/PHASE1_EXIT_REVIEW.md`, Git history and current release gates. Do not duplicate the completed task specifications here.

---

## Phase 3: Post-launch lead, CMS and admin route enablement

### [#P3M1T01] [Cloudflare Access/Tunnel, Turnstile, services/lead-api/, services/directus/] `enable_admin_route_lead_and_cms_after_static_launch()`

**Goal:** Configure the secure admin route contract and enable online enquiries and CMS publishing only after the static launch is stable.

**Depends on:** `[#P2M1T04]`

**Parallel-safe:** `no`

**Status:** `[DEFERRED — static launch first; admin.vorigin.vn NXDOMAIN is intentional deferred scope]`

**Scope:**
1. Configure the admin route contract: route `admin.vorigin.vn` -> Directus `127.0.0.1:8055` through Cloudflare Tunnel + Cloudflare Access.
2. Establish least-privilege Directus roles/tokens and perform secret-safe verification without exposing credentials.
3. Configure approved Turnstile keys through secure storage (`ops/.env`).
4. Run an owner-approved real-domain fixture with exact-ID cleanup and multidimensional baseline comparison checks (verifying primary target and neighboring metrics).
5. Enable forms (`contact_forms_enabled=true`) and content sync with monitoring and rollback readiness.

**Verify:** Cloudflare Access policy and Tunnel routing for `admin.vorigin.vn`; server-side least-privilege role read-back; real-domain E2E test; exact-ID cleanup; multidimensional baseline comparison; rollback evidence.

**Constraints:** No real customer data, broad cleanup, secret exposure, schema migration or use of this task to bypass static-launch gates.

**Definition of Done:** Admin route behind Access, Directus least-privilege tokens, Turnstile integration, lead/CMS evidence, cleanup, rollback and monitoring are independently reviewed and pass.
