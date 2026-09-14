$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force baseline,portable,out,verify | Out-Null
gh run download 34839888666 --repo bachlangcomic-creator/maplenghia -n Nghia-V9.9.6-CoordinateMapBuilder-Windows-Candidate -D baseline
if ($LASTEXITCODE -ne 0) { throw 'baseline artifact download failed' }
$zip='baseline/NghiaClient_V9.9.6_CoordinateMapBuilder_Windows_Candidate.zip'
if (!(Test-Path $zip)) { throw 'baseline candidate zip missing' }
Expand-Archive $zip -DestinationPath portable -Force
if (!(Test-Path portable/NghiaLauncher.exe)) { throw 'NghiaLauncher.exe missing' }
if (!(Test-Path portable/app_payload/nghia_spotify_nologin.py)) { throw 'UI source missing' }
Write-Host 'V997_BASELINE_PREPARE_OK'
