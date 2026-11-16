$ErrorActionPreference = 'Stop'
Set-Location "$env:USERPROFILE\FiguraCloud"
$path = Join-Path $PWD.Path 'server.py'
$source = [IO.File]::ReadAllText($path)
$pattern = '(?ms)(    async def motd\(req\):\r?\n        user\(req\)\r?\n)        return web\.json_response\([^\r\n]*\)'
$match = [regex]::Match($source, $pattern)
if (!$match.Success) { throw 'MOTD block not found. No files changed.' }
Copy-Item -LiteralPath $path -Destination ($path + '.backup-' + [guid]::NewGuid().ToString('N'))
$replacement = @'
        return web.json_response({"text":"จัดทำโดย\n\n⋆. 𐙚˚࿔ T-Zero 𝜗𝜚˚⋆"})
'@
$updated = $source.Substring(0, $match.Index) + $match.Groups[1].Value + $replacement.TrimEnd() + $source.Substring($match.Index + $match.Length)
[IO.File]::WriteAllText($path, $updated, [Text.UTF8Encoding]::new($false))
$argsList = @('compose','-f','compose.try.yaml')
if (Test-Path 'compose.autocloud.yaml') { $argsList += @('-f','compose.autocloud.yaml') }
elseif (Test-Path 'compose.dashboard.yaml') { $argsList += @('-f','compose.dashboard.yaml') }
$argsList += @('up','-d','--build','--no-deps','backend')
& docker @argsList
if ($LASTEXITCODE -ne 0) { throw 'Backend update failed.' }
Write-Host 'Credit updated. Restart Minecraft to refresh the cloud message.'
