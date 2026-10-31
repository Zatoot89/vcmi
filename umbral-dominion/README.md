# Umbral Dominion — Automated GitHub Action for Windows VCMI (draft)

This folder is the source of the Umbral Dominion faction in the existing VCMI fork. It generates a **development draft**, not a playable town and not a Windows .exe.

## Automated runs
Push changes to `umbral-dominion/design/`, `umbral-dominion/scripts/`, `umbral-dominion/assets/` or `.github/workflows/umbral-dominion-autobuild.yml` on `develop` to regenerate the package.

Actions → **Umbral Dominion - Auto Build (Windows mod draft)** → **Run workflow** also supports manual runs. The optional `strict_assets` input fails if required artwork is missing.

The job builds 14 creature configs (seven base/upgrade pairs), eight heroes, two hero classes, Ebonspire's schema-level town (36 buildings, including seven basic and seven upgraded creature dwellings), a mod manifest, schema validation and a `umbral-dominion-windows-DRAFT` Actions artifact. The editable town specification is `design/ebonspire-town.json`.

The current successful development run reports 260 missing graphics assets and no runtime tests. Generated building positions, siege images and puzzle map art are still placeholders: **schema validation alone does not make the town playable**. To advance to playable status, replace placeholders with original/licensed art and audio, finalize siege/map object rendering and test in a local Windows VCMI installation with your own legally obtained Heroes III data. The official schemas in `config/schemas` are used at build time.

Only use original or appropriately licensed art; do not redistribute proprietary Heroes III assets.
Official docs: https://vcmi.eu/modders/Readme/

## Windows QA checklist

- [ ] Create the 260 missing animation/image files from the generated `missing-assets.json`.
- [ ] Add licensed/original town music and tavern video; verify VCMI asset paths.
- [ ] Verify building artwork, hit areas, town scene placements, and puzzle map.
- [ ] Test each basic and upgraded dwelling for correct recruitment, cost, growth, and upgrades.
- [ ] Test maps, sieges, Mage Guild, tavern heroes, and special buildings.
- [ ] Capture VCMI logs/screenshots and PASS/FAIL evidence from the Windows installation.
- [ ] Run the GitHub workflow with `strict_assets=true` and ship only after all runtime checks pass.

## Generated graphics and installing on Windows

**Artwork is NOT finished.** This stage introduces **14 painted creature concept stills, eight painted hero portrait concepts, and one illustrated 800×374 Ebonspire backdrop**, committed under `assets-source/`. Most other graphics (building overlays, sprite maps, specialty icons, siege, puzzle assets) remain geometric placeholders. The creature animation groups repeat static painted concepts rather than real motion frames. Two previews are included: `ARTWORK_PREVIEW.png` shows the illustrated concept studies; `ASSET_PREVIEW.png` shows the unrefined procedural assets still in the generator. See [WINDOWS_QA.md](WINDOWS_QA.md) for game tests, or install the draft with `scripts/install_windows.ps1` after downloading the CI ZIP. Runtime compatibility is still unverified.

## Release status — BLOCKED

- GitHub Actions green means **JSON structure and archive packaging pass only**.
- Some images are now original **AI-painted concept studies**; unfinished assets are still procedural placeholders. Tier-2 now depicts painted quadruped hounds (basic/upgraded color studies); tier-3 has humanoid skeleton studies without accurate ranged equipment and remains unapproved. The concepts are not roster-approved.
- The 14 creatures require **distinct approved visual designs and individually authored motion frames**; mirrored or slightly shifted still images do not count.
- Eight heroes need finished portraits and specialities; Ebonspire needs a professionally illustrated town, buildings, town map and screens.
- Gameplay on **Windows VCMI has not been tested**.
- Running the generator with `--release` deliberately fails rather than shipping these placeholders as a completed faction.

**Do not call this a completed playable mod.** The package is only an engineering prototype.

### Latest illustrated concept stage (31 October 2026)

- [x] Painted 800×374 Ebonspire panorama integrated as `UD_TOWN_BACKGROUND.png`.
- [x] 14 cropped painted creature stills loaded via `assets-source/creature-concepts.png`.
- [x] 8 painted hero portrait studies loaded via `assets-source/hero-portraits.png`.
- [x] GitHub Actions build and static archive QA **PASS** ([run #41231372364](https://github.com/Zatoot89/vcmi/actions/runs/41231372364)).
- [x] Replace the mismatched T2 skeleton concepts with painted dark hound studies.
- [ ] Author separate upgraded hound design and real T3 archer/nightstalker art; obtain visual approval for every unit.
- [ ] Produce 14 genuine, individually authored battle animations; static frames aren't movement.
- [ ] Produce 36 aligned building overlays, map-town animations, siege/puzzle/UI graphics.
- [ ] Test actual Windows VCMI gameplay with screenshots and logs.

**Technical CI PASS ≠ playable or finished art.** Release is deliberately blocked.

## Reproducible animation and sprite-sheet pipeline (prototype v0.2)

- **14 VCMI animation JSON files**, with explicit group coverage and varying generated action poses.
- **14 actual 6×6 sprite sheets**, one for each creature, stored within the mod archive.
- **Eight painted building graphics mapped** to selected Ebonspire structure animations. These overlays are not aligned or runtime-verified yet.
- **New inputs:** `assets-source/creatures-master.webp`, `buildings-master.webp` from the improved transparent PNG cuts.
- **Automated QA** checks action groups, frame uniqueness and every referenced PNG. Review `SPRITE_ACTION_PREVIEW.png`, `SPRITE_MOTION_PREVIEW.gif`, and `sprite-pose-report.json` in the workflow artifact.
- **Artist-authored pose override** supported at `assets-source/authored-poses/<creatureKey>/group-XX/*.png`; see [POSES_AND_SPRITESHEETS.md](POSES_AND_SPRITESHEETS.md).

**Quality statement:** These are transformed still-art procedural action previews, **not** individually illustrated movement, attacks, or death animations. The production/release gate remains BLOCKED until hand-authored action work and real VCMI Windows gameplay QA are complete.
