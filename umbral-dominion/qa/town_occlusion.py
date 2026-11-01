#!/usr/bin/env python3
"""Town pixel-overlap triage. This is an ART REVIEW, not an engine renderer test.

Separates mutually-upgraded structures, physically related additions, and
independent building footprints. Computes real source-PNG alpha intersections
instead of assuming every 155x112 rectangle is opaque.
"""
import json
import re
import sys
from pathlib import Path
from PIL import Image, ImageChops

TILE=(155,112)
AREA=TILE[0]*TILE[1]
THRESHOLD=.40

def family(k):
    if k in ('villageHall','townHall','cityHall','capitol'):return 'hall'
    if k in ('fort','citadel','castle'):return 'fort'
    if k.startswith('mageGuild'):return 'mageGuild'
    m=re.fullmatch(r'dwelling(?:Up)?Lvl([1-7])',k)
    if m:return 'dwelling'+m.group(1)
    m=re.fullmatch(r'horde([1-2])(?:Upgr)?',k)
    if m:return 'horde'+m.group(1)
    return k

def related(a,b):
    pair={a,b}
    if pair=={'marketplace','resourceSilo'}:return True
    for horde,tier in (('horde1','1'),('horde2','3')):
        if any(x.startswith(horde) for x in pair):
            if any(re.fullmatch(r'dwelling(?:Up)?Lvl'+tier,x) for x in pair):
                return True
    return False

def analyze(build):
    build=Path(build)
    report=json.loads((build/'town-art-report.json').read_text(encoding='utf-8'))
    atlas=build/'generated-assets'
    structs=report['structures']
    assert len(structs)==36
    masks={}
    visible={}
    for item in structs:
        key=item['generatedKey']+'_FRAME0.png'
        with Image.open(atlas/key) as img:
            if img.size!=TILE:raise AssertionError((key,img.size))
            mask=img.convert('RGBA').getchannel('A').point(lambda p:255 if p>=80 else 0)
            masks[item['building']]=mask
            visible[item['building']]=mask.histogram()[255]
    overlaps=[]
    for i,a in enumerate(structs):
        for b in structs[i+1:]:
            x1=max(a['x'],b['x']);y1=max(a['y'],b['y'])
            x2=min(a['x']+TILE[0],b['x']+TILE[0])
            y2=min(a['y']+TILE[1],b['y']+TILE[1])
            if x1>=x2 or y1>=y2:continue
            rect_fraction=((x2-x1)*(y2-y1))/AREA
            if rect_fraction<THRESHOLD:continue
            names=(a['building'],b['building'])
            if family(names[0])==family(names[1]):
                kind='UPGRADE_CHAIN'
            elif related(*names):
                kind='RELATED_ATTACHMENT'
            else:
                kind='INDEPENDENT_REVIEW'
            aa=masks[names[0]].crop((x1-a['x'],y1-a['y'],x2-a['x'],y2-a['y']))
            bb=masks[names[1]].crop((x1-b['x'],y1-b['y'],x2-b['x'],y2-b['y']))
            intersection=ImageChops.multiply(aa,bb).histogram()[255]
            alpha_fraction=intersection/max(1,min(visible[names[0]],visible[names[1]]))
            overlaps.append({'first':names[0],'second':names[1],
               'classification':kind,'aabbOverlapPercent':round(rect_fraction*100,1),
               'visibleAlphaOverlapPixels':intersection,
               'smallerSpriteVisibleAlphaOverlapPercent':round(alpha_fraction*100,1),
               'runtimeVisibilityAndZOrderTested':False})
    counts={k:sum(x['classification']==k for x in overlaps)
           for k in ('UPGRADE_CHAIN','RELATED_ATTACHMENT','INDEPENDENT_REVIEW')}
    # A changed overlap count is intentionally visible, not silently called PASS.
    output={'status':'PREVIEW_ONLY_NEEDS_TOWN_GAMEPLAY_QA',
        'townStructures':len(structs),'sourceIndependentPaintings':report['sourcePaintings'],
        'rectangleOverlapThresholdPercent':40,'allAabbIntersections':len(overlaps),
        'classifications':counts,
        'independentAlphaVisibleOverlaps':sum(x['visibleAlphaOverlapPixels']>0
            for x in overlaps if x['classification']=='INDEPENDENT_REVIEW'),
        'independentReviewPriority':sorted(
            (x for x in overlaps if x['classification']=='INDEPENDENT_REVIEW'),
            key=lambda x:(-x['visibleAlphaOverlapPixels'],-x['aabbOverlapPercent'])),
        'allPairs':overlaps,
        'inGameLayeringChecked':False,'townClickMasksChecked':False,
        'warnings':['AABB overlap is not an in-game error by itself',
            'Alpha overlap does not consider gameplay visibility, selected town upgrades or z-order',
            'Same-chain upgrade and related building footprints may intentionally overlap']}
    (build/'TOWN_OCCLUSION_AUDIT.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    lines=['# Ebonspire town overlap triage (static pixels only)','',
        'Automated source-PNG alpha analysis; not a VCMI game screenshot or runtime PASS.','',
        '| Classification | Pair count |',
        '|---|---:|']
    lines += [f'| {name} | {n} |' for name,n in counts.items()]
    lines += ['','## Unrelated structures requiring human visual review','',
        '| Building A | Building B | Rect overlap | Visible alpha pixels |',
        '|---|---|---:|---:|']
    for p in output['independentReviewPriority']:
        lines.append(f"| {p['first']} | {p['second']} | {p['aabbOverlapPercent']}% | {p['visibleAlphaOverlapPixels']} |")
    lines+=['','**No automatic relocation is performed.** Approve or correct using actual VCMI town view and click-region screenshots.']
    (build/'TOWN_OCCLUSION_REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    # Regression bound: if new independent overlaps are introduced, fail CI.
    if counts['INDEPENDENT_REVIEW']>19:
        raise AssertionError(f"New independent layout overlaps: {counts['INDEPENDENT_REVIEW']} > baseline 19")
    if report['placementClippingCount']!=0:
        raise AssertionError('Out-of-canvas town overlays detected')
    print('PASS town audit: %s candidate AABB intersections, %s upgrade, %s related, %s independent review.'%(
        len(overlaps),counts['UPGRADE_CHAIN'],counts['RELATED_ATTACHMENT'],counts['INDEPENDENT_REVIEW']))
    print('INFO pixel-positive independent pair overlaps: '+str(output['independentAlphaVisibleOverlaps']))
    print('GAME RUNTIME NOT TESTED: layering, overlaps, masked hit regions.')
    return output

if __name__=='__main__':
    analyze(sys.argv[1] if len(sys.argv)>1 else 'umbral-dominion/build')
