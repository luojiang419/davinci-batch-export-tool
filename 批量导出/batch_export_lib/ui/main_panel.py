"""
批量导出 主面板 - 左右分栏布局

左侧: 时间线浏览器 (S2实现)
右侧: 导出设置面板 (S3实现)
"""
from PySide2 import QtWidgets, QtCore

from ..utils.resolve_api import get_api
from ..core.export_settings_model import ExportSettings
from ..core.naming_engine import get_naming_engine
from ..core.export_engine import ExportEngine
from ..core.preset_manager import PresetManager


class BatchExportPanel(QtWidgets.QWidget):
    """批量导出插件主面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api = get_api()
        self._preset_mgr = PresetManager()
        self._init_ui()
        self._connect_signals()
        self._load_presets()

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

        # 分辨率 + 帧率
        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(QtWidgets.QLabel("分辨率:"))
        self._resolution_combo = QtWidgets.QComboBox()
        self._resolution_combo.addItems(self._api.get_resolutions())
        self._resolution_combo.setMinimumWidth(160)
        row1.addWidget(self._resolution_combo)

        row1.addWidget(QtWidgets.QLabel("帧率:"))
        self._framerate_combo = QtWidgets.QComboBox()
        self._framerate_combo.addItems(self._api.get_frame_rates())
        self._framerate_combo.setCurrentText("24")
        row1.addWidget(self._framerate_combo)
        row1.addStretch()
        layout.addLayout(row1)

        # 自定义分辨率 (默认隐藏)
        self._custom_res_widget = QtWidgets.QWidget()
        custom_layout = QtWidgets.QHBoxLayout(self._custom_res_widget)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.addWidget(QtWidgets.QLabel("自定义宽×高:"))
        self._custom_width_edit = QtWidgets.QLineEdit("1920")
        self._custom_width_edit.setFixedWidth(60)
        self._custom_width_edit.setValidator(QtWidgets.QIntValidator(1, 99999))
        custom_layout.addWidget(self._custom_width_edit)
        custom_layout.addWidget(QtWidgets.QLabel("×"))
        self._custom_height_edit = QtWidgets.QLineEdit("1080")
        self._custom_height_edit.setFixedWidth(60)
        self._custom_height_edit.setValidator(QtWidgets.QIntValidator(1, 99999))
        custom_layout.addWidget(self._custom_height_edit)
        custom_layout.addStretch()
        self._custom_res_widget.setVisible(False)
        layout.addWidget(self._custom_res_widget)

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

        # 编码配置行
        row3 = QtWidgets.QHBoxLayout()
        row3.addWidget(QtWidgets.QLabel("编码档次:"))
        self._encoding_profile_combo = QtWidgets.QComboBox()
        self._encoding_profile_combo.addItems(["Auto", "Baseline", "Main", "High"])
        row3.addWidget(self._encoding_profile_combo)

        row3.addWidget(QtWidgets.QLabel("关键帧间隔:"))
        self._keyframe_spin = QtWidgets.QSpinBox()
        self._keyframe_spin.setRange(0, 300)
        self._keyframe_spin.setValue(0)
        self._keyframe_spin.setSuffix(" 帧")
        self._keyframe_spin.setToolTip("0 = 自动")
        row3.addWidget(self._keyframe_spin)
        row3.addStretch()
        layout.addLayout(row3)

        # 高级选项行
        row4 = QtWidgets.QHBoxLayout()
        row4.addWidget(QtWidgets.QLabel("数据级别:"))
        self._data_levels_combo = QtWidgets.QComboBox()
        self._data_levels_combo.addItems(["Auto", "Video", "Full"])
        row4.addWidget(self._data_levels_combo)

        row4.addWidget(QtWidgets.QLabel("色彩空间:"))
        self._color_space_combo = QtWidgets.QComboBox()
        self._color_space_combo.addItems([
            "Same as timeline",
            "Rec.709",
            "Rec.2020",
            "Rec.2100 PQ",
            "Rec.2100 HLG",
            "P3-D65",
            "sRGB",
        ])
        self._color_space_combo.setMinimumWidth(110)
        row4.addWidget(self._color_space_combo)
        row4.addStretch()
        layout.addLayout(row4)

        # 复选框行
        row5 = QtWidgets.QHBoxLayout()
        self._alpha_check = QtWidgets.QCheckBox("导出Alpha通道")
        row5.addWidget(self._alpha_check)
        self._bypass_check = QtWidgets.QCheckBox("可能时跳过重新编码")
        row5.addWidget(self._bypass_check)
        row5.addStretch()
        layout.addLayout(row5)

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

        row.addWidget(QtWidgets.QLabel("比特率:"))
        self._audio_bitrate_combo = QtWidgets.QComboBox()
        self._audio_bitrate_combo.addItems([
            "128 kbps", "192 kbps", "256 kbps", "320 kbps"
        ])
        self._audio_bitrate_combo.setCurrentText("192 kbps")
        row.addWidget(self._audio_bitrate_combo)
        row.addStretch()
        layout.addLayout(row)

        return group

    def _build_naming_group(self) -> QtWidgets.QGroupBox:
        """命名规则分组"""
        self._naming_engine = get_naming_engine()

        group = QtWidgets.QGroupBox("命名规则")
        layout = QtWidgets.QVBoxLayout(group)

        # 变量插入按钮
        var_row = QtWidgets.QHBoxLayout()
        var_row.addWidget(QtWidgets.QLabel("变量:"))
        for var_name, var_label in self._naming_engine.get_variables().items():
            btn = QtWidgets.QPushButton(var_name)
            btn.setFixedHeight(22)
            btn.setToolTip(var_label)
            btn.setStyleSheet("font-size: 10px; padding: 2px 6px;")
            btn.clicked.connect(
                lambda checked, v=var_name: self._insert_variable(v)
            )
            var_row.addWidget(btn)
        var_row.addStretch()
        layout.addLayout(var_row)

        # 命名模板输入
        tmpl_row = QtWidgets.QHBoxLayout()
        tmpl_row.addWidget(QtWidgets.QLabel("模板:"))
        self._naming_edit = QtWidgets.QLineEdit("{timeline}_{date}_{index}")
        self._naming_edit.textChanged.connect(self._update_naming_preview)
        tmpl_row.addWidget(self._naming_edit)
        layout.addLayout(tmpl_row)

        # 预览
        preview_row = QtWidgets.QHBoxLayout()
        preview_row.addWidget(QtWidgets.QLabel("预览:"))
        self._naming_preview = QtWidgets.QLabel()
        self._naming_preview.setStyleSheet("color: #888; font-style: italic;")
        preview_row.addWidget(self._naming_preview)
        preview_row.addStretch()
        layout.addLayout(preview_row)

        # 初始化预览
        self._update_naming_preview()

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
        self._resolution_combo.currentTextChanged.connect(self._on_resolution_changed)
        self._quality_slider.valueChanged.connect(self._on_quality_changed)
        self._browse_btn.clicked.connect(self._on_browse_output)
        self._export_btn.clicked.connect(self._on_start_export)
        self._cancel_btn.clicked.connect(self._on_cancel)
        self._folder_tree.itemChanged.connect(self._on_tree_item_changed)
        self._preset_combo.currentTextChanged.connect(self._on_preset_selected)
        self._preset_save_btn.clicked.connect(self._on_save_preset)
        self._preset_delete_btn.clicked.connect(self._on_delete_preset)

    # ── 信号处理 ──

    def _on_format_changed(self, fmt_name: str):
        """格式切换时更新编码器选项"""
        self._video_codec_combo.clear()
        self._video_codec_combo.addItems(self._api.get_video_codecs(fmt_name))

    def _on_resolution_changed(self, res_text: str):
        """分辨率切换 - 显示/隐藏自定义宽高输入"""
        self._custom_res_widget.setVisible(res_text == "自定义")

    def _on_quality_changed(self, value: int):
        self._quality_label.setText(str(value))

    def _insert_variable(self, var: str):
        """在光标位置插入变量"""
        cursor = self._naming_edit.cursorPosition()
        text = self._naming_edit.text()
        new_text = text[:cursor] + var + text[cursor:]
        self._naming_edit.setText(new_text)
        self._naming_edit.setCursorPosition(cursor + len(var))

    def _update_naming_preview(self):
        """更新命名预览"""
        template = self._naming_edit.text().strip() or "{timeline}"
        fmt = self._format_combo.currentText()
        codec = self._video_codec_combo.currentText()
        preview = self._naming_engine.generate_preview(
            template,
            timeline_name="示例时间线",
            format=fmt,
            codec=codec,
        )
        ext = ExportSettings(format=fmt).file_extension
        self._naming_preview.setText(f"{preview}{ext}")

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
        """开始导出"""
        selected = self._get_selected_timelines()
        if not selected:
            QtWidgets.QMessageBox.warning(
                self, "提示", "请先选择要导出的时间线"
            )
            return

        settings = self.collect_settings()
        if not settings.output_path:
            QtWidgets.QMessageBox.warning(
                self, "提示", "请先选择导出文件夹"
            )
            return

        # 禁用导出按钮防止重复点击
        self._export_btn.setEnabled(False)
        self._export_btn.setText("导出中...")
        self._cancel_btn.setEnabled(True)

        # 创建导出引擎
        engine = ExportEngine()
        jobs = engine.create_jobs(selected, settings)

        names = [j.output_filename for j in jobs[:3]]
        self._status_label.setText(
            f"导出 {len(jobs)} 个文件到 {settings.output_path}: "
            f"{', '.join(names)}"
            f"{'...' if len(jobs) > 3 else ''}"
        )

        # 执行导出
        success = engine.execute(
            settings,
            progress_callback=self._on_export_progress,
            log_callback=self._on_export_log,
        )

        # 恢复UI
        self._export_btn.setEnabled(True)
        self._export_btn.setText("开始导出")
        self._cancel_btn.setEnabled(False)

        status = engine.get_status()
        if success:
            self._status_label.setText(
                f"导出完成: {status['completed']} 个文件已保存"
            )
            QtWidgets.QMessageBox.information(
                self, "导出完成",
                f"成功导出 {status['completed']} 条时间线到:\n{settings.output_path}"
            )
        else:
            self._status_label.setText(
                f"导出结束: {status['completed']} 成功, {status['failed']} 失败"
            )

    def _on_export_progress(self, current: int, total: int, name: str):
        """导出进度回调"""
        self._status_label.setText(
            f"正在导出 [{current}/{total}]: {name}"
        )

    def _on_export_log(self, message: str):
        """导出日志回调"""
        self._status_label.setText(message)

    def _on_cancel(self):
        self._status_label.setText("已取消")
        if self._api.is_connected:
            self._api.delete_all_render_jobs()

    def _on_preset_selected(self, name: str):
        """预设选择 - 加载预设设置到UI"""
        if not name or name == "自定义":
            return
        settings = self._preset_mgr.load_preset_settings(name)
        if settings:
            self.apply_settings(settings)

    def _on_save_preset(self):
        """保存当前设置为预设"""
        name, ok = QtWidgets.QInputDialog.getText(
            self, "保存预设", "预设名称:"
        )
        if ok and name.strip():
            self._preset_mgr.save_preset(name.strip(), self.collect_settings())
            self._load_presets()
            idx = self._preset_combo.findText(name.strip())
            if idx >= 0:
                self._preset_combo.setCurrentIndex(idx)
            self._status_label.setText(f"预设已保存: {name.strip()}")

    def _on_delete_preset(self):
        """删除选中的预设"""
        name = self._preset_combo.currentText()
        if name == "自定义":
            return
        reply = QtWidgets.QMessageBox.question(
            self, "确认删除", f"确定要删除预设 \"{name}\" 吗？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self._preset_mgr.delete_preset(name)
            self._load_presets()

    def _load_presets(self):
        """加载预设列表到下拉框"""
        self._preset_combo.blockSignals(True)
        self._preset_combo.clear()
        self._preset_combo.addItem("自定义")
        for name in self._preset_mgr.get_preset_names():
            self._preset_combo.addItem(name)
        self._preset_combo.setCurrentIndex(0)
        self._preset_combo.blockSignals(False)

    def apply_settings(self, settings: ExportSettings):
        """将 ExportSettings 应用到UI控件"""
        # 格式
        idx = self._format_combo.findText(settings.format)
        if idx >= 0:
            self._format_combo.setCurrentIndex(idx)

        # 视频编码器
        idx = self._video_codec_combo.findText(settings.video_codec)
        if idx >= 0:
            self._video_codec_combo.setCurrentIndex(idx)

        # 音频编码器
        idx = self._audio_codec_combo.findText(settings.audio_codec)
        if idx >= 0:
            self._audio_codec_combo.setCurrentIndex(idx)

        # 分辨率
        idx = self._resolution_combo.findText(settings.resolution)
        if idx >= 0:
            self._resolution_combo.setCurrentIndex(idx)
        self._custom_width_edit.setText(str(settings.custom_width))
        self._custom_height_edit.setText(str(settings.custom_height))

        # 帧率
        idx = self._framerate_combo.findText(settings.frame_rate)
        if idx >= 0:
            self._framerate_combo.setCurrentIndex(idx)

        # 质量
        self._quality_slider.setValue(
            settings.quality if settings.quality > 0 else 85
        )
        quality_idx = 0 if settings.quality < 0 else 1
        if quality_idx < self._quality_combo.count():
            self._quality_combo.setCurrentIndex(quality_idx)

        # 高级视频
        idx = self._data_levels_combo.findText(settings.data_levels)
        if idx >= 0:
            self._data_levels_combo.setCurrentIndex(idx)
        idx = self._color_space_combo.findText(settings.color_space_tag)
        if idx >= 0:
            self._color_space_combo.setCurrentIndex(idx)
        self._alpha_check.setChecked(settings.alpha_channel)
        self._bypass_check.setChecked(settings.bypass_reencode)
        self._keyframe_spin.setValue(settings.keyframe_interval)
        idx = self._encoding_profile_combo.findText(settings.encoding_profile)
        if idx >= 0:
            self._encoding_profile_combo.setCurrentIndex(idx)

        # 音频
        idx = self._sample_rate_combo.findText(settings.sample_rate)
        if idx >= 0:
            self._sample_rate_combo.setCurrentIndex(idx)
        idx = self._bit_depth_combo.findText(settings.bit_depth)
        if idx >= 0:
            self._bit_depth_combo.setCurrentIndex(idx)
        idx = self._audio_bitrate_combo.findText(settings.audio_bitrate)
        if idx >= 0:
            self._audio_bitrate_combo.setCurrentIndex(idx)

        # 命名
        self._naming_edit.setText(settings.naming_template)

        # 输出路径
        self._output_path_edit.setText(settings.output_path)

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

    def collect_settings(self) -> ExportSettings:
        """收集当前UI中所有导出设置，返回结构化数据"""
        quality_text = self._quality_combo.currentText()
        quality_value = -1 if quality_text == "自动" else self._quality_slider.value()

        custom_w = int(self._custom_width_edit.text()) if self._custom_width_edit.text() else 1920
        custom_h = int(self._custom_height_edit.text()) if self._custom_height_edit.text() else 1080

        return ExportSettings(
            format=self._format_combo.currentText(),
            video_codec=self._video_codec_combo.currentText(),
            audio_codec=self._audio_codec_combo.currentText(),
            resolution=self._resolution_combo.currentText(),
            custom_width=custom_w,
            custom_height=custom_h,
            frame_rate=self._framerate_combo.currentText(),
            quality=quality_value,
            data_levels=self._data_levels_combo.currentText(),
            color_space_tag=self._color_space_combo.currentText(),
            alpha_channel=self._alpha_check.isChecked(),
            bypass_reencode=self._bypass_check.isChecked(),
            keyframe_interval=self._keyframe_spin.value(),
            encoding_profile=self._encoding_profile_combo.currentText(),
            sample_rate=self._sample_rate_combo.currentText(),
            bit_depth=self._bit_depth_combo.currentText(),
            audio_bitrate=self._audio_bitrate_combo.currentText(),
            naming_template=self._naming_edit.text().strip(),
            output_path=self._output_path_edit.text().strip(),
        )

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
