# Windows installation and runtime acceptance test — prototype

This mod is **not a verified playable release**. The GitHub Actions generated prototype has original procedural artwork and JSON animations, but it has not been loaded into a real Windows VCMI game. Its visuals are deliberate placeholders.

1. In [the latest successful Actions run](https://github.com/Zatoot89/vcmi/actions), download `umbral-dominion-windows-DRAFT`.
2. Unzip the Actions artifact. Then unzip its nested `umbral-dominion-dev-DRAFT.zip`.
3. Copy the enclosed `Mods/umbralDominion` folder into `%USERPROFILE%\Documents\My Games\vcmi\Mods\umbralDominion`. Respect existing custom `userDataPath` overrides.
4. Launch VCMI Launcher; use your own legally obtained Heroes III Complete game data.
5. Enable Umbral Dominion in the Mods list. Record a screenshot and whether the launcher reports parse or missing-asset errors.
6. Start a new skirmish using Ebonspire. Capture the VCMI version, game log path, an in-town screenshot, and any error dialogue.
7. In a new game, verify all 7 basic and upgraded dwellings, creature recruitment, growth, army upgrades, and battlefield sprite groups. Verify siege, map town objects, tavern heroes, mage guild, and the town music.

## PASS / FAIL evidence

| Test | Current state |
|---|---|
| JSON schemas | PASS (CI) |
| 14 creatures, 8 heroes, 2 hero classes | PASS (CI) |
| 36 town buildings, 14 dwellings | PASS static configuration (CI) |
| PNG / animation / OGG package | PASS static (CI), if workflow green |
| VCMI launcher discovers and enables mod | NOT TESTED |
| Town screen visible without errors | NOT TESTED |
| Dwelling recruitment + upgrade | NOT TESTED |
| Creature combat animations | NOT TESTED |
| Windows gameplay and siege | NOT TESTED |

Static validation cannot prove game compatibility. Keep this prototype clearly labelled until runtime PASS. See [VCMI Windows installation](https://vcmi.eu/players/Installation_Windows/) and [VCMI animation format](https://vcmi.eu/modders/Animation_Format/).
