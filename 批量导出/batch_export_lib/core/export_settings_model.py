"""
导出设置数据模型 - 结构化保存所有导出参数
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExportSettings:
    """单次批量导出的完整设置"""

    # 格式
    format: str = "MP4"
    video_codec: str = "H.264"
    audio_codec: str = "AAC"

    # 视频
    resolution: str = "1920×1080 (Full HD)"
    custom_width: int = 1920
    custom_height: int = 1080
    frame_rate: str = "24"
    quality: int = 85  # 1-100 或 "自动"时用-1

    # 高级视频
    data_levels: str = "Auto"       # Auto / Video / Full
    color_space_tag: str = "Same as timeline"
    color_space_gamma: str = "Same as timeline"
    bypass_reencode: bool = False
    alpha_channel: bool = False
    keyframe_interval: int = 0      # 0 = 自动

    # 高级编码
    encoding_profile: str = "Auto"  # Auto / High / Main / Baseline
    multi_pass: str = "off"         # off / first / all
    pixel_aspect: str = "Square"

    # 音频
    sample_rate: str = "48000Hz"
    bit_depth: str = "16-bit"
    audio_bitrate: str = "192 kbps"
    audio_channels: str = "Same as timeline"

    # 命名
    naming_template: str = "{timeline}_{date}_{index}"

    # 输出
    output_path: str = ""

    # 文件名设置
    use_unique_filenames: bool = True

    @property
    def width(self) -> int:
        if self.resolution == "自定义":
            return self.custom_width
        try:
            w = self.resolution.split("×")[0].strip()
            return int(w)
        except (IndexError, ValueError):
            return 1920

    @property
    def height(self) -> int:
        if self.resolution == "自定义":
            return self.custom_height
        try:
            h_part = self.resolution.split("×")[1]
            h = h_part.split("(")[0].strip().split()[0]
            return int(h)
        except (IndexError, ValueError):
            return 1080

    @property
    def file_extension(self) -> str:
        ext_map = {
            "QuickTime": ".mov",
            "MP4": ".mp4",
            "AVI": ".avi",
            "MXF OP-Atom": ".mxf",
            "MXF OP1A": ".mxf",
        }
        return ext_map.get(self.format, ".mp4")

    def to_resolve_render_settings(self) -> dict:
        """转换为达芬奇渲染设置字典"""
        return {
            "TargetDir": self.output_path,
            "CustomName": self.naming_template,
            "FormatWidth": self.width,
            "FormatHeight": self.height,
            "VideoFormat": self._resolve_video_format(),
            "VideoCodec": self._resolve_video_codec(),
            "AudioCodec": self._resolve_audio_codec(),
        }

    def _resolve_video_format(self) -> str:
        mapping = {
            "QuickTime": "QuickTime",
            "MP4": "mp4",
            "AVI": "avi",
            "MXF OP-Atom": "MXF OP-Atom",
            "MXF OP1A": "MXF OP1A",
        }
        return mapping.get(self.format, "mp4")

    def _resolve_video_codec(self) -> str:
        mapping = {
            "H.264": "h264",
            "H.265": "h265",
            "DNxHR": "DNxHR",
            "ProRes": "ProRes",
            "Uncompressed": "Uncompressed",
            "MJPEG": "MJPEG",
            "DNxHD": "DNxHD",
            "XDCAM": "XDCAM",
        }
        return mapping.get(self.video_codec, "h264")

    def _resolve_audio_codec(self) -> str:
        mapping = {
            "AAC": "aac",
            "PCM": "Linear PCM",
            "MP3": "mp3",
        }
        return mapping.get(self.audio_codec, "aac")

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "format": self.format,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "resolution": self.resolution,
            "custom_width": self.custom_width,
            "custom_height": self.custom_height,
            "frame_rate": self.frame_rate,
            "quality": self.quality,
            "data_levels": self.data_levels,
            "color_space_tag": self.color_space_tag,
            "color_space_gamma": self.color_space_gamma,
            "bypass_reencode": self.bypass_reencode,
            "alpha_channel": self.alpha_channel,
            "keyframe_interval": self.keyframe_interval,
            "encoding_profile": self.encoding_profile,
            "multi_pass": self.multi_pass,
            "pixel_aspect": self.pixel_aspect,
            "sample_rate": self.sample_rate,
            "bit_depth": self.bit_depth,
            "audio_bitrate": self.audio_bitrate,
            "audio_channels": self.audio_channels,
            "naming_template": self.naming_template,
            "output_path": self.output_path,
            "use_unique_filenames": self.use_unique_filenames,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExportSettings":
        """从字典反序列化"""
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})


# ── 预设管理 ──────────────────────────────────────────

@dataclass
class ExportPreset:
    """导出预设"""
    name: str
    settings: ExportSettings = field(default_factory=ExportSettings)
    created_at: str = ""
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "settings": self.settings.to_dict(),
            "created_at": self.created_at,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExportPreset":
        return cls(
            name=data.get("name", ""),
            settings=ExportSettings.from_dict(data.get("settings", {})),
            created_at=data.get("created_at", ""),
            description=data.get("description", ""),
        )
