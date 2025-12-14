#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据获取模块
默认使用 Baostock（免费），ETF 数据需要 Tushare Pro
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache

import baostock as bs

# Tushare 仅在需要 ETF 数据时延迟加载
_ts = None
_pro = None

# Tushare Token（仅 ETF 功能需要）
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '60248d95f9274d71d389fb8c3def80d0929c4d155dc9cffbec917c84')


def _get_pro():
    """获取 Tushare Pro API 实例（延迟加载，仅 ETF 功能需要）"""
    global _ts, _pro
    if _pro is None:
        try:
            import tushare as ts
            _ts = ts
            token = os.getenv('TUSHARE_TOKEN', TUSHARE_TOKEN)
            if not token:
                raise ValueError("ETF 功能需要设置 TUSHARE_TOKEN")
            ts.set_token(token)
            _pro = ts.pro_api()
        except ImportError:
            raise ImportError("ETF 功能需要安装 tushare: pip install tushare")
    return _pro


def _convert_code_to_ts(code: str) -> str:
    """将普通代码转换为 Tushare 格式
    
    000630 -> 000630.SZ
    601899 -> 601899.SH
    159941 -> 159941.SZ
    513500 -> 513500.SH
    """
    if code.startswith(('0', '3')):
        return f"{code}.SZ"
    elif code.startswith('6'):
        return f"{code}.SH"
    elif code.startswith('1'):  # 深市 ETF
        return f"{code}.SZ"
    elif code.startswith('5'):  # 沪市 ETF
        return f"{code}.SH"
    else:
        return f"{code}.SH"


def _standardize_columns(df: pd.DataFrame, is_index: bool = False) -> pd.DataFrame:
    """标准化列名，与原有代码兼容"""
    if df is None or df.empty:
        return df
    
    column_map = {
        'trade_date': '日期',
        'open': '开盘',
        'high': '最高',
        'low': '最低',
        'close': '收盘',
        'vol': '成交量',
        'amount': '成交额',
        'pct_chg': '涨跌幅',
    }
    
    df = df.rename(columns=column_map)
    
    if '日期' in df.columns:
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期').reset_index(drop=True)
    
    return df


def get_etf_daily(code: str, days: int = 120) -> pd.DataFrame:
    """获取 ETF 日线数据
    
    Args:
        code: ETF 代码，如 '159941'
        days: 获取最近多少天的数据
    
    Returns:
        DataFrame with columns: 日期, 开盘, 最高, 最低, 收盘, 成交量
    """
    pro = _get_pro()
    ts_code = _convert_code_to_ts(code)
    
    # 多取一些数据，确保有足够的交易日
    start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y%m%d')
    end_date = datetime.now().strftime('%Y%m%d')
    
    try:
        df = pro.fund_daily(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date
        )
        df = _standardize_columns(df)
        return df.tail(days)
    except Exception as e:
        print(f"[错误] 获取 ETF {code} 数据失败: {e}")
        return pd.DataFrame()


def get_etf_monthly(code: str, months: int = 6) -> pd.DataFrame:
    """获取 ETF 月线数据
    
    Args:
        code: ETF 代码
        months: 获取最近多少个月的数据
    
    Returns:
        DataFrame with columns: 日期, 开盘, 最高, 最低, 收盘, 成交量
    """
    # Tushare 没有直接的月线接口，用日线数据聚合
    df = get_etf_daily(code, days=months * 25)
    if df.empty:
        return df
    
    df['月份'] = df['日期'].dt.to_period('M')
    monthly = df.groupby('月份').agg({
        '日期': 'last',
        '开盘': 'first',
        '最高': 'max',
        '最低': 'min',
        '收盘': 'last',
        '成交量': 'sum'
    }).reset_index(drop=True)
    
    return monthly


def get_stock_daily(code: str, days: int = 250) -> pd.DataFrame:
    """获取个股日线数据（使用 Baostock）
    
    Args:
        code: 股票代码，如 '000630'
        days: 获取最近多少天的数据
    
    Returns:
        DataFrame with columns: 日期, 开盘, 最高, 最低, 收盘, 成交量
    """
    # 使用 Baostock 获取数据（免费）
    return get_stock_daily_baostock(code, days=days)


