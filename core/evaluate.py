"""Deterministic synthetic diagnostics, separate from a research evaluation."""
import time
from datetime import datetime, timezone

from core import db
from core.textutils import batch_key


def run_quick(callback=None) -> dict:
    from core.investigator import investigate
    from core.props import demo_cases
    rows = []
    started = time.perf_counter()
    for index, case in enumerate(demo_cases()):
        before = time.perf_counter()
        alerts = case.get("alerts", [])
        state = investigate(dict(case.get("fields", {})), alerts, context={"demo": True, "real_alert_count": 0})
        answers = case.get("answers", [])
        if isinstance(answers, dict):
            answers = [answers]
        for answer in answers[:3]:
            if state.get("status") != "waiting":
                break
            state = investigate(state["fields"], alerts, context=state.get("context"), answer=answer)
        final = state.get("final") or {}
        expected = case.get("expected")
        if isinstance(expected, dict):
            expected = expected.get("label")
        actual = final.get("label") or state.get("status", "unknown")
        passed = actual == expected or (expected == "waiting" and state.get("status") == "waiting")
        row = {"id": case["id"], "name": case.get("name", case.get("title", case["id"])),
               "expected": expected, "actual": actual, "passed": passed,
               "latency_ms": round((time.perf_counter() - before) * 1000, 2), "synthetic": True}
        rows.append(row)
        if callback:
            callback({"type": "step", "node": "diagnostic", "step": index + 1,
                      "message": f"Checked synthetic scenario {index + 1}.", "result": row})
    report = {"id": "quick", "available": True, "kind": "synthetic_diagnostic", "synthetic": True,
              "title": "Offline synthetic diagnostics", "created_at": datetime.now(timezone.utc).isoformat(),
              "notice": "These authored scenarios check application behavior. They do not measure performance on real medicines or establish research accuracy.",
              "total": len(rows), "passed": sum(row["passed"] for row in rows),
              "failed": sum(not row["passed"] for row in rows), "rows": rows, "cases": rows,
              "duration_ms": round((time.perf_counter() - started) * 1000, 2)}
    db.save_document("evaluation", "latest", report)
    return report


def latest() -> dict:
    return db.get_document("evaluation", "latest") or {"available": False, "kind": "synthetic_diagnostic", "rows": [], "notice": "Run the offline diagnostics to see results."}


# ---------------------------------------------------------------------------
# Research evaluation (M7): golden set from real alert rows, three arms, two HITL policies.
# ---------------------------------------------------------------------------
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path

from core import config

ARMS = ("baseline", "agent_rules", "agent_hybrid")
HITL = ("oracle", "none")
POSITIVE = {"FLAGGED", "SUSPECTED_FAKE"}
MAX_ANSWERS = 3
VERDICT = {True: "held", False: "did not hold", None: "not evaluable"}
ADOPT = {True: "adopt", False: "do not adopt", None: "not evaluable"}


def wilson(k, n, z=1.96):
    """Wilson 95% score interval; None when n is 0."""
    if not n:
        return None
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)]


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value from the discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(b, c) + 1)) / 2 ** n
    return round(min(1.0, 2 * tail), 6)


def _percentile(values, q):
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    low, high = math.floor(pos), math.ceil(pos)
    return ordered[low] + (ordered[high] - ordered[low]) * (pos - low)


def _file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def perceive(manifest, folder, refresh=False, log=None):
    """Read every image once through the public perception API; cache keyed by image and pack_tools hashes."""
    from core.pack_tools import read_pack
    folder = Path(folder)
    cache_path = folder / "perception.json"
    tools = _file_hash(config.ROOT / "core" / "pack_tools.py")[:16]
    cache = {}
    if cache_path.is_file() and not refresh:
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except ValueError:
            cache = {}
    out = {}
    for number, item in enumerate(manifest["items"], 1):
        key = f"{item['image_sha256'][:16]}:{tools}"
        if key not in cache:
            started = time.perf_counter()
            try:
                reading = read_pack(folder / item["image"])
                fields, error = reading.get("fields", {}), ""
                lines = [line.get("text", "") for line in reading.get("lines", [])]
                engine = reading.get("engine")
            except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
                fields, error, lines, engine = {}, str(exc)[:200], [], None
            cache[key] = {"fields": {k: fields.get(k, "") for k in ("batch", "product", "product_text", "brand", "mfg", "exp", "maker", "source", "confirmed")},
                          "lines": lines[:40], "engine": engine, "error": error,
                          "seconds": round(time.perf_counter() - started, 3)}
            cache_path.write_text(json.dumps(cache, indent=1, ensure_ascii=True), encoding="utf-8")
            if log and number % 10 == 0:
                log(f"  perceived {number}/{len(manifest['items'])}")
        out[item["id"]] = cache[key]
    return out


