"""
批量导出时间线 - DaVinci Resolve 19+ 插件包

所有导入延迟到 GetUI() 调用时，避免 Resolve 扫描阶段因 import 错误而静默跳过。
"""

PLUGIN_ID = "com.batch-export.timelines"
PLUGIN_NAME = "批量导出时间线"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "批量导出达芬奇时间线，支持自定义命名规则和完整导出参数设置"


def GetUI(resolve):
    """
    Resolve 点击菜单时调用此函数。
    所有模块在此处延迟导入，确保错误可见。
    """
    from .ui.main_panel import BatchExportPanel
    from .utils.resolve_api import get_api

    api = get_api()
    api.initialize(resolve_obj=resolve)

    panel = BatchExportPanel()
    panel.refresh_timelines()
    return panel


def GetPluginInfo():
    return {
        "id": PLUGIN_ID,
        "name": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "description": PLUGIN_DESCRIPTION,
        "author": "luojiang419",
        "min_resolve_version": "19.0",
    }
