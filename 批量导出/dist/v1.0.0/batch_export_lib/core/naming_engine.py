"""
命名规则引擎 - 模板变量解析与文件名生成
"""
from datetime import datetime
from typing import Dict, List


# 支持的变量定义
VARIABLES = {
    "{timeline}": "时间线名称",
    "{date}": "日期 (YYYYMMDD)",
    "{time}": "时间 (HHMMSS)",
    "{index}": "导出序号 (01起)",
    "{project}": "项目名称",
    "{resolution}": "分辨率 (如1920x1080)",
    "{fps}": "帧率",
    "{format}": "导出格式 (如mp4)",
    "{codec}": "视频编码器",
}


class NamingEngine:
    """命名规则引擎"""

    def __init__(self):
        self._counter: Dict[str, int] = {}

    def reset_counter(self):
        """重置序号计数器"""
        self._counter.clear()

    def generate_filename(self, template: str, timeline_name: str,
                          index: int = 1, **kwargs) -> str:
        """
        根据模板生成文件主名 (不含扩展名)

        Args:
            template: 模板字符串，如 "{timeline}_{date}_{index}"
            timeline_name: 当前时间线名称
            index: 导出序号 (1-based)
            **kwargs: 额外上下文 (project, resolution, fps, format, codec)

        Returns:
            生成的文件名 (不含扩展名)
        """
        now = datetime.now()

        result = template
        result = result.replace("{timeline}", timeline_name)
        result = result.replace("{date}", now.strftime("%Y%m%d"))
        result = result.replace("{time}", now.strftime("%H%M%S"))
        result = result.replace("{index}", self._format_index(index))
        result = result.replace("{project}", kwargs.get("project", ""))
        result = result.replace("{resolution}",
                                kwargs.get("resolution", "1920x1080"))
        result = result.replace("{fps}", kwargs.get("fps", "24"))
        result = result.replace("{format}",
                                kwargs.get("format", "mp4").lower())
        result = result.replace("{codec}", kwargs.get("codec", "H264"))

        # 清理文件名中的非法字符
        result = self._sanitize(result)
        return result

    def generate_preview(self, template: str, timeline_name: str = "示例时间线",
                         index: int = 1, **kwargs) -> str:
        """生成命名预览，使用示例值"""
        return self.generate_filename(
            template, timeline_name, index,
            project=kwargs.get("project", "我的项目"),
            resolution=kwargs.get("resolution", "1920x1080"),
            fps=kwargs.get("fps", "24"),
            format=kwargs.get("format", "mp4"),
            codec=kwargs.get("codec", "H264"),
        )

    def get_variables(self) -> Dict[str, str]:
        """返回可用变量字典 {变量名: 描述}"""
        return dict(VARIABLES)

    def _format_index(self, index: int) -> str:
        """序号格式化: 两位数补零"""
        return f"{index:02d}"

    def _sanitize(self, name: str) -> str:
        """移除文件名非法字符"""
        illegal = r'<>:"/\|?*'
        for ch in illegal:
            name = name.replace(ch, '_')
        # 去除首尾空格和点
        name = name.strip('. ').rstrip()
        return name


# 全局单例
_engine: NamingEngine = None


def get_naming_engine() -> NamingEngine:
    global _engine
    if _engine is None:
        _engine = NamingEngine()
    return _engine
