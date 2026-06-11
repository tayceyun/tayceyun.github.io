from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from .market_data import MarketSnapshot
from .models import DailyReport, StrategyState, TriggerState


def _reset_trigger(trigger: TriggerState) -> None:
    trigger.status = "idle"
    trigger.activated_on = None
    trigger.status_updated_on = None
    trigger.pending_days_open = 0
    trigger.cooldown_remaining = 0
    trigger.current_suggested_amount = None
    trigger.current_adjustment_factor = None
    trigger.executed_amount = None
    trigger.executed_price = None
    trigger.note = ""


def _reset_all_triggers(state: StrategyState) -> None:
    for trigger in state.triggers.values():
        _reset_trigger(trigger)


def _advance_existing_triggers(state: StrategyState, config: dict, market_date: str) -> list[int]:
    expired_triggers: list[int] = []
    pending_limit = int(config["execution"]["pending_market_days"])
    retrigger_days = int(config["execution"]["retrigger_cooldown_market_days"])

    for trigger in state.triggers.values():
        if trigger.status == "pending":
            trigger.pending_days_open += 1
            if trigger.pending_days_open > pending_limit:
                trigger.status = "expired"
                trigger.status_updated_on = market_date
                trigger.pending_days_open = 0
                trigger.cooldown_remaining = retrigger_days
                expired_triggers.append(trigger.threshold)
        elif trigger.status in {"expired", "skipped"} and trigger.cooldown_remaining > 0:
            trigger.cooldown_remaining -= 1

    return expired_triggers


def _build_valuation_context(history: pd.DataFrame, market_date: str, config: dict) -> dict:
    context = {
        "available": False,
        "mode": config["valuation"]["mode"],
        "forward_pe": None,
        "forward_pe_date": None,
        "source": None,
        "percentile": None,
        "latest_known_forward_pe": None,
        "latest_known_forward_pe_date": None,
    }

    if history.empty:
        return context

    history = history.copy()
    history["date"] = pd.to_datetime(history["date"])
    target_date = pd.to_datetime(market_date)
    historical = history.loc[history["date"] <= target_date].sort_values("date")
    if historical.empty:
        return context

    latest_row = historical.iloc[-1]
    context["latest_known_forward_pe"] = float(latest_row["forward_pe"])
    context["latest_known_forward_pe_date"] = latest_row["date"].strftime("%Y-%m-%d")

    exact_row = history.loc[history["date"] == target_date]
    if exact_row.empty and config["valuation"].get("exact_date_required", True):
        return context

    row = exact_row.iloc[-1] if not exact_row.empty else latest_row
    context["available"] = True
    context["forward_pe"] = float(row["forward_pe"])
    context["forward_pe_date"] = row["date"].strftime("%Y-%m-%d")
    context["source"] = row.get("source", "unknown")

    rolling_years = int(config["valuation"].get("rolling_window_years", 5))
    window_start = target_date - pd.DateOffset(years=rolling_years)
    window = historical.loc[historical["date"] >= window_start]
    if not window.empty:
        percentile = float((window["forward_pe"] <= context["forward_pe"]).sum() / len(window))
        context["percentile"] = percentile

    return context


def _resolve_pe_adjustment(valuation_context: dict, config: dict) -> float | None:
    if not valuation_context["available"]:
        return None

    if config["valuation"]["mode"] == "percentile":
        percentile = valuation_context["percentile"]
        if percentile is None:
            return None
        for rule in config["valuation"]["percentile_adjustments"]:
            if percentile <= float(rule["lte"]):
                return float(rule["adjustment"])
    else:
        forward_pe = float(valuation_context["forward_pe"])
        for rule in config["valuation"]["raw_forward_pe_adjustments"]:
            if forward_pe <= float(rule["lte"]):
                return float(rule["adjustment"])
    return None


def _resolve_vix_adjustment(vix_close: float, config: dict) -> float:
    for rule in config["vix_adjustments"]:
        if vix_close < float(rule["lt"]):
            return float(rule["adjustment"])
    return 0.0


