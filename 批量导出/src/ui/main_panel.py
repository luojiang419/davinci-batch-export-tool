"""
批量导出 主面板 - 左右分栏布局

左侧: 时间线浏览器 (S2实现)
右侧: 导出设置面板 (S3实现)
"""
from PySide2 import QtWidgets, QtCore

from ..utils.resolve_api import get_api


class BatchExportPanel(QtWidgets.QWidget):
    """批量导出插件主面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api = get_api()
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """初始化UI布局"""
        self.setWindowTitle("批量导出时间线")
        self.setMinimumSize(900, 600)

        # ── 主布局: 左右分栏 ──
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_splitter.setHandleWidth(1)

        # ── 左侧: 时间线浏览器 ──
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)

        left_label = QtWidgets.QLabel("媒体池结构")
        left_label.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px;")

        self._folder_tree = QtWidgets.QTreeWidget()
        self._folder_tree.setHeaderLabels(["时间线", "时长", "帧率"])
        self._folder_tree.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self._folder_tree.setRootIsDecorated(True)

        left_layout.addWidget(left_label)
        left_layout.addWidget(self._folder_tree)

        # ── 右侧: 导出设置 ──
        right_scroll = QtWidgets.QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)

        # 预设选择
        right_layout.addWidget(self._build_preset_bar())

        # 格式设置分组
        right_layout.addWidget(self._build_format_group())

        # 视频设置分组
        right_layout.addWidget(self._build_video_group())

        # 音频设置分组
        right_layout.addWidget(self._build_audio_group())

        # 命名规则分组
        right_layout.addWidget(self._build_naming_group())

        # 输出路径
        right_layout.addWidget(self._build_output_path())

        # 弹性空间
        right_layout.addStretch()

        # 底部按钮
        right_layout.addWidget(self._build_action_bar())

        right_scroll.setWidget(right_widget)

        # 加入分割器
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_scroll)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 3)

        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(main_splitter)

    # ── 各UI区域构建方法 ──

    def _build_preset_bar(self) -> QtWidgets.QWidget:
        """预设选择栏"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QtWidgets.QLabel("预设:"))
        self._preset_combo = QtWidgets.QComboBox()
        self._preset_combo.addItem("自定义")
        self._preset_combo.setMinimumWidth(180)
        layout.addWidget(self._preset_combo)

        self._preset_save_btn = QtWidgets.QPushButton("保存预设")
        self._preset_save_btn.setFixedWidth(80)
        layout.addWidget(self._preset_save_btn)

        self._preset_delete_btn = QtWidgets.QPushButton("删除")
        self._preset_delete_btn.setFixedWidth(50)
        layout.addWidget(self._preset_delete_btn)

        layout.addStretch()
        return widget

    def _build_format_group(self) -> QtWidgets.QGroupBox:
        """导出格式分组"""
        group = QtWidgets.QGroupBox("格式")
        layout = QtWidgets.QVBoxLayout(group)

        # 格式选择
        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(QtWidgets.QLabel("导出格式:"))
        self._format_combo = QtWidgets.QComboBox()
        self._format_combo.addItems(
            [f["name"] for f in self._api.get_render_formats()]
        )
        row1.addWidget(self._format_combo)
        row1.addStretch()
        layout.addLayout(row1)

        # 编码器
        row2 = QtWidgets.QHBoxLayout()
        row2.addWidget(QtWidgets.QLabel("视频编码器:"))
        self._video_codec_combo = QtWidgets.QComboBox()
        self._video_codec_combo.addItems(self._api.get_video_codecs("MP4"))
        row2.addWidget(self._video_codec_combo)

        row2.addWidget(QtWidgets.QLabel("音频编码器:"))
        self._audio_codec_combo = QtWidgets.QComboBox()
        self._audio_codec_combo.addItems(self._api.get_audio_codecs())
        row2.addWidget(self._audio_codec_combo)
        layout.addLayout(row2)

        return group

    def _build_video_group(self) -> QtWidgets.QGroupBox:
        """视频设置分组"""
        group = QtWidgets.QGroupBox("视频")
        layout = QtWidgets.QVBoxLayout(group)

        # 分辨率
        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(QtWidgets.QLabel("分辨率:"))
        self._resolution_combo = QtWidgets.QComboBox()
        self._resolution_combo.addItems(self._api.get_resolutions())
        self._resolution_combo.setMinimumWidth(160)
        row1.addWidget(self._resolution_combo)

        # 帧率
        row1.addWidget(QtWidgets.QLabel("帧率:"))
        self._framerate_combo = QtWidgets.QComboBox()
        self._framerate_combo.addItems(self._api.get_frame_rates())
        self._framerate_combo.setCurrentText("24")
        row1.addWidget(self._framerate_combo)
        row1.addStretch()
        layout.addLayout(row1)

        # 质量
        row2 = QtWidgets.QHBoxLayout()
        row2.addWidget(QtWidgets.QLabel("质量:"))
        self._quality_combo = QtWidgets.QComboBox()
        self._quality_combo.addItems(["自动", "最低", "低", "中", "高", "最高"])
        row2.addWidget(self._quality_combo)

        self._quality_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._quality_slider.setRange(1, 100)
        self._quality_slider.setValue(85)
        self._quality_slider.setFixedWidth(100)
        row2.addWidget(self._quality_slider)

        self._quality_label = QtWidgets.QLabel("85")
        row2.addWidget(self._quality_label)
        row2.addStretch()
        layout.addLayout(row2)

        return group

    def _build_audio_group(self) -> QtWidgets.QGroupBox:
        """音频设置分组"""
        group = QtWidgets.QGroupBox("音频")
        layout = QtWidgets.QVBoxLayout(group)

        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("采样率:"))
        self._sample_rate_combo = QtWidgets.QComboBox()
        self._sample_rate_combo.addItems(self._api.get_sample_rates())
        self._sample_rate_combo.setCurrentText("48000Hz")
        row.addWidget(self._sample_rate_combo)

        row.addWidget(QtWidgets.QLabel("位深:"))
        self._bit_depth_combo = QtWidgets.QComboBox()
        self._bit_depth_combo.addItems(self._api.get_bit_depth())
        row.addWidget(self._bit_depth_combo)
        row.addStretch()
        layout.addLayout(row)

        return group

    def _build_naming_group(self) -> QtWidgets.QGroupBox:
        """命名规则分组"""
        group = QtWidgets.QGroupBox("命名规则")
        layout = QtWidgets.QVBoxLayout(group)

        # 变量插入按钮
        var_row = QtWidgets.QHBoxLayout()
        var_row.addWidget(QtWidgets.QLabel("变量:"))
        variables = [
            ("{timeline}", "时间线名称"),
            ("{date}", "日期"),
            ("{time}", "时间"),
            ("{index}", "序号"),
            ("{project}", "项目名称"),
        ]
        for var_name, var_label in variables:
            btn = QtWidgets.QPushButton(var_name)
            btn.setFixedHeight(22)
            btn.setToolTip(var_label)
            btn.setStyleSheet("font-size: 10px; padding: 2px 6px;")
            var_row.addWidget(btn)
        var_row.addStretch()
        layout.addLayout(var_row)

        # 命名模板输入
        tmpl_row = QtWidgets.QHBoxLayout()
        tmpl_row.addWidget(QtWidgets.QLabel("模板:"))
        self._naming_edit = QtWidgets.QLineEdit("{timeline}_{date}_{index}")
        tmpl_row.addWidget(self._naming_edit)
        layout.addLayout(tmpl_row)

        # 预览
        preview_row = QtWidgets.QHBoxLayout()
        preview_row.addWidget(QtWidgets.QLabel("预览:"))
        self._naming_preview = QtWidgets.QLabel("我的时间线_20260601_01.mp4")
        self._naming_preview.setStyleSheet("color: #888;")
        preview_row.addWidget(self._naming_preview)
        preview_row.addStretch()
        layout.addLayout(preview_row)

        return group

    def _build_output_path(self) -> QtWidgets.QWidget:
        """输出路径选择"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QtWidgets.QLabel("导出到:"))
        self._output_path_edit = QtWidgets.QLineEdit()
        layout.addWidget(self._output_path_edit)

        self._browse_btn = QtWidgets.QPushButton("浏览...")
        self._browse_btn.setFixedWidth(60)
        layout.addWidget(self._browse_btn)

        return widget

    def _build_action_bar(self) -> QtWidgets.QWidget:
        """底部操作栏"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 4, 0, 4)

        self._status_label = QtWidgets.QLabel("就绪")
        layout.addWidget(self._status_label)

        layout.addStretch()

        self._cancel_btn = QtWidgets.QPushButton("取消")
        self._cancel_btn.setFixedWidth(80)
        layout.addWidget(self._cancel_btn)

        self._export_btn = QtWidgets.QPushButton("开始导出")
        self._export_btn.setFixedWidth(100)
        self._export_btn.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; "
            "font-weight: bold; padding: 6px 16px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        layout.addWidget(self._export_btn)

        return widget

    def _connect_signals(self):
        """连接信号槽"""
        self._format_combo.currentTextChanged.connect(self._on_format_changed)
        self._quality_slider.valueChanged.connect(self._on_quality_changed)
        self._browse_btn.clicked.connect(self._on_browse_output)
        self._export_btn.clicked.connect(self._on_start_export)
        self._cancel_btn.clicked.connect(self._on_cancel)

    # ── 信号处理 ──

    def _on_format_changed(self, fmt_name: str):
        """格式切换时更新编码器选项"""
        self._video_codec_combo.clear()
        self._video_codec_combo.addItems(self._api.get_video_codecs(fmt_name))

    def _on_quality_changed(self, value: int):
        self._quality_label.setText(str(value))

    def _on_browse_output(self):
        """选择输出文件夹"""
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择导出文件夹"
        )
        if path:
            self._output_path_edit.setText(path)

    def _on_start_export(self):
        """开始导出 (S5 实现核心逻辑)"""
        selected = self._get_selected_timelines()
        if not selected:
            QtWidgets.QMessageBox.warning(
                self, "提示", "请先选择要导出的时间线"
            )
            return

        output_path = self._output_path_edit.text().strip()
        if not output_path:
            QtWidgets.QMessageBox.warning(
                self, "提示", "请先选择导出文件夹"
            )
            return

        self._status_label.setText(f"准备导出 {len(selected)} 条时间线...")

    def _on_cancel(self):
        self._status_label.setText("已取消")
        if self._api.is_connected:
            self._api.delete_all_render_jobs()

    def _get_selected_timelines(self) -> list:
        """获取用户在树中勾选的时间线 (S2 完善)"""
        selected = []
        root = self._folder_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) == QtCore.Qt.Checked:
                selected.append(item.text(0))
        return selected

    # ── 公开方法 ──

    def refresh_timelines(self):
        """刷新时间线列表 (S2 实现具体逻辑)"""
        self._folder_tree.clear()
        if self._api.is_mock:
            self._populate_mock_timelines()

    def _populate_mock_timelines(self):
        """Mock 数据填充 (开发阶段用)"""
        from ..utils.resolve_api import _MockFolder

        folders = _MockFolder("根目录").GetSubFolderList()
        for folder in folders:
            folder_item = QtWidgets.QTreeWidgetItem([folder.GetName()])
            folder_item.setFlags(
                folder_item.flags() | QtCore.Qt.ItemIsUserCheckable
            )
            folder_item.setCheckState(0, QtCore.Qt.Unchecked)

            for i in range(1, 4):
                child = QtWidgets.QTreeWidgetItem([
                    f"时间线_{folder.GetName()}_{i}",
                    f"0:{i:02d}:00",
                    "24"
                ])
                child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
                child.setCheckState(0, QtCore.Qt.Unchecked)
                folder_item.addChild(child)

            self._folder_tree.addTopLevelItem(folder_item)
            folder_item.setExpanded(True)
