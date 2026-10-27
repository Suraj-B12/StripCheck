"""Clearly labelled synthetic demo fixtures, never inserted into the live index."""
from copy import deepcopy
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from core import config

def _base_alert():
    return {"id": 10001, "product": "Lumera Tablets", "brand": "", "batch_raw": "LM2408B", "batch_key": "LM2408B",
            "mfg": "2024-08", "exp": "2027-07", "maker_raw": "Example Laboratories", "maker_name": "Example Laboratories",
            "list_month": "2026-09", "list_kind": "nsq", "list_level": "synthetic", "entry_type": "NSQ",
            "result": "Synthetic example: dissolution", "reported_by": "Demonstration laboratory",
            "source_title": "Synthetic demonstration fixture", "source_url": "", "source_sha256": "",
            "flags": ["synthetic"], "synthetic": True, "removed_at": None}

def _fields():
    return {"batch": "LM2408B", "product": "Lumera Tablets", "product_text": "Lumera Tablets", "brand": "",
            "mfg": "2024-08", "exp": "2027-07", "maker": "Example Laboratories", "source": "ocr", "confirmed": False}

def demo_cases():
    rows = []
    def add(id, name, description, fields, alerts, expected, answers=None):
        rows.append({"id": id, "name": name, "title": name, "description": description, "synthetic": True,
                     "fields": fields, "alerts": alerts, "expected": expected, "answers": answers or [],
                     "image_url": f"/api/demo/cases/{id}/image"})
    add("01", "Listed batch", "A clear pack read matches a synthetic quality alert. Confirm its printed batch.",
        _fields(), [_base_alert()], "FLAGGED", [{"typed": "LM2408B"}])
    f = _fields(); f["batch"] = "LM7777X"
    add("02", "No match on loaded lists", "A readable batch does not occur in this isolated example index.", f, [_base_alert()], "NOT_LISTED")
    f = _fields(); f["batch"] = "LM24088"
    add("03", "One character matters", "An OCR read confuses the final B with 8. The printed character decides the result.",
        f, [_base_alert()], "FLAGGED", [{"choice": "LM2408B"}])
    alert = _base_alert(); alert.update({"entry_type": "SPURIOUS", "list_kind": "spurious", "result": "Synthetic spurious alert", "maker_name": ""})
    add("04", "Spurious-list example", "A synthetic entry demonstrates the stronger alert, with batch confirmation.",
        _fields(), [alert], "SUSPECTED_FAKE", [{"typed": "LM2408B"}])
    f = _fields(); f.update({"maker": "", "mfg": "", "exp": ""})
    add("05", "Need the carton", "The batch and product match, but the pack needs manufacturer or date evidence.",
        f, [_base_alert()], "CANT_VERIFY", [{"choice": "cant_tell"}])
    f = _fields(); f.update({"product": "Coralin Capsules", "product_text": "Coralin Capsules"})
    add("06", "Same code, different product", "A shared batch code must not cause an alert for another product.", f, [_base_alert()], "NOT_LISTED")
    f = _fields(); f.update({"product": "", "product_text": "", "brand": ""})
    add("07", "Product text missing", "A batch alone is not enough to connect the pack to a listed product.",
        f, [_base_alert()], "CANT_VERIFY", [{"choice": "cant_tell"}])
    f = _fields(); f["batch"] = ""
    add("08", "Read the batch together", "When a batch is obscured, enter the exact printed text to continue.",
        f, [_base_alert()], "FLAGGED", [{"typed": "LM2408B"}])
    f = _fields(); f["exp"] = "2027-01"
    add("09", "Dates disagree", "The product and batch agree, but the printed expiry needs a closer look.",
        f, [_base_alert()], "CANT_VERIFY", [{"choice": "2027-01"}])
    add("10", "Neighbouring batch", "Correct the proposed batch to LM2408R. An alert for LM2408B must not follow it.",
        _fields(), [_base_alert()], "NOT_LISTED", [{"typed": "LM2408R"}])
    f = {"batch": "", "product": "", "product_text": "", "brand": "", "mfg": "", "exp": "", "maker": "", "source": "ocr", "confirmed": False}
    add("11", "Unreadable pack", "Missing evidence ends in an honest incomplete result, never an invented reading.",
        f, [_base_alert()], "CANT_VERIFY", [{"choice": "cant_tell"}])
    return deepcopy(rows)

def _font(size):
    for font in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(font, size=size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)

def render_demo(id):
    case_id = str(id).split("_")[0].zfill(2)
    case = next((case for case in demo_cases() if case["id"] == case_id), None)
    if case is None:
        raise ValueError("Unknown demonstration case")
    dest = config.DATA_DIR / "props" / f"{case_id}_synthetic.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1400, 900), "#edf0fa")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((55, 50, 1345, 850), radius=44, fill="#ffffff", outline="#d0d6e8", width=3)
    draw.rounded_rectangle((90, 85, 1310, 160), radius=18, fill="#e9e4ff")
    draw.text((120, 105), "SYNTHETIC DEMONSTRATION · NOT FOR MEDICAL USE", fill="#554581", font=_font(30))
    f = case["fields"]
    draw.text((120, 230), f["product"] or "[Product text obscured]", fill="#172139", font=_font(76))
    for index, text in enumerate((f"Batch No: {f['batch'] or '[obscured]'}",
                                  f"Mfg: {f['mfg'] or '[obscured]'}   Exp: {f['exp'] or '[obscured]'}",
                                  f"Manufactured by: {f['maker'] or '[obscured]'}")):
        # Dates are rendered in the printed MM/YYYY form for the actual OCR pipeline.
        for key in ("mfg", "exp"):
            if f[key]:
                text = text.replace(f[key], f[key][5:7] + "/" + f[key][:4])
        draw.text((125, 365 + index * 95), text, fill="#25334e", font=_font(43 if index < 2 else 35))
    draw.line((120, 710, 1280, 710), fill="#dfe3ef", width=2)
    draw.text((125, 755), f"StripCheck / fictional fixture {case_id}", fill="#65718b", font=_font(28))
    image.save(dest)
    return dest

def generate_demo():
    cases = demo_cases()
    for case in cases:
        case["path"] = str(render_demo(case["id"]))
    return cases
