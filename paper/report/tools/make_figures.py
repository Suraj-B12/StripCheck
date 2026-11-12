"""Data figures for the StripCheck report (vector PDF + CSV per figure).

Run from the repository root:
    .venv\\Scripts\\python.exe paper\\report\\tools\\make_figures.py

Sources (read only): the local SQLite database (core.config.DB_PATH), runs/eval_seed7_latest.json,
git show e283407:docs/results/eval_seed7.md (run 1), paper/report/data/eval_seed1.json (seed 1 run
in a clean clone). Every number plotted is also written to the CSV beside the PDF.
"""
import csv
import json
import math
import re
import sqlite3
import statistics
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

REPORT = Path(__file__).resolve().parents[1]
ROOT = REPORT.parents[1]
FIG = REPORT / "figures"
DATA = REPORT / "data"
sys.path.insert(0, str(ROOT))

ARMS = ["baseline", "agent_rules", "agent_hybrid"]
ARM_LABEL = {"baseline": "Baseline (lookup)", "agent_rules": "Agent (rules)", "agent_hybrid": "Agent (hybrid)"}
ARM_COLOR = {"baseline": "#7F7F7F", "agent_rules": "#0072B2", "agent_hybrid": "#E69F00"}
EXTRA = "#009E73"
NEUTRAL = "#4D4D4D"
SCENARIOS = ["clean", "glare", "qr", "misread", "spurious", "genuine", "collision", "sibling"]
SCEN_LABEL = {"clean": "Clean", "glare": "Glare", "qr": "QR code", "misread": "Misread",
              "spurious": "Spurious", "genuine": "Not listed", "collision": "Collision", "sibling": "Sibling"}
FULL, HALF = 6.0, 3.0
summary_lines = []


def setup_style():
    for name in ("cmunrm.otf", "cmunbx.otf", "cmunti.otf"):
        try:
            path = subprocess.run(["kpsewhich", name], capture_output=True, text=True, timeout=20).stdout.strip()
            if path:
                font_manager.fontManager.addfont(path)
        except (OSError, subprocess.SubprocessError):
            pass
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["CMU Serif", "DejaVu Serif"], "mathtext.fontset": "cm",
        "font.size": 11, "axes.labelsize": 11, "xtick.labelsize": 10, "ytick.labelsize": 10,
        "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.8, "axes.edgecolor": "#333333", "axes.axisbelow": True,
        "axes.unicode_minus": False, "pdf.fonttype": 3, "savefig.bbox": "standard",
        "figure.constrained_layout.use": True, "hatch.linewidth": 0.8, "legend.frameon": False})


def hgrid(ax):
    ax.yaxis.grid(True, color="#D9D9D9", linewidth=0.6)
    ax.xaxis.grid(False)


def vgrid(ax):
    ax.xaxis.grid(True, color="#D9D9D9", linewidth=0.6)
    ax.yaxis.grid(False)


def wilson(k, n, z=1.959964):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def save(fig, name, header, rows, note):
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)
    with open(FIG / f"{name}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    summary_lines.append(f"{name}.pdf: {note}")


def label_kn(k, n):
    return f"{k}/{n}"


def zero_mark(ax, x, width, color, horizontal=False):
    """A short coloured stroke on the axis so a bar of height 0 still shows which arm it is."""
    if horizontal:
        ax.plot([0, 0], [x - width / 2, x + width / 2], color=color, linewidth=3.0, solid_capstyle="butt", zorder=4, clip_on=False)
    else:
        ax.plot([x - width / 2, x + width / 2], [0, 0], color=color, linewidth=3.0, solid_capstyle="butt", zorder=4, clip_on=False)


# ---------------------------------------------------------------- data loading

def db_rows():
    from core import config
    con = sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)
    rows = con.execute("SELECT list_kind, list_month, mfg, exp FROM alerts WHERE removed_at IS NULL").fetchall()
    con.close()
    return rows


def ym(s):
    if s and re.fullmatch(r"\d{4}-\d{2}", s):
        return int(s[:4]) * 12 + int(s[5:7]) - 1
    return None


