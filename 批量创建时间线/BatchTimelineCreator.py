#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
Batch Timeline Creator for DaVinci Resolve 19+

In-Resolve usage:
  Place in Scripts/Utility/, then run from Workspace > Scripts > Utility

External usage:
  Run run_standalone.bat or use the packaged .exe

Requirements: DaVinci Resolve Studio 19+
"""

import sys
import os

# ── 路径自动检测 ────────────────────────────────────────────────────
def _find_resolve_paths():
    """自动查找 DaVinci Resolve 的安装路径，返回 (script_api_dir, script_lib_dll)"""
    # 先检查环境变量
    api = os.environ.get("RESOLVE_SCRIPT_API", "")
    lib = os.environ.get("RESOLVE_SCRIPT_LIB", "")
    if api and lib and os.path.isdir(api) and os.path.isfile(lib):
        return api, lib

    # 对于已打包为 exe 的运行，DaVinciResolveScript.py 已在 sys.path 中
    # 仅需找到 fusionscript.dll
    if api and os.path.isdir(api):
        # 尝试默认 lib 路径
        default_lib = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
        if os.path.isfile(default_lib):
            return api, default_lib

    # 自动扫描常见安装路径
    program_data = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")

    # 候选 Scripting API 路径
    api_candidates = [
        os.path.join(program_data, r"Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"),
        os.path.join(os.environ.get("APPDATA", ""), r"Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"),
    ]

    # 候选 fusionscript.dll 路径
    lib_candidates = [
        os.path.join(program_files, r"Blackmagic Design\DaVinci Resolve\fusionscript.dll"),
        os.path.join(program_files, r"Blackmagic Design\DaVinci Resolve 19\fusionscript.dll"),
        os.path.join(program_files, r"Blackmagic Design\DaVinci Resolve 20\fusionscript.dll"),
    ]

    found_api = ""
    for path in api_candidates:
        modules_dir = os.path.join(path, "Modules")
        if os.path.isdir(modules_dir):
            found_api = path
            break

    if not found_api:
        # 最后尝试通过注册表查找
        found_api = _find_resolve_via_registry()

    found_lib = ""
    for path in lib_candidates:
        if os.path.isfile(path):
            found_lib = path
            break

    return found_api, found_lib


def _find_resolve_via_registry():
    """通过 Windows 注册表查找 Resolve 安装路径"""
    try:
        import winreg
        for key_path in [
            r"SOFTWARE\Blackmagic Design\DaVinci Resolve",
            r"SOFTWARE\WOW6432Node\Blackmagic Design\DaVinci Resolve",
        ]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    install_dir, _ = winreg.QueryValueEx(key, "InstallPath")
                    if install_dir:
                        # Scripting API 路径总是在 ProgramData，不在安装目录
                        pass
            except (FileNotFoundError, OSError):
                pass
    except Exception:
        pass
    return ""


# ── 延迟连接 ────────────────────────────────────────────────────────
resolve = None
fusion = None
project = None
bmd = None
_last_connect_error = None


def is_running_in_resolve():
    """检测是否在 Resolve 内部运行（Scripts 菜单模式）"""
    return globals().get("resolve") is not None and globals().get("fusion") is not None


def _connect_resolve():
    """连接到 DaVinci Resolve，设置全局 resolve/fusion/project/bmd"""
    global resolve, fusion, project, bmd, _last_connect_error
    _last_connect_error = None

    _g = globals()

    # 模式 1: 从 Resolve Scripts 菜单运行
    r = _g.get("resolve")
    f = _g.get("fusion")
    b = _g.get("bmd")
    if r is not None and f is not None:
        p = r.GetProjectManager().GetCurrentProject()
        if p is None:
            _last_connect_error = "当前没有打开的项目，请先打开或创建一个项目。"
            return False
        resolve, fusion, project, bmd = r, f, p, b
        return True

    # 模式 2: 外部运行 / 打包为 exe
    script_api, script_lib = _find_resolve_paths()
    if not script_api:
        _last_connect_error = (
            "无法找到 DaVinci Resolve Scripting API。\n"
            "请安装 DaVinci Resolve Studio 19+，或设置环境变量 RESOLVE_SCRIPT_API"
        )
        return False

    sys.path.append(os.path.join(script_api, "Modules"))

    try:
        import DaVinciResolveScript as dvr
    except ImportError:
        _last_connect_error = "无法导入 DaVinciResolveScript。\n请确保路径: " + script_api
        return False

    r = dvr.scriptapp("Resolve")
    if r is None:
        _last_connect_error = (
            "无法连接到 DaVinci Resolve。\n"
            "请确保:\n"
            "1. DaVinci Resolve Studio 正在运行\n"
            "2. 已在 Preferences > System > General 中启用 External Scripting = Local"
        )
        return False

    f = r.Fusion()
    try:
        import bmd as _bmd
        b = _bmd
    except ImportError:
        b = None

    p = r.GetProjectManager().GetCurrentProject()
    if p is None:
        _last_connect_error = "当前没有打开的项目，请先打开或创建一个项目。"
        return False

    resolve, fusion, project, bmd = r, f, p, b
    return True


def _get_resolve_scripts_dir():
    """返回 Resolve Scripts/Utility 目录路径"""
    program_data = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
    appdata = os.environ.get("APPDATA", "")
    candidates = [
        os.path.join(program_data, r"Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility"),
        os.path.join(appdata, r"Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility"),
    ]
    for d in candidates:
        if os.path.isdir(d):
            return d
    # 返回默认路径（可能不存在，后续创建）
    return candidates[0]


def auto_install_script():
    """首次运行时自动将脚本安装到 Resolve 目录（仅 exe 模式有效）"""
    if not getattr(sys, 'frozen', False):
        return False  # 非 exe 模式，跳过

    target_dir = _get_resolve_scripts_dir()
    target = os.path.join(target_dir, "BatchTimelineCreator.py")

    if os.path.isfile(target):
        return True  # 已安装

    # 从 PyInstaller 打包数据中读取 .py 文件
    try:
        meipass = sys._MEIPASS
        source = os.path.join(meipass, "BatchTimelineCreator.py")
        if os.path.isfile(source):
            os.makedirs(target_dir, exist_ok=True)
            import shutil
            shutil.copy2(source, target)
            return True
    except Exception:
        pass
    return False


# ── 预设数据 ─────────────────────────────────────────────────────────
RESOLUTION_PRESETS = [
    ("3840x2160 (UHD 4K)", "3840", "2160"),
    ("1920x1080 (Full HD)", "1920", "1080"),
    ("1280x720 (HD)", "1280", "720"),
    ("4096x2160 (DCI 4K)", "4096", "2160"),
    ("2048x1080 (DCI 2K)", "2048", "1080"),
    ("3840x3840 (方形 UHD)", "3840", "3840"),
    ("1080x1920 (竖屏 Full HD)", "1080", "1920"),
    ("1080x1080 (方形 HD)", "1080", "1080"),
    ("自定义", "", ""),
]

FRAME_RATES = [
    "23.976",
    "24",
    "25",
    "29.97",
    "29.97 DF",
    "30",
    "50",
    "59.94",
    "59.94 DF",
    "60",
    "120",
]


# ── 辅助函数 ──────────────────────────────────────────────────────────
def get_project_defaults():
    """读取当前项目设置作为 UI 默认值"""
    try:
        w = project.GetSetting("timelineResolutionWidth")
        h = project.GetSetting("timelineResolutionHeight")
        fps = project.GetSetting("timelineFrameRate")
        return {
            "width": w or "1920",
            "height": h or "1080",
            "framerate": fps or "24",
        }
    except Exception:
        return {"width": "1920", "height": "1080", "framerate": "24"}


def save_project_color_settings():
    """保存项目色彩管理设置，用于规避 useCustomSettings bug"""
    keys = [
        "colorSpaceTimeline",
        "colorSpaceTimelineGamma",
        "colorSpaceOutput",
        "colorSpaceOutputGamma",
        "isAutoColorManage",
        "separateColorSpaceAndGamma",
        "useCATransform",
        "disableFusionToneMapping",
        "rcmPresetMode",
        "timelineOutputResMismatchBehavior",
        "timelineInputResMismatchBehavior",
        "videoMonitorFormat",
    ]
    saved = {}
    for key in keys:
        try:
            saved[key] = project.GetSetting(key)
        except Exception:
            saved[key] = ""
    return saved


def apply_color_settings_to_timeline(timeline, saved):
    """将保存的色彩设置恢复到指定的时间线"""
    for key, val in saved.items():
        if val and val != "":
            try:
                timeline.SetSetting(key, val)
            except Exception:
                pass


def create_timelines(names, width, height, framerate, create_folders, callback_progress):
    """批量创建时间线，通过 callback_progress 报告进展"""
    mediapool = project.GetMediaPool()
    root = mediapool.GetRootFolder()

    saved_color = save_project_color_settings()

    created = 0
    errors = []
    total = len(names)

    for i, name in enumerate(names):
        name = name.strip()
        if not name:
            continue

        try:
            timeline = mediapool.CreateEmptyTimeline(name)
            if timeline is None:
                errors.append(f'"{name}": CreateEmptyTimeline 返回 None')
                callback_progress(i + 1, total, name, False, "创建失败")
                continue

            # 启用自定义设置（会触发 useCustomSettings bug，后续恢复）
            try:
                timeline.SetSetting("useCustomSettings", "1")
            except Exception:
                pass

            # 恢复项目色彩设置
            apply_color_settings_to_timeline(timeline, saved_color)

            # 应用用户指定的分辨率和帧率
            if width:
                timeline.SetSetting("timelineResolutionWidth", str(width))
            if height:
                timeline.SetSetting("timelineResolutionHeight", str(height))
            if framerate:
                timeline.SetSetting("timelineFrameRate", str(framerate))

            # 在媒体池中创建对应文件夹
            if create_folders:
                try:
                    mediapool.AddSubFolder(root, name)
                except Exception as e:
                    errors.append(f'"{name}": 时间线已创建, 但文件夹创建失败 ({e})')

            created += 1
            callback_progress(i + 1, total, name, True, "创建成功")

        except Exception as e:
            errors.append(f'"{name}": {e}')
            callback_progress(i + 1, total, name, False, str(e))

    return created, errors


# ── UI: UIManager 版本 (Resolve 内部运行) ─────────────────────────────
def build_ui_uimanager(defaults):
    """使用 Resolve 内置 UIManager 构建 UI"""
    ui = fusion.UIManager()
    dispatcher = bmd.UIDispatcher(ui)

    res_preset_names = [p[0] for p in RESOLUTION_PRESETS]

    default_res_index = 1
    for idx, p in enumerate(RESOLUTION_PRESETS):
        if p[1] == defaults["width"] and p[2] == defaults["height"]:
            default_res_index = idx
            break

    default_fps_index = 1
    try:
        default_fps_index = FRAME_RATES.index(defaults["framerate"])
    except ValueError:
        for idx, fps in enumerate(FRAME_RATES):
            if fps.replace(" DF", "") == defaults["framerate"]:
                default_fps_index = idx
                break

    left_panel = ui.VGroup([
        ui.Label({"Text": "时间线名称（每行一个）:", "Weight": 0}),
        ui.TextEdit({
            "ID": "nameInput", "Text": "", "Weight": 1,
            "MinimumSize": [280, 300],
        }),
        ui.VGap(4),
        ui.Label({"ID": "countLabel", "Text": "将创建 0 个时间线", "Weight": 0}),
    ])

    right_panel = ui.VGroup([
        ui.Label({"Text": "时间线配置:", "Weight": 0}),
        ui.VGap(8),
        ui.Label({"Text": "预设分辨率", "Weight": 0}),
        ui.ComboBox({
            "ID": "resPreset", "ItemText": res_preset_names,
            "CurrentIndex": default_res_index,
        }),
        ui.VGap(4),
        ui.HGroup([
            ui.Label({"Text": "宽", "Weight": 0}),
            ui.LineEdit({"ID": "widthInput", "Text": defaults["width"], "MinimumSize": [60, 0]}),
            ui.Label({"Text": "x 高", "Weight": 0}),
            ui.LineEdit({"ID": "heightInput", "Text": defaults["height"], "MinimumSize": [60, 0]}),
        ]),
        ui.VGap(12),
        ui.Label({"Text": "帧率 (fps)", "Weight": 0}),
        ui.ComboBox({
            "ID": "framerateInput", "ItemText": FRAME_RATES,
            "CurrentIndex": default_fps_index, "Editable": True,
        }),
        ui.VGap(16),
        ui.CheckBox({"ID": "createFoldersCheck", "Text": "在媒体池中创建对应文件夹", "Checked": False}),
    ])

    button_bar = ui.HGroup([
        ui.Button({"ID": "createBtn", "Text": "创建时间线", "MinimumSize": [120, 36]}),
        ui.Button({"ID": "cancelBtn", "Text": "取消", "MinimumSize": [80, 36]}),
    ])

    status_bar = ui.Label({"ID": "statusLabel", "Text": "状态: 就绪", "WordWrap": True})

    main_layout = ui.VGroup([
        ui.HGroup([left_panel, right_panel]),
        ui.VGap(8), button_bar, ui.VGap(4), status_bar,
    ])

    win = dispatcher.AddWindow(
        {"ID": "mainWin", "WindowTitle": "批量创建时间线 - Batch Timeline Creator",
         "MinimumSize": [720, 460]},
        main_layout,
    )

    # ── 事件处理 ──
    def on_name_changed(ev):
        text = win.Find("nameInput").Text
        names = [n for n in text.strip().split("\n") if n.strip()]
        win.Find("countLabel").Text = f"将创建 {len(names)} 个时间线"

    def on_res_preset_changed(ev):
        idx = win.Find("resPreset").CurrentIndex
        if 0 <= idx < len(RESOLUTION_PRESETS) - 1:
            _, w, h = RESOLUTION_PRESETS[idx]
            win.Find("widthInput").Text = w
            win.Find("heightInput").Text = h
            win.Find("widthInput").ReadOnly = True
            win.Find("heightInput").ReadOnly = True
        else:
            win.Find("widthInput").ReadOnly = False
            win.Find("heightInput").ReadOnly = False

    def do_create():
        text = win.Find("nameInput").Text
        names = [n for n in text.strip().split("\n") if n.strip()]
        if not names:
            win.Find("statusLabel").Text = "错误: 请输入至少一个时间线名称"
            return
        width = win.Find("widthInput").Text.strip()
        height = win.Find("heightInput").Text.strip()
        framerate = win.Find("framerateInput").CurrentText.strip()
        create_folders = win.Find("createFoldersCheck").Checked

        if width and not width.isdigit():
            win.Find("statusLabel").Text = "错误: 分辨率宽度必须为正整数"; return
        if height and not height.isdigit():
            win.Find("statusLabel").Text = "错误: 分辨率高度必须为正整数"; return

        seen, dupes = set(), set()
        for n in names:
            lower = n.lower()
            if lower in seen: dupes.add(n)
            seen.add(lower)
        if dupes:
            win.Find("statusLabel").Text = f"错误: 存在重复名称: {', '.join(list(dupes)[:3])}"; return

        win.Find("createBtn").Enabled = False
        win.Find("cancelBtn").Enabled = False
        win.Find("statusLabel").Text = f"正在创建 {len(names)} 个时间线..."

        def progress(current, total, name, success, msg):
            if success:
                win.Find("statusLabel").Text = f"进度: [{current}/{total}] 已创建 \"{name}\""
            else:
                win.Find("statusLabel").Text = f"进度: [{current}/{total}] \"{name}\" 失败: {msg}"

        created, errors = create_timelines(names, width, height, framerate, create_folders, progress)

        win.Find("createBtn").Enabled = True
        win.Find("cancelBtn").Enabled = True

        if errors:
            err_msg = "; ".join(errors[:3])
            if len(errors) > 3:
                err_msg += f" ... 及其他 {len(errors) - 3} 个错误"
            win.Find("statusLabel").Text = f"完成: {created}/{len(names)} 成功。错误: {err_msg}"
        else:
            extra = " (含媒体池文件夹)" if create_folders else ""
            win.Find("statusLabel").Text = f"完成: 成功创建 {created} 个时间线！{extra}"

    def on_create_clicked(ev):
        do_create()

    def on_cancel(ev):
        dispatcher.ExitLoop()

    def on_close(ev):
        dispatcher.ExitLoop()

    win.On.nameInput.TextChanged = on_name_changed
    win.On.resPreset.CurrentIndexChanged = on_res_preset_changed
    win.On.createBtn.Clicked = on_create_clicked
    win.On.cancelBtn.Clicked = on_cancel
    win.On.mainWin.Close = on_close

    if default_res_index < len(RESOLUTION_PRESETS) - 1:
        win.Find("widthInput").ReadOnly = True
        win.Find("heightInput").ReadOnly = True

    win.Show()
    dispatcher.RunLoop()
    win.Hide()


# ── 达芬奇暗黑主题配色 ─────────────────────────────────────────────
# Resolve-style dark color palette
DR_BG        = "#1e1e1e"   # 主背景
DR_PANEL     = "#2a2a2a"   # 面板
DR_INPUT     = "#333333"   # 输入框
DR_TEXT      = "#cccccc"   # 主文字
DR_TEXT_DIM  = "#888888"   # 次要文字
DR_ACCENT    = "#4a90d9"   # 强调蓝
DR_BORDER    = "#444444"   # 边框
DR_BTN_HOVER = "#3a3a3a"   # 按钮悬停
DR_SELECT    = "#1a3a5c"   # 选中
DR_SUCCESS   = "#4caf50"   # 成功绿
DR_ERROR     = "#e04f4f"   # 错误红


def _apply_dark_theme(root, style):
    """配置 ttk 暗黑主题样式"""
    style.theme_use("clam")

    # 通用字体
    font_default = ("Segoe UI", 9)
    font_small   = ("Segoe UI", 8)
    font_bold    = ("Segoe UI", 9, "bold")
    font_mono    = ("Consolas", 10)

    style.configure(".", font=font_default,
                    background=DR_BG, foreground=DR_TEXT,
                    fieldbackground=DR_INPUT, borderwidth=1)

    # Frame
    style.configure("TFrame", background=DR_BG)
    style.configure("Dark.TFrame", background=DR_PANEL)

    # LabelFrame
    style.configure("TLabelframe", background=DR_BG, foreground=DR_TEXT,
                    bordercolor=DR_BORDER, relief="flat")
    style.configure("TLabelframe.Label", background=DR_BG, foreground=DR_TEXT,
                    font=font_bold)

    # Label
    style.configure("TLabel", background=DR_BG, foreground=DR_TEXT)
    style.configure("Dim.TLabel", foreground=DR_TEXT_DIM, font=font_small)
    style.configure("Status.TLabel", foreground=DR_TEXT_DIM, font=font_small,
                    background=DR_BG)

    # Button - accent
    style.configure("Accent.TButton", font=font_default,
                    background=DR_ACCENT, foreground="#ffffff",
                    borderwidth=0, relief="flat",
                    padding=(16, 6))
    style.map("Accent.TButton",
              background=[("active", "#5aa0e9"), ("disabled", DR_BORDER)],
              foreground=[("disabled", DR_TEXT_DIM)])

    # Button - normal
    style.configure("TButton", font=font_default,
                    background=DR_PANEL, foreground=DR_TEXT,
                    borderwidth=0, relief="flat",
                    padding=(12, 6))
    style.map("TButton",
              background=[("active", DR_BTN_HOVER)],
              relief=[("pressed", "flat")])

    # Entry
    style.configure("TEntry", fieldbackground=DR_INPUT, foreground=DR_TEXT,
                    background=DR_INPUT, borderwidth=1,
                    bordercolor=DR_BORDER, relief="solid",
                    padding=(6, 4))
    style.map("TEntry",
              fieldbackground=[("readonly", "#2a2a2a")],
              bordercolor=[("focus", DR_ACCENT)])

    # Combobox
    style.configure("TCombobox", fieldbackground=DR_INPUT,
                    background=DR_INPUT, foreground=DR_TEXT,
                    arrowcolor=DR_TEXT, borderwidth=1,
                    bordercolor=DR_BORDER, relief="solid",
                    padding=(6, 4))
    style.map("TCombobox",
              fieldbackground=[("readonly", DR_INPUT)],
              bordercolor=[("focus", DR_ACCENT), ("hover", DR_ACCENT)],
              background=[("active", DR_ACCENT)])

    # Combobox dropdown list
    root.option_add("*TCombobox*Listbox.background", DR_INPUT)
    root.option_add("*TCombobox*Listbox.foreground", DR_TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", DR_SELECT)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
    root.option_add("*TCombobox*Listbox.font", font_default)

    # Checkbutton
    style.configure("TCheckbutton", background=DR_BG, foreground=DR_TEXT)
    style.map("TCheckbutton",
              background=[("active", DR_BG)],
              foreground=[("active", "#ffffff")])

    # Scrollbar
    style.configure("TScrollbar", background=DR_PANEL,
                    troughcolor=DR_BG, borderwidth=0,
                    arrowcolor=DR_TEXT, relief="flat")
    style.map("TScrollbar",
              background=[("active", DR_BORDER)])

    # PanedWindow
    style.configure("TPanedwindow", background=DR_BG, borderwidth=0)

    return font_mono


# ── UI: Tkinter 版本 (外部 / .exe 运行) ────────────────────────────────
def build_ui_tkinter(defaults, connected=False, install_status=False):
    """使用 Tkinter 构建达芬奇暗黑风格 UI"""
    import tkinter as tk
    from tkinter import ttk, messagebox

    root = tk.Tk()
    root.title("Batch Timeline Creator - DaVinci Resolve")
    root.geometry("780x560")
    root.minsize(680, 460)
    root.resizable(True, True)
    root.configure(bg=DR_BG)

    # 应用暗黑主题
    style = ttk.Style()
    font_mono = _apply_dark_theme(root, style)

    # ── 连接状态栏 ──
    status_frame = tk.Frame(root, bg=DR_PANEL)
    status_frame.pack(fill="x")

    conn_indicator = tk.Frame(status_frame, width=10, height=10,
                              bg=DR_SUCCESS if connected else DR_ERROR)
    conn_indicator.pack(side="left", padx=(12, 6), pady=8)

    conn_text = ("已连接 DaVinci Resolve" if connected
                 else "未连接 - 请启动 DaVinci Resolve Studio 并打开项目")
    conn_label = tk.Label(status_frame, text=conn_text,
                          bg=DR_PANEL, fg=DR_SUCCESS if connected else DR_ERROR,
                          font=("Segoe UI", 9))
    conn_label.pack(side="left", pady=8)

    reconnect_btn = ttk.Button(status_frame, text="重新连接", style="TButton",
                               command=lambda: do_reconnect())
    reconnect_btn.pack(side="right", padx=12, pady=6)
    if connected:
        reconnect_btn.pack_forget()

    install_msg = ""
    if getattr(sys, 'frozen', False):
        install_msg = ("脚本已安装到 Resolve 菜单" if install_status
                       else "未能安装到 Resolve 菜单（可手动运行 install.bat）")
    install_note = tk.Label(status_frame, text=install_msg,
                            bg=DR_PANEL, fg=DR_TEXT_DIM,
                            font=("Segoe UI", 7))
    if install_msg:
        install_note.pack(side="right", padx=12, pady=6)

    # 分割线
    tk.Frame(root, height=1, bg=DR_BORDER).pack(fill="x")

    # ── 主容器 ──
    main_frame = tk.Frame(root, bg=DR_BG)
    main_frame.pack(fill="both", expand=True, padx=10, pady=(10, 8))

    # ── 左右分栏 ──
    paned = ttk.PanedWindow(main_frame, orient="horizontal")
    paned.pack(fill="both", expand=True)

    # ════════════════════════════════════════════════════════════
    # 左侧面板 — 时间线名称输入
    # ════════════════════════════════════════════════════════════
    left_frame = ttk.LabelFrame(paned, text=" 时间线名称（每行一个） ", padding="10")
    paned.add(left_frame, weight=1)

    name_text = tk.Text(
        left_frame, width=32, height=16,
        font=font_mono, undo=True, wrap="none",
        bg=DR_INPUT, fg=DR_TEXT,
        insertbackground=DR_TEXT,
        selectbackground=DR_SELECT,
        selectforeground="#ffffff",
        relief="flat", borderwidth=1,
        padx=8, pady=8,
        highlightthickness=1,
        highlightcolor=DR_ACCENT,
        highlightbackground=DR_BORDER,
    )
    name_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=name_text.yview)
    name_text.configure(yscrollcommand=name_scrollbar.set)
    name_text.pack(side="left", fill="both", expand=True)
    name_scrollbar.pack(side="right", fill="y")

    count_var = tk.StringVar(value="将创建 0 个时间线")
    count_label = tk.Label(left_frame, textvariable=count_var,
                           bg=DR_BG, fg=DR_TEXT_DIM, font=("Segoe UI", 8),
                           anchor="w")
    count_label.pack(fill="x", pady=(6, 0))

    def update_count(*_args):
        text = name_text.get("1.0", "end-1c")
        names = [n for n in text.strip().split("\n") if n.strip()]
        count_var.set(f"将创建 {len(names)} 个时间线")

    name_text.bind("<KeyRelease>", update_count)

    # ════════════════════════════════════════════════════════════
    # 右侧面板 — 配置
    # ════════════════════════════════════════════════════════════
    right_frame = ttk.LabelFrame(paned, text=" 时间线配置 ", padding="10")
    paned.add(right_frame, weight=0)

    tk.Label(right_frame, text="预设分辨率", bg=DR_BG, fg=DR_TEXT,
             font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
    res_var = tk.StringVar()
    res_combo = ttk.Combobox(right_frame, textvariable=res_var,
                             state="readonly", width=26)
    res_combo["values"] = [p[0] for p in RESOLUTION_PRESETS]
    res_combo.pack(fill="x")

    wh_frame = tk.Frame(right_frame, bg=DR_BG)
    wh_frame.pack(fill="x", pady=(8, 0))
    tk.Label(wh_frame, text="宽", bg=DR_BG, fg=DR_TEXT).pack(side="left")
    width_var = tk.StringVar(value=defaults["width"])
    width_entry = ttk.Entry(wh_frame, textvariable=width_var, width=7)
    width_entry.pack(side="left", padx=(6, 10))
    tk.Label(wh_frame, text="x  高", bg=DR_BG, fg=DR_TEXT).pack(side="left")
    height_var = tk.StringVar(value=defaults["height"])
    height_entry = ttk.Entry(wh_frame, textvariable=height_var, width=7)
    height_entry.pack(side="left", padx=(6, 0))

    def on_res_combo_changed(*_args):
        idx = res_combo.current()
        if 0 <= idx < len(RESOLUTION_PRESETS) - 1:
            _, w, h = RESOLUTION_PRESETS[idx]
            width_var.set(w); height_var.set(h)
            width_entry.configure(state="readonly")
            height_entry.configure(state="readonly")
        else:
            width_entry.configure(state="normal")
            height_entry.configure(state="normal")

    res_combo.bind("<<ComboboxSelected>>", on_res_combo_changed)

    tk.Label(right_frame, text="帧率 (fps)", bg=DR_BG, fg=DR_TEXT,
             font=("Segoe UI", 9)).pack(anchor="w", pady=(14, 4))
    fps_var = tk.StringVar()
    fps_combo = ttk.Combobox(right_frame, textvariable=fps_var, width=26)
    fps_combo["values"] = FRAME_RATES
    fps_combo.pack(fill="x")

    sep = tk.Frame(right_frame, height=1, bg=DR_BORDER)
    sep.pack(fill="x", pady=(16, 12))

    folder_var = tk.BooleanVar(value=False)
    folder_check = ttk.Checkbutton(
        right_frame, text="在媒体池中创建对应文件夹",
        variable=folder_var,
    )
    folder_check.pack(anchor="w")
    tk.Label(right_frame,
             text="勾选后按时间线名称在媒体池根目录下\n创建对应素材文件夹",
             bg=DR_BG, fg=DR_TEXT_DIM, font=("Segoe UI", 7),
             justify="left").pack(anchor="w", pady=(4, 0))

    # ── 默认选中项 ──
    default_res_idx = 1
    for idx, p in enumerate(RESOLUTION_PRESETS):
        if p[1] == defaults["width"] and p[2] == defaults["height"]:
            default_res_idx = idx; break
    res_combo.current(default_res_idx)
    if default_res_idx < len(RESOLUTION_PRESETS) - 1:
        width_entry.configure(state="readonly")
        height_entry.configure(state="readonly")

    default_fps_idx = 1
    try:
        default_fps_idx = FRAME_RATES.index(defaults["framerate"])
    except ValueError:
        for idx, fps in enumerate(FRAME_RATES):
            if fps.replace(" DF", "") == defaults["framerate"]:
                default_fps_idx = idx; break
    fps_combo.current(default_fps_idx)

    # ════════════════════════════════════════════════════════════
    # 底部 — 按钮 & 状态栏
    # ════════════════════════════════════════════════════════════
    bottom_frame = tk.Frame(main_frame, bg=DR_BG)
    bottom_frame.pack(fill="x", pady=(10, 0))

    tk.Frame(bottom_frame, height=1, bg=DR_BORDER).pack(fill="x", pady=(0, 8))

    btn_frame = tk.Frame(bottom_frame, bg=DR_BG)
    btn_frame.pack(fill="x")

    status_var = tk.StringVar(
        value="状态: 就绪" if connected else "请先连接 DaVinci Resolve"
    )
    tk.Label(btn_frame, textvariable=status_var, bg=DR_BG, fg=DR_TEXT_DIM,
             font=("Segoe UI", 8), anchor="w").pack(side="left", fill="x", expand=True)

    # ── Reconnect logic ──
    def do_reconnect():
        nonlocal connected
        ok = _connect_resolve()
        if ok:
            connected = True
            conn_indicator.configure(bg=DR_SUCCESS)
            conn_label.configure(text="已连接 DaVinci Resolve", fg=DR_SUCCESS)
            reconnect_btn.pack_forget()
            create_btn.configure(state="normal")
            status_var.set("状态: 就绪")
            # Refresh defaults from project
            try:
                d = get_project_defaults()
                width_var.set(d["width"]); height_var.set(d["height"])
                fps_val = d["framerate"]
                for i, f in enumerate(FRAME_RATES):
                    if f.replace(" DF", "") == fps_val:
                        fps_combo.current(i); break
            except Exception:
                pass
        else:
            conn_indicator.configure(bg=DR_ERROR)
            err = _last_connect_error or "连接失败"
            conn_label.configure(text=err.split("\n")[0], fg=DR_ERROR)
            status_var.set('连接失败: ' + err.split('\n')[0])

    def do_create():
        if not connected:
            status_var.set("错误: 未连接 DaVinci Resolve，请点击 [重新连接]")
            return
        text = name_text.get("1.0", "end-1c")
        names = [n for n in text.strip().split("\n") if n.strip()]
        if not names:
            status_var.set("错误: 请输入至少一个时间线名称"); return
        w = width_var.get().strip()
        h = height_var.get().strip()
        fps = fps_var.get().strip()
        create_folders = folder_var.get()
        if w and not w.isdigit():
            status_var.set("错误: 分辨率宽度必须为正整数"); return
        if h and not h.isdigit():
            status_var.set("错误: 分辨率高度必须为正整数"); return
        seen, dupes = set(), set()
        for n in names:
            lower = n.lower()
            if lower in seen: dupes.add(n)
            seen.add(lower)
        if dupes:
            status_var.set(f"错误: 存在重复名称: {', '.join(list(dupes)[:3])}"); return

        create_btn.configure(state="disabled")
        cancel_btn.configure(state="disabled")
        status_var.set(f"正在创建 {len(names)} 个时间线...")
        root.update()

        def progress(current, total, name, success, msg):
            status_var.set(
                f"[{current}/{total}] {'OK' if success else 'FAIL'}: {name}"
                + (f" - {msg}" if not success else "")
            )
            root.update()

        created, errors = create_timelines(names, w, h, fps, create_folders, progress)

        create_btn.configure(state="normal")
        cancel_btn.configure(state="normal")

        if errors:
            err_detail = "\n".join(errors[:5])
            if len(errors) > 5:
                err_detail += f"\n... 及其他 {len(errors) - 5} 个错误"
            status_var.set(f"完成: {created}/{len(names)} 成功，{len(errors)} 个失败")
            messagebox.showwarning("创建完成（有错误）",
                                   f"成功: {created}/{len(names)}\n\n错误:\n{err_detail}")
        else:
            extra = " (含媒体池文件夹)" if create_folders else ""
            status_var.set(f"完成: 成功创建 {created} 个时间线！{extra}")

    cancel_btn = ttk.Button(btn_frame, text="退出", command=root.destroy)
    cancel_btn.pack(side="right", padx=(8, 0))

    create_btn = ttk.Button(btn_frame, text="创建时间线", style="Accent.TButton",
                            command=do_create)
    if not connected:
        create_btn.configure(state="disabled")
        status_var.set("请先启动 DaVinci Resolve 并打开项目，点击 [重新连接]")
    create_btn.pack(side="right")

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


# ── UI 选择入口 ──────────────────────────────────────────────────────
def build_ui():
    """自动选择可用的 UI 后端"""
    # 检查是否在 Resolve 内部运行
    if is_running_in_resolve():
        try:
            _connect_resolve()
            defaults = get_project_defaults() if project else {"width": "1920", "height": "1080", "framerate": "24"}
            build_ui_uimanager(defaults)
            return
        except Exception:
            pass

    # exe/外部模式: 先尝试自动安装
    installed = auto_install_script()

    # 尝试连接
    connected = _connect_resolve()
    defaults = get_project_defaults() if project else {"width": "1920", "height": "1080", "framerate": "24"}

    # 使用 Tkinter UI
    build_ui_tkinter(defaults, connected=connected,
                     install_status=installed)


# ── 入口 ──
if __name__ == "__main__":
    build_ui()
