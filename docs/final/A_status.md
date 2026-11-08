# Agent A status: Windows photo OCR

Resume point: read this checklist, then `git diff core/pack_tools.py requirements.txt`. Nothing committed (lead commits).

- [x] 1. requirements.txt: Windows/Linux OCR stack with `sys_platform != 'darwin'` markers (rapidocr pinned to 3.10.x because the pinned weight files ship with it)
- [x] 2. RapidOCR pinned (explicit model paths), logger silenced, engine created once in a long-lived worker process
- [x] 3. Demo packs rendered and checked (read_pack, CLI `check`, API upload); extraction bugs fixed
- [x] 4. tests/test_perception_windows.py (9 tests, ~10 s)
- [x] 5. Latency measured
- [x] 6. Full suite: 204 passed, 2 skipped, 1 failed (failure is outside A's files, see "Requests")

## What changed (core/pack_tools.py only; core/crops.py needed no change)
- **Pinned models.** `RAPID_MODELS` passes explicit `Det/Cls/Rec.model_path` for `PP-OCRv6_det_small.onnx`, `ch_ppocr_mobile_v2.0_cls_mobile.onnx`, `PP-OCRv6_rec_small.onnx` from the installed package (rapidocr 3.10.0). An explicit `model_path` skips RapidOCR's downloader. `Global.log_level=error` plus the `RapidOCR` logger set to ERROR. Engine label in results: `RapidOCR PP-OCRv6-small` (falls back to `RapidOCR (unpinned models)` only if those files are missing but other local weights exist; never downloads).
- **Engine once.** OCR used to start a new Python process per image (model load ~1.5 s every time). Now `_rapid_request` keeps one worker (`_rapid_serve`, JSON lines over stdin/stdout) behind a lock. Every request still has the deadline: on overrun the worker is killed and the read falls back to manual entry; a dead worker is restarted on the next image; `atexit` kills it, and it also exits when the parent's pipe closes.
- **Glued labels.** RapidOCR drops spaces between printed fields: `Mfg:08/2024Exp:07/2027`. `_clean_line` inserts a space before a field label that directly follows a digit (any label) or a letter (capitalised date or party labels only, so `Pilot:` never becomes a `Lot:` batch label). The label must be followed by `:` or `-`.
- **Bracketed notes.** `[obscured]`-style notes are removed before extraction, so they are never used as maker or product (were 2 errors on demo packs 05, 07, 11).
- **Enhanced re-read bug.** The enhanced (grayscale, autocontrast, sharpen) re-read only ran when the plain read returned some text. Faint print (#ebebeb on #f0f0f0) returns no text at all, so it was never retried. It now also runs when the plain read is empty, within the same 60 s deadline.
- **Barcodes.** zxing-cpp shows a raw GS1 FNC1 separator as `<GS>`; it is now mapped back to `\x1d` so the existing GS1 parser reads batch/expiry from such DataMatrix codes. The OpenCV QR fallback now catches `cv2.error` (e.g. unreadable file) too.
- Safety: no rule was loosened. Misread labels (`Batch Nc`, `Buach Neo`) still give no batch and the user is asked; an unlabelled barcode (`SYN2408B` alone) is not taken as a batch; QR/OCR disagreement still un-confirms the batch.

## OCR accuracy on the 11 demo packs (`python cli.py props --demo`, RapidOCR, Windows 11)
| field | before fixes | after fixes |
|---|---|---|
| batch | 11/11 | 11/11 |
| mfg | 11/11 | 11/11 |
| exp | 2/11 | 11/11 |
| maker | 9/11 | 11/11 |
| product | 9/11 | 11/11 |
Expected values are the case fields the prop was rendered from (empty for obscured fields). Packs 08 and 11 correctly end with "The batch label was not readable" and a question.

Degraded renders (Pillow, default font 40 px): faint text, blur 1.5, 30% scale all read `LM2408B`; faint #ebebeb now read via enhanced path; blur 4 to 5 and 12 to 15% scale misread the label, so no batch is proposed (by design).

Barcodes: GS1 QR, GS1 DataMatrix (HRI and raw FNC1), QR pasted on a demo pack all decode (~0.2 s); with zxing absent, OpenCV decodes QR (not DataMatrix).

## Latency (Windows 11 laptop, CPU onnxruntime)
- Worker cold start (model load) + first image: ~1.5 s + 0.35 s; warm OCR inference on a 1400x900 prop: ~0.34 s.
- `read_pack` per demo pack: before ~2.2 s (4.0 s when the enhanced re-read ran); now ~0.73 s warm (OCR + barcode subprocess ~0.2 s), ~1.1 to 1.2 s when the enhanced re-read runs, ~2.2 s for the very first image.
- API `POST /api/checks` with one photo (server on 8101, warm): ~1.0 s end to end. CLI `python cli.py check IMAGE`: ~2.4 s (includes Python start and cold model load).

## Requests for other owners
- **cli.py (lead):** `check IMAGE` with stdout piped but stdin a console raises `EOFError` at `input()` when a question is pending (packs 08, 11). Catch `EOFError` and stop asking (or check `sys.stdin.isatty()` and `sys.stdout.isatty()`).
- **tests/test_api_resilience.py (lead):** `test_malformed_origin_token_and_method_return_structured_errors` fails after commit 1563ef6 (token gate now reads `application.state.gate`, the test sets `isolated.state.lan = True`). Set `isolated.state.gate = True` in the test.
- **core/props.py (agent B):** the demo product line uses no "synthetic" word, good; `extract_fields` skips lines containing "synthetic"/"demonstration"/"fictional" as product candidates, so keep those words off the product line.
- **paper (agent D):** perception numbers above can go in the implementation/evaluation sections (engine `RapidOCR PP-OCRv6-small`, 11/11 fields on clean demo props, ~0.7 s per photo warm).
