"""Crop the Phoenix trace screenshot (R3 walkthrough, run 1) for the report.

Source: docs/trace/02_phoenix_run1_misread_trace.png (1600 x 1000, fictional prop 03 data).
Output: paper/report/figures/fig_phoenix_trace.png. Keeps the span tree and the input/output panel,
drops the Phoenix navigation sidebar and the trace list. Run from the repository root.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "docs" / "trace" / "02_phoenix_run1_misread_trace.png"
OUT = ROOT / "paper" / "report" / "figures" / "fig_phoenix_trace.png"
BOX = (400, 45, 1600, 1000)  # left, top, right, bottom in source pixels -> 1200 x 955

Image.open(SRC).convert("RGB").crop(BOX).save(OUT, optimize=True)
print("wrote", OUT.relative_to(ROOT))
