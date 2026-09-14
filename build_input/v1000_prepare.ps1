$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force baseline,portable,out,verify | Out-Null
gh run download 34850034459 --repo bachlangcomic-creator/maplenghia -n Nghia-V9.9.8-PiratePointsMapBuilder-Windows-Candidate -D baseline
if ($LASTEXITCODE -ne 0) { throw 'V9.9.8 baseline artifact download failed' }
$zip='baseline/NghiaClient_V9.9.8_PiratePointsMapBuilder_Windows_Candidate.zip'
if (!(Test-Path $zip)) { throw 'V9.9.8 baseline zip missing' }
$got=(Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($got -ne '5b26364bbc6667628d1d005d33b8615269f820552a1faa1203a4e6e02a01ed15') { throw "baseline hash mismatch $got" }
Expand-Archive $zip -DestinationPath portable -Force
$expected=@{
  'spotify_recovered_core.py'='18e164944d5842629af55ca0f70f274192421515c01ac6451c0bdedf13109d95'
  'spotify_recovered_api.py'='1ceb0d194d1edfcab1a8005ac7fdd04343a90ff6962dc77d2dc675aac06a4339'
  'spotify_behavior_engine.py'='de137e5486518d183e26b83d360fa4a164e0fd136ce1deef003d6ad7b953fe97'
  'spotify_main_farm_orchestrator.py'='1404ef82297bf6af9e3e74df1b75a6915dfdf5b4e0c557de5027934649b25f68'
  'maple_nghia_pro.py'='5f7a97629175640006f026886ffd3eed6f703aa2cb74113431c20a28ae866af9'
  'nghia_spotify_nologin.py'='b22ae1169d2746edd00e328d4f3304edb2ac37de7d7f4b80eb4753ba9a4d723f'
  'maps.json'='52364dc3a284e051a04263b49e008caf699de9127cc62c8c59b7a8bb6533671d'
}
foreach ($name in $expected.Keys) {
  $path=Join-Path 'portable/app_payload' $name
  $h=(Get-FileHash $path -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($h -ne $expected[$name]) { throw "$name baseline hash mismatch $h" }
}
Write-Host 'V1000_BASELINE_V998_OK'
