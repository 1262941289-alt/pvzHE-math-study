@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 启动寸止MCP服务器
echo 启动寸止MCP服务器...
python 寸止.py
