$ErrorActionPreference = 'Stop'

$target = Join-Path (Resolve-Path 'portable/app_payload').Path 'tesseract'
$targetExe = Join-Path $target 'tesseract.exe'
$targetTessdata = Join-Path $target 'tessdata'
$targetKor = Join-Path $targetTessdata 'kor.traineddata'
$targetEng = Join-Path $targetTessdata 'eng.traineddata'

function Test-PortableBundle {
  return (Test-Path $targetExe) -and (Test-Path $targetKor) -and (Test-Path $targetEng)
}

if (-not (Test-PortableBundle)) {
  $candidates = @(
    'C:\Program Files\Tesseract-OCR',
    'C:\Program Files (x86)\Tesseract-OCR'
  )
  $source = $null
  foreach ($candidate in $candidates) {
    if (Test-Path (Join-Path $candidate 'tesseract.exe')) {
      $source = $candidate
      break
    }
  }

  if (-not $source) {
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
      throw 'Tesseract is not installed and Chocolatey is unavailable on the Windows builder.'
    }
    choco install tesseract -y --no-progress
    if ($LASTEXITCODE -ne 0) { throw 'Chocolatey Tesseract install failed' }
    foreach ($candidate in $candidates) {
      if (Test-Path (Join-Path $candidate 'tesseract.exe')) {
        $source = $candidate
        break
      }
    }
  }
  if (-not $source) { throw 'Could not locate Tesseract-OCR after install.' }

  if (Test-Path $target) { Remove-Item $target -Recurse -Force }
  Copy-Item $source $target -Recurse -Force
  New-Item -ItemType Directory -Force $targetTessdata | Out-Null

  $korUrl = 'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/kor.traineddata'
  $engUrl = 'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/eng.traineddata'
  Invoke-WebRequest -Uri $korUrl -OutFile $targetKor -UseBasicParsing
  Invoke-WebRequest -Uri $engUrl -OutFile $targetEng -UseBasicParsing
}

if (-not (Test-PortableBundle)) { throw 'Portable Tesseract bundle is incomplete.' }
if ((Get-Item $targetKor).Length -lt 1000000) { throw 'kor.traineddata looks incomplete.' }
if ((Get-Item $targetEng).Length -lt 1000000) { throw 'eng.traineddata looks incomplete.' }

$env:TESSDATA_PREFIX = (Resolve-Path $targetTessdata).Path
$langs = @(& $targetExe --list-langs 2>&1 | ForEach-Object { $_.ToString().Trim() })
if ($LASTEXITCODE -ne 0) { throw 'Bundled Tesseract failed --list-langs.' }
if ($langs -notcontains 'kor') { throw 'Bundled Tesseract does not report Korean language data.' }
if ($langs -notcontains 'eng') { throw 'Bundled Tesseract does not report English language data.' }

Write-Host "PORTABLE_TESSERACT_KOR_ENG_OK target=$target"
