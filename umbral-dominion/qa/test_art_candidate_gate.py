#!/usr/bin/env python3
"""No-provider test: reject posters/duplicate keyframes, accept reviewable pose layouts."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
from PIL import Image, ImageDraw

script=Path(__file__).resolve().parent/'generate_art_candidates.py'
if not script.is_file():
    script=Path(__file__).resolve().parent.parent/'scripts'/'generate_art_candidates.py'
spec=importlib.util.spec_from_file_location('generate_art_candidates',script)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
W,H=module.WIDTH,module.HEIGHT

def make(path,mode):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    draw=ImageDraw.Draw(img)
    for row in range(2):
        for col in range(4):
            x=col*W//4+95;y=row*H//2+80
            color=(130+20*col,70+40*row,240,255)
            if mode=='recolored':
                draw.ellipse((x,y,x+170,y+250),fill=color)
            elif col==0:
                draw.ellipse((x,y,x+180,y+250),fill=color)
            elif col==1:
                draw.polygon([(x,y+20),(x+190,y),(x+200,y+260),(x+80,y+200)],fill=color)
            elif col==2:
                draw.rectangle((x+40,y,x+115,y+280),fill=color)
                draw.polygon([(x-50,y+145),(x+210,y+160),(x+130,y+260)],fill=color)
            else:
                draw.polygon([(x,y+250),(x+90,y),(x+200,y+250)],fill=color)
    img.save(path)

with TemporaryDirectory() as temp:
    d=Path(temp)
    for mode in ('distinct','recolored'):
        source=d/(mode+'.png');make(source,mode)
        report=module.inspect_candidate(source,d/mode,'ashling-cinderimp')
        if mode=='distinct':
            assert report['eligibleForHumanReview'],report
        else:
            assert not report['eligibleForHumanReview'],report
            assert report['genuineTransparency'] and not report['fourDistinctPosesEach']
    opaque=d/'opaque.png';Image.new('RGB',(W,H),(60,25,90)).save(opaque)
    report=module.inspect_candidate(opaque,d/'opaque','ashling-cinderimp')
    assert not report['eligibleForHumanReview']
    assert not report['genuineTransparency']
print('PASS: original transparent silhouettes pass review intake; recolored duplicates and opaque poster are rejected')
print('NOT TESTED: artistic coherence, completed animation or VCMI runtime')