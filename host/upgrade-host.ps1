$ErrorActionPreference = 'Stop'
$source = $PSScriptRoot
$target = Join-Path $env:USERPROFILE 'FiguraCloud'
if (!(Test-Path (Join-Path $target 'compose.try.yaml'))) {
    throw 'Existing FiguraCloud/compose.try.yaml not found. Do not continue in another directory.'
}
$backup = Join-Path $target ('backup-before-autocloud-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $backup | Out-Null
foreach ($name in @('server.py','Dockerfile','requirements.txt','dashboard.py','publisher.py','compose.autocloud.yaml')) {
    $existing = Join-Path $target $name
    if (Test-Path $existing) { Copy-Item -LiteralPath $existing -Destination $backup }
    Copy-Item -LiteralPath (Join-Path $source $name) -Destination $target -Force
}
foreach ($name in @('setup-token.ps1','Start-AutoCloud.bat','Stop-AutoCloud.bat')) {
    Copy-Item -LiteralPath (Join-Path $source $name) -Destination $target -Force
}
Set-Location $target
$ignore = Join-Path $target '.dockerignore'
$rules = @'
.github-publisher.token
backup-before-autocloud-*
*.backup-*
cloud-files.zip
'@
Add-Content -LiteralPath $ignore -Value $rules -Encoding ASCII
if (!(Test-Path '.github-publisher.token')) {
    & (Join-Path $target 'setup-token.ps1')
}
docker compose -f compose.try.yaml -f compose.autocloud.yaml config --quiet
if ($LASTEXITCODE -ne 0) { throw 'Compose validation failed.' }
docker compose -f compose.try.yaml -f compose.autocloud.yaml up -d --build
if ($LASTEXITCODE -ne 0) { throw 'AutoCloud could not start.' }
Start-Process 'http://localhost:8787'
Write-Host 'Ready. Give players the matching AutoCloud JAR plus Figura 0.1.6.'
