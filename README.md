# pyBoxshade 2.0

pyBoxshade 是用于多序列比对着色、预览和导出的桌面程序，支持蛋白质与核酸序列。输入为已经完成比对的序列文件，程序根据共识、相似残基组或指定参考序列进行着色。

本版本基于 [Michael Baron 的 pyBoxshade](https://github.com/mdbaron42/pyBoxshade) 升级，保留可配置的 BOXSHADE 着色方式，增加现代桌面工作区、矢量导出和命令行导出。项目采用 [GPL-3.0](LICENSE) 许可证。

## 功能

- 实时着色预览、源码标签页、最近打开文件，以及拖放打开。
- 快速调整序列类型、保守性阈值、每行残基数、共识行和位置标尺。
- 在完整设置中配置颜色、相似残基、残基分组、参考序列及序列编号。
- 缩放、平移、适配窗口和原始比例显示。
- 导出 SVG、分页 PDF、PNG、RTF、PostScript 和参考序列比较文本。
- 命令行导出，适合脚本调用和批量处理。
- 支持高 DPI 显示及 Windows 中文安装路径。
- 简体中文与英文界面，可即时切换并自动保存语言选择。

## 输入与输出

### 输入文件

支持 FASTA、Clustal、PHYLIP（常规、relaxed 和 sequential）、MSF、Nexus、Stockholm。

输入要求：

- 至少包含两条序列，各序列的比对长度相同。
- 文件使用 UTF-8 编码，可带 BOM。
- 残基使用英文字母；支持 `-`、`.`、`~` 缺口符号。
- 比对中至少有一个残基。

项目提供人工示例 [examples/demo.fasta](examples/demo.fasta)，用于检查启动与导出。

### 输出文件

| 格式 | 用途与说明 |
| --- | --- |
| SVG | 矢量图，保留文字与着色，适合后续排版和编辑 |
| PDF | 矢量文档，长比对自动分页 |
| PNG | 像素图片，适合直接查看和插入文档 |
| RTF | 带着色的富文本，可用于文字处理软件 |
| PS | PostScript，沿用原版字体与页面宽度约束 |
| TXT | 与指定参考序列比较的文本，需要选择参考序列 |

导出采用原子写入，写入失败时保留已有目标文件。Unicode 序列名称建议使用 SVG、PDF 或 RTF。

## 安装与启动

需要 Python 3.10 或更高版本。依赖由 [pyproject.toml](pyproject.toml) 管理：

| 依赖 | 版本范围 |
| --- | --- |
| PyQt5 | `>=5.15.11,<6` |
| Biopython | `>=1.85,<2` |
| NumPy | `>=1.26,<3` |

以下命令均在项目根目录执行。

### Windows

使用 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pyboxshade
```

安装完成后，也可以使用 PowerShell 7 执行启动脚本：

```powershell
pwsh -File .\launch.ps1
```

如已在本机构建 Windows 程序，可直接打开 `dist\pyBoxshade\pyBoxshade.exe`。移动程序时保留整个 `dist\pyBoxshade` 文件夹。

### Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m pyboxshade
```

图形界面需要可用的桌面环境和 Qt 系统依赖。Linux 的自动测试环境依赖安装步骤见 [.github/workflows/tests.yml](.github/workflows/tests.yml)。

原启动入口 `python BS_app.py` 也可打开当前桌面工作区。

## 图形界面使用

首次启动默认使用简体中文。在 **语言 / Language** 菜单中选择 **简体中文** 或 **English**，界面即时切换，后续启动沿用该选择。菜单、工具栏、全部设置页及常用提示均提供中文。输入解析失败、编码不正确、路径不存在、权限不足、文件占用和空间不足等常见错误显示中文原因及处理建议；弹窗中的 **显示详细信息** 可展开原始诊断。未识别的第三方错误提供中文概括及完整原始详情。语言切换保留序列名称、比对内容、着色参数和导出内容。

也可通过启动参数指定语言：

```powershell
.\.venv\Scripts\python.exe -m pyboxshade --language zh_CN
.\.venv\Scripts\python.exe -m pyboxshade --language en
# 打包程序同样支持
.\dist\pyBoxshade\pyBoxshade.exe --language zh_CN
```

1. 点击 **打开比对文件 / Open alignment**，或将比对文件拖入窗口。
2. 在左侧选择 **蛋白质 / Protein** 或 **DNA / RNA**，设置 **共识阈值 / Threshold** 与 **每行位点数 / Residues / line**。
3. 勾选 **共识序列行 / Consensus line** 和 **位置标尺 / Position ruler**。
4. 点击 **全部设置 / All settings** 配置颜色、分组、参考序列和编号。
5. 按住 Ctrl 滚动鼠标滚轮缩放，拖动预览平移；**适应窗口 / Fit** 适配窗口，**100%** 恢复原始比例。
6. 在 **导出 / Export** 菜单中选择导出格式。

共识与相似性结果取决于阈值、缺口计数、相似残基配置和参考序列选择。桌面设置沿用 `Boxshade/Boxshade` 命名空间，并保存最近文件及窗口状态。

更详细的中文操作说明见 [使用说明.md](使用说明.md)，原项目的完整功能文档见 [pyBoxshadeDocs.pdf](pyBoxshadeDocs.pdf)。

## 命令行导出

Windows 示例：

```powershell
.\.venv\Scripts\python.exe -m pyboxshade examples\demo.fasta --export alignment.svg
.\.venv\Scripts\python.exe -m pyboxshade examples\demo.fasta --export alignment.pdf --threshold 0.7 --line-width 60
.\.venv\Scripts\python.exe -m pyboxshade examples\demo.fasta --export comparison.txt --reference 1
```

Linux / macOS 使用 `.venv/bin/python`，并将路径分隔符写为 `/`。

| 参数 | 说明 |
| --- | --- |
| `alignment` | 输入比对文件；图形界面启动时可省略 |
| `--export PATH` | 导出后退出，根据扩展名选择 SVG、PDF、PNG、RTF、PS 或 TXT |
| `--threshold FLOAT` | 保守性阈值，范围 0–1 |
| `--line-width INT` | 每行残基数，范围 10–250 |
| `--dna` | 使用核酸模式 |
| `--reference INT` | 参考序列编号，从 1 开始；TXT 导出需要此参数 |
| `--language zh_CN/en` | 指定并保存图形界面语言；与 `--export` 同用时不修改桌面语言偏好 |
| `--version` | 显示版本 |
| `--help` | 显示帮助 |

命令行导出使用隔离的默认设置及传入参数，保留桌面偏好。默认阈值为 0.7，每行 60 个残基。成功返回退出码 `0`，输入或导出失败返回 `2`。

批量导出附加 `--language zh_CN` 可输出中文错误原因，同时保留原始技术详情；未指定语言时沿用英文命令行提示。读取失败时保留当前界面已有比对，写入失败时保留已有目标文件。格式异常、文件被占用或权限不足仍需按提示修正输入或保存位置。

需要保留生成文件时，建议将它们放在 `artifacts/` 中，该目录已配置 Git 忽略。

## 开发与测试

Windows：

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m build
```

开发依赖包括 pytest、build、wheel、PyInstaller 和 pypdf。

已在 Windows、Python 3.12 环境完成 60 项测试，覆盖输入格式、着色、缺口列、参考序列、编号、界面状态、中英文切换与保存、设置窗口翻译、语言切换后的数据和导出一致性、六种导出和失败保护。错误处理测试包括六种格式的损坏输入、解析器异常、文件权限和空间错误、非 UTF-8 编码、弹窗原始诊断以及中文命令行错误。Windows 打包程序已实际完成六种导出，并检查 PDF 文字、SVG 结构及 PNG 解码。

CI 配置覆盖 Windows / Linux 与 Python 3.10、3.12、3.13；远程 CI 及其他操作系统的实际结果尚待验证。

## Windows 打包

先安装开发依赖，然后使用 PowerShell 7：

```powershell
pwsh -File .\build_windows.ps1
```

输出目录为 `dist/pyBoxshade/`，其中包含程序、运行依赖、许可证、说明文档及示例文件。手写配置 [pyboxshade-modern.spec](pyboxshade-modern.spec) 包含中文安装路径兼容处理，应随源码提交。

Python 分发包通过 `python -m build` 生成，输出 wheel 和源码压缩包到 `dist/`。

## 仓库文件

| 路径 | 内容 |
| --- | --- |
| `pyboxshade/` | 桌面工作区、输入读取、导出、启动和资源处理 |
| `pyboxshade/assets/` | 程序运行需要的图标 |
| `BS_app.py`、`BS_config.py` | 原项目的着色、布局与共享配置 |
| `OutDevs.py`、`mydialog.py` | 输出设备与完整设置界面 |
| `tests/` | 自动测试 |
| `examples/` | 人工示例比对 |
| `.github/workflows/` | CI 配置 |
| `images/`、`pyBoxshadeDocs.pdf` | 原项目保留的资源与文档 |

[.gitignore](.gitignore) 排除虚拟环境、缓存、构建目录、安装元数据、临时导出、本机验证报告及本地环境配置。源码、测试、示例、运行资源和手写打包配置保留在版本管理范围内。

本地生成的 `build/`、`dist/` 和 `artifacts/` 内容可按需保留在磁盘中。需要分发程序时，可将构建产物作为发布附件提供。

## 运行边界

- 输入须已完成多序列比对。
- 解析、着色和渲染在界面线程中进行，大型比对处理期间界面可能等待。
- PNG 与预览的宽高上限为 32767 像素，总像素上限为一亿。
- SVG 高度上限为 32767 单位；较长的比对适合分页 PDF。
- PostScript 有字体及页面宽度限制。
- 目前已完成当前 Windows 环境验证，Linux 和 macOS 尚未完成实际运行验收。

## 来源与许可证

原项目：[mdbaron42/pyBoxshade](https://github.com/mdbaron42/pyBoxshade)。

本版本遵循 [GPL-3.0](LICENSE)。分发修改后的程序时，应按许可证提供对应源码并保留许可信息。
