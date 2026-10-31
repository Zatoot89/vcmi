#!/usr/bin/env python3
"""Deterministic Ebonspire preview pose animation and sprite sheets.

These are PROCEDURALLY DISTORTED ILLUSTRATED STILL IMAGES, not frame-by-frame
illustrated combat art. The source asset must match the character. Release
remains blocked pending approved artwork, authored poses and Windows runtime QA.
"""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'assets-source'
CANVAS = (180,160)
CONTACT_GROUPS=(0,2,3,4,5,12)
ALL_CREATURES = ('ashling','cinderImp','gloomHound','dreadHound','veilArcher',
 'nightstalker','graveSentinel','doomSentinel','hexbinder','soulWeaver',
 'duskReaver','abyssalReaver','umbralDragon','eclipseDragon')
NEW_CREATURES=('gloomHound','dreadHound','veilArcher','nightstalker')
NEW_BUILDINGS={
 'cathedral_gate':'villageHall',
 'arcane_keep':'fort',
 'ebonspire_citadel':'citadel',
 'observatory_library':'mageGuild1',
 'market_hall':'marketplace',
 'tavern_house':'tavern',
 'soul_forge':'blacksmith',
 'spectral_tower':'obsidianReliquary',
}
ARCHER={'veilArcher','nightstalker'}
MAGE={'hexbinder','soulWeaver'}
DRAGON={'umbralDragon','eclipseDragon'}


def crop_alpha(image):
    im=image.convert('RGBA')
    bbox=im.getchannel('A').getbbox()
    if bbox is None:
        raise ValueError('Transparent-only input; source art missing')
    return im.crop(bbox)


