@echo off
chcp 65001 >nul
echo ============================================================
echo   微盘股指数分析系统 - 启动后端服务
echo ============================================================
echo.
echo 正在启动后端服务...
echo.
cd /d "%~dp0web\backend"
python start_backend.py
pause
