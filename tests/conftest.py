"""Shared test setup: the vision model is off unless a test turns it on (tests never reach a real Ollama)."""
import pytest

from core import config


@pytest.fixture(autouse=True)
def vision_model_off(monkeypatch):
    monkeypatch.setattr(config, "VLM_MODEL", "")
