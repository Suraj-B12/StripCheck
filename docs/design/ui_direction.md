# StripCheck UI direction (v2)

*Design system and screen specs for the FastAPI + React web app that replaces the Streamlit UI of spec v1.1. Written 25 Oct 2026 during the design phase. Coding agents build against this file; change it here first if a decision changes.*

## 1. The subject, the audience, the single job

- **Subject.** A medicine strip or carton held up to a phone. Its world is aluminium blister foil, clear PVC pockets, perforations, inkjet batch codes ("B.No. SP240165 · Mfg. 06/2024 · Exp. 05/2026"), chemist counters, and CDSCO's monthly tables of failed samples.
- **Audience.** (1) A person in India checking a medicine they bought, usually on a phone, possibly reading in Hindi or a regional language. (2) A pharmacist doing a quick lookup. (3) Examiners watching a laptop demo on a projector. (4) The team, reading traces and evaluation results.
- **The single job of the main screen.** Read one pack and say, with evidence, whether its batch is on an official list of failed or suspected-spurious samples, or that the app could not tell.

## 2. Design thesis

The product's whole difficulty is that a camera can be confidently wrong about one character (a scuffed `B` read as `3`). So the interface shows the batch number as the thing being worked on: a strip of character cells, like pills in a blister pack, that the agent inspects one at a time and that a person can confirm with their own eyes. Everything else stays quiet, clinical and legible.

**Signature element: the batch strip.** The batch number is set in a foil band of rounded "pockets", one character per pocket, separated by perforation marks. Cells the agent doubts show their confusable alternatives. When the agent asks a question, the doubted cell lifts out of the strip and the real camera pixels of that glyph appear beside it, enlarged. A confirmed cell settles back with a tick. This is the one bold element; nothing else competes with it.

**The deliberate risk, and why it is justified.** Skeuomorphic foil is unfashionable. Here it is functional: it puts character-level uncertainty, the core agentic behaviour, on screen in a form anyone who has held a medicine strip understands.

## 3. Tokens

### Colour (light theme, default)

| Token | Hex | Use |
|---|---|---|
| `--paper` | `#F4F5F7` | page background (cool, not cream) |
| `--card` | `#FFFFFF` | panels, slips |
| `--ink` | `#14171C` | primary text |
| `--ink-2` | `#4B5462` | secondary text |
| `--ink-3` | `#7B8494` | captions, inactive |
| `--rule` | `#DCDFE5` | hairlines, borders |
| `--foil-hi` | `#F7F8FA` | strip highlight |
| `--foil` | `#E3E7EC` | strip band |
| `--foil-mid` | `#C5CBD3` | perforations, pocket edges |
| `--foil-lo` | `#9EA6B1` | pocket shadow |
| `--pen` | `#22389E` | the accent: links, focus, primary buttons. Ballpoint-pen blue, the colour of a chemist's handwriting on an Indian bill |
| `--pen-hover` | `#1B2D80` | |
| `--pen-soft` | `#E7EAF8` | selected rows, focus halos |

Verdict colours carry meaning and are never used decoratively:

| Verdict | Ink | Soft background | Extra cue for colour-blind users |
|---|---|---|---|
| `FLAGGED` (NSQ) | `#B4232A` | `#FBEAEA` | solid 6 px rule |
| `SUSPECTED_FAKE` (spurious) | `#6E1631` | `#F5E4EA` | diagonal hatch on the rule |
| `NOT_LISTED` | `#3A4A5C` | `#E9EDF2` | hollow rule (outline only) |
| `CANT_VERIFY` | `#9A5B13` | `#FBF0E0` | dashed rule |

**No green anywhere in a verdict.** Green reads as "safe", and StripCheck must never imply that a medicine is safe (spec §9.8). `NOT_LISTED` is a neutral slate: it reports the absence of a listing, nothing more. This choice is argued in the paper's risk-communication discussion.

Dark theme (projector-hostile, so not the default): `--paper #0F1216`, `--card #161A20`, `--ink #E8EBF0`, `--ink-2 #AEB6C2`, `--ink-3 #7D8694`, `--rule #262C35`, foil becomes gunmetal (`#2B3139 / #3A414B / #4C5562`), `--pen #8EA2F0`, verdict inks lightened to keep 4.5:1 on `--card`.

Every text/background pair must pass WCAG 2.2 AA (4.5:1 body, 3:1 large text and UI glyphs). A test in `web/` checks the token pairs.

### Type

| Role | Family | Why |
|---|---|---|
| Display | **Archivo** (variable, width 82, weight 760 for verdicts, 680 for page titles) | a semi-condensed grotesque with the punch of a pharma carton's brand line; used only for verdict headlines and page titles |
| Body | **Atkinson Hyperlegible Next** | designed for low-vision readers so that look-alike characters stay distinct |
| Data | **Atkinson Hyperlegible Mono** | every batch number, date, row reference and code. It was drawn so `0/O`, `1/I/l` and `B/8` cannot be mistaken, which are exactly the confusions this agent fights |
| Hindi / Kannada | **Noto Sans Devanagari**, **Noto Sans Kannada** | verdict templates in Indian languages |

