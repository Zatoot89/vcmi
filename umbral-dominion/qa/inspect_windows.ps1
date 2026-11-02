# Umbral Dominion v0.5 — Windows inspection with reproducible JSON evidence
# Never marks actual gameplay as PASS without separate game testing.
[CmdletBinding()]
param(
  [string] $VcmiDataDir = "$env:USERPROFILE\Documents\My Games\vcmi",
  [string] $ReportDir = "$env:USERPROFILE\Desktop\UmbralDominion-QA",
  [string] $GameExecutable = "",
  [switch] $LaunchGame
)
$ErrorActionPreference = "Stop"
$tests = New-Object 'System.Collections.Generic.List[object]'
function Check([string] $name, [bool] $passed, [string] $detail) {
  $tests.Add([pscustomobject]@{ test=$name;status=$(if($passed){"PASS"}else{"FAIL"});detail=$detail })
  Write-Host ("{0} {1}: {2}" -f $(if($passed){"PASS"}else{"FAIL"}),$name,$detail)
}
$mod = Join-Path $VcmiDataDir 'Mods\umbralDominion'
$rootFound=Test-Path -LiteralPath $mod -PathType Container
Check 'Mod installed' $rootFound $mod
$creatureCfg = Join-Path $mod 'Content\config\creatures.json'
$factionCfg = Join-Path $mod 'Content\config\faction.json'
if (-not (Test-Path -LiteralPath $creatureCfg)) {throw "Missing creature config $creatureCfg"}
if (-not (Test-Path -LiteralPath $factionCfg)) {throw "Missing faction config $factionCfg"}
$creatures=Get-Content -LiteralPath $creatureCfg -Raw | ConvertFrom-Json
$factions=Get-Content -LiteralPath $factionCfg -Raw | ConvertFrom-Json
$creatureProps=@($creatures.PSObject.Properties)
Check '14 creature configurations' ($creatureProps.Count -eq 14) "$($creatureProps.Count) found"
$animations=New-Object 'System.Collections.Generic.List[string]'
$wavReferences=New-Object 'System.Collections.Generic.List[string]'
foreach($entry in $creatureProps) {
  $c=$entry.Value
  if ($c.graphics.animation) {
    $animations.Add([string]$c.graphics.animation)
  }
  foreach($s in @($c.sound.PSObject.Properties)){
    $wavReferences.Add([string]$s.Value)
  }
}
$missingAnimations=@($animations | Where-Object { -not (Test-Path -LiteralPath (Join-Path $mod ('Content\sprites\' + $_))) })
Check 'Creature animations on disk' ($missingAnimations.Count -eq 0 -and $animations.Count -eq 14) "$($animations.Count) refs; missing $($missingAnimations.Count)"
$uniqueSfx=@($wavReferences | Sort-Object -Unique)
$missingWav=@($uniqueSfx | Where-Object { -not (Test-Path -LiteralPath (Join-Path $mod ('Content\sounds\' + $_))) })
Check 'Original prototype sound references' ($uniqueSfx.Count -eq 72 -and $missingWav.Count -eq 0) "$($uniqueSfx.Count) files; missing $($missingWav.Count)"
$facProps=@($factions.PSObject.Properties)
$structures=@()
if ($facProps.Count -gt 0) {
  $structures=@($facProps[0].Value.town.structures.PSObject.Properties)
}
Check '36 town structures configured' ($structures.Count -eq 36) "$($structures.Count) buildings"
$overlays=@(Get-ChildItem -LiteralPath (Join-Path $mod 'Content\sprites') -Filter 'UD_TOWN_*_FRAME0.png' -File -ErrorAction SilentlyContinue)
Check '36 prototype town overlays' ($overlays.Count -ge 36) "$($overlays.Count) overlays"
$theme=Test-Path -LiteralPath (Join-Path $mod 'Content\Music\UD_EBON_SPIRE.ogg')
Check 'Original Ebonspire town music' $theme "OGG exists: $theme"
$gameFound=$false
if ($GameExecutable) {
  $gameFound=Test-Path -LiteralPath $GameExecutable -PathType Leaf
} else {
  $cmd=Get-Command 'vcmi_client.exe' -ErrorAction SilentlyContinue
  if ($cmd) { $GameExecutable=$cmd.Source; $gameFound=$true }
}
Check 'VCMI executable detected' $gameFound $(if($gameFound){$GameExecutable}else{'Not supplied; use -GameExecutable PATH'})
$ranGame=$false
if ($LaunchGame) {
  if (-not $gameFound) {throw '-LaunchGame requires a valid -GameExecutable path'}
  Write-Warning "Launching the game. Close VCMI after manually inspecting town, combat, recruitment and animation."
  Start-Process -FilePath $GameExecutable -Wait
  $ranGame=$true
}
New-Item -Path $ReportDir -ItemType Directory -Force | Out-Null
$report=[ordered]@{
    version='0.5.0-alpha'
    mode='WINDOWS_INSTALL_INSPECTION_NOT_GAMEPLAY_PASS'
    collected=(Get-Date).ToString('o')
    VcmiDataDir=$VcmiDataDir
    gameExecutable=$GameExecutable
    gameLaunchedByThisScript=$ranGame
    inGameTownCombatRecruitmentVerified=$false
    testCount=$tests.Count
    passed=@($tests|Where-Object status -eq PASS).Count
    failed=@($tests|Where-Object status -eq FAIL).Count
    tests=@($tests.ToArray())
    requiredGameplayEvidence=@('VCMI version','launcher screenshot with enabled mod','town screenshot',
      'tavern hero recruitment','all 7 dwelling upgrades','combat attacks, deaths and projectiles',
      'original sound playback','siege screenshot','VCMI logs with no mod errors')
}
$target=Join-Path $ReportDir 'umbral-windows-inspection.json'
$report|ConvertTo-Json -Depth 12|Set-Content -LiteralPath $target -Encoding utf8
Write-Host "EVIDENCE: $target"
if ($report.failed -gt 0) {exit 1}
exit 0
