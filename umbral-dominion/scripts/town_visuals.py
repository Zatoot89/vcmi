#!/usr/bin/env python3
"""Experimental Ebonspire town overlays and placement report.

Eight independent concept buildings support 36 *derivative* overlays via palette,
size and effect variations. THIS IS NOT 36 separately illustrated buildings, and
no overlay positions have been tested against a running VCMI game.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
from PIL import Image, ImageOps, ImageEnhance, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
ATLAS_PATH=ROOT/'assets-source'/'buildings-master.webp'
CELL=(256,288)
TILE=(155,112)
TOWN=(800,374)
BASES=(
    'cathedral_gate', 'arcane_keep','ebonspire_citadel','observatory_library',
    'market_hall','tavern_house','soul_forge','spectral_tower'
)

def archetype(name):
    if name in {'villageHall','townHall','cityHall','capitol'}:return 0
    if name in {'fort','citadel','castle'}:return 2 if name in {'citadel','castle'} else 1
    if name in {'tavern'}:return 5
    if name in {'blacksmith','resourceSilo'}:return 6
    if name in {'marketplace'}:return 4
    if name.startswith('mageGuild'):return 3
    if name in {'obsidianReliquary','wellOfShadows'}:return 7
    if name.startswith('horde'):return 7
    if name.startswith('dwelling'):
        try:level=int(name[-1])
        except ValueError:level=1
        return [0,1,6,2,3,7,2][level-1]
    return 0

def place(source,dimensions=TILE):
    im=source.convert('RGBA'); bbox=im.getchannel('A').getbbox()
    if not bbox:raise ValueError('Blank source town image')
    im=im.crop(bbox)
    reduced=ImageOps.contain(im,(dimensions[0]-8, dimensions[1]-7),Image.Resampling.LANCZOS)
    output=Image.new('RGBA', dimensions)
    output.alpha_composite(reduced,((dimensions[0]-reduced.width)//2,dimensions[1]-reduced.height-3))
    return output

def build_town_visuals(generated, build, town):
    generated=Path(generated);build=Path(build)
    if not ATLAS_PATH.is_file(): raise FileNotFoundError(ATLAS_PATH)
    with Image.open(ATLAS_PATH) as art:
        art=art.convert('RGBA')
        if art.size!=(1024,576):raise ValueError(f'Building atlas must be 1024x576, got {art.size}')
        originals=[art.crop((i%4*256,i//4*288,(i%4+1)*256,(i//4+1)*288)) for i in range(8)]
    structs=town['structures']
    audit=[]
    for name in sorted(structs):
        src_idx=archetype(name)
        arche=BASES[src_idx]
        dest='UD_TOWN_'+name.upper()
        variant=int(hashlib.sha256(name.encode()).hexdigest()[:6],16)
        base=place(originals[src_idx]);modified=base.copy()
        # A deterministic atmospheric tint and small accent distinguishes variants.
        # This remains a derivative of the same eight original paintings.
        color=(146+variant%48,90+variant%70,210+variant%38)
        d=ImageDraw.Draw(modified,'RGBA')
        seed=variant%5
        for x in (18+seed*11,65+seed*6,123-seed*6):
            d.polygon(((x,33),(x+2,29),(x+4,33),(x+2,41)),fill=(*color,145))
        for frame in (0,1):
            pic=modified.copy()
            if frame:
                # Town animations must still be painted later; prototype glow only.
                pic=ImageEnhance.Brightness(pic).enhance(1.06)
            pic.save(generated/(dest+f'_FRAME{frame}.png'),optimize=True)
        # Only produce previews for clickable masks; do not override VCMI masks,
        # because mask semantics have not been verified on Windows.
        source=structs[name]
        x=int(source.get('x',0));y=int(source.get('y',0));z=int(source.get('z',0))
        clipped=max(0,-x)+max(0,-y)+max(0,x+TILE[0]-TOWN[0])+max(0,y+TILE[1]-TOWN[1])
        audit.append({'building':name,'template':arche,'illustratedIndependently':False,
                      'derivedFrom':arche,'frameCount':2,'generatedKey':dest,
                      'x':x,'y':y,'z':z,'outOfCanvasByPixels':clipped,
                      'animationApproved':False,'clickMaskTested':False})
    # Preview of all actual overlays (no in-game screenshot claims).
    columns=6;rows=(len(audit)+columns-1)//columns;thumb=(172,158)
    preview=Image.new('RGB',(columns*thumb[0],rows*thumb[1]+75),(24,17,37))
    d=ImageDraw.Draw(preview)
    d.text((12,12),'EBONSPIRE — 36 TOWN BUILDING DERIVATIVES (8 SOURCE PAINTINGS)',fill=(232,207,252))
    d.text((12,33),'NOT 36 independently illustrated buildings; town coordinates NOT gameplay-tested',fill=(207,166,235))
    for i,item in enumerate(audit):
        col=i%columns;row=i//columns;x=col*thumb[0];y=65+row*thumb[1]
        fname=item['generatedKey']+'_FRAME0.png'
        with Image.open(generated/fname) as pict:
            preview.paste(pict,(x+7,y+6),pict)
        d.text((x+4,y+123),item['building'][:22],fill=(225,199,244))
        if item['outOfCanvasByPixels']:
            d.text((x+4,y+140),'PLACEMENT CLIPS',fill=(247,138,132))
    preview.save(build/'TOWN_STRUCTURE_REVIEW.png',optimize=True)
    # Approximate composite is only a diagnostic; overlaps and hit regions not verified.
    backdrop=generated/'UD_TOWN_BACKGROUND.png'
    with Image.open(backdrop) as image:town_view=image.convert('RGBA')
    for item in sorted(audit,key=lambda t:(t['z'],t['building'])):
        with Image.open(generated/(item['generatedKey']+'_FRAME0.png')) as layer:
            town_view.paste(layer,(item['x'],item['y']),layer)
    town_view.save(build/'TOWN_LAYOUT_DIAGNOSTIC.png',optimize=True)
    stats={'townStructures':len(audit),'sourcePaintings':len(BASES),
           'illustratedIndependently':0,'reusedIllustrationDerivatives':len(audit),
           'placementClippingCount':sum(item['outOfCanvasByPixels']>0 for item in audit),
           'clickMasksRuntimeVerified':False,'vcmiTownRuntimeVerified':False,
           'structures':audit,'releaseApproved':False}
    (build/'town-art-report.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf-8')
    return stats