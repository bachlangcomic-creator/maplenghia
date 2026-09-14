param([Parameter(Mandatory=$true)][string]$Root)
$ErrorActionPreference='Stop'
$root=(Resolve-Path $Root).Path
$ud=Join-Path $root 'user_data'; New-Item -ItemType Directory -Force $ud | Out-Null
$crash=Join-Path $ud 'launcher_crash.log'; if (Test-Path $crash) { Remove-Item $crash -Force }
$lp=Start-Process -FilePath (Join-Path $root 'NghiaLauncher.exe') -WorkingDirectory $root -PassThru
$deadline=(Get-Date).AddSeconds(35); $app=$null
while ((Get-Date) -lt $deadline) {
  $apps=@(Get-Process -Name NghiaClientApp -ErrorAction SilentlyContinue)
  if ($apps.Count -gt 0) { $app=$apps[0]; break }
  if (Test-Path $crash) { Get-Content $crash; throw 'launcher crash log created' }
  Start-Sleep -Milliseconds 500
}
if ($null -eq $app) { throw 'NghiaClientApp.exe did not start' }
Start-Sleep -Seconds 3
$app.Refresh(); if ($app.HasExited) { throw 'app exited during smoke' }
Write-Host "V998_LAUNCH_OK PID=$($app.Id) ROOT=$root"
@((Get-Process -Name NghiaClientApp -ErrorAction SilentlyContinue)) | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
if (!$lp.HasExited) { Stop-Process -Id $lp.Id -Force -ErrorAction SilentlyContinue }
if (Test-Path $crash) { throw 'launcher_crash.log exists after smoke' }
