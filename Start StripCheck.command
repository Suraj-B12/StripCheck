#!/bin/zsh
# Double-click after completing the one-time setup in README.md.
set -e
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python || ! -f web/dist/index.html ]]; then
  echo "Complete the one-time Python and website setup in README.md first."
  echo "Then double-click Start StripCheck.command again."
  read -r "?Press Return to close. "
  exit 1
fi
port="${STRIPCHECK_PORT:-8000}"
url="http://127.0.0.1:${port}"
if curl --fail --silent --max-time 1 "$url/api/health" >/dev/null 2>&1; then
  open "$url"
  exit 0
fi
(
  for attempt in {1..30}; do
    if curl --fail --silent --max-time 1 "$url/api/health" >/dev/null 2>&1; then
      open "$url"
      break
    fi
    sleep 0.5
  done
) &
echo "Keep this window open while using StripCheck. Press Control-C to stop."
exec .venv/bin/python cli.py serve --port "$port"
