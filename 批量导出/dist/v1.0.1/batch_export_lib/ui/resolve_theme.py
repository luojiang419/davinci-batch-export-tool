"""
达芬奇专业深灰暗黑主题样式表
"""
import sys
from ..utils.qt_compat import QtGui, QT_VERSION


def apply_dark_theme(app):
    """应用达芬奇风格深灰暗黑主题"""
    app.setStyle("Fusion")

    dark_palette = QtGui.QPalette()

    # 基础色板
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#1e1e1e"))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#cccccc"))
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor("#252525"))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#2a2a2a"))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor("#2d2d2d"))
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor("#cccccc"))
    dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor("#cccccc"))
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor("#2d2d2d"))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#cccccc"))
    dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor("#ff4444"))
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor("#4da6ff"))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#2d72b5"))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))

    # 禁用状态
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText,
                          QtGui.QColor("#666666"))
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text,
                          QtGui.QColor("#666666"))
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText,
                          QtGui.QColor("#666666"))
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight,
                          QtGui.QColor("#3a3a3a"))
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText,
                          QtGui.QColor("#888888"))

    app.setPalette(dark_palette)

    # 精调样式
    app.setStyleSheet("""
        QToolTip {
            color: #cccccc;
            background-color: #2d2d2d;
            border: 1px solid #4a4a4a;
            padding: 3px;
        }
        QGroupBox {
            color: #cccccc;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 16px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 2px 8px;
            color: #aaaaaa;
        }
        QComboBox {
            background-color: #2d2d2d;
            color: #cccccc;
            border: 1px solid #4a4a4a;
            border-radius: 3px;
            padding: 3px 8px;
            min-width: 80px;
        }
        QComboBox:hover { border-color: #5a5a5a; }
        QComboBox::drop-down {
            border: none;
            padding-right: 6px;
        }
        QComboBox QAbstractItemView {
            background-color: #2a2a2a;
            color: #cccccc;
            selection-background-color: #2d72b5;
            border: 1px solid #4a4a4a;
        }
        QPushButton {
            background-color: #333333;
            color: #cccccc;
            border: 1px solid #4a4a4a;
            border-radius: 3px;
            padding: 4px 12px;
        }
        QPushButton:hover {
            background-color: #404040;
            border-color: #5a5a5a;
        }
        QPushButton:pressed {
            background-color: #2a2a2a;
        }
        QPushButton:disabled {
            background-color: #252525;
            color: #555555;
            border-color: #333333;
        }
        QLineEdit {
            background-color: #252525;
            color: #cccccc;
            border: 1px solid #4a4a4a;
            border-radius: 3px;
            padding: 3px 6px;
        }
        QLineEdit:focus {
            border-color: #5a8fc9;
        }
        QSpinBox {
            background-color: #2d2d2d;
            color: #cccccc;
            border: 1px solid #4a4a4a;
            border-radius: 3px;
            padding: 3px 6px;
        }
        QSlider::groove:horizontal {
            background: #333333;
            height: 6px;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #5a8fc9;
            width: 14px;
            margin: -4px 0;
            border-radius: 7px;
        }
        QSlider::handle:horizontal:hover {
            background: #6aa0da;
        }
        QSlider::sub-page:horizontal {
            background: #2d72b5;
            border-radius: 3px;
        }
        QTreeWidget {
            background-color: #1e1e1e;
            color: #cccccc;
            border: 1px solid #3a3a3a;
            alternate-background-color: #232323;
            outline: none;
        }
        QTreeWidget::item {
            padding: 3px 4px;
        }
        QTreeWidget::item:selected {
            background-color: #2d72b5;
            color: #ffffff;
        }
        QTreeWidget::item:hover {
            background-color: #333333;
        }
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {
            border-image: none;
        }
        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {
            border-image: none;
        }
        QHeaderView::section {
            background-color: #2a2a2a;
            color: #aaaaaa;
            border: none;
            border-right: 1px solid #3a3a3a;
            border-bottom: 1px solid #3a3a3a;
            padding: 4px 8px;
        }
        QScrollBar:horizontal {
            background: #1a1a1a;
            height: 10px;
        }
        QScrollBar::handle:horizontal {
            background: #444444;
            border-radius: 4px;
            min-width: 30px;
        }
        QScrollBar::handle:horizontal:hover { background: #555555; }
        QScrollBar:vertical {
            background: #1a1a1a;
            width: 10px;
        }
        QScrollBar::handle:vertical {
            background: #444444;
            border-radius: 4px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover { background: #555555; }
        QScrollBar::add-line, QScrollBar::sub-line {
            height: 0px; width: 0px;
        }
        QSplitter::handle {
            background-color: #2a2a2a;
            width: 1px;
        }
        QCheckBox {
            color: #cccccc;
            spacing: 6px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        QCheckBox::indicator:unchecked {
            border: 1px solid #555555;
            background: #2d2d2d;
            border-radius: 2px;
        }
        QCheckBox::indicator:checked {
            border: 1px solid #2d72b5;
            background: #2d72b5;
            border-radius: 2px;
        }
        QLabel {
            color: #cccccc;
        }
        QStatusBar {
            background: #1e1e1e;
            color: #999999;
            border-top: 1px solid #333333;
        }
        QScrollArea {
            border: none;
            background: transparent;
        }
        QMenu {
            background-color: #2a2a2a;
            color: #cccccc;
            border: 1px solid #4a4a4a;
        }
        QMenu::item:selected {
            background-color: #2d72b5;
        }
        QProgressBar {
            background-color: #2d2d2d;
            border: 1px solid #4a4a4a;
            border-radius: 3px;
            text-align: center;
            color: #cccccc;
        }
        QProgressBar::chunk {
            background-color: #2d72b5;
            border-radius: 2px;
        }
    """)
