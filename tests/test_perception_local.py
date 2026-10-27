"""Real local reads of synthetic fixtures plus deterministic extraction tests."""
import sys
from pathlib import Path
import pytest
from core import config, db
from core.pack_tools import extract_fields, read_pack, validate_image
from core.props import demo_cases, render_demo
from core.crops import batch_line_crop, char_boxes, glyph_crops
from core.textutils import parse_qr_payload

def test_qr_parse_grounded_gs1():
    fields = parse_qr_payload("(01)12345678901234(10)SYN2408B(17)270731")
    assert fields["batch"] == "SYN2408B"
    assert fields["exp"] == "2027-07"

def test_extract_uses_printed_labels():
    fields = extract_fields(["Synthetic Medicine Tablets", "Batch No: SYN2408B", "Mfg: 08/2024 Exp: 07/2027", "Manufactured by: Example Labs"])
    assert fields["batch"] == "SYN2408B"
    assert fields["mfg"] == "2024-08" and fields["exp"] == "2027-07"
    assert fields["maker"] == "Example Labs"
    assert fields["source"] == "ocr" and fields["confirmed"] is False

def test_missing_batch_is_not_guessed():
    fields = extract_fields(["Lumera Tablets", "20 mg", "MRP: 240.80", "Keep away from children"])
    assert fields["batch"] == ""

def test_grounded_iso_dates_are_retained():
    fields = extract_fields(["Batch No: SYN2408B", "Mfg: 2024-08 Exp: 2027-07"])
    assert fields["mfg"] == "2024-08" and fields["exp"] == "2027-07"

def test_synthetic_cases_are_isolated():
    cases = demo_cases()
    assert len(cases) == 11
    assert all(case["synthetic"] for case in cases)
    assert all(alert["synthetic"] and not alert["source_url"] for case in cases for alert in case["alerts"])

def test_decode_invalid_image(tmp_path):
    bad = tmp_path / "bad.png"
    bad.write_text("not an image")
    with pytest.raises(ValueError, match="could not be read"):
        validate_image(bad)

def test_crops_are_real_images(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    path = render_demo("01")
    box = [[120, 360], [650, 360], [650, 415], [120, 415]]
    assert batch_line_crop(path, box).exists()
    boxes = char_boxes(box, "Batch No: LM2408B", (10, 17))
    assert len(boxes) == 7
    assert all(path.exists() for path in glyph_crops(path, boxes))

@pytest.mark.skipif(sys.platform != "darwin", reason="Real Apple Vision OCR requires macOS")
def test_real_ocr_on_clean_synthetic_prop(tmp_path, monkeypatch):
    pytest.importorskip("Vision")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    result = read_pack(render_demo("01"))
    if not result["lines"]:
        pytest.skip("Apple Vision cannot access its local recognition service in this sandbox")
    assert result["fields"]["batch"] == "LM2408B"
    assert result["fields"]["product"] == "Lumera Tablets"
    assert result["fields"]["maker"] == "Example Laboratories"
    assert result["fields"]["mfg"] == "2024-08"
    assert result["fields"]["exp"] == "2027-07"
    assert result["boxes"]


@pytest.mark.skipif(sys.platform != "darwin", reason="Native barcode recognition requires macOS")
def test_real_qr_on_synthetic_gs1(tmp_path):
    pytest.importorskip("Vision")
    qrcode = pytest.importorskip("qrcode")
    from core.pack_tools import decode_qr
    path = tmp_path / "synthetic-gs1.png"
    qrcode.make("(01)12345678901234(10)SYN2408B(17)270731").save(path)
    result = decode_qr(path)
    if not result["found"]:
        pytest.skip("Local barcode engine is unavailable in this sandbox")
    assert result["fields"]["batch"] == "SYN2408B"
    assert result["fields"]["exp"] == "2027-07"
