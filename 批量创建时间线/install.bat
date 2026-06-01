@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Batch Timeline Creator - Installer
echo   For DaVinci Resolve Studio 19+
echo ============================================
echo.

:: Detect Resolve installation
set "RESOLVE_EXE=C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
if not exist "%RESOLVE_EXE%" (
    echo [WARN] Resolve.exe not found at default path.
    echo        Will attempt to install script files anyway.
    echo.
)

:: Target path - all users (recommended)
set "TARGET_DIR=%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility"

:: Fallback to current user path
if not exist "%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts" (
    set "TARGET_DIR=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility"
)

echo Target: %TARGET_DIR%
echo.

:: Create target directory if needed
if not exist "%TARGET_DIR%" (
    echo Creating directory: %TARGET_DIR%
    mkdir "%TARGET_DIR%" 2>nul
    if errorlevel 1 (
        echo [ERROR] Cannot create target directory. Run as Administrator.
        pause
        exit /b 1
    )
)

:: Copy script
set "SOURCE=%~dp0BatchTimelineCreator.py"

if not exist "%SOURCE%" (
    echo [ERROR] Source file not found: %SOURCE%
    echo        Make sure BatchTimelineCreator.py is in the same folder as this script.
    pause
    exit /b 1
)

copy /Y "%SOURCE%" "%TARGET_DIR%\BatchTimelineCreator.py"
if errorlevel 1 (
    echo [ERROR] Copy failed.
    pause
    exit /b 1
)

echo [OK] Installed to: %TARGET_DIR%\BatchTimelineCreator.py
echo.
echo ============================================
echo   Usage:
echo   1. Launch DaVinci Resolve Studio
echo   2. Enable: Preferences ^> System ^> General ^> External Scripting = Local
echo   3. Open any project
echo   4. Menu: Workspace ^> Scripts ^> Utility ^> BatchTimelineCreator
echo ============================================
echo.
pause
