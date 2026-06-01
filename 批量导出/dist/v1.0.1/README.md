# 批量导出时间线插件 (Batch Export Timelines)

适用于 DaVinci Resolve 19+ 的 Fusion Script 插件。

## 功能

- 按媒体池文件夹结构浏览时间线
- 勾选/Shift多选需导出的时间线
- 完整的达芬奇导出参数设置面板
- 自定义命名规则（支持时间线名、日期、序号等变量）
- 批量导出到指定文件夹

## 安装

1. 运行 `install\install.bat`
2. 在达芬奇里启用：偏好设置 → 系统 → 常规 → External Scripting = Local
3. 重启 DaVinci Resolve
4. 在菜单 "工作区" → "脚本" → "Utility" → "BatchExport"

或手动复制：
```
将 `BatchExport.py` 和 `batch_export_lib/` 复制到:
%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility\
```

## 要求

- DaVinci Resolve 19.0+
- Windows 10/11

## 项目结构

```
批量导出/
├── BatchExport.py        # Fusion Script 入口
├── batch_export_lib/     # 插件代码
│   ├── ui/               # UI 模块
│   ├── core/             # 核心逻辑
│   └── utils/            # 工具/API封装
├── install/             # 安装脚本
├── docs/                # 文档
├── tests/               # 测试
└── dist/                # 编译输出
```