def get_index_daily(code: str = "000001", days: int = 60) -> pd.DataFrame:
    """获取指数日线数据（使用 Baostock）
    
    Args:
        code: 指数代码，如 '000001' (上证指数)
        days: 获取最近多少天的数据
    
    Returns:
        DataFrame with columns: 日期, 开盘, 最高, 最低, 收盘, 成交量
    """
    # Baostock 指数代码格式
    if code == "000001":
        bs_code = "sh.000001"  # 上证指数
    elif code == "399001":
        bs_code = "sz.399001"  # 深证成指
    elif code == "000300":
        bs_code = "sh.000300"  # 沪深300
    else:
        bs_code = f"sh.{code}"
    
    # 登录 baostock
    lg = bs.login()
    if lg.error_code != '0':
        print(f"[错误] Baostock 登录失败: {lg.error_msg}")
        return pd.DataFrame()
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y-%m-%d')
        
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="d"
        )
        
        if rs.error_code != '0':
            print(f"[错误] 获取指数 {code} 数据失败: {rs.error_msg}")
            return pd.DataFrame()
        
        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())
        
        if not data_list:
            return pd.DataFrame()
        
        df = pd.DataFrame(data_list, columns=['日期', '开盘', '最高', '最低', '收盘', '成交量'])
        df['日期'] = pd.to_datetime(df['日期'])
        for col in ['开盘', '最高', '最低', '收盘']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
        
        df = df.sort_values('日期').reset_index(drop=True)
        return df.tail(days)
        
    except Exception as e:
        print(f"[错误] 获取指数 {code} 数据失败: {e}")
        return pd.DataFrame()
    finally:
        bs.logout()


def get_etf_realtime(code: str) -> dict:
    """获取 ETF 实时行情（包含溢价率）
    
    注意：Tushare 免费版不提供实时行情，这里返回最新收盘价
    溢价率需要另外的数据源
    
    Args:
        code: ETF 代码
    
    Returns:
        dict with keys: current_price, premium_rate (溢价率暂返回0)
    """
    df = get_etf_daily(code, days=5)
    if df.empty:
        return {"current_price": 0, "premium_rate": 0}
    
    return {
        "current_price": float(df['收盘'].iloc[-1]),
        "premium_rate": 0.0  # Tushare 免费版不提供溢价率
    }


def get_historical_data(code: str, start_date: str = None, end_date: str = None, 
                        days: int = 250) -> pd.DataFrame:
    """获取历史数据（用于回测，使用 Baostock）
    
    Args:
        code: 股票代码（ETF 暂不支持）
        start_date: 开始日期 'YYYY-MM-DD'
        end_date: 结束日期 'YYYY-MM-DD'
        days: 如果不指定日期，获取最近多少天
    
    Returns:
        DataFrame
    """
    # 判断是 ETF 还是股票
    is_etf = code.startswith(('1', '5'))
    
    if is_etf:
        print(f"[警告] Baostock 不支持 ETF 数据，代码 {code} 无法获取")
        return pd.DataFrame()
    
    # 使用 Baostock 获取个股数据
    df = get_stock_daily_baostock(code, start_date, end_date, days=days + 120)
    
    if df.empty:
        return df
    
    # 按日期范围筛选
    if start_date:
        df = df[df['日期'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['日期'] <= pd.to_datetime(end_date)]
    
    return df


# =============================================================================
# Baostock 数据源（免费，支持长历史数据）
# =============================================================================

def _convert_code_to_bs(code: str) -> str:
    """将普通代码转换为 Baostock 格式
    
    000630 -> sz.000630
    601899 -> sh.601899
    """
    if code.startswith(('0', '3')):
        return f"sz.{code}"
    elif code.startswith('6'):
        return f"sh.{code}"
    else:
        return f"sh.{code}"


def get_stock_daily_baostock(code: str, start_date: str = None, end_date: str = None,
                              days: int = 500) -> pd.DataFrame:
    """使用 Baostock 获取个股日线数据（免费，支持长历史）
    
    Args:
        code: 股票代码，如 '601899'
        start_date: 开始日期 'YYYY-MM-DD'
        end_date: 结束日期 'YYYY-MM-DD'
        days: 如果不指定日期，获取最近多少天的数据
    
    Returns:
        DataFrame with columns: 日期, 开盘, 最高, 最低, 收盘, 成交量
    """
    # 登录 baostock
    lg = bs.login()
    if lg.error_code != '0':
        print(f"[错误] Baostock 登录失败: {lg.error_msg}")
        return pd.DataFrame()
    
    try:
        bs_code = _convert_code_to_bs(code)
        
        # 计算日期范围
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y-%m-%d')
        
        # 获取日线数据
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="2"  # 前复权
        )
        
        if rs.error_code != '0':
            print(f"[错误] 获取股票 {code} 数据失败: {rs.error_msg}")
            return pd.DataFrame()
        
        # 转换为 DataFrame
        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())
        
        if not data_list:
            print(f"[警告] 股票 {code} 无数据")
            return pd.DataFrame()
        
        df = pd.DataFrame(data_list, columns=['日期', '开盘', '最高', '最低', '收盘', '成交量'])
        
        # 转换数据类型
        df['日期'] = pd.to_datetime(df['日期'])
        for col in ['开盘', '最高', '最低', '收盘']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
        
        # 排序并返回最近 days 天
        df = df.sort_values('日期').reset_index(drop=True)
        return df.tail(days)
        
    except Exception as e:
        print(f"[错误] 获取股票 {code} 数据失败: {e}")
        return pd.DataFrame()
    finally:
        bs.logout()


