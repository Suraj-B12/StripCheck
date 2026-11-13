# Live demo guide (for the professor's review)

This runs StripCheck on Suraj's laptop and makes it reachable from any phone through a private Cloudflare link. Allow about 10 minutes for the demo.

## Before the review (once, the day before)
1. Pull the latest code: `git pull` in the repository folder.
2. Check that the one-time setup in `README.md` was done (the `.venv` folder exists and `web\dist\index.html` exists). If `web\dist` is missing, run `cd web; npm ci; npm run build`.
3. Check that these are installed: `cloudflared` (`winget install Cloudflare.cloudflared`) and Ollama with the model (`ollama pull qwen2.5:3b`).
4. Do a full dry run of the steps below on your own phone.

## Start the demo (2 minutes before)
1. Connect the laptop to the internet (college Wi-Fi or a phone hotspot).
2. Double-click **`Start StripCheck Demo.cmd`** in the repository folder.
   Or in PowerShell, from the repository folder:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\start-demo-tunnel.ps1
   ```
3. Wait for these lines (about 30 to 60 seconds; the script starts Ollama and loads the model if needed):
   ```
   Model ready
   Phone link : https://<random-words>.trycloudflare.com/?k=<token>
   QR code    : ...stripcheck-demo-qr.png (opening it now)
   ```
4. A QR code opens on the laptop. The professor scans it with a phone camera, or open the phone link in the laptop browser and project it.
5. **Keep that window open** for the whole demo. Closing it or pressing Ctrl-C stops the site. The link changes every time you start it.

The link only works with its token: anyone without the full link gets "Pair this device". Do not post it anywhere.

## Demo script (about 8 minutes)

**1. The problem (30 s).** CDSCO publishes monthly lists of drug batches that failed quality tests. Batch numbers are tiny, printed on foil, and OCR confuses characters such as B/8, 0/O, Z/2. Our agent checks a pack against 6,923 indexed alerts from the official portal, Jan 2019 to Sep 2026.

**2. Live thinking and a question (3 min).** Make sure **Local AI reasoning** (the switch next to the check button) is on. Click **Try a demo pack** and choose **03** (the misread batch).
- Point at the **Thinking** panel: the local model (qwen2.5:3b, running on the laptop, no internet API) streams its reasoning for each decision. When it finishes, the panel collapses to "Thought for 2 s" with the action it chose.
- Point at **Behind this check**: every step appears live (extract fields, exact search, look-alike search, grade).
- The agent then **asks a question**: "Which batch is printed on your pack: LM24088 or LM2408B?", with the reason it is asking. Explain: it never raises an alarm from a machine reading alone; a person must confirm the doubtful character.
- Choose **LM2408B**. The result says the batch is on an alert list. Point out that it is labelled as a synthetic demonstration, because demo packs never touch the real data.

**3. A real listed batch from a photo (2 min).** Upload `data\samples\pack_types\misread_FLAGGED.png` (or the realistic image you generated from `data\samples\realistic_pack_prompt.md`).
- The agent reads the photo locally (RapidOCR), shows the cropped batch line, thinks, and asks you to confirm the look-alike character.
- Answer with what is printed. The result is FLAGGED with a citation to the CDSCO list month and a link to the source.

**4. Safety behaviour (1 min).** Click **New check**, type a batch that is not on the lists (for example `QX7781`) and check it. The result is "No matching alert found". Point out the careful wording: it says the batch is not on the lists loaded, it never says the medicine is safe, and it is never shown in green.

**5. Failsafe (optional, 1 min).** Turn **Local AI reasoning** off and run demo pack 03 again: the same result comes from the rules alone. Every model call has a time limit and a rule fallback, so a check completes with Ollama off and without internet.

**6. Evidence (optional).** Show `docs/guide/index.html` (visual guide), the report PDF, and `docs/trace/` (Phoenix trace screenshots of a full check).

## If something goes wrong
| Problem | Fix |
|---|---|
| "The tunnel did not report a public address" | The internet connection blocks Cloudflare. Switch to a phone hotspot and start again. |
| No internet at all | Run `.\.venv\Scripts\python.exe cli.py serve` and open http://127.0.0.1:8000 on the laptop and project it. Everything works offline; only the phone link needs internet. |
| The phone shows "Pair this device" | Open the full link including `?k=...`, or scan the QR code again. |
| The AI reasoning switch is greyed out | Ollama is not running. Start it (`ollama serve`) and reload the page, or demo with the rules: results are the same. |
| The first thought is slow (over 10 s) | The model was still loading. Run the demo pack once before the professor arrives. |
| "Run the one-time Windows setup" | Follow the setup section of `README.md`. |
| A photo gives "No matching alert found" for a demo pack image | Expected: demo packs use invented batches that are not in the real alert data. Use "Try a demo pack" instead. |

## After the demo
Press Ctrl-C in the window (or close it). The site and the tunnel stop and the link no longer works.
