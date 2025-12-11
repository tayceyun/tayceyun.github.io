#!/bin/bash
# ETF投资分析工具 - 一键运行脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "🔧 首次运行，正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 正在安装依赖..."
    pip install -r requirements.txt -q
else
    source venv/bin/activate
fi

# 运行分析
echo ""
python etf_analyzer.py

