@echo off
chcp 65001 >nul
title 微盘股指数分析系统 - 启动服务

echo ========================================
echo 微盘股指数分析系统
echo ========================================
echo.

echo [1/3] 启动后端服务...
start "后端服务" cmd /k "cd /d %~dp0web\backend && python start_backend.py"

echo [2/3] 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo [3/3] 打开前端页面...
start "" "http://localhost:5500/web/frontend/index.html"

echo.
echo ========================================
echo 系统启动完成！
echo - 后端服务：http://localhost:5000
echo - 前端页面：http://localhost:5500/web/frontend/index.html
echo ========================================
echo.
echo 按任意键退出启动脚本...
pause >nul
