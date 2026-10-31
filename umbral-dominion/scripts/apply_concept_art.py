#!/usr/bin/env python3
"""Integrate painted Ebonspire *concept studies*, not final sprites.

Tier-2/Tier-3 art is role-mismatched and combat frames are NOT animated.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets-source'
ROWS=[['ashling','gloomHound','veilArcher','graveSentinel','hexbinder','duskReaver','umbralDragon'],
      ['cinderImp','dreadHound','nightstalker','doomSentinel','soulWeaver','abyssalReaver','eclipseDragon']]
HEROES=['morvane','kaedros','tharok','elysVorn','seralyth','veyra','malachar','nyxara']

def save_fit(im, filename, size):
    src=ImageOps.contain(im.convert('RGBA'),size,Image.Resampling.LANCZOS)
    dst=Image.new('RGBA',size)
    dst.alpha_composite(src,((size[0]-src.width)//2,(size[1]-src.height)//2))
    dst.save(filename,optimize=True)

def apply_painted_concepts(generated_dir,build_dir):
    generated_dir=Path(generated_dir);build_dir=Path(build_dir)
    files=[SRC/f for f in ('creature-concepts.png','hero-portraits.png','ebonspire-town.png')]
    if not all(p.exists() for p in files):
        raise FileNotFoundError('Painted concept atlases missing: '+str([str(p) for p in files if not p.exists()]))
    stats={'creatures':0,'heroes':0,'townScenes':0,'approvedCharacterDesigns':0,
           'genuineAnimationSequences':0,
           'status':'PAINTED_ART_DIRECTION_CONCEPTS_NOT_PRODUCTION_SPRITES',
           'problems':['T2 painted quadruped wolf studies are concept-only; base and upgraded color variants need independent illustration',
                       'T3 studies are skeleton warriors with incorrect swords/shields; actual ranged archer designs must be painted',
                       'Single illustrated still per creature: actions/flight/walk/death unanimated'],
           'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    with Image.open(files[0]) as src:
        src=src.convert('RGBA')
        if src.size!=(1008,224): raise ValueError('Wrong creature atlas dimensions '+str(src.size))
        for row, names in enumerate(ROWS):
            for col,key in enumerate(names):
                sprite=src.crop((col*144,row*112,(col+1)*144,(row+1)*112))
                if sprite.getbbox() is None: raise ValueError('Blank painted sprite: '+key)
                prefix='UD_'+key.upper()
                for i in range(3):
                    # Deliberately repeated stills are NOT called actual combat animation.
                    save_fit(sprite,generated_dir/f'{prefix}_FRAME{i}.png',(120,110))
                save_fit(sprite,generated_dir/f'{prefix}_LARGE.png',(128,128))
                save_fit(sprite,generated_dir/f'{prefix}_SMALL.png',(58,58))
                stats['creatures']+=1
    with Image.open(files[1]) as src:
        src=src.convert('RGB')
        if src.size!=(704,110):raise ValueError('Wrong hero atlas dimensions '+str(src.size))
        for col,key in enumerate(HEROES):
            face=src.crop((col*88,0,(col+1)*88,110))
            prefix='UD_HERO_'+key.upper()
            save_fit(face,generated_dir/f'{prefix}_LARGE.png',(128,128))
            save_fit(face,generated_dir/f'{prefix}_SMALL.png',(58,58))
            stats['heroes']+=1
    with Image.open(files[2]) as im:
        if im.size!=(800,374):raise ValueError('Wrong town scene size '+str(im.size))
        im.convert('RGBA').save(generated_dir/'UD_TOWN_BACKGROUND.png',optimize=True)
        stats['townScenes']=1
    (build_dir/'artwork-concepts.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf-8')
    preview=Image.new('RGB',(1008,800),(24,13,34))
    d=ImageDraw.Draw(preview)
    d.text((12,14),'UMBRAL DOMINION — PAINTED CONCEPTS (NOT FINAL ART)',fill=(241,209,253))
    d.text((12,32),'Static illustrations only • roster mismatches • Windows QA outstanding',fill=(200,151,220))
    with Image.open(files[2]) as im:preview.paste(im.convert('RGB'),(104,55))
    with Image.open(files[0]) as im:preview.paste(im.convert('RGBA'),(0,440),im.convert('RGBA'))
    with Image.open(files[1]) as im:preview.paste(im.convert('RGB'),(152,680))
    preview.save(build_dir/'ARTWORK_PREVIEW.png',optimize=True)
    return stats