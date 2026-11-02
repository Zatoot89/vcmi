#!/usr/bin/env python3
"""Original deterministic creature sound-effects for VCMI development prototype.

No Heroes III files or samples. Sounds are algorithmically synthesized WAV files,
NOT human-directed final creature voice performances. Each creature/action gets
a distinct, reproducible 22050 Hz 16-bit PCM mono effect.
"""
from pathlib import Path
import math
import json
import hashlib
import random
import struct
import wave

EVENTS=("attack","defend","killed","move","wince")
RATE=22050
DUR={"attack":0.26,"defend":0.22,"killed":0.42,
     "move":0.18,"wince":0.19,"shoot":0.25}
def soundtrack_names(creatures):
    mapping={}
    for key,creature in sorted(creatures.items()):
        slots=list(EVENTS)
        if "missile" in creature.get("graphics",{}):
            slots.append("shoot")
        prefix="UD_"+key.upper()
        mapping[key]={event:f"{prefix}_{event.upper()}.wav" for event in slots}
    return mapping

def generate_creature_sfx(mod,creatures,output=None):
    """Generate all filenames included in each creature's exact sound mapping."""
    mod=Path(mod)
    destination=mod/"Content"/"sounds"
    destination.mkdir(parents=True,exist_ok=True)
    mapping=soundtrack_names(creatures)
    report=[]
    for key,slots in mapping.items():
        seed=int(hashlib.sha256(key.encode("utf8")).hexdigest()[:12],16)
        for event,filename in slots.items():
            rng=random.Random(seed ^ int(hashlib.sha256(event.encode()).hexdigest()[:12],16))
            n=int(DUR[event]*RATE)
            base=72+(seed%210)+(list(slots).index(event)*39)
            data=bytearray()
            for i in range(n):
                t=i/RATE
                v=i/max(1,n-1)
                attack=min(1.0,t/0.012)
                decay=max(0,(1-v)**(1.2 if event in ("move","defend") else 1.8))
                env=attack*decay
                vibrato=1+0.035*math.sin(2*math.pi*(7+(seed%5))*t)
                sweep=(1+0.7*(1-v)) if event in ("attack","shoot") else (0.75+0.55*(1-v))
                phase=2*math.pi*base*sweep*vibrato*t
                tone=0.48*math.sin(phase)+0.18*math.sin(phase*2.01)+0.09*math.sin(phase*3.13)
                noise=rng.uniform(-1.0,1.0)
                rasp=0.28*noise if event in ("attack","wince","killed") else 0.11*noise
                if event=="killed":tone*=max(0,1-v*1.4)
                sample=max(-1,min(1,env*(tone+rasp)*0.62))
                data.extend(struct.pack("<h",round(sample*32767)))
            target=destination/filename
            with wave.open(str(target),"wb") as out:
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(RATE)
                out.writeframes(bytes(data))
            digest=hashlib.sha256(target.read_bytes()).hexdigest()
            report.append({"creature":key,"event":event,"file":filename,
                           "durationSeconds":round(n/RATE,3),"sha256":digest,
                           "status":"SYNTHESIZED_PROTOTYPE_SOUND"})
    summary={"creatures":len(creatures),"soundEffects":len(report),
             "audioOrigin":"ORIGINAL_SYNTHESIZED_PROTOTYPE_NOT_PRODUCTION_MIX",
             "gameAudioPlaybackVerified":False,"files":report}
    if output is not None:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        (output/"creature-audio-report.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf8")
    return summary
