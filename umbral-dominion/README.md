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

**Artwork is NOT finished.** All generated silhouettes, town backgrounds, UI graphics and animation loops are **temporary placeholders**. Their presence does not mean production art exists. The generator creates geometric PNGs and prototype VCMI JSON frame sequences with a composed OGG theme. They are not polished fantasy illustrations or genuine gameplay animations. An artifact preview `ASSET_PREVIEW.png` shows the generated look. See [WINDOWS_QA.md](WINDOWS_QA.md) for game tests, or install the draft with `scripts/install_windows.ps1` after downloading the CI ZIP. Runtime compatibility is still unverified.

## Release status — BLOCKED

- GitHub Actions green means **JSON structure and archive packaging pass only**.
- The art generator creates **procedural placeholder imagery** rather than finished original illustrations.
- The 14 creatures require **distinct approved visual designs and individually authored motion frames**; mirrored or slightly shifted still images do not count.
- Eight heroes need finished portraits and specialities; Ebonspire needs a professionally illustrated town, buildings, town map and screens.
- Gameplay on **Windows VCMI has not been tested**.
- Running the generator with `--release` deliberately fails rather than shipping these placeholders as a completed faction.

**Do not call this a completed playable mod.** The package is only an engineering prototype.
