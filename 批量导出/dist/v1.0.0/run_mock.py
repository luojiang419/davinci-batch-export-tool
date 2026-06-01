"""独立运行入口 - Mock模式，无需达芬奇"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from batch_export_lib import GetUI
from batch_export_lib.utils.qt_compat import QtWidgets

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

panel = GetUI(None)
panel.setWindowTitle("Batch Export (Mock Mode)")
panel.resize(960, 640)
panel.show()

app.exec_()
