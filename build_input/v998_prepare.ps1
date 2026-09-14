$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force baseline,portable,out,verify | Out-Null
gh run download 34842071204 --repo bachlangcomic-creator/maplenghia -n Nghia-V9.9.7-CoordinateMapBuilder-Windows-Candidate -D baseline
if ($LASTEXITCODE -ne 0) { throw 'baseline artifact download failed' }
$zip='baseline/NghiaClient_V9.9.7_CoordinateMapBuilder_Windows_Candidate.zip'
if (!(Test-Path $zip)) { throw 'baseline zip missing' }
$got=(Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($got -ne '5a499a62fbfb4d928af51cf5c83df59f5df4e8d6378cfc04067c8a779f7f0140') { throw "baseline hash mismatch $got" }
Expand-Archive $zip -DestinationPath portable -Force
$maps=(Get-FileHash portable/app_payload/maps.json -Algorithm SHA256).Hash.ToLowerInvariant()
if ($maps -ne '52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d') { throw "maps hash mismatch $maps" }
$orch=(Get-FileHash portable/app_payload/spotify_main_farm_orchestrator.py -Algorithm SHA256).Hash.ToLowerInvariant()
if ($orch -ne '1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68') { throw "orchestrator hash mismatch $orch" }
Write-Host 'V998_BASELINE_OK'
