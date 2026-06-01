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
        self._folder_tree.itemChanged.connect(self._on_tree_item_changed)

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

    def _on_tree_item_changed(self, item, column):
        """文件夹勾选联动: 勾选/取消文件夹时同步所有子孙时间线"""
        if column != 0:
            return
        self._folder_tree.blockSignals(True)
        is_folder = item.data(0, QtCore.Qt.UserRole) == "folder"
        state = item.checkState(0)
        if is_folder:
            self._set_children_check(item, state)
        # 如果取消勾选子项, 更新父文件夹为部分选中或取消
        self._update_parent_check(item.parent())
        self._folder_tree.blockSignals(False)

    def _set_children_check(self, parent, state):
        """递归设置所有子孙项的勾选状态"""
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.flags() & QtCore.Qt.ItemIsUserCheckable:
                child.setCheckState(0, state)
            self._set_children_check(child, state)

    def _update_parent_check(self, parent):
        """根据子项状态更新父项的勾选状态"""
        if parent is None or parent is self._folder_tree.invisibleRootItem():
            return
        checked = 0
        total = 0
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.flags() & QtCore.Qt.ItemIsUserCheckable:
                total += 1
                if child.checkState(0) == QtCore.Qt.Checked:
                    checked += 1
        if total == 0:
            parent.setCheckState(0, QtCore.Qt.Unchecked)
        elif checked == total:
            parent.setCheckState(0, QtCore.Qt.Checked)
        elif checked == 0:
            parent.setCheckState(0, QtCore.Qt.Unchecked)
        else:
            parent.setCheckState(0, QtCore.Qt.PartiallyChecked)
        self._update_parent_check(parent.parent())

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

        names = [s["name"] for s in selected]
        self._status_label.setText(
            f"准备导出 {len(selected)} 条时间线: {', '.join(names[:3])}"
            f"{'...' if len(names) > 3 else ''}"
        )

    def _on_cancel(self):
        self._status_label.setText("已取消")
        if self._api.is_connected:
            self._api.delete_all_render_jobs()

    def _get_selected_timelines(self) -> list:
        """递归遍历树，获取所有勾选的时间线节点 (名称, 父文件夹名)"""
        selected = []
        self._collect_checked(self._folder_tree.invisibleRootItem(), selected)
        return selected

    def _collect_checked(self, parent_item, result: list):
        """递归收集勾选的时间线"""
        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            # 时间线项：列数为3 (名称/时长/帧率) 且有勾选框
            if item.columnCount() == 3 and item.checkState(0) == QtCore.Qt.Checked:
                folder_name = ""
                p = item.parent()
                if p and p is not self._folder_tree.invisibleRootItem():
                    folder_name = p.text(0)
                result.append({
                    "name": item.text(0),
                    "duration": item.text(1),
                    "fps": item.text(2),
                    "folder": folder_name,
                })
            # 递归处理子项
            self._collect_checked(item, result)

    # ── 公开方法 ──

    def refresh_timelines(self):
        """扫描媒体池并刷新时间线树"""
        self._folder_tree.clear()

        from ..core.timeline_scanner import scan_timelines

        root_node = scan_timelines()
        self._populate_tree(self._folder_tree.invisibleRootItem(), root_node)
        self._status_label.setText(
            f"已加载 {root_node.total_timeline_count} 条时间线"
        )

    def _populate_tree(self, parent_item, folder_node):
        """将 FolderNode 树递归填充到 QTreeWidget"""
        for subfolder in folder_node.subfolders:
            folder_item = QtWidgets.QTreeWidgetItem([subfolder.name])
            folder_item.setFlags(
                folder_item.flags() | QtCore.Qt.ItemIsUserCheckable
            )
            folder_item.setCheckState(0, QtCore.Qt.Unchecked)
            folder_item.setData(0, QtCore.Qt.UserRole, "folder")

            # 递归填充子文件夹
            self._populate_tree(folder_item, subfolder)

            # 填充时间线
            for tl in subfolder.timelines:
                tl_item = QtWidgets.QTreeWidgetItem([
                    tl.name, tl.duration, tl.fps
                ])
                tl_item.setFlags(
                    tl_item.flags() | QtCore.Qt.ItemIsUserCheckable
                )
                tl_item.setCheckState(0, QtCore.Qt.Unchecked)
                tl_item.setData(0, QtCore.Qt.UserRole, "timeline")
                folder_item.addChild(tl_item)

            parent_item.addChild(folder_item)
            folder_item.setExpanded(True)

        # 根层级的时间线 (不属于任何子文件夹)
        for tl in folder_node.timelines:
            tl_item = QtWidgets.QTreeWidgetItem([
                tl.name, tl.duration, tl.fps
            ])
            tl_item.setFlags(
                tl_item.flags() | QtCore.Qt.ItemIsUserCheckable
            )
            tl_item.setCheckState(0, QtCore.Qt.Unchecked)
            tl_item.setData(0, QtCore.Qt.UserRole, "timeline")
            parent_item.addChild(tl_item)
