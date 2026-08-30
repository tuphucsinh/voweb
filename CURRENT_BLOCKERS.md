# Remaining owner-controlled public launch gates — rc7

The website code and Pi 5 staging package are ready. Public production remains intentionally gated until the following owner-controlled items are completed or approved:

1. Business phone number for publication.
2. Business address in Vietnamese and English.
3. Final owner authorization for the production MARIGOLD image set and Vietnam-market label/dossier wording.
4. Final Privacy Policy approval.
5. Final Terms of Use approval.
6. Cloudflare Tunnel, Turnstile and Access configuration/secrets.
7. Directus production tokens/roles generated and tested on the Pi.
8. `launch.production_ready=true` only after the production preflight passes.

Current content note:
- The statement "exclusive distributor in Vietnam" is retained only as an internal claim record and is hidden from the public website at the owner's request.
- Public MARIGOLD vitamin, no-preservatives, Halal and manufacturer quality-system/heritage information must continue to remain traceable to the claim registry/source records.

Pi 5 **staging deployment is ready now**. Public DNS should not be pointed at the Pi until `python3 scripts/preflight.py --production` returns `PASS`.
