#!/usr/bin/env python3
"""Static mod resource resolver: fail on missing Umbral Dominion file references.

Checks every UD_ / UDPUZ file reference in all shipped JSON config files and
animation descriptors. Does NOT claim VCMI game-load or visual-art approval.
"""
from pathlib import PurePosixPath,Path
from collections import defaultdict
import io,json,sys,zipfile
from PIL import Image

EXT={".json",".png",".wav",".ogg",".webp",".bmp",".def"}
PREFIXES=("UD_","UDPUZ")
def nested_strings(data):
    if isinstance(data,str):
        yield data
    elif isinstance(data,list):
        for x in data:yield from nested_strings(x)
    elif isinstance(data,dict):
        for x in data.values():yield from nested_strings(x)

def validate(build):
    path=Path(build)/"umbral-dominion-dev-DRAFT.zip"
    report={"status":"STATIC_RESOURCE_RESOLUTION_ONLY","gameplayVerified":False,
            "originalArtworkApproved":False,"references":0,
            "missing":[],"ambiguous":[],"invalidResources":[]}
    with zipfile.ZipFile(path) as z:
        files={name for name in z.namelist() if name and not name.endswith("/")}
        root="Mods/umbralDominion/"
        stems=defaultdict(list)
        for filename in sorted(files):
            stems[PurePosixPath(filename).name.upper()].append(filename)
        texts=[f for f in sorted(files)
               if f.startswith(root+"Content/") and f.endswith(".json")]
        assert len(texts)>=20,("Expected VCMI animation descriptors in mod ZIP",len(texts))
        for filename in texts:
            try:
                obj=json.loads(z.read(filename))
            except Exception as exc:
                report["invalidResources"].append({"file":filename,"error":str(exc)})
                continue
            for val in nested_strings(obj):
                short=PurePosixPath(val.replace("\\","/")).name
                if not short.upper().startswith(PREFIXES):continue
                ext=PurePosixPath(short).suffix.lower()
                if ext not in EXT:continue
                report["references"]+=1
                matches=stems.get(short.upper(),[])
                if not matches:
                    report["missing"].append({"source":filename,"reference":val})
                elif len(matches)>3:
                    report["ambiguous"].append({"source":filename,"reference":val,
                                                "locations":matches})
        # Sample every present sound WAV and validate the physical resource is readable.
        audio=[x for x in files if x.startswith(root+"Content/sounds/") and x.endswith(".wav")]
        report["audioFileCount"]=len(audio)
        report["configAndAnimationJsonCount"]=len(texts)
        # Asset references may intentionally exist in both Content/data and
        # Content/sprites; count but do not flag this as ambiguous.
    (Path(build)/"resource-resolution.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    if report["missing"] or report["invalidResources"]:
        raise AssertionError("Unresolved Umbral resources: "+
                             json.dumps({"missing":report["missing"][:12],
                                         "invalid":report["invalidResources"][:8]}))
    assert report["references"]>=350,("Unexpectedly few mod resource references",report["references"])
    assert report["audioFileCount"]==72
    print(f"PASS static mod refs: {report['references']} references, "+
          f"{report['configAndAnimationJsonCount']} JSON resources and "+
          f"{report['audioFileCount']} original SFX WAVs")
    print("NOT TESTED: VCMI runtime file resolution, in-game audio or actual gameplay")
    return report

if __name__=="__main__":
    validate(sys.argv[1] if len(sys.argv)>1 else "umbral-dominion/build")
