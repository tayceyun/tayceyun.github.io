from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import load_config, project_paths
from .market_data import MarketSnapshot, fetch_all_time_high, fetch_market_snapshot
from .notifier import send_wxpusher
from .storage import (
    append_forward_pe_entry,
    import_forward_pe_history,
    load_forward_pe_history,
    load_state,
    save_report,
    save_state,
)
from .strategy import confirm_trigger, evaluate_daily_strategy


def _project_root(path_value: str | None) -> Path:
    return Path(path_value).expanduser().resolve() if path_value else Path.cwd().resolve()


def _report_date(config: dict) -> str:
    return datetime.now(ZoneInfo(config["project_timezone"])).date().isoformat()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nasdaq Strategy Bot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    daily = subparsers.add_parser("daily-report", help="生成策略日报")
    daily.add_argument("--project-root", help="项目根目录")
    daily.add_argument("--dry-run", action="store_true", help="仅打印日报，不发送 WxPusher")
    daily.add_argument("--force", action="store_true", help="允许重复处理同一 market date")
    daily.add_argument("--market-date", help="手工指定 market date，用于离线验证")
    daily.add_argument("--qqq-close", type=float, help="手工指定 QQQ 收盘价")
    daily.add_argument("--qqqm-close", type=float, help="手工指定 QQQM 收盘价")
    daily.add_argument("--vix-close", type=float, help="手工指定 VIX 收盘价")

    import_history = subparsers.add_parser("import-forward-pe", help="导入历史 Forward PE 文件")
    import_history.add_argument("--project-root", help="项目根目录")
    import_history.add_argument("--file", required=True, help="待导入的 CSV 文件路径")

    add_entry = subparsers.add_parser("add-forward-pe", help="补录单日 Forward PE")
    add_entry.add_argument("--project-root", help="项目根目录")
    add_entry.add_argument("--date", required=True, help="日期 YYYY-MM-DD")
    add_entry.add_argument("--value", required=True, type=float, help="Forward PE 值")
    add_entry.add_argument("--source", default="manual", help="数据来源")

    confirm = subparsers.add_parser("confirm-trigger", help="确认某个回撤档位状态")
    confirm.add_argument("--project-root", help="项目根目录")
    confirm.add_argument("--threshold", required=True, type=int, help="档位，例如 20 表示 -20%%")
    confirm.add_argument("--status", required=True, choices=["executed", "skipped", "expired"], help="新状态")
    confirm.add_argument("--action-date", help="状态变更日期 YYYY-MM-DD")
    confirm.add_argument("--executed-amount", type=float, help="已执行金额")
    confirm.add_argument("--executed-price", type=float, help="已执行价格")
    confirm.add_argument("--note", default="", help="备注")
    return parser


def _resolve_snapshot(args: argparse.Namespace, config: dict, state) -> MarketSnapshot:
    manual_values = [args.market_date, args.qqq_close, args.qqqm_close, args.vix_close]
    if any(value is not None for value in manual_values):
        if not all(value is not None for value in manual_values):
            raise ValueError("手工指定市场快照时，market-date、qqq-close、qqqm-close、vix-close 必须同时提供")
        try:
            qqq_all_time_high_close, qqq_all_time_high_date = fetch_all_time_high(config["symbols"]["qqq"])
        except Exception:
            if state.high_close is None or state.high_close_date is None:
                raise
            qqq_all_time_high_close = float(state.high_close)
            qqq_all_time_high_date = state.high_close_date
        return MarketSnapshot(
            market_date=args.market_date,
            qqq_close=float(args.qqq_close),
            qqqm_close=float(args.qqqm_close),
            vix_close=float(args.vix_close),
            qqq_all_time_high_close=qqq_all_time_high_close,
            qqq_all_time_high_date=qqq_all_time_high_date,
        )
    return fetch_market_snapshot(config["symbols"])


def _run_daily_report(args: argparse.Namespace) -> int:
    project_root = _project_root(args.project_root)
    paths = project_paths(project_root)
    config = load_config(paths["config"])
    state = load_state(paths["state"], config["drawdown_base_amounts"])
    history = load_forward_pe_history(paths["history"])
    snapshot = _resolve_snapshot(args, config, state)

    if state.last_report_market_date == snapshot.market_date and not args.force:
        print(f"market date {snapshot.market_date} 已处理，若要重跑请加 --force")
        return 0

    report, state = evaluate_daily_strategy(
        snapshot=snapshot,
        history=history,
        state=state,
        config=config,
        report_date=_report_date(config),
        force=args.force,
    )
    text = report.render_text()

    save_state(paths["state"], state)
    save_report(paths["output"], text)
    print(text)
    send_wxpusher(
        content=text,
        summary=report.summary(),
        api_url=config["notification"]["wxpusher_api"],
        dry_run=args.dry_run,
    )
    return 0


def _run_import_history(args: argparse.Namespace) -> int:
    project_root = _project_root(args.project_root)
    paths = project_paths(project_root)
    merged = import_forward_pe_history(paths["history"], Path(args.file).expanduser().resolve())
    print(f"已导入 Forward PE 历史数据，共 {len(merged)} 条")
    return 0


def _run_add_forward_pe(args: argparse.Namespace) -> int:
    project_root = _project_root(args.project_root)
    paths = project_paths(project_root)
    merged = append_forward_pe_entry(paths["history"], args.date, args.value, args.source)
    print(f"已写入 {args.date} 的 Forward PE，当前共 {len(merged)} 条")
    return 0


def _run_confirm_trigger(args: argparse.Namespace) -> int:
    project_root = _project_root(args.project_root)
    paths = project_paths(project_root)
    config = load_config(paths["config"])
    state = load_state(paths["state"], config["drawdown_base_amounts"])
    action_date = args.action_date or _report_date(config)
    confirm_trigger(
        state=state,
        threshold=args.threshold,
        status=args.status,
        action_date=action_date,
        config=config,
        executed_amount=args.executed_amount,
        executed_price=args.executed_price,
        note=args.note,
    )
    save_state(paths["state"], state)
    print(f"已更新 -{args.threshold}% 档位为 {args.status}")
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "daily-report":
        return _run_daily_report(args)
    if args.command == "import-forward-pe":
        return _run_import_history(args)
    if args.command == "add-forward-pe":
        return _run_add_forward_pe(args)
    if args.command == "confirm-trigger":
        return _run_confirm_trigger(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
