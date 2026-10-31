# Umbral Dominion — Production Art Acceptance Criteria

**Status: blocked. The CI artifact contains temporary procedural silhouettes and is not finished art.**

## Assets to produce (source artwork, not auto-generated dummy files)

| Category | Minimum distinct deliverables | Acceptance gate |
|---|---|---|
| Ebonspire town background | 1 complete scene designed for the VCMI town layout | Professionally illustrated 800×374 or VCMI-compatible scene; fits structures |
| Individual town structures | 36 distinct overlaid structures or authored animations | Transparencies, positioning, masks and clickable regions tested |
| Creature units | 14 unique illustrated designs: Ashling, Cinder Imp, Gloom Hound, Dread Hound, Veil Archer, Nightstalker, Grave Sentinel, Doom Sentinel, Hexbinder, Soul Weaver, Dusk Reaver, Abyssal Reaver, Umbral Dragon, Eclipse Dragon | Each recognizably distinct and consistent with its named fantasy role |
| Creature battle sequences | 14 authored action sets | Idle, walk/fly, melee, defend, hit, death, shooting/casting as applicable, facing directions and frame timing |
| Eight heroes | Morvane, Kaedros, Tharok, Elys Vorn, Seralyth, Veyra, Malachar, Nyxara | Individually composed portraits (large and small), specialty icons |
| Map and town interface | Village/Fort/Citadel/Castle variants, hall icons, guild backgrounds, siege art, minimap, masks, puzzle map | Proper layers, alignment, transparency and no copied Heroes III artwork |
| Music | Original loopable Ebonspire OGG | Provenance and looping QA |

### Non-negotiable quality rules

1. **No simple colored polygons as creatures, no repeated single-frame fake walk cycles.**
2. Never describe `missingArtCount: 0` as proof of artwork completeness; it only means filenames resolve.
3. All artwork must be original/legally usable. Do not embed third-party copyrighted game assets.
4. Validate VCMI mod format; inspect assets visually; run actual Windows gameplay tests with logs and screenshots.
5. Run `python umbral-dominion/scripts/build_mod.py --release` as a final release gate. It currently **deliberately fails** until production release support is implemented and verified.

### Deliverables required for a release

A single installable VCMI package with 14 distinct creature designs and animations, eight heroes, Ebonspire town art, map assets, and all gameplay checks PASS. The current automated ZIP is not this deliverable.
