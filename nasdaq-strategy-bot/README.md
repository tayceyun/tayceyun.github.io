# Nasdaq Strategy Bot

一个独立的 Python 策略机器人，用于每天基于 `QQQ` 回撤、`VIX` 和 `Forward PE` 给出纳指相关操作建议，并通过 `WxPusher` 推送到微信。

当前版本的设计原则：

1. 固定定投与额外加仓分层。
2. 固定定投只提醒，不自动下单。
3. 额外加仓统一输出 `QQQM` 建议金额。
4. `Forward PE` 使用本地历史文件，支持后续导入你整理的 5 年历史数据。
5. 支持手动补录 `Forward PE` 和手动确认信号状态。
6. 当前默认按月频 `Forward PE` 运行，日报沿用最近一期月度值。

## 目录结构

```text
nasdaq-strategy-bot/
├── config/defaults.json
├── data/forward_pe_history.csv
├── state/strategy_state.json
├── requirements.txt
└── src/nasdaq_strategy_bot/
    ├── cli.py
    ├── config.py
    ├── market_data.py
    ├── models.py
    ├── notifier.py
    ├── storage.py
    └── strategy.py
```

## 数据文件

`data/forward_pe_history.csv` 默认格式：

```csv
date,forward_pe,source
2024-01-02,24.80,manual
```

如果你后续提供的是两列表：

```csv
date,forward_pe
```

也可以直接通过导入命令合并进去。

如果你提供的是月频两列表：

```csv
date,pe
```

当前版本也可以直接导入，系统会自动把 `pe` 识别为 `forward_pe`。

## 本地运行

```bash
cd /Users/yzh817/Documents/tayceyun.github.io/nasdaq-strategy-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 1. 导入历史 Forward PE

```bash
PYTHONPATH=src python -m nasdaq_strategy_bot.cli import-forward-pe \
  --project-root . \
  --file /path/to/forward_pe_history.csv
```

### 2. 补录单日 Forward PE

```bash
PYTHONPATH=src python -m nasdaq_strategy_bot.cli add-forward-pe \
  --project-root . \
  --date 2026-06-10 \
  --value 24.8 \
  --source manual
```

### 3. 生成日报

```bash
PYTHONPATH=src python -m nasdaq_strategy_bot.cli daily-report --project-root . --dry-run
```

### 4. 本地离线验证

```bash
PYTHONPATH=src python -m nasdaq_strategy_bot.cli daily-report \
  --project-root . \
  --dry-run \
  --force \
  --market-date 2026-06-10 \
  --qqq-close 518.32 \
  --qqqm-close 223.45 \
  --vix-close 19.80
```

### 5. 确认信号状态

```bash
PYTHONPATH=src python -m nasdaq_strategy_bot.cli confirm-trigger \
  --project-root . \
  --threshold 20 \
  --status executed \
  --action-date 2026-06-11 \
  --executed-amount 10000 \
  --executed-price 221.7
```

## GitHub Actions

仓库根目录的 `.github/workflows/` 已预留三条工作流：

1. `nasdaq_daily_report.yml`: 定时跑日报。
2. `nasdaq_manual_forward_pe.yml`: 手动补录 `Forward PE` 并重跑日报。
3. `nasdaq_confirm_signal.yml`: 手动确认信号状态。

## Secrets

需要在 GitHub 仓库中配置：

1. `WXPUSHER_APP_TOKEN`
2. `WXPUSHER_UID`

## 当前估值模式

默认使用 `5 年滚动（月频）Forward PE 百分位` 作为主估值因子，同时在日报里保留原始 `Forward PE` 值。

当前按月频运行：如果当天不是月度更新时间，日报会沿用最近一期已知月频 `Forward PE`。
