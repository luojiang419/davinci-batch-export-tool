@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   批量导出时间线 v1.0.0 - 安装程序
echo   适用于 DaVinci Resolve Studio 19+
echo ============================================
echo.

:: 检测 Resolve 安装
set "RESOLVE_EXE=C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"
if not exist "%RESOLVE_EXE%" (
    echo [WARN] Resolve.exe not found at default path.
    echo        Will attempt to install script files anyway.
    echo.
)

:: 目标路径 - 所有用户(推荐)
set "TARGET_DIR=%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility"

:: 回退到当前用户路径
if not exist "%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts" (
    set "TARGET_DIR=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility"
)

echo Target: %TARGET_DIR%
echo.

:: 创建目标目录
if not exist "%TARGET_DIR%" (
    echo Creating directory: %TARGET_DIR%
    mkdir "%TARGET_DIR%" 2>nul
    if errorlevel 1 (
        echo [ERROR] Cannot create target directory. Run as Administrator.
        pause
        exit /b 1
    )
)

:: 源路径
set "SCRIPT_DIR=%~dp0.."

:: 检查源文件
set "MAIN_SCRIPT=%SCRIPT_DIR%\BatchExport.py"
set "SRC_DIR=%SCRIPT_DIR%\src"

if not exist "%MAIN_SCRIPT%" (
    echo [ERROR] Main script not found: %MAIN_SCRIPT%
    pause
    exit /b 1
)

if not exist "%SRC_DIR%" (
    echo [ERROR] Source directory not found: %SRC_DIR%
    pause
    exit /b 1
)

:: 1. 复制主入口脚本
echo [1/2] Installing main script...
copy /Y "%MAIN_SCRIPT%" "%TARGET_DIR%\BatchExport.py"
if errorlevel 1 (
    echo [ERROR] Failed to copy main script.
    pause
    exit /b 1
)
echo        Installed: %TARGET_DIR%\BatchExport.py

:: 2. 复制模块包
echo [2/2] Installing modules...
set "MODULE_TARGET=%TARGET_DIR%\BatchExport_src"
if exist "%MODULE_TARGET%" rmdir /S /Q "%MODULE_TARGET%"
xcopy "%SRC_DIR%\*" "%MODULE_TARGET%\" /E /I /Y /Q >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy modules.
    pause
    exit /b 1
)
echo        Installed: %MODULE_TARGET%

echo.
echo ============================================
echo   安装完成!
echo ============================================
echo.
echo   使用方法:
echo   1. 启用外部脚本: 偏好设置 ^> 系统 ^> 常规 ^> 外部脚本 = 本地
echo   2. 打开任意项目
echo   3. 菜单: 工作区 ^> 脚本 ^> Utility ^> BatchExport
echo.

pause
