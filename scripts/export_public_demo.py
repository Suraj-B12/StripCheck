"""Export only authored synthetic API replays for the static public website.

Run as a separate process: paths are isolated before any application import.
No official snapshots, local checks, photos, or network requests are used.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "web/src/lib/public-demo-fixtures.json"


def normalize(value):
    if isinstance(value, dict):
        return {
            key: (0 if key == "ms" else normalize(item))
            for key, item in value.items()
            if key not in {"thread_id", "created_at", "updated_at", "latency_ms", "duration_ms", "image_url"}
        }
    if isinstance(value, list):
        return [normalize(item) for item in value]
    return value


def export():
    with tempfile.TemporaryDirectory(prefix="stripcheck-public-demo-") as temporary:
        isolated = Path(temporary)
        # These overrides precede importing config and server.app's module-level app.
        os.environ.update({
            "STRIPCHECK_DATA_DIR": str(isolated / "data"),
            "STRIPCHECK_DB_PATH": str(isolated / "demo.db"),
            "STRIPCHECK_RUNS_DIR": str(isolated / "runs"),
            "STRIPCHECK_OFFLINE": "1",
            "STRIPCHECK_LANG": "en",
            "STRIPCHECK_PLANNER": "rules",
        })
        sys.path.insert(0, str(ROOT))
        from fastapi.testclient import TestClient
        from core import config, db
        from core.props import demo_cases
        from server.app import create_app

        assert config.DB_PATH.is_relative_to(isolated)
        assert config.DATA_DIR.is_relative_to(isolated)
        assert config.RUNS_DIR.is_relative_to(isolated)
        cases, alerts, seen = [], [], set()
        headers = {"Accept": "application/json"}

        def no_network(*_args, **_kwargs):
            raise AssertionError("Public demo export must never connect to a network.")

        with patch.object(socket.socket, "connect", no_network), TestClient(create_app(config.DB_PATH)) as client:
            assert client.get("/api/stats").json()["alerts"] == 0
            assert client.get("/api/sources").json()["items"] == []
            definitions = demo_cases()
            assert len(definitions) == 11
            for case in definitions:
                assert case["synthetic"] and all(row["synthetic"] for row in case["alerts"])
                response = client.post("/api/demo/checks", json={"case_id": case["id"]}, headers=headers)
                response.raise_for_status()
                snapshot = response.json()
                snapshots = [normalize(snapshot)]
                answers = case.get("answers", [])
                assert isinstance(answers, list) and len(answers) <= 8
                for answer in answers:
                    assert snapshot["status"] == "waiting", case["id"]
                    response = client.post(f"/api/checks/{snapshot['thread_id']}/resume", json=answer, headers=headers)
                    response.raise_for_status()
                    snapshot = response.json()
                    snapshots.append(normalize(snapshot))
                assert snapshot["status"] == "done", case["id"]
                assert snapshot["final"]["label"] == case["expected"], case["id"]
                assert all(item["demo"] for item in snapshots)
                assert snapshot["final"]["demo"]
                assert all(citation["synthetic"] and not citation["url"] for citation in snapshot["final"]["citations"])
                cases.append({
                    "definition": normalize({key: value for key, value in case.items() if key not in {"answers", "alerts"}}),
                    "answers": answers,
                    "snapshots": snapshots,
                })
                for row in case["alerts"]:
                    key = json.dumps(row, sort_keys=True)
                    if key not in seen:
                        seen.add(key)
                        # The catalogue has separate IDs for the quality/spurious fixtures.
                        alerts.append({**row, "id": len(alerts) + 1, "fixture_row_id": row["id"]})

            response = client.post("/api/eval/quick", json={}, headers=headers)
            response.raise_for_status()
            report = normalize(response.json())
            assert report["passed"] == len(cases) and report["failed"] == 0
            assert client.get("/api/stats").json()["alerts"] == 0
            assert db.list_documents("sources") == []

        digest = hashlib.sha256()
        for path in sorted((ROOT / "core").glob("*.py")) + [ROOT / "server/app.py"]:
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(path.read_bytes())
        return {
            "version": 1, "synthetic": True, "replay_only": True,
            "provenance": {"generator": "scripts/export_public_demo.py", "verdict_templates": "core/templates.py", "engine_sha256": digest.hexdigest()},
            "notice": "Precomputed synthetic examples from the Python checking engine. No real medicine is checked on this website.",
            "cases": cases, "alerts": alerts,
            "evaluation": {**report, "replay": True, "precomputed": True},
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the committed synthetic replay differs from the current engine.")
    args = parser.parse_args()
    content = json.dumps(export(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    assert len(content.encode()) < 512 * 1024, "Public fixture size exceeded its bound."
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit("Synthetic replay differs. Run scripts/export_public_demo.py to regenerate it.")
        print("Public synthetic replay verified: 11 cases; no live data or network.")
    else:
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"Exported 11 synthetic API replays ({len(content.encode())} bytes).")


if __name__ == "__main__":
    main()
