# -*- coding: utf-8 -*-
"""极简测试脚本 - 验证达芬奇是否能加载 Utility 目录下的脚本"""
from PySide2 import QtWidgets

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
msg = QtWidgets.QMessageBox()
msg.setWindowTitle("测试")
msg.setText("如果你看到这个弹窗，说明脚本加载正常！\n\n请检查批量导出插件:\n工作区 > 脚本 > Utility > BatchExport")
msg.exec_()
