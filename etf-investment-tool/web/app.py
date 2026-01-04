#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Web 后端

功能：
1. 触发指数/个股分析
2. 获取历史报告列表
3. 查看报告详情
4. 配置管理

启动方式：
    cd etf-investment-tool
    python -m uvicorn web.app:app --reload --port 8000

或者直接运行：
    python web/app.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("[警告] FastAPI 未安装，Web 功能不可用")
    print("[提示] 安装方法: pip install fastapi uvicorn")

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 配置目录
CONFIG_DIR = PROJECT_ROOT / "config"


def cleanup_old_reports(report_type: str, keep_latest: int = 1, index_code: str = None):
    """
    清理旧报告，只保留最新的 N 个
    
    Args:
        report_type: 报告类型 ("market", "index", "stock", "report")
        keep_latest: 保留最新的报告数量，默认1
        index_code: 对于 index 类型，指定指数代码
    """
    if not OUTPUT_DIR.exists():
        return
    
    if report_type == "market":
        pattern = "market_*.html"
    elif report_type == "index":
        if index_code:
            pattern = f"index_{index_code}_*.html"
        else:
            pattern = "index_*.html"
    elif report_type == "stock":
        pattern = "stock_*.html"
    elif report_type == "report":
        pattern = "report_*.html"
    else:
        return
    
    files = list(OUTPUT_DIR.glob(pattern))
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    for old_file in files[keep_latest:]:
        try:
            old_file.unlink()
        except Exception:
            pass

# 静态文件目录
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)


# ============= Pydantic 模型 =============

class AnalysisRequest(BaseModel):
    """分析请求"""
    index_code: str = "000001"
    include_capital: bool = False


class AnalysisResponse(BaseModel):
    """分析响应"""
    success: bool
    message: str
    report_path: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ReportInfo(BaseModel):
    """报告信息"""
    filename: str
    filepath: str
    created_time: str
    report_type: str
    index_code: Optional[str] = None


class ConfigResponse(BaseModel):
    """配置响应"""
    success: bool
    config: Optional[Dict[str, Any]] = None
    message: str = ""


