#!/usr/bin/env python3
"""Optional original-image candidate generation; NEVER auto-merge unapproved art.

Default mode is zero-cost and emits exactly the production brief. An explicit
--generate --authorize-charges and GEMINI_API_KEY are required for an API request.
Opaque backgrounds, missing sprite cells or repeated silhouettes FAIL QA. A
failed candidate is still retained for correction rather than faking alpha.
"""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
from PIL import Image, ImageOps

PAIR_NAMES = {
 'ashling-cinderimp':('Ashling','Cinder Imp','An ash-imp and larger horned cinder-imp with flame veins'),
 'grave-doom-sentinels':('Grave Sentinel','Doom Sentinel','Armored undead grave knight and its obsidian-plated larger guardian'),
 'hexbinder-soulweaver':('Hexbinder','Soul Weaver','Hooded curse mage and luminous soul-ribbon weaving archmage'),
 'dusk-abyssal-reavers':('Dusk Reaver','Abyssal Reaver','Dual-blade shadow warrior and its armored abyssal champion'),
 'umbral-eclipse-dragons':('Umbral Dragon','Eclipse Dragon','Black-violet dragon and upgraded eclipse-crowned plated dragon')
}
WIDTH, HEIGHT = 1774, 887
COLUMNS, ROWS = 4, 2
MODEL_DEFAULT = 'gemini-3.1-flash-image'


def brief(pair):
    name1, name2, identity = PAIR_NAMES[pair]
    prompt = (
      'Create only a transparent-background original fantasy game sprite-source atlas. '
      'Do not create a poster, marketing banner, labels, diagram, table borders, heading or UI. '
      'Exactly EIGHT distinct full-body illustrations on a single rectangular 2-row x 4-column canvas. '
      f'Top row is {name1}. Bottom row is {name2}. {identity}. '
      'Each row, left-to-right: 1 idle alert pose; 2 advancing or flying movement pose with clearly '
      'changed arms/legs/wings; 3 forceful attack or distinct spell-casting pose; 4 recoiling from damage. '
      'All eight illustrations have the same right-facing 3/4 battlefield perspective; keep original '
      'character anatomy, scale and gear consistent within each row. Render every limb, wing and weapon '
      'entirely inside its own cell. Four truly different silhouettes, not recolored or resized stills. '
      'Empty cell backgrounds should be genuine transparent alpha, not checkerboard, white, black or scenery. '
      'Dark gothic violet and charcoal fantasy concept art, readable bold game silhouettes. '
      'Use ORIGINAL imagery, do not imitate existing Heroes III creature assets.'
    )
    return {'atlas': pair+'.webp', 'pair': pair, 'creatures':[name1,name2],
            'poseColumns':['idle','move','attack','hit'],
            'requiredDimensions':[WIDTH,HEIGHT], 'requiredRows':2, 'requiredColumns':4,
            'artistReviewRequired':True, 'prompt':prompt,
            'releasesOrOverwritesProductionAssets':False}


