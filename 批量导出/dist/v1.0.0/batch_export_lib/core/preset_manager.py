"""
预设管理器 - JSON 文件读写、预设增删改查
"""
import json
import os
from datetime import datetime
from typing import List, Optional

from ..core.export_settings_model import ExportPreset, ExportSettings


class PresetManager:
    """预设管理器"""

    def __init__(self, presets_dir: str = None):
        """
        Args:
            presets_dir: 预设文件存储目录，默认为插件目录下的 presets/
        """
        if presets_dir is None:
            presets_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "presets"
            )
        self._dir = presets_dir
        os.makedirs(self._dir, exist_ok=True)
        self._file = os.path.join(self._dir, "export_presets.json")
        self._presets: List[ExportPreset] = []
        self._load()

    # ── 公共 API ──────────────────────────────────────

    def list_presets(self) -> List[ExportPreset]:
        """返回所有预设"""
        return list(self._presets)

    def get_preset_names(self) -> List[str]:
        """返回所有预设名称"""
        return [p.name for p in self._presets]

    def get_preset(self, name: str) -> Optional[ExportPreset]:
        """按名称查找预设"""
        for p in self._presets:
            if p.name == name:
                return p
        return None

    def save_preset(self, name: str, settings: ExportSettings,
                    description: str = "") -> bool:
        """保存预设（同名则覆盖）"""
        # 检查是否已存在
        existing = self.get_preset(name)
        if existing:
            existing.settings = settings
            existing.description = description or existing.description
        else:
            preset = ExportPreset(
                name=name,
                settings=settings,
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                description=description,
            )
            self._presets.append(preset)

        self._save()
        return True

    def delete_preset(self, name: str) -> bool:
        """删除预设"""
        for i, p in enumerate(self._presets):
            if p.name == name:
                self._presets.pop(i)
                self._save()
                return True
        return False

    def load_preset_settings(self, name: str) -> Optional[ExportSettings]:
        """加载预设设置，返回 ExportSettings 或 None"""
        preset = self.get_preset(name)
        if preset:
            return preset.settings
        return None

    # ── 内部方法 ──────────────────────────────────────

    def _load(self):
        """从 JSON 文件加载预设"""
        if not os.path.exists(self._file):
            self._presets = []
            # 创建默认预设
            self._create_defaults()
            return

        try:
            with open(self._file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._presets = [
                ExportPreset.from_dict(item)
                for item in data.get("presets", [])
            ]
        except (json.JSONDecodeError, KeyError, TypeError):
            self._presets = []
            self._create_defaults()

    def _save(self):
        """保存到 JSON 文件"""
        data = {
            "version": "1.0",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "presets": [p.to_dict() for p in self._presets],
        }
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _create_defaults(self):
        """创建内置默认预设"""
        defaults = [
            ExportPreset(
                name="YouTube 1080p",
                settings=ExportSettings(
                    format="MP4", video_codec="H.264",
                    resolution="1920×1080 (Full HD)", frame_rate="30",
                ),
                description="YouTube 1080p 30fps H.264",
            ),
        ]
        self._presets.extend(defaults)
        self._save()
