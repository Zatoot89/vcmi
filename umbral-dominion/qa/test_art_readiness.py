#!/usr/bin/env python3
"""Strict provenance audit: green CI means prototype coverage, not release art."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile
from PIL import Image

CREATURES = ['ashling','cinderImp','gloomHound','dreadHound','veilArcher',
 'nightstalker','graveSentinel','doomSentinel','hexbinder','soulWeaver',
 'duskReaver','abyssalReaver','umbralDragon','eclipseDragon']


def check(path):
    folder=Path(path)
    pose=json.loads((folder/'sprite-pose-report.json').read_text(encoding='utf-8'))
    town=json.loads((folder/'town-art-report.json').read_text(encoding='utf-8'))
    validation=json.loads((folder/'validation.json').read_text(encoding='utf-8'))
    assert pose['creatureCount']==14
    assert pose['illustratedKeyPoseCreatureCount']==4
    assert pose['illustratedKeyPoseCount']==16
    assert pose['derivedPoseCreatureCount']==10
    assert pose['derivedPoseCount']==40
    assert pose['overallAuthoredAnimationFrames']==0
    assert not pose['releaseApproved']
    assert town['townStructures']==36
    assert town['sourcePaintings']==8
    assert town['reusedIllustrationDerivatives']==36
    assert town['illustratedIndependently']==0
    assert not town['vcmiTownRuntimeVerified']
    assert town['placementClippingCount']==0, 'town overlay exceeds 800x374 preview canvas'
    assert town['correctedOutOfCanvasCount']==15
    assert town['coordinateCorrectionsFile']=='design/town-layout-corrections.json'
    assert town['overlapReviewCount']>=0
    assert validation['artReadiness']['status']=='BLOCKED'
    assert validation['artReadiness']['genuineKeyPoseSourceUnits']==4
    assert validation['artReadiness']['derivedFromSingleStillUnits']==10
    assert validation['artReadiness']['fullIndependentlyIllustratedBuildings']==0
    assert validation['windowsQA']=='NOT_TESTED' # isolated zip install is not gameplay
    units={v['id']:v for v in pose['creatures']}
    assert set(units)==set(CREATURES)
    assert sum(u['derivedKeyPoseCount'] for u in units.values())==40
    for name in CREATURES:
        unit=units[name]
        if name in {'gloomHound','dreadHound','veilArcher','nightstalker'}:
            assert unit['illustratedKeyPoseCount']==4 and unit['derivedKeyPoseCount']==0
            assert unit['illustrationOrigin']=='AI_GENERATED_DISTINCT_KEYPOSE_ILLUSTRATIONS'
        else:
            assert unit['illustratedKeyPoseCount']==0 and unit['derivedKeyPoseCount']==4
            assert unit['illustrationOrigin']=='PROCEDURALLY_DERIVED_FROM_ONE_PAINTED_STILL'
    for name in ('DERIVED_POSE_REVIEW.png','KEYPOSE_APPROVAL_SHEET.png',
                 'TOWN_STRUCTURE_REVIEW.png','TOWN_LAYOUT_DIAGNOSTIC.png',
                 'TOWN_LAYOUT_BEFORE_AFTER.png'):
        p=folder/name
        with Image.open(p) as im:im.verify()
    with zipfile.ZipFile(folder/'umbral-dominion-dev-DRAFT.zip') as z:
        filelist=set(z.namelist())
        root='Mods/umbralDominion/Content/sprites/'
        for item in town['structures']:
            for frame in (0,1):
                filename=f"UD_TOWN_{item['building'].upper()}_FRAME{frame}.png"
                assert root+filename in filelist,filename
        assert all(root+('UD_'+n.upper()+'.json') in filelist for n in CREATURES)
    print('PASS prototype coverage: 14 creatures, 16 AI-illustrated source poses + 40 single-still-derived studies')
    print('PASS town asset audit: 36 illustrative derivatives from ONLY 8 independently painted building sources')
    print('PASS honesty gates: art/release blocked, placement and VCMI gameplay explicitly unverified')
    print('PASS town placement bounds: 15 corrected coordinates; 0 out-of-canvas objects in static preview')
    print(f'REVIEW town artistic occlusions: {town["overlapReviewCount"]} potential AABB overlaps; real-game checks pending')

if __name__=='__main__':
    check(sys.argv[1] if len(sys.argv)>1 else 'umbral-dominion/build')