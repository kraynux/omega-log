<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**Server log manager and viewer**

> Built by [kraynux](https://github.com/kraynux) for [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Official page: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/en/) &nbsp; Preview: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 Interface, documentation and exports available in **17 languages**.  
**Languages:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** is the tool of the `omega-` suite dedicated to managing, reading and analysing server log files in a TUI — automatic detection of active services and their logs, a central library, three reading modes (simple follow, classic reading, multi-file merge via `lnav`), IP handling, statistics, rotation/backup/restore, safe purge and export. Built by **porting and adapting** the already mature code of [omega-fire](https://github.com/kraynux) and [omega-serv](https://github.com/kraynux) rather than rewritten from scratch.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-log/D.png" width="24%" />
</p>

## 1. Vision and scope

Omega-log answers a simple question: "what is happening in my logs, and how do I take care of them?" — without relying on a fixed list of known paths, without ever running as root by default, and without ever silently losing or corrupting a real log file.

### What Omega-log does

- Automatically detects the services active on the machine (web servers, databases, mail, DNS, security, `omega-serv`...) and offers to import their known logs, one by one or all at once — in addition to a manual scan of any folder.
- Centralises the logs to handle in a single Library, the entry point for every other screen.
- Reads a log in one of three modes depending on the need: simple follow with parsing and statistics, raw classic reading with live follow, or multi-file merge wrapping `lnav`.
- Saves logs + viewer combinations as Favorites, for a direct launch.
- Computes the top 10 IPs per period, or searches for a specific IP, and allows their targeted removal from one or more files.
- Computes access statistics (volume, unique IPs, error rate, hourly distribution) that can be exported as JSON or themed HTML.
- Backs up (compression + automatic retention) by hand or every night through scheduled backups, restores (merge or replace, with a safety backup) and purges (in-place truncation or deletion) log files, always with explicit confirmation.
- Checks log health (permissions, silent or damaged logs, disk space, backups) and says what to do for each finding.
- Adapts automatically to the terminal's capabilities (colours, size) through `omega-lib`, like the rest of the suite.

### What Omega-log does not do

| Function | Responsible tool |
|---|---|
| Firewall, network rules, intrusion detection | OMEGA-FIRE |
| Web server, reverse proxy, WAF, Active Defense | OMEGA-SERV |
| Port scanning, network service identification | OMEGA-CHECK |
| Network observation, digital identity of a target | OMEGA-TRACK |

No CLI at full parity with the TUI (yet) (the current command-line mode only covers the service scan, see §3.2), no centralised multi-machine aggregation, no real-time threshold alerting — Omega-log remains a local inspection and maintenance tool, not a SIEM.

### Usage warning

Maintenance actions (**Purge**, **Rotate → Restore in Replace mode**) permanently modify or erase the real content of your log files — always preceded by an explicit confirmation listing the files concerned, never triggered automatically. When in doubt, back up (**Rotate → Back up now**) before acting.

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
[ -d omega-log ] && echo "ℹ️ Already extracted here, skipping." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Creates the `.venv` virtual environment if it does not already exist.
2. Installs the dependencies (vendored `omega-lib` first if present, then `pip install -e .` — `pyproject.toml` remains the single source of truth).
3. Makes `omega-log.sh` and `install.sh` executable.
4. Checks that `lnav` is present (informative warning if missing, never blocking).
5. Adds the `log` alias to `~/.bashrc` and `~/.zshrc` (no duplicate if already present).

### Dependencies

Declared in `pyproject.toml` (no separate `requirements.txt`):
- `omega-lib`: shared library of the suite (TUI + export themes, terminal detection, settings storage)
- `textual`: TUI interface
- `jinja2`: themed HTML export (statistics, archives)
- `pyte`: terminal emulation for the `lnav` viewer (rendered in a wrapped pty)
- Development dependencies (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Usage

### 3.1. Interactive mode (TUI)

Recommended for everyday use — launched without arguments:

```bash
./omega-log.sh
```
if you created the alias, just type `log` in a new terminal:
```bash
log
```

General flow: splash screen → main menu (two columns — Capability registry/Library/View logs/Favorites/View and Handle IPs/Statistics (access) on one side, Rotate/Purge/Export/Log health/Options/Help on the other) → screen of the chosen function → back to the menu (`Esc`). The full help (`a`) details every screen, every viewer and the cross-cutting concepts (one-off sudo elevation, log states, selection by numbers) — see §4 for the essentials.

#### Keyboard shortcuts

| Key | Action |
|---|---|
| `↑` / `↓` | Move between the items of a screen |
| `Tab` / `Shift+Tab` | Move between the fields of a form |
| `Esc` | Back to the previous screen (exit confirmation on the home screen) |
| `t` | Next theme (applied immediately, without confirmation) |
| `r` | Refresh terminal detection |
| `a` | Show the help (exhaustive, one chapter per screen) |
| `q` | Quit (with confirmation) |

### 3.2. Command-line mode (CLI)                                                              

No full parity with the TUI yet (favorites, purge... will come with their own phases, see `plan_omega_log.md` §12):

```bash
# Detect active services and their known logs
python -m omega_log scan

# + manual scan of an additional folder
python -m omega_log scan --path /var/log

# Installed version, compared with the latest published version
python -m omega_log version --check

# Scheduled backups that are due (run every night by the systemd timer or the crontab)
python -m omega_log rotate run-automations
```

### 3.3. Environment variables

| Variable | Effect |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Changes the location of the application state folder (`./var` by default, relative to the launch folder) |
| `OMEGA_LOG_LANG` | Forces the interface language for the session (e.g. `en`, `de`, `ja`) without changing the saved setting |

## 4. Features

| Screen | Description |
|---|---|
| **Capability registry** | Detects the services active on the machine and offers to import their known logs, one by one or all at once. Manual scan of a folder in addition. |
| **Library** | Central hub referencing every log to handle — fed by the Registry, by manual import, by Omega-Serv's known logs or by a copy fetched over SSH. |
| **View logs** | Selection of one or more logs from the Library + choice of viewer (1 log → all 3 viewers; 2+ logs → `lnav` only). |
| **Favorites** | Logs + viewer combinations saved under a name, for a direct launch. |
| **View and Handle IPs** | Top 10 IPs per period (24h/7d/30d/all), or search for a specific IP (IPv4 or IPv6), and targeted removal of an IP from one or more logs. |
| **Statistics (access)** | Volume, unique IPs, error rate, top IPs, hourly distribution — JSON/HTML export with 5 themes. |
| **Rotate** | Compressed backup of a log + automatic retention of surplus archives + restore (merge or replace, with a safety backup). **Scheduled backups**: a log backed up every day, week or month, run every night by a systemd timer or a line in your crontab (OpenRC, runit), under your account, never root. |
| **Purge** | Empties a log's content (in-place truncation, safe for a service that still has it open) or completely deletes one or more files — always with confirmation. |
| **Export** | Export of the archive list (Rotate) as JSON or themed HTML. |
| **Log health** | Read-only check of the Library's logs, the disk, backups and scheduled backups: permissions, silent or damaged logs, dates, logrotate, days before the disk is full, with the action to take. Fixing of overly open permissions (with sudo if needed), JSON/HTML/TXT export. |
| **Options** | Theme, rendering profile, interface language and export language (17 languages), purge of application folders (exports/screenshots). |

### The 3 viewers

1. **Simple** — live follow with generic parsing (timestamp, IP, level, service) and a mini statistics table. For a recognised HTTP access log, extra HTTP code / latency columns, coloured by threshold.
2. **Classic** — reading of the last raw lines + "Follow live" toggle, without parsing: the simplest and most reliable whatever the format.
3. **lnav** — merge of several files in a wrapped terminal (pty), for cross-analysis. Theme cycling (`t`), marking + clipboard copy (`Ctrl+C`, OSC 52), exit (`Ctrl+Q`) — all intercepted before `lnav` itself.

## 5. Terminal compatibility

The TUI (Textual) automatically detects the terminal's capabilities (emulator, size) and adapts its structural stylesheet accordingly (`complete`/`standard`/`reduced`/`mono`), without any manual flag — the same policy shared by the whole `omega-` suite (`omega-lib`, `terminal/policies.py`). Can be refreshed live with the `r` key.

### Profile by detected emulator

| Emulator | Initial profile |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modern SSH | `reduced` |
| Linux TTY, legacy SSH | `mono` |
| Unrecognised emulator | `reduced` (default fallback) |

### Profile by terminal size

| Minimum size (columns × lines) | Profile ceiling |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| below | `mono` |

The final profile is **the more restrictive of the two** (emulator and size).

## 6. Architecture

Clean Architecture (domain / application / infrastructure / interfaces), same convention as the rest of the OMEGA suite:

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

Depends on [`omega-lib`](../../../../LIB/omega-lib) for theming (10 TUI themes + 5 export themes), terminal detection and settings storage — the same foundation as the rest of the suite. Heavy computations (top IPs, access statistics) run in a dedicated `ProcessPoolExecutor` (`infrastructure/concurrency/`), never on the interface thread, to stay responsive even on a file of several hundred thousand lines.

## 7. Tests

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 tests
ruff check .
mypy src
```

Structure: `tests/unit/` (domain and application, no real I/O), `tests/integration/` (real files, headless TUI through Textual's `Pilot` API).

## 8. Development status

The 10 phases of the development plan are complete: foundation, domain, basic TUI, viewers, favorites/library/IPs, maintenance, statistics/export, finalisation, one-off sudo elevation, CPU-bound computations offloaded to a separate process — see `plan_omega_log.md` for the details of each porting decision. Since 1.6.0, the new features of the omega-serv 2.6.0 log manager have been carried over: Log health, scheduled backups, search for a specific IP, displayed version and update check.

## 9. License

MIT — see [LICENSE](../../../LICENSE).

---

> Omega-log — Detect, centralise, read, analyse, maintain.
> Your logs remain yours: no privilege elevation without a real need, no destructive action without confirmation.
