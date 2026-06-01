"""
批量导出时间线 - 向后兼容入口

实际入口已移至 __init__.py（Resolve 19+ 标准）。
此文件保留供手动脚本调用。
"""
from . import (
    GetUI,
    GetPluginInfo,
    PLUGIN_ID,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    PLUGIN_DESCRIPTION,
)