def load_eval(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run1_tables():
    """Parse run 1 (commit e283407) Table A and Table C from the markdown kept in git."""
    text = subprocess.run(["git", "show", "e283407:docs/results/eval_seed7.md"], cwd=ROOT,
                          capture_output=True, text=True, encoding="utf-8", timeout=60, check=True).stdout
    sections = re.split(r"^## ", text, flags=re.M)
    out = {}
    for sec in sections:
        title = sec.splitlines()[0] if sec else ""
        key = None
        if title.startswith("Table A") and "oracle" in title:
            key = "A_oracle"
        elif title.startswith("Table B"):
            key = "A_none"
        elif title.startswith("Table C") and "oracle" in title:
            key = "C_oracle"
        if not key:
            continue
        table = {}
        for line in sec.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 4 and not cells[0].startswith("---") and cells[0] not in ("Metric", "Scenario"):
                table[cells[0]] = dict(zip(ARMS, cells[1:]))
        out[key] = table
    return out


def kn_from_cell(cell):
    m = re.search(r"(\d+)/(\d+)", cell)
    return int(m.group(1)), int(m.group(2))


# ---------------------------------------------------------------- figures

def fig_alerts_per_year(rows):
    years = list(range(2019, 2027))
    counts = {y: 0 for y in years}
    kinds = {y: {"nsq": 0, "spurious": 0} for y in years}
    for kind, month, _, _ in rows:
        y = int(month[:4])
        counts[y] += 1
        kinds[y][kind] = kinds[y].get(kind, 0) + 1
    last_month = max(r[1] for r in rows)
    fig, ax = plt.subplots(figsize=(FULL, 2.9))
    xs = range(len(years))
    vals = [counts[y] for y in years]
    bars = ax.bar(xs, vals, width=0.68, color=NEUTRAL)
    bars[-1].set_facecolor("white")
    bars[-1].set_edgecolor(NEUTRAL)
    bars[-1].set_hatch("////")
    for x, v in zip(xs, vals):
        ax.text(x, v + 35, f"{v:,}", ha="center", va="bottom", fontsize=10)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([str(y) if y < 2026 else "2026\n(Jan to Sep)" for y in years])
    ax.set_ylabel("Alerts listed (count)")
    ax.set_xlabel("Year of the alert list month")
    ax.set_ylim(0, 2250)
    ax.set_yticks(range(0, 2001, 500))
    hgrid(ax)
    total = sum(vals)
    save(fig, "fig_alerts_per_year", ["year", "alerts", "nsq", "spurious"],
         [[y, counts[y], kinds[y]["nsq"], kinds[y]["spurious"]] for y in years],
         f"{total} indexed alerts (removed_at IS NULL); per year {vals}; last list month {last_month}")
    return dict(total=total, counts=counts, last_month=last_month)


def fig_alert_timing(rows):
    lag, rem = [], []
    for _, month, mfg, exp in rows:
        if ym(mfg) is not None:
            lag.append(ym(month) - ym(mfg))
        if ym(exp) is not None:
            rem.append(ym(exp) - ym(month))
    n_all = len(rows)
    fig, axes = plt.subplots(1, 2, figsize=(FULL, 2.9), sharey=False)
    specs = [
        (axes[0], lag, list(range(0, 61, 3)), "Months from manufacture\nto alert list month", "lag"),
        (axes[1], rem, list(range(-12, 61, 3)), "Months of shelf life left\nat the alert list month", "rem"),
    ]
    csv_rows = []
    info = {}
    for ax, vals, bins, xlabel, key in specs:
        lo, hi = bins[0], bins[-1]
        shown = [v for v in vals if lo <= v < hi]
        below = sum(1 for v in vals if v < lo)
        above = sum(1 for v in vals if v >= hi)
        color = NEUTRAL if key == "lag" else EXTRA
        counts, edges, _ = ax.hist(shown, bins=bins, color=color, edgecolor="white", linewidth=0.6)
        med = statistics.median(vals)
        ymax = max(counts)
        ax.axvline(med, color="#D55E00", linewidth=1.4, linestyle="--")
        ax.text(med + 1.2, ymax * 1.04, f"median {med:g}", color="#D55E00", fontsize=10, va="bottom", ha="left")
        if key == "rem":
            ax.axvline(0, color="#333333", linewidth=0.8)
        ax.set_ylim(0, ymax * 1.22)
        ax.set_xlim(lo, hi)
        ax.set_xticks(list(range(lo, hi + 1, 12)))
        ax.set_xlabel(xlabel)
        hgrid(ax)
        q = lambda p: sorted(vals)[int(p * (len(vals) - 1))]
        info[key] = dict(n=len(vals), excluded_no_date=n_all - len(vals), median=med, q1=q(.25), q3=q(.75),
                         below=below, above=above, min=min(vals), max=max(vals))
        for a, b, c in zip(edges[:-1], edges[1:], counts):
            csv_rows.append([key, int(a), int(b), int(c)])
    axes[0].set_ylabel("Alerts (count)")
    save(fig, "fig_alert_timing", ["series", "bin_from_month", "bin_to_month_exclusive", "alerts"], csv_rows,
         f"lag {info['lag']}; remaining {info['rem']}")
    return info


def fig_headline(ev):
    metrics = [("hit_recall", "Hit recall\n(listed packs)"),
               ("far_all", "False-alarm rate\n(all not-listed packs)"),
               ("far_collision", "False-alarm rate\n(collision packs)")]
    res = ev["results"]["oracle"]
    fig, ax = plt.subplots(figsize=(FULL, 3.4))
    width = 0.26
    rows = []
    for j, arm in enumerate(ARMS):
        s = res[arm]["summary"]
        for i, (m, _) in enumerate(metrics):
            k, n = s[m]["k"], s[m]["n"]
            lo, hi = wilson(k, n)
            assert abs(lo - s[m]["ci"][0]) < 1e-3 and abs(hi - s[m]["ci"][1]) < 1e-3, (arm, m)
            x = i + (j - 1) * width
            r = k / n
            ax.bar(x, r, width=width * 0.92, color=ARM_COLOR[arm], zorder=2)
            if k == 0:
                zero_mark(ax, x, width * 0.92, ARM_COLOR[arm])
            ax.errorbar(x, r, yerr=[[r - lo], [hi - r]], fmt="none", ecolor="#222222", elinewidth=0.9, capsize=2.5, zorder=3)
            ax.text(x, hi + 0.025, label_kn(k, n), ha="center", va="bottom", fontsize=9.5)
            rows.append([arm, m, k, n, round(r, 4), round(lo, 4), round(hi, 4)])
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels([m[1] for m in metrics])
    ax.set_ylabel("Proportion of packs")
    ax.set_ylim(0, 1.18)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlim(-0.55, 2.55)
    hgrid(ax)
    fig.legend(handles=[Patch(color=ARM_COLOR[a], label=ARM_LABEL[a]) for a in ARMS],
               loc="outside upper center", ncol=3, handlelength=1.2, columnspacing=1.4)
    save(fig, "fig_headline_seed7", ["arm", "metric", "k", "n", "rate", "wilson_lo", "wilson_hi"], rows,
         "seed 7, HITL oracle: " + "; ".join(f"{r[0]} {r[1]} {r[2]}/{r[3]}" for r in rows))
    return rows


def fig_scenarios(ev):
    res = ev["results"]["oracle"]
    fig, axes = plt.subplots(1, 3, figsize=(FULL, 3.5), sharey=True)
    rows = []
    order = list(reversed(SCENARIOS))
    n_of = {sc: res["baseline"]["summary"]["by_scenario"][sc]["n"] for sc in order}
    for ax, arm in zip(axes, ARMS):
        for i, sc in enumerate(order):
            b = res[arm]["summary"]["by_scenario"][sc]
            k, n = b["correct"], b["n"]
            ax.barh(i, k, height=0.62, color=ARM_COLOR[arm], zorder=2)
            if k == 0:
                zero_mark(ax, i, 0.62, ARM_COLOR[arm], horizontal=True)
            ax.text(k + 0.25, i, label_kn(k, n), va="center", ha="left", fontsize=9.5)
            rows.append([sc, arm, k, n])
        ax.set_xlim(0, 11.5)
        ax.set_xticks([0, 4, 8])
        ax.set_xlabel("Correct (packs)")
        ax.text(0.0, 1.02, ARM_LABEL[arm], transform=ax.transAxes, ha="left", va="bottom", fontsize=10.5,
                color=ARM_COLOR[arm] if arm != "baseline" else "#555555", fontweight="bold")
        vgrid(ax)
    axes[0].set_yticks(range(len(order)))
    axes[0].set_yticklabels([f"{SCEN_LABEL[sc]} ($n$ = {n_of[sc]})" for sc in order])
    axes[0].set_ylim(-0.6, len(order) - 0.4)
    save(fig, "fig_scenarios_seed7", ["scenario", "arm", "correct", "n"], rows,
         "seed 7, HITL oracle, correct per scenario: " + "; ".join(f"{r[0]} {r[1]} {r[2]}/{r[3]}" for r in rows))
    return rows


def fig_hitl(ev):
    metrics = [("hit_recall", "Hit recall\n(listed packs)"), ("abstention", "Abstention rate\n(all packs)"),
               ("far_all", "False-alarm rate\n(not-listed packs)")]
    arm = "agent_rules"
    fig, ax = plt.subplots(figsize=(FULL, 3.2))
    width = 0.34
    rows = []
    for j, policy in enumerate(["oracle", "none"]):
        s = ev["results"][policy][arm]["summary"]
        for i, (m, _) in enumerate(metrics):
            k, n = s[m]["k"], s[m]["n"]
            lo, hi = wilson(k, n)
            x = i + (j - 0.5) * width
            r = k / n
            if policy == "oracle":
                ax.bar(x, r, width=width * 0.92, color=ARM_COLOR[arm], zorder=2)
            else:
                ax.bar(x, r, width=width * 0.92, facecolor="white", edgecolor=ARM_COLOR[arm], hatch="////", linewidth=1.0, zorder=2)
            if k == 0:
                zero_mark(ax, x, width * 0.92, ARM_COLOR[arm])
            ax.errorbar(x, r, yerr=[[r - lo], [hi - r]], fmt="none", ecolor="#222222", elinewidth=0.9, capsize=2.5, zorder=3)
            ax.text(x, hi + 0.025, label_kn(k, n), ha="center", va="bottom", fontsize=9.5)
            rows.append([arm, policy, m, k, n, round(r, 4), round(lo, 4), round(hi, 4)])
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels([m[1] for m in metrics])
    ax.set_ylabel("Proportion of packs")
    ax.set_ylim(0, 1.18)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlim(-0.55, 2.55)
    hgrid(ax)
    fig.legend(handles=[Patch(color=ARM_COLOR[arm], label="Agent (rules), person answers (oracle)"),
                       Patch(facecolor="white", edgecolor=ARM_COLOR[arm], hatch="////", label="Agent (rules), no answers (none)")],
               loc="outside upper center", ncol=2, handlelength=1.6, columnspacing=1.4)
    save(fig, "fig_hitl_seed7", ["arm", "hitl", "metric", "k", "n", "rate", "wilson_lo", "wilson_hi"], rows,
         "seed 7, agent rules: " + "; ".join(f"{r[1]} {r[2]} {r[3]}/{r[4]}" for r in rows))
    return rows


def fig_latency(ev):
    res = ev["results"]["oracle"]
    fig, axes = plt.subplots(1, 2, figsize=(FULL, 2.7), sharey=True)
    rows = []
    for ax, key, xlabel, xmax in [(axes[0], "latency_s", "Time per pack, end to end (s)", 11.5),
                                  (axes[1], "reasoning_s", "Reasoning time only (s)", 11.5)]:
        for i, arm in enumerate(reversed(ARMS)):
            s = res[arm]["summary"][key]
            med, p95 = s["median"], s["p95"]
            col = ARM_COLOR[arm]
            ax.barh(i + 0.19, med, height=0.36, color=col, zorder=2)
            ax.barh(i - 0.19, p95, height=0.36, facecolor="white", edgecolor=col, hatch="////", linewidth=1.0, zorder=2)
            fmt = (lambda v: f"{v:.2f}") if key == "latency_s" else (lambda v: f"{v:.3f}")
            ax.text(med + 0.15, i + 0.19, fmt(med), va="center", fontsize=9.5)
            ax.text(p95 + 0.15, i - 0.19, fmt(p95), va="center", fontsize=9.5)
            rows.append([arm, key, med, p95])
        ax.set_xlim(0, xmax)
        ax.set_xticks([0, 2, 4, 6, 8, 10])
        ax.set_xlabel(xlabel)
        vgrid(ax)
    axes[0].set_yticks(range(len(ARMS)))
    axes[0].set_yticklabels([ARM_LABEL[a] for a in reversed(ARMS)])
    axes[0].set_ylim(-0.6, len(ARMS) - 0.4)
    fig.legend(handles=[Patch(color="#666666", label="Median"),
                        Patch(facecolor="white", edgecolor="#666666", hatch="////", label="95th percentile")],
               loc="outside upper center", ncol=2, handlelength=1.6)
    save(fig, "fig_latency_seed7", ["arm", "measure", "median_s", "p95_s"], rows,
         "seed 7, HITL oracle: " + "; ".join(f"{r[0]} {r[1]} median {r[2]} p95 {r[3]}" for r in rows))
    return rows


def fig_run1_run2(ev, run1):
    arm = "agent_rules"
    s2 = ev["results"]["oracle"][arm]["summary"]
    a1 = run1["A_oracle"]
    c1 = run1["C_oracle"]
    metrics = [("hit_recall", "Hit recall", "Hit recall"), ("hit_recall_clean_qr", "Hit recall (clean + QR)", "Hit recall\n(clean + QR)"),
               ("accuracy", "Overall accuracy", "Overall\naccuracy")]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL, 3.9), gridspec_kw={"width_ratios": [1.0, 1.0]})
    rows = []
    h = 0.36
    morder = list(reversed(metrics))
    for i, (m, md_name, label) in enumerate(morder):
        k1, n1 = kn_from_cell(a1[md_name][arm])
        k2, n2 = s2[m]["k"], s2[m]["n"]
        for dy, (k, n, run) in [(h / 2, (k1, n1, "run 1")), (-h / 2, (k2, n2, "run 2"))]:
            lo, hi = wilson(k, n)
            y = i + dy
            r = k / n
            if run == "run 2":
                ax1.barh(y, r, height=h * 0.92, color=ARM_COLOR[arm], zorder=2)
            else:
                ax1.barh(y, r, height=h * 0.92, facecolor="white", edgecolor=ARM_COLOR[arm], hatch="////", linewidth=1.0, zorder=2)
            ax1.errorbar(r, y, xerr=[[r - lo], [hi - r]], fmt="none", ecolor="#222222", elinewidth=0.9, capsize=2.0, zorder=3)
            ax1.text(hi + 0.03, y, label_kn(k, n), ha="left", va="center", fontsize=9.5)
            rows.append(["headline", m, run, k, n, round(r, 4), round(lo, 4), round(hi, 4)])
    ax1.set_yticks(range(len(morder)))
    ax1.set_yticklabels([m[2] for m in morder])
    ax1.set_xlabel("Proportion of packs")
    ax1.set_xlim(0, 1.42)
    ax1.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax1.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
    ax1.set_ylim(-0.6, len(morder) - 0.4)
    vgrid(ax1)
    order = list(reversed(SCENARIOS))
    for i, sc in enumerate(order):
        k1, n1 = kn_from_cell(c1[sc][arm])
        b2 = s2["by_scenario"][sc]
        k2, n2 = b2["correct"], b2["n"]
        ax2.barh(i + h / 2, k1, height=h * 0.92, facecolor="white", edgecolor=ARM_COLOR[arm], hatch="////", linewidth=1.0, zorder=2)
        ax2.barh(i - h / 2, k2, height=h * 0.92, color=ARM_COLOR[arm], zorder=2)
        ax2.text(k1 + 0.1, i + h / 2, label_kn(k1, n1), va="center", fontsize=9)
        ax2.text(k2 + 0.1, i - h / 2, label_kn(k2, n2), va="center", fontsize=9)
        rows.append(["scenario", sc, "run 1", k1, n1, "", "", ""])
        rows.append(["scenario", sc, "run 2", k2, n2, "", "", ""])
    ax2.set_yticks(range(len(order)))
    ax2.set_yticklabels([SCEN_LABEL[sc] for sc in order])
    ax2.set_xlim(0, 10.2)
    ax2.set_xticks(range(0, 9, 2))
    ax2.set_xlabel("Correct verdicts (packs)")
    ax2.set_ylim(-0.6, len(order) - 0.4)
    vgrid(ax2)
    fig.legend(handles=[Patch(facecolor="white", edgecolor=ARM_COLOR[arm], hatch="////", label="Run 1 (commit e283407)"),
                        Patch(color=ARM_COLOR[arm], label="Run 2 (after the three fixes)")],
               loc="outside upper center", ncol=2, handlelength=1.6)
    save(fig, "fig_run1_run2", ["part", "metric_or_scenario", "run", "k", "n", "rate", "wilson_lo", "wilson_hi"], rows,
         "agent rules, seed 7, HITL oracle: " + "; ".join(f"{r[1]} {r[2]} {r[3]}/{r[4]}" for r in rows))
    return rows


