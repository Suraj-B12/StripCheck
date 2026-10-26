# Decisions and spec deviations

*Numbered, dated, never deleted. A later decision that replaces an earlier one says "supersedes Dn", and the earlier one gets "superseded by Dm". Every spec change and every deviation from the spec gets an entry here in the same commit.*

| ID | Date | Decision | Why | Where |
|---|---|---|---|---|
| D1 | 2026-10-25 | CDSCO's SUGAM portal JSON (Jan 2019 onward) is the primary data source; legacy PDFs are secondary (provenance crops, PDF-parsing accuracy check). | The portal's own JavaScript calls plain JSON endpoints; v1.1 would have stopped at June 2025. | spec v2 §0 C1-C2, §3 |
| D2 | 2026-10-25 | Streamlit replaced by FastAPI + React (Vite, TypeScript) with server-sent events; usable from a phone on the LAN. | Streaming plus human-in-the-loop questions fight Streamlit's rerun model; the owner asked for a distinctive UI. | spec v2 §0 C3, §13, §14 |
| D3 | 2026-10-25 | Confirm-before-alarm gate: FLAGGED or SUSPECTED_FAKE needs the batch from a QR code, the user, or two agreeing independent reads. | A confident misread can land exactly on a listed sibling batch (58 same-maker sibling keys in the data). | spec v2 §0 C4, §10.4, §10.7 R2 |
| D4 | 2026-10-26 | `confirm_batch` asks the person to type the two characters most likely to be misread; no yes/no button. Refines D3. | People habituate to yes/no confirmations and tap without looking (survey theme T15). | spec v2 §10.4; ui_direction §4.3 |
| D5 | 2026-10-25 | Brand corroboration; a one-digit date difference on an exact or confirmed batch is asked, a larger one is a conflict that leads to CANT_VERIFY; variant siblings with different dates are rejected. | The portal now has a brand field; one typo or misread must not silently reject a true match. | spec v2 §10.5, Appendix A2 |
| D6 | 2026-10-25 | Noisy-channel ranking of variants from calibration and user-confirmation counts; the prior never skips the question. | Defensible model; sibling batches make silent correction unsafe. | spec v2 §10.6 |
| D7 | 2026-10-25 | Optional local vision-language second reader, used only for agreement. | Only an independent model family can catch confident OCR misreads automatically. | spec v2 §9 |
| D8 | 2026-10-25 | `MAX_STEPS` 12 -> 16; typed corrections reject the read key; reader disagreement becomes a character question; the drafter applies the batch gate; fields carry a version. | Tracing all 11 demo scenarios through the planner (the unreadable pack needs 14 steps). | spec v2 §6, §10.4 |
| D9 | 2026-10-26 | Python 3.12; OpenCV < 5; RapidOCR `ocr_version` pinned; FastAPI native SSE; LangGraph >= 1.2.16; MCP 2.x API; Phoenix server in its own venv. | Tech scan of 26 Oct 2026 (numpy 2.5 and scipy 1.18 have no cp311 wheels; RapidOCR default changed to PP-OCRv6). | spec v2 §5.1 |
| D10 | 2026-10-25 | `SUSPECTED_FAKE` has two wordings: the labelled maker denies the batch, or the testing laboratory declared it spurious. | Both kinds appear in the portal data. | spec v2 §10.9 |
| D11 | 2026-10-25 | NOT_LISTED is never green; user-facing verdict text only from templates; banned phrases enforced by tests. | Risk-communication evidence; spec v1.1 safety rules. | ui_direction §3, spec v2 §10.9 |
| D12 | 2026-10-26 | Evaluation adds predictive value at realistic base rates (1%, 0.1%), OCR confidence calibration on batch codes, and blocking recall of the variant search. | Test sets are 30% listed; a person's shelf is almost all unlisted (survey §9). | spec v2 §15.8, paper §V |
| D13 | 2026-10-26 | Paper claims the combination plus durable measurements, crediting prior tools (Nazar, SafeDose, RecallOps India, Blacklisted). | The survey found these tools already cover parts of the design. | paper §I-II |
| D14 | 2026-10-27 | CDSCO data never enters git; each machine fetches its own copy; test fixtures are synthetic. | CDSCO copyright policy. | `docs/COLLABORATION.md` §8 |
| D15 | 2026-10-27 | Two machines, one `main` branch, no force-push; Builder implements, Integrator runs models, data, evaluation and paper. | Owner's working arrangement. | `docs/COLLABORATION.md` |

## Pending (owner decisions)

- **P1 · Ollama upgrade** from 0.17.7 to 0.40.x (unlocks qwen3.5, gemma4, glm-ocr for the M4 benchmark). Owner: Integrator.
- **P2 · Regional language** besides Hindi for verdict templates (Kannada assumed) and the native-speaker reviewer who signs off translations. Owner: Integrator.
- **P3 · Team names and institution** for the paper header. Owner: Integrator.
- **P4 · Freeze the preregistered decision rules** R-A, R-B and R-C (spec v2 §15.10) here, with a date, before the seed-7 evaluation run in M7. Owner: Integrator.
