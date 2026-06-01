# 批量导出时间线插件 (Batch Export Timelines)

适用于 DaVinci Resolve 19+ 的 Workflow Integration 插件。

## 功能

- 按媒体池文件夹结构浏览时间线
- 勾选/Shift多选需导出的时间线
- 完整的达芬奇导出参数设置面板
- 自定义命名规则（支持时间线名、日期、序号等变量）
- 批量导出到指定文件夹

## 安装

1. 运行 `install\install.bat`
2. 重启 DaVinci Resolve
3. 在菜单 "工作区" → "Workflow Integrations" → "批量导出时间线"

或手动复制：
```
将 src/ 目录下的全部内容复制到:
%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Workflow Integration Plugins\BatchExport\
```

## 要求

- DaVinci Resolve 19.0+
- Windows 10/11

## 项目结构

```
批量导出/
├── src/                  # 源代码
│   ├── main.py          # 插件入口
│   ├── ui/              # UI 模块
│   ├── core/            # 核心逻辑
│   └── utils/           # 工具/API封装
├── install/             # 安装脚本
├── docs/                # 文档
├── tests/               # 测试
└── dist/                # 编译输出
```