def ollama_status(timeout=2):
    import requests
    try:
        result = requests.get(config.OLLAMA_URL.rstrip("/") + "/api/tags", timeout=timeout)
        result.raise_for_status()
        models = [row.get("name") for row in result.json().get("models", [])]
        return {"up": True, "models": models, "model": config.LLM_MODEL, "model_present": config.LLM_MODEL in models}
    except Exception as exc:  # any failure means the arm runs on its fallbacks
        return {"up": False, "models": [], "model": config.LLM_MODEL, "model_present": False, "error": type(exc).__name__}


def oracle_answer(pending, printed):
    """Answer truthfully from the manifest's printed truth."""
    kind = pending.get("kind")
    truth = printed.get("batch", "")
    if kind in {"type_batch", "confirm_batch"}:
        return {"typed": truth, "choice": truth} if truth else {"skip": True}
    if kind == "confirm_char":
        return {"choice": "listed"} if batch_key(truth) == batch_key(pending.get("listed")) else {"choice": "printed"}
    if kind == "confirm_field":
        field = pending.get("field")
        return {"choice": "listed"} if printed.get(field) == pending.get("listed") else {"choice": "printed"}
    supplied = {key: printed.get(key, "") for key in ("product", "brand", "maker", "mfg", "exp") if printed.get(key)}
    return {"fields": supplied, "source": "user"} if supplied else {"skip": True}


def safety_violations(final):
    """Banned phrases in user-facing text, unknown labels, or a listed result without a citation."""
    from core.templates import BANNED, LABELS
    problems = []
    text = " ".join(str(final.get(key, "")) for key in ("headline", "explanation", "advice"))
    if BANNED.search(text):
        problems.append("banned_phrase")
    if final.get("label") not in LABELS:
        problems.append("unknown_label")
    if final.get("label") in POSITIVE and not final.get("citations"):
        problems.append("flag_without_citation")
    return problems


def _list_context(alerts):
    months = sorted({str(a.get("list_month")) for a in alerts if a.get("list_month")})
    return {"latest_month": months[-1] if months else None,
            "list_count": len({(a.get("list_month"), a.get("source_url") or a.get("source_title"), a.get("entry_type")) for a in alerts}),
            "real_alert_count": len(alerts)}


def _index(alerts):
    index = {}
    for alert in alerts:
        key = batch_key(alert.get("batch_key") or alert.get("batch_raw"))
        if key:
            index.setdefault(key, []).append(alert)
    return index


def run_baseline(fields, index, list_context):
    """Arm A: QR or OCR batch -> exact lookup -> any hit is a listed result, typed by entry type."""
    from core.templates import render_verdict
    key = batch_key(fields.get("batch"))
    hits = index.get(key, []) if key else []
    if not key:
        label, top, reason = "CANT_VERIFY", None, "a readable batch number was not provided"
    elif hits:
        top = next((h for h in hits if h.get("entry_type") == "SPURIOUS"), hits[0])
        label, reason = ("SUSPECTED_FAKE" if top.get("entry_type") == "SPURIOUS" else "FLAGGED"), ""
    else:
        label, top, reason = "NOT_LISTED", None, ""
    final = render_verdict(label, fields, top, dict(list_context), reason, fields.get("source", "none"))
    return {"label": label, "final": final, "asks": 0, "steps": 1, "questions": [], "sources": {"script": 1}}


def run_agent(fields, alerts, list_context, printed, hitl, planner):
    """Arms B and C: the investigator, answered by the oracle or with every question skipped."""
    from core.investigator import investigate
    context = dict(list_context, lang="en", planner=planner, llm_model=config.LLM_MODEL, ollama_url=config.OLLAMA_URL)
    state = investigate(dict(fields), alerts, context=context)
    questions = []
    for _ in range(MAX_ANSWERS):
        if state.get("status") != "waiting":
            break
        pending = state.get("pending") or {}
        answer = oracle_answer(pending, printed) if hitl == "oracle" else {"skip": True}
        questions.append({"kind": pending.get("kind"), "answer": answer})
        state = investigate(state["fields"], alerts, context=state.get("context"), answer=answer)
    final = state.get("final") or {}
    label = final.get("label") or "CANT_VERIFY"  # still waiting after the bound counts as an abstention
    engine = (state.get("context") or {}).get("_engine", {})
    sources = Counter(str(step.get("source", "rules")) for step in state.get("history", []))
    partial = any((c.get("evidence") or {}).get("product") == "partial" for c in state.get("candidates", []))
    return {"label": label, "final": final, "asks": int(engine.get("asks", len(questions))), "steps": len(state.get("history", [])),
            "questions": questions, "sources": dict(sources), "partial_product": partial,
            "still_waiting": state.get("status") == "waiting"}


