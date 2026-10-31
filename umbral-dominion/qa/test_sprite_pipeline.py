#!/usr/bin/env python3
"""Strict static audit of the visual prototype. DOES NOT assert artistic quality or game runtime."""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from PIL import Image

NAMES=('ashling','cinderImp','gloomHound','dreadHound','veilArcher','nightstalker',
 'graveSentinel','doomSentinel','hexbinder','soulWeaver','duskReaver','abyssalReaver',
 'umbralDragon','eclipseDragon')
BASE_GROUPS={0,1,2,3,4,5,6,7,8,11,12,13,17,18,19,20,21,22,23,24}

def check(build_dir):
    path=Path(build_dir)
    report=json.loads((path/'sprite-pose-report.json').read_text())
    assert report['creatureCount']==14
    assert report['spriteSheetCount']==14
    assert report['paintedBuildingOverlays']==8
    assert report['releaseApproved'] is False
    assert report['illustratedKeyPoseCreatureCount']==4
    assert report['illustratedKeyPoseCount']==16
    assert report['keyPoseMethod'].startswith('AI_ILLUSTRATED_')
    assert report['rangedMissile']['directions']==5
    for key in ('gloomHound','dreadHound','veilArcher','nightstalker'):
        unit=next(x for x in report['creatures'] if x['id']==key)
        assert unit['illustratedKeyPoseCount']==4, key
        assert len(set(unit['illustratedKeyPoseHashes'].values()))==4, key
        assert unit['illustratedKeyPoseApproved'] is False
    assert report['engineVerified'] is False
    assert report['overallAuthoredAnimationFrames']==sum(x['authoredActionFrames'] for x in report['creatures'])
    for item in report['creatures']:
        assert item['uniqueFrameHashes']>=20, item['id']
        assert item['frames']>=75, item['id']
    with Image.open(path/'KEYPOSE_APPROVAL_SHEET.png') as im:
        assert im.size==(880,810)
    with Image.open(path/'SPRITE_ACTION_PREVIEW.png') as im:
        assert im.size==(1120,1805)
    archive=path/'umbral-dominion-dev-DRAFT.zip'
    with zipfile.ZipFile(archive) as z:
        names=set(z.namelist())
        prefix='Mods/umbralDominion/Content/sprites/'
        assert prefix+'UD_VOID_ARROW.json' in names
        arrows=json.loads(z.read(prefix+'UD_VOID_ARROW.json'))
        assert len(arrows['sequences'][0]['frames'])==5
        for fn in arrows['sequences'][0]['frames']:
            assert prefix+fn in names
        for name in NAMES:
            key='UD_'+name.upper()
            animation=prefix+key+'.json'
            assert animation in names, animation
            data=json.loads(z.read(animation))
            by_group={s['group']:s['frames'] for s in data['sequences']}
            expected=set(BASE_GROUPS)
            if name in {'veilArcher','nightstalker'}: expected.update([14,15,16])
            if name in {'hexbinder','soulWeaver'}:expected.update([30,31,32])
            if name in {'umbralDragon','eclipseDragon'}:expected.update([40,41,42])
            assert expected <= set(by_group), (name,sorted(expected-set(by_group)))
            distinct=set()
            for group,files in by_group.items():
                assert len(files)>0,(name,group)
                for filename in files:
                    file=prefix+filename
                    assert file in names,file
                    distinct.add(hashlib.sha256(z.read(file)).hexdigest())
            assert len(distinct)>=20,(name,len(distinct))
            sheet=prefix+key+'_SHEET.png'
            assert sheet in names, sheet
            with z.open(sheet) as f:
                with Image.open(f) as im:
                    assert im.size==(1080,960),(name,im.size)
        for structure in ('VILLAGEHALL','FORT','CITADEL','MAGEGUILD1','MARKETPLACE','TAVERN','BLACKSMITH','OBSIDIANRELIQUARY'):
            for i in (0,1):
                p=prefix+f'UD_TOWN_{structure}_FRAME{i}.png'
                assert p in names,p
        assert 'Mods/umbralDominion/Content/Music/UD_EBON_SPIRE.ogg' in names
    print('PASS: 14 structured sprite sheets, 14 VCMI JSON animation descriptors, 8 illustrated structures')
    print('PASS: required action groups, non-identical frames, alpha spritesheet format, archive assets')
    print('PASS: 16 distinct illustrated key poses assigned to 4 units; source hash/animation traceability')
    print('NOT PASSED: full authored animation, art approval, VCMI gameplay (not tested)')

if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('build',type=Path)
    args=cli.parse_args()
    check(args.build)