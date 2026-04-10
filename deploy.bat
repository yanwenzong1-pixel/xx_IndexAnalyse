@echo off
echo ========================================
echo 微盘股指数分析系统 - 部署脚本
echo ========================================
echo.
echo [1/3] 安装依赖...
python -m pip install --upgrade pip
pip install flask requests pandas numpy scipy
if errorlevel 1 (
    echo 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)
echo.
echo [2/3] 验证安装...
python -c "import flask, requests, pandas, numpy, scipy; print('依赖安装成功')"
if errorlevel 1 (
    echo 依赖验证失败
    pause
    exit /b 1
)
echo.
echo [3/3] 启动服务...
cd web\backend
python app.py
pause