def _rate(rows, test):
    k, n = sum(1 for r in rows if test(r)), len(rows)
    return {"k": k, "n": n, "rate": round(k / n, 4) if n else None, "ci": wilson(k, n)}


def _summary(rows):
    """Metrics for one arm x HITL setting."""
    positives = [r for r in rows if r["truth"] in POSITIVE]
    negatives = [r for r in rows if r["truth"] == "NOT_LISTED"]
    detected = [r for r in positives if r["label"] in POSITIVE]
    latency = [r["latency_s"] for r in rows]
    reasoning = [r["reasoning_s"] for r in rows]
    by_scenario = {}
    for scenario in sorted({r["scenario"] for r in rows}):
        sub = [r for r in rows if r["scenario"] == scenario]
        by_scenario[scenario] = {"correct": sum(r["correct"] for r in sub), "n": len(sub),
                                 "labels": dict(Counter(r["label"] for r in sub)),
                                 "questions": round(sum(r["asks"] for r in sub) / len(sub), 3)}
    sources = Counter()
    for r in rows:
        sources.update(r.get("sources", {}))
    spread = lambda v, d: {"median": round(statistics.median(v), d), "mean": round(statistics.fmean(v), d), "p95": round(_percentile(v, 0.95), d)}
    return {
        "n": len(rows),
        "accuracy": _rate(rows, lambda r: r["correct"]),
        "hit_recall": _rate(positives, lambda r: r["label"] in POSITIVE),
        "hit_recall_clean_qr": _rate([r for r in positives if r["scenario"] in ("clean", "qr")], lambda r: r["label"] in POSITIVE),
        "type_accuracy": _rate(detected, lambda r: r["label"] == r["truth"]),
        "far_all": _rate(negatives, lambda r: r["label"] in POSITIVE),
        "far_collision": _rate([r for r in negatives if r["scenario"] == "collision"], lambda r: r["label"] in POSITIVE),
        "far_sibling": _rate([r for r in negatives if r["scenario"] == "sibling"], lambda r: r["label"] in POSITIVE),
        "abstention": _rate(rows, lambda r: r["label"] == "CANT_VERIFY"),
        "questions_per_pack": round(sum(r["asks"] for r in rows) / len(rows), 3) if rows else None,
        "steps_per_pack": round(sum(r["steps"] for r in rows) / len(rows), 3) if rows else None,
        "latency_s": spread(latency, 3) if rows else None,
        "reasoning_s": spread(reasoning, 4) if rows else None,
        "safety_violations": sum(len(r["safety"]) for r in rows),
        "by_scenario": by_scenario,
        "step_sources": dict(sources),
        "fallback_steps": sum(v for k, v in sources.items() if "fallback" in k),
        "llm_steps": sum(v for k, v in sources.items() if k.startswith("llm")),
    }


def run_arm(arm, hitl, manifest, perception, alerts, index=None, list_context=None):
    index = index if index is not None else _index(alerts)
    list_context = list_context or _list_context(alerts)
    rows = []
    for item in manifest["items"]:
        seen = perception[item["id"]]
        fields = dict(seen["fields"])
        started = time.perf_counter()
        if arm == "baseline":
            result = run_baseline(fields, index, list_context)
        else:
            result = run_agent(fields, alerts, list_context, item["printed"], hitl, "hybrid" if arm == "agent_hybrid" else "rules")
        reasoning = time.perf_counter() - started
        final = result.pop("final")
        rows.append(dict(result, id=item["id"], scenario=item["scenario"], truth=item["truth"],
                         correct=result["label"] == item["truth"], read_batch=fields.get("batch", ""),
                         read_source=fields.get("source", ""), printed_batch=item["printed"]["batch"],
                         reasoning_s=round(reasoning, 4), latency_s=round(seen["seconds"] + reasoning, 3),
                         safety=safety_violations(final), reason=final.get("reason", ""),
                         headline=final.get("headline", "")))
    return rows


def paired(rows_a, rows_b):
    """Exact McNemar on correctness for identical items."""
    by_id = {r["id"]: r["correct"] for r in rows_b}
    b = sum(1 for r in rows_a if r["correct"] and not by_id[r["id"]])
    c = sum(1 for r in rows_a if not r["correct"] and by_id[r["id"]])
    return {"agent_only_correct": b, "baseline_only_correct": c, "p_value": mcnemar_exact(b, c)}


