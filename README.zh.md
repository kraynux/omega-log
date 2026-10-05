<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 许可证（见 LICENSE 文件） -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**服务器日志管理与查看工具**

> 由 **kraynux** 为 **Omega-server** 开发
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

官方页面：[OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/) &nbsp; 预览：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

**语言：**
🇫🇷 [Français](README.md) · 🇬🇧 [English](README.en.md) · 🇪🇸 [Español](README.es.md) · 🇷🇺 [Русский](README.ru.md) · 🇨🇳 **[中文](README.zh.md)**

---

**Omega-log** 是 `omega-` 系列中专门用于在 TUI 中管理、读取和分析服务器日志文件的工具——自动检测活动服务及其日志、统一的中央日志库、三种阅读模式（简单跟踪、经典阅读、通过 `lnav` 合并多文件）、IP 处理、统计分析、轮转/备份/恢复、安全清空与导出。通过**移植并改编**已经成熟的 [omega-fire](https://github.com/kraynux) 和 [omega-serv](https://github.com/kraynux) 代码构建而成，而非从零重写。

## 1. 定位与范围

Omega-log 回答一个简单的问题：「我的日志里发生了什么，我该如何处理？」——不依赖固定的已知路径列表，默认绝不以 root 身份运行，并且绝不会悄无声息地丢失或损坏真实的日志文件。

### Omega-log 能做什么

- 自动检测机器上活动的服务（Web 服务器、数据库、邮件、DNS、安全组件、`omega-serv`……），并提供导入其已知日志的选项——可按明细或整体导入，还可手动扫描任意文件夹作为补充。
- 将待处理的日志集中到唯一的日志库中，作为所有其他界面的统一入口。
- 根据需要以三种模式之一阅读日志：带解析与统计的简单跟踪、带实时跟随的经典原始阅读，或通过封装 `lnav` 实现的多文件合并。
- 将日志(组) + 查看器的组合保存为收藏，便于直接启动。
- 按时间段计算访问量前 10 的 IP，并支持从一个或多个文件中定向删除。
- 计算访问统计信息（流量、唯一 IP 数、错误率、按小时分布），可导出为 JSON 或带主题的 HTML。
- 对日志文件进行备份（压缩 + 自动保留策略）、恢复（合并或覆盖，并先行安全备份）以及清空（原地截断或删除）——始终需要明确确认。
- 通过 `omega-lib` 自动适配终端能力（颜色、尺寸），与整个系列保持一致。

### Omega-log 不做什么

| 功能 | 负责工具 |
|---|---|
| 防火墙、网络规则、入侵检测 | OMEGA-FIRE |
| Web 服务器、反向代理、WAF、Active Defense | OMEGA-SERV |
| 端口扫描、网络服务识别 | OMEGA-CHECK |
| 网络侦察、目标数字身份画像 | OMEGA-TRACK |

目前尚无与 TUI 功能完全对等的 CLI（当前命令行模式仅覆盖服务扫描，见 §3.2），没有跨多台机器的集中聚合，也没有基于阈值的实时告警——Omega-log 始终是一个本地检查与维护工具，而不是 SIEM。

### 使用警告

维护类操作（**清空**、**Rotate → 以覆盖模式恢复**）会永久修改或清除日志文件的真实内容——操作前始终会显示明确的确认提示，列出涉及的文件，绝不会自动触发。如有疑虑，请在操作前先备份（**Rotate → 立即备份**）。

## 2. 安装

### 先决条件

- Python 3.10+
- Linux（已在 Arch/Manjaro、Debian/Ubuntu、RHEL/Fedora 上测试）
- 系统已安装 `lnav`，仅多文件合并查看器需要（其余两个查看器在没有它的情况下也能正常工作）：

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### 安装步骤

```bash
[ -d omega-log ] && echo "ℹ️ 已在此处解压，跳过该步骤。" || tar -xzf omega-log.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh` 会：

1. 如果尚不存在，创建虚拟环境 `.venv`。
2. 安装依赖项（如存在已随附的 `omega-lib` 则先安装，再执行 `pip install -e .` —— `pyproject.toml` 始终是唯一的权威来源）。
3. 为 `omega-log.sh` 和 `install.sh` 添加可执行权限。
4. 检查 `lnav` 是否存在（缺失时仅给出提示性警告，绝不阻断安装）。
5. 向 `~/.bashrc` 和 `~/.zshrc` 添加 `log` 别名（若已存在则不重复添加）。

### 依赖项

全部声明在 `pyproject.toml` 中（没有单独的 `requirements.txt`）：
- `omega-lib`：系列共享库（TUI 与导出主题、终端检测、设置存储）
- `textual`：TUI 框架
- `jinja2`：带主题的 HTML 导出（统计、归档）
- `pyte`：`lnav` 查看器所需的终端模拟（在封装的 pty 中渲染）
- 开发依赖（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`ruff`、`mypy`

## 3. 使用方法

### 3.1. 交互模式（TUI）

推荐用于日常使用——不带参数启动：

```bash
./omega-log.sh
```
如果已创建别名，只需在新终端中输入 `log`：
```bash
log
```

总体流程：启动画面 → 主菜单（两栏——一侧为注册表/日志库/查看日志/收藏/查看与处理 IP/统计，另一侧为 Rotate/清空/导出/设置/帮助/退出）→ 所选功能界面 → 返回菜单（`Esc`）。应用内完整帮助（按 `a`）详细说明了每个界面、每个查看器以及贯穿全局的概念（一次性 sudo 提权、日志状态、按编号选择）——要点见 §4。

#### 快捷键

| 按键 | 操作 |
|---|---|
| `↑` / `↓` | 在界面元素间导航 |
| `Tab` / `Shift+Tab` | 在表单字段间导航 |
| `Esc` | 返回上一界面（主界面上为退出确认） |
| `t` | 切换到下一主题（立即应用，无需确认） |
| `r` | 刷新终端检测 |
| `a` | 显示帮助（详尽内容，每个界面一章） |
| `q` | 退出（需确认） |

### 3.2. 命令行模式（CLI）

目前仅限于服务扫描（尚未与 TUI 完全对等——收藏、Rotate、清空功能将随各自阶段陆续加入，见 `plan_omega_log.md` §12）：

```bash
# 检测活动服务及其已知日志
python -m omega_log scan

# + 手动扫描额外的文件夹
python -m omega_log scan --path /var/log
```

### 3.3. 环境变量

| 变量 | 作用 |
|---|---|
| `OMEGA_LOG_VAR_DIR` | 更改应用状态文件夹的位置（默认 `./var`，相对于启动目录） |

## 4. 功能一览

| 界面 | 说明 |
|---|---|
| **功能注册表** | 检测机器上活动的服务，并提供导入其已知日志的选项（明细或整体）。另可手动扫描文件夹。 |
| **日志库** | 引用所有待处理日志的中央枢纽——由注册表或手动导入填充。 |
| **查看日志** | 从日志库中选择一个或多个日志 + 选择查看器（1 个日志 → 全部 3 种查看器；2 个及以上 → 仅 `lnav`）。 |
| **收藏** | 以名称保存的日志(组) + 查看器组合，便于直接启动。 |
| **查看与处理 IP** | 按时间段（24 小时/7 天/30 天/全部）统计访问量前 10 的 IP，并支持从一个或多个日志中定向删除某个 IP。 |
| **统计（访问）** | 流量、唯一 IP 数、错误率、热门 IP、按小时分布——支持导出 JSON/HTML，提供 5 种主题。 |
| **Rotate** | 对日志进行压缩备份 + 自动清理超额归档 + 恢复（合并或覆盖，并先行安全备份）。 |
| **清空** | 清空日志内容（原地截断，对仍持有该文件打开状态的服务是安全的）或完全删除一个或多个文件——始终需要确认。 |
| **导出** | 将归档列表（Rotate）导出为 JSON 或带主题的 HTML。 |
| **设置** | 主题、渲染配置、清理应用文件夹（exports/screenshots）。 |

### 3 种查看器

1. **简单** —— 实时跟踪，带通用解析（时间戳、IP、级别、服务）和小型统计面板。对于可识别的 HTTP 访问日志，会额外显示 HTTP 状态码/延迟列，并按阈值着色。
2. **经典** —— 读取最后若干行原始内容 + 「实时跟随」开关，不做解析：无论格式如何都最简单、最可靠。
3. **lnav** —— 在封装终端（pty）内合并多个文件，用于交叉分析。主题切换（`t`）、标记并复制到剪贴板（`Ctrl+C`，OSC 52）、退出（`Ctrl+Q`）——均在到达 `lnav` 本身之前被拦截处理。

## 5. 终端兼容性

TUI（Textual）会自动检测终端能力（模拟器类型、尺寸），并据此调整其结构化样式表（`complete`/`standard`/`reduced`/`mono`），无需手动设置任何参数——这是整个 `omega-` 系列共享的统一策略（`omega-lib`，`terminal/policies.py`）。可通过 `r` 键实时刷新。

### 按检测到的终端模拟器确定的配置

| 终端模拟器 | 初始配置 |
|---|---|
| Ghostty、Alacritty、WezTerm、Kitty | `complete` |
| Konsole、GNOME Terminal、Terminator、Xfce4 Terminal | `standard` |
| xterm、urxvt、现代 SSH | `reduced` |
| Linux TTY、旧版 SSH | `mono` |
| 未识别的模拟器 | `reduced`（默认回退） |

### 按终端尺寸确定的配置

| 最小尺寸（列 × 行） | 配置上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 低于此值 | `mono` |

最终采用的配置是**两者中更严格的一个**（模拟器与尺寸）。

## 6. 架构

采用 Clean Architecture（domain / application / infrastructure / interfaces），与整个 OMEGA 系列保持一致的约定：

```text
src/omega_log/
├── core/            功能注册表（服务检测）
├── domain/          纯业务逻辑（解析、统计、轮转、清空）
├── ports/           契约（Protocol）
├── application/     用例
├── infrastructure/  具体实现（探测、存储、归档、导出、lnav、并发）
├── interfaces/      TUI（Textual）+ CLI
└── app/             组合根
```

依赖 [`omega-lib`](../LIB/omega-lib) 提供主题（10 种 TUI 主题 + 5 种导出主题）、终端检测和设置存储——与系列其余部分共用同一基础。繁重的计算（热门 IP、访问统计）在专用的 `ProcessPoolExecutor`（`infrastructure/concurrency/`）中执行，绝不占用界面线程，即使处理数十万行的文件也能保持响应。

## 7. 测试

```bash
source .venv/bin/activate
pytest tests/ -q      # 171 个测试
ruff check .
mypy src
```

结构：`tests/unit/`（领域与应用层，无真实 I/O）、`tests/integration/`（真实文件，通过 Textual 的 `Pilot` API 进行无界面 TUI 测试）。

## 8. 开发状态

开发计划的全部 10 个阶段均已完成：基础架构、领域模型、基础 TUI、查看器、收藏/日志库/IP、维护功能、统计/导出、收尾完善、一次性 sudo 提权、将 CPU 密集型计算转移到独立进程——每项移植决策的详情见 `plan_omega_log.md`。

## 9. 许可证

MIT —— 见 [LICENSE](LICENSE)。

---

> Omega-log —— 检测、集中、阅读、分析、维护。
> 您的日志始终归您所有：绝不在非必要时提升权限，绝不在未经确认的情况下执行破坏性操作。
