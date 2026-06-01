# 进度快照 07 - 修复安装方案为 Fusion Script

**时间**: 2026-06-01
**修复**: 安装方案从 Workflow Integration Plugin → Fusion Script

## 问题原因

之前的方案将插件安装到 `Workflow Integration Plugins\` 目录，但达芬奇 19 的实际使用方式是通过 **Fusion Scripts** 菜单加载。参考同一仓库下成功安装的 `批量创建时间线` 项目，正确的安装路径是:

```
%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility\
```

## 修改内容

### 新增文件
| 文件 | 说明 |
|------|------|
| `BatchExport.py` | 顶层入口脚本（独立文件，含 Resolve API 自动检测） |
| `run_standalone.bat` | 独立运行脚本（Mock模式，无需Resolve） |

### 修改文件
| 文件 | 变化 |
|------|------|
| `src/__init__.py` | 包含 GetUI() GetPluginInfo() 入口函数 |
| `src/main.py` | 简化，改为从 __init__.py 重导出 |
| `install/install.bat` | 目标路径改为 Fusion\Scripts\Utility\，安装 BatchExport.py + BatchExport_src/ |
| `dist/v1.0.0/` | 重建，含新结构 |

### 安装后目录结构
```
Fusion\Scripts\Utility\
├── BatchExport.py           ← 入口脚本
└── BatchExport_src\         ← 插件包
    ├── __init__.py           ← GetUI() 入口
    ├── main.py
    ├── ui/main_panel.py
    ├── core/
    │   ├── timeline_scanner.py
    │   ├── export_engine.py
    │   ├── export_settings_model.py
    │   ├── naming_engine.py
    │   └── preset_manager.py
    └── utils/resolve_api.py
```

### 使用方式
1. 运行 `install\install.bat` 安装
2. 启用: 偏好设置 > 系统 > 常规 > 外部脚本 = 本地
3. 使用: 工作区 > 脚本 > Utility > BatchExport

## 当前项目结构
```
批量导出/
├── BatchExport.py            ← 新增: Fusion Script 入口
├── run_standalone.bat        ← 新增: Mock 独立运行
├── src/
│   ├── __init__.py           ← 修改: 包含入口函数
│   ├── main.py               ← 修改: 重导出
│   ├── ui/main_panel.py
│   ├── core/
│   ├── utils/resolve_api.py
├── install/install.bat       ← 修改: Fusion Script 路径
├── docs/README.md
├── dist/v1.0.0/              ← 重建
├── backup/v1.0.0/
└── 进度快照/
```
