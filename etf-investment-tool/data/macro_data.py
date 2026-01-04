#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宏观数据获取模块

数据源：
1. 手动配置文件 config/macro_manual.json（优先）
2. AkShare 自动获取（备选）

包含：
1. 北向资金净流入
2. 10年期国债收益率
3. 制造业PMI
4. 指数PE估值分位
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')

# 配置文件路径
CONFIG_DIR = Path(__file__).parent.parent / "config"
MANUAL_CONFIG_FILE = CONFIG_DIR / "macro_manual.json"


def load_manual_config() -> Optional[Dict]:
    """加载手动配置的宏观数据
    
    Returns:
        配置字典，如果文件不存在或解析失败返回 None
    """
    if not MANUAL_CONFIG_FILE.exists():
        return None
    
    try:
        with open(MANUAL_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查配置日期是否是今天（超过3天的数据视为过期）
        update_date = config.get("update_date", "")
        if update_date:
            try:
                config_date = datetime.strptime(update_date, "%Y-%m-%d")
                days_old = (datetime.now() - config_date).days
                if days_old > 3:
                    print(f"[警告] 手动配置数据已过期 {days_old} 天，建议更新 config/macro_manual.json")
            except ValueError:
                pass
        
        return config
        
    except Exception as e:
        print(f"[警告] 读取手动配置失败: {e}")
        return None


# 加载手动配置（模块加载时执行一次）
_manual_config: Optional[Dict] = None


def get_manual_config() -> Optional[Dict]:
    """获取手动配置（带缓存）"""
    global _manual_config
    if _manual_config is None:
        _manual_config = load_manual_config()
        if _manual_config:
            print(f"[数据源] 使用手动配置 (更新日期: {_manual_config.get('update_date', '未知')})")
    return _manual_config

# 尝试导入 akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("[警告] akshare 未安装，宏观数据功能将使用模拟数据")


@dataclass
class MacroData:
    """宏观数据结构"""
    date: str                          # 数据日期
    bond_yield_10y: float              # 10年期国债收益率
    pmi: float                         # 制造业PMI
    north_money_5d: float              # 北向资金5日净流入（亿元）
    north_money_today: float           # 北向资金当日净流入（亿元）
    data_source: str = "akshare"       # 数据来源


@dataclass
class IndexValuation:
    """指数估值数据"""
    index_name: str                    # 指数名称
    pe: float                          # 当前PE
    pe_percentile: float               # PE分位（%）
    pb: float                          # 当前PB
    pb_percentile: float               # PB分位（%）
    dividend_yield: float              # 股息率（%）
    update_date: str                   # 更新日期


class MacroDataFetcher:
    """宏观数据获取器"""
    
    # 指数名称映射（用于韭圈儿PE查询）
    INDEX_NAME_MAP = {
        "000001": "上证指数",
        "000300": "沪深300",
        "000016": "上证50",
        "000905": "中证500",
        "000852": "中证1000",
        "399303": "国证2000",
        "399006": "创业板指",
        "000688": "科创50",
    }
    
    # 韭圈儿支持的指数名称
    FUNDDB_INDEX_MAP = {
        "000001": "上证指数",
        "000300": "沪深300",
        "000016": "上证50",
        "000905": "中证500",
        "000852": "中证1000",
        "399006": "创业板指",
        # 注：科创50、国证2000 韭圈儿可能不支持
    }
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, datetime] = {}
        self._cache_duration = timedelta(hours=1)  # 缓存1小时
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self._cache_time:
            return False
        return datetime.now() - self._cache_time[key] < self._cache_duration
    
    def get_north_money(self, days: int = 5) -> Dict[str, float]:
        """获取北向资金数据
        
        Returns:
            {
                "today": 当日净流入（亿元）,
                "5d_sum": 5日累计净流入（亿元）,
                "10d_sum": 10日累计净流入（亿元）
            }
        """
        cache_key = "north_money"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        result = {"today": 0.0, "5d_sum": 0.0, "10d_sum": 0.0}
        
        # 1. 优先使用手动配置
        manual = get_manual_config()
        if manual:
            macro_data = manual.get("基础宏观数据", {})
            if macro_data.get("north_money_today") is not None:
                result = {
                    "today": float(macro_data.get("north_money_today", 0)),
                    "5d_sum": float(macro_data.get("north_money_5d", 0)),
                    "10d_sum": float(macro_data.get("north_money_5d", 0)) * 2  # 估算
                }
                self._cache[cache_key] = result
                self._cache_time[cache_key] = datetime.now()
                return result
        
        # 2. 尝试 AkShare 自动获取
        if not AKSHARE_AVAILABLE:
            # 模拟数据
            result = {"today": 50.0, "5d_sum": 120.0, "10d_sum": 200.0}
        else:
            try:
                # 获取北向资金历史数据（使用正确的API名称）
                df = ak.stock_hsgt_hist_em(symbol="北向资金")
                if df is not None and not df.empty:
                    # 确保日期列存在并排序
                    if '日期' in df.columns:
                        df = df.sort_values('日期', ascending=False)
                    
                    # 获取净流入列
                    flow_col = None
                    for col in ['当日净流入', '净流入', '资金净流入']:
                        if col in df.columns:
                            flow_col = col
                            break
                    
                    if flow_col:
                        df[flow_col] = pd.to_numeric(df[flow_col], errors='coerce')
                        recent = df.head(10)
                        
                        if len(recent) > 0:
                            result["today"] = float(recent.iloc[0][flow_col]) if len(recent) > 0 else 0.0
                            result["5d_sum"] = float(recent.head(5)[flow_col].sum()) if len(recent) >= 5 else 0.0
                            result["10d_sum"] = float(recent.head(10)[flow_col].sum()) if len(recent) >= 10 else 0.0
                        
            except Exception as e:
                print(f"[警告] 获取北向资金数据失败: {e}")
                result = {"today": 0.0, "5d_sum": 0.0, "10d_sum": 0.0}
        
        self._cache[cache_key] = result
        self._cache_time[cache_key] = datetime.now()
        return result
    
    def get_bond_yield_10y(self) -> float:
        """获取10年期国债收益率
        
        Returns:
            收益率（%），如 2.85 表示 2.85%
        """
        cache_key = "bond_yield_10y"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        result = 2.5  # 默认值
        
        # 1. 优先使用手动配置
        manual = get_manual_config()
        if manual:
            macro_data = manual.get("基础宏观数据", {})
            if macro_data.get("bond_yield_10y") is not None:
                result = float(macro_data.get("bond_yield_10y", 2.5))
                self._cache[cache_key] = result
                self._cache_time[cache_key] = datetime.now()
                return result
        
        # 2. 尝试 AkShare 自动获取
        if not AKSHARE_AVAILABLE:
            result = 2.8  # 模拟数据
        else:
            try:
                # 获取中美国债收益率
                df = ak.bond_zh_us_rate()
                if df is not None and not df.empty:
                    # 获取最新的中国10年期国债收益率
                    latest = df.iloc[-1]
                    if '中国国债收益率10年' in df.columns:
                        result = float(latest['中国国债收益率10年'])
                    elif '中国10年' in df.columns:
                        result = float(latest['中国10年'])
                        
            except Exception as e:
                print(f"[警告] 获取国债收益率失败: {e}")
        
        self._cache[cache_key] = result
        self._cache_time[cache_key] = datetime.now()
        return result
    
    def get_pmi(self) -> float:
        """获取制造业PMI
        
        Returns:
            PMI值，如 51.2
        """
        cache_key = "pmi"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        result = 50.0  # 默认值（荣枯线）
        
        # 1. 优先使用手动配置
        manual = get_manual_config()
        if manual:
            macro_data = manual.get("基础宏观数据", {})
            if macro_data.get("pmi") is not None:
                result = float(macro_data.get("pmi", 50.0))
                self._cache[cache_key] = result
                self._cache_time[cache_key] = datetime.now()
                return result
        
        # 2. 尝试 AkShare 自动获取
        if not AKSHARE_AVAILABLE:
            result = 51.0  # 模拟数据
        else:
            try:
                # 获取PMI数据
                df = ak.macro_china_pmi_yearly()
                if df is not None and not df.empty:
                    # 获取最新的制造业PMI
                    latest = df.iloc[-1]
                    if '制造业' in df.columns:
                        result = float(latest['制造业'])
                    elif 'pmi' in df.columns.str.lower():
                        result = float(latest[df.columns[df.columns.str.lower().str.contains('pmi')][0]])
                        
            except Exception as e:
                print(f"[警告] 获取PMI数据失败: {e}")
        
        self._cache[cache_key] = result
        self._cache_time[cache_key] = datetime.now()
        return result
    
    def get_index_valuation(self, index_code: str) -> Optional[IndexValuation]:
        """获取指数估值数据（PE分位等）
        
        Args:
            index_code: 指数代码（如 "000300"）
        
        Returns:
            IndexValuation 或 None
        """
        cache_key = f"valuation_{index_code}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        index_name = self.FUNDDB_INDEX_MAP.get(index_code, self.INDEX_NAME_MAP.get(index_code, index_code))
        
        # 1. 优先使用手动配置
        manual = get_manual_config()
        if manual:
            valuations = manual.get("估值数据", {})
            if index_code in valuations:
                v = valuations[index_code]
                result = IndexValuation(
                    index_name=v.get("name", index_name),
                    pe=float(v.get("pe", 15.0)),
                    pe_percentile=float(v.get("pe_percentile", 50.0)),
                    pb=float(v.get("pb", 1.5)),
                    pb_percentile=float(v.get("pb_percentile", 50.0)),
                    dividend_yield=float(v.get("dividend_yield", 2.0)),
                    update_date=manual.get("update_date", datetime.now().strftime("%Y-%m-%d"))
                )
                self._cache[cache_key] = result
                self._cache_time[cache_key] = datetime.now()
                return result
        
        # 2. 尝试 AkShare 自动获取
        if index_code not in self.FUNDDB_INDEX_MAP:
            # 不支持的指数，返回模拟数据
            return IndexValuation(
                index_name=index_name,
                pe=15.0,
                pe_percentile=50.0,
                pb=1.5,
                pb_percentile=50.0,
                dividend_yield=2.0,
                update_date=datetime.now().strftime("%Y-%m-%d")
            )
        
        if not AKSHARE_AVAILABLE:
            # 模拟数据
            return IndexValuation(
                index_name=index_name,
                pe=15.0,
                pe_percentile=50.0,
                pb=1.5,
                pb_percentile=50.0,
                dividend_yield=2.0,
                update_date=datetime.now().strftime("%Y-%m-%d")
            )
        
        try:
            # 尝试使用中证指数官网数据
            # 指数代码映射
            csindex_map = {
                "沪深300": "000300",
                "中证500": "000905",
                "中证1000": "000852",
                "上证50": "000016",
                "上证指数": "000001",
                "创业板指": "399006",
            }
            
            cs_code = csindex_map.get(index_name)
            if cs_code and hasattr(ak, 'stock_zh_index_value_csindex'):
                try:
                    df = ak.stock_zh_index_value_csindex(symbol=cs_code)
                    if df is not None and not df.empty:
                        # 获取最新数据
                        latest = df.iloc[-1]
                        
                        current_pe = float(latest.get('市盈率', 15.0)) if pd.notna(latest.get('市盈率')) else 15.0
                        current_pb = float(latest.get('市净率', 1.5)) if pd.notna(latest.get('市净率')) else 1.5
                        
                        # 计算历史分位
                        if '市盈率' in df.columns and len(df) > 0:
                            pe_percentile = float((df['市盈率'] <= current_pe).sum() / len(df) * 100)
                        else:
                            pe_percentile = 50.0
                        
                        if '市净率' in df.columns and len(df) > 0:
                            pb_percentile = float((df['市净率'] <= current_pb).sum() / len(df) * 100)
                        else:
                            pb_percentile = 50.0
                        
                        result = IndexValuation(
                            index_name=index_name,
                            pe=round(current_pe, 2),
                            pe_percentile=round(pe_percentile, 1),
                            pb=round(current_pb, 2),
                            pb_percentile=round(pb_percentile, 1),
                            dividend_yield=0.0,
                            update_date=datetime.now().strftime("%Y-%m-%d")
                        )
                        
                        self._cache[cache_key] = result
                        self._cache_time[cache_key] = datetime.now()
                        return result
                except Exception:
                    pass  # 继续使用默认值
            
            # 如果无法获取真实数据，返回默认估值
            return IndexValuation(
                index_name=index_name,
                pe=15.0,
                pe_percentile=50.0,
                pb=1.5,
                pb_percentile=50.0,
                dividend_yield=0.0,
                update_date=datetime.now().strftime("%Y-%m-%d")
            )
            
        except Exception as e:
            print(f"[警告] 获取 {index_name} 估值数据失败: {e}")
            return IndexValuation(
                index_name=index_name,
                pe=15.0,
                pe_percentile=50.0,
                pb=1.5,
                pb_percentile=50.0,
                dividend_yield=0.0,
                update_date=datetime.now().strftime("%Y-%m-%d")
            )
    
    def get_all_macro_data(self) -> MacroData:
        """获取所有宏观数据
        
        Returns:
            MacroData 对象
        """
        north_money = self.get_north_money()
        bond_yield = self.get_bond_yield_10y()
        pmi = self.get_pmi()
        
        return MacroData(
            date=datetime.now().strftime("%Y-%m-%d"),
            bond_yield_10y=bond_yield,
            pmi=pmi,
            north_money_5d=north_money["5d_sum"],
            north_money_today=north_money["today"],
            data_source="akshare" if AKSHARE_AVAILABLE else "mock"
        )
    
    def get_pe_diff(self, index1_code: str, index2_code: str) -> float:
        """计算两个指数的PE分位差
        
        Args:
            index1_code: 指数1代码
            index2_code: 指数2代码
        
        Returns:
            index1 PE分位 - index2 PE分位
        """
        val1 = self.get_index_valuation(index1_code)
        val2 = self.get_index_valuation(index2_code)
        
        if val1 and val2:
            return val1.pe_percentile - val2.pe_percentile
        return 0.0


