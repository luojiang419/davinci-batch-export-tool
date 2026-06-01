@echo off
chcp 65001 >nul
title 批量导出时间线 - 独立运行 (Mock模式)

echo ============================================
echo   批量导出时间线 - Mock 测试模式
echo   此模式不需要 DaVinci Resolve 运行
echo   使用 Mock 数据验证 UI 和功能
echo ============================================
echo.

cd /d "%~dp0"

:: 查找 Python
set "PYTHON="
if exist "C:\Program Files\Blackmagic Design\DaVinci Resolve\python.exe" (
    set "PYTHON=C:\Program Files\Blackmagic Design\DaVinci Resolve\python.exe"
)
if "%PYTHON%"=="" (
    where python >nul 2>&1
    if %ERRORLEVEL%==0 (set "PYTHON=python") else (
        echo [ERROR] Python not found.
        pause
        exit /b 1
    )
)

echo Using: %PYTHON%
echo.

:: 本地目录使用 src/ 包名; 安装后使用 BatchExport_src/
"%PYTHON%" -c "import sys, os; sys.path.insert(0, r'%~dp0'); from src import GetUI; panel = GetUI(None); panel.setWindowTitle('批量导出时间线 (Mock)'); panel.resize(960, 640); panel.show(); from PySide2 import QtWidgets; app = QtWidgets.QApplication.instance(); app and app.exec_()"

pause
