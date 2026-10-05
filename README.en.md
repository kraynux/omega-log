<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT License (see LICENSE file) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**Server log manager and viewer**

> Developed by **kraynux** for **Omega-server**
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Official page: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/) &nbsp; Preview: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

**Languages:**
🇫🇷 [Français](README.md) · 🇬🇧 **[English](README.en.md)** · 🇪🇸 [Español](README.es.md) · 🇷🇺 [Русский](README.ru.md) · 🇨🇳 [中文](README.zh.md)

---

**Omega-log** is the `omega-` suite's tool dedicated to managing, reading and analyzing server log files in a TUI — automatic detection of active services and their logs, a central library, three reading modes (simple tail, classic reading, multi-file merge via `lnav`), IP processing, statistics, rotation/backup/restore, secure purge and export. Built by **porting and adapting** already-mature code from [omega-fire](https://github.com/kraynux) and [omega-serv](https://github.com/kraynux) rather than rewritten from scratch.

## 1. Vision and scope

Omega-log answers a simple question: "what's happening in my logs, and how do I take care of it?" — without depending on a fixed list of known paths, never running as root by default, and never silently losing or corrupting a real log file.

### What Omega-log does

- Automatically detects active services on the machine (web servers, databases, mail, DNS, security, `omega-serv`...) and offers to import their known logs, in detail or in full — in addition to a manual scan of any folder.
- Centralizes the logs to process in a single Library, the entry point for every other screen.
- Reads a log using three modes depending on the need: simple tail with parsing and statistics, raw classic reading with live follow, or multi-file merge wrapping `lnav`.
- Remembers log(s) + viewer combinations as Favorites, for direct launch.
- Computes the top 10 IPs over a period and allows targeted removal in one or more files.
- Computes access statistics (volume, unique IPs, error rate, hourly breakdown) exportable as JSON or themed HTML.
- Backs up (compression + automatic retention), restores (merge or overwrite, with a safety backup) and purges (in-place truncation or deletion) log files, always with explicit confirmation.
- Automatically adapts to terminal capabilities (colors, size) via `omega-lib`, like the rest of the suite.

### What Omega-log does not do

| Function | Responsible tool |
|---|---|
| Firewall, network rules, intrusion detection | OMEGA-FIRE |
| Web server, reverse proxy, WAF, Active Defense | OMEGA-SERV |
| Port scanning, network service fingerprinting | OMEGA-CHECK |
| Network observation, digital identity of a target | OMEGA-TRACK |

No (yet) CLI with full parity with the TUI (the current command-line mode only covers service scanning, see §3.2), no centralized multi-machine aggregation, no real-time threshold alerting — Omega-log remains a local inspection and maintenance tool, not a SIEM.

### Usage warning

Maintenance actions (**Purge**, **Rotate → Restore in Overwrite mode**) permanently modify or erase the real content of your log files — always preceded by an explicit confirmation detailing the files involved, never triggered automatically. If in doubt, back up (**Rotate → Back up now**) before acting.

## 2. Installation

### Prerequisites

