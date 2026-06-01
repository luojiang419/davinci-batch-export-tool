"""
时间线扫描器 - 递归扫描媒体池文件夹结构，组织时间线树
"""
from dataclasses import dataclass, field
from typing import List, Optional

from ..utils.resolve_api import get_api


@dataclass
class TimelineInfo:
    """时间线信息"""
    name: str
    duration: str = "00:00:00"
    fps: str = "24"
    start_frame: int = 0
    end_frame: int = 0

    @property
    def frame_count(self) -> int:
        return self.end_frame - self.start_frame


@dataclass
class FolderNode:
    """文件夹节点（树结构）"""
    name: str
    subfolders: List["FolderNode"] = field(default_factory=list)
    timelines: List[TimelineInfo] = field(default_factory=list)
    parent: Optional["FolderNode"] = None

    @property
    def total_timeline_count(self) -> int:
        """当前文件夹及子文件夹中的时间线总数"""
        count = len(self.timelines)
        for sub in self.subfolders:
            count += sub.total_timeline_count
        return count


def scan_timelines() -> FolderNode:
    """
    扫描媒体池，返回按文件夹结构组织的时间线树

    策略:
      1. 获取项目中所有时间线名称 → 时间线对象的映射
      2. 递归遍历媒体池文件夹
      3. 在每个文件夹的 clip 列表中查找匹配名称的时间线
      4. 未匹配到文件夹的时间线归入 "未分类" 节点
    """
    api = get_api()

    if api.is_mock:
        return _scan_mock()

    try:
        project = api.get_current_project()
    except Exception:
        return FolderNode(name="未连接")

    # 1. 获取所有时间线映射
    timeline_map = api.get_all_timelines_map()

    # 2. 递归扫描媒体池
    media_pool = project.GetMediaPool()
    root_folder = media_pool.GetRootFolder()

    root_node = FolderNode(name=api.get_project_name())
    matched_names: set = set()

    _scan_folder(api, root_folder, root_node, timeline_map, matched_names)

    # 3. 未被匹配的时间线放入 "未分类"
    unmatched = {}
    for name, tl in timeline_map.items():
        if name not in matched_names:
            unmatched[name] = tl

    if unmatched:
        uncategorized = FolderNode(name="未分类", parent=root_node)
        for name, tl in unmatched.items():
            info = _build_timeline_info(api, tl, name)
            uncategorized.timelines.append(info)
        root_node.subfolders.append(uncategorized)

    return root_node


def _scan_folder(api, folder, parent_node: FolderNode,
                 timeline_map: dict, matched_names: set):
    """递归扫描文件夹"""
    # 获取子文件夹
    try:
        subfolders = folder.GetSubFolderList()
    except Exception:
        subfolders = []

    for sub in subfolders:
        sub_name = sub.GetName()
        sub_node = FolderNode(name=sub_name, parent=parent_node)

        # 递归处理子文件夹
        _scan_folder(api, sub, sub_node, timeline_map, matched_names)

        parent_node.subfolders.append(sub_node)

    # 检查当前文件夹中的 clip（时间线引用）
    try:
        clips = folder.GetClipList()
    except Exception:
        clips = []

    for clip in clips:
        clip_name = clip.GetName()
        if clip_name in timeline_map and clip_name not in matched_names:
            tl = timeline_map[clip_name]
            info = _build_timeline_info(api, tl, clip_name)
            parent_node.timelines.append(info)
            matched_names.add(clip_name)


def _build_timeline_info(api, timeline, name: str) -> TimelineInfo:
    """从 Resolve 时间线对象构建 TimelineInfo"""
    try:
        start = timeline.GetStartFrame()
        end = timeline.GetEndFrame()
        fps = api.get_timeline_fps(timeline)
        duration = api.get_timeline_duration(timeline)
    except Exception:
        start, end = 0, 0
        fps = "24"
        duration = "00:00:00"

    return TimelineInfo(
        name=name,
        duration=duration,
        fps=fps,
        start_frame=start,
        end_frame=end,
    )


def _scan_mock() -> FolderNode:
    """Mock 数据"""
    root = FolderNode(name="Mock项目")

    folders_data = {
        "工程": [
            TimelineInfo("开篇动画", "00:00:15", "24", 0, 360),
            TimelineInfo("产品展示", "00:01:30", "24", 0, 2160),
            TimelineInfo("结尾字幕", "00:00:10", "24", 0, 240),
        ],
        "素材": [
            TimelineInfo("B-Roll合集", "00:03:00", "25", 0, 4500),
        ],
        "输出": [],
    }

    for folder_name, timelines in folders_data.items():
        sub = FolderNode(name=folder_name, parent=root)
        sub.timelines = timelines
        root.subfolders.append(sub)

    # 添加嵌套子文件夹示例
    nested = FolderNode(name="子项目", parent=root.subfolders[0])
    nested.timelines = [
        TimelineInfo("A镜_特写", "00:00:05", "24", 0, 120),
        TimelineInfo("B镜_全景", "00:00:08", "30", 0, 240),
    ]
    root.subfolders[0].subfolders.append(nested)

    return root
