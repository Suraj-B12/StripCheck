"""Golden evaluation set built from real alert rows in the local database (spec v2 section 15.4).

Each item renders a synthetic carton marked DEMO PROP - NOT A MEDICINE. The manifest records the
printed truth, the rendered text and the truth label. Deterministic from the seed.
"""
import hashlib
import json
import random
import re
from pathlib import Path

from core import config, db
from core.textutils import CONFUSABLE, batch_key, confusion_variants, product_coverage
from rapidfuzz import fuzz

# Scenario weights for the default mix (n=60 gives 8 per scenario and 4 siblings).
MIX = {"clean": 8, "glare": 8, "misread": 8, "qr": 8, "spurious": 8, "collision": 8, "genuine": 8, "sibling": 4}
TRUTH = {"clean": "FLAGGED", "glare": "FLAGGED", "misread": "FLAGGED", "qr": "FLAGGED", "spurious": "SUSPECTED_FAKE",
         "collision": "NOT_LISTED", "genuine": "NOT_LISTED", "sibling": "NOT_LISTED"}
KEY_RE = re.compile(r"[A-Z0-9]{5,12}")


def eval_dir(seed):
    return config.DATA_DIR / "eval" / f"seed{int(seed)}"


def allocate(n):
    """Largest-remainder split of n over MIX, stable order."""
    total = sum(MIX.values())
    raw = {k: n * v / total for k, v in MIX.items()}
    counts = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: (-(raw[k] - counts[k]), list(MIX).index(k)))[: n - sum(counts.values())]:
        counts[k] += 1
    return counts


def _usable(row):
    return (row.get("status", "valid") == "valid" and not row.get("removed_at") and row.get("product")
            and KEY_RE.fullmatch(row.get("batch_key") or "") and len(row["product"]) <= 70)


CORPORATE = set("m s ltd limited pvt private pharma pharmaceutical pharmaceuticals laboratories laboratory labs lab "
                "healthcare health care industries industry the inc co company life sciences science remedies formulations".split())


def _maker_differs(a, b):
    """Maker names differ once common corporate words are removed."""
    core = lambda s: " ".join(t for t in re.sub(r"[^a-z0-9 ]", " ", (s or "").lower()).split() if t not in CORPORATE)
    return fuzz.token_set_ratio(core(a), core(b)) < 70


def _variant_free(key, index):
    """True when neither the key nor any of its one- or two-substitution confusion variants is listed."""
    return key not in index and not any(v in index for v, _ in confusion_variants(key, 2))


def _one_sub(key, index, rng, need_unlisted=True):
    """A one-character confusable substitution of key that is not itself listed (or None)."""
    options = [(i, c) for i, ch in enumerate(key) for c in CONFUSABLE.get(ch, "")]
    rng.shuffle(options)
    for i, c in options:
        variant = key[:i] + c + key[i + 1:]
        if not need_unlisted or variant not in index:
            return variant, (i, key[i], c)
    return None, None


def _invent_key(template, index, rng):
    """Same shape as a real key (letters stay letters, digits stay digits), variant-free in the index."""
    for _ in range(200):
        key = "".join(rng.choice("ABEFHKMNPRUVWXY") if ch.isalpha() else rng.choice("0123456789") for ch in template)
        if _variant_free(key, index):
            return key
    return None


def _gs1(batch, mfg, exp, rng):
    gtin = "089" + "".join(rng.choice("0123456789") for _ in range(11))
    yymm = lambda v: f"{v[2:4]}{v[5:7]}01" if v else ""
    payload = f"(01){gtin}(10){batch}"
    if mfg:
        payload += f"(11){yymm(mfg)}"
    if exp:
        payload += f"(17){yymm(exp)}"
    return payload


def _pack(row, batch=None):
    return {"product": row["product"], "brand": row.get("brand") or "", "batch": batch or row["batch_key"],
            "mfg": row.get("mfg") or "", "exp": row.get("exp") or "", "maker": row.get("maker_name") or ""}


