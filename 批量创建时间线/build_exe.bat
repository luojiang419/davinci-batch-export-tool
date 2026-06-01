@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Build BatchTimelineCreator.exe
echo   Requires: Python 3.10-3.12 + PyInstaller
echo ============================================
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH.
    echo        Install Python 3.10-3.12 and add to PATH.
    pause
    exit /b 1
)

echo Checking PyInstaller...
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

echo.
echo Building executable...
echo Output will be in: %~dp0dist\
echo.

:: PyInstaller build with spec file or inline args
python -m PyInstaller ^
    --onefile ^
    --console ^
    --name "BatchTimelineCreator" ^
    --exclude-module matplotlib ^
    --exclude-module numpy ^
    --exclude-module pandas ^
    --exclude-module PIL ^
    --exclude-module cv2 ^
    --distpath "%~dp0dist" ^
    --workpath "%~dp0build" ^
    --specpath "%~dp0" ^
    "%~dp0BatchTimelineCreator.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed. See output above for details.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build complete!
echo   EXE location: %~dp0dist\BatchTimelineCreator.exe
echo.
echo   Usage:
echo   1. Launch DaVinci Resolve Studio with a project open
echo   2. Run BatchTimelineCreator.exe
echo   3. If Resolve API is not auto-detected, set:
echo      RESOLVE_SCRIPT_API environment variable
echo ============================================
echo.

:: Cleanup build temp files
if exist "%~dp0build" (
    echo Cleaning build temp files...
    rmdir /s /q "%~dp0build"
)

pause
