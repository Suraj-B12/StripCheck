param([switch]$Lan, [ValidateRange(1, 65535)][int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$Python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (!(Test-Path $Python) -or !(Test-Path 'web\dist\index.html')) {
    Write-Host 'Complete the one-time Windows setup in README.md first.'
    exit 1
}
$Url = "http://127.0.0.1:$Port"
if ($Lan) {
    if (!$env:STRIPCHECK_LAN_TOKEN) {
        $env:STRIPCHECK_LAN_TOKEN = & $Python -c 'import secrets; print(secrets.token_urlsafe(24))'
    }
    $Url += '/?k=' + $env:STRIPCHECK_LAN_TOKEN
    Write-Host 'Connect the phone to the same trusted Wi-Fi and open the pairing screen in StripCheck.'
}
$BrowserJob = Start-Job -ArgumentList $Url -ScriptBlock {
    param($Target)
    for ($Attempt = 0; $Attempt -lt 30; $Attempt++) {
        try {
            $Response = Invoke-WebRequest -Uri $Target -TimeoutSec 1 -UseBasicParsing
            if ($Response.StatusCode -eq 200) { Start-Process $Target; break }
        } catch { Start-Sleep -Milliseconds 500 }
    }
}
try {
    Write-Host 'Keep this window open while using StripCheck. Press Control-C to stop.'
    if ($Lan) { & $Python cli.py serve --lan --port $Port }
    else { & $Python cli.py serve --port $Port }
} finally {
    Stop-Job $BrowserJob -ErrorAction SilentlyContinue
    Remove-Job $BrowserJob -Force -ErrorAction SilentlyContinue
}