def normalized_silhouette(cell):
    a=cell.getchannel('A')
    bbox=a.getbbox()
    if not bbox:return set()
    region=a.crop(bbox)
    region=ImageOps.contain(region,(64,64),Image.Resampling.LANCZOS)
    screen=Image.new('L',(64,64))
    screen.paste(region,((64-region.width)//2,(64-region.height)//2))
    return {i for i,v in enumerate(screen.tobytes()) if v>=100}


def inspect_candidate(path, output, pair):
    """Conservative appearance gate, not an AI art-approval certificate."""
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    with Image.open(path) as candidate:
        original_mode=candidate.mode
        im=candidate.convert('RGBA')
    # Keep the original image, never delete, and never hallucinate alpha.
    original_shape=im.size
    a=im.getchannel('A')
    rgba_alpha=a.getextrema()
    alpha_ok=(rgba_alpha[0]==0 and rgba_alpha[1]==255)
    report={'pair':pair,'originalSize':original_shape,'originalMode':original_mode,
       'genuineTransparency':alpha_ok,'requiredDimensions':[WIDTH,HEIGHT],
       'sourceHash':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
       'sourcePoseApproved':False,'artistApproved':False,'gameplayValidated':False,
       'warnings':[],'cells':[]}
    if not alpha_ok:
        report['warnings'].append('Source is opaque or lacks genuine zero-alpha pixels. No fake black-to-transparent conversion permitted.')
    # Fit into target shape WITHOUT cutting off the character silhouettes.
    padded=Image.new('RGBA',(WIDTH,HEIGHT),(0,0,0,0))
    fit=ImageOps.contain(im,(WIDTH,HEIGHT),Image.Resampling.LANCZOS)
    padded.alpha_composite(fit,((WIDTH-fit.width)//2,(HEIGHT-fit.height)//2))
    pixel_area=(WIDTH//COLUMNS)*(HEIGHT//ROWS)
    signatures=[]
    for row in range(ROWS):
        for col in range(COLUMNS):
            bounds=(col*WIDTH//COLUMNS,row*HEIGHT//ROWS,
                  (col+1)*WIDTH//COLUMNS,(row+1)*HEIGHT//ROWS)
            cell=padded.crop(bounds)
            alpha=cell.getchannel('A')
            occupied=sum(1 for x in alpha.tobytes() if x>=100)
            silhouette=normalized_silhouette(cell)
            signatures.append(silhouette)
            report['cells'].append({'row':row,'col':col,'visibleAlphaPixels':occupied,
                'nonEmpty':occupied>=pixel_area*.025})
    report['eightNonemptyCells']=all(c['nonEmpty'] for c in report['cells'])
    if not report['eightNonemptyCells']:
        report['warnings'].append('One or more pose cells are empty or contain too few visible pixels.')
    report['rowPoseSilhouetteDifferences']=[]
    for row in range(ROWS):
        for i in range(COLUMNS):
            for j in range(i+1,COLUMNS):
                x,y=signatures[row*4+i],signatures[row*4+j]
                difference=1-len(x&y)/max(1,len(x|y))
                report['rowPoseSilhouetteDifferences'].append({'row':row,'first':i,'second':j,
                     'differenceRatio':round(difference,4)})
    report['fourDistinctPosesEach']=all(x['differenceRatio']>=.08 for x in report['rowPoseSilhouetteDifferences'])
    if not report['fourDistinctPosesEach']:
        report['warnings'].append('One or more pose silhouettes are too similar to count as distinct. Repainting required.')
    report['eligibleForHumanReview']=alpha_ok and report['eightNonemptyCells'] and report['fourDistinctPosesEach']
    # Eligibility is NOT automatic approval or any mod installation.
    if report['eligibleForHumanReview']:
        padded.save(output/(pair+'-review-only.png'),optimize=True)
    (output/'candidate_qa.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    return report


def generate_image(prompt, model, api_key):
    # Google Gemini generateContent; official API endpoint, no key in URLs/logs.
    url=f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    payload=json.dumps({'contents':[{'role':'user','parts':[{'text':prompt}]}],
        'generationConfig':{'responseModalities':['IMAGE']}}).encode()
    request=urllib.request.Request(url,data=payload,method='POST',headers={
        'x-goog-api-key':api_key,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=180) as r:
            response=json.load(r)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'Image provider HTTP error {exc.code}; see provider billing and model access') from None
    for result in response.get('candidates',[]):
        for part in result.get('content',{}).get('parts',[]):
            item=part.get('inlineData') or part.get('inline_data')
            if item and item.get('data'):
                return base64.b64decode(item['data'])
    raise RuntimeError('Provider returned no image. Preserve brief; no blank or fake sprite generated.')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pair',required=True,choices=sorted(PAIR_NAMES))
    p.add_argument('--output',default='umbral-dominion/build/art-candidate')
    p.add_argument('--generate',action='store_true',help='Actual paid provider request; requires authorization')
    p.add_argument('--authorize-charges',action='store_true',help='Explicitly permit one image generation request')
    p.add_argument('--model',default=MODEL_DEFAULT)
    p.add_argument('--inspect-existing',default=None,help='Inspect image without API usage')
    args=p.parse_args()
    dest=Path(args.output);dest.mkdir(parents=True,exist_ok=True)
    detail=brief(args.pair)
    (dest/'source_brief.json').write_text(json.dumps(detail,indent=2)+'\n',encoding='utf8')
    if args.inspect_existing:
        result=inspect_candidate(Path(args.inspect_existing),dest,args.pair)
        print('REVIEW REQUIRED: '+json.dumps({k:v for k,v in result.items() if k in ('eligibleForHumanReview','warnings','sourcePoseApproved')}))
    elif args.generate:
        if not args.authorize_charges:raise SystemExit('Refusing paid API call: --authorize-charges missing')
        key=os.environ.get('GEMINI_API_KEY','')
        if not key:raise SystemExit('GEMINI_API_KEY unavailable; only zero-cost briefs produced')
        data=generate_image(detail['prompt'],args.model,key)
        candidate=dest/(args.pair+'-RAW-CANDIDATE.png')
        with Image.open(io.BytesIO(data)) as im:
            im.save(candidate)
        result=inspect_candidate(candidate,dest,args.pair)
        print('IMAGE CANDIDATE: '+str(candidate))
        print('ELIGIBLE FOR MANUAL ART REVIEW: '+str(result['eligibleForHumanReview']))
    else:
        print('DRY RUN: prepared no-cost artwork source brief; API request NOT made')

if __name__=='__main__':main()