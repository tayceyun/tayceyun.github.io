#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史行情数据下载脚本
下载40只行业龙头股的日K和5分钟数据到本地
"""

import os
import json
import argparse
import pandas as pd
import baostock as bs
from datetime import datetime, timedelta
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import box

console = Console()

# 数据存储目录
DATA_DIR = os.path.join(os.path.dirname(__file__), "market_data")
DAILY_DIR = os.path.join(DATA_DIR, "daily")
MIN5_DIR = os.path.join(DATA_DIR, "5min")
LOG_FILE = os.path.join(DATA_DIR, "download_log.json")

# 40只行业龙头股列表
STOCK_LIST = {
    # 消费行业（4只）
    "600519": "贵州茅台",
    "000858": "五粮液",
    "600887": "伊利股份",
    "603288": "海天味业",
    
    # 科技/半导体行业（5只）
    "688981": "中芯国际",
    "002371": "北方华创",
    "603501": "韦尔股份",
    "002230": "科大讯飞",
    "002475": "立讯精密",
    
    # 新能源行业（5只）
    "300750": "宁德时代",
    "002594": "比亚迪",
    "601012": "隆基绿能",
    "300274": "阳光电源",
    "600900": "长江电力",
    
    # 医药生物行业（5只）
    "300760": "迈瑞医疗",
    "600276": "恒瑞医药",
    "603259": "药明康德",
    "600436": "片仔癀",
    "300015": "爱尔眼科",
    
    # 金融行业（5只）
    "601398": "工商银行",
    "600036": "招商银行",
    "601318": "中国平安",
    "600030": "中信证券",
    "601628": "中国人寿",
    
    # 高端制造/军工（5只）
    "600031": "三一重工",
    "600760": "中航沈飞",
    "600893": "航发动力",
    "601138": "工业富联",
    "601766": "中国中车",
    
    # 人工智能/算力（3只）
    "002415": "海康威视",
    "603019": "中科曙光",
    "000938": "紫光股份",
    
    # 汽车行业（4只）- 比亚迪已在新能源
    "601238": "长城汽车",
    "600660": "福耀玻璃",
    "600741": "华域汽车",
    
    # 家电行业（3只）
    "000333": "美的集团",
    "000651": "格力电器",
    "600690": "海尔智家",
    
    # 资源/周期行业（5只）
    "601088": "中国神华",
    "601899": "紫金矿业",
    "601857": "中国石油",
    "600019": "宝钢股份",
    "600309": "万华化学",
    
    # 通信行业（3只）
    "600941": "中国移动",
    "000063": "中兴通讯",
    "300628": "亿联网络",
}


def _convert_code_to_bs(code: str) -> str:
    """将普通代码转换为 Baostock 格式"""
    if code.startswith(('0', '3')):
        return f"sz.{code}"
    elif code.startswith('6'):
        return f"sh.{code}"
    else:
        return f"sh.{code}"


def load_download_log() -> dict:
    """加载下载记录"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"daily": {}, "5min": {}}


