#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Minimal test - verify script execution in Resolve
"""
import sys
import os
import traceback

log_path = os.path.join(os.environ.get("TEMP", ""), "batch_test_log.txt")

try:
    with open(log_path, "w") as f:
        f.write("Step 1: Script executed\n")

        # Add Utility dir to path
        me = os.path.dirname(os.path.abspath(__file__))
        if me not in sys.path:
            sys.path.insert(0, me)
        f.write(f"Step 2: path={me}\n")
        f.write(f"Step 3: sys.path[0]={sys.path[0]}\n")

        # Try importing our lib
        f.write("Step 4: importing batch_export_lib...\n")
        from batch_export_lib import GetUI
        f.write("Step 5: import OK\n")

        # Try getting Resolve
        env_path = os.environ.get("RESOLVE_SCRIPT_API", "")
        if env_path and env_path not in sys.path:
            sys.path.insert(0, env_path)
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
        f.write(f"Step 6: resolve={'OK' if resolve else 'NONE'}\n")

        if resolve:
            from PySide2 import QtWidgets
            panel = GetUI(resolve)
            panel.setWindowTitle("BatchExport")
            panel.resize(960, 640)
            panel.show()
            f.write("Step 7: panel shown\n")

        f.write("ALL OK\n")
except Exception as e:
    with open(log_path, "a") as f:
        f.write(f"ERROR: {e}\n{traceback.format_exc()}\n")
