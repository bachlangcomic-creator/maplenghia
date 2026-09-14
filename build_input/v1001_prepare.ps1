$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force baseline,portable,out,verify | Out-Null
$asset='NghiaClient_V10.0.0_IsolatedStrategyEngine_Windows_Candidate.zip'
gh release download v10.0.0 --repo bachlangcomic-creator/maplenghia --pattern $asset --dir baseline --clobber
if ($LASTEXITCODE -ne 0) { throw 'V10.0.0 baseline release download failed' }
$zip=Join-Path 'baseline' $asset
if (!(Test-Path $zip)) { throw 'V10.0.0 baseline zip missing' }
$got=(Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($got -ne '801cece7f9fd02c14f4fc29ab5624b54fa81eb708e9cbee4dd29857a8f766291') { throw "baseline hash mismatch $got" }
Expand-Archive $zip -DestinationPath portable -Force
$expected=@{
  'spotify_recovered_core.py'='18e164944d5842629af55ca0f70f274192421515c01ac6451c0bdedf13109d95'
  'maple_nghia_pro.py'='203ac9e103ae3d7e441f7021d15e975e2a3cddaebed4ef8f2a53c17730c0e8bc'
  'nghia_spotify_nologin.py'='378d7bfcd4c9bd3cbc5e86fe23851e4cd6f399c823afc31ed60e83783ad92bb1'
  'nghia_strategy_v10.py'='6066d1ec948b7e9783944a1c2825a033061b1e130fde44b3799783263b1da9b8'
  'maps.json'='52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d'
}
foreach ($name in $expected.Keys) {
  $path=Join-Path 'portable/app_payload' $name
  $h=(Get-FileHash $path -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($h -ne $expected[$name]) { throw "$name baseline hash mismatch $h" }
}
Write-Host 'V1001_BASELINE_V1000_OK'