def get_stock_monthly_baostock(code: str, months: int = 12) -> pd.DataFrame:
    """使用 Baostock 获取个股月线数据
    
    Args:
        code: 股票代码
        months: 获取最近多少个月的数据
    
    Returns:
        DataFrame with columns: 日期, 开盘, 最高, 最低, 收盘, 成交量
    """
    # 登录 baostock
    lg = bs.login()
    if lg.error_code != '0':
        print(f"[错误] Baostock 登录失败: {lg.error_msg}")
        return pd.DataFrame()
    
    try:
        bs_code = _convert_code_to_bs(code)
        
        # 计算日期范围
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=months * 35)).strftime('%Y-%m-%d')
        
        # 获取月线数据
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="m",  # 月线
            adjustflag="2"  # 前复权
        )
        
        if rs.error_code != '0':
            print(f"[错误] 获取股票 {code} 月线数据失败: {rs.error_msg}")
            return pd.DataFrame()
        
        # 转换为 DataFrame
        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())
        
        if not data_list:
            return pd.DataFrame()
        
        df = pd.DataFrame(data_list, columns=['日期', '开盘', '最高', '最低', '收盘', '成交量'])
        
        # 转换数据类型
        df['日期'] = pd.to_datetime(df['日期'])
        for col in ['开盘', '最高', '最低', '收盘']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
        
        df = df.sort_values('日期').reset_index(drop=True)
        return df.tail(months)
        
    except Exception as e:
        print(f"[错误] 获取股票 {code} 月线数据失败: {e}")
        return pd.DataFrame()
    finally:
        bs.logout()


def get_historical_data_baostock(code: str, start_date: str = None, end_date: str = None,
                                  days: int = 500) -> pd.DataFrame:
    """使用 Baostock 获取历史数据（用于回测）
    
    Args:
        code: 股票代码
        start_date: 开始日期 'YYYY-MM-DD'
        end_date: 结束日期 'YYYY-MM-DD'
        days: 如果不指定日期，获取最近多少天
    
    Returns:
        DataFrame
    """
    return get_stock_daily_baostock(code, start_date, end_date, days)


