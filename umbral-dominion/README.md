# Umbral Dominion — Automated GitHub Action for Windows VCMI (draft)

This folder is the source of the Umbral Dominion faction in the existing VCMI fork. It generates a **development draft**, not a playable town and not a Windows .exe.

## Automated runs
Push changes to `umbral-dominion/design/`, `umbral-dominion/scripts/`, `umbral-dominion/assets/` or `.github/workflows/umbral-dominion-autobuild.yml` on `develop` to regenerate the package.

Actions → **Umbral Dominion - Auto Build (Windows mod draft)** → **Run workflow** also supports manual runs. The optional `strict_assets` input fails if required artwork is missing.

The job builds 14 creature configs (seven base/upgrade pairs), eight heroes, two hero classes, a preliminary faction, a mod manifest, schema validation and a `umbral-dominion-windows-DRAFT` Actions artifact.

To advance to playable status, implement Ebonspire's town configuration, its buildings and dwellings, siege, map objects, graphics and audio; test in a local Windows VCMI installation with your own Heroes III data. The official schemas in `config/schemas` are used at build time.

Only use original or appropriately licensed art; do not redistribute proprietary Heroes III assets.
Official docs: https://vcmi.eu/modders/Readme/
