from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TriggerState:
    threshold: int
    base_amount: float
    status: str = "idle"
    activated_on: Optional[str] = None
    status_updated_on: Optional[str] = None
    pending_days_open: int = 0
    cooldown_remaining: int = 0
    current_suggested_amount: Optional[float] = None
    current_adjustment_factor: Optional[float] = None
    executed_amount: Optional[float] = None
    executed_price: Optional[float] = None
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "threshold": self.threshold,
            "base_amount": self.base_amount,
            "status": self.status,
            "activated_on": self.activated_on,
            "status_updated_on": self.status_updated_on,
            "pending_days_open": self.pending_days_open,
            "cooldown_remaining": self.cooldown_remaining,
            "current_suggested_amount": self.current_suggested_amount,
            "current_adjustment_factor": self.current_adjustment_factor,
            "executed_amount": self.executed_amount,
            "executed_price": self.executed_price,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TriggerState":
        return cls(
            threshold=int(data["threshold"]),
            base_amount=float(data["base_amount"]),
            status=data.get("status", "idle"),
            activated_on=data.get("activated_on"),
            status_updated_on=data.get("status_updated_on"),
            pending_days_open=int(data.get("pending_days_open", 0)),
            cooldown_remaining=int(data.get("cooldown_remaining", 0)),
            current_suggested_amount=data.get("current_suggested_amount"),
            current_adjustment_factor=data.get("current_adjustment_factor"),
            executed_amount=data.get("executed_amount"),
            executed_price=data.get("executed_price"),
            note=data.get("note", ""),
        )


@dataclass
class StrategyState:
    version: int = 1
    high_close: Optional[float] = None
    high_close_date: Optional[str] = None
    last_market_date: Optional[str] = None
    last_report_market_date: Optional[str] = None
    triggers: dict[str, TriggerState] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "high_close": self.high_close,
            "high_close_date": self.high_close_date,
            "last_market_date": self.last_market_date,
            "last_report_market_date": self.last_report_market_date,
            "triggers": {key: trigger.to_dict() for key, trigger in self.triggers.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StrategyState":
        trigger_data = data.get("triggers", {})
        return cls(
            version=int(data.get("version", 1)),
            high_close=data.get("high_close"),
            high_close_date=data.get("high_close_date"),
            last_market_date=data.get("last_market_date"),
            last_report_market_date=data.get("last_report_market_date"),
            triggers={key: TriggerState.from_dict(value) for key, value in trigger_data.items()},
        )


@dataclass
class DailyReport:
    market_date: str
    report_date: str
    qqq_close: float
    qqq_high_close: float
    qqq_high_close_date: str | None
    drawdown_pct: float
    vix_close: float
    qqqm_reference_close: float
    max_acceptable_price: float
    is_new_high: bool
    fixed_dca_amount: float
    fixed_dca_weekday: str
    valuation_available: bool
    valuation_mode: str
    forward_pe: float | None
    forward_pe_date: str | None
    forward_pe_source: str | None
    forward_pe_percentile: float | None
    latest_known_forward_pe: float | None
    latest_known_forward_pe_date: str | None
    adjustment_factor: float | None
    pending_triggers: list[dict[str, Any]]
    new_triggers: list[int]
    expired_triggers: list[int]
    total_suggested_amount: float | None
    conclusion: str
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.total_suggested_amount is not None and self.total_suggested_amount > 0:
            return f"纳指策略: QQQ 回撤 {self.drawdown_pct:.2f}%, 建议额外加仓 {self.total_suggested_amount:.2f}"
        if self.fixed_dca_amount > 0:
            return f"纳指策略: {self.fixed_dca_weekday} 固定定投 021000 {self.fixed_dca_amount:.0f}"
        return f"纳指策略: QQQ 回撤 {self.drawdown_pct:.2f}%, 今日观察"

    def render_text(self) -> str:
        lines = [
            "纳指策略日报",
            f"市场日期: {self.market_date}",
            f"生成日期: {self.report_date}",
            f"QQQ 收盘: {self.qqq_close:.2f}",
            f"历史最高收盘: {self.qqq_high_close:.2f} ({self.qqq_high_close_date or '-'})",
            f"当前回撤: -{self.drawdown_pct:.2f}%",
            f"VIX: {self.vix_close:.2f}",
        ]

        if self.is_new_high:
            lines.append("状态: QQQ 收盘创新高，整轮回撤状态已重置")

        if self.valuation_available:
            lines.append(
                f"Forward PE: {self.forward_pe:.2f} | 日期: {self.forward_pe_date} | 来源: {self.forward_pe_source or 'unknown'}"
            )
            if self.forward_pe_date and self.forward_pe_date != self.market_date:
                lines.append("估值口径: 月频，当前沿用最近一期 Forward PE")
            if self.forward_pe_percentile is not None:
                lines.append(f"5年滚动（月频）Forward PE 百分位: {self.forward_pe_percentile * 100:.2f}%")
            if self.adjustment_factor is not None:
                lines.append(f"调整系数 A: {self.adjustment_factor:.2f}")
        else:
            lines.append("Forward PE: 当日数据缺失，暂不输出新的最终额外加仓金额")
            if self.latest_known_forward_pe is not None and self.latest_known_forward_pe_date is not None:
                lines.append(
                    f"最近已知 Forward PE: {self.latest_known_forward_pe:.2f} ({self.latest_known_forward_pe_date})"
                )

        if self.fixed_dca_amount > 0:
            lines.append(f"固定定投: 今天是 {self.fixed_dca_weekday}，021000 定投 {self.fixed_dca_amount:.0f}")
        else:
            lines.append("固定定投: 今日不是固定定投日")

        lines.append(f"QQQM 前收盘: {self.qqqm_reference_close:.2f}")
        lines.append(f"QQQM 最高可接受买入价: {self.max_acceptable_price:.2f} (2% 阈值)")

        if self.new_triggers:
            lines.append("新触发档位: " + ", ".join(f"-{value}%" for value in self.new_triggers))

        if self.expired_triggers:
            lines.append("本日失效档位: " + ", ".join(f"-{value}%" for value in self.expired_triggers))

        if self.pending_triggers:
            lines.append("待执行信号:")
            for item in self.pending_triggers:
                amount_text = (
                    f"{item['suggested_amount']:.2f}" if item["suggested_amount"] is not None else "待补 Forward PE"
                )
                lines.append(
                    f"- 回撤 -{item['threshold']}% | 状态 {item['status']} | 建议 QQQM {amount_text} | 已打开 {item['pending_days_open']} 日"
                )
        else:
            lines.append("待执行信号: 无")

        if self.total_suggested_amount is not None:
            lines.append(f"待执行信号合计金额: {self.total_suggested_amount:.2f}")

        for warning in self.warnings:
            lines.append(f"提示: {warning}")

        lines.append(f"结论: {self.conclusion}")
        return "\n".join(lines)
