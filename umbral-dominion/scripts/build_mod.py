#!/usr/bin/env python3
"""Build Umbral Dominion VCMI draft content from source designs.

Outputs a schema-validated DEVELOPMENT ARCHIVE, NOT an installable town.
No downloads, proprietary game files, or fake artwork are included.
"""
import argparse
import json
import shutil
import sys
import zipfile
from collections import Counter
from art_pipeline import generate_assets, generate_music, make_preview
from apply_concept_art import apply_painted_concepts
from compile_sprites import generate_pose_sheets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent
DESIGNS = ROOT / "design"
DEFAULT_OUTPUT = ROOT / "build"
COST = {1: 65, 2: 120, 3: 250, 4: 400, 5: 750, 6: 1400, 7: 3200}
STACK = {1: (12, 24), 2: (7, 13), 3: (5, 9), 4: (3, 6),
         5: (2, 4), 6: (1, 3), 7: (1, 2)}
FACTION_ID = "umbralDominion"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")

def plural(name):
    return name + ("es" if name.endswith("s") else "s")

def validate_design(creatures, heroes, faction):
    if len(creatures) != 14 or len(heroes) != 8:
        raise ValueError("Expected exactly 14 creatures and eight heroes")
    if Counter(v["tier"] for v in creatures.values()) != {i: 2 for i in range(1, 8)}:
        raise ValueError("Seven tiers must have exactly two creatures each")
    for key, c in creatures.items():
        if c["damage"]["min"] > c["damage"]["max"]:
            raise ValueError(f"{key}: min damage > max")
        if min(c["attack"], c["defense"], c["hitPoints"], c["speed"]) <= 0:
            raise ValueError(f"{key}: invalid combat stat")
        target = c.get("upgradeTo")
        if target:
            if target not in creatures or creatures[target]["tier"] != c["tier"] or not creatures[target]["upgraded"]:
                raise ValueError(f"{key}: upgrade target invalid")
        elif not c["upgraded"]:
            raise ValueError(f"{key}: basic creature needs an upgrade")
    if set(faction["heroClasses"]) != {"Dreadlord", "Voidcaller"}:
        raise ValueError("Expected Dreadlord and Voidcaller")
    for h in heroes.values():
        if h["class"] not in faction["heroClasses"]:
            raise ValueError("Unknown hero class: " + h["class"])

def make_creatures(raw):
    result, assets = {}, []
    for key, src in raw.items():
        level = src["tier"]
        asset = "UD_" + key.upper()
        gold = int(COST[level] * (1.4 if src["upgraded"] else 1))
        value = max(1, round(src["hitPoints"] * (src["attack"] + src["defense"]) / 7))
        entity = {
            "name": {"singular": src["name"], "plural": plural(src["name"])},
            "description": "A warrior of the Umbral Dominion.",
            "faction": FACTION_ID, "level": level,
            "cost": {"gold": gold},
            "speed": src["speed"], "hitPoints": src["hitPoints"],
            "attack": src["attack"], "defense": src["defense"],
            "damage": src["damage"], "growth": src["growth"],
            "fightValue": value, "aiValue": value,
            "advMapAmount": {"min": STACK[level][0], "max": STACK[level][1]},
            "graphics": {
                "animation": asset + ".DEF",
                "map": asset + "_MAP.DEF",
                "iconLarge": asset + "_LARGE.png",
                "iconSmall": asset + "_SMALL.png",
                "animationTime": {"attack": 0.6, "walk": 0.9, "idle": 1.0},
                "timeBetweenFidgets": 15,
            },
            "sound": {},
        }
        if src.get("upgradeTo"):
            entity["upgrades"] = [src["upgradeTo"]]
        if src["role"] == "ranged":
            entity["shots"] = 12
            entity["graphics"]["missile"] = {
                "projectile": "UD_VOID_ARROW.json",
                "attackClimaxFrame": 3,
                "offset": {"upperX": 70, "upperY": 44,
                           "middleX": 88, "middleY": 75,
                           "lowerX": 86, "lowerY": 100},
                "frameAngles": [90, 45, 0, -45, -90],
            }
        if level == 7:
            entity["doubleWide"] = True
        result[key] = entity
        assets.extend([
            {"owner": key, "type": "creature animation", "filename": asset + ".DEF"},
            {"owner": key, "type": "map animation", "filename": asset + "_MAP.DEF"},
            {"owner": key, "type": "large icon", "filename": asset + "_LARGE.png"},
            {"owner": key, "type": "small icon", "filename": asset + "_SMALL.png"},
        ])
    return result, assets

def make_heroes(raw):
    heroes, assets = {}, []
    for key, src in raw.items():
        hero_class = "dreadlord" if src["class"] == "Dreadlord" else "voidcaller"
        portrait = "UD_HERO_" + key.upper()
        special = src["specialtyConcept"]
        is_might = hero_class == "dreadlord"
        heroes[key] = {
            "class": hero_class,
            "female": key in {"seralyth", "veyra", "nyxara"},
            "army": [{"creature": "ashling", "min": 15, "max": 25},
                     {"creature": "gloomHound", "min": 3, "max": 5}],
            "skills": [{"skill": "offense", "level": "basic"}] if is_might
                      else [{"skill": "wisdom", "level": "basic"}],
            "specialty": {"creature": "ashling"} if is_might
                         else {"secondary": "sorcery"},
            "texts": {
                "name": src["name"],
                "biography": f"{src['name']} serves the Umbral Dominion.",
                "specialty": {
                    "name": special,
                    "description": f"Concept: {special}. Prototype specialty requires implementation.",
                    "tooltip": f"Concept: {special}; temporary vanilla-compatible specialty."
                },
            },
            "images": {
                "large": portrait + "_LARGE.png",
                "small": portrait + "_SMALL.png",
                "specialtyLarge": portrait + "_SPEC_LARGE.png",
                "specialtySmall": portrait + "_SPEC_SMALL.png",
            },
        }
        for suffix, kind in [
            ("_LARGE.png", "hero portrait large"),
            ("_SMALL.png", "hero portrait small"),
            ("_SPEC_LARGE.png", "hero specialty large icon"),
            ("_SPEC_SMALL.png", "hero specialty small icon"),
        ]:
            assets.append({"owner": key, "type": kind, "filename": portrait + suffix})
    return heroes, assets

def make_hero_classes():
    classes = {}
    for name, affinity in [("dreadlord", "might"), ("voidcaller", "magic")]:
        base = "UD_" + name.upper()
        if affinity == "might":
            primary = {"attack": 2, "defense": 2, "spellPower": 1, "knowledge": 1}
            low = {"attack": 35, "defense": 35, "spellPower": 15, "knowledge": 15}
            high = {"attack": 30, "defense": 30, "spellPower": 20, "knowledge": 20}
            secondary = {"offense": 8, "armorer": 6, "tactics": 6, "logistics": 5,
                         "wisdom": 2, "sorcery": 2}
        else:
            primary = {"attack": 0, "defense": 1, "spellPower": 3, "knowledge": 2}
            low = {"attack": 10, "defense": 15, "spellPower": 40, "knowledge": 35}
            high = {"attack": 15, "defense": 15, "spellPower": 35, "knowledge": 35}
            secondary = {"wisdom": 8, "sorcery": 7, "earthMagic": 7,
                         "intelligence": 5, "offense": 2}
        classes[name] = {
            "name": "Dreadlord" if affinity == "might" else "Voidcaller",
            "faction": FACTION_ID, "affinity": affinity,
            "commander": "graveSentinel",
            "animation": {"battle": {"male": base + "_MALE.DEF",
                                     "female": base + "_FEMALE.DEF"}},
            "mapObject": {"filters": {}},
            "primarySkills": primary,
            "secondarySkills": secondary,
            "lowLevelChance": low,
            "highLevelChance": high,
            "defaultTavern": 5,
            "tavern": {},
        }
    assets = [
        {"owner": "hero classes", "type": "hero battle animation",
         "filename": "UD_" + name.upper() + "_" + gender + ".DEF"}
        for name in ("dreadlord", "voidcaller")
        for gender in ("MALE", "FEMALE")
    ]
    return classes, assets

def validate_schemas(schema_dir, data):
    try:
        from jsonschema import Draft4Validator, RefResolver
        import json5
    except ImportError as exc:
        raise RuntimeError("Install dependency with pip install jsonschema") from exc
    results = {}
    for typ, schema_filename, obj in data:
        path = schema_dir / schema_filename
        if not path.exists():
            raise FileNotFoundError(f"Required official VCMI schema is missing: {path}")
        schema = json5.loads(path.read_text(encoding="utf-8"))
        resolver = RefResolver(base_uri=path.resolve().as_uri(), referrer=schema)
        validator = Draft4Validator(schema, resolver=resolver)
        count = 0
        for key, value in obj.items():
            errors = sorted(validator.iter_errors(value), key=lambda e: str(e.path))
            if errors:
                msg = "; ".join(f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors[:5])
                raise ValueError(f"{typ}.{key} schema validation failed: {msg}")
            count += 1
        results[typ] = count
    return results

