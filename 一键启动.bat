@echo off
chcp 65001 >nul
title 微盘股指数分析系统 - 一键启动

echo.
echo ========================================
echo   微盘股指数分析系统
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python 已安装

REM 检查端口 5000 是否被占用
netstat -ano | findstr ":5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 后端服务已在运行 (端口 5000)
) else (
    echo [1/3] 启动后端服务...
    start "后端服务" cmd /k "cd /d %~dp0web\backend && python start_backend.py"
    timeout /t 3 /nobreak >nul
)

REM 检查端口 5500 是否被占用
netstat -ano | findstr ":5500" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 前端服务已在运行 (端口 5500)
) else (
    echo [2/3] 启动前端服务...
    start "前端服务" cmd /k "cd /d %~dp0web\frontend && python -m http.server 5500"
    timeout /t 2 /nobreak >nul
)

echo [3/3] 打开浏览器...
timeout /t 5 /nobreak >nul
start "" "http://localhost:5500/web/frontend/index.html"

echo.
echo ========================================
echo ✅ 系统启动完成！
echo ========================================
echo - 后端服务：http://localhost:5000
echo - 前端服务：http://localhost:5500
echo - 访问地址：http://localhost:5500/web/frontend/index.html
echo ========================================
echo.
echo 窗口将在 10 秒后自动关闭...
timeout /t 10 /nobreak >nul
