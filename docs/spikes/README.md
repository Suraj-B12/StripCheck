# Design-phase spikes (verified reference code, not the app)

These folders hold small, tested pieces written during the design phase so the coding phase starts from verified code instead of re-deriving it. They are not imported by the app.

## `v2_matching/`
`core/textutils.py` and `core/matching.py` are spec v1.1 Appendix A1/A2 with exactly the v2 Appendix A amendments applied (label regexes that ignore words like "Lotion"/"Batchwise", label and value on separate lines, `DD/MM/YY` dates, release-descriptor stop words, brand evidence, date-conflict handling for exact/confirmed batches only, noisy-channel variant ranking with a lookup cap).

Verified 25 Oct 2026 with Python 3.11.9 and rapidfuzz 3.14.6:
```
cd docs/spikes/v2_matching
python -m pytest -q        # 12 passed: v1.1 A3 tests copied verbatim (incl. the 7 matching scenarios) + v2 tests
```
M3 copies these two modules into `core/` (constants move to `core/config.py`) and the two test files into `tests/`.

## `data_analysis/`
- `snapshot_cdsco.py`: the polite one-off snapshot of the SUGAM portal JSON (one request per 1.5 s).
- `analyze_snapshot.py`: the exploratory statistics quoted in `research_notes/StripCheck engineering scan/cdsco_data_sources.md`.
- `analysis_output.txt`: its output on the 25 Oct 2026 snapshot (7,005 rows, Jan 2019 to Sep 2026).

M1 reimplements both properly (`core/portal.py`, `core/analysis.py`, reading from the database) and regenerates every number for the paper.
