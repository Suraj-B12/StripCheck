# Live mobile demo: StripCheck on this laptop, reachable from any phone through a Cloudflare quick tunnel.
# Usage (PowerShell, repository root):  ./scripts/start-demo-tunnel.ps1 [-Port 8000]
# The server stays bound to 127.0.0.1; only cloudflared reaches it. Every request needs the pairing token,
# which is embedded in the printed link (the phone stores it as a cookie on first open). Ctrl-C stops both.
param([ValidateRange(1, 65535)][int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
$Python = Join-Path $Root '.venv\Scripts\python.exe'
$Cloudflared = (Get-Command cloudflared -ErrorAction SilentlyContinue).Source
if (-not $Cloudflared) { $Cloudflared = 'C:\Program Files (x86)\cloudflared\cloudflared.exe' }
if (!(Test-Path $Python) -or !(Test-Path 'web\dist\index.html')) { Write-Host 'Run the one-time Windows setup in README.md first.'; exit 1 }
if (!(Test-Path $Cloudflared)) { Write-Host 'Install cloudflared first: winget install Cloudflare.cloudflared'; exit 1 }

# Optional local model for the live "thinking" view. Checks still complete with the rules if this fails.
function Test-Ollama { try { Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null; $true } catch { $false } }
if (-not (Test-Ollama)) {
    $Ollama = (Get-Command ollama -ErrorAction SilentlyContinue).Source
    if (-not $Ollama) { $Ollama = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe' }
    if (Test-Path $Ollama) {
        Write-Host 'Starting Ollama...'
        Start-Process -FilePath $Ollama -ArgumentList 'serve' -WindowStyle Hidden | Out-Null
        for ($i = 0; $i -lt 30 -and -not (Test-Ollama); $i++) { Start-Sleep -Seconds 1 }
    }
}
if (Test-Ollama) {
    Write-Host 'Loading the local model (qwen2.5:3b)...'
    & $Python -c "from core import llm, config; print('Model ready' if llm.warm(config.LLM_MODEL, timeout=120) else 'Model not loaded: checks will use the rules')"
} else {
    Write-Host 'Ollama is not running: checks will use the rules (the live AI reasoning switch stays off).'
}

$env:STRIPCHECK_LAN_TOKEN = & $Python -c 'import secrets; print(secrets.token_urlsafe(18))'
$env:STRIPCHECK_REQUIRE_TOKEN = '1'
$Log = Join-Path $env:TEMP 'stripcheck-tunnel.log'
Remove-Item $Log -ErrorAction SilentlyContinue

$Server = Start-Process -FilePath $Python -ArgumentList 'cli.py', 'serve', '--port', "$Port" -PassThru -WindowStyle Hidden
$Tunnel = Start-Process -FilePath $Cloudflared -ArgumentList 'tunnel', '--no-autoupdate', '--url', "http://127.0.0.1:$Port", '--logfile', $Log -PassThru -WindowStyle Hidden
try {
    $Url = $null
    for ($i = 0; $i -lt 60 -and -not $Url; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-Path $Log) { $Url = (Select-String -Path $Log -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' | Select-Object -First 1).Matches.Value }
    }
    if (-not $Url) { throw 'The tunnel did not report a public address within 30 s. Check your internet connection.' }
    $Link = "$Url/?k=$($env:STRIPCHECK_LAN_TOKEN)"
    $Qr = Join-Path $env:TEMP 'stripcheck-demo-qr.png'
    & $Python -c "import qrcode,sys; qrcode.make(sys.argv[1]).save(sys.argv[2])" $Link $Qr
    Write-Host ''
    Write-Host "Phone link : $Link"
    Write-Host "QR code    : $Qr (opening it now)"
    Write-Host 'Anyone with this link can use the demo while this window is open. Press Ctrl-C to stop.'
    Start-Process $Qr
    Wait-Process -Id $Server.Id
} finally {
    Stop-Process -Id $Tunnel.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $Server.Id -ErrorAction SilentlyContinue
}
