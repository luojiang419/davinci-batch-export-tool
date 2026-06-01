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
        echo [ERROR] Python not found.
        pause
        exit /b 1
    )
)

echo Python: %PYTHON%
echo Running: %~dp0run_mock.py
echo.

"%PYTHON%" "%~dp0run_mock.py"

pause
