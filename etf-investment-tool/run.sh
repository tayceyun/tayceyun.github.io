#!/bin/bash
# 投资分析工具 - 一键运行脚本
# 输出：终端显示 + HTML 报告

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Tushare API Token
export TUSHARE_TOKEN="60248d95f9274d71d389fb8c3def80d0929c4d155dc9cffbec917c84"

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

# 运行主分析脚本
python main.py

# 打开生成的 HTML 报告
TODAY=$(date +%Y-%m-%d)
REPORT_FILE="output/report_${TODAY}.html"
if [ -f "$REPORT_FILE" ]; then
    echo ""
    echo "📄 HTML报告已生成: $REPORT_FILE"
    # macOS 打开报告
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$REPORT_FILE"
    # Linux 打开报告
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "$REPORT_FILE" 2>/dev/null || echo "请手动打开报告文件"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "                      ✅ 分析完成                               "
echo "═══════════════════════════════════════════════════════════════"
