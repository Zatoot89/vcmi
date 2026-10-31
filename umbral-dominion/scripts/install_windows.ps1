# Install a draft Umbral Dominion VCMI mod safely on Windows
# Uses the VCMI user data folder rather than modifying game executables.
# Example: powershell -ExecutionPolicy Bypass -File .\install_windows.ps1 -Archive .\umbral-dominion-dev-DRAFT.zip
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$Archive,
  [string]$VcmiDataDir = "$env:USERPROFILE\Documents\My Games\vcmi"
)
$ErrorActionPreference="Stop"
$resolved=(Resolve-Path -LiteralPath $Archive).Path
if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) { throw "ZIP not found: $Archive" }
if ([IO.Path]::GetExtension($resolved).ToLowerInvariant() -ne ".zip") { throw "Provide a ZIP archive." }
$work=Join-Path $env:TEMP ("umbral-install-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $work -Force | Out-Null
try {
  Expand-Archive -LiteralPath $resolved -DestinationPath $work -Force
  $source=Get-ChildItem $work -Filter "mod.json" -File -Recurse |
     Where-Object { $_.Directory.Name -eq "umbralDominion" } | Select-Object -First 1
  if (-not $source) {
    $nested=Get-ChildItem $work -Filter "*DRAFT.zip" -File -Recurse | Select-Object -First 1
    if (-not $nested) { throw "No Mods/umbralDominion/mod.json found in archive" }
    $inside=Join-Path $work "nested"
    Expand-Archive -LiteralPath $nested.FullName -DestinationPath $inside -Force
    $source=Get-ChildItem $inside -Filter "mod.json" -File -Recurse |
       Where-Object { $_.Directory.Name -eq "umbralDominion" } | Select-Object -First 1
    if (-not $source) { throw "Nested archive contains no mod.json" }
  }
  $meta=Get-Content -LiteralPath $source.FullName -Raw | ConvertFrom-Json
  if ($meta.name -notmatch 'Umbral Dominion') { throw "Unexpected mod: $($meta.name)" }
  $modroot=Join-Path $VcmiDataDir "Mods"
  if (-not (Test-Path -LiteralPath $modroot)) { New-Item -ItemType Directory -Path $modroot -Force | Out-Null }
  $dest=Join-Path $modroot "umbralDominion"
  if (Test-Path -LiteralPath $dest) {
    $backup=Join-Path $modroot ("umbralDominion-backup-"+(Get-Date -Format "yyyyMMdd-HHmmss"))
    Move-Item -LiteralPath $dest -Destination $backup
    Write-Host "Previous version backed up to: $backup"
  }
  Copy-Item -LiteralPath $source.Directory.FullName -Destination $dest -Recurse
  if (-not (Test-Path -LiteralPath (Join-Path $dest "Content\config\creatures.json"))) {
    throw "Copy completed but content layout check failed"
  }
  Write-Host "Installed prototype into $dest"
  Write-Warning "This copy is a PROCEDURAL PROTOTYPE. Launch VCMI manually and complete WINDOWS_QA.md."
  Write-Host "VCMI data and logs folder: $VcmiDataDir"
} finally {
  Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}
