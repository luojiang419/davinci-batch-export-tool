"""
批量导出时间线 - DaVinci Resolve 19+ Workflow Integration 插件

入口点: Resolve 导入此包时调用 GetUI(resolve) 获取面板组件。
"""
from .ui.main_panel import BatchExportPanel

# 插件元信息
PLUGIN_ID = "com.batch-export.timelines"
PLUGIN_NAME = "批量导出时间线"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "批量导出达芬奇时间线，支持自定义命名规则和完整导出参数设置"


def GetUI(resolve):
    """
    Resolve Workflow Integration API 入口

    Resolve 19+ 加载插件包时自动调用此函数，传入 Resolve 实例，
    返回 QWidget 作为插件面板嵌入 Resolve UI。

    Args:
        resolve: DaVinciResolveScript 实例

    Returns:
        QWidget: 插件面板
    """
    from .utils.resolve_api import get_api

    # 注入 Resolve 实例
    api = get_api()
    api.initialize(resolve_obj=resolve)

    # 创建面板并加载时间线
    panel = BatchExportPanel()
    panel.refresh_timelines()

    return panel


def GetPluginInfo():
    """返回插件元信息"""
    return {
        "id": PLUGIN_ID,
        "name": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "description": PLUGIN_DESCRIPTION,
        "author": "luojiang419",
        "min_resolve_version": "19.0",
    }
