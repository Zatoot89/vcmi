#!/usr/bin/env python3
"""Create a reproducible queue of missing illustrated *source* poses.

This does not generate art, invoke a paid image API, or claim artistic approval.
Review the briefs, then add original 1774x887 transparent atlases to assets-source.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAIR_SPECS=[
('ashling-cinderimp.webp','ashling','cinderImp','ash-and-ember spectral imps; upgraded has pronounced horns, lava veins and larger claws'),
('grave-doom-sentinels.webp','graveSentinel','doomSentinel','armored grave guardians with broad shield and mace; upgraded has black obsidian plate, runes and heavier silhouette'),
('hexbinder-soulweaver.webp','hexbinder','soulWeaver','hooded cursed sorcerers casting eldritch violet magic; upgraded has luminous soul ribbons and ornate staff'),
('dusk-abyssal-reavers.webp','duskReaver','abyssalReaver','fierce abyssal melee warriors with dual blades; upgraded wears heavier infernal armor and longer hooked blades'),
('umbral-eclipse-dragons.webp','umbralDragon','eclipseDragon','violet-black winged dragons; upgraded shows eclipse crown, plated scales, spectral glow and imposing larger silhouette'),
]
def main():
    dest=ROOT/'build'/'art-briefs'
    dest.mkdir(parents=True,exist_ok=True)
    backlog=[]
    existing=ROOT/'assets-source'/'keypose-atlases'
    for filename,basic,upgrade,direction in PAIR_SPECS:
        if (existing/filename).is_file():continue
        prompt=(
            'Create a true transparent-alpha orthographic sprite-pose atlas for a '
            'dark fantasy game faction named Umbral Dominion. Exactly TWO ROWS and '
            'FOUR COLUMNS with no text, lines, borders, scenery, labels or shadows. '
            'Top row: '+basic+'. Bottom row: '+upgrade+'. '
            'Pose columns for BOTH characters: (1) idle guarded standing, '
            '(2) side-facing advancing stride or wing flap, '
            '(3) distinct weapon swing or magical casting attack with visible limbs, '
            '(4) recoil from a hit. '+direction+'. '
            'Each character retains the SAME identity, armor, equipment and scale '
            'in all four cells. Distinct visible poses—not color changes, duplicate '
            'stills, marketing slides or an infographic. '
            'Isolated, highly legible game sprite silhouettes, right-facing, '
            'violet/obsidian palette; original artwork, no copyrighted game sprite copying. '
            'Final atlas: 1774x887 WEBP or PNG source resampled to exactly that size, '
            'real alpha transparency on all empty pixels. '
            'Do not add titles, UI panels, mockups or downloadable buttons.')
        item={'filename':filename,'topRow':basic,'bottomRow':upgrade,
            'poseColumns':['idle','move','attack','hit'],
            'sourceDimensions':[1774,887], 'requiresTrueTransparency':True,
            'needsVisualAndSilhouetteApproval':True,'prompt':prompt,
            'status':'AWAITING_ORIGINAL_SOURCE_ART',
            'estimatedSourcePoseCount':8,
            'heroIIIAssetReuseAllowed':False}
        backlog.append(item)
        (dest/(filename+'.json')).write_text(json.dumps(item,indent=2)+'\n')
    (ROOT/'build'/'ART_GENERATION_BRIEFS.json').write_text(json.dumps({
       'missingPairs':len(backlog),'missingCreatures':len(backlog)*2,
       'sourcePosesMissing':len(backlog)*8,
       'note':'Image generation is not invoked by CI. Generating artwork may require a user-authorized image provider.',
       'items':backlog,
       'releaseStatus':'BLOCKED'},indent=2)+'\n')
    print(f"ART GENERATION PLAN: {len(backlog)} atlases / {len(backlog)*8} distinct source poses pending")
if __name__=='__main__':
    main()