def replace_custom_animation_refs(value):
    """Map our virtual DEF identifiers to VCMI-native JSON animation files."""
    if isinstance(value, dict):
        return {k: replace_custom_animation_refs(v) for k, v in value.items()}
    if isinstance(value, list):
        return [replace_custom_animation_refs(v) for v in value]
    if isinstance(value, str) and value.startswith("UD_") and value.upper().endswith(".DEF"):
        return value[:-4] + ".json"
    return value

def build(schema_dir, output, require_art=False, procedural=True, release=False):
    creatures_raw = load(DESIGNS / "creatures.json")
    heroes_raw = load(DESIGNS / "heroes.json")
    faction_design = load(DESIGNS / "faction-design.json")
    validate_design(creatures_raw, heroes_raw, faction_design)
    town_design = load(DESIGNS / "ebonspire-town.json")
    town = town_design["town"]
    if len(town["creatures"]) != 7:
        raise ValueError("Ebonspire must define seven creature tiers")
    for tier, pair in enumerate(town["creatures"], start=1):
        if len(pair) != 2 or any(c not in creatures_raw for c in pair):
            raise ValueError(f"Unknown or invalid Ebonspire creature tier {tier}")
        if any(creatures_raw[c]["tier"] != tier for c in pair):
            raise ValueError(f"Ebonspire tier mismatch: {tier}")
        for building in ("dwellingLvl" + str(tier), "dwellingUpLvl" + str(tier)):
            if building not in town["buildings"] or building not in town["structures"]:
                raise ValueError(f"Missing Ebonspire town dwelling: {building}")
    for row in town["hallSlots"]:
        for slot in row:
            for building in slot:
                if building not in town["buildings"]:
                    raise ValueError(f"Missing Ebonspire hall building: {building}")
    creatures, creature_assets = make_creatures(creatures_raw)
    heroes, hero_assets = make_heroes(heroes_raw)
    classes, class_assets = make_hero_classes()
    # Generated artwork is explicitly a prototype, not a substitute for final art.
    town["tavernVideo"] = "TAVERN.BIK"  # use installed original-game data, do not redistribute it
    town["siege"]["imagePrefix"] = "SGIN"  # base-game siege layers until bespoke artwork is QA-tested
    faction = {FACTION_ID: {
        "name": faction_design["name"],
        "description": "Ebonspire original-art gameplay prototype; Windows runtime not verified.",
        "boat": "boatNecropolis",
        "alignment": "evil",
        "nativeTerrain": "subterranean",
        "creatureBackground": {"120px": "UD_CREATURE_BG_120.png", "130px": "UD_CREATURE_BG_130.png"},
        "town": town,
        "puzzleMap": town_design["puzzleMap"],
        "preferUndergroundPlacement": True,
    }}
    manifest = {
        "name": "Umbral Dominion (original-art prototype)",
        "description": "Procedurally illustrated alpha preview. Requires Windows VCMI gameplay QA.",
        "version": "0.3.0-alpha",
        "author": "Zatoot89",
        "contact": "https://github.com/Zatoot89/vcmi",
        "modType": "Town",
        "factions": ["config/faction.json"],
        "creatures": ["config/creatures.json"],
        "heroClasses": ["config/heroClasses.json"],
        "heroes": ["config/heroes.json"],
    }
    creatures = replace_custom_animation_refs(creatures)
    heroes = replace_custom_animation_refs(heroes)
    classes = replace_custom_animation_refs(classes)
    faction = replace_custom_animation_refs(faction)
    validated = validate_schemas(schema_dir, [
        ("creatures", "creature.json", creatures),
        ("heroes", "hero.json", heroes),
        ("heroClasses", "heroClass.json", classes),
        ("factions", "faction.json", faction),
        ("mod", "mod.json", {"manifest": manifest}),
    ])
    mod = output / "Mods" / "umbralDominion"
    if mod.exists():
        shutil.rmtree(mod)
    config = mod / "Content" / "config"
    write(mod / "mod.json", manifest)
    write(config / "creatures.json", creatures)
    write(config / "heroes.json", heroes)
    write(config / "heroClasses.json", classes)
    write(config / "faction.json", faction)
    town_assets = [{"owner": "Ebonspire", "type": "town graphics", "filename": name}
                   for name in town_design["requiredAssets"]]
    assets = creature_assets + hero_assets + class_assets + town_assets + [
        {"owner": "Ebonspire", "type": "creature screen", "filename": "UD_CREATURE_BG_120.png"},
        {"owner": "Ebonspire", "type": "creature screen", "filename": "UD_CREATURE_BG_130.png"},
    ]
    expected = sorted(set(a["filename"] for a in assets))
    generated_dir = output / "generated-assets"
    generated = generate_assets(expected, generated_dir) if procedural else {"covered": 0, "generated": 0}
    if procedural:
        make_preview(generated_dir, output / "ASSET_PREVIEW.png")
        painted_concepts = apply_painted_concepts(generated_dir, output)
        pose_report = generate_pose_sheets(generated_dir, output)
    else:
        pose_report = {"creatureCount": 0, "spriteSheetCount": 0, "paintedBuildingOverlays": 0,
                       "overallAuthoredAnimationFrames": 0}
        painted_concepts = {"creatures": 0, "heroes": 0, "townScenes": 0,
                            "approvedCharacterDesigns": 0, "genuineAnimationSequences": 0}
    supplied_dir = ROOT / "assets"
    # Animations are modern VCMI JSON; individual frames are PNG.
    for source in sorted(generated_dir.glob("*")) if procedural else []:
        if source.name == "ASSET_CATALOG.json":
            continue
        paths = ["sprites"] if source.suffix.lower() == ".json" else ["data", "sprites"]
        for category in paths:
            target = mod / "Content" / category / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for a in assets:
        filename = a["filename"]
        generated_name = filename[:-4] + ".json" if filename.upper().endswith(".DEF") else filename
        source = supplied_dir / generated_name
        if not source.exists() and not filename.upper().endswith(".DEF"):
            source = supplied_dir / filename
        a["suppliedByUser"] = source.is_file()
        a["provided"] = a["suppliedByUser"] or (generated_dir / generated_name).is_file()
        a["prototype"] = bool(not a["suppliedByUser"] and a["provided"])
        if a["suppliedByUser"]:
            for category in (["sprites"] if source.suffix.lower() == ".json" else ["data", "sprites"]):
                target = mod / "Content" / category / generated_name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    missing = [a for a in assets if not a["provided"]]
    placeholder_count = sum(a["prototype"] for a in assets)
    # A present image file is not proof of production-quality sprite animation.
    # Explicitly block any release from this prototype generator.
    if release:
        raise RuntimeError(
            f"RELEASE BLOCKED: {placeholder_count} procedural placeholder references; "
            "no VCMI Windows runtime QA evidence; final animations not verified. "
            "The current pipeline only builds prototype artifacts."
        )
    music_file = generate_music(mod) if procedural else None
    write(output / "missing-assets.json", missing)
    write(output / "validation.json", {
        "schemaDirectory": str(schema_dir),
        "validatedEntities": validated,
        "tierCount": 7,
        "missingArtCount": len(missing),
        "townImplemented": True,
        "townRuntimeTested": False,
        "proceduralPrototypeArt": procedural,
        "generatedFileCount": generated["generated"],
        "generatedAssetReferences": generated["covered"],
        "originalArtwork": False,
        "musicCreated": music_file is not None,
        "visualPlaceholderCount": placeholder_count,
        "paintedConceptArt": painted_concepts,
        "spritePosePipeline": {
            "creatures": pose_report["creatureCount"],
            "spriteSheets": pose_report["spriteSheetCount"],
            "buildingOverlays": pose_report["paintedBuildingOverlays"],
            "artistAuthoredAnimationFrames": pose_report["overallAuthoredAnimationFrames"],
            "illustratedKeyPoseCreatures": pose_report["illustratedKeyPoseCreatureCount"],
            "illustratedKeyPoseCount": pose_report["illustratedKeyPoseCount"],
            "keyPoseMethod": pose_report["keyPoseMethod"],
            "rangedMissile": pose_report["rangedMissile"],
            "animationStatus": "GENERATED_MOTION_PREVIEW_REQUIRES_AUTHOR_ART",
        },
        "productionArtComplete": False,
        "artworkQuality": "PLACEHOLDER_CONCEPT_ONLY" if placeholder_count else "UNVERIFIED_CUSTOM",
        "animationQuality": "PROCEDURALLY_POSED_FRAMES_NOT_HAND_AUTHORED",
        "releaseReady": False,
        "windowsQA": "NOT_TESTED",
        "sourceImagesAreReleaseArt": False,
        "townBuildingCount": len(town["buildings"]),
        "townDwellingCount": sum(k.startswith("dwelling") for k in town["buildings"]),
        "playable": False,
        "runtimeVerified": False,
        "notes": ["Ebonspire JSON configuration is generated; UI graphics and runtime verification remain incomplete.",
                  "Painterly concepts now replace unit stills, portrait icons and Ebonspire background.",
                  "Tier 2/Tier 3 painted concepts do not match named hounds/archers.",
                  "Animation groups now have distinct procedurally posed preview frames; NOT hand-authored animation.",
                  "Other graphics remain procedural placeholders.",
                  "Hero specialties and hero-class map objects are provisional.",
                  "Schema validation DOES NOT mean VCMI runtime compatibility.",
                  "Never redistribute Heroes III assets as part of this package."]
    })
    summary = [
        "# Umbral Dominion - automated build",
        "", "| Check | Status |", "|---|---|",
        "| Seven creature tiers | PASS |",
        "| 14 creature JSON objects | PASS |",
        "| Eight hero JSON objects | PASS |",
        "| Two hero class JSON objects | PASS |",
        "| VCMI JSON schema validation | PASS |",
        f"| Missing artwork files | {len(missing)} |",
        f"| Ebonspire town structures/buildings | {len(town['buildings'])} configured |",
        "| Ebonspire dwelling buildings | 14 configured |",
        f"| Artwork covered | {len(assets)-len(missing)} / {len(assets)} (procedural placeholders) |",
        f"| Original ambient music | {'YES' if music_file else 'NO'} |",
        f"| Procedural placeholder references | {placeholder_count} |",
        f"| Painted creature concept stills | {painted_concepts['creatures']} (NOT final roster art) |",
        f"| Painted hero portrait concepts | {painted_concepts['heroes']} |",
        f"| Painted Ebonspire scene | {painted_concepts['townScenes']} |",
        f"| Grouped sprite sheets | {pose_report['spriteSheetCount']} generated (unapproved animation) |",
        f"| VCMI mapped building overlays | {pose_report['paintedBuildingOverlays']} illustrated prototypes |",
        f"| Distinct AI-illustrated key poses | {pose_report['illustratedKeyPoseCount']} (4 creatures) |",
        f"| Artist-authored animation frames | {pose_report['overallAuthoredAnimationFrames']} |",
        "| Windows install smoke | Separate Windows Actions job; not gameplay |",
        "| Production-quality artwork | NOT DELIVERED |",
        "| Genuine authored animation / runtime | NOT YET |",
        "| Production release | BLOCKED |",
        "| Playable Ebonspire town | NOT RUNTIME TESTED |",
        "| Prototype install smoke test | MANUAL WINDOWS QA REQUIRED |",
        "", "This is a DEVELOPMENT BUILD. Do not install it as a completed faction."
    ]
    summary_path = output / "BUILD_REPORT.md"
    summary_path.write_text("\n".join(summary) + "\n", encoding="utf-8")
    zipname = output / "umbral-dominion-dev-DRAFT.zip"
    with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(mod.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(output))
        for p in (summary_path, output / "validation.json",
                  output / "missing-assets.json",
                  output / "sprite-pose-report.json") if procedural else (
                  summary_path, output / "validation.json",
                  output / "missing-assets.json"):
            z.write(p, p.relative_to(output))
    if require_art and missing:
        raise RuntimeError(f"Strict asset check failed: {len(missing)} art files missing.")
    print(f"PASS: {validated}; missing assets {len(missing)}")
    print(f"DRAFT: {zipname}")
    return zipname

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schemas", type=Path, default=PROJECT_ROOT / "config" / "schemas")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--strict-assets", action="store_true")
    parser.add_argument("--release", action="store_true",
                        help="Block releases until production art and Windows QA are implemented")
    parser.add_argument("--no-generated-art", action="store_true",
                        help="Require licensed user-supplied graphics instead of generated prototypes")
    args = parser.parse_args()
    try:
        build(args.schemas, args.out, args.strict_assets,
              procedural=not args.no_generated_art, release=args.release)
    except Exception as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
