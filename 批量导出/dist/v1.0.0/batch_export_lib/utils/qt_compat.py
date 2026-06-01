"""Qt 兼容层 - 自动适配 PySide2 (Resolve) 或 PySide6 (独立运行)"""
try:
    from PySide2 import QtWidgets, QtCore, QtGui
    QT_VERSION = 2
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui
    QT_VERSION = 6