def fit(im, box, margin=8):
    im=crop_alpha(im)
    target=tuple(x-2*margin for x in box)
    size=ImageOps.contain(im,target,Image.Resampling.LANCZOS)
    out=Image.new('RGBA',box)
    out.alpha_composite(size,((box[0]-size.width)//2,box[1]-margin-size.height))
    return out


def source_cell(atlas, index, cell):
    col=index%4
    row=index//4
    im=atlas.crop((col*cell[0],row*cell[1],(col+1)*cell[0],(row+1)*cell[1]))
    return crop_alpha(im)


def load_exact_masters():
    expected=[('creatures-master.webp',(1024,256)),('buildings-master.webp',(1024,576))]
    atlases={}
    for name,dims in expected:
        path=SRC/name
        if not path.is_file():
            raise FileNotFoundError('Missing source atlas: '+str(path))
        with Image.open(path) as src:
            if src.size!=dims:
                raise ValueError(f'{name}: expected {dims}, got {src.size}')
            if src.mode not in ('RGBA','P'):
                raise ValueError(f'{name}: expected alpha channel')
            atlases[name]=src.convert('RGBA')
    return atlases


def pose(base, key, action, index, n):
    """Make PREVIEW poses via canvas/shape transformations and new FX overlays.

    No skeletal rig or individually re-illustrated body parts are provided.
    This is intentionally marked generated, even though frames differ.
    """
    t=index/max(n-1,1)
    w,h=CANVAS
    bob=0;shift=0;lean=0;sx=1.;sy=1.;opacity=255
    if action=='move':
        shift=round(13*math.sin(t*2*math.pi)); bob=round(-4*abs(math.sin(t*2*math.pi)))
        lean=4*math.sin(t*2*math.pi)
        sx=1+0.035*math.cos(t*2*math.pi)
    elif action=='idle':
        bob=round(-3*math.sin(t*2*math.pi));lean=1.3*math.sin(t*2*math.pi)
        sx=1+0.015*math.cos(t*2*math.pi);sy=1-0.010*math.cos(t*2*math.pi)
    elif action=='hit':
        lean=-13*math.sin(math.pi*t);shift=-6*math.sin(math.pi*t)
        opacity=round(255-35*math.sin(math.pi*t))
    elif action=='defend':
        sy=1-0.18*math.sin(math.pi*t);sx=1+0.08*math.sin(math.pi*t)
        lean=-4*math.sin(math.pi*t)
    elif action=='death':
        lean=-66*t;sy=1-.47*t;sx=1+.24*t
        shift=-13*t;bob=round(11*t)
        opacity=round(255-90*max(0,(t-.60)/.40))
    elif action=='attack':
        phase=math.sin(math.pi*t)
        shift=round(23*phase);lean=-13*phase; sx=1+.14*phase;sy=1-.07*phase
        bob=round(-4*phase)
    elif action=='shoot':
        phase=math.sin(math.pi*t)
        lean=7*phase;shift=-7*phase;bob=round(-2*phase)
    elif action=='cast':
        phase=math.sin(math.pi*t)
        sy=1+.08*phase;lean=-5*phase;bob=round(-9*phase)
    elif action=='turn':
        sx=1-.42*math.sin(math.pi*t)
    elif action=='start':
        lean=4*t;shift=6*t
    elif action=='end':
        lean=4*(1-t);shift=6*(1-t)
    img=base.copy()
    if sx!=1 or sy!=1:
        new=(max(1,round(w*sx)),max(1,round(h*sy)))
        img=img.resize(new,Image.Resampling.BICUBIC)
        centered=Image.new('RGBA',CANVAS)
        centered.alpha_composite(img,((w-img.width)//2,(h-img.height))) if img.width<=w and img.height<=h else centered.paste(img,((w-img.width)//2,h-img.height),img)
        img=centered
    if lean:
        img=img.rotate(lean,Image.Resampling.BICUBIC,center=(w/2,h-16),expand=False)
    if opacity<255:
        a=img.getchannel('A').point(lambda v:int(v*opacity/255))
        img.putalpha(a)
    out=Image.new('RGBA',CANVAS)
    out.alpha_composite(img,(round(shift),round(bob))) if -w<shift<w and -h<bob<h else None
    draw=ImageDraw.Draw(out,'RGBA')
    # All FX are original strokes, not copyrighted game art.
    if action in ('attack','shoot','cast') and 0.1<t<0.91:
        bright=(207,85,255,int(110+135*math.sin(math.pi*t)))
        if action=='shoot':
            arrowx=int(100+62*t)
            arrowy=int(56-10*t)
            draw.line((90,75,arrowx,arrowy),fill=bright,width=4)
            draw.polygon([(arrowx+10,arrowy),(arrowx,arrowy-5),(arrowx,arrowy+5)],fill=bright)
        elif action=='attack':
            for k in range(3):
                x=round(117+14*t+k*8)
                draw.arc((x,42-k*6,x+30,100-k*6),start=25,end=155,fill=bright,width=3)
        else:
            rad=round(8+21*math.sin(math.pi*t))
            draw.ellipse((112-rad,47-rad,112+rad,47+rad),outline=bright,width=4)
    if action=='hit' and 0.15<t<0.8:
        draw.line((50,43,101,87),fill=(244,117,160,140),width=4)
    if action=='death' and index==n-1:
        draw.ellipse((36,136,148,146),fill=(61,28,93,120))
    return out


def groups_for(key):
    # Group IDs follow VCMI's published Animation Format list.
    groups={0:('move',6),1:('idle',4),2:('idle',5),3:('hit',4),4:('defend',4),
      5:('death',7),6:('death',7),7:('turn',4),8:('turn',4),
      11:('attack',6),12:('attack',6),13:('attack',6),
      17:('cast',6),18:('cast',6),19:('cast',6),20:('start',3),21:('end',3),
      22:('dead',1),23:('dead',1),24:('resurrection',7)}
    if key in ARCHER:
        groups.update({14:('shoot',6),15:('shoot',6),16:('shoot',6)})
    if key in MAGE:
        groups.update({30:('cast',6),31:('cast',6),32:('cast',6)})
    if key in DRAGON:
        groups.update({40:('cast',6),41:('cast',6),42:('cast',6)})
    return groups


def render_animation(source, key, dest, sheet_folder):
    prefix='UD_'+key.upper()
    role='archer' if key in ARCHER else ('mage' if key in MAGE else 'dragon' if key in DRAGON else 'melee')
    base=fit(source,CANVAS,margin=18)
    sequences=[];hashes={};cache={};action_names=[];authored_count=0;authored_groups=[]
    group_map=groups_for(key)
    for group,(action,count) in sorted(group_map.items()):
        authored_dir=SRC/'authored-poses'/key/f'group-{group:02d}'
        artwork_files=sorted(authored_dir.glob('*.png')) if authored_dir.is_dir() else []
        if authored_dir.is_dir():
            if len(artwork_files)<2:
                raise ValueError(f'{key} group {group}: authored source must contain 2+ frames')
            digests={hashlib.sha256(p.read_bytes()).hexdigest() for p in artwork_files}
            if len(digests)<2:
                raise ValueError(f'{key} group {group}: authored frames are identical')
            count=len(artwork_files)
            authored_count+=count; authored_groups.append(group)
        frames=[]
        for frame in range(count):
            index=count-1-frame if action=='resurrection' else frame
            actual='death' if action in ('dead','resurrection') else action
            tcount=7 if action in ('dead','resurrection') else count
            if action=='dead': index=6
            # Avoid writing duplicate bytes for different facing-group variants.
            png=f'{prefix}_G{group:02d}_{frame:02d}.png'
            output=dest/png
            if artwork_files:
                with Image.open(artwork_files[frame]) as authored:
                    im=fit(authored,CANVAS,margin=2)
            else:
                im=pose(base,key,actual,index,tcount)
            if not artwork_files and action in ('turn','shoot','attack','cast') and group in (11,14,17,30,40):
                im=ImageOps.mirror(im)
            pixel_hash=hashlib.sha256(im.tobytes()).hexdigest()
            if pixel_hash in cache:
                # Reuse existing PNG when two VCMI groups refer to precisely
                # the same animation frame. No false new art and smaller ZIP.
                png=cache[pixel_hash]
            else:
                im.save(output,optimize=True)
                cache[pixel_hash]=png
            frames.append(png)
            hashes[png]=pixel_hash
        sequences.append({'group':group,'frames':frames,'generateShadow':1})
        if action not in action_names:action_names.append(action)
    desc={'sequences':sequences}
    (dest/(prefix+'.json')).write_text(json.dumps(desc,indent=2)+'\n',encoding='utf-8')
    cols=6; rows=len(CONTACT_GROUPS)
    sheet=Image.new('RGBA',(cols*CANVAS[0],rows*CANVAS[1]))
    for row,group in enumerate(CONTACT_GROUPS):
        if group not in group_map:continue
        descriptor=next(x for x in sequences if x['group']==group)
        for col in range(cols):
            filename=descriptor['frames'][min(col,len(descriptor['frames'])-1)]
            with Image.open(dest/filename) as frame:
                sheet.alpha_composite(frame,(col*CANVAS[0],row*CANVAS[1]))
    sheet_file=sheet_folder/(prefix+'_SHEET.png')
    sheet.save(sheet_file,optimize=True)
    sheet.save(dest/sheet_file.name,optimize=True)
    return {'id':key,'role':role,'groups':len(sequences),'frames':sum(len(s['frames']) for s in sequences),
            'uniqueFrameHashes':len(set(hashes.values())),'sheet':sheet_file.name,
            'authoredActionFrames':authored_count,'authoredGroups':authored_groups,
            'poseMethod':'AUTHORED_SOURCE_OVERRIDE_PLUS_GENERATED_FALLBACK' if authored_count else 'PROCEDURAL_IMAGE_TRANSFORM_AND_EFFECTS',
            'source':'IMPROVED_ISOLATED_ART' if key in NEW_CREATURES else 'PAINTED_CONCEPT_ATLAS'}


def preview_sheet(sheets, output):
    # Useful human review. Individual full-resolution sprite sheets also generated.
    canvas=Image.new('RGB',(1120,14*125+55),(22,16,36))
    draw=ImageDraw.Draw(canvas)
    draw.text((20,12),'UMBRAL DOMINION — ACTION PREVIEW  /  MOTION GENERATED, NOT HAND-ANIMATED',fill=(235,207,253))
    draw.text((20,32),'Each unit also has a 6 x 6 action sheet and VCMI grouped animation JSON',fill=(198,155,220))
    for idx,(name,path) in enumerate(sheets):
        with Image.open(path) as im:
            im=im.convert('RGBA')
            # frame 0 for each action in CONTACT_GROUPS
            draw.text((12,65+idx*125),name,fill=(211,171,248))
            for col in range(6):
                frame=im.crop((min(3,(6-1))*CANVAS[0],col*CANVAS[1],(min(3,(6-1))+1)*CANVAS[0],(col+1)*CANVAS[1]))
                frame.thumbnail((125,108),Image.Resampling.LANCZOS)
                canvas.paste(frame,(180+col*150,57+idx*125),frame)
    canvas.save(output,optimize=True)


def generate_pose_sheets(generated_dir, build_dir):
    dest=Path(generated_dir); build=Path(build_dir)
    atlases=load_exact_masters()
    creature_atlas=atlases['creatures-master.webp']
    building_atlas=atlases['buildings-master.webp']
    built=[];sheets=[]
    for idx,key in enumerate(ALL_CREATURES):
        prefix='UD_'+key.upper()
        if key in NEW_CREATURES:
            source=source_cell(creature_atlas,NEW_CREATURES.index(key),(256,256))
            # These preview icons are based on extracted original art, not geometrical placeholders.
            for suffix,size in (('_LARGE.png',(128,128)),('_SMALL.png',(58,58))):
                fit(source,size,margin=4).save(dest/(prefix+suffix),optimize=True)
            # Keep the legacy prototype frame references consistent too.
            for k in range(3):
                fit(source,(120,110),margin=4).save(dest/(prefix+f'_FRAME{k}.png'),optimize=True)
        else:
            still=dest/(prefix+'_FRAME0.png')
            if not still.exists():raise FileNotFoundError('Expected concept still for '+key)
            with Image.open(still) as im:source=crop_alpha(im)
        result=render_animation(source,key,dest,build)
        built.append(result)
        sheets.append((key,build/result['sheet']))
    buildings=[]
    for i,(name,building_key) in enumerate(NEW_BUILDINGS.items()):
        image=source_cell(building_atlas,i,(256,288))
        prefix='UD_TOWN_'+building_key.upper()+'_FRAME'
        for j in range(2):
            pic=fit(image,(155,112),margin=4)
            if j:
                pic=ImageEnhance.Brightness(pic).enhance(1.1)
            pic.save(dest/(prefix+str(j)+'.png'),optimize=True)
        buildings.append({'source':name,'townStructure':building_key,
                          'animationFrames':2,'role':'ILLUSTRATED_CONCEPT_OVERLAY_NOT_LAYOUT_APPROVED'})
    preview_sheet(sheets,build/'SPRITE_ACTION_PREVIEW.png')
    # Animated gallery of four improved units. This is a preview of generated
    # motion, not evidence of genuine hand-animated battle sprites.
    gallery=[]
    for i in range(12):
        scene=Image.new('RGBA',(CANVAS[0]*4,CANVAS[1]),(20,13,35,255))
        for col,key in enumerate(NEW_CREATURES):
            prefix='UD_'+key.upper()
            group=0 if i<6 else 12
            frame=(i%6)
            desc=json.loads((dest/(prefix+'.json')).read_text())
            seq=next(x for x in desc['sequences'] if x['group']==group)
            with Image.open(dest/seq['frames'][frame]) as img:
                scene.alpha_composite(img.convert('RGBA'),(col*CANVAS[0],0))
        gallery.append(scene.convert('RGB'))
    gallery[0].save(build/'SPRITE_MOTION_PREVIEW.gif',save_all=True,
       append_images=gallery[1:],duration=130,loop=0,optimize=False)
    report={'mode':'DEVELOPMENT_POSE_PREVIEW', 'creatures':built,
            'creatureCount':len(built),'spriteSheetCount':len(built),
            'buildings':buildings,'paintedBuildingOverlays':len(buildings),
            'overallAuthoredAnimationFrames':sum(x['authoredActionFrames'] for x in built),
            'engineVerified':False,'windowsRuntimeTested':False,
            'releaseApproved':False,
            'caveats':['Fallback poses generated by geometric transforms/FX of stills; NOT frame-by-frame authored.',
                       'Animation groups technically present; actual in-game transitions unverified.',
                       '8 painted building image overlays provisional: town-screen alignment unverified.',
                       'The 10 other creatures need original action-specific keyframes.']}
    (build/'sprite-pose-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--generated',type=Path,required=True)
    p.add_argument('--build',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(generate_pose_sheets(args.generated,args.build),indent=2)[:900])