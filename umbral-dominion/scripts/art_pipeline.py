#!/usr/bin/env python3
"""Original deterministic Ebonspire prototype art; no third-party game artwork.

Each generated frame is a genuine PNG. VCMI animations use JSON sequences
rather than pretending a JSON file is a binary Heroes III DEF container.
These geometric/pixel silhouettes are placeholders, NOT release-quality art.
"""
from pathlib import Path
import hashlib
import json
import math
import random
import struct
import wave
import subprocess
from PIL import Image, ImageDraw, ImageFont

PALETTE=[(123,70,190),(208,88,143),(89,179,200),(203,140,79),
         (135,193,120),(222,102,79),(160,139,235)]
def seed(name):
    return int.from_bytes(hashlib.sha256(name.encode()).digest()[:8],"big")
def canvas(name, frame=0):
    upper=name.upper()
    if "TOWN_BACKGROUND" in upper: return (800,374)
    if "HALL_BACKGROUND" in upper: return (800,374)
    if "GUILD_BACKGROUND" in upper: return (640,450)
    if "GUILD_WINDOW" in upper: return (260,200)
    if "SIEGE_TOWER" in upper: return (96,96)
    if "UDPUZ" in upper: return (96,96)
    if "_MAP_" in upper: return (110,90)
    if "_TOWN_" in upper: return (155,112)
    if "HALL_ICONS" in upper: return (72,72)
    if "_LARGE" in upper: return (128,128)
    if "_SMALL" in upper: return (58,58)
    if "_AREA_" in upper or "_BORDER_" in upper: return (155,112)
    if "HERO" in upper: return (120,120)
    if upper.endswith(".DEF") or "_0.PNG" in upper: return (120,110)
    return (112,112)

def draw_scene(im, name, frame=0):
    w,h=im.size
    rng=random.Random(seed(name))
    d=ImageDraw.Draw(im,"RGBA")
    upper=name.upper()
    if "AREA_" in upper:
        d.ellipse((w*.11,h*.12,w*.91,h*.85),fill=(130,75,218,65))
        d.ellipse((w*.19,h*.19,w*.81,h*.75),fill=(177,105,243,45))
        return
    if "BORDER_" in upper:
        d.rounded_rectangle((6,6,w-6,h-6),8,outline=(198,134,250,220),width=4)
        d.line((14,h-20,w//2,h-4,w-14,h-20),fill=(235,154,244,200),width=2)
        return
    is_back="BACKGROUND" in upper
    if is_back:
        for y in range(h):
            t=y/max(1,h-1)
            d.line((0,y,w,y),fill=(int(12+20*t),int(8+9*t),int(33+16*t),255))
        moon_x=int(w*.75);moon_y=int(h*.23);moon_r=int(min(w,h)*.14)
        d.ellipse((moon_x-moon_r,moon_y-moon_r,moon_x+moon_r,moon_y+moon_r),
                  fill=(175,142,230,210),outline=(229,205,255,245),width=3)
        for i in range(48):
            x=rng.randrange(w);y=rng.randrange(max(1,int(h*.65)))
            rad=1+(i%3==0)
            d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=(215,194,253,155))
    else:
        d.rounded_rectangle((1,1,w-2,h-2),radius=10,
                            fill=(20,17,42,255),outline=(129,80,167,240),width=2)
    if "UDPUZ" in upper:
        d.polygon([(10,h-13),(w//2,9),(w-11,h-13)],fill=(72,46,100,240),
                  outline=(198,140,246,255))
        for i in range(5):
            x=12+i*(w-24)//5
            d.line((x,h-15,x+12,h-40),fill=(235,172,245,170),width=2)
        return
    if "HERO" in upper or "DREADLORD" in upper or "VOIDCALLER" in upper:
        accent=PALETTE[seed(name)%len(PALETTE)]
        d.polygon([(w*.15,h*.95),(w*.26,h*.50),(w*.42,h*.32),(w*.56,h*.34),
                   (w*.77,h*.52),(w*.87,h*.95)],fill=(*accent,220),outline=(11,5,19,255))
        d.ellipse((w*.38,h*.27,w*.65,h*.57),fill=(47,27,62,255),outline=(*accent,255),width=2)
        d.polygon([(w*.30,h*.47),(w*.45,h*.13),(w*.58,h*.16),(w*.72,h*.50)],
                  fill=(29,20,47,230),outline=(*accent,210))
        d.line((w*.43,h*.44,w*.48,h*.44),fill=(240,174,243,255),width=3)
        d.line((w*.55,h*.44,w*.60,h*.44),fill=(240,174,243,255),width=3)
        return
    if "UD_" in upper and ("MAP_" in upper or "TOWN_" in upper or "DWELLING" in upper
       or "GUILD" in upper or "HALL" in upper or "FORT" in upper):
        accent=PALETTE[seed(name)%len(PALETTE)]
        y0=int(h*.72)
        d.polygon([(w*.12,y0),(w*.5,h*.27),(w*.88,y0)],fill=(48,32,70,255),
                  outline=(*accent,230))
        d.rectangle((w*.23,h*.48,w*.77,h*.91),fill=(42,29,62,255),outline=(*accent,235),width=3)
        for off in (-.22,0,.22):
            x=int(w*(.5+off))
            d.rectangle((x-8,h*.30,x+8,h*.69),fill=(69,42,89,255),outline=(*accent,245))
            d.polygon([(x-13,h*.3),(x,h*.10),(x+13,h*.3)],fill=(*accent,230))
            d.rectangle((x-2,h*.41,x+2,h*.54),fill=(242,149,239,255))
        d.arc((w*.40,h*.67,w*.60,h*1.03),180,360,fill=(190,110,245,255),width=3)
        return
    # Distinct tier-gated original creature silhouettes, no copied H3 sprites
    accent=PALETTE[seed(name)%len(PALETTE)]
    d.ellipse((w*.16,h*.78,w*.90,h*.90),fill=(0,0,0,110))
    sway=math.sin(frame*1.57)*3
    cx=w*.5+sway
    d.polygon([(cx-30,h*.72),(cx-21,h*.34),(cx,h*.18),(cx+20,h*.35),(cx+31,h*.71)],
              fill=(44,34,67,255),outline=(*accent,255))
    d.ellipse((cx-17,h*.26,cx+17,h*.51),fill=(75,45,95,255),outline=(*accent,250),width=3)
    d.polygon([(cx-19,h*.27),(cx-27,h*.07),(cx-3,h*.25)],fill=(35,20,55,255),outline=(*accent,230))
    d.polygon([(cx+2,h*.25),(cx+27,h*.06),(cx+19,h*.27)],fill=(35,20,55,255),outline=(*accent,230))
    d.line((cx-11,h*.39,cx-5,h*.39),fill=(245,178,249,255),width=3)
    d.line((cx+5,h*.39,cx+11,h*.39),fill=(245,178,249,255),width=3)
    d.polygon([(cx-24,h*.48),(cx-40,h*.42),(cx-38,h*.60),(cx-25,h*.67)],
              fill=(*accent,175))
    d.polygon([(cx+24,h*.48),(cx+40,h*.42),(cx+38,h*.60),(cx+25,h*.67)],
              fill=(*accent,175))
    if "DRAGON" in upper or "REAVER" in upper:
        d.polygon([(cx-22,h*.46),(w*.04,h*.18),(w*.18,h*.68)],fill=(*accent,150))
        d.polygon([(cx+22,h*.46),(w*.96,h*.18),(w*.84,h*.68)],fill=(*accent,150))
    d.line((cx+27,h*.58,cx+40,h*.19),fill=(193,165,223,255),width=4)
    d.ellipse((cx+36,h*.16,cx+43,h*.23),fill=(230,110,240,255))

def save_png(path,name,frame=0):
    im=Image.new("RGBA",canvas(name))
    draw_scene(im,name,frame)
    path.parent.mkdir(parents=True,exist_ok=True)
    im.save(path,optimize=True)

def generate_assets(required, dest):
    dest=Path(dest)
    dest.mkdir(parents=True,exist_ok=True)
    emitted=set()
    catalog=[]
    for filename in sorted(set(required)):
        if filename.lower().endswith(".def"):
            base=Path(filename).stem
            descriptor=base+".json"
            creature=not any(x in base for x in ("UD_TOWN_","UD_MAP_","UD_HALL_","UD_DREADLORD_","UD_VOIDCALLER_"))
            frames=[]
            for frame in range(3 if creature else 2):
                name=f"{base}_FRAME{frame}.png"
                save_png(dest/name,filename,frame)
                emitted.add(name)
                frames.append(name)
            if creature:
                # H3/VCMI group IDs: movement, idle, hit, death, turning, attacks, etc.
                groups=list(range(0,25))
                sequences=[{"group":g,"frames":frames if g not in (22,23) else [frames[-1]],
                            "generateShadow":1} for g in groups]
            else:
                sequences=[{"group":0,"frames":frames}]
            (dest/descriptor).write_text(json.dumps({"sequences":sequences},indent=2)+"\n",
                                         encoding="utf-8")
            emitted.add(descriptor)
            catalog.append({"requested":filename,"generated":descriptor,"kind":"VCMI_JSON_animation"})
        elif filename.lower().endswith(".png"):
            save_png(dest/filename,filename)
            emitted.add(filename)
            catalog.append({"requested":filename,"generated":filename,"kind":"prototype_PNG"})
        else:
            raise ValueError(f"Unknown required art format: {filename}")
    (dest/"ASSET_CATALOG.json").write_text(json.dumps(catalog,indent=2)+"\n",encoding="utf-8")
    emitted.add("ASSET_CATALOG.json")
    return {"generated":len(emitted),"covered":len(catalog)}

def generate_music(mod):
    """A self-composed minimal dark-ambient theme, encoded as OGG via ffmpeg."""
    mod=Path(mod)
    folder=mod/"Content"/"Music"
    folder.mkdir(parents=True,exist_ok=True)
    wav=folder/"UD_EBON_SPIRE.wav"
    rate=22050
    duration=9
    chords=(110.0,130.8128,164.8138)
    with wave.open(str(wav),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
        samples=bytearray()
        for i in range(rate*duration):
            t=i/rate
            fade=min(1,t/1.5,(duration-t)/1.5)
            fade=max(0,fade)
            tone=sum(math.sin(2*math.pi*f*t)*0.23 for f in chords)
            sub=math.sin(2*math.pi*55*t)*0.24
            swell=0.7+0.3*math.sin(2*math.pi*t/6)
            sample=int(max(-1,min(1,(tone+sub)*fade*swell))*14000)
            samples.extend(struct.pack("<h",sample))
        w.writeframes(bytes(samples))
    ogg=folder/"UD_EBON_SPIRE.ogg"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",
                    str(wav),"-c:a","libvorbis","-q:a","3",str(ogg)],check=True)
    wav.unlink()
    return ogg
