from __future__ import annotations

import json
from pathlib import Path


def project_paths(project_root: Path) -> dict[str, Path]:
    return {
        "root": project_root,
        "config": project_root / "config" / "defaults.json",
        "history": project_root / "data" / "forward_pe_history.csv",
        "state": project_root / "state" / "strategy_state.json",
        "output": project_root / "output" / "latest_report.txt",
    }


def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)
