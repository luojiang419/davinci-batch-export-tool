@echo off
title 批量导出插件 - 安装程序

:: 强制切换到脚本所在目录
cd /d "%~dp0"

echo ============================================
echo   批量导出时间线 v1.0.0 - 安装程序
echo   适用于 DaVinci Resolve Studio 19+
echo ============================================
echo.
echo 当前目录: %cd%
echo 脚本目录: %~dp0
echo.

:: 检测 Resolve 安装
set "RESOLVE_EXE=C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
if not exist "%RESOLVE_EXE%" (
    echo [WARN] Resolve.exe not found at: %RESOLVE_EXE%
    echo        Will attempt to install script files anyway.
    echo.
) else (
    echo [OK] Resolve found.
    echo.
)

:: 目标路径
set "TARGET_DIR=%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility"
if not exist "%TARGET_DIR%" (
    set "TARGET_DIR=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility"
)
echo Target: %TARGET_DIR%

:: 创建目标目录
if not exist "%TARGET_DIR%" (
    echo Creating: %TARGET_DIR%
    mkdir "%TARGET_DIR%" 2>nul
    if errorlevel 1 (
        echo [ERROR] Cannot create directory. Try running as Administrator.
        pause
        exit /b 1
    )
)
echo.

:: 源文件检查 (相对于脚本目录)
set "SCRIPT_DIR=%~dp0.."
pushd "%SCRIPT_DIR%"
set "SCRIPT_DIR=%cd%"
popd

set "MAIN_SCRIPT=%SCRIPT_DIR%\BatchExport.py"
set "SRC_DIR=%SCRIPT_DIR%\batch_export_lib"

echo 源文件检查:
if exist "%MAIN_SCRIPT%" (
    echo   [OK] %MAIN_SCRIPT%
) else (
    echo   [ERROR] Not found: %MAIN_SCRIPT%
    echo   请确保 install\install.bat 在 批量导出\install\ 目录下运行
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

:: 安装
echo [1/2] Installing main script...
copy /Y "%MAIN_SCRIPT%" "%TARGET_DIR%\BatchExport.py"
if errorlevel 1 (
    echo [ERROR] Copy failed. Run as Administrator.
    pause
    exit /b 1
)
echo        Installed: %TARGET_DIR%\BatchExport.py

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
echo        Installed: %MODULE_TARGET%

:: 验证安装
echo.
echo 验证安装:
if exist "%TARGET_DIR%\BatchExport.py" (echo   [OK] BatchExport.py) else (echo   [FAIL] BatchExport.py)
if exist "%MODULE_TARGET%\__init__.py" (echo   [OK] batch_export_lib\__init__.py) else (echo   [FAIL] __init__.py)
if exist "%MODULE_TARGET%\ui\main_panel.py" (echo   [OK] ui\main_panel.py) else (echo   [FAIL] main_panel.py)
if exist "%MODULE_TARGET%\core\export_engine.py" (echo   [OK] core\export_engine.py) else (echo   [FAIL] export_engine.py)
if exist "%MODULE_TARGET%\utils\resolve_api.py" (echo   [OK] utils\resolve_api.py) else (echo   [FAIL] resolve_api.py)

echo.
echo ============================================
echo   安装完成!
echo ============================================
echo.
echo   使用方法:
echo   1. 启用: 偏好设置 ^> 系统 ^> 常规 ^> 外部脚本 = 本地
echo   2. 达芬奇菜单: 工作区 ^> 脚本 ^> Utility ^> BatchExport
echo.

pause
