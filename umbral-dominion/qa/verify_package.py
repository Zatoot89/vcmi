#!/usr/bin/env python3
"""Artifact static smoke tests. Does NOT execute a game or claim gameplay PASS."""
import io
import json
import wave
import hashlib
import sys
import zipfile
from pathlib import Path
from PIL import Image

build=Path(sys.argv[1]) if len(sys.argv)>1 else Path("umbral-dominion/build")
report=json.loads((build/"validation.json").read_text(encoding="utf-8"))
assert report["validatedEntities"]["creatures"]==14
assert report["validatedEntities"]["heroes"]==8
assert report["townDwellingCount"]==14
assert report["missingArtCount"]==0,"Some artwork references are unresolved"
assert report["musicCreated"],"No original generated theme"
assert report["originalCreatureSfxCount"]==72,"Expected original 72 prototype creature SFX"
assert report["sfxProductionReady"] is False
archive=build/"umbral-dominion-dev-DRAFT.zip"
with zipfile.ZipFile(archive) as z:
    names=set(z.namelist())
    root="Mods/umbralDominion/"
    assert root+"mod.json" in names
    assert root+"Content/Music/UD_EBON_SPIRE.ogg" in names
    configs=[n for n in names if "/config/" in n and n.endswith(".json")]
    assert len(configs)>=4
    sprites={Path(n).name for n in names if "/sprites/" in n}
    images={Path(n).name for n in names if "/data/" in n}
    for item in sorted(n for n in names if "/sprites/" in n and n.endswith(".json")):
        data=json.loads(z.read(item))
        assert "sequences" in data and data["sequences"],item
        for seq in data["sequences"]:
            assert seq["frames"],item
            assert all(f in sprites for f in seq["frames"]),(item,seq)
    image_count=0
    for item in sorted(n for n in names if "/data/" in n and n.endswith(".png")):
        with Image.open(io.BytesIO(z.read(item))) as img:
            img.verify()
        image_count+=1
    assert image_count>=250,f"Only {image_count} PNG files present"
    for item in configs:
        assert json.loads(z.read(item)),"Empty JSON config: "+item
    sound_root=root+"Content/sounds/"
    actual_sounds={n for n in names if n.startswith(sound_root) and n.lower().endswith(".wav")}
    creature_cfg=json.loads(z.read(root+"Content/config/creatures.json"))
    assert len(creature_cfg)==14
    configured=[]
    for key,creature in creature_cfg.items():
        sounds=creature["sound"]
        expected={"attack","defend","killed","move","wince"}
        if key in ("veilArcher","nightstalker"):expected.add("shoot")
        assert set(sounds)==expected, (key,sounds)
        for event,f in sounds.items():
            assert sound_root+f in actual_sounds,(key,event,f)
            configured.append(sound_root+f)
    assert len(set(configured))==72 and len(actual_sounds)==72
    for path in configured:
        with wave.open(io.BytesIO(z.read(path)),"rb") as wav:
            assert wav.getnchannels()==1
            assert wav.getsampwidth()==2
            assert wav.getframerate()==22050
            assert wav.getnframes()>2000
    print("PASS original prototype creature audio: 14 units, 72 valid distinct PCM WAV effects")
    art=report["paintedConceptArt"]
    assert art["creatures"]==14 and art["heroes"]==8 and art["townScenes"]==1
    assert not report["releaseReady"] and art["genuineAnimationSequences"]==0
    assert report["windowsQA"]=="NOT_TESTED"
    with Image.open(io.BytesIO(z.read(root+"Content/data/UD_TOWN_BACKGROUND.png"))) as im:
        assert im.size==(800,374)
    for creature in ("ASHLING","UMBRALDRAGON","GLOOMHOUND"):
        with Image.open(io.BytesIO(z.read(root+"Content/sprites/UD_"+creature+"_FRAME0.png"))) as img:
            assert img.size==(120,110)
    print("PAINTED CONCEPT QA: 14 unit stills, 8 portraits, 1 scene — no original artist motion frames.")
    motion = report["spritePosePipeline"]
    assert motion["creatures"] == 14 and motion["spriteSheets"] == 14
    assert motion["buildingOverlays"] == 8
    assert motion["animationStatus"] == "GENERATED_MOTION_PREVIEW_REQUIRES_AUTHOR_ART"
    assert (build/"SPRITE_ACTION_PREVIEW.png").is_file()
    assert (build/"SPRITE_MOTION_PREVIEW.gif").is_file()
    print(f"PASS prototype static QA: {image_count} verified PNGs; "
          f"{len([n for n in names if n.endswith('.json') and '/sprites/' in n])} "
          "animation descriptors; 14 dwellings; 14 creatures; music OGG.")
    print("NOT TESTED: VCMI runtime, Windows loading, recruitment, combat, or polished art.")
