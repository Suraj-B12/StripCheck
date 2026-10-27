"""Synthetic image failures and malformed local-engine output have bounded fallbacks."""
import json
import subprocess
import time
from types import SimpleNamespace
import pytest
from PIL import Image
from core import config, pack_tools as pack


@pytest.fixture
def photo(tmp_path):
    path = tmp_path / 'synthetic.png'
    Image.new('RGB', (320, 200), 'white').save(path)
    return path


def line(text='Batch No: SYN2408B', **extra):
    return {'text': text, 'score': .9, 'box': [[10, 10], [200, 10], [200, 40], [10, 40]], 'engine': 'Synthetic stub', **extra}


@pytest.mark.parametrize('output', [None, {}, ['bad'], [{'text': 'x', 'box': None}], [line(box=[[float('nan'), 0]] * 4)], [line(score='bad')]])
def test_malformed_ocr_output_is_ignored(output):
    assert pack._normalize_lines(output, 320, 200) == []


def test_ocr_coordinates_are_clamped_and_scores_bounded():
    result = pack._normalize_lines([line(score=3, box=[[-1, -2], [400, 0], [400, 300], [0, 300]])], 320, 200)[0]
    assert result['score'] == 1
    assert all(0 <= x <= 320 and 0 <= y <= 200 for x, y in result['box'])


def test_barcode_selection_uses_batch_evidence_and_rejects_conflicts():
    result = pack._select_barcode([{'raw': 'https://example.invalid'}, {'raw': '(10)SYN2408B(17)279931'}])
    assert result['fields']['batch'] == 'SYN2408B' and 'exp' not in result['fields']
    result = pack._select_barcode([{'raw': '(10)SYN2408B'}, {'raw': '(10)SYN2408C'}])
    assert result['ambiguous'] and not result['fields']


def test_whole_photo_pipeline_decodes_only_once(photo, monkeypatch):
    original = pack.validate_image
    calls = []
    def validate(path):
        calls.append(path)
        return original(path)
    monkeypatch.setattr(pack, 'validate_image', validate)
    monkeypatch.setattr(pack, 'decode_qr', lambda path, **kwargs: pack._select_barcode([]))
    monkeypatch.setattr(pack, 'ocr_read', lambda path, **kwargs: [line()])
    result = pack.read_pack(photo)
    assert result['fields']['batch'] == 'SYN2408B'
    assert calls == [photo]


def test_qr_disagreement_updates_batch_provenance(photo, monkeypatch):
    monkeypatch.setattr(pack, 'decode_qr', lambda path, **kwargs: pack._select_barcode([{'raw': '(10)SYN2408C'}]))
    monkeypatch.setattr(pack, 'ocr_read', lambda path, **kwargs: [line()])
    fields = pack.read_pack(photo)['fields']
    assert fields['batch'] == 'SYN2408B' and not fields['confirmed']
    assert fields['provenance']['batch']['value'] == 'SYN2408B'
    assert fields['provenance']['batch']['source'] == 'ocr'


def test_expired_deadline_starts_no_engine(photo, monkeypatch):
    monkeypatch.setattr(pack.subprocess, 'run', lambda *args, **kwargs: pytest.fail('must not start another worker'))
    image = pack.validate_image(photo)
    assert pack.ocr_read(photo, _image=image, _deadline=time.monotonic() - 1) == []
    assert pack.decode_qr(photo, _image=image, _deadline=time.monotonic() - 1)['found'] is False


def test_malformed_worker_results_fall_back(photo, monkeypatch):
    monkeypatch.setattr(pack.subprocess, 'run', lambda *args, **kwargs: SimpleNamespace(stdout='null'))
    monkeypatch.setattr(pack.shutil, 'which', lambda name: None)
    assert pack.ocr_read(photo) == []
    assert pack.decode_qr(photo)['found'] is False


def test_barcode_receives_normalized_bounded_image(tmp_path, monkeypatch):
    photo = tmp_path / 'synthetic-large.png'
    Image.new('RGB', (5000, 3000), 'white').save(photo)
    sizes = []
    def run(args, **kwargs):
        with Image.open(args[-1]) as image:
            sizes.append(image.size)
        assert kwargs['timeout'] <= 20
        return SimpleNamespace(stdout='[]')
    monkeypatch.setattr(pack.subprocess, 'run', run)
    assert pack.decode_qr(photo)['found'] is False
    assert sizes == [(2400, 1440)]


def test_engine_timeout_has_manual_fallback(photo, monkeypatch):
    def run(*args, **kwargs):
        raise subprocess.TimeoutExpired('synthetic-worker', kwargs['timeout'])
    monkeypatch.setattr(pack.subprocess, 'run', run)
    monkeypatch.setattr(pack.shutil, 'which', lambda name: None)
    result = pack.read_pack(photo)
    assert result['fields']['batch'] == '' and result['warnings']


def test_upload_dimensions_and_size_fail_before_decode(photo, monkeypatch):
    monkeypatch.setattr(config, 'MAX_IMAGE_PIXELS', 100)
    with pytest.raises(ValueError, match='24 megapixels'):
        pack.validate_image(photo)
    monkeypatch.setattr(config, 'MAX_UPLOAD_BYTES', 10)
    with pytest.raises(ValueError, match='15 MB'):
        pack.validate_image(photo)


@pytest.mark.parametrize('box', [[], [float('nan'), 0, 10, 20], [20, 20, 10, 10], [[1, 2], [3, 4]], [400, 0, 500, 20]])
def test_invalid_crop_boxes_fail_cleanly(photo, tmp_path, box):
    from core.crops import batch_line_crop
    with pytest.raises(ValueError):
        batch_line_crop(photo, box, tmp_path / 'crop.png')
    assert not (tmp_path / 'crop.png').exists()


def test_many_glyph_crops_share_one_decode(photo, tmp_path, monkeypatch):
    from core.crops import glyph_crops
    original = pack.validate_image
    calls = []
    def validate(path):
        calls.append(path)
        return original(path)
    monkeypatch.setattr(pack, 'validate_image', validate)
    crops = glyph_crops(photo, [[10 + i * 5, 10, 15 + i * 5, 30] for i in range(12)], tmp_path)
    assert len(crops) == 12 and calls == [photo]
