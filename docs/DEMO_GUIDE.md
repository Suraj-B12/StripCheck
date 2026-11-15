# Live demo guide (for the professor's review)

This runs StripCheck on Suraj's laptop and makes it reachable from any phone through a private Cloudflare link. Allow about 12 minutes for the demo.

## Before the review (once, the day before)
1. Pull the latest code: `git pull` in the repository folder.
2. Check that the one-time setup in `README.md` was done (the `.venv` folder exists and `web\dist\index.html` exists). If `web\dist` is missing, run `cd web; npm ci; npm run build`.
3. Check that these are installed: `cloudflared` (`winget install Cloudflare.cloudflared`) and Ollama with both models (`ollama pull qwen2.5:3b` and `ollama pull qwen2.5vl:3b`, the vision model).
4. Do a full dry run of the steps below on your own phone.
5. Warm both models once, because the first call loads them into memory. Run demo pack 03 in Agent mode, then upload `data\samples\pack_types\unreadable_test.png` once and answer its questions. The vision model has no GPU on this laptop and takes 2 to 6 seconds per crop (the first call is slower), so do this before the professor arrives.

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

## Demo script (about 12 minutes)

**1. The problem (30 s).** CDSCO publishes monthly lists of drug batches that failed quality tests. Batch numbers are tiny, printed on foil, and OCR confuses characters such as B/8, 0/O, Z/2. Our agent checks a pack against 6,923 indexed alerts from the official portal, Jan 2019 to Sep 2026.

**2. Agent mode: Thought, Action, Observation (3 min).** Next to the check button, set the planner control to **Agent** (it is greyed out when Ollama is off). Click **Try a demo pack** and choose **03** (the misread batch).
- Point at the **Thinking** panel. Each decision shows three rows: **Thought** (the model's reasoning, streamed live from the local qwen2.5:3b model, no internet API), **Action** (the tool it chose, for example `search_variants`) and **Observation** (what the tool found). Then the loop repeats. Explain: the model chooses the tool, but the rules decide which tools it may choose, so it cannot skip a search or the confirmation question.
- Point at the **agent badges** on each step (perception, investigator, verifier, supervisor) and the **hand-off** rows between them, for example perception handing the fields to the investigator, and the investigator handing a draft to the verifier. Each agent has one job.
- If a **self-check** row appears (the verifier rejected the draft and the planner revises it once), point at it: the agent corrects itself once, and if that does not help it answers "More evidence is needed". It does not always appear, so do not wait for it.
- The agent then **asks a question**: "Which batch is printed on your pack: LM24088 or LM2408B?", with the reason it is asking. It never raises an alarm from a machine reading alone; a person must confirm the doubtful character.
- Choose **LM2408B**. The result says the batch is on an alert list. Point out that it is labelled as a synthetic demonstration, because demo packs never touch the real data.

**3. A real listed batch from a photo (2 min).** Upload `data\samples\pack_types\misread_FLAGGED.png` (or the realistic image you generated from `data\samples\realistic_pack_prompt.md`).
- The agent reads the photo locally (RapidOCR), shows the cropped batch line, thinks, and asks you to confirm the look-alike character.
- Answer with what is printed. The result is FLAGGED with a citation to the CDSCO list month and a link to the source.

**4. Vision fallback when OCR cannot read the batch (3 min).** Upload `data\samples\pack_types\unreadable_test.png`. Its batch number is blurred, so OCR reads only the words "Batch No".
- The agent calls **read_with_vision**: the local vision model (qwen2.5vl:3b) looks at the cropped batch line. Say that it is slow on this laptop's CPU (2 to 6 seconds per crop), and that you ran it once before the demo.
- It then asks a **yes/no question** with the crop beside it: "Is this the batch printed on your pack?" and the reading it found. Explain: a vision model can be wrong, so its reading is never used alone. In our live test it read `AYA2107` with 0.95 stated confidence when the pack says `AYA2101`.
- Answer **Yes**. The agent still runs its look-alike search and asks the **look-alike question** (which of `AYA2107` and `AYA-2101` is printed). Choose the one on the pack. The result is FLAGGED with its citation. This is the point of the design: the confirmation and the look-alike question caught the wrong digit.
- Optional: run it again and answer **No**. Only then does the agent ask you to type the batch.

**5. Safety behaviour (1 min).** Click **New check**, type a batch that is not on the lists (for example `QX7781`) and check it. The result is "No matching alert found". Point out the careful wording: it says the batch is not on the lists loaded, it never says the medicine is safe, and it is never shown in green.

**6. Failsafe (optional, 1 min).** Set the planner control to **Rules** and run demo pack 03 again: the same result comes from the rules alone. Every model call has a time limit and a rule fallback, so a check completes with Ollama off and without internet. If the vision model is off or times out, the agent skips it and asks you to type the batch.

**7. The autonomous monitor (optional, 1 min).** While the server runs, open `http://127.0.0.1:8000/api/monitor` in the laptop browser. It shows when the background monitor last ran, when it runs next, the number of failures and the last cycle: whether a sync was needed, how many new alerts, how many saved packs it re-checked and how many notifications it made. Explain: the monitor runs by itself every 6 hours, and a failure never affects a check. `python cli.py monitor --once` runs one cycle on demand.

**8. Evidence (optional).** Show `docs/guide/index.html` (visual guide), the report PDF, and `docs/trace/` (Phoenix trace screenshots of a full check).

## If something goes wrong
| Problem | Fix |
|---|---|
| "The tunnel did not report a public address" | The internet connection blocks Cloudflare. Switch to a phone hotspot and start again. |
| No internet at all | Run `.\.venv\Scripts\python.exe cli.py serve` and open http://127.0.0.1:8000 on the laptop and project it. Everything works offline; only the phone link needs internet. |
| The phone shows "Pair this device" | Open the full link including `?k=...`, or scan the QR code again. |
| The Agent or Hybrid planner choice is greyed out | Ollama is not running. Start it (`ollama serve`) and reload the page, or demo with the rules: results are the same. |
| The first thought is slow (over 10 s) | The model was still loading. Run the demo pack once before the professor arrives. Agent mode takes about 8 s per check on this laptop, against about 1.4 s for rules. |
| The vision step is slow or skipped | The vision model runs on the CPU (2 to 6 s per crop) and is skipped after a 30 s timeout. Run the unreadable test image once before the demo, and check that `qwen2.5vl:3b` is installed (`ollama list`). The agent then asks you to type the batch instead. |
| "Run the one-time Windows setup" | Follow the setup section of `README.md`. |
| A photo gives "No matching alert found" for a demo pack image | Expected: demo packs use invented batches that are not in the real alert data. Use "Try a demo pack" instead. |

## After the demo
Press Ctrl-C in the window (or close it). The site and the tunnel stop and the link no longer works.
