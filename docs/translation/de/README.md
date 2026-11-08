<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**Verwaltung und Anzeige von Server-Logs**

> Entwickelt von [kraynux](https://github.com/kraynux) für [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Offizielle Seite: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/de/) &nbsp; Vorschau: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 Oberfläche, Dokumentation und Exporte in **17 Sprachen** verfügbar.  
**Sprachen:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** ist das Werkzeug der `omega-`-Suite für die Verwaltung, das Lesen und die Analyse von Server-Logdateien in einer TUI — automatische Erkennung aktiver Dienste und ihrer Logs, zentrale Bibliothek, drei Lesemodi (einfaches Verfolgen, klassisches Lesen, Zusammenführen mehrerer Dateien über `lnav`), IP-Bearbeitung, Statistiken, Rotation/Sicherung/Wiederherstellung, sichere Bereinigung und Export. Entstanden durch **Portierung und Anpassung** des bereits ausgereiften Codes von [omega-fire](https://github.com/kraynux) und [omega-serv](https://github.com/kraynux), statt von Grund auf neu geschrieben.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-log/D.png" width="24%" />
</p>

## 1. Vision und Umfang

Omega-log beantwortet eine einfache Frage: „Was passiert in meinen Logs, und wie kümmere ich mich darum?“ — ohne von einer festen Liste bekannter Pfade abzuhängen, ohne jemals standardmäßig als root zu laufen und ohne jemals eine echte Logdatei stillschweigend zu verlieren oder zu beschädigen.

### Was Omega-log tut

- Erkennt automatisch die auf dem Rechner aktiven Dienste (Webserver, Datenbanken, Mail, DNS, Sicherheit, `omega-serv`...) und bietet den Import ihrer bekannten Logs an, einzeln oder vollständig — ergänzend zu einem manuellen Scan eines beliebigen Ordners.
- Bündelt die zu bearbeitenden Logs in einer einzigen Bibliothek, dem Einstiegspunkt aller anderen Bildschirme.
- Liest ein Log je nach Bedarf in drei Modi: einfaches Verfolgen mit Parsing und Statistiken, klassisches Rohlesen mit Live-Verfolgung oder Zusammenführen mehrerer Dateien mit eingebettetem `lnav`.
- Speichert Kombinationen aus Logs + Viewer als Favoriten für den Direktstart.
- Berechnet die Top 10 der IPs pro Zeitraum oder sucht eine bestimmte IP und ermöglicht deren gezielte Entfernung aus einer oder mehreren Dateien.
- Berechnet Zugriffsstatistiken (Volumen, eindeutige IPs, Fehlerquote, stündliche Verteilung), exportierbar als JSON oder HTML mit Theme.
- Sichert (Kompression + automatische Aufbewahrung) von Hand oder jede Nacht über geplante Backups, stellt wieder her (Zusammenführen oder Überschreiben, mit Sicherheitskopie) und bereinigt (Kürzen an Ort und Stelle oder Löschen) die Logdateien, immer mit ausdrücklicher Bestätigung.
- Prüft den Zustand der Logs (Rechte, stumme oder beschädigte Logs, Speicherplatz, Sicherungen) und sagt zu jedem Befund, was zu tun ist.
- Passt sich über `omega-lib` automatisch an die Fähigkeiten des Terminals an (Farben, Größe), wie der Rest der Suite.

### Was Omega-log nicht tut

| Funktion | Zuständiges Werkzeug |
|---|---|
| Firewall, Netzwerkregeln, Einbruchserkennung | OMEGA-FIRE |
| Webserver, Reverse Proxy, WAF, Active Defense | OMEGA-SERV |
| Port-Scan, Identifizierung von Netzwerkdiensten | OMEGA-CHECK |
| Netzwerkbeobachtung, digitale Identität eines Ziels | OMEGA-TRACK |

(Noch) keine CLI mit vollständiger Parität zur TUI (der aktuelle Kommandozeilenmodus deckt nur den Dienst-Scan ab, siehe §3.2), keine zentrale Aggregation über mehrere Rechner, keine Echtzeit-Alarmierung bei Schwellwerten — Omega-log bleibt ein Werkzeug zur lokalen Inspektion und Wartung, kein SIEM.

### Nutzungshinweis

Die Wartungsaktionen (**Bereinigen**, **Rotate → Wiederherstellen im Modus Überschreiben**) ändern oder löschen den tatsächlichen Inhalt Ihrer Logdateien endgültig — stets nach einer ausdrücklichen Bestätigung mit den betroffenen Dateien, niemals automatisch ausgelöst. Im Zweifel vorher sichern (**Rotate → Jetzt sichern**).

## 2. Installation

### Voraussetzungen

- Python 3.10+
- Linux (getestet auf Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` auf dem System installiert, nur für den Viewer zum Zusammenführen mehrerer Dateien (die beiden anderen Viewer funktionieren auch ohne):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Installation

```bash
[ -d omega-log ] && echo "ℹ️ Hier bereits entpackt, Schritt übersprungen." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Erstellt die virtuelle Umgebung `.venv`, falls sie noch nicht existiert.
2. Installiert die Abhängigkeiten (zuerst das mitgelieferte `omega-lib`, falls vorhanden, dann `pip install -e .` — `pyproject.toml` bleibt die einzige maßgebliche Quelle).
3. Macht `omega-log.sh` und `install.sh` ausführbar.
4. Prüft, ob `lnav` vorhanden ist (informative Warnung, falls es fehlt, nie blockierend).
5. Fügt den Alias `log` zu `~/.bashrc` und `~/.zshrc` hinzu (ohne Duplikat, falls bereits vorhanden).

### Abhängigkeiten

Deklariert in `pyproject.toml` (keine separate `requirements.txt`):
- `omega-lib`: gemeinsame Bibliothek der Suite (TUI- und Export-Themes, Terminalerkennung, Speicherung der Einstellungen)
- `textual`: TUI-Oberfläche
- `jinja2`: HTML-Export mit Theme (Statistiken, Archive)
- `pyte`: Terminalemulation für den `lnav`-Viewer (Darstellung in einem eingebetteten pty)
- Entwicklungsabhängigkeiten (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Verwendung

### 3.1. Interaktiver Modus (TUI)

Empfohlen für den täglichen Gebrauch — ohne Argument gestartet:

```bash
./omega-log.sh
```
wenn Sie den Alias angelegt haben, tippen Sie in einem neuen Terminal einfach `log`:
```bash
log
```

Allgemeiner Ablauf: Startbildschirm → Hauptmenü (zwei Spalten — Fähigkeitsregister/Bibliothek/Logs ansehen/Favoriten/IP ansehen und bearbeiten/Statistiken auf der einen Seite, Rotate/Bereinigen/Exportieren/Log-Zustand/Optionen/Hilfe auf der anderen) → Bildschirm der gewählten Funktion → zurück zum Menü (`Esc`). Die vollständige Hilfe (`a`) beschreibt jeden Bildschirm, jeden Viewer und die übergreifenden Konzepte (punktuelle sudo-Rechteerhöhung, Zustände der Logs, Auswahl über Nummern) — das Wesentliche siehe §4.

#### Tastenkürzel

| Taste | Aktion |
|---|---|
| `↑` / `↓` | Zwischen den Elementen eines Bildschirms navigieren |
| `Tab` / `Umschalt+Tab` | Zwischen den Feldern eines Formulars navigieren |
| `Esc` | Zurück zum vorherigen Bildschirm (Beenden-Bestätigung auf dem Startbildschirm) |
| `t` | Nächstes Theme (sofort angewendet, ohne Bestätigung) |
| `r` | Terminalerkennung aktualisieren |
| `a` | Hilfe anzeigen (vollständig, ein Kapitel pro Bildschirm) |
| `q` | Beenden (mit Bestätigung) |

### 3.2. Kommandozeilenmodus (CLI)                                                              

Noch keine vollständige Parität mit der TUI (Favoriten, Bereinigung... folgen in eigenen Phasen, siehe `plan_omega_log.md` §12):

```bash
# Erkennt die aktiven Dienste und ihre bekannten Logs
python -m omega_log scan

# + manueller Scan eines zusätzlichen Ordners
python -m omega_log scan --path /var/log

# Installierte Version und Vergleich mit der zuletzt veröffentlichten Version
python -m omega_log version --check

# Fällige geplante Backups (jede Nacht vom systemd-Timer oder der crontab gestartet)
python -m omega_log rotate run-automations
```

### 3.3. Umgebungsvariablen

| Variable | Wirkung |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Ändert den Ort des Anwendungs-Zustandsordners (standardmäßig `./var`, relativ zum Startordner) |
| `OMEGA_LOG_LANG` | Erzwingt die Sprache der Oberfläche für die Sitzung (z. B. `en`, `de`, `ja`), ohne die gespeicherte Einstellung zu ändern |

## 4. Funktionen

| Bildschirm | Beschreibung |
|---|---|
| **Fähigkeitsregister** | Erkennt die auf dem Rechner aktiven Dienste und bietet den Import ihrer bekannten Logs an, einzeln oder vollständig. Ergänzend manueller Scan eines Ordners. |
| **Bibliothek** | Zentraler Hub, der alle zu bearbeitenden Logs referenziert — gespeist vom Register, durch manuellen Import, durch die bekannten Logs von Omega-Serv oder durch eine per SSH abgerufene Kopie. |
| **Logs ansehen** | Auswahl eines oder mehrerer Logs der Bibliothek + Wahl des Viewers (1 Log → alle 3 Viewer; 2+ Logs → nur `lnav`). |
| **Favoriten** | Unter einem Namen gespeicherte Kombinationen aus Logs + Viewer für den Direktstart. |
| **IP ansehen und bearbeiten** | Top 10 der IPs pro Zeitraum (24 h/7 T/30 T/alles) oder Suche nach einer bestimmten IP (IPv4 oder IPv6) und gezielte Entfernung einer IP aus einem oder mehreren Logs. |
| **Statistiken (Zugriff)** | Volumen, eindeutige IPs, Fehlerquote, Top-IPs, stündliche Verteilung — Export als JSON/HTML mit 5 Themes. |
| **Rotate** | Komprimierte Sicherung eines Logs + automatische Aufbewahrung überzähliger Archive + Wiederherstellung (Zusammenführen oder Überschreiben, mit Sicherheitskopie). **Geplante Backups**: ein Log wird täglich, wöchentlich oder monatlich gesichert, jede Nacht ausgeführt von einem systemd-Timer oder einer Zeile Ihrer crontab (OpenRC, runit), unter Ihrem Konto, nie als root. |
| **Bereinigen** | Leert den Inhalt eines Logs (Kürzen an Ort und Stelle, sicher für einen Dienst, der es noch geöffnet hat) oder löscht eine oder mehrere Dateien vollständig — immer mit Bestätigung. |
| **Exportieren** | Export der Archivliste (Rotate) als JSON oder HTML mit Theme. |
| **Log-Zustand** | Reine Leseprüfung der Logs der Bibliothek, des Datenträgers, der Sicherungen und der geplanten Backups: Rechte, stumme oder beschädigte Logs, Datumsangaben, logrotate, Tage bis zum vollen Datenträger, jeweils mit dem zu ergreifenden Schritt. Korrektur zu offener Rechte (bei Bedarf mit sudo), Export als JSON/HTML/TXT. |
| **Optionen** | Theme, Rendering-Profil, Sprache der Oberfläche und Sprache der Exporte (17 Sprachen), Leeren der Anwendungsordner (exports/screenshots). |

### Die 3 Viewer

1. **Einfach** — Live-Verfolgung mit generischem Parsing (Zeitstempel, IP, Level, Dienst) und kleiner Statistiktabelle. Bei einem erkannten HTTP-Access-Log zusätzliche Spalten HTTP-Code / Latenz, nach Schwellwert eingefärbt.
2. **Klassisch** — Lesen der letzten Rohzeilen + Umschalter „Live verfolgen“, ohne Parsing: am einfachsten und zuverlässigsten, unabhängig vom Format.
3. **lnav** — Zusammenführen mehrerer Dateien in einem eingebetteten Terminal (pty) für eine Kreuzanalyse. Theme-Wechsel (`t`), Markieren + Kopieren in die Zwischenablage (`Ctrl+C`, OSC 52), Beenden (`Ctrl+Q`) — alle abgefangen, bevor `lnav` selbst sie erhält.

## 5. Terminal-Kompatibilität

Die TUI (Textual) erkennt automatisch die Fähigkeiten des Terminals (Emulator, Größe) und passt ihr strukturelles Stylesheet entsprechend an (`complete`/`standard`/`reduced`/`mono`), ohne manuelles Flag — dieselbe Richtlinie für die gesamte `omega-`-Suite (`omega-lib`, `terminal/policies.py`). Live aktualisierbar mit der Taste `r`.

### Profil je nach erkanntem Emulator

| Emulator | Anfangsprofil |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modernes SSH | `reduced` |
| Linux-TTY, älteres SSH | `mono` |
| Nicht erkannter Emulator | `reduced` (Standard-Rückfall) |

### Profil je nach Terminalgröße

| Mindestgröße (Spalten × Zeilen) | Profil-Obergrenze |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| darunter | `mono` |

Das endgültig gewählte Profil ist **das restriktivere der beiden** (Emulator und Größe).

## 6. Architektur

Clean Architecture (Domäne / Anwendung / Infrastruktur / Schnittstellen), dieselbe Konvention wie der Rest der OMEGA-Suite:

```text
src/omega_log/
├── core/            Fähigkeitsregister (Erkennung von Diensten)
├── domain/          Reine Geschäftslogik (Parsing, Statistiken, Rotation, Bereinigung)
├── ports/           Verträge (Protocol)
├── application/     Anwendungsfälle
├── infrastructure/  Echte Implementierungen (Probes, Speicherung, Archive, Export, lnav, Nebenläufigkeit)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

Hängt von [`omega-lib`](../../../../LIB/omega-lib) ab für das Theme (10 TUI-Themes + 5 Export-Themes), die Terminalerkennung und die Speicherung der Einstellungen — dieselbe Basis wie der Rest der Suite. Die aufwendigen Berechnungen (Top-IPs, Zugriffsstatistiken) laufen in einem eigenen `ProcessPoolExecutor` (`infrastructure/concurrency/`), nie im Thread der Oberfläche, damit sie auch bei einer Datei mit mehreren hunderttausend Zeilen reaktionsfähig bleibt.

## 7. Tests

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 Tests
ruff check .
mypy src
```

Struktur: `tests/unit/` (Domäne und Anwendung, ohne echte I/O), `tests/integration/` (echte Dateien, headless TUI über die `Pilot`-API von Textual).

## 8. Entwicklungsstand

Die 10 Phasen des Entwicklungsplans sind abgeschlossen: Basis, Domäne, grundlegende TUI, Viewer, Favoriten/Bibliothek/IP, Wartung, Statistiken/Export, Fertigstellung, punktuelle sudo-Rechteerhöhung, in einen separaten Prozess ausgelagerte CPU-lastige Berechnungen — siehe `plan_omega_log.md` für die Einzelheiten jeder Portierungsentscheidung. Seit 1.6.0 sind die Neuerungen der Log-Verwaltung von omega-serv 2.6.0 übernommen: Log-Zustand, geplante Backups, Suche nach einer bestimmten IP, Versionsanzeige und Prüfung auf Aktualisierungen.

## 9. Lizenz

MIT — siehe [LICENSE](../../../LICENSE).

---

> Omega-log — Erkennen, bündeln, lesen, analysieren, pflegen.
> Ihre Logs bleiben Ihre: keine Rechteerhöhung ohne echte Notwendigkeit, keine zerstörende Aktion ohne Bestätigung.
