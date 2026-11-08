"""Golden-set generator and research evaluation: fast, offline, rules arms only (no Ollama, no OCR)."""
import json

from PIL import Image

from core import config, db, evaluate, golden
from core.textutils import CONFUSABLE, batch_key, confusion_variants

NAMES = ["Alpharin", "Betazolam", "Corvexil", "Dravinox", "Elmotrid", "Fenzarol", "Gravadol", "Hexipram", "Isotravin",
         "Jumoxil", "Kelvaprin", "Lorzetan", "Mivocort", "Nebrazide", "Ortivane", "Pelnaxin", "Quorvidil", "Ranzolet",
         "Sivotrex", "Tamberol", "Ulvaprine", "Vexidrol", "Wenzapam", "Xylatrin", "Yorbicet", "Zentravir", "Acurolin",
         "Bramexol", "Cindapril", "Doxarvin", "Eprazolin", "Fulvatrex", "Glimbarin", "Hydrozent", "Ivarnex", "Jextolin"]


def fixture_alerts():
    rows = []
    for i, name in enumerate(NAMES):
        spurious = i >= 32
        rows.append({"id": i + 1, "product": f"{name} Tablets IP 10 mg", "brand": "", "batch_raw": f"K{i:02d}B8{i % 7}Q",
                     "batch_key": f"K{i:02d}B8{i % 7}Q", "mfg": "2025-01", "exp": "2027-12",
                     "maker_raw": f"{name} Laboratories Pvt Ltd", "maker_name": f"{name} Laboratories Pvt Ltd",
                     "list_month": "2026-0" + str(1 + i % 9), "list_kind": "spurious" if spurious else "nsq",
                     "list_level": "central", "entry_type": "SPURIOUS" if spurious else "NSQ", "result": "Assay",
                     "reported_by": "Test laboratory", "source_title": "Unit-test fixture list",
                     "source_url": "https://example.invalid/list", "source_sha256": "0" * 64, "flags": [],
                     "status": "valid", "removed_at": None, "row_no": i + 1})
    return rows


def fake_perception(manifest, folder, refresh=False, log=None):
    """Perfect reader of the rendered text, shaped like pack_tools.extract_fields output."""
    out = {}
    for item in manifest["items"]:
        r = item["rendered"]
        out[item["id"]] = {"fields": {"batch": r["batch"], "product": r["brand"] or r["product"],
                                      "product_text": f"{r['brand']} {r['product']}".strip(), "brand": r["brand"],
                                      "mfg": r["mfg"], "exp": r["exp"], "maker": r["maker"],
                                      "source": "qr" if item["qr"] else "ocr", "confirmed": bool(item["qr"])},
                           "lines": [], "engine": "fake", "error": "", "seconds": 0.5}
    return out


def test_allocation_matches_registered_mix():
    assert golden.allocate(60) == golden.MIX
    for n in (8, 16, 33, 200):
        assert sum(golden.allocate(n).values()) == n


def test_manifest_is_deterministic_and_truthful():
    alerts = fixture_alerts()
    index = {a["batch_key"]: a for a in alerts}
    first, again, other = (golden.build_manifest(alerts, n=16, seed=s) for s in (1, 1, 7))
    assert first == again
    assert [i["alert_id"] for i in first] != [i["alert_id"] for i in other]
    for item in first:
        assert item["truth"] == golden.TRUTH[item["scenario"]]
        printed, rendered = batch_key(item["printed"]["batch"]), batch_key(item["rendered"]["batch"])
        if item["scenario"] == "misread":
            assert printed in index and rendered not in index
            diffs = [(a, b) for a, b in zip(printed, rendered) if a != b]
            assert len(diffs) == 1 and diffs[0][0] in CONFUSABLE[diffs[0][1]]
        elif item["scenario"] == "sibling":
            assert rendered in index and printed not in index
        elif item["scenario"] == "genuine":
            assert printed not in index and not any(v in index for v, _ in confusion_variants(printed, 2))
        elif item["scenario"] == "collision":
            assert printed in index and item["printed"]["product"] != index[printed]["product"]
        else:
            assert printed == rendered and printed in index
        if item["scenario"] == "qr":
            assert f"(10){printed}" in item["qr"]


