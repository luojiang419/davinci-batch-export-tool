@echo off
chcp 65001 >nul
title 批量导出插件 - 安装程序

echo ============================================
echo   批量导出时间线插件 v1.0.0 - 安装程序
echo   适用于 DaVinci Resolve 19+
echo ============================================
echo.

REM 目标安装路径
set "PLUGIN_DIR=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Workflow Integration Plugins\BatchExport"

REM 源路径 (脚本所在目录)
set "SRC_DIR=%~dp0..\src"

echo 目标路径: %PLUGIN_DIR%
echo 源路径:   %SRC_DIR%
echo.

REM 检查目标目录
if not exist "%APPDATA%\Blackmagic Design\DaVinci Resolve\Support" (
    echo [错误] 未检测到达芬奇安装目录，请确保已安装 DaVinci Resolve 19+
    pause
    exit /b 1
)

REM 创建插件目录
if not exist "%PLUGIN_DIR%" mkdir "%PLUGIN_DIR%"

REM 复制文件
echo 正在复制插件文件...
xcopy "%SRC_DIR%\*" "%PLUGIN_DIR%\" /E /I /Y /Q >nul

if %ERRORLEVEL% NEQ 0 (
    echo [错误] 文件复制失败!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   安装完成!
echo ============================================
echo.
echo 请重启 DaVinci Resolve，
echo 在菜单中点击 "工作区" - "Workflow Integrations" - "批量导出时间线"
echo.

pause
