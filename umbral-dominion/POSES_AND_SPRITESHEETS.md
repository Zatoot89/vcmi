# Umbral Dominion Sprite Pipeline — VCMI

## Status: reproducible **alpha motion prototype**; not release-ready

One `push` to the `develop` branch with files under `umbral-dominion/scripts/`, `assets-source/`, or `design/` launches the GitHub workflow **Umbral Dominion – Auto Build**. This generates all sprite frames, sprite sheets, VCMI JSON animation descriptors, archive, preview images and QA reports. The job deliberately does **not** claim in-game compatibility or frame-by-frame animation artistry.

### Generation inputs

- `assets-source/creatures-master.webp` — four isolated, correctly mapped dark-fantasy creature illustrations (Gloom Hound, Dread Hound, Veil Archer, Nightstalker), 4× 256px cells.
- `assets-source/buildings-master.webp` — eight isolated illustrated structures in a 4×2 atlas (256×288px cells).
- `assets-source/creature-concepts.png` — existing other ten painted creature studies.
- `assets-source/authored-poses/<creatureKey>/group-XX/*.png` — **optional real manually authored animation frames** for one creature and VCMI group, in numbered order. If the directory exists it **must** contain at least 2 visually different PNGs; otherwise the build fails. Example `assets-source/authored-poses/veilArcher/group-15/000.png`, `001.png`, `002.png`, etc.

### Group coverage and output

The generated baseline covers the documented VCMI groups: 0 movement, 1 fidget, 2 idle, 3 hit, 4 defense, 5 and 6 death, 7 and 8 turning, 11–13 melee, 17–19 special, 20 and 21 movement start/end, 22–23 dead pose, 24 resurrection. Veil Archer and Nightstalker additionally include shooting groups 14–16. Hexbinder and Soul Weaver include spellcasting 30–32; dragons include group attacks 40–42.

For all 14 creatures the build writes:

- `Content/sprites/UD_<CREATURE>.json` — VCMI group descriptors with precise PNG filenames
- `Content/sprites/UD_<CREATURE>_G<GROUP>_<FRAME>.png` — frame files, with transparent canvas
- `Content/sprites/UD_<CREATURE>_SHEET.png` — actual 6×6 sprite/contact sheet for review (1080×960 px)
- `SPRITE_ACTION_PREVIEW.png` — 14-creature review matrix
- `sprite-pose-report.json` — group counts, frame counts, unique-frame hashes and origin of each group
- `BUILD_REPORT.md`, `validation.json`, `missing-assets.json`, `umbral-dominion-dev-DRAFT.zip`

The pipeline also substitutes eight building illustrations for their matching `UD_TOWN_*_FRAME0/1.png` prototypes: village hall, fort, citadel, mage guild level 1, marketplace, tavern, blacksmith and Obsidian Reliquary. Town alignment and 28 remaining buildings remain provisional.

### Quality gates

The CI audit checks file counts, actual distinct PNG bytes, required combat group IDs, transparent format, sprite sheet shape, exact VCMI JSON references, and eight town overlay mappings. It does **not** approve a mod merely because files exist. Generated pose motion consists of transformations and effects of painted still art, **not** true independently illustrated motion frames, and cannot pass the artistic release gate. The release gate remains blocked until the art is approved and tested on Windows VCMI.

Reference: https://vcmi.eu/modders/Animation_Format/ and https://vcmi.eu/modders/Entities_Format/Creature_Format/ .
## Milestone 0.3 — four AI-illustrated action-pose sets and Windows installation QA

- Source: `assets-source/keypose-atlases/hounds.webp` and `archers.webp`, both original generated transparent 2×4 illustration atlases.
- Units: Gloom Hound, Dread Hound, Veil Archer and Nightstalker. Each has four **distinct illustrated source poses**: idle, move, attack/shoot, hit (16 total).
- The build extracts source key poses, interpolates intermediate action frames, creates 14 sprite sheets and overwrites group descriptors. This is **AI-illustrated keyframe material plus synthetic motion**, not fully artist-animated movement.
- Ranged units now have a directional `UD_VOID_ARROW.json` projectile with five PNG directions. Timing/offset remain unverified without a VCMI game.
- `KEYPOSE_APPROVAL_SHEET.png` is the new QA visual artifact. `sprite-pose-report.json` records source image checksums and distinguishes these source poses from manually authored `authored-poses` overrides.
- A second GitHub Actions job runs **on Windows** with no Heroes III assets. It extracts/installs the generated ZIP in an isolated directory, checks required graphics and creates an upgrade backup on second installation.
- **Release remains blocked**: 10 creatures still have generated poses based on single painted stills; these four units lack fully illustrated action sequences; town-screen structures and gameplay remain untested.

The Windows CI smoke test is **not** a gameplay or launch test. Full acceptance still requires a user-controlled PC with VCMI and legitimate Heroes III resources.
