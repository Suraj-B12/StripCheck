"""Bad optional numeric settings must not prevent local startup."""
import importlib.util
from pathlib import Path
import pytest
from core import config


@pytest.mark.parametrize('value', ['not-a-number', 'nan', 'inf', '-inf', '', '10000000000000000000000000000000000', '-100'])
def test_numeric_configuration_is_finite_and_bounded(monkeypatch, value):
    for name in ('SYNC_DELAY', 'NETWORK_TIMEOUT', 'LLM_TIMEOUT', 'VLM_TIMEOUT'):
        monkeypatch.setenv(f'STRIPCHECK_{name}', value)
    spec = importlib.util.spec_from_file_location('isolated_config', Path(config.__file__))
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    assert 1.5 <= settings.SYNC_DELAY <= 60
    assert 3 <= settings.NETWORK_TIMEOUT <= 60
    assert 1 <= settings.LLM_TIMEOUT <= 90
    assert 1 <= settings.VLM_TIMEOUT <= 60
