# Umbral Dominion — Production Art Acceptance Criteria

**Status: blocked. The new alpha now contains illustrated source concepts for 14 creatures, 8 heroes and the Ebonspire town background, but they are NOT finished art or animation.**

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

## Stage 1 painted study — evidence

The `assets-source/` folder contains original AI-painted concept atlases, and `apply_concept_art.py` crops these into the build. The updated [GitHub Actions build](https://github.com/Zatoot89/vcmi/actions/runs/41231372364) passes JSON/package validation, not gameplay. It reports 14 creature stills, eight portrait studies and one painted background. **Zero** actual animation sequences are approved, and Windows runtime testing is still outstanding.

**Known invalid creature mappings:** Gloom Hound / Dread Hound now have painted four-legged wolf concepts but need independently drawn upgrades and animation. Veil Archer / Nightstalker still have skeleton warrior studies with wrong weapons; proper bow-wielding designs must be painted. Please don't treat image file counts or repeated still frames as completion.

## v0.4 independent art provenance audit

- 4 creatures × 4 AI-illustrated source poses = **16** key pose studies (still require quality approval and authored transitions).
- 10 other creatures × 4 computer-derived transformations = **40** non-illustrated pose studies. **0** newly independently illustrated poses for these ten.
- 36 town image overlays are variants of **8 original architectural concept paintings**. **0** independently illustrated additional buildings.
- 15 town overlay placements extend beyond the configured 800×374 review canvas. Some may be intentional; inspect individually in actual VCMI.
- A distinct `qa/test_art_readiness.py` file verifies provenance and prevents a successful packaging build from falsely claiming complete artwork.
- Latest full Linux + Windows installation smoke PASS: [run #41240677938](https://github.com/Zatoot89/vcmi/actions/runs/41240677938).
- **Production release: BLOCKED.** Windows installation QA is not game-runtime QA.

## v0.5 town occlusion and illustration backlog evidence

The new town QA separately flags 54 rectangle overlaps as upgrade chains, related structure attachments or independent cases requiring visual review; only alpha-pixel intersections are used to prioritize—not to approve—those cases. The source artwork production briefs for the ten unfinished creatures are automatically emitted as `ART_GENERATION_BRIEFS.json` and `art-briefs/*.json` on each build. Their existence **does not mean** the illustrations are complete.

The automated pipeline must not mark gameplay, artistic animation or fully independent building artwork as passed solely because ZIP, schema, and Windows installer smoke tests pass.

## Creature sounds (prototype)

72 original synthesized PCM WAV clips are generated, mapped to creature attack/defend/killed/move/wince/shoot events, and statically tested. SFX gameplay mix/playback is **not verified**. These are not finished sampled/followed sound effects. Studio or human-reviewed sound polish remains outstanding.
