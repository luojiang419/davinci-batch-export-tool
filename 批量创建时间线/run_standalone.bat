@echo off
setlocal

echo ============================================
echo   Batch Timeline Creator - Standalone
echo   For DaVinci Resolve Studio 19+
echo ============================================
echo.

:: Environment variables for Resolve scripting API
set "RESOLVE_SCRIPT_API=%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
set "RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"

if not exist "%RESOLVE_SCRIPT_API%" (
    echo [WARN] Resolve Scripting API not found at:
    echo        %RESOLVE_SCRIPT_API%
    echo        If Resolve is installed elsewhere, edit this script to fix the path.
)

:: Add API modules to PYTHONPATH
set "PYTHONPATH=%RESOLVE_SCRIPT_API%\Modules;%PYTHONPATH%"

echo RESOLVE_SCRIPT_API = %RESOLVE_SCRIPT_API%
echo RESOLVE_SCRIPT_LIB  = %RESOLVE_SCRIPT_LIB%
echo.

:: Locate Python
set "PYTHON_EXE="

where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        set "PYTHON_EXE=%%i"
        goto :found_python
    )
)

:: Try common Python install paths
for %%d in (
    "C:\Python312"
    "C:\Python311"
    "C:\Python310"
    "%LOCALAPPDATA%\Programs\Python\Python312"
    "%LOCALAPPDATA%\Programs\Python\Python311"
    "%LOCALAPPDATA%\Programs\Python\Python310"
) do (
    if exist "%%~d\python.exe" (
        set "PYTHON_EXE=%%~d\python.exe"
        goto :found_python
    )
)

echo [ERROR] Python not found. Install Python 3.10 - 3.12 and add to PATH.
pause
exit /b 1

:found_python
echo Python: %PYTHON_EXE%
echo.

:: Run the script
set "SCRIPT=%~dp0BatchTimelineCreator.py"

if not exist "%SCRIPT%" (
    echo [ERROR] Script not found: %SCRIPT%
    pause
    exit /b 1
)

echo Starting Batch Timeline Creator...
echo.
echo NOTE: DaVinci Resolve Studio must be running with a project open.
echo.

"%PYTHON_EXE%" "%SCRIPT%"

if errorlevel 1 (
    echo.
    echo ============================================
    echo   Run failed. Please check:
    echo   1. DaVinci Resolve Studio is running
    echo   2. Preferences ^> System ^> General ^> External Scripting = Local
    echo   3. A project is currently open
    echo ============================================
)

echo.
pause
