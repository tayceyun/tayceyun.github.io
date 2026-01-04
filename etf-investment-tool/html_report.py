#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 报告生成模块
生成美观的每日投资分析报告
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "output"


def ensure_output_dir():
    """确保输出目录存在"""
    OUTPUT_DIR.mkdir(exist_ok=True)


def generate_html_report(etf_results: List[Dict], stock_results: List[Dict]) -> str:
    """生成 HTML 报告
    
    Args:
        etf_results: ETF 分析结果列表
        stock_results: 个股分析结果列表
    
    Returns:
        生成的 HTML 文件路径
    """
    ensure_output_dir()
    
    today = datetime.now().strftime("%Y-%m-%d")
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日投资分析报告 - {today}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 20px;
            color: #e4e4e4;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            padding: 30px 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            margin-bottom: 24px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 8px;
        }}
        
        .header .date {{
            color: #8b8b9a;
            font-size: 14px;
        }}
        
        .section {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 20px;
            padding-left: 12px;
            border-left: 3px solid #4ade80;
        }}
        
        .section-title.orange {{
            border-left-color: #fb923c;
        }}
        
        .section-title.blue {{
            border-left-color: #60a5fa;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
        }}
        
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        th {{
            color: #8b8b9a;
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
        }}
        
        td {{
            font-size: 14px;
        }}
        
        .price {{
            font-family: "SF Mono", Monaco, monospace;
            font-weight: 500;
        }}
        
        .positive {{
            color: #4ade80;
        }}
        
        .negative {{
            color: #f87171;
        }}
        
        .neutral {{
            color: #fbbf24;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .badge-green {{
            background: rgba(74, 222, 128, 0.2);
            color: #4ade80;
        }}
        
        .badge-yellow {{
            background: rgba(251, 191, 36, 0.2);
            color: #fbbf24;
        }}
        
        .badge-red {{
            background: rgba(248, 113, 113, 0.2);
            color: #f87171;
        }}
        
        .stock-info {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }}
        
        .stock-info-item {{
            background: rgba(255, 255, 255, 0.05);
            padding: 12px 20px;
            border-radius: 8px;
        }}
        
        .stock-info-label {{
            color: #8b8b9a;
            font-size: 12px;
            margin-bottom: 4px;
        }}
        
        .stock-info-value {{
            font-size: 18px;
            font-weight: 600;
        }}
        
        .target-levels {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 12px;
        }}
        
        .target-level {{
            background: rgba(255, 255, 255, 0.05);
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .target-level-label {{
            color: #8b8b9a;
            font-size: 12px;
            margin-bottom: 8px;
        }}
        
        .target-level-price {{
            font-size: 20px;
            font-weight: 600;
            color: #4ade80;
        }}
        
        .target-level-deviation {{
            font-size: 12px;
            color: #f87171;
            margin-top: 4px;
        }}
        
        .tech-indicators {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }}
        
        .tech-item {{
            background: rgba(255, 255, 255, 0.05);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .tech-label {{
            color: #8b8b9a;
            font-size: 11px;
            margin-bottom: 4px;
        }}
        
        .tech-value {{
            font-size: 14px;
            font-weight: 500;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #8b8b9a;
            font-size: 12px;
        }}
        
        @media (max-width: 600px) {{
            .target-levels {{
                grid-template-columns: 1fr;
            }}
            
            .stock-info {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 每日投资分析报告</h1>
            <p class="date">{report_time}</p>
        </div>
        
        {_generate_etf_section(etf_results)}
        
        {_generate_stock_section(stock_results)}
        
        <div class="footer">
            <p>本报告仅供参考，不构成投资建议</p>
        </div>
    </div>
</body>
</html>
'''
    
    # 保存文件
    filename = f"report_{today}.html"
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(filepath)


def _generate_etf_section(etf_results: List[Dict]) -> str:
    """生成 ETF 定投部分"""
    if not etf_results:
        return ""
    
    rows = ""
    for etf in etf_results:
        advice = etf.get("advice", "暂缓买入")
        if "强烈买入" in advice:
            badge_class = "badge-green"
        elif "正常买入" in advice:
            badge_class = "badge-green"
        elif "减半买入" in advice:
            badge_class = "badge-yellow"
        else:
            badge_class = "badge-red"
        
        premium = etf.get("premium_rate", 0)
        premium_class = "negative" if premium > 0 else "positive"
        
        rows += f'''
        <tr>
            <td>{etf.get("name", "")}</td>
            <td class="price">{etf.get("current_price", 0):.3f}</td>
            <td class="price">{etf.get("target_price", 0):.3f}</td>
            <td class="{premium_class}">{premium:+.1f}%</td>
            <td><span class="badge {badge_class}">{advice}</span></td>
            <td>¥{etf.get("amount", 0)}</td>
        </tr>
        '''
    
    return f'''
    <div class="section">
        <h2 class="section-title">美股ETF定投</h2>
        <table>
            <thead>
                <tr>
                    <th>ETF</th>
                    <th>现价</th>
                    <th>目标价</th>
                    <th>溢价率</th>
                    <th>建议</th>
                    <th>定投金额</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    '''


def _generate_stock_section(stock_results: List[Dict]) -> str:
    """生成个股分析部分"""
    if not stock_results:
        return ""
    
    sections = ""
    for stock in stock_results:
        profit_class = "positive" if stock.get("profit_pct", 0) >= 0 else "negative"
        
        # 持仓信息
        position_html = ""
        if stock.get("cost", 0) > 0:
            position_html = f'''
            <div class="stock-info-item">
                <div class="stock-info-label">成本</div>
                <div class="stock-info-value price">{stock.get("cost", 0):.3f}</div>
            </div>
            <div class="stock-info-item">
                <div class="stock-info-label">盈亏</div>
                <div class="stock-info-value {profit_class}">{stock.get("profit_pct", 0):+.1f}%</div>
            </div>
            '''
        
        if stock.get("shares", 0) > 0:
            position_html += f'''
            <div class="stock-info-item">
                <div class="stock-info-label">持仓</div>
                <div class="stock-info-value">{stock.get("shares", 0)}股</div>
            </div>
            '''
        
        # 生成目标价档位
        target_levels = stock.get("target_levels", [])
        levels_html = ""
        for level in target_levels:
            deviation = level.get("deviation", 0)
            deviation_class = "negative" if deviation < 0 else "positive"
            levels_html += f'''
            <div class="target-level">
                <div class="target-level-label">{level.get("label", "")}</div>
                <div class="target-level-price">{level.get("price", 0):.3f}</div>
                <div class="target-level-deviation {deviation_class}">{deviation:+.1f}%</div>
            </div>
            '''
        
        # 技术指标
        tech_html = ""
        if stock.get("ma5"):
            rsi = stock.get("rsi", 50)
            rsi_class = "positive" if rsi < 30 else "negative" if rsi > 70 else ""
            macd = stock.get("macd_signal", "")
            macd_class = "positive" if "金叉" in macd or "多头" in macd else "negative" if macd else ""
            
            tech_html = f'''
            <div class="tech-indicators">
                <div class="tech-item">
                    <div class="tech-label">MA5</div>
                    <div class="tech-value">{stock.get("ma5", 0):.3f}</div>
                </div>
                <div class="tech-item">
                    <div class="tech-label">MA10</div>
                    <div class="tech-value">{stock.get("ma10", 0):.3f}</div>
                </div>
                <div class="tech-item">
                    <div class="tech-label">MA20</div>
                    <div class="tech-value">{stock.get("ma20", 0):.3f}</div>
                </div>
                <div class="tech-item">
                    <div class="tech-label">MA60</div>
                    <div class="tech-value">{stock.get("ma60", 0):.3f}</div>
                </div>
                <div class="tech-item">
                    <div class="tech-label">RSI</div>
                    <div class="tech-value {rsi_class}">{rsi:.1f}</div>
                </div>
                <div class="tech-item">
                    <div class="tech-label">MACD</div>
                    <div class="tech-value {macd_class}">{macd}</div>
                </div>
            </div>
            '''
        
        sections += f'''
        <div class="section">
            <h2 class="section-title orange">{stock.get("name", "")} - 目标买入价</h2>
            
            <div class="stock-info">
                <div class="stock-info-item">
                    <div class="stock-info-label">现价</div>
                    <div class="stock-info-value price">{stock.get("current_price", 0):.3f}</div>
                </div>
                {position_html}
            </div>
            
            <div class="target-levels">
                {levels_html}
            </div>
            
            {tech_html}
        </div>
        '''
    
    return sections


def generate_backtest_html_report(code: str, strategy: str, metrics: Dict, 
                                   trades: List[Dict], portfolio_values: List[Dict],
                                   trade_stats: Dict = None, strategy_params: Dict = None,
                                   start_date: str = "", end_date: str = "") -> str:
    """生成回测 HTML 报告
    
    Args:
        code: 股票代码
        strategy: 策略名称
        metrics: 回测指标
        trades: 交易记录列表
        portfolio_values: 组合价值时序数据
        trade_stats: 交易统计（目标价策略用）
        strategy_params: 策略参数
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        生成的 HTML 文件路径
    """
    ensure_output_dir()
    
    today = datetime.now().strftime("%Y-%m-%d")
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 收益指标
    total_return = metrics.get("total_return", 0)
    hold_return = metrics.get("hold_return", 0)
    excess_return = metrics.get("excess_return", 0)
    annual_return = metrics.get("annual_return", 0)
    max_drawdown = metrics.get("max_drawdown", 0)
    sharpe = metrics.get("sharpe", 0)
    volatility = metrics.get("volatility", 0)
    trading_days = metrics.get("trading_days", 0)
    
    # 策略评价
    if excess_return > 5:
        evaluation = "策略非常有效 ✅"
        eval_class = "positive"
    elif excess_return > 0:
        evaluation = "策略有效 ✅"
        eval_class = "positive"
    elif excess_return > -5:
        evaluation = "策略一般 ⚠️"
        eval_class = "neutral"
    else:
        evaluation = "策略无效 ❌"
        eval_class = "negative"
    
    # 策略参数 HTML
    params_html = ""
    if strategy_params:
        params_rows = ""
        for key, value in strategy_params.items():
            label = {
                "formula": "基础目标价",
                "dynamic_formula": "动态调整",
                "score_factor": "评分系数",
                "profit_target": "止盈比例",
                "stop_loss": "止损比例",
            }.get(key, key)
            
            if key == "profit_target" or key == "stop_loss":
                display_value = f"{value * 100:.0f}%"
            elif key == "score_factor":
                display_value = f"{value}%/分"
            else:
                display_value = str(value)
            
            params_rows += f'<tr><td>{label}</td><td>{display_value}</td></tr>'
        
        params_html = f'''
        <div class="card">
            <h3>📋 策略参数</h3>
            <table class="params-table">
                <tbody>{params_rows}</tbody>
            </table>
        </div>
        '''
    
    # 交易统计 HTML
    buy_count = len([t for t in trades if t.get("操作") == "买入"])
    sell_count = len([t for t in trades if t.get("操作") == "卖出"])
    
    trade_stats_html = ""
    if trade_stats:
        profit_trades = trade_stats.get("profit_trades", 0)
        loss_trades = trade_stats.get("loss_trades", 0)
        technical_sells = trade_stats.get("technical_sells", 0)
        holding_trades = trade_stats.get("holding_trades", 0)
        win_rate = trade_stats.get("win_rate", 0)
        
        trade_stats_html = f'''
        <div class="stat-row">
            <div class="stat-item">
                <div class="stat-label">止盈次数</div>
                <div class="stat-value positive">{profit_trades}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">止损次数</div>
                <div class="stat-value negative">{loss_trades}</div>
            </div>
            {"<div class='stat-item'><div class='stat-label'>技术面卖出</div><div class='stat-value neutral'>" + str(technical_sells) + "</div></div>" if technical_sells > 0 else ""}
            <div class="stat-item">
                <div class="stat-label">持仓中</div>
                <div class="stat-value">{holding_trades}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">胜率</div>
                <div class="stat-value {'positive' if win_rate >= 50 else 'negative'}">{win_rate:.1f}%</div>
            </div>
        </div>
        '''
    
    # 交易记录表格
    trades_html = ""
    if trades:
        trades_rows = ""
        for trade in trades[-50:]:  # 最近50条
            action_class = "positive" if trade.get("操作") == "买入" else "negative"
            trades_rows += f'''
            <tr>
                <td>{trade.get("日期", "")}</td>
                <td class="{action_class}">{trade.get("操作", "")}</td>
                <td class="price">{trade.get("价格", 0):.2f}</td>
                <td>{trade.get("数量", 0)}</td>
                <td>¥{trade.get("金额", 0):,.0f}</td>
                <td>{trade.get("评分", trade.get("目标价", "-"))}</td>
                <td class="reason">{trade.get("原因", "")}</td>
            </tr>
            '''
        
        trades_html = f'''
        <div class="card">
            <h3>📝 交易记录 (最近50条)</h3>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>日期</th>
                            <th>操作</th>
                            <th>价格</th>
                            <th>数量</th>
                            <th>金额</th>
                            <th>评分/目标价</th>
                            <th>原因</th>
                        </tr>
                    </thead>
                    <tbody>
                        {trades_rows}
                    </tbody>
                </table>
            </div>
        </div>
        '''
    
    # 组合价值图表数据
    chart_labels = []
    chart_values = []
    chart_prices = []
    for i, pv in enumerate(portfolio_values):
        if i % 5 == 0 or i == len(portfolio_values) - 1:  # 每5天取一个点
            date_obj = pv.get("日期")
            if hasattr(date_obj, 'strftime'):
                chart_labels.append(date_obj.strftime("%m-%d"))
            else:
                chart_labels.append(str(date_obj)[-5:])
            chart_values.append(round(pv.get("组合价值", 0), 2))
            chart_prices.append(round(pv.get("股价", 0), 2))
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>回测报告 - {code} {strategy}策略</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 20px;
            color: #e4e4e4;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            padding: 30px 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            margin-bottom: 24px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 8px;
        }}
        
        .header .subtitle {{
            color: #8b8b9a;
            font-size: 14px;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .card h3 {{
            font-size: 16px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 20px;
            padding-left: 12px;
            border-left: 3px solid #4ade80;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}
        
        .metric-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .metric-label {{
            color: #8b8b9a;
            font-size: 12px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}
        
        .metric-value {{
            font-size: 24px;
            font-weight: 600;
        }}
        
        .metric-value.positive {{ color: #4ade80; }}
        .metric-value.negative {{ color: #f87171; }}
        .metric-value.neutral {{ color: #fbbf24; }}
        
        .stat-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 16px;
        }}
        
        .stat-item {{
            background: rgba(255, 255, 255, 0.05);
            padding: 12px 20px;
            border-radius: 8px;
            text-align: center;
            flex: 1;
            min-width: 100px;
        }}
        
        .stat-label {{
            color: #8b8b9a;
            font-size: 11px;
            margin-bottom: 4px;
        }}
        
        .stat-value {{
            font-size: 18px;
            font-weight: 600;
        }}
        
        .stat-value.positive {{ color: #4ade80; }}
        .stat-value.negative {{ color: #f87171; }}
        .stat-value.neutral {{ color: #fbbf24; }}
        
        .evaluation-box {{
            text-align: center;
            padding: 24px;
            background: rgba(74, 222, 128, 0.1);
            border: 1px solid rgba(74, 222, 128, 0.3);
            border-radius: 12px;
            margin-top: 20px;
        }}
        
        .evaluation-box.negative {{
            background: rgba(248, 113, 113, 0.1);
            border-color: rgba(248, 113, 113, 0.3);
        }}
        
        .evaluation-box.neutral {{
            background: rgba(251, 191, 36, 0.1);
            border-color: rgba(251, 191, 36, 0.3);
        }}
        
        .evaluation-text {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .evaluation-detail {{
            color: #8b8b9a;
            font-size: 14px;
        }}
        
        .params-table {{
            width: 100%;
        }}
        
        .params-table td {{
            padding: 10px 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .params-table td:first-child {{
            color: #8b8b9a;
            width: 120px;
        }}
        
        .chart-container {{
            height: 300px;
            margin-top: 16px;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        th {{
            color: #8b8b9a;
            font-weight: 500;
            font-size: 11px;
            text-transform: uppercase;
        }}
        
        .price {{
            font-family: "SF Mono", Monaco, monospace;
        }}
        
        .reason {{
            max-width: 200px;
            font-size: 12px;
            color: #8b8b9a;
        }}
        
        .positive {{ color: #4ade80; }}
        .negative {{ color: #f87171; }}
        .neutral {{ color: #fbbf24; }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #8b8b9a;
            font-size: 12px;
        }}
        
        @media (max-width: 600px) {{
            .metrics-grid {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 {strategy}策略回测报告</h1>
            <p class="subtitle">{code} | {start_date} ~ {end_date} | 共{trading_days}个交易日</p>
        </div>
        
        {params_html}
        
        <div class="card">
            <h3>📊 收益指标</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">策略收益</div>
                    <div class="metric-value {'positive' if total_return >= 0 else 'negative'}">{total_return:+.2f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">持有收益</div>
                    <div class="metric-value {'positive' if hold_return >= 0 else 'negative'}">{hold_return:+.2f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">超额收益</div>
                    <div class="metric-value {'positive' if excess_return >= 0 else 'negative'}">{excess_return:+.2f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">年化收益</div>
                    <div class="metric-value {'positive' if annual_return >= 0 else 'negative'}">{annual_return:+.2f}%</div>
                </div>
            </div>
            
            <div class="evaluation-box {eval_class}">
                <div class="evaluation-text">{evaluation}</div>
                <div class="evaluation-detail">超额收益: {excess_return:+.2f}%</div>
            </div>
        </div>
        
        <div class="card">
            <h3>⚠️ 风险指标</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">最大回撤</div>
                    <div class="metric-value negative">-{max_drawdown:.2f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">夏普比率</div>
                    <div class="metric-value {'positive' if sharpe >= 1 else 'neutral' if sharpe >= 0 else 'negative'}">{sharpe:.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">波动率</div>
                    <div class="metric-value">{volatility:.2f}%</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📈 交易统计</h3>
            <div class="stat-row">
                <div class="stat-item">
                    <div class="stat-label">总交易次数</div>
                    <div class="stat-value">{len(trades)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">买入次数</div>
                    <div class="stat-value positive">{buy_count}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">卖出次数</div>
                    <div class="stat-value negative">{sell_count}</div>
                </div>
            </div>
            {trade_stats_html}
        </div>
        
        <div class="card">
            <h3>📉 组合价值走势</h3>
            <div class="chart-container">
                <canvas id="portfolioChart"></canvas>
            </div>
        </div>
        
        {trades_html}
        
        <div class="footer">
            <p>生成时间: {report_time} | 本报告仅供参考，不构成投资建议</p>
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('portfolioChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {chart_labels},
                datasets: [{{
                    label: '组合价值',
                    data: {chart_values},
                    borderColor: '#4ade80',
                    backgroundColor: 'rgba(74, 222, 128, 0.1)',
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y'
                }}, {{
                    label: '股价',
                    data: {chart_prices},
                    borderColor: '#60a5fa',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    tension: 0.4,
                    yAxisID: 'y1'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false
                }},
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#8b8b9a'
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        ticks: {{ color: '#8b8b9a' }},
                        grid: {{ color: 'rgba(255,255,255,0.05)' }}
                    }},
                    y: {{
                        type: 'linear',
                        position: 'left',
                        ticks: {{ color: '#4ade80' }},
                        grid: {{ color: 'rgba(255,255,255,0.05)' }}
                    }},
                    y1: {{
                        type: 'linear',
                        position: 'right',
                        ticks: {{ color: '#60a5fa' }},
                        grid: {{ drawOnChartArea: false }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
'''
    
    # 保存文件
    filename = f"backtest_{code}_{strategy}_{today}.html"
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(filepath)


# 测试
if __name__ == "__main__":
    # 模拟数据测试
    stock_results = [
        {
            "name": "紫金矿业",
            "code": "601899",
            "current_price": 18.52,
            "cost": 28.32,
            "profit_pct": -34.6,
            "shares": 600,
            "ma5": 18.45,
            "ma10": 18.32,
            "ma20": 18.15,
            "ma60": 17.88,
            "rsi": 45.2,
            "macd_signal": "金叉",
            "target_levels": [
                {"label": "保守", "price": 17.80, "deviation": -3.9},
                {"label": "正常", "price": 17.20, "deviation": -7.1},
                {"label": "激进", "price": 16.50, "deviation": -10.9}
            ]
        }
    ]
    
    filepath = generate_html_report([], stock_results)
    print(f"报告已生成: {filepath}")