- Python 3.10+
- Linux (tested on Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` installed on the system, only for the multi-file merge viewer (the other two viewers work normally without it):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Installation

```bash
[ -d omega-log ] && echo "ℹ️ Already extracted here, step skipped." || tar -xzf omega-log.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Creates the `.venv` virtual environment if it doesn't already exist.
2. Installs dependencies (vendored `omega-lib` first if present, then `pip install -e .` — `pyproject.toml` remains the single source of truth).
3. Makes `omega-log.sh` and `install.sh` executable.
4. Checks for `lnav` (informational warning if missing, never blocking).
5. Adds the `log` alias to `~/.bashrc` and `~/.zshrc` (no duplicate if already present).

### Dependencies

Declared in `pyproject.toml` (no separate `requirements.txt`):
- `omega-lib`: the suite's shared library (TUI + export themes, terminal detection, settings storage)
- `textual`: the TUI framework
- `jinja2`: themed HTML export (statistics, archives)
- `pyte`: terminal emulation for the `lnav` viewer (rendered inside a wrapped pty)
- Development dependencies (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Usage

### 3.1. Interactive mode (TUI)

Recommended for daily use — launched with no argument:

```bash
./omega-log.sh
```
if you created the alias, just type `log` in a new terminal:
```bash
log
```

General flow: splash screen → main menu (two columns — Registry/Library/View logs/Favorites/View and Process IPs/Statistics on one side, Rotate/Purge/Export/Options/Help/Quit on the other) → the chosen screen → back to the menu (`Escape`). The full in-app help (`a`) details every screen, every viewer, and the cross-cutting concepts (one-off sudo elevation, log states, selection by number) — see §4 for the essentials.

#### Keyboard shortcuts

| Key | Action |
|---|---|
| `↑` / `↓` | Navigate between the elements of a screen |
| `Tab` / `Shift+Tab` | Navigate between the fields of a form |
| `Escape` | Back to the previous screen (exit confirmation on the home screen) |
| `t` | Next theme (applied immediately, no confirmation) |
| `r` | Refresh terminal detection |
| `a` | Show help (exhaustive, one chapter per screen) |
| `q` | Quit (with confirmation) |

### 3.2. Command-line mode (CLI)

Limited to service scanning for now (not yet at full parity with the TUI — favorites, rotate, purge will come with their own phases, see `plan_omega_log.md` §12):

```bash
# Detect active services and their known logs
python -m omega_log scan

# + manual scan of an additional folder
python -m omega_log scan --path /var/log
```

### 3.3. Environment variables

| Variable | Effect |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Changes the location of the application state folder (`./var` by default, relative to the launch directory) |

## 4. Features

| Screen | Description |
|---|---|
| **Capability registry** | Detects active services on the machine and offers to import their known logs, in detail or in full. Manual folder scan available in addition. |
| **Library** | Central hub referencing all logs to process — fed by the Registry or by manual import. |
| **View logs** | Select one or more logs from the Library + choose the viewer (1 log → all 3 viewers; 2+ logs → `lnav` only). |
| **Favorites** | Log(s) + viewer combinations saved under a name, for direct launch. |
| **View and Process IPs** | Top 10 IPs per period (24h/7d/30d/all) and targeted removal of an IP from one or more logs. |
| **Statistics (access)** | Volume, unique IPs, error rate, top IPs, hourly breakdown — JSON/HTML export with 5 themes. |
| **Rotate** | Compressed backup of a log + automatic retention of excess archives + restore (merge or overwrite, with safety backup). |
| **Purge** | Empties a log's content (in-place truncation, safe for a service that still has it open) or completely deletes one or more files — always with confirmation. |
| **Export** | Export of the archive list (Rotate) as JSON or themed HTML. |
| **Options** | Theme, render profile, purge of application folders (exports/screenshots). |

### The 3 viewers

1. **Simple** — live tail with generic parsing (timestamp, IP, level, service) and a small statistics panel. For a recognized HTTP access log, extra columns appear for HTTP status code / latency, colored by threshold.
2. **Classic** — reads the last raw lines + a "Follow live" toggle, no parsing: the simplest and most reliable option regardless of format.
3. **lnav** — merges several files inside a wrapped terminal (pty), for cross-analysis. Theme cycling (`t`), mark + clipboard copy (`Ctrl+C`, OSC 52), quit (`Ctrl+Q`) — all intercepted before reaching `lnav` itself.

## 5. Terminal compatibility

The TUI (Textual) automatically detects the terminal's capabilities (emulator, size) and adapts its structural stylesheet accordingly (`complete`/`standard`/`reduced`/`mono`), with no manual flag — the same policy shared by the whole `omega-` suite (`omega-lib`, `terminal/policies.py`). Refreshable live with the `r` key.

### Profile by detected emulator

| Emulator | Initial profile |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modern SSH | `reduced` |
| Linux TTY, legacy SSH | `mono` |
| Unrecognized emulator | `reduced` (default fallback) |

### Profile by terminal size

| Minimum size (columns × rows) | Profile ceiling |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| below | `mono` |

The final profile used is **the more restrictive of the two** (emulator and size).

## 6. Architecture

Clean Architecture (domain / application / infrastructure / interfaces), the same convention as the rest of the OMEGA suite:

```text
src/omega_log/
├── core/            Capability registry (service detection)
├── domain/          Pure business logic (parsing, statistics, rotation, purge)
├── ports/           Contracts (Protocol)
├── application/     Use cases
├── infrastructure/  Real implementations (probes, storage, archives, export, lnav, concurrency)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

Depends on [`omega-lib`](../LIB/omega-lib) for theming (10 TUI themes + 5 export themes), terminal detection, and settings storage — the same foundation as the rest of the suite. Heavy computations (top IP, access statistics) run in a dedicated `ProcessPoolExecutor` (`infrastructure/concurrency/`), never on the UI thread, to stay responsive even on a file with hundreds of thousands of lines.

## 7. Tests

```bash
source .venv/bin/activate
pytest tests/ -q      # 171 tests
ruff check .
mypy src
```

Structure: `tests/unit/` (domain and application, no real I/O), `tests/integration/` (real files, headless TUI via Textual's `Pilot` API).

## 8. Development status

All 10 phases of the development plan are complete: foundation, domain, basic TUI, viewers, favorites/library/IP, maintenance, statistics/export, finalization, one-off sudo elevation, CPU-bound computations offloaded to a separate process — see `plan_omega_log.md` for the detail of each porting decision.

## 9. License

MIT — see [LICENSE](LICENSE).

---

> Omega-log — Detect, centralize, read, analyze, maintain.
> Your logs stay yours: no privilege escalation without real necessity, no destructive action without confirmation.