# 单例
_macro_fetcher: Optional[MacroDataFetcher] = None


def get_macro_fetcher() -> MacroDataFetcher:
    """获取宏观数据获取器单例"""
    global _macro_fetcher
    if _macro_fetcher is None:
        _macro_fetcher = MacroDataFetcher()
    return _macro_fetcher


# 便捷函数
def get_macro_data() -> MacroData:
    """获取宏观数据"""
    return get_macro_fetcher().get_all_macro_data()


def get_index_valuation(index_code: str) -> Optional[IndexValuation]:
    """获取指数估值"""
    return get_macro_fetcher().get_index_valuation(index_code)


# 测试
if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    fetcher = MacroDataFetcher()
    
    # 获取宏观数据
    console.print("\n[bold cyan]宏观数据[/bold cyan]")
    macro = fetcher.get_all_macro_data()
    console.print(f"  日期: {macro.date}")
    console.print(f"  10Y国债收益率: {macro.bond_yield_10y}%")
    console.print(f"  PMI: {macro.pmi}")
    console.print(f"  北向资金(今日): {macro.north_money_today}亿")
    console.print(f"  北向资金(5日): {macro.north_money_5d}亿")
    console.print(f"  数据源: {macro.data_source}")
    
    # 获取指数估值
    console.print("\n[bold cyan]指数估值[/bold cyan]")
    table = Table(show_header=True)
    table.add_column("指数")
    table.add_column("PE", justify="right")
    table.add_column("PE分位", justify="right")
    table.add_column("PB", justify="right")
    table.add_column("PB分位", justify="right")
    
    for code in ["000300", "000905", "000852", "399006"]:
        val = fetcher.get_index_valuation(code)
        if val:
            table.add_row(
                val.index_name,
                f"{val.pe:.2f}",
                f"{val.pe_percentile:.1f}%",
                f"{val.pb:.2f}",
                f"{val.pb_percentile:.1f}%"
            )
    
    console.print(table)

