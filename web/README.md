# StripCheck website

React, TypeScript and Vite client for the local StripCheck API. See the [root setup guide](../README.md) to install the Python backend and load official lists.

From the repository root:

```sh
npm --prefix web ci
npm --prefix web run dev
```

The development proxy expects the API at `http://127.0.0.1:8765`; start it with `python cli.py serve --port 8765`. For normal local use, build with `npm --prefix web run build`, then use the Python server directly; it serves the generated website and API from one origin.

## Verification

```sh
npm --prefix web test
npm --prefix web run lint
npm --prefix web run build
```

Tests cover theme contrast, fragmented streaming responses, early disconnects, oversized events, timeouts, cancellation, stale responses and unavailable browser storage. Secondary pages load on demand. Requests have deadlines, and saved state restores only if it is still the latest operation. Photo previews are temporary object URLs; verdicts come from the server.

The website does not certify medicines. Synthetic examples are labelled and isolated from real alert records. No fonts or images are loaded from a CDN. See the root README for the local storage and phone-pairing boundaries.