All fonts are self-hosted from `@fontsource` packages and bundled by Vite: the demo runs with no internet.

Scale (ratio about 1.2, base 16 px on phones, 17 px from 1024 px): 12.5, 14, 16, 19, 23, 28, 34, 41, 49. Body line height 1.5; headings 1.1; batch strip characters 28 px (phone 24 px), weight 600, tracking 0.

### Space, shape, depth

- 4 px grid. Phone side gutter 16 px; desktop content max 1240 px.
- Radius: cards 10 px; buttons 8 px; strip pockets 10 px; chips 999 px.
- Depth only where the physical metaphor needs it (the strip). Cards are flat with a 1 px `--rule` border; no drop shadows elsewhere.

### Icons

Phosphor icons (regular weight), self-hosted. Five nav glyphs: camera (Check), list (Alert lists), first-aid box (Cabinet), chart (Evaluation), path (Traces). No emoji anywhere.

## 4. Components

### 4.1 Batch strip (`<BatchStrip>`)
- Props: `chars: {ch, state, alts, cropUrl?}[]`, `source: 'qr'|'ocr'|'vlm'|'user'|'carton'`, `mode: 'display'|'ask'|'edit'`, `askIndex?`.
- States per cell: `read`, `confusable` (shows alternatives in `--ink-3` beneath, e.g. `8 B`), `asked` (lifts 6 px, `--pen` ring, glyph crop callout), `confirmed` (tick under the cell), `conflict` (verdict-red underline).
- Source tag at the strip's left edge in mono caps: `QR`, `OCR`, `OCR+VLM`, `YOU`.
- Edit mode: tap a cell to retype it; the strip offers "Check with this batch".
- Motion: during variant search, confusable cells flick through their alternatives twice (split-flap, 120 ms per glyph). With `prefers-reduced-motion`, alternatives appear statically.
- The glyph crop is the real photo pixels, scaled 4x with `image-rendering: pixelated`, so a person judges the evidence, not a redrawing of it.

### 4.2 Reasoning timeline (`<StepTimeline>`)
- One row per planner decision and tool result, streamed over SSE. Step numbers are shown because the agent's steps are a real, bounded sequence ("step 4 of at most 12").
- Row: step number (mono) · action (mono, e.g. `search_variants`) · source badge (`rules`, `LLM`, `LLM→rules fallback`) · the planner's one-line reason · the tool's result summary · duration (mono, right-aligned). Expand for raw JSON.
- `aria-live="polite"` region announces each new step for screen readers.

### 4.3 Question card (`<AskCard>`)
Built from the interrupt payload, never from free text:
- `confirm_char`: "Look at the 2nd character of the batch on your strip." Glyph crop + the listed and read characters as large buttons ("It's B" / "It's 3") + "Can't tell". If the learned prior applies, one line: "OCR has misread B as 3 twice before."
- `confirm_batch` (new in v2, spec §10.4): "Before we show this result, look at the batch on your strip. Type its 4th and 7th characters." Batch-line crop + two one-character mono inputs (the positions the confusion model rates most likely to be misread) + "Type the whole batch instead" / "Can't tell". No yes/no button: people habituate to those and tap without looking.
- `box_photo`: "Photograph the carton. Its batch and dates are usually printed more clearly." Camera / upload / "Skip".
- `type_batch`: a mono input that renders into strip cells as you type, "Check this batch" / "Skip".
- `confirm_field` (dates, new in v2): "Your strip's expiry reads 08/2026; CDSCO lists 06/2026. Which is printed?"
- Keyboard: options are 1/2/3; Enter submits. Phone: the card is a bottom sheet with 48 px targets.

### 4.4 Verdict slip (`<VerdictSlip>`)
```
┃ ON A CDSCO LIST OF FAILED SAMPLES                    (Archivo 760, verdict ink)
┃ Batch BBT2305 · Paracetamol Tablets IP 650 mg (Demo-650)
┃ Failed: Dissolution · Tested by CDL Kolkata · March 2025 list
┃
┃ Show this pack to your pharmacist. Do not stop any prescribed
┃ medicine without medical advice.                      (template text, §9.8)
┃
┃ Batch ◐ you confirmed   Product ● match   Dates ● match   Maker ● match
┃ Source  CDSCO NSQ portal · MAR-2025 · row 23            View record
┃ [Save to cabinet]  [Read aloud]  [हिन्दी]  [See reasoning]
```
Headlines (user-facing words for the four labels):

| Label | Headline | Sub-line |
|---|---|---|
| `FLAGGED` | On a CDSCO list of failed samples | Not of Standard Quality · {Month YYYY} · {failed test} |
| `SUSPECTED_FAKE` | Listed by CDSCO as possibly spurious | The named maker says it did not make this batch · {Month YYYY} |
| `NOT_LISTED` | Not on the CDSCO lists we have | Lists loaded up to {Mon YYYY} · this does not certify the medicine |
| `CANT_VERIFY` | Couldn't verify this pack | {reason} |

Explanations are always the verified templates from spec §9.8 (and their reviewed Hindi/Kannada translations); the LLM never writes user-facing verdict text.

