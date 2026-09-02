# Remaining owner-controlled public launch gates — rc7

The static release candidate is current. Public contact and partnership forms are intentionally disabled until the online enquiry flow is approved and protected; the lead API is not called by the public site in this state.

## Current production preflight blocker

1. `launch.production_ready=true` remains false and must not be enabled until the approved production/runtime evidence is complete.

## Deferred while contact forms are disabled

- `TURNSTILE_SITE_KEY` and `TURNSTILE_SECRET_KEY` are intentionally blank and are not required by production preflight while `contact_forms_enabled=false`.
- Public contact UI displays the bilingual temporary-unavailable status and provides direct contact details; it does not render an active lead form.

## Already recorded

- Business phone: `84 913736233`.
- Vietnamese address: `E2, đường N5 KĐT Ecoxuân Lái Thiêu HCMC`.
- English address rendering is present in `config/site.json` as a working translation.
- Privacy/Terms review flags are approved by the owner; the pages remain self-authored policy drafts and should receive any required legal sign-off before public use.
- Official MARIGOLD asset confirmation is approved by the owner.
- `IP_HASH_SALT` was generated locally with `openssl rand -hex 32` and stored in `ops/.env` with mode `600`; the value is never printed or tracked.

## Additional runtime evidence still required

- If Directus delivery is enabled later, approved least-privilege production tokens/roles must be configured and tested without exposing their values.
- Staging deployment, real-domain browser checks, performance measurement, lead delivery and rollback remain approval-gated; no deployment has been performed.

Current content note:
- The statement "exclusive distributor in Vietnam" is retained only as an internal claim record and is hidden from the public website at the owner's request.
- Public MARIGOLD vitamin, no-preservatives, Halal and manufacturer quality-system/heritage information must continue to remain traceable to the claim registry/source records.

Do not point public DNS at the Pi until `python3 scripts/preflight.py --production` returns `PASS` and the remaining runtime evidence is reviewed.