def test_generate_writes_marked_images(tmp_path):
    manifest = golden.generate(n=8, seed=1, alerts=fixture_alerts(), out=tmp_path)
    assert manifest["banner"] == "DEMO PROP - NOT A MEDICINE"
    saved = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert saved["n"] == 8 == len(list(tmp_path.glob("*.png")))
    with Image.open(tmp_path / saved["items"][0]["image"]) as image:
        assert image.size == (1400, 900)
        assert image.getpixel((80, 75)) == (255, 231, 224)  # banner strip


def test_statistics_helpers():
    assert evaluate.wilson(0, 0) is None
    low, high = evaluate.wilson(0, 8)
    assert low == 0 and 0.32 < high < 0.33
    assert evaluate.wilson(8, 8)[1] == 1.0
    assert evaluate.mcnemar_exact(0, 8) == 0.007812
    assert evaluate.mcnemar_exact(3, 3) == 1.0


def test_oracle_answers_from_printed_truth():
    printed = {"batch": "AB123", "product": "X Tablets", "brand": "", "maker": "M Ltd", "mfg": "2025-01", "exp": "2027-12"}
    assert evaluate.oracle_answer({"kind": "confirm_batch"}, printed)["typed"] == "AB123"
    assert evaluate.oracle_answer({"kind": "confirm_char", "listed": "AB123"}, printed) == {"choice": "listed"}
    assert evaluate.oracle_answer({"kind": "confirm_char", "listed": "A8123"}, printed) == {"choice": "printed"}
    assert evaluate.oracle_answer({"kind": "confirm_field", "field": "exp", "listed": "2027-12"}, printed) == {"choice": "listed"}
    assert evaluate.oracle_answer({"kind": "box_photo"}, printed)["fields"]["maker"] == "M Ltd"


def test_research_run_end_to_end_rules_arms(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", None)
    db.init_db(tmp_path / "eval.db")
    monkeypatch.setattr(evaluate, "perceive", fake_perception)
    report = evaluate.run_research(arms=["baseline", "agent_rules"], hitl=["oracle", "none"], seed=1, n=16,
                                   alerts=fixture_alerts(), eval_folder=tmp_path / "set", runs_dir=tmp_path / "runs",
                                   write_paper=True, paper_dir=tmp_path / "paper", results_dir=tmp_path / "results", log=lambda *_: None)
    oracle = report["results"]["oracle"]
    base, rules = oracle["baseline"]["summary"], oracle["agent_rules"]["summary"]
    assert base["far_collision"]["rate"] == 1.0 and rules["far_collision"]["rate"] == 0.0
    assert base["by_scenario"]["misread"]["correct"] == 0 and rules["by_scenario"]["misread"]["correct"] == 2
    assert rules["safety_violations"] == 0 and base["safety_violations"] == 0
    assert report["results"]["none"]["agent_rules"]["summary"]["questions_per_pack"] > 0
    assert oracle["agent_rules"]["vs_baseline"]["decision_rule"]["adopt"] is True
    assert {p["prediction"].split(":")[0] for p in report["predictions"]} >= {"Clean packs", "Collisions", "Misreads"}
    macros = (tmp_path / "paper" / "results.tex").read_text(encoding="utf-8")
    assert "\\newcommand{\\ResRulesOracleHitRecall}" in macros and "\\ResBaseSkipFARCollision" in macros
    assert "\\begin{tabular}" in (tmp_path / "paper" / "results_tables.tex").read_text(encoding="utf-8")
    assert (tmp_path / "results" / "eval_seed1.md").is_file()
    md = (tmp_path / "runs").glob("eval_2*.md")
    assert any("Table C" in path.read_text(encoding="utf-8") for path in md)
    # Re-running only one policy keeps the other policy's results in the combined store.
    again = evaluate.run_research(arms=["baseline"], hitl=["none"], seed=1, n=16, alerts=fixture_alerts(),
                                  eval_folder=tmp_path / "set", runs_dir=tmp_path / "runs", write_paper=False, log=lambda *_: None)
    assert "agent_rules" in again["results"]["oracle"]