def decision_rule(agent, baseline):
    """Adopt the agent if collision FAR is >= 50% lower (relative) and hit recall is <= 5 points lower."""
    a_far, b_far = agent["far_collision"]["rate"], baseline["far_collision"]["rate"]
    a_hr, b_hr = agent["hit_recall"]["rate"], baseline["hit_recall"]["rate"]
    if not b_far or a_far is None or a_hr is None or b_hr is None:
        return {"adopt": None, "detail": "not evaluable: the baseline has no collision false alarms or a rate is missing"}
    reduction = 1 - a_far / b_far
    drop = b_hr - a_hr
    return {"adopt": reduction >= 0.5 and drop <= 0.05, "relative_far_reduction": round(reduction, 4), "hit_recall_drop": round(drop, 4),
            "detail": f"collision FAR {a_far:.2f} vs {b_far:.2f} ({reduction:.0%} lower); hit recall {a_hr:.2f} vs {b_hr:.2f} ({abs(drop) * 100:.1f} points {'lower' if drop > 0 else 'higher' if drop < 0 else 'apart'})"}


def predictions(results):
    """Registered predictions (plan section 4.7), each held / did not hold / not evaluable, with counts (HITL oracle)."""
    out = []
    oracle = results.get("oracle", {})
    base, rules, hybrid = oracle.get("baseline"), oracle.get("agent_rules"), oracle.get("agent_hybrid")

    def add(name, held, detail):
        out.append({"prediction": name, "held": held, "detail": detail})

    if base and rules:
        arms = [(n, a) for n, a in (("baseline", base), ("agent_rules", rules), ("agent_hybrid", hybrid)) if a]
        counts = {n: (a["summary"]["by_scenario"].get("clean", {}).get("correct", 0), a["summary"]["by_scenario"].get("clean", {}).get("n", 0)) for n, a in arms}
        add("Clean packs: all arms tie", len({k for k, _ in counts.values()}) == 1,
            "; ".join(f"{n} {k}/{m}" for n, (k, m) in counts.items()))
        bf, af = base["summary"]["far_collision"], rules["summary"]["far_collision"]
        held = None if not bf["n"] else (bf["k"] == bf["n"] and af["rate"] <= 0.10)
        add("Collisions: baseline false-alarms on every one; agent at most 10%", held,
            f"baseline {bf['k']}/{bf['n']}, agent_rules {af['k']}/{af['n']}")
        mis = [r for r in rules["rows"] if r["scenario"] == "misread"]
        b_hits = sum(1 for r in base["rows"] if r["scenario"] == "misread" and r["label"] in POSITIVE)
        a_hits = sum(1 for r in mis if r["label"] == r["truth"])
        qpp = sum(r["asks"] for r in mis) / len(mis) if mis else None
        held = None if not mis else (b_hits == 0 and a_hits / len(mis) >= 0.8 and qpp <= 1.0)
        add("Misreads: baseline misses every flag; agent with oracle recovers at least 80% at no more than 1 question per pack", held,
            f"baseline detected {b_hits}/{len(mis)}; agent_rules correct {a_hits}/{len(mis)} at {round(qpp, 2) if mis else 'n/a'} questions per pack")
    if rules and hybrid:
        h = {r["id"]: r for r in hybrid["rows"]}
        same = sum(1 for r in rules["rows"] if h[r["id"]]["label"] == r["label"])
        add("Hybrid matches rules on verdicts", same == len(rules["rows"]), f"{same}/{len(rules['rows'])} identical labels")
        partial = [r for r in rules["rows"] if r.get("partial_product") or h[r["id"]].get("partial_product")]
        if partial:
            rk, hk = sum(r["correct"] for r in partial), sum(h[r["id"]]["correct"] for r in partial)
            add("Hybrid beats rules on partial product matches", hk > rk, f"hybrid {hk}/{len(partial)}, rules {rk}/{len(partial)}")
        else:
            add("Hybrid beats rules on partial product matches", None, "no item produced a partial product match")
    return out


def _manifest_sha(manifest):
    return hashlib.sha256(json.dumps([[i["id"], i["image_sha256"], i["truth"]] for i in manifest["items"]]).encode()).hexdigest()[:16]


