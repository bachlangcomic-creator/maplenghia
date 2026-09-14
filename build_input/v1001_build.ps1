$ErrorActionPreference='Stop'
Push-Location portable/app_payload
try {
  if (Test-Path dist_nuitka) { Remove-Item dist_nuitka -Recurse -Force }
  python -m nuitka `
    --onefile `
    --assume-yes-for-downloads `
    --windows-console-mode=disable `
    --enable-plugin=tk-inter `
    --include-package=customtkinter `
    --include-package-data=customtkinter `
    --include-module=client_paths `
    --include-module=client_update_bridge `
    --include-module=nghia_strategy_v10 `
    --include-module=spotify_recovered_core `
    --include-module=spotify_recovered_api `
    --include-module=spotify_behavior_engine `
    --include-module=spotify_focus_parity `
    --include-module=spotify_detection_parity `
    --include-module=spotify_watchdog `
    --include-module=spotify_exact_assets `
    --include-module=spotify_miumiu_sell `
    --include-module=spotify_pc_alarm `
    --include-module=spotify_all_cure_assets `
    --include-module=spotify_all_cure_executor `
    --include-module=spotify_all_cure_market `
    --include-module=spotify_main_farm_orchestrator `
    --include-module=spotify_c2_runtime_support `
    --include-data-dir=spotify_miumiu=spotify_miumiu `
    --include-data-dir=evidence=evidence `
    --include-data-files=background.png=background.png `
    --include-data-files=maps.json=maps.json `
    --include-data-files=mushroom_icon.png=mushroom_icon.png `
    --include-data-files=mushroom_icon.ico=mushroom_icon.ico `
    --include-data-files=spotify_yellow_dot.png=spotify_yellow_dot.png `
    --windows-icon-from-ico=mushroom_icon.ico `
    --output-filename=NghiaClientApp.exe `
    --output-dir=dist_nuitka `
    nghia_spotify_nologin.py
  if ($LASTEXITCODE -ne 0) { throw 'Nuitka build failed' }
  if (!(Test-Path dist_nuitka/NghiaClientApp.exe)) { throw 'NghiaClientApp.exe missing' }
  Copy-Item dist_nuitka/NghiaClientApp.exe NghiaClientApp.exe -Force
}
finally { Pop-Location }
$bytes=[IO.File]::ReadAllBytes('portable/app_payload/NghiaClientApp.exe')
if ($bytes[0] -ne 0x4d -or $bytes[1] -ne 0x5a) { throw 'not PE/MZ' }
Write-Host 'V1001_NUITKA_PE_OK'
