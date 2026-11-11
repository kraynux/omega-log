<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="512">
</div>

# 📜 OMEGA-LOG

**服务器日志管理与查看工具**

> 由 [kraynux](https://github.com/kraynux) 为 [Omega-Server](https://kraynux.snake-mackarel.ts.net) 打造   

官方页面：[OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/zh-CN/) &nbsp; 预览：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 界面、文档和导出提供 **17 种语言**。  
**语言：**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** 是 `omega-` 套件中专门用于在 TUI 中管理、阅读和分析服务器日志文件的工具——自动检测正在运行的服务及其日志、中央日志库、三种阅读模式（简单跟踪、经典阅读、通过 `lnav` 合并多个文件）、IP 处理、统计、轮转/备份/恢复、安全清理和导出。它通过**移植和改编** [omega-fire](https://github.com/kraynux) 和 [omega-serv](https://github.com/kraynux) 中已经成熟的代码构建，而不是从零重写。

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-log/D.png" width="24%" />
</p>

## 1. 愿景与范围

Omega-log 回答一个简单的问题：“我的日志里发生了什么，我该如何处理？”——不依赖固定的已知路径列表，默认从不以 root 身份运行，也从不悄无声息地丢失或损坏真实的日志文件。

### Omega-log 能做什么

- 自动检测本机上正在运行的服务（Web 服务器、数据库、邮件、DNS、安全、`omega-serv`...），并提议逐个或全部导入它们的已知日志——此外还可以手动扫描任意文件夹。
- 将待处理的日志集中到唯一的日志库中，作为所有其他界面的入口。
- 按需以三种模式阅读日志：带解析和统计的简单跟踪、带实时跟踪的经典原始阅读，或封装 `lnav` 的多文件合并。
- 将“日志 + 查看器”组合保存为收藏，以便直接启动。
- 按时间段计算前 10 名 IP，或查找某个特定 IP，并可从一个或多个文件中有针对性地删除它们。
- 计算访问统计（访问量、独立 IP、错误率、按小时分布），可导出为 JSON 或带主题的 HTML。
- 备份（压缩 + 自动保留），可手动执行，也可通过计划备份每晚执行；恢复（合并或覆盖，并附带安全备份）以及清理（就地截断或删除）日志文件，始终需要明确确认。
- 检查日志健康状况（权限、静默或损坏的日志、磁盘空间、备份），并针对每项发现说明该怎么做。
- 通过 `omega-lib` 自动适应终端的能力（颜色、尺寸），与套件其他工具一致。

### Omega-log 不做什么

| 功能 | 负责的工具 |
|---|---|
| 防火墙、网络规则、入侵检测 | OMEGA-FIRE |
| Web 服务器、反向代理、WAF、Active Defense | OMEGA-SERV |
| 端口扫描、网络服务识别 | OMEGA-CHECK |
| 网络观察、目标的数字身份 | OMEGA-TRACK |

（暂时）还没有与 TUI 功能完全对等的 CLI（当前命令行模式只涵盖服务扫描，见 §3.2），没有多机集中聚合，也没有基于阈值的实时告警——Omega-log 仍然是一个本地检查和维护工具，而不是 SIEM。

### 使用警告

维护操作（**清理**、**Rotate → 以覆盖模式恢复**）会永久修改或删除日志文件的真实内容——执行前始终会有明确的确认，详细列出相关文件，从不自动触发。如有疑问，请先备份（**Rotate → 立即备份**）再操作。

## 2. 安装

### 前提条件

- Python 3.10+
- Linux（已在 Arch/Manjaro、Debian/Ubuntu、RHEL/Fedora 上测试）
- 系统中已安装 `lnav`，仅用于多文件合并查看器（另外两个查看器无需它即可正常工作）：

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### 安装

```bash
[ -d omega-log ] && echo "ℹ️ 已在此处解压，跳过此步骤。" || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`：

1. 如果虚拟环境 `.venv` 尚不存在，则创建它。
2. 安装依赖（如果存在内置的 `omega-lib` 则先安装，然后执行 `pip install -e .`——`pyproject.toml` 仍是唯一的依据来源）。
3. 使 `omega-log.sh` 和 `install.sh` 可执行。
4. 检查 `lnav` 是否存在（缺失时给出提示性警告，从不阻断）。
5. 将别名 `log` 添加到 `~/.bashrc` 和 `~/.zshrc`（已存在则不重复添加）。

### 依赖

在 `pyproject.toml` 中声明（没有单独的 `requirements.txt`）：
- `omega-lib`：套件共享库（TUI 与导出主题、终端检测、设置存储）
- `textual`：TUI 界面
- `jinja2`：带主题的 HTML 导出（统计、归档）
- `pyte`：为 `lnav` 查看器提供终端仿真（在封装的 pty 中渲染）
- 开发依赖（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`ruff`、`mypy`

## 3. 使用

### 3.1. 交互模式（TUI）

推荐日常使用——不带参数启动：

```bash
./omega-log.sh
```
如果您已创建别名，只需在新终端中输入 `log`：
```bash
log
```

总体流程：启动画面 → 主菜单（两列——一侧是 能力清单/日志库/查看日志/收藏/查看并处理 IP/统计，另一侧是 Rotate/清理/导出/日志健康/选项/帮助）→ 所选功能的界面 → 返回菜单（`Esc`）。完整帮助（`a`）详细介绍每个界面、每个查看器以及通用概念（临时 sudo 提权、日志状态、按编号选择）——要点见 §4。

#### 键盘快捷键

| 按键 | 操作 |
|---|---|
| `↑` / `↓` | 在界面元素之间移动 |
| `Tab` / `Shift+Tab` | 在表单字段之间移动 |
| `Esc` | 返回上一界面（在主页上会确认退出） |
| `t` | 下一个主题（立即应用，无需确认） |
| `r` | 刷新终端检测 |
| `a` | 显示帮助（完整，每个界面一章） |
| `q` | 退出（需确认） |

### 3.2. 命令行模式（CLI）                                                              

尚未与 TUI 功能完全对等（收藏、清理等将在各自的阶段中加入，见 `plan_omega_log.md` §12）：

```bash
# 检测正在运行的服务及其已知日志
python -m omega_log scan

# + 手动扫描另一个文件夹
python -m omega_log scan --path /var/log

# 已安装的版本，并与最新发布的版本进行比较
python -m omega_log version --check

# 到期的计划备份（每晚由 systemd 定时器或 crontab 启动）
python -m omega_log rotate run-automations
```

### 3.3. 环境变量

| 变量 | 作用 |
|---|---|
| `OMEGA_LOG_VAR_DIR` | 更改应用状态文件夹的位置（默认 `./var`，相对于启动目录） |
| `OMEGA_LOG_LANG` | 为本次会话强制指定界面语言（如 `en`、`de`、`ja`），不更改已保存的设置 |

## 4. 功能

| 界面 | 说明 |
|---|---|
| **能力清单** | 检测本机上正在运行的服务，并提议逐个或全部导入它们的已知日志。另可手动扫描文件夹。 |
| **日志库** | 汇总所有待处理日志的中心——来源包括能力清单、手动导入、Omega-Serv 的已知日志，或通过 SSH 取回的副本。 |
| **查看日志** | 从日志库中选择一个或多个日志 + 选择查看器（1 个日志 → 3 个查看器均可用；2 个及以上 → 仅 `lnav`）。 |
| **收藏** | 以名称保存的“日志 + 查看器”组合，用于直接启动。 |
| **查看并处理 IP** | 按时间段（24 小时/7 天/30 天/全部）列出前 10 名 IP，或查找特定 IP（IPv4 或 IPv6），并从一个或多个日志中有针对性地删除某个 IP。 |
| **统计（访问）** | 访问量、独立 IP、错误率、前几名 IP、按小时分布——导出为 JSON/HTML，共 5 种主题。 |
| **Rotate** | 日志的压缩备份 + 自动清除多余归档的保留策略 + 恢复（合并或覆盖，并附带安全备份）。**计划备份**：按天、周或月备份某个日志，每晚由 systemd 定时器或您 crontab 中的一行（OpenRC、runit）执行，以您的账户运行，从不使用 root。 |
| **清理** | 清空日志内容（就地截断，对仍打开该文件的服务是安全的）或彻底删除一个或多个文件——始终需要确认。 |
| **导出** | 将归档列表（Rotate）导出为 JSON 或带主题的 HTML。 |
| **日志健康** | 对日志库中的日志、磁盘、备份和计划备份进行只读检查：权限、静默或损坏的日志、日期、logrotate、距磁盘写满的天数，并给出应采取的措施。修正过于宽松的权限（必要时使用 sudo），导出 JSON/HTML/TXT。 |
| **选项** | 主题、渲染配置、界面语言和导出语言（17 种语言）、清理应用文件夹（exports/screenshots）。 |

### 3 种查看器

1. **简单** — 实时跟踪，带通用解析（时间戳、IP、级别、服务）和小型统计表。对于可识别的 HTTP 访问日志，额外显示 HTTP 状态码/延迟列，并按阈值着色。
2. **经典** — 阅读最后几行原始内容 + 切换“实时跟踪”，不做解析：无论何种格式都最简单、最可靠。
3. **lnav** — 在封装的终端（pty）中合并多个文件，用于交叉分析。切换主题（`t`）、标记 + 复制到剪贴板（`Ctrl+C`，OSC 52）、退出（`Ctrl+Q`）——均在 `lnav` 本身之前被拦截。

## 5. 终端兼容性

TUI（Textual）会自动检测终端的能力（模拟器、尺寸），并据此调整其结构样式表（`complete`/`standard`/`reduced`/`mono`），无需手动参数——整个 `omega-` 套件共享同一策略（`omega-lib`，`terminal/policies.py`）。可按 `r` 键实时刷新。

### 根据检测到的模拟器选择配置

| 模拟器 | 初始配置 |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, 现代 SSH | `reduced` |
| Linux TTY, 旧版 SSH | `mono` |
| 无法识别的模拟器 | `reduced`（默认回退） |

### 根据终端尺寸选择配置

| 最小尺寸（列 × 行） | 配置上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 更小 | `mono` |

最终采用的配置是**两者中限制最严格的**（模拟器和尺寸）。

## 6. 架构

Clean Architecture（领域 / 应用 / 基础设施 / 接口），与 OMEGA 套件其余部分的约定相同：

```text
src/omega_log/
├── core/            能力清单（服务检测）
├── domain/          纯业务逻辑（解析、统计、轮转、清理）
├── ports/           契约（Protocol）
├── application/     用例
├── infrastructure/  真实实现（探测、存储、归档、导出、lnav、并发）
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

依赖 [`omega-lib`](../../../../LIB/omega-lib) 提供主题（10 种 TUI 主题 + 5 种导出主题）、终端检测和设置存储——与套件其余部分共用同一基础。繁重的计算（前几名 IP、访问统计）在专用的 `ProcessPoolExecutor`（`infrastructure/concurrency/`）中执行，从不在界面线程上运行，因此即使面对数十万行的文件也能保持响应。

## 7. 测试

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 个测试
ruff check .
mypy src
```

结构：`tests/unit/`（领域与应用，无真实 I/O），`tests/integration/`（真实文件，通过 Textual 的 `Pilot` API 进行无界面 TUI 测试）。

## 8. 开发状态

开发计划的 10 个阶段均已完成：基础、领域、基础 TUI、查看器、收藏/日志库/IP、维护、统计/导出、收尾、临时 sudo 提权、将 CPU 密集型计算移至独立进程——每项移植决策的详情见 `plan_omega_log.md`。自 1.6.0 起，引入了 omega-serv 2.6.0 日志管理器的新功能：日志健康、计划备份、查找特定 IP、显示版本和检查更新。

## 9. 许可证

MIT — 见 [LICENSE](../../../LICENSE)。

---

> Omega-log — 检测、集中、阅读、分析、维护。
> 您的日志始终属于您：没有真正必要绝不提权，未经确认绝不执行破坏性操作。
