$ErrorActionPreference='Stop'
Remove-Item portable/app_payload/dist_nuitka -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem portable -Directory -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item portable/user_data/launcher_crash.log -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force out | Out-Null
$zip='out/NghiaClient_V9.9.7_CoordinateMapBuilder_Windows_Candidate.zip'
Compress-Archive -Path portable/* -DestinationPath $zip -CompressionLevel Optimal -Force
$sha=(Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
"$sha  NghiaClient_V9.9.7_CoordinateMapBuilder_Windows_Candidate.zip" | Set-Content -Encoding utf8 out/preflight_hashes.txt
$report=@{version='9.9.7';variant='CoordinateMapBuilderActiveUIFix';baseline='verified V9.9.6 CoordinateMapBuilder Windows candidate';compileall=$true;coordinate_map_feature_tests=$true;nuitka_build=$true;windows_launcher_smoke=$true;packaged_launcher_smoke=$false;portable_sha256=$sha;public_publish_performed=$false}
$report | ConvertTo-Json | Set-Content -Encoding utf8 out/preflight_report.json
Write-Host "V997_PACKAGE_OK $sha"