### 4.5 Data freshness chip
Always visible in the header: `Lists to Sep 2026 · 14,2xx entries`. It turns amber when the newest list is more than 45 days old, because a stale index silently weakens `NOT_LISTED`.

### 4.6 Phone pairing
Header button "Use your phone": shows a QR code of the laptop's LAN address (served by `/api/lan/qr.png`). The phone opens the same app and uses its own camera through `<input type="file" accept="image/*" capture="environment">`, which works over plain HTTP on a LAN.

## 5. Screens

### 5.1 Check (default)
Desktop, at least 1024 px:
```
┌ rail ┬──────────────────────────────────────────────────────────────────┐
│ ◉    │ Check a pack                           Lists to Sep 2026 · 14,2xx │
│ ☰    ├──────────────────────────┬───────────────────────────────────────┤
│ ✚    │ PACK                     │ REASONING                              │
│ ▤    │ ┌──────────────────────┐ │ 1  read_qr          rules   no QR found│
│ ⌁    │ │ photo + OCR boxes    │ │ 2  read_text        rules   9 lines    │
│      │ └──────────────────────┘ │ 3  extract_fields   rules   B3T2305    │
│      │ OCR [B][3][T][2][3][0][5]│ 4  search_exact     rules   0 entries  │
│      │         8 B              │ 5  search_variants  LLM  "the 3 may be │
│      │ Product  Demo-650 …      │       a scuffed B" → 1 entry BBT2305   │
│      │ Mfg 01/2025  Exp 12/2027 │ 6  grade            rules  needs char  │
│      │ Maker Demo Remedies      │ ┌ ask ───────────────────────────────┐ │
│      │                          │ │ Look at the 2nd character …        │ │
│      │                          │ └────────────────────────────────────┘ │
└──────┴──────────────────────────┴───────────────────────────────────────┘
```
When the run finishes, the verdict slip takes the top of the right column and the timeline collapses under "See reasoning".

Phone: single column: capture → strip → fields → (timeline collapsed to the current step) → ask sheet → verdict slip. Bottom tab bar: Check · Lists · Cabinet · More.

Empty state: "Photograph the strip so the batch number is sharp. Tilt it away from the light to avoid glare." Buttons: "Take photo", "Upload", "Type a batch instead". A "Demo packs" drawer (for examiners) lists the generated props with their expected outcome hidden until run.

### 5.2 Alert lists
- One summary line, not a stats hero: entries, months covered, latest month, spurious count, last sync.
- "Sync with CDSCO" runs the supervisor; a live log streams the ingest report (per source: found / valid / flagged / repaired / quarantined, completeness).
- Table: month, level, product (brand), batch (mono), maker, failed test, lab/state. Search by batch (confusion-aware: typing `B3T2305` also surfaces `BBT2305`, labelled "1 character differs") or product.
- Tabs: Entries · Quarantine (row, reasons, raw text) · Data quality (flag counts).

### 5.3 Cabinet
- Saved medicines as rows with a mini batch strip, the last verdict chip, last checked date and an expiry countdown.
- Notifications on top: "Batch SP240165 (Pantoshang-40) in your cabinet now appears on the Sep 2026 list."
- "Re-check all now".

### 5.4 Evaluation
- The preregistered A/B decision rule and whether it was met, in one sentence.
- Tables with 95% Wilson intervals; McNemar p-values vs the baseline; ablation table; robustness curves (hit recall and false-alarm rate vs degradation severity); latency distribution. Charts follow the `dataviz` skill; verdict colours are reused for verdict series only.

### 5.5 Traces
- List of checks (time, verdict, steps, asks, seconds, planner mode). Opening one shows the step timeline with a timing waterfall, the evidence ledger, and a link to Phoenix when it is running.

## 6. Writing rules for the interface

- Name things by what people see and do: "batch number", "the strip", "your pharmacist", not "entity", "pipeline" or "inference".
- Buttons say what happens: "Check this pack", "Save to cabinet", "Sync with CDSCO". The result toast repeats the verb: "Saved to cabinet".
- Errors say what happened and what to do: "Ollama isn't running, so the planner is using rules only. Checks still work." Never apologise, never vague.
- Never: "safe", "genuine", "authentic", "fake medicine", "stop taking". Never praise ("Great photo!"). No exclamation marks, no emoji.
- Sentence case everywhere except mono codes and the four internal labels in developer views.

## 7. Quality floor

Responsive from 360 px; visible 3 px `--pen` focus ring with 2 px offset; all actions keyboard-operable; `prefers-reduced-motion` respected; `lang` set on Hindi/Kannada spans; tap targets of at least 44 px; no layout shift when steps stream in (reserve row height); works offline (no CDN, fonts bundled).

## 8. Self-critique log

- Rejected: a green "all clear" state (implies safety); a big-number stats hero on Alert lists (template look); a rubber-stamp verdict (would imitate an official CDSCO mark, which a third-party tool must not do).
- Kept to one bold element: the batch strip. The verdict slip is flat with a single coloured rule.
- Open question for the team: which regional language besides Hindi to ship first (Kannada assumed until the team says otherwise).
