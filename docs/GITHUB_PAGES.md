# Public showcase

The Pages build is an interactive presentation of StripCheck for friends, teachers and reviewers. It uses the same visual design and eleven clearly labelled fictional stories. It replays recorded results produced by the Python engine; it does not check real medicines, read photos, fetch CDSCO records or run a classifier in the browser.

The configured project address is **https://suraj-b12.github.io/StripCheck/**. This address becomes available after an authorized repository owner enables GitHub Pages and the deployment workflow succeeds. Follow the latest [Pages workflow](https://github.com/Suraj-B12/StripCheck/actions/workflows/pages.yml) for deployment status.

## One-time repository setting

An owner, maintainer or person with permission to manage Pages must open [Settings → Pages](https://github.com/Suraj-B12/StripCheck/settings/pages). Under **Build and deployment**, choose **GitHub Actions** as the **Source**. Ordinary code-write access cannot enable Pages initially. No personal token needs to be copied into the repository.

After enabling it, use **Run workflow** on the **Publish GitHub Pages showcase** workflow, or rerun a failed deployment. Future changes to the website on `main` trigger a tested build and deployment automatically. The workflow publishes only `web/dist-pages` with the official GitHub Pages actions.

## Preview and verify

```sh
npm --prefix web ci
npm --prefix web test
npm --prefix web run lint
npm --prefix web run build:pages
node scripts/check_pages_build.mjs
npm --prefix web run preview:pages
```

Open **http://127.0.0.1:4173/StripCheck/**. Hash routes such as `#/lists` work when shared, refreshed, or opened in another tab without a server rewrite. The normal `npm --prefix web run build` still writes `web/dist` for the local Python application.

The showcase stores only known demonstration identifiers and progress in browser-tab session storage. History is limited to thirty examples. No photo picker, real check, live sync, LAN pairing, or real-pack recheck is available in this build. If storage is blocked, examples remain usable in memory for that page visit. Clearing or closing the tab ends that session according to the browser's session-restoration policy.

## Rebuild the authored examples

The fixture source is `core.props.demo_cases()`. To regenerate after changing the engine:

```sh
python scripts/export_public_demo.py
python scripts/export_public_demo.py --check
```

The exporter creates an isolated temporary database before importing application modules, blocks network connections, and verifies that no live alerts or source snapshots were loaded. The committed JSON contains only authored synthetic fixtures and server-template verdicts. CI checks it against the engine; changes require tests and review before publication.

The public build never includes `data/`, `runs/`, databases, uploaded photos, credentials, or raw official source records. Real pack checks still require the local app and its own downloaded alert index. See the [root setup guide](../README.md).