def run_research(arms=ARMS, hitl=HITL, seed=7, n=60, alerts=None, eval_folder=None, runs_dir=None,
                 write_paper=None, paper_dir=None, results_dir=None, log=print):
    """Run the golden-set evaluation and write runs/eval_<ts>.json/.md. Returns the combined report.

    Results for each arm x HITL are merged into runs/eval_seed<N>_latest.json, so separate
    invocations (oracle, then none) build one complete report for the same manifest."""
    from core import golden
    runs_dir = Path(runs_dir) if runs_dir else config.RUNS_DIR
    runs_dir.mkdir(parents=True, exist_ok=True)
    alerts = alerts if alerts is not None else db.all_alerts()
    folder = Path(eval_folder) if eval_folder else golden.eval_dir(seed)
    manifest = golden.load(seed, folder)
    if manifest is None or manifest.get("requested_n") != n:
        log(f"Generating golden set seed {seed} n={n} in {folder}")
        manifest = golden.generate(n=n, seed=seed, alerts=alerts, out=folder)
    alert_ids = {a["id"] for a in alerts}
    missing = [i["id"] for i in manifest["items"] if i.get("alert_id") is not None and i["alert_id"] not in alert_ids]
    if missing:
        raise ValueError(f"Manifest items cite alerts missing from the database: {missing[:5]}")
    log(f"Perception for {len(manifest['items'])} images (cached when unchanged)")
    perception = perceive(manifest, folder, log=log)
    index, list_context = _index(alerts), _list_context(alerts)
    store_file = runs_dir / f"eval_seed{int(seed)}_latest.json"
    store = {}
    if store_file.is_file():
        try:
            store = json.loads(store_file.read_text(encoding="utf-8"))
        except ValueError:
            store = {}
    if store.get("manifest_sha") != _manifest_sha(manifest) or store.get("alert_count") != len(alerts):
        store = {}
    store.update(seed=int(seed), n=manifest["n"], manifest_sha=_manifest_sha(manifest), mix=manifest["mix"],
                 alert_count=len(alerts), results=store.get("results", {}))
    store["perception"] = {"engines": dict(Counter(str(p.get("engine")) for p in perception.values())),
                           "errors": sum(1 for p in perception.values() if p.get("error")),
                           "batch_read_exact": sum(1 for i in manifest["items"] if batch_key(perception[i["id"]]["fields"].get("batch")) == batch_key(i["rendered"]["batch"])),
                           "median_s": round(statistics.median(p["seconds"] for p in perception.values()), 3)}
    for policy in hitl:
        for arm in arms:
            if arm == "agent_hybrid":
                store["ollama"] = ollama_status()
            log(f"Running {arm} with HITL={policy}")
            started = time.perf_counter()
            rows = run_arm(arm, policy, manifest, perception, alerts, index, list_context)
            store["results"].setdefault(policy, {})[arm] = {"summary": _summary(rows), "rows": rows,
                                                              "wall_s": round(time.perf_counter() - started, 2),
                                                              "ran_at": datetime.now(timezone.utc).isoformat()}
            store_file.write_text(json.dumps(store, indent=1, ensure_ascii=True), encoding="utf-8")
    for policy, done in store["results"].items():
        base = done.get("baseline")
        for arm, cell in done.items():
            if arm != "baseline" and base:
                cell["vs_baseline"] = {"mcnemar": paired(cell["rows"], base["rows"]),
                                       "decision_rule": decision_rule(cell["summary"], base["summary"])}
    store["predictions"] = predictions(store["results"])
    store_file.write_text(json.dumps(store, indent=1, ensure_ascii=True), encoding="utf-8")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = dict(store, created_at=datetime.now(timezone.utc).isoformat(), invocation={"arms": list(arms), "hitl": list(hitl)})
    json_path, md_path = runs_dir / f"eval_{stamp}.json", runs_dir / f"eval_{stamp}.md"
    text = markdown(report)
    json_path.write_text(json.dumps(report, indent=1, ensure_ascii=True), encoding="utf-8")
    md_path.write_text(text, encoding="utf-8")
    report["paths"] = {"json": str(json_path), "md": str(md_path)}
    if write_paper if write_paper is not None else int(seed) == 7:
        results_dir = Path(results_dir) if results_dir else config.ROOT / "docs" / "results"
        paper_dir = Path(paper_dir) if paper_dir else config.ROOT / "paper" / "generated"
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / f"eval_seed{int(seed)}.md").write_text(text, encoding="utf-8")
        write_latex(report, paper_dir)
        report["paths"].update(results=str(results_dir / f"eval_seed{int(seed)}.md"), latex=str(paper_dir))
    db.save_document("evaluation", "research_latest", {
        "kind": "research_evaluation", "available": True, "seed": int(seed), "n": manifest["n"],
        "created_at": report["created_at"], "md": str(md_path),
        "headline": {p: {a: {k: c["summary"][k] for k in ("hit_recall", "far_all", "far_collision", "abstention", "questions_per_pack")}
                         for a, c in done.items()} for p, done in store["results"].items()}})
    return report


def research_latest():
    return db.get_document("evaluation", "research_latest") or {"available": False, "kind": "research_evaluation"}


