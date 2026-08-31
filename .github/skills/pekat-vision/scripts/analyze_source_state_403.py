"""Read-only, exact-4.0.3 stored source-state summary.

Only the sibling restricted Pickle parser is used.  This helper never opens
PEKAT, Socket.IO, a browser, or a project writer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from analyze_flow_database import UnsafePickleError, restricted_loads


def _load_database(project: Path, name: str) -> dict[str, Any]:
    path = project / "database" / name
    if not path.is_file():
        raise ValueError(f"missing database/{name}")
    value = restricted_loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError(f"database/{name} root is not an object")
    return value


def analyze_source_state(project: Path) -> dict[str, Any]:
    project = project.resolve()
    package_path = project / "pekat_package.json"
    try:
        package = json.loads(package_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("invalid or missing pekat_package.json") from error
    if not isinstance(package, dict) or package.get("version") != "4.0.3":
        raise ValueError("source-state helper requires exact PEKAT 4.0.3")
    camera = _load_database(project, "camera.db")
    running = _load_database(project, "running.db")
    watcher = camera.get("imageFolderWatcher") if isinstance(camera.get("imageFolderWatcher"), dict) else {}
    mode = watcher.get("simulationMode")
    return {
        "read_only": True,
        "version": "4.0.3",
        "stored_persistent_evidence": {
            "source_provider": camera.get("provider"),
            "current_camera": camera.get("currentCamera"),
            "camera_status": camera.get("cameraStatus"),
            "folder": {
                "path": watcher.get("folderPath"),
                "analyze_existing": watcher.get("analyzeExisting"),
                "delete_images": watcher.get("autoDelete"),
                "production_simulation": "simulation" if mode is True else "production" if mode is False else "unknown",
                "simulationMode": mode,
            },
            "analyze_incoming": running.get("processing"),
            "auto_capture_save": running.get("save"),
            "live_stream_persistent": camera.get("cameraIsRunning"),
            "configured_port": package.get("port"),
        },
        "runtime_checks": {
            "project_process": "not_checked",
            "port_listening": "not_checked",
            "ping": "not_checked",
            "camera_connection": "unknown_live_state",
            "camera_acquisition": "unknown_live_state",
            "flow_evaluation": "unknown_live_state",
        },
        "derived_interpretation": {
            "running_processing_means": "Analyze incoming images",
            "running_save_means": "Save incoming images / auto capture",
            "simulationMode_scope": "Folder source only; not a project-wide Production/Simulation control",
            "persistent_not_runtime_truth": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only exact PEKAT 4.0.3 stored source-state summary")
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(analyze_source_state(args.project), ensure_ascii=False, indent=2))
    except (ValueError, UnsafePickleError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
