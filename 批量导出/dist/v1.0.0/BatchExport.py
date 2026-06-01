#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BatchExport - DaVinci Resolve 19+ Fusion Script

Install: Fusion/Scripts/Utility
Usage: Workspace > Scripts > Utility > BatchExport
"""
import sys
import os
import traceback
import datetime

# ── Crash log ───────────────────────────────────────────────────────
_LOG_FILE = os.path.join(os.environ.get("TEMP", "."), "BatchExport_crash.log")


def _log(msg: str):
    try:
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {msg}\n")
    except Exception:
        pass


def _show_error(msg: str):
    _log(f"ERROR: {msg}")
    try:
        try:
            from PySide2 import QtWidgets
        except ImportError:
            from PySide6 import QtWidgets
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QMessageBox.critical(None, "BatchExport Error", msg)
    except Exception as e:
        _log(f"Failed to show error dialog: {e}")
        print(f"ERROR: {msg}")


def _get_script_dir():
    file_path = globals().get("__file__")
    if file_path:
        return os.path.dirname(os.path.abspath(file_path))

    argv0 = sys.argv[0] if sys.argv and sys.argv[0] else ""
    if argv0:
        return os.path.dirname(os.path.abspath(argv0))

    return os.getcwd()


# ── Resolve API ─────────────────────────────────────────────────────
def _find_resolve_module():
    env_path = os.environ.get("RESOLVE_SCRIPT_API", "")
    if env_path and os.path.isdir(os.path.join(env_path, "Modules")):
        return env_path
    for base in [
        os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"),
                     r"Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"),
        os.path.join(os.environ.get("APPDATA", ""),
                     r"Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"),
    ]:
        if os.path.isdir(os.path.join(base, "Modules")):
            return base
    return None


def _get_resolve():
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
    try:
        import fusionscript as fs
        resolve = fs.scriptapp("Resolve")
        if resolve is not None:
            return resolve
    except ImportError:
        pass
    return None


# ── Main ─────────────────────────────────────────────────────────────
def main():
    _log("=== BatchExport started ===")

    # Resolve may execute scripts without defining __file__.
    script_dir = _get_script_dir()
    _log(f"Script dir: {script_dir}")
    _log(f"sys.path: {sys.path[:3]}")
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    # Import plugin
    try:
        from batch_export_lib import GetUI
        _log("Import OK")
    except Exception as e:
        _log(f"Import failed: {traceback.format_exc()}")
        _show_error(
            "Failed to load plugin modules.\n\n"
            f"Check log at: {_LOG_FILE}\n\n"
            f"Error: {str(e)}"
        )
        return

    # Connect to Resolve
    resolve = _get_resolve()
    if resolve is None:
        _log("Cannot connect to Resolve")
        _show_error(
            "Cannot connect to DaVinci Resolve.\n\n"
            "Make sure:\n"
            "1. Resolve is running\n"
            "2. A project is open\n"
            "3. Preferences > System > General > External Scripting = Local"
        )
        return
    _log("Connected to Resolve OK")

    # Create UI
    try:
        panel = GetUI(resolve)
        panel.setWindowTitle("Batch Export Timelines")
        panel.resize(960, 640)
        panel.show()
        _log("Panel shown OK")
        return panel
    except Exception as e:
        _log(f"Panel failed: {traceback.format_exc()}")
        _show_error(f"Failed to load panel:\n\n{str(e)}")
        return


# ── Entry ────────────────────────────────────────────────────────────
try:
    _panel = main()
except Exception as e:
    _log(f"Top-level crash: {traceback.format_exc()}")
    _show_error(f"Unexpected error:\n\n{str(e)}")