# ---- Reports ----
ARM_NAMES = {"baseline": "Baseline (lookup)", "agent_rules": "Agent (rules)", "agent_hybrid": "Agent (hybrid)"}
SCENARIOS = ("clean", "glare", "misread", "qr", "spurious", "collision", "genuine", "sibling")


def _fmt_rate(cell):
    if not cell or not cell.get("n"):
        return "n/a"
    lo, hi = cell["ci"]
    return f"{cell['rate']:.2f} ({cell['k']}/{cell['n']}; {lo:.2f}-{hi:.2f})"


def _metric_rows(summaries):
    rows = []

    def line(name, getter):
        rows.append([name] + [getter(s) for s in summaries.values()])
    line("Hit recall", lambda s: _fmt_rate(s["hit_recall"]))
    line("Hit recall (clean + QR)", lambda s: _fmt_rate(s["hit_recall_clean_qr"]))
    line("Type accuracy", lambda s: _fmt_rate(s["type_accuracy"]))
    line("False-alarm rate (all NOT_LISTED)", lambda s: _fmt_rate(s["far_all"]))
    line("False-alarm rate (collisions)", lambda s: _fmt_rate(s["far_collision"]))
    line("False-alarm rate (siblings)", lambda s: _fmt_rate(s["far_sibling"]))
    line("Abstention rate", lambda s: _fmt_rate(s["abstention"]))
    line("Overall accuracy", lambda s: _fmt_rate(s["accuracy"]))
    line("Questions per pack", lambda s: f"{s['questions_per_pack']:.2f}")
    line("Steps per pack", lambda s: f"{s['steps_per_pack']:.1f}")
    line("Latency median / mean / p95 (s)", lambda s: f"{s['latency_s']['median']:.2f} / {s['latency_s']['mean']:.2f} / {s['latency_s']['p95']:.2f}")
    line("Reasoning only, median / p95 (s)", lambda s: f"{s['reasoning_s']['median']:.3f} / {s['reasoning_s']['p95']:.3f}")
    line("Safety violations", lambda s: str(s["safety_violations"]))
    line("LLM steps / fallback steps", lambda s: f"{s['llm_steps']} / {s['fallback_steps']}")
    return rows


def _md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return "\n".join(out + ["| " + " | ".join(str(c) for c in row) + " |" for row in rows])


def markdown(report):
    res = report["results"]
    lines = [f"# StripCheck evaluation, seed {report['seed']} (n = {report['n']})", "",
             f"Created {report.get('created_at', '')}. The golden set renders {report['n']} cartons from real CDSCO alert rows "
             f"(local database: {report['alert_count']} alerts). Every image carries the banner DEMO PROP - NOT A MEDICINE. "
             "Misread and sibling items simulate an OCR error by rendering the misread string; the oracle answers from the printed truth. "
             "Thresholds were not tuned on this seed.", "",
             f"Scenario mix: {', '.join(f'{k} {v}' for k, v in report['mix'].items())}.", ""]
    p = report.get("perception", {})
    lines += [f"Perception (shared by all arms, read once per image): engines {p.get('engines')}, errors {p.get('errors')}, "
              f"batch read equal to the rendered text on {p.get('batch_read_exact')}/{report['n']} images, median {p.get('median_s')} s per image. "
              "Latency per pack is perception time plus the arm's own reasoning time.", ""]
    if report.get("ollama"):
        o = report["ollama"]
        lines += [f"Ollama at the hybrid run: up={o.get('up')}, model {o.get('model')} present={o.get('model_present')}.", ""]
    for table, policy in (("A", "oracle"), ("B", "none")):
        if policy in res:
            arms = {ARM_NAMES.get(a, a): res[policy][a]["summary"] for a in ARMS if a in res[policy]}
            lines += [f"## Table {table}: headline metrics, HITL = {policy}", "", "Rates as value (k/n; Wilson 95% interval).", "",
                      _md_table(["Metric"] + list(arms), _metric_rows(arms)), ""]
    for policy in ("oracle", "none"):
        if policy in res:
            names = [a for a in ARMS if a in res[policy]]
            cell = lambda a, s: res[policy][a]["summary"]["by_scenario"].get(s, {"correct": 0, "n": 0})
            rows = [[s] + [f"{cell(a, s)['correct']}/{cell(a, s)['n']}" for a in names] for s in SCENARIOS]
            lines += [f"## Table C: correct verdicts per scenario (k/n), HITL = {policy}", "",
                      _md_table(["Scenario"] + [ARM_NAMES[a] for a in names], rows), ""]
    lines += ["## Paired comparison and decision rule", "",
              "Exact McNemar test on per-item correctness against the baseline. Decision rule (registered at R2): adopt the agent if its "
              "collision false-alarm rate is at least 50% lower (relative) than the baseline's and its hit recall is no more than 5 points lower.", ""]
    rows = []
    for policy in ("oracle", "none"):
        for arm in ("agent_rules", "agent_hybrid"):
            cell = res.get(policy, {}).get(arm, {})
            if "vs_baseline" in cell:
                m, d = cell["vs_baseline"]["mcnemar"], cell["vs_baseline"]["decision_rule"]
                rows.append([ARM_NAMES[arm], policy, m["agent_only_correct"], m["baseline_only_correct"], m["p_value"], ADOPT[d["adopt"]], d["detail"]])
    lines += [_md_table(["Arm", "HITL", "Agent-only correct", "Baseline-only correct", "McNemar p", "Decision", "Detail"], rows), ""]
    lines += ["## Registered predictions (HITL = oracle)", "",
              _md_table(["Prediction", "Outcome", "Counts"], [[x["prediction"], VERDICT[x["held"]], x["detail"]] for x in report.get("predictions", [])]), ""]
    errors = []
    for policy in ("oracle", "none"):
        for arm in ARMS:
            for r in res.get(policy, {}).get(arm, {}).get("rows", []):
                if not r["correct"]:
                    errors.append([policy, arm, r["id"], r["truth"], r["label"], r["read_batch"] or "-", r["printed_batch"], r["asks"],
                                   ",".join(q["kind"] for q in r.get("questions", [])) or "-", (r["reason"] or "")[:70]])
    lines += ["## Every incorrect verdict", "",
              _md_table(["HITL", "Arm", "Item", "Truth", "Verdict", "Read batch", "Printed batch", "Asks", "Questions", "Reason"], errors) if errors else "None.", ""]
    return "\n".join(lines) + "\n"


