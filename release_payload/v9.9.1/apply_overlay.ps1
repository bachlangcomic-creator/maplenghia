param([Parameter(Mandatory=$true)][string]$PortableRoot)
$ErrorActionPreference='Stop'
$root=(Resolve-Path $PortableRoot).Path
$app=Join-Path $root 'app_payload'
$overlay=Split-Path -Parent $MyInvocation.MyCommand.Path

foreach($name in @('spotify_all_cure_assets.py','spotify_all_cure_market.py')){
  $src=Join-Path $overlay $name
  if(!(Test-Path $src)){ throw "missing V9.9.1 overlay member $name" }
  Copy-Item $src (Join-Path $app $name) -Force
}

$maple=Join-Path $app 'maple_nghia_pro.py'
$text=[IO.File]::ReadAllText($maple).Replace("`r`n","`n").Replace("`r","`n")
[IO.File]::WriteAllText($maple,$text,[Text.UTF8Encoding]::new($false))
Push-Location $root
try {
  $patchPath=Join-Path $overlay 'maple_nghia_pro.patch'
  git apply --check --directory=app_payload $patchPath
  if($LASTEXITCODE -ne 0){ throw 'V9.9.1 host patch check failed' }
  git apply --directory=app_payload $patchPath
  if($LASTEXITCODE -ne 0){ throw 'V9.9.1 host patch apply failed' }
}
finally { Pop-Location }

New-Item -ItemType Directory -Force (Join-Path $app 'evidence') | Out-Null
Copy-Item (Join-Path $overlay 'evidence/all_cure_market.json') (Join-Path $app 'evidence/all_cure_market.json') -Force
Write-Host 'V991_ALL_CURE_OVERLAY_APPLY_OK'