def fig_seeds(ev7, ev1):
    metrics = [("hit_recall", "Hit recall (listed packs)"), ("accuracy", "Overall accuracy (all packs)"),
               ("far_all", "False-alarm rate (not-listed packs)"), ("far_collision", "False-alarm rate (collision packs)")]
    fig, axes = plt.subplots(2, 2, figsize=(FULL, 4.4), sharey=True)
    rows = []
    h = 0.36
    for ax, (m, xlabel) in zip(axes.flat, metrics):
        for i, arm in enumerate(reversed(ARMS)):
            for dy, ev, seed in [(h / 2, ev1, 1), (-h / 2, ev7, 7)]:
                cell = ev["results"]["oracle"].get(arm)
                if not cell:
                    continue
                s = cell["summary"][m]
                k, n = s["k"], s["n"]
                lo, hi = wilson(k, n)
                r = k / n
                y = i + dy
                if seed == 7:
                    ax.barh(y, r, height=h * 0.92, color=ARM_COLOR[arm], zorder=2)
                else:
                    ax.barh(y, r, height=h * 0.92, facecolor="white", edgecolor=ARM_COLOR[arm], hatch="....", linewidth=1.0, zorder=2)
                if k == 0:
                    zero_mark(ax, y, h * 0.92, ARM_COLOR[arm], horizontal=True)
                ax.errorbar(r, y, xerr=[[r - lo], [hi - r]], fmt="none", ecolor="#222222", elinewidth=0.9, capsize=2.0, zorder=3)
                ax.text(hi + 0.03, y, label_kn(k, n), ha="left", va="center", fontsize=9)
                rows.append([arm, m, seed, k, n, round(r, 4), round(lo, 4), round(hi, 4)])
        ax.set_xlim(0, 1.38)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
        ax.set_xlabel(xlabel, fontsize=10.5)
        vgrid(ax)
    for ax in axes[:, 0]:
        ax.set_yticks(range(len(ARMS)))
        ax.set_yticklabels([ARM_LABEL[a] for a in reversed(ARMS)])
        ax.set_ylim(-0.6, len(ARMS) - 0.4)
    fig.legend(handles=[Patch(facecolor="white", edgecolor="#555555", hatch="....", label="Seed 1 (development set)"),
                        Patch(color="#555555", label="Seed 7 (evaluation set)")],
               loc="outside upper center", ncol=2, handlelength=1.6)
    save(fig, "fig_seeds", ["arm", "metric", "seed", "k", "n", "rate", "wilson_lo", "wilson_hi"], rows,
         "HITL oracle: " + "; ".join(f"{r[0]} {r[1]} seed{r[2]} {r[3]}/{r[4]}" for r in rows))
    return rows


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    setup_style()
    rows = db_rows()
    fig_alerts_per_year(rows)
    fig_alert_timing(rows)
    ev7 = load_eval(ROOT / "runs" / "eval_seed7_latest.json")
    fig_headline(ev7)
    fig_scenarios(ev7)
    fig_hitl(ev7)
    fig_latency(ev7)
    fig_run1_run2(ev7, run1_tables())
    seed1 = DATA / "eval_seed1.json"
    if seed1.is_file():
        fig_seeds(ev7, load_eval(seed1))
    else:
        summary_lines.append("fig_seeds.pdf: skipped (paper/report/data/eval_seed1.json missing)")
    for line in summary_lines:
        print(line)


if __name__ == "__main__":
    main()
