"""Real RapidOCR / zxing-cpp reads of synthetic Pillow renders (Windows and Linux; skipped without the engines)."""
import importlib.util
import time
from pathlib import Path
import pytest
from PIL import Image, ImageDraw, ImageFont
from core import config, pack_tools as pack

def _rapid_ready():
    spec = importlib.util.find_spec("rapidocr")
    if spec is None or importlib.util.find_spec("onnxruntime") is None:
        return False
    models = Path(spec.origin).parent / "models"
    return any(models.glob("*.onnx"))

needs_rapid = pytest.mark.skipif(not _rapid_ready(), reason="RapidOCR with local weights is not installed")

@pytest.fixture(autouse=True)
def _local_only(monkeypatch):
    # Exercise the RapidOCR path even where Apple Vision or Tesseract exist.
    def no_vision(*args, **kwargs):
        raise RuntimeError("Apple Vision disabled for this test")
    monkeypatch.setattr(pack, "_vision_read_bounded", no_vision)
    monkeypatch.setattr(pack.shutil, "which", lambda name: None)

def _render(path, lines, fg="#1b2540", bg="#ffffff", size=44):
    image = Image.new("RGB", (1200, 120 + 100 * len(lines)), bg)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=size)
    for index, text in enumerate(lines):
        draw.text((60, 60 + index * 100), text, fill=fg, font=font)
    image.save(path)
    return path

PACK = ["Corvexa Tablets", "Batch No: SYN2408B", "Mfg: 08/2024   Exp: 07/2027",
        "Manufactured by: Example Laboratories"]

@needs_rapid
def test_rapidocr_reads_batch_dates_and_maker(tmp_path):
    started = time.monotonic()
    result = pack.read_pack(_render(tmp_path / "pack.png", PACK))
    fields = result["fields"]
    assert result["engine"] == pack.RAPID_LABEL
    assert fields["batch"] == "SYN2408B" and fields["source"] == "ocr" and fields["confirmed"] is False
    assert fields["mfg"] == "2024-08" and fields["exp"] == "2027-07"
    assert fields["maker"] == "Example Laboratories"
    assert fields["product"] == "Corvexa Tablets"
    assert result["boxes"] and time.monotonic() - started < 60

@needs_rapid
def test_rapidocr_reads_demo_prop(tmp_path, monkeypatch):
    from core.props import render_demo
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    fields = pack.read_pack(render_demo("01"))["fields"]
    assert (fields["batch"], fields["mfg"], fields["exp"]) == ("LM2408B", "2024-08", "2027-07")
    assert fields["maker"] == "Example Laboratories" and fields["product"] == "Lumera Tablets"

@needs_rapid
def test_obscured_fields_stay_empty(tmp_path):
    lines = ["[Product text obscured]", "Batch No: [obscured]", "Mfg: [obscured]  Exp: [obscured]", "Manufactured by: [obscured]"]
    result = pack.read_pack(_render(tmp_path / "obscured.png", lines))
    fields = result["fields"]
    assert fields["batch"] == "" and fields["maker"] == "" and fields["product"] == ""
    assert fields["mfg"] == "" and fields["exp"] == ""
    assert any("batch" in warning.lower() for warning in result["warnings"])

@needs_rapid
def test_faint_print_uses_enhanced_reread(tmp_path):
    path = _render(tmp_path / "faint.png", PACK, fg="#ebebeb", bg="#f0f0f0")
    assert pack.read_pack(path)["fields"]["batch"] == "SYN2408B"

@needs_rapid
def test_engine_is_reused_and_worker_recovers(tmp_path):
    path = _render(tmp_path / "pack.png", PACK[:2])
    assert pack.ocr_read(path)
    worker = pack._rapid_proc
    assert worker is not None and worker.poll() is None
    assert pack.ocr_read(path) and pack._rapid_proc is worker
    pack._stop_rapid()
    assert pack.ocr_read(path) and pack._rapid_proc is not worker

@needs_rapid
def test_worker_overrun_is_killed_and_falls_back(tmp_path):
    path = _render(tmp_path / "pack.png", PACK)
    pack._stop_rapid()  # a cold start (model load) cannot finish inside the 0.1 s minimum wait
    with pytest.raises(OSError):
        pack._rapid_request(path, 0.001)
    assert pack._rapid_proc is None
    assert pack.ocr_read(path)

def test_glued_labels_are_split_without_inventing_batches():
    fields = pack.extract_fields(["Batch No:LM2408BMfg:08/2024Exp:07/2027"])
    assert (fields["batch"], fields["mfg"], fields["exp"]) == ("LM2408B", "2024-08", "2027-07")
    assert pack.extract_fields(["Pilot: 123ABC"])["batch"] == ""
    assert pack.extract_fields(["Manufactured by: [obscured]"])["maker"] == ""

def test_gs1_datamatrix_and_qr_decode(tmp_path):
    zxingcpp = pytest.importorskip("zxingcpp")
    qrcode = pytest.importorskip("qrcode")
    import numpy as np
    qrcode.make("(01)12345678901234(10)SYN2408B(17)270731").save(tmp_path / "qr.png")
    result = pack.decode_qr(tmp_path / "qr.png")
    assert result["fields"]["batch"] == "SYN2408B" and result["fields"]["exp"] == "2027-07"
    # Raw FNC1 group separator, as printed by many GS1 DataMatrix encoders.
    symbol = zxingcpp.create_barcode("\x1d01123456789012341727073110SYN2408B", zxingcpp.BarcodeFormat.DataMatrix)
    Image.fromarray(np.array(zxingcpp.write_barcode_to_image(symbol, scale=8))).save(tmp_path / "dm.png")
    result = pack.decode_qr(tmp_path / "dm.png")
    assert result["fields"]["batch"] == "SYN2408B" and result["fields"]["exp"] == "2027-07"

def test_unlabelled_barcode_is_not_a_batch(tmp_path):
    zxingcpp = pytest.importorskip("zxingcpp")
    import numpy as np
    symbol = zxingcpp.create_barcode("SYN2408B", zxingcpp.BarcodeFormat.DataMatrix)
    Image.fromarray(np.array(zxingcpp.write_barcode_to_image(symbol, scale=8))).save(tmp_path / "plain.png")
    result = pack.decode_qr(tmp_path / "plain.png")
    assert result["found"] and "batch" not in result["fields"]
