@echo off
title BatchExport - Standalone Mock Mode

echo ============================================
echo   BatchExport - Mock Test Mode
echo   No DaVinci Resolve required
echo ============================================
echo.

cd /d "%~dp0"

:: Find Python
set "PYTHON="
if exist "C:\Program Files\Blackmagic Design\DaVinci Resolve\python.exe" (
    set "PYTHON=C:\Program Files\Blackmagic Design\DaVinci Resolve\python.exe"
)
if "%PYTHON%"=="" (
    where python >nul 2>&1
    if %ERRORLEVEL%==0 (set "PYTHON=python") else (
        echo [ERROR] Python not found. Install Python or DaVinci Resolve.
        pause
        exit /b 1
    )
)

echo Python: %PYTHON%
echo.

"%PYTHON%" -c "import sys, os; sys.path.insert(0, r'%~dp0'); from batch_export_lib import GetUI; panel = GetUI(None); panel.setWindowTitle('Batch Export (Mock)'); panel.resize(960, 640); panel.show(); from PySide2 import QtWidgets; app = QtWidgets.QApplication.instance(); app and app.exec_()"

pause