def _tex(value, digits=2):
    return "n/a" if value is None else f"{value:.{digits}f}"


def _esc(text):
    return str(text).replace("\\", "/").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("<=", "$\\le$").replace(">=", "$\\ge$")


def write_latex(report, folder):
    """paper/generated/results.tex (macros) and results_tables.tex (tables) from the combined report."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    arm_tag = {"baseline": "Base", "agent_rules": "Rules", "agent_hybrid": "Hybrid"}
    hitl_tag = {"oracle": "Oracle", "none": "Skip"}
    metric_tag = {"hit_recall": "HitRecall", "hit_recall_clean_qr": "HitRecallCleanQR", "type_accuracy": "TypeAcc",
                  "far_all": "FAR", "far_collision": "FARCollision", "far_sibling": "FARSibling", "abstention": "Abstain",
                  "accuracy": "Accuracy"}
    macros = ["% Generated by cli.py eval from runs/eval_seed*_latest.json. Do not edit by hand.",
              "% Naming: \\Res<Arm><HITL><Metric>, Arm in Base/Rules/Hybrid, HITL in Oracle/Skip; suffix K = k/n, CI = Wilson 95%.",
              f"\\newcommand{{\\ResSeed}}{{{report['seed']}}}", f"\\newcommand{{\\ResN}}{{{report['n']}}}",
              f"\\newcommand{{\\ResAlertCount}}{{{report['alert_count']:,}}}".replace(",", "{,}", 1) if report['alert_count'] >= 1000 else f"\\newcommand{{\\ResAlertCount}}{{{report['alert_count']}}}"]
    for scenario, count in report["mix"].items():
        macros.append(f"\\newcommand{{\\ResMix{scenario.capitalize()}}}{{{count}}}")
    for policy, arms in report["results"].items():
        for arm, cell in arms.items():
            s, prefix = cell["summary"], "\\Res" + arm_tag[arm] + hitl_tag[policy]
            for key, tag in metric_tag.items():
                c = s[key]
                ci = c["ci"] or [None, None]
                macros += [f"\\newcommand{{{prefix}{tag}}}{{{_tex(c['rate'])}}}",
                           f"\\newcommand{{{prefix}{tag}K}}{{{c['k']}/{c['n']}}}",
                           f"\\newcommand{{{prefix}{tag}CI}}{{[{_tex(ci[0])}, {_tex(ci[1])}]}}"]
            macros += [f"\\newcommand{{{prefix}Questions}}{{{_tex(s['questions_per_pack'])}}}",
                       f"\\newcommand{{{prefix}Steps}}{{{_tex(s['steps_per_pack'], 1)}}}",
                       f"\\newcommand{{{prefix}LatMedian}}{{{_tex(s['latency_s']['median'])}}}",
                       f"\\newcommand{{{prefix}LatMean}}{{{_tex(s['latency_s']['mean'])}}}",
                       f"\\newcommand{{{prefix}LatPNinetyFive}}{{{_tex(s['latency_s']['p95'])}}}",
                       f"\\newcommand{{{prefix}ReasonMedian}}{{{_tex(s['reasoning_s']['median'], 3)}}}",
                       f"\\newcommand{{{prefix}Safety}}{{{s['safety_violations']}}}",
                       f"\\newcommand{{{prefix}LLMSteps}}{{{s['llm_steps']}}}",
                       f"\\newcommand{{{prefix}FallbackSteps}}{{{s['fallback_steps']}}}"]
            if "vs_baseline" in cell:
                m, d = cell["vs_baseline"]["mcnemar"], cell["vs_baseline"]["decision_rule"]
                macros += [f"\\newcommand{{{prefix}McNemarP}}{{{m['p_value']:.3g}}}",
                           f"\\newcommand{{{prefix}McNemarB}}{{{m['agent_only_correct']}}}",
                           f"\\newcommand{{{prefix}McNemarC}}{{{m['baseline_only_correct']}}}",
                           f"\\newcommand{{{prefix}Decision}}{{{ADOPT[d['adopt']]}}}"]
    p = report.get("perception", {})
    macros += [f"\\newcommand{{\\ResOCRBatchExact}}{{{p.get('batch_read_exact', 0)}/{report['n']}}}",
               f"\\newcommand{{\\ResOCRMedian}}{{{_tex(p.get('median_s'))}}}"]
    names = ("One", "Two", "Three", "Four", "Five", "Six")
    for i, pred in enumerate(report.get("predictions", [])[:6]):
        macros.append(f"\\newcommand{{\\ResPrediction{names[i]}}}{{{VERDICT[pred['held']]}}}")
    (folder / "results.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")

    tables = ["% Generated by cli.py eval. Do not edit by hand. Needs booktabs and graphicx."]
    for policy, label in (("oracle", "oracle user"), ("none", "every question skipped")):
        if policy not in report["results"]:
            continue
        arms = [a for a in ARMS if a in report["results"][policy]]
        summaries = {ARM_NAMES[a]: report["results"][policy][a]["summary"] for a in arms}
        tables += ["\\begin{table}[t]\\centering\\footnotesize",
                   f"\\caption{{Headline metrics on the eval set (seed {report['seed']}, $n={report['n']}$), HITL: {label}. Rates as value ($k/n$; Wilson 95\\% interval).}}",
                   f"\\label{{tab:results-{policy}}}", "\\resizebox{\\columnwidth}{!}{%",
                   "\\begin{tabular}{l" + "l" * len(arms) + "}", "\\toprule",
                   "Metric & " + " & ".join(_esc(n) for n in summaries) + " \\\\", "\\midrule"]
        tables += [" & ".join(_esc(c) for c in row) + " \\\\" for row in _metric_rows(summaries)]
        tables += ["\\bottomrule", "\\end{tabular}}", "\\end{table}", ""]
    for policy in ("oracle", "none"):
        if policy not in report["results"]:
            continue
        arms = [a for a in ARMS if a in report["results"][policy]]
        tables += ["\\begin{table}[t]\\centering\\footnotesize",
                   f"\\caption{{Correct verdicts per scenario ($k/n$), HITL: {'oracle' if policy == 'oracle' else 'questions skipped'}.}}",
                   f"\\label{{tab:scenario-{policy}}}", "\\begin{tabular}{l" + "c" * len(arms) + "}", "\\toprule",
                   "Scenario & " + " & ".join(_esc(ARM_NAMES[a]) for a in arms) + " \\\\", "\\midrule"]
        for s in SCENARIOS:
            cells = [report["results"][policy][a]["summary"]["by_scenario"].get(s) for a in arms]
            if any(cells):
                tables.append(s + " & " + " & ".join(f"{c['correct']}/{c['n']}" if c else "--" for c in cells) + " \\\\")
        tables += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    if report.get("predictions"):
        tables += ["\\begin{table}[t]\\centering\\footnotesize", "\\caption{Registered predictions and outcomes (HITL: oracle).}",
                   "\\label{tab:predictions}", "\\begin{tabular}{p{0.40\\columnwidth}p{0.14\\columnwidth}p{0.34\\columnwidth}}", "\\toprule",
                   "Prediction & Outcome & Counts \\\\", "\\midrule"]
        tables += [f"{_esc(x['prediction'])} & {VERDICT[x['held']]} & {_esc(x['detail'])} \\\\" for x in report["predictions"]]
        tables += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    (folder / "results_tables.tex").write_text("\n".join(tables) + "\n", encoding="utf-8")
