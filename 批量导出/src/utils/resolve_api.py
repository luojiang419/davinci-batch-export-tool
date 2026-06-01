"""
DaVinci Resolve Scripting API 封装层

统一处理版本差异(Resolve 19+)、运行环境检测、Mock回退。
"""
import sys
from typing import Optional, Any


class ResolveAPIError(Exception):
    """Resolve API 调用异常"""


class ResolveAPI:
    """达芬奇 API 统一封装"""

    def __init__(self):
        self._resolve: Optional[Any] = None
        self._fusion = None
        self._media_storage = None
        self._is_mock = False

    def initialize(self, resolve_obj=None) -> bool:
        """初始化 API 连接，传入 Resolve 实例或自动获取"""
        if resolve_obj is not None:
            self._resolve = resolve_obj
            self._is_mock = False
            return True

        try:
            import DaVinciResolveScript as dvr
            self._resolve = dvr.scriptapp("Resolve")
            if self._resolve is not None:
                self._is_mock = False
                return True
        except ImportError:
            pass

        print("警告: 未检测到达芬奇运行环境，使用Mock模式")
        self._is_mock = True
        return False

    @property
    def is_connected(self) -> bool:
        return self._resolve is not None and not self._is_mock

    @property
    def is_mock(self) -> bool:
        return self._is_mock

    # ── 项目管理 ──────────────────────────────────────

    def get_project_manager(self):
        if self._is_mock:
            return _MockProjectManager()
        return self._resolve.GetProjectManager()

    def get_current_project(self):
        if self._is_mock:
            return _MockProject()
        pm = self.get_project_manager()
        if pm is None:
            raise ResolveAPIError("无法获取项目管理器")
        proj = pm.GetCurrentProject()
        if proj is None:
            raise ResolveAPIError("当前没有打开的项目")
        return proj

    # ── 媒体池 ────────────────────────────────────────

    def get_media_pool(self):
        project = self.get_current_project()
        return project.GetMediaPool()

    def get_root_folder(self):
        media_pool = self.get_media_pool()
        return media_pool.GetRootFolder()

    # ── 时间线 ────────────────────────────────────────

    def get_timeline_count(self) -> int:
        project = self.get_current_project()
        return project.GetTimelineCount()

    def get_timeline_by_index(self, index: int):
        project = self.get_current_project()
        return project.GetTimelineByIndex(index)

    def get_current_timeline(self):
        project = self.get_current_project()
        return project.GetCurrentTimeline()

    # ── 渲染设置 ──────────────────────────────────────

    def get_render_presets(self) -> list:
        project = self.get_current_project()
        return project.GetRenderPresetList()

    def load_render_preset(self, preset_name: str) -> bool:
        project = self.get_current_project()
        return project.LoadRenderPreset(preset_name)

    def set_render_settings(self, settings: dict) -> bool:
        project = self.get_current_project()
        return project.SetRenderSettings(settings)

    def add_render_job(self) -> str:
        """添加渲染任务，返回 job ID"""
        project = self.get_current_project()
        return project.AddRenderJob()

    def start_rendering(self, *job_ids) -> bool:
        """开始渲染"""
        project = self.get_current_project()
        return project.StartRendering(*job_ids)

    def delete_all_render_jobs(self) -> bool:
        project = self.get_current_project()
        return project.DeleteAllRenderJobs()

    def get_render_job_status(self, job_id: str) -> str:
        project = self.get_current_project()
        return project.GetRenderJobStatus(job_id)

    # ── 导出相关 ──────────────────────────────────────

    def get_render_formats(self) -> list:
        """返回支持的导出格式列表"""
        return [
            {"name": "QuickTime", "ext": ".mov"},
            {"name": "MP4", "ext": ".mp4"},
            {"name": "AVI", "ext": ".avi"},
            {"name": "MXF OP-Atom", "ext": ".mxf"},
            {"name": "MXF OP1A", "ext": ".mxf"},
        ]

    def get_video_codecs(self, format_name: str = "MP4") -> list:
        """根据格式返回可用编码器"""
        codecs = {
            "MP4": ["H.264", "H.265"],
            "QuickTime": ["H.264", "H.265", "DNxHR", "ProRes"],
            "AVI": ["Uncompressed", "MJPEG"],
            "MXF OP-Atom": ["DNxHR", "DNxHD"],
            "MXF OP1A": ["DNxHR", "DNxHD", "XDCAM"],
        }
        return codecs.get(format_name, ["H.264"])

    def get_audio_codecs(self) -> list:
        return ["AAC", "PCM", "MP3"]

    def get_resolutions(self) -> list:
        return [
            "1920×1080 (Full HD)",
            "3840×2160 (4K UHD)",
            "4096×2160 (4K DCI)",
            "1280×720 (HD)",
            "720×576 (SD PAL)",
            "720×480 (SD NTSC)",
            "自定义",
        ]

    def get_frame_rates(self) -> list:
        return ["23.976", "24", "25", "29.97", "30", "50", "59.94", "60"]

    def get_sample_rates(self) -> list:
        return ["32000Hz", "44100Hz", "48000Hz", "96000Hz"]

    def get_bit_depth(self) -> list:
        return ["8-bit", "10-bit", "16-bit"]


# ── Mock 对象（用于无 Resolve 环境的开发和测试）───

class _MockProjectManager:
    def GetCurrentProject(self):
        return _MockProject()


class _MockMediaPool:
    def GetRootFolder(self):
        return _MockFolder("根目录")


class _MockFolder:
    def __init__(self, name):
        self._name = name
    def GetName(self):
        return self._name
    def GetSubFolderList(self):
        return [
            _MockFolder("工程"),
            _MockFolder("素材"),
            _MockFolder("输出"),
        ]
    def GetClipList(self):
        return []


class _MockTimeline:
    def __init__(self, name, idx):
        self._name = name
        self._idx = idx
    def GetName(self):
        return self._name
    def GetStartFrame(self):
        return 0
    def GetEndFrame(self):
        return 1000


class _MockProject:
    def GetMediaPool(self):
        return _MockMediaPool()
    def GetTimelineCount(self):
        return 3
    def GetTimelineByIndex(self, idx):
        return _MockTimeline(f"时间线_{idx+1}", idx)
    def GetCurrentTimeline(self):
        return _MockTimeline("当前时间线", 0)
    def GetRenderPresetList(self):
        return ["YouTube 1080p", "Vimeo 4K", "自定义"]
    def GetName(self):
        return "Mock项目"


# 全局单例
_api_instance: Optional[ResolveAPI] = None


def get_api() -> ResolveAPI:
    """获取 ResolveAPI 全局单例"""
    global _api_instance
    if _api_instance is None:
        _api_instance = ResolveAPI()
        _api_instance.initialize()
    return _api_instance
