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

## Milestone 0.4 — coverage reporting and town-placement audit

- **14/14 creatures have action-state coverage**, but only four units have four distinct AI-illustrated key poses each (16 illustrated sources). The other **ten use 40 computer-derived poses**, four per unit, from their original single stills. They are **not** new illustrated artwork and **not** approved animation.
- The reproducible `DERIVED_POSE_REVIEW.png` displays those ten rows and source-action transformations. The existing `KEYPOSE_APPROVAL_SHEET.png` continues to display the four AI-illustrated units.
- All **36 Ebonspire town-structure overlays** now use deterministic derivatives of the **eight painted source buildings**; these are **not 36 independent building paintings**. The `TOWN_STRUCTURE_REVIEW.png` contact sheet identifies the derived source for each.
- `TOWN_LAYOUT_DIAGNOSTIC.png` previews the configured x/y/z positions. `town-art-report.json` records placements extending past the town's 800×374 canvas. Overlaps and click masks are not verified by the game.
- `qa/test_art_readiness.py` independently verifies art provenance, prevents source-count inflation, requires truthful release readiness, and audits every packaged structure PNG.
- GitHub Actions continues to run separate Linux JSON/asset QA and a **Windows installation-only smoke test**. Neither proves gameplay.

**Release remains BLOCKED.** Future work: 40 authentic source poses for the remaining ten, complete authored combat frames, uniquely illustrated towns, engine runtime testing.

## v0.5 static placement correction — bounded, reversible, NOT gameplay-verified

The v0.4 town structure configuration had **15 overlays with x/y coordinates beyond the 800×374 preview canvas** (155×112 preview sprites). The original coordinates and exact before/after delta for each are saved in `design/town-layout-corrections.json`. This milestone conservatively clamps only those 15 x/y positions inside the preview image; other 21 positions and all z values are unchanged.

This resolves *static* canvas clipping but **does not solve artistic overlapping, clickable masks, depth order or the real VCMI renderer**. The new `TOWN_LAYOUT_BEFORE_AFTER.png` and `town-art-report.json` contain the evidence; the report lists potential bounding-box occlusions for review. The CI gate fails if any town overlay remains outside canvas bounds.

## v0.5 art ingestion and automatic coverage accounting

Ten remaining creature pairs can now be upgraded simply by adding a **transparent 1774×887 2-row × 4-column atlas** under `assets-source/keypose-atlases/`. Use these exact filenames:

| Source atlas | Top row | Bottom row |
|---|---|---|
| `ashling-cinderimp.webp` | Ashling | Cinder Imp |
| `grave-doom-sentinels.webp` | Grave Sentinel | Doom Sentinel |
| `hexbinder-soulweaver.webp` | Hexbinder | Soul Weaver |
| `dusk-abyssal-reavers.webp` | Dusk Reaver | Abyssal Reaver |
| `umbral-eclipse-dragons.webp` | Umbral Dragon | Eclipse Dragon |

For each row use columns **idle, move, attack (or cast), hit**. Draw distinct character poses, consistent right-facing perspective, transparent canvas, centered figure and preserved anatomy and silhouette. Use independent original/lawfully licensed art; do not substitute recolored still frames.

When a valid atlas is committed, the same workflow **automatically** replaces the single-still derived group frames, checks all four poses for uniqueness, updates `KEYPOSE_APPROVAL_SHEET.png`, shrinks `ARTWORK_BACKLOG.json`, and updates the creature source-quality counters. No Python edits are required for each asset.

These 4 poses per unit are **key-pose studies, not full finished combat animation**. Death, turn, attacks, gameplay bounds and all rendered transitions still require review.
