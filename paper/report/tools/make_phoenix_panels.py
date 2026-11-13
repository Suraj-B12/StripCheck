"""Readable crops of the Phoenix screenshots (R3 walkthrough of 8 Nov 2026) for the report.

Sources (fictional prop 03 data, 1600 x 1000 px each):
  docs/trace/02_phoenix_run1_misread_trace.png, docs/trace/01_phoenix_trace_list.png
Outputs in paper/report/figures/:
  fig_phoenix_tree.png  span tree of run 1 split into two columns (Figure 7.1)
  fig_phoenix_io.png    root span input and output panes of run 1 (Appendix C)
  fig_phoenix_list.png  trace list of the project without the sidebar (Appendix C)
Only crops and pastes; no pixel is redrawn. Run from the repository root.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
TRACE = ROOT / "docs" / "trace"
FIG = ROOT / "paper" / "report" / "figures"


def main():
    run1 = Image.open(TRACE / "02_phoenix_run1_misread_trace.png").convert("RGB")
    header = run1.crop((402, 95, 750, 160))      # status, total cost, trace latency
    left = run1.crop((402, 208, 750, 608))       # check .. search_variants (planner_llm 4.5s)
    right = run1.crop((402, 608, 750, 1000))     # grade .. ask_user (planner_llm 3.8s), check.resume
    gap = 16
    w = left.width
    h = header.height + left.height
    bg = run1.getpixel((420, 990))
    tree = Image.new("RGB", (2 * w + gap, h), (255, 255, 255))
    col = Image.new("RGB", (w, h), bg)
    col.paste(header, (0, 0))
    col.paste(left, (0, header.height))
    tree.paste(col, (0, 0))
    col2 = Image.new("RGB", (w, h), bg)
    col2.paste(right, (0, 0))
    tree.paste(col2, (w + gap, 0))
    tree.save(FIG / "fig_phoenix_tree.png", optimize=True)
    run1.crop((776, 160, 1578, 850)).save(FIG / "fig_phoenix_io.png", optimize=True)
    lst = Image.open(TRACE / "01_phoenix_trace_list.png").convert("RGB")
    lst.crop((262, 48, 1150, 615)).save(FIG / "fig_phoenix_list.png", optimize=True)
    print("tree", tree.size, "header", header.height)


if __name__ == "__main__":
    main()