def save_download_log(log: dict):
    """保存下载记录"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def download_daily_data(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """下载日K数据"""
    bs_code = _convert_code_to_bs(code)
    
    rs = bs.query_history_k_data_plus(
        bs_code,
        "date,open,high,low,close,volume,amount,turn,pctChg",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="2"  # 前复权
    )
    
    if rs.error_code != '0':
        console.print(f"[red]下载 {code} 日K数据失败: {rs.error_msg}[/red]")
        return pd.DataFrame()
    
    data_list = []
    while rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        return pd.DataFrame()
    
    df = pd.DataFrame(data_list, columns=[
        '日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额', '换手率', '涨跌幅'
    ])
    
    # 转换数据类型
    df['日期'] = pd.to_datetime(df['日期'])
    for col in ['开盘', '最高', '最低', '收盘', '成交额', '换手率', '涨跌幅']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce').astype('Int64')
    
    return df.sort_values('日期').reset_index(drop=True)


def download_5min_data(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """下载5分钟K线数据"""
    bs_code = _convert_code_to_bs(code)
    
    rs = bs.query_history_k_data_plus(
        bs_code,
        "date,time,open,high,low,close,volume,amount",
        start_date=start_date,
        end_date=end_date,
        frequency="5",
        adjustflag="2"  # 前复权
    )
    
    if rs.error_code != '0':
        console.print(f"[red]下载 {code} 5分钟数据失败: {rs.error_msg}[/red]")
        return pd.DataFrame()
    
    data_list = []
    while rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        return pd.DataFrame()
    
    df = pd.DataFrame(data_list, columns=[
        '日期', '时间', '开盘', '最高', '最低', '收盘', '成交量', '成交额'
    ])
    
    # 转换数据类型
    df['日期'] = pd.to_datetime(df['日期'])
    for col in ['开盘', '最高', '最低', '收盘', '成交额']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce').astype('Int64')
    
    # 创建完整的datetime列
    def parse_time(row):
        time_str = str(row['时间'])
        date_str = row['日期'].strftime('%Y-%m-%d')
        if len(time_str) >= 12:
            hour = time_str[8:10] if len(time_str) >= 17 else time_str[:2]
            minute = time_str[10:12] if len(time_str) >= 17 else time_str[2:4]
        else:
            hour = time_str[:2].zfill(2)
            minute = time_str[2:4].zfill(2)
        return f"{date_str} {hour}:{minute}:00"
    
    df['datetime'] = pd.to_datetime(df.apply(parse_time, axis=1))
    
    return df.sort_values('datetime').reset_index(drop=True)


def run_download(download_daily: bool = True, download_5min: bool = True,
                 codes: list = None, force: bool = False):
    """执行下载任务"""
    
    # 确保目录存在
    os.makedirs(DAILY_DIR, exist_ok=True)
    os.makedirs(MIN5_DIR, exist_ok=True)
    
    # 加载下载记录
    log = load_download_log()
    
    # 确定要下载的股票
    if codes:
        stocks = {c: STOCK_LIST.get(c, c) for c in codes if c in STOCK_LIST}
    else:
        stocks = STOCK_LIST
    
    if not stocks:
        console.print("[yellow]没有找到要下载的股票[/yellow]")
        return
    
    # 登录 Baostock
    console.print("[cyan]正在连接 Baostock...[/cyan]")
    lg = bs.login()
    if lg.error_code != '0':
        console.print(f"[red]Baostock 登录失败: {lg.error_msg}[/red]")
        return
    console.print("[green]Baostock 连接成功[/green]\n")
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 下载日K数据
    if download_daily:
        console.print("[bold cyan]📊 下载日K数据 (2020-2025)[/bold cyan]")
        daily_start = "2020-01-01"
        daily_end = today
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("下载日K数据", total=len(stocks))
            
            for code, name in stocks.items():
                progress.update(task, description=f"下载 {name}({code})")
                
                file_path = os.path.join(DAILY_DIR, f"{code}.csv")
                
                # 检查是否需要更新
                if not force and code in log.get("daily", {}):
                    last_date = log["daily"][code].get("end_date", "")
                    if last_date >= today:
                        progress.advance(task)
                        continue
                    # 增量更新
                    daily_start_code = (datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                else:
                    daily_start_code = daily_start
                
                df = download_daily_data(code, daily_start_code, daily_end)
                
                if not df.empty:
                    # 如果是增量更新，合并数据
                    if os.path.exists(file_path) and not force:
                        existing_df = pd.read_csv(file_path, parse_dates=['日期'])
                        df = pd.concat([existing_df, df]).drop_duplicates(subset=['日期']).sort_values('日期')
                    
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                    
                    # 更新日志
                    if "daily" not in log:
                        log["daily"] = {}
                    log["daily"][code] = {
                        "name": name,
                        "start_date": df['日期'].min().strftime('%Y-%m-%d'),
                        "end_date": df['日期'].max().strftime('%Y-%m-%d'),
                        "rows": len(df),
                        "updated_at": today
                    }
                
                progress.advance(task)
        
        console.print(f"[green]✓ 日K数据下载完成，保存到 {DAILY_DIR}[/green]\n")
    
    # 下载5分钟数据（最近1年）
    if download_5min:
        console.print("[bold cyan]📊 下载5分钟数据 (最近1年)[/bold cyan]")
        min5_start = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        min5_end = today
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("下载5分钟数据", total=len(stocks))
            
            for code, name in stocks.items():
                progress.update(task, description=f"下载 {name}({code})")
                
                file_path = os.path.join(MIN5_DIR, f"{code}.csv")
                
                # 检查是否需要更新
                if not force and code in log.get("5min", {}):
                    last_date = log["5min"][code].get("end_date", "")
                    if last_date >= today:
                        progress.advance(task)
                        continue
                    # 增量更新
                    min5_start_code = (datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                else:
                    min5_start_code = min5_start
                
                df = download_5min_data(code, min5_start_code, min5_end)
                
                if not df.empty:
                    # 如果是增量更新，合并数据
                    if os.path.exists(file_path) and not force:
                        existing_df = pd.read_csv(file_path, parse_dates=['日期', 'datetime'])
                        df = pd.concat([existing_df, df]).drop_duplicates(subset=['datetime']).sort_values('datetime')
                    
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                    
                    # 更新日志
                    if "5min" not in log:
                        log["5min"] = {}
                    log["5min"][code] = {
                        "name": name,
                        "start_date": df['日期'].min().strftime('%Y-%m-%d'),
                        "end_date": df['日期'].max().strftime('%Y-%m-%d'),
                        "rows": len(df),
                        "updated_at": today
                    }
                
                progress.advance(task)
        
        console.print(f"[green]✓ 5分钟数据下载完成，保存到 {MIN5_DIR}[/green]\n")
    
    # 保存下载记录
    save_download_log(log)
    
    # 登出
    bs.logout()
    
    # 显示统计信息
    show_statistics(log)


def show_statistics(log: dict):
    """显示下载统计"""
    console.print("[bold]📈 下载统计[/bold]\n")
    
    # 日K统计
    if log.get("daily"):
        table = Table(title="日K数据", box=box.ROUNDED)
        table.add_column("股票代码", style="cyan")
        table.add_column("股票名称")
        table.add_column("起始日期", justify="center")
        table.add_column("结束日期", justify="center")
        table.add_column("数据条数", justify="right")
        
        total_rows = 0
        for code, info in log["daily"].items():
            table.add_row(
                code,
                info.get("name", ""),
                info.get("start_date", ""),
                info.get("end_date", ""),
                str(info.get("rows", 0))
            )
            total_rows += info.get("rows", 0)
        
        table.add_row("", "[bold]合计[/bold]", "", "", f"[bold]{total_rows:,}[/bold]")
        console.print(table)
        console.print()
    
    # 5分钟统计
    if log.get("5min"):
        table = Table(title="5分钟数据", box=box.ROUNDED)
        table.add_column("股票代码", style="cyan")
        table.add_column("股票名称")
        table.add_column("起始日期", justify="center")
        table.add_column("结束日期", justify="center")
        table.add_column("数据条数", justify="right")
        
        total_rows = 0
        for code, info in log["5min"].items():
            table.add_row(
                code,
                info.get("name", ""),
                info.get("start_date", ""),
                info.get("end_date", ""),
                str(info.get("rows", 0))
            )
            total_rows += info.get("rows", 0)
        
        table.add_row("", "[bold]合计[/bold]", "", "", f"[bold]{total_rows:,}[/bold]")
        console.print(table)


def main():
    parser = argparse.ArgumentParser(description="下载历史行情数据")
    parser.add_argument("--daily", "-d", action="store_true", help="只下载日K数据")
    parser.add_argument("--5min", "-m", dest="min5", action="store_true", help="只下载5分钟数据")
    parser.add_argument("--code", "-c", nargs="+", help="指定股票代码（多个用空格分隔）")
    parser.add_argument("--force", "-f", action="store_true", help="强制重新下载（忽略增量更新）")
    parser.add_argument("--list", "-l", action="store_true", help="显示股票列表")
    parser.add_argument("--stats", "-s", action="store_true", help="显示下载统计")
    
    args = parser.parse_args()
    
    if args.list:
        console.print("[bold]📋 支持的股票列表[/bold]\n")
        table = Table(box=box.ROUNDED)
        table.add_column("代码", style="cyan")
        table.add_column("名称")
        for code, name in STOCK_LIST.items():
            table.add_row(code, name)
        console.print(table)
        return
    
    if args.stats:
        log = load_download_log()
        show_statistics(log)
        return
    
    # 确定下载类型
    if args.daily and not args.min5:
        download_daily = True
        download_5min = False
    elif args.min5 and not args.daily:
        download_daily = False
        download_5min = True
    else:
        download_daily = True
        download_5min = True
    
    run_download(
        download_daily=download_daily,
        download_5min=download_5min,
        codes=args.code,
        force=args.force
    )


if __name__ == "__main__":
    main()