# ============= FastAPI App =============

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="多周期共振分析系统",
        description="指数/个股多周期技术分析与资金面分析 API",
        version="1.0.0"
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 静态文件
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


    # ============= API 路由 =============
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """首页"""
        index_html = STATIC_DIR / "index.html"
        if index_html.exists():
            return FileResponse(index_html)
        
        # 如果没有静态页面，返回简单的 HTML
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>多周期共振分析系统</title>
            <style>
                body { font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #333; }
                a { color: #3B82F6; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>📊 多周期共振分析系统</h1>
            <p>API 服务已启动</p>
            
            <h2>可用接口</h2>
            <div class="endpoint">
                <strong>POST /api/analyze/index</strong> - 执行指数分析
            </div>
            <div class="endpoint">
                <strong>GET /api/reports</strong> - 获取报告列表
            </div>
            <div class="endpoint">
                <strong>GET /api/reports/{filename}</strong> - 获取报告详情
            </div>
            <div class="endpoint">
                <strong>GET /api/config</strong> - 获取配置
            </div>
            
            <p><a href="/docs">查看完整 API 文档</a></p>
        </body>
        </html>
        """
    
    @app.post("/api/analyze/index", response_model=AnalysisResponse)
    async def analyze_index(request: AnalysisRequest):
        """执行指数分析
        
        Args:
            request: 分析请求参数
        
        Returns:
            分析结果
        """
        try:
            from analyzers.index_analyzer import IndexAnalyzer
            from jinja2 import Template
            
            analyzer = IndexAnalyzer(request.index_code)
            result = analyzer.analyze()
            
            if result is None:
                return AnalysisResponse(
                    success=False,
                    message="分析失败，无法获取数据"
                )
            
            # 生成报告
            template_path = PROJECT_ROOT / "templates" / "index_report.html"
            report_path = None
            
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = Template(f.read())
                
                data = analyzer.to_dict(result)
                html_content = template.render(**data)
                
                report_name = f"index_{request.index_code}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.html"
                report_file = OUTPUT_DIR / report_name
                
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # 清理该指数的旧报告，只保留最新的1个
                cleanup_old_reports("index", keep_latest=1, index_code=request.index_code)
                
                report_path = str(report_file)
            
            return AnalysisResponse(
                success=True,
                message="分析完成",
                report_path=report_path,
                data=analyzer.to_dict(result)
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return AnalysisResponse(
                success=False,
                message=f"分析出错: {str(e)}"
            )
    
    @app.get("/api/reports", response_model=List[ReportInfo])
    async def list_reports(
        report_type: Optional[str] = Query(None, description="报告类型: index/stock"),
        limit: int = Query(20, description="返回数量限制")
    ):
        """获取报告列表
        
        Args:
            report_type: 报告类型筛选
            limit: 返回数量限制
        
        Returns:
            报告列表
        """
        reports = []
        
        if not OUTPUT_DIR.exists():
            return reports
        
        for file in sorted(OUTPUT_DIR.glob("*.html"), key=os.path.getmtime, reverse=True):
            filename = file.name
            
            # 解析报告类型
            if filename.startswith("index_"):
                rtype = "index"
                # 提取指数代码
                parts = filename.split("_")
                index_code = parts[1] if len(parts) > 1 else None
            elif filename.startswith("stock_"):
                rtype = "stock"
                index_code = None
            else:
                rtype = "other"
                index_code = None
            
            # 筛选
            if report_type and rtype != report_type:
                continue
            
            reports.append(ReportInfo(
                filename=filename,
                filepath=str(file),
                created_time=datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                report_type=rtype,
                index_code=index_code
            ))
            
            if len(reports) >= limit:
                break
        
        return reports
    
    @app.get("/api/reports/{filename}")
    async def get_report(filename: str):
        """获取报告内容
        
        Args:
            filename: 报告文件名
        
        Returns:
            报告 HTML 内容
        """
        report_path = OUTPUT_DIR / filename
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="报告不存在")
        
        return FileResponse(report_path, media_type="text/html")
    
    @app.get("/api/config", response_model=ConfigResponse)
    async def get_config():
        """获取配置"""
        try:
            import json
            
            config_file = CONFIG_DIR / "signal_rules.json"
            
            if not config_file.exists():
                return ConfigResponse(
                    success=False,
                    message="配置文件不存在"
                )
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return ConfigResponse(
                success=True,
                config=config
            )
            
        except Exception as e:
            return ConfigResponse(
                success=False,
                message=f"读取配置失败: {str(e)}"
            )
    
    @app.get("/api/capital-flow")
    async def get_capital_flow():
        """获取资金面数据"""
        try:
            from data.capital_flow import CapitalFlowAnalyzer
            
            analyzer = CapitalFlowAnalyzer()
            summary = analyzer.get_capital_flow_summary()
            
            return JSONResponse(content={
                "success": True,
                "data": summary
            })
            
        except Exception as e:
            return JSONResponse(content={
                "success": False,
                "message": f"获取资金面数据失败: {str(e)}"
            })
    
    @app.get("/api/pressure-line")
    async def get_pressure_line(date: Optional[str] = None):
        """获取压力线位置
        
        Args:
            date: 日期，格式 YYYY-MM-DD，默认今天
        """
        try:
            from analyzers.pressure_line import PressureLineCalculator
            
            calc = PressureLineCalculator()
            
            if date:
                position = calc.get_position_by_str(date)
            else:
                position = calc.get_position(datetime.now())
            
            return JSONResponse(content={
                "success": True,
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "pressure_position": position
            })
            
        except Exception as e:
            return JSONResponse(content={
                "success": False,
                "message": f"计算压力线失败: {str(e)}"
            })
    
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {"status": "ok", "time": datetime.now().isoformat()}


# ============= 主函数 =============

def main():
    """启动 Web 服务"""
    if not FASTAPI_AVAILABLE:
        print("[错误] FastAPI 未安装，无法启动 Web 服务")
        print("[提示] 安装方法: pip install fastapi uvicorn")
        return
    
    import uvicorn
    
    print("=" * 60)
    print("多周期共振分析系统 - Web 服务")
    print("=" * 60)
    print(f"访问地址: http://localhost:8000")
    print(f"API 文档: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        "web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()