def _clamp_adjustment_factor(pe_adjustment: float | None, vix_adjustment: float, config: dict) -> float | None:
    if pe_adjustment is None:
        return None
    factor = 1 + pe_adjustment + vix_adjustment
    return max(0.85, min(1.5, factor))


def _activate_trigger(
    trigger: TriggerState,
    market_date: str,
    adjustment_factor: float | None,
) -> None:
    trigger.status = "pending"
    trigger.activated_on = market_date
    trigger.status_updated_on = market_date
    trigger.pending_days_open = 1
    trigger.cooldown_remaining = 0
    trigger.executed_amount = None
    trigger.executed_price = None
    if adjustment_factor is not None:
        trigger.current_adjustment_factor = adjustment_factor
        trigger.current_suggested_amount = round(trigger.base_amount * adjustment_factor, 2)
    else:
        trigger.current_adjustment_factor = None
        trigger.current_suggested_amount = None


def _today_dca_amount(config: dict, report_date: str) -> tuple[float, str]:
    local_day = datetime.fromisoformat(report_date).strftime("%A").upper()
    amount = float(config["fixed_dca"].get(local_day, 0))
    return amount, local_day


def evaluate_daily_strategy(
    snapshot: MarketSnapshot,
    history: pd.DataFrame,
    state: StrategyState,
    config: dict,
    report_date: str | None = None,
    force: bool = False,
) -> tuple[DailyReport, StrategyState]:
    report_date = report_date or datetime.now(ZoneInfo(config["project_timezone"])).date().isoformat()
    is_new_market_date = state.last_market_date != snapshot.market_date
    expired_triggers: list[int] = []

    previous_high_close = state.high_close
    previous_high_date = state.high_close_date
    state.high_close = snapshot.qqq_all_time_high_close
    state.high_close_date = snapshot.qqq_all_time_high_date

    is_new_high = (
        snapshot.market_date == snapshot.qqq_all_time_high_date
        and (
            previous_high_close is None
            or float(previous_high_close) != snapshot.qqq_all_time_high_close
            or previous_high_date != snapshot.qqq_all_time_high_date
        )
    )
    if is_new_high:
        _reset_all_triggers(state)

    drawdown_pct = 0.0
    if state.high_close:
        drawdown_pct = max(0.0, (float(state.high_close) - snapshot.qqq_close) / float(state.high_close) * 100)

    if is_new_market_date and not is_new_high:
        expired_triggers = _advance_existing_triggers(state, config, snapshot.market_date)

    valuation_context = _build_valuation_context(history, snapshot.market_date, config)
    pe_adjustment = _resolve_pe_adjustment(valuation_context, config)
    vix_adjustment = _resolve_vix_adjustment(snapshot.vix_close, config)
    adjustment_factor = _clamp_adjustment_factor(pe_adjustment, vix_adjustment, config)

    new_triggers: list[int] = []
    for key in sorted(config["drawdown_base_amounts"], key=lambda value: int(value)):
        trigger = state.triggers[key]
        threshold = int(key)
        if drawdown_pct < threshold:
            continue

        if trigger.status == "idle":
            _activate_trigger(trigger, snapshot.market_date, adjustment_factor)
            new_triggers.append(threshold)
            continue

        if trigger.status in {"expired", "skipped"} and trigger.cooldown_remaining <= 0:
            _activate_trigger(trigger, snapshot.market_date, adjustment_factor)
            new_triggers.append(threshold)
            continue

        if trigger.status == "pending" and trigger.current_suggested_amount is None and adjustment_factor is not None:
            trigger.current_adjustment_factor = adjustment_factor
            trigger.current_suggested_amount = round(trigger.base_amount * adjustment_factor, 2)

    if is_new_market_date or force:
        state.last_market_date = snapshot.market_date
    state.last_report_market_date = snapshot.market_date

    fixed_dca_amount, fixed_dca_weekday = _today_dca_amount(config, report_date)
    max_acceptable_price = round(snapshot.qqqm_close * (1 + float(config["execution"]["max_price_deviation_pct"])), 2)

    pending_triggers = []
    suggested_amounts = []
    for key in sorted(state.triggers, key=lambda value: int(value)):
        trigger = state.triggers[key]
        if trigger.status != "pending":
            continue
        pending_triggers.append(
            {
                "threshold": trigger.threshold,
                "status": trigger.status,
                "pending_days_open": trigger.pending_days_open,
                "suggested_amount": trigger.current_suggested_amount,
            }
        )
        if trigger.current_suggested_amount is not None:
            suggested_amounts.append(trigger.current_suggested_amount)

    total_suggested_amount = round(sum(suggested_amounts), 2) if pending_triggers and len(suggested_amounts) == len(pending_triggers) else None

    warnings: list[str] = []
    if not valuation_context["available"]:
        warnings.append("请补录当日 Forward PE 后再生成正式额外加仓金额")
    if pending_triggers and total_suggested_amount is None:
        warnings.append("存在待执行信号，但部分金额尚未完成估值计算")

    if is_new_high:
        conclusion = "QQQ 收盘创新高，整轮回撤状态已重置。"
    elif pending_triggers and total_suggested_amount is not None:
        conclusion = f"当前存在待执行信号，建议额外加仓 QQQM {total_suggested_amount:.2f}。"
    elif pending_triggers:
        conclusion = "当前存在待执行信号，但需补齐当日 Forward PE 后再给出正式金额。"
    elif fixed_dca_amount > 0:
        conclusion = f"今日以固定定投为主，021000 定投 {fixed_dca_amount:.0f}。"
    else:
        conclusion = "今日无新增额外加仓信号，继续观察。"

    report = DailyReport(
        market_date=snapshot.market_date,
        report_date=report_date,
        qqq_close=snapshot.qqq_close,
        qqq_high_close=float(state.high_close),
        qqq_high_close_date=state.high_close_date,
        drawdown_pct=round(drawdown_pct, 2),
        vix_close=snapshot.vix_close,
        qqqm_reference_close=snapshot.qqqm_close,
        max_acceptable_price=max_acceptable_price,
        is_new_high=is_new_high,
        fixed_dca_amount=fixed_dca_amount,
        fixed_dca_weekday=fixed_dca_weekday,
        valuation_available=valuation_context["available"],
        valuation_mode=config["valuation"]["mode"],
        forward_pe=valuation_context["forward_pe"],
        forward_pe_date=valuation_context["forward_pe_date"],
        forward_pe_source=valuation_context["source"],
        forward_pe_percentile=valuation_context["percentile"],
        latest_known_forward_pe=valuation_context["latest_known_forward_pe"],
        latest_known_forward_pe_date=valuation_context["latest_known_forward_pe_date"],
        adjustment_factor=adjustment_factor,
        pending_triggers=pending_triggers,
        new_triggers=new_triggers,
        expired_triggers=expired_triggers,
        total_suggested_amount=total_suggested_amount,
        conclusion=conclusion,
        warnings=warnings,
    )
    return report, state


def confirm_trigger(
    state: StrategyState,
    threshold: int,
    status: str,
    action_date: str,
    config: dict,
    executed_amount: float | None = None,
    executed_price: float | None = None,
    note: str = "",
) -> StrategyState:
    trigger = state.triggers[str(threshold)]
    trigger.status = status
    trigger.status_updated_on = action_date
    trigger.note = note
    trigger.pending_days_open = 0

    if status == "executed":
        trigger.executed_amount = executed_amount
        trigger.executed_price = executed_price
        trigger.cooldown_remaining = 0
    elif status in {"expired", "skipped"}:
        trigger.cooldown_remaining = int(config["execution"]["retrigger_cooldown_market_days"])
    return state
