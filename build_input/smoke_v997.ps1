param(
  [Parameter(Mandatory=$true)][string]$Root,
  [Parameter(Mandatory=$true)][string]$Label
)
$ErrorActionPreference='Stop'
$rootPath=(Resolve-Path $Root).Path
$ud=Join-Path $rootPath 'user_data'
New-Item -ItemType Directory -Force $ud | Out-Null
$crash=Join-Path $ud 'launcher_crash.log'
if (Test-Path $crash) { Remove-Item $crash -Force }
$lp=Start-Process -FilePath (Join-Path $rootPath 'NghiaLauncher.exe') -WorkingDirectory $rootPath -PassThru
$deadline=(Get-Date).AddSeconds(35)
$app=$null
while ((Get-Date) -lt $deadline) {
  $apps=@(Get-Process -Name NghiaClientApp -ErrorAction SilentlyContinue)
  if ($apps.Count -gt 0) { $app=$apps[0]; break }
  if (Test-Path $crash) { Get-Content $crash; throw "$Label launcher crash log created" }
  Start-Sleep -Milliseconds 500
}
if ($null -eq $app) { throw "$Label NghiaClientApp.exe did not start within 35 seconds" }
Start-Sleep -Seconds 3
$app.Refresh()
if ($app.HasExited) { throw "$Label app exited during stability window" }
Write-Host "$Label OK PID=$($app.Id)"
@((Get-Process -Name NghiaClientApp -ErrorAction SilentlyContinue)) | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
if (!$lp.HasExited) { Stop-Process -Id $lp.Id -Force -ErrorAction SilentlyContinue }
if (Test-Path $crash) { throw "$Label launcher_crash.log exists after smoke" }
