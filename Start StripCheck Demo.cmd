@echo off
rem Double-click to start the StripCheck live demo (server + local model + Cloudflare tunnel).
rem Keep this window open during the demo. Close it or press Ctrl-C to stop.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\start-demo-tunnel.ps1" -Port 8000
pause
