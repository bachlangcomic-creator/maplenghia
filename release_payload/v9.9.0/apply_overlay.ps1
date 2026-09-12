param([Parameter(Mandatory=$true)][string]$PortableRoot)
$ErrorActionPreference='Stop'
$root=(Resolve-Path $PortableRoot).Path
$app=Join-Path $root 'app_payload'
$overlay=Split-Path -Parent $MyInvocation.MyCommand.Path

$copies=@(
  'spotify_detection_parity.py','spotify_watchdog.py','spotify_all_cure_assets.py',
  'spotify_all_cure_executor.py','spotify_all_cure_market.py','spotify_main_farm_orchestrator.py'
)
foreach($name in $copies){
  $src=Join-Path $overlay $name
  if(!(Test-Path $src)){ throw "missing overlay member $name" }
  Copy-Item $src (Join-Path $app $name) -Force
}

# Normalize LF only for patch targets, matching the existing V9.8.1 workflow.
foreach($target in @('spotify_recovered_core.py','maple_nghia_pro.py')){
  $path=Join-Path $app $target
  $text=[IO.File]::ReadAllText($path).Replace("`r`n","`n").Replace("`r","`n")
  [IO.File]::WriteAllText($path,$text,[Text.UTF8Encoding]::new($false))
}
Push-Location $root
try {
  foreach($patch in @('spotify_recovered_core.patch','maple_nghia_pro.patch','maple_nghia_pro_mainfarm.patch','maple_nghia_pro_legacy_contract.patch')){
    $patchPath=Join-Path $overlay $patch
    git apply --check --directory=app_payload $patchPath
    if($LASTEXITCODE -ne 0){ throw "$patch check failed" }
    git apply --directory=app_payload $patchPath
    if($LASTEXITCODE -ne 0){ throw "$patch apply failed" }
  }
}
finally {
  Pop-Location
}
New-Item -ItemType Directory -Force (Join-Path $app 'evidence') | Out-Null
Copy-Item (Join-Path $overlay 'evidence/*.json') (Join-Path $app 'evidence') -Force
Write-Host 'V990_OVERLAY_APPLY_OK'