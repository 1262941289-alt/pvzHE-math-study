@echo off
chcp 65001 >nul
echo 🚀 Cursor MCP寸止工具配置助手
echo.

REM 检查Cursor是否运行
tasklist /FI "IMAGENAME eq Cursor.exe" 2>NUL | find /I /N "Cursor.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ 检测到Cursor正在运行
) else (
    echo ⚠️  Cursor未运行，建议先启动Cursor
)

echo.
echo 📋 配置步骤：
echo.
echo 1️⃣  在Cursor中按 Ctrl+Shift+P
echo 2️⃣  输入 "Preferences: Open Settings (JSON)"
echo 3️⃣  将以下配置添加到settings.json中：
echo.
echo {
echo   "mcp.servers": {
echo     "寸止": {
echo       "command": "python",
echo       "args": ["寸止.py"],
echo       "cwd": "%CD%",
echo       "env": {
echo         "PYTHONPATH": "%CD%",
echo         "PYTHONIOENCODING": "utf-8"
echo       }
echo     }
echo   },
echo   "mcp.client": {
echo     "timeout": 30000,
echo     "retries": 3,
echo     "logLevel": "info",
echo     "autoReconnect": true
echo   },
echo   "mcp.enabled": true,
echo   "mcp.autoStart": true
echo }
echo.
echo 4️⃣  保存设置并重启Cursor
echo 5️⃣  按 Ctrl+Shift+P 搜索 "MCP" 验证功能
echo.
echo 📖 详细说明请查看: Cursor-MCP配置指导.md
echo.
pause
