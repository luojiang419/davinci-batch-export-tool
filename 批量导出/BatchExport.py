#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
批量导出时间线 - DaVinci Resolve 19+ Fusion Script

安装: 放置到 Fusion\Scripts\Utility\ 目录
使用: DaVinci Resolve > 工作区 > 脚本 > Utility > BatchExport

依赖: DaVinci Resolve Studio 19+
"""
import sys
import os


# ── Resolve API 路径检测 ──────────────────────────────────────────
def _find_resolve_module():
    """定位 DaVinciResolveScript 模块"""
    # 环境变量优先
    env_path = os.environ.get("RESOLVE_SCRIPT_API", "")
    if env_path and os.path.isdir(env_path):
        modules_dir = os.path.join(env_path, "Modules")
        if os.path.isdir(modules_dir):
            return env_path

    # 扫描常见安装路径
    candidates = [
        os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"),
                     r"Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"),
        os.path.join(os.environ.get("APPDATA", ""),
                     r"Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"),
    ]
    for path in candidates:
        if os.path.isdir(os.path.join(path, "Modules")):
            return path
    return None


def _get_resolve():
    """获取 Resolve 实例"""
    api_path = _find_resolve_module()
    if api_path and api_path not in sys.path:
        sys.path.insert(0, api_path)

    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
        if resolve is not None:
            return resolve
    except ImportError:
        pass

    # 尝试 Fusion 内置方式
    try:
        import fusionscript as fscript
        resolve = fscript.scriptapp("Resolve")
        if resolve is not None:
            return resolve
    except ImportError:
        pass

    print("错误: 无法连接 DaVinci Resolve，请确认 Resolve 正在运行")
    return None


# ── 入口 ───────────────────────────────────────────────────────────
def main():
    resolve = _get_resolve()
    if resolve is None:
        # 显示错误对话框
        from PySide2 import QtWidgets
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        QtWidgets.QMessageBox.critical(
            None, "错误",
            "无法连接到 DaVinci Resolve。\n请确认:\n"
            "1. DaVinci Resolve 正在运行\n"
            "2. 已打开一个项目\n"
            "3. 偏好设置 > 系统 > 常规 > 外部脚本 = 本地"
        )
        return

    # 确保 src/ 包在路径中
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    # 导入插件模块（兼容安装名 BatchExport_src 和本地名 src）
    try:
        from BatchExport_src import GetUI
    except ImportError:
        from src import GetUI

    # 获取面板并显示
    panel = GetUI(resolve)
    panel.setWindowTitle("批量导出时间线")
    panel.resize(960, 640)
    panel.show()

    # 保持窗口运行(Resolve 环境下由 Resolve 托管事件循环)
    return panel


# 支持直接运行
if __name__ == "__main__":
    _panel = main()