def build_manifest(alerts, n=60, seed=7):
    """Choose items from real rows. Returns a list of manifest items (no images yet)."""
    rng = random.Random(f"stripcheck-golden-{int(seed)}")
    index = {}
    for row in alerts:
        index.setdefault(row["batch_key"], []).append(row)
    rows = sorted((r for r in alerts if _usable(r)), key=lambda r: r["id"])
    unique = lambda r: len(index.get(r["batch_key"], [])) == 1
    nsq = [r for r in rows if r["entry_type"] == "NSQ" and r.get("mfg") and r.get("exp") and r.get("maker_name")
           and unique(r) and "non_drug" not in (r.get("flags") or [])]
    spurious = [r for r in rows if r["entry_type"] == "SPURIOUS" and unique(r)]
    rng.shuffle(nsq)
    rng.shuffle(spurious)
    used, items = set(), []
    counts = allocate(n)

    def take(pool, ok=lambda r: True):
        for row in pool:
            if row["id"] not in used and ok(row):
                used.add(row["id"])
                return row
        return None

    def add(scenario, printed, rendered, alert, extra=None):
        item = {"id": f"s{int(seed)}_{len(items) + 1:03d}_{scenario}", "scenario": scenario, "truth": TRUTH[scenario],
                "alert_id": alert["id"] if alert else None, "printed": printed, "rendered": rendered,
                "qr": "", "degrade": None, "note": ""}
        item.update(extra or {})
        items.append(item)

    for scenario, count in counts.items():
        made = 0
        for _ in range(count * 40):
            if made >= count:
                break
            if scenario in ("clean", "glare", "qr"):
                row = take(nsq)
                if not row:
                    break
                printed = _pack(row)
                extra = {}
                if scenario == "glare":
                    extra["degrade"] = {"kind": "glare" if made % 2 == 0 else "blur", "severity": 1 + made % 2, "seed": rng.randint(0, 10 ** 6)}
                if scenario == "qr":
                    extra["qr"] = _gs1(printed["batch"], printed["mfg"], printed["exp"], rng)
                add(scenario, printed, dict(printed), row, extra)
            elif scenario == "spurious":
                row = take(spurious)
                if not row:
                    break
                add(scenario, _pack(row), _pack(row), row)
            elif scenario == "misread":
                row = take(nsq, lambda r: any(ch in CONFUSABLE for ch in r["batch_key"]))
                if not row:
                    break
                variant, sub = _one_sub(row["batch_key"], index, rng)
                if not variant:
                    continue
                # Simulated OCR error: the image shows the misread string; the printed truth is the listed key.
                rendered = _pack(row, variant)
                add(scenario, _pack(row), rendered, row, {"note": f"simulated misread at position {sub[0] + 1}: {sub[1]} read as {sub[2]}"})
            elif scenario == "sibling":
                row = take(nsq, lambda r: any(ch in CONFUSABLE for ch in r["batch_key"]))
                if not row:
                    break
                sibling, sub = _one_sub(row["batch_key"], index, rng)
                if not sibling:
                    continue
                # The pack's true batch is an unlisted neighbour; the image shows the listed key (OCR adds a stroke).
                add(scenario, _pack(row, sibling), _pack(row), row,
                    {"note": f"true batch {sibling} is unlisted; simulated OCR read gives the listed {row['batch_key']}"})
            elif scenario == "collision":
                a = take(nsq)
                if not a:
                    break
                same_key = index.get(a["batch_key"], [])
                b = take(rows, lambda r: r["entry_type"] == "NSQ" and r.get("maker_name") and _maker_differs(r["maker_name"], a.get("maker_name"))
                         and all((product_coverage(x["product"], r["product"]) or 0) < 0.5 for x in same_key))
                if not b:
                    break
                printed = _pack(b, a["batch_key"])
                add(scenario, printed, dict(printed), a, {"note": f"batch of alert {a['id']} printed on the product and maker of alert {b['id']}", "donor_id": b["id"]})
            elif scenario == "genuine":
                row = take(rows, lambda r: r["entry_type"] == "NSQ" and r.get("maker_name"))
                if not row:
                    break
                key = _invent_key(row["batch_key"], index, rng)
                if not key:
                    continue
                printed = _pack(row, key)
                add(scenario, printed, dict(printed), None, {"donor_id": row["id"], "note": "invented batch, no listed key within two confusable substitutions"})
            made += 1
    return items


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def generate(n=60, seed=7, alerts=None, out=None):
    """Write images and manifest.json under data/eval/seed<N>/. Idempotent for the same inputs."""
    from core.props import render_pack
    alerts = alerts if alerts is not None else db.all_alerts()
    if not alerts:
        raise ValueError("No alert rows in the local database; run ingest first")
    out = Path(out) if out else eval_dir(seed)
    out.mkdir(parents=True, exist_ok=True)
    items = build_manifest(alerts, n=n, seed=seed)
    for item in items:
        spec = dict(item["rendered"], qr=item["qr"], degrade=item["degrade"])
        path = render_pack(spec, out / f"{item['id']}.png")
        item["image"] = path.name
        item["image_sha256"] = _sha(path)
    manifest = {"seed": int(seed), "n": len(items), "requested_n": int(n), "mix": allocate(n),
                "alert_count": len(alerts), "banner": "DEMO PROP - NOT A MEDICINE",
                "note": "Rendered synthetic cartons with text copied from real CDSCO alert rows. Misread and sibling items simulate an OCR error by rendering the misread string; the manifest keeps the printed truth.",
                "items": items}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")
    return manifest


def load(seed=7, out=None):
    path = (Path(out) if out else eval_dir(seed)) / "manifest.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
