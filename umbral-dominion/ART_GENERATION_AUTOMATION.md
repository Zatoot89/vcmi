# Ebonspire — Automated source artwork (v0.5, manual approval)

## Why this exists

Source artwork is **not yet complete**. Four characters have 16 AI-illustrated source poses; ten characters still need five **original two-character pose atlases** (40 independently illustrated action poses). Rendered marketing posters do not count.

## GitHub Actions: Artwork Candidate

Run [Umbral Dominion - Artwork Candidate (manual)](https://github.com/Zatoot89/vcmi/actions/workflows/umbral-dominion-art-candidates.yml) on branch `develop`.

1. Select exactly one pair: `ashling-cinderimp`, `grave-doom-sentinels`, `hexbinder-soulweaver`, `dusk-abyssal-reavers`, or `umbral-eclipse-dragons`.
2. Leave `generate_paid_candidate=false` (default) for a **zero-cost** run that only writes the art brief and runs source-art QA.
3. To request **one potentially billable image** using Google's Gemini API, first create a repository Actions secret named `GEMINI_API_KEY` in GitHub Settings → Secrets and variables → Actions. Then explicitly select `generate_paid_candidate=true` AND `acknowledge_provider_charges=true`. Do not paste the API key into code or chat.
4. Download the `umbral-dominion-art-candidate-<run number>` artifact. Inspect `candidate_qa.json`, the source image, and any generated review preview.
5. A candidate **is not automatically approved, committed, merged, or released**. Human review must confirm anatomical consistency, limb and weapon positions, true transparency, and four distinct illustrated actions for each character.
6. Only after approval, convert the candidate to **1774 × 887 WebP with actual alpha**, and commit it with the appropriate exact filename to `umbral-dominion/assets-source/keypose-atlases/`.

The main build's `compile_sprites.py` ingests these filenames automatically when available and updates `ARTWORK_BACKLOG.json`.

## Production gates

- `test_art_candidate_gate.py` tests image transparency and rejects synthetic recolors of identical silhouettes. It is called from both workflows and passes offline without keys.
- The candidate generator runs in dry-run mode unless both charge-authorization inputs are true. No image API key or provider charges are required to validate code.
- Even successful image QA means **eligible for artistic review**, not finished combat animation or actual Windows gameplay verification.
- The Windows VCMI engine remains untested with Heroes III game data; release is blocked.
- Existing [main automated build](https://github.com/Zatoot89/vcmi/actions/workflows/umbral-dominion-autobuild.yml) can be manually dispatched on `develop`; the GitHub connection currently does not provide a direct workflow-dispatch operation.

Reference: [Google Gemini official image-generation guide](https://ai.google.dev/gemini-api/docs/generate-content/image-generation).
