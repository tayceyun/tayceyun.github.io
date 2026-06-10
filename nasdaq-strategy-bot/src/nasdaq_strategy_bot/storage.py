from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .models import StrategyState, TriggerState


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_state(state_path: Path, base_amounts: dict[str, float]) -> StrategyState:
    if not state_path.exists():
        state = StrategyState()
        _ensure_triggers(state, base_amounts)
        return state

    with state_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)
    state = StrategyState.from_dict(raw)
    _ensure_triggers(state, base_amounts)
    return state


def save_state(state_path: Path, state: StrategyState) -> None:
    _ensure_parent(state_path)
    with state_path.open("w", encoding="utf-8") as file:
        json.dump(state.to_dict(), file, ensure_ascii=False, indent=2)


def _ensure_triggers(state: StrategyState, base_amounts: dict[str, float]) -> None:
    for key, amount in base_amounts.items():
        if key not in state.triggers:
            state.triggers[key] = TriggerState(threshold=int(key), base_amount=float(amount))
        else:
            state.triggers[key].base_amount = float(amount)


def load_forward_pe_history(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return pd.DataFrame(columns=["date", "forward_pe", "source"])

    history = pd.read_csv(csv_path)
    if "source" not in history.columns:
        history["source"] = "import"
    history = history[["date", "forward_pe", "source"]].copy()
    history["date"] = pd.to_datetime(history["date"]).dt.strftime("%Y-%m-%d")
    history["forward_pe"] = pd.to_numeric(history["forward_pe"], errors="coerce")
    history = history.dropna(subset=["date", "forward_pe"]).drop_duplicates(subset=["date"], keep="last")
    history = history.sort_values("date").reset_index(drop=True)
    return history


def save_forward_pe_history(csv_path: Path, history: pd.DataFrame) -> None:
    _ensure_parent(csv_path)
    history = history[["date", "forward_pe", "source"]].copy()
    history = history.sort_values("date").reset_index(drop=True)
    history.to_csv(csv_path, index=False)


def import_forward_pe_history(csv_path: Path, import_file: Path) -> pd.DataFrame:
    existing = load_forward_pe_history(csv_path)
    incoming = pd.read_csv(import_file)
    if "forward_pe" not in incoming.columns and "pe" in incoming.columns:
        incoming = incoming.rename(columns={"pe": "forward_pe"})
    if "date" not in incoming.columns or "forward_pe" not in incoming.columns:
        raise ValueError("导入文件必须包含 date 和 forward_pe 两列，或 date 和 pe 两列")
    if "source" not in incoming.columns:
        incoming["source"] = "import"
    incoming = incoming[["date", "forward_pe", "source"]].copy()
    incoming["date"] = pd.to_datetime(incoming["date"]).dt.strftime("%Y-%m-%d")
    incoming["forward_pe"] = pd.to_numeric(incoming["forward_pe"], errors="coerce")
    merged = pd.concat([existing, incoming], ignore_index=True)
    merged = merged.dropna(subset=["date", "forward_pe"]).drop_duplicates(subset=["date"], keep="last")
    merged = merged.sort_values("date").reset_index(drop=True)
    save_forward_pe_history(csv_path, merged)
    return merged


def append_forward_pe_entry(csv_path: Path, date: str, forward_pe: float, source: str) -> pd.DataFrame:
    history = load_forward_pe_history(csv_path)
    new_row = pd.DataFrame([
        {"date": pd.to_datetime(date).strftime("%Y-%m-%d"), "forward_pe": float(forward_pe), "source": source}
    ])
    merged = pd.concat([history, new_row], ignore_index=True)
    merged = merged.drop_duplicates(subset=["date"], keep="last").sort_values("date").reset_index(drop=True)
    save_forward_pe_history(csv_path, merged)
    return merged


def save_report(output_path: Path, text: str) -> None:
    _ensure_parent(output_path)
    output_path.write_text(text, encoding="utf-8")
