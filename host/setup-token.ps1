$ErrorActionPreference = 'Stop'
Set-Location "$env:USERPROFILE\FiguraCloud"
Write-Host 'Use a fine-grained GitHub token for T0R1409/t0ch1na-figura-cloud ONLY.'
Write-Host 'Repository permissions: Contents = Read and write. Do not send the token in chat.'
$secret = Read-Host 'Paste the token here (hidden)' -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try {
    $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    if ([string]::IsNullOrWhiteSpace($token)) { throw 'Token is empty.' }
    $path = Join-Path $PWD.Path '.github-publisher.token'
    [IO.File]::WriteAllText($path, $token.Trim(), [Text.UTF8Encoding]::new($false))
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    $token = $null
    $secret.Dispose()
}
$identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
& icacls $path /inheritance:r /grant:r "${identity}:(R,W)" | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Could not protect the token file.' }
Write-Host 'Publisher token saved locally. It is NOT included in the player mod.'
