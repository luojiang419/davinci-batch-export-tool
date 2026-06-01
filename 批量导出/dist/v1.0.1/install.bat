@echo off
title BatchExport - Installer

cd /d "%~dp0"

echo ============================================
echo   BatchExport v1.0.1 - Installer
echo   For DaVinci Resolve Studio 19+
echo ============================================
echo.
echo Current dir: %cd%
echo Script dir: %~dp0
echo.

:: Detect Resolve
set "RESOLVE_EXE=C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
if not exist "%RESOLVE_EXE%" (
    echo [WARN] Resolve.exe not found
    echo        Installing files anyway...
    echo.
) else (
    echo [OK] Resolve found at: %RESOLVE_EXE%
    echo.
)

:: Target path
set "TARGET_DIR=%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility"
if not exist "%TARGET_DIR%" (
    set "TARGET_DIR=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility"
)
echo Target: %TARGET_DIR%

:: Create target directory
if not exist "%TARGET_DIR%" (
    echo Creating: %TARGET_DIR%
    mkdir "%TARGET_DIR%" 2>nul
    if errorlevel 1 (
        echo [ERROR] Cannot create target directory.
        echo         Run as Administrator and try again.
        pause
        exit /b 1
    )
)
echo.

:: Source files (relative to this script - it's in install/ folder)
set "SCRIPT_DIR=%~dp0.."
pushd "%SCRIPT_DIR%"
set "SCRIPT_DIR=%cd%"
popd

set "MAIN_SCRIPT=%SCRIPT_DIR%\BatchExport.py"
set "SRC_DIR=%SCRIPT_DIR%\batch_export_lib"

echo Checking source files:
if exist "%MAIN_SCRIPT%" (
    echo   [OK] %MAIN_SCRIPT%
) else (
    echo   [ERROR] Not found: %MAIN_SCRIPT%
    echo   Make sure install.bat is in the install/ folder.
    pause
    exit /b 1
)

if exist "%SRC_DIR%" (
    echo   [OK] %SRC_DIR%
) else (
    echo   [ERROR] Not found: %SRC_DIR%
    pause
    exit /b 1
)
echo.

:: Install
echo [1/2] Installing main script...
copy /Y "%MAIN_SCRIPT%" "%TARGET_DIR%\BatchExport.py"
if errorlevel 1 (
    echo [ERROR] Copy failed. Run as Administrator.
    pause
    exit /b 1
)
echo        -> %TARGET_DIR%\BatchExport.py

echo [2/2] Installing modules...
set "MODULE_TARGET=%TARGET_DIR%\batch_export_lib"
if exist "%MODULE_TARGET%" rmdir /S /Q "%MODULE_TARGET%"
if exist "%TARGET_DIR%\src" rmdir /S /Q "%TARGET_DIR%\src"
if exist "%TARGET_DIR%\BatchExport_src" rmdir /S /Q "%TARGET_DIR%\BatchExport_src"
xcopy "%SRC_DIR%\*" "%MODULE_TARGET%\" /E /I /Y /Q
if errorlevel 1 (
    echo [ERROR] Module copy failed.
    pause
    exit /b 1
)
echo        -> %MODULE_TARGET%

:: Verify
echo.
echo Verification:
if exist "%TARGET_DIR%\BatchExport.py" (echo   [OK] BatchExport.py) else (echo   [FAIL] BatchExport.py)
if exist "%MODULE_TARGET%\__init__.py" (echo   [OK] batch_export_lib\__init__.py) else (echo   [FAIL] __init__.py)
if exist "%MODULE_TARGET%\ui\main_panel.py" (echo   [OK] ui\main_panel.py) else (echo   [FAIL] main_panel.py)
if exist "%MODULE_TARGET%\core\export_engine.py" (echo   [OK] core\export_engine.py) else (echo   [FAIL] export_engine.py)
if exist "%MODULE_TARGET%\utils\resolve_api.py" (echo   [OK] utils\resolve_api.py) else (echo   [FAIL] resolve_api.py)

echo.
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo   To use:
echo   1. Enable: Preferences ^> System ^> General ^> External Scripting = Local
echo   2. Restart DaVinci Resolve
echo   3. Menu: Workspace ^> Scripts ^> Utility ^> BatchExport
echo.

pause
