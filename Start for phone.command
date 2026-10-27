#!/bin/zsh
# Same-Wi-Fi access with a fresh pairing token for each launch.
set -e
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python || ! -f web/dist/index.html ]]; then
  echo "Complete the one-time setup in README.md before starting phone access."
  read -r "?Press Return to close. "
  exit 1
fi
port="${STRIPCHECK_PORT:-8000}"
if curl --fail --silent --max-time 1 "http://127.0.0.1:${port}/api/health" >/dev/null 2>&1; then
  echo "StripCheck is already running. Stop its Terminal window with Control-C, then open this launcher again."
  read -r "?Press Return to close. "
  exit 1
fi
export STRIPCHECK_LAN_TOKEN="${STRIPCHECK_LAN_TOKEN:-$(.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(24))')}"
url="http://127.0.0.1:${port}/?k=${STRIPCHECK_LAN_TOKEN}"
(
  for attempt in {1..30}; do
    if curl --fail --silent --max-time 1 --header "X-StripCheck-Key: ${STRIPCHECK_LAN_TOKEN}" "http://127.0.0.1:${port}/api/health" >/dev/null 2>&1; then
      open "$url"
      break
    fi
    sleep 0.5
  done
) &
echo "Keep this window open. Connect your phone to the same trusted Wi-Fi."
echo "Open the phone pairing screen in the website and scan its QR code."
exec .venv/bin/python cli.py serve --lan --port "$port"