def get_stock_minute_baostock(code: str, start_date: str = None, end_date: str = None,
                               days: int = 30, frequency: str = "5") -> pd.DataFrame:
    """使用 Baostock 获取个股分钟级别K线数据
    
    Args:
        code: 股票代码，如 '601899'
        start_date: 开始日期 'YYYY-MM-DD'
        end_date: 结束日期 'YYYY-MM-DD'
        days: 如果不指定日期，获取最近多少天的数据
        frequency: 分钟级别 "5", "15", "30", "60"
    
    Returns:
        DataFrame with columns: 日期, 时间, 开盘, 最高, 最低, 收盘, 成交量, datetime
    """
    lg = bs.login()
    if lg.error_code != '0':
        print(f"[错误] Baostock 登录失败: {lg.error_msg}")
        return pd.DataFrame()
    
    try:
        bs_code = _convert_code_to_bs(code)
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 获取分钟K线数据
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,time,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            adjustflag="2"  # 前复权
        )
        
        if rs.error_code != '0':
            print(f"[错误] 获取股票 {code} {frequency}分钟数据失败: {rs.error_msg}")
            return pd.DataFrame()
        
        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())
        
        if not data_list:
            print(f"[警告] 股票 {code} 无{frequency}分钟数据")
            return pd.DataFrame()
        
        df = pd.DataFrame(data_list, columns=['日期', '时间', '开盘', '最高', '最低', '收盘', '成交量'])
        
        # 转换数据类型
        df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d')
        # Baostock 分钟数据时间格式: 20241213093500000 (年月日时分秒毫秒，17位)
        # 或者 093500000 (时分秒毫秒，9-12位)
        df['时间'] = df['时间'].astype(str)
        for col in ['开盘', '最高', '最低', '收盘']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
        
        # 创建完整的日期时间列
        # 时间格式可能是: 20241213093500000 (17位) 或 093500000 (9位以上)
        def parse_time(row):
            time_str = str(row['时间'])
            date_str = row['日期'].strftime('%Y-%m-%d')
            if len(time_str) >= 12:
                # 长格式: 20241213093500000，取时分部分
                hour = time_str[8:10] if len(time_str) >= 17 else time_str[:2]
                minute = time_str[10:12] if len(time_str) >= 17 else time_str[2:4]
            else:
                # 短格式: 093500000
                hour = time_str[:2]
                minute = time_str[2:4]
            return f"{date_str} {hour}:{minute}:00"
        
        df['datetime'] = pd.to_datetime(df.apply(parse_time, axis=1), format='%Y-%m-%d %H:%M:%S')
        
        df = df.sort_values('datetime').reset_index(drop=True)
        return df
        
    except Exception as e:
        print(f"[错误] 获取股票 {code} {frequency}分钟数据失败: {e}")
        return pd.DataFrame()
    finally:
        bs.logout()


def get_stock_10min_baostock(code: str, start_date: str = None, end_date: str = None,
                              days: int = 30) -> pd.DataFrame:
    """使用 Baostock 获取个股10分钟K线数据（通过5分钟聚合）
    
    Args:
        code: 股票代码，如 '601899'
        start_date: 开始日期 'YYYY-MM-DD'
        end_date: 结束日期 'YYYY-MM-DD'
        days: 如果不指定日期，获取最近多少天的数据
    
    Returns:
        DataFrame with columns: 日期, 时间, 开盘, 最高, 最低, 收盘, 成交量, datetime
    """
    # 获取5分钟数据
    df_5min = get_stock_minute_baostock(code, start_date, end_date, days, frequency="5")
    
    if df_5min.empty:
        return pd.DataFrame()
    
    # 将时间向下取整到10分钟
    df_5min['time_10min'] = df_5min['datetime'].dt.floor('10min')
    
    # 按10分钟聚合
    df_10min = df_5min.groupby('time_10min').agg({
        '日期': 'first',
        '时间': 'first',
        '开盘': 'first',
        '最高': 'max',
        '最低': 'min',
        '收盘': 'last',
        '成交量': 'sum'
    }).reset_index()
    
    df_10min = df_10min.rename(columns={'time_10min': 'datetime'})
    df_10min = df_10min.sort_values('datetime').reset_index(drop=True)
    
    return df_10min


# 测试函数
if __name__ == "__main__":
    print("测试 Tushare 数据获取...")
    
    # 测试 ETF
    df = get_etf_daily("159941", days=10)
    print(f"\n纳指100ETF 最近10天数据:")
    print(df)
    
    # 测试股票
    df = get_stock_daily("000630", days=10)
    print(f"\n铜陵有色 最近10天数据:")
    print(df)
    
    # 测试指数
    df = get_index_daily("000001", days=10)
    print(f"\n上证指数 最近10天数据:")
    print(df)
    
    # 测试10分钟K线
    print("\n测试10分钟K线数据...")
    df = get_stock_10min_baostock("601899", days=5)
    print(f"\n铜陵有色 最近5天10分钟K线数据:")
    print(df.head(20) if not df.empty else "无数据")


