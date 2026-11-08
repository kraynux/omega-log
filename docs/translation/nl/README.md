<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**Beheer en weergave van serverlogs**

> Ontwikkeld door [kraynux](https://github.com/kraynux) voor [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Officiële pagina: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/nl/) &nbsp; Voorbeeld: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 Interface, documentatie en exports beschikbaar in **17 talen**.  
**Talen:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** is het hulpmiddel van de `omega-`-suite voor het beheren, lezen en analyseren van serverlogbestanden in een TUI — automatische detectie van actieve diensten en hun logs, centrale bibliotheek, drie leesmodi (eenvoudig volgen, klassiek lezen, samenvoegen van meerdere bestanden via `lnav`), IP-behandeling, statistieken, rotatie/back-up/herstel, veilig opschonen en export. Gebouwd door **overzetting en aanpassing** van de al volwassen code van [omega-fire](https://github.com/kraynux) en [omega-serv](https://github.com/kraynux), in plaats van vanaf nul herschreven.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/nl/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/nl/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/nl/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/nl/omega-log/D.png" width="24%" />
</p>

## 1. Visie en reikwijdte

Omega-log beantwoordt een eenvoudige vraag: "wat gebeurt er in mijn logs, en hoe ga ik ermee om?" — zonder afhankelijk te zijn van een vaste lijst bekende paden, zonder ooit standaard als root te draaien en zonder ooit stilzwijgend een echt logbestand te verliezen of te beschadigen.

### Wat Omega-log doet

- Detecteert automatisch de actieve diensten op de machine (webservers, databases, mail, DNS, beveiliging, `omega-serv`...) en biedt aan hun bekende logs te importeren, afzonderlijk of allemaal — als aanvulling op een handmatige scan van een willekeurige map.
- Centraliseert de te behandelen logs in één Bibliotheek, het startpunt van alle andere schermen.
- Leest een log in drie modi, naargelang de behoefte: eenvoudig volgen met parsing en statistieken, klassiek ruw lezen met live volgen, of samenvoegen van meerdere bestanden met een ingebedde `lnav`.
- Onthoudt combinaties van logs + viewer als Favorieten, om ze direct te starten.
- Berekent de top 10 van IP's per periode, of zoekt een specifiek IP, en maakt het gericht verwijderen ervan uit één of meerdere bestanden mogelijk.
- Berekent toegangsstatistieken (volume, unieke IP's, foutpercentage, verdeling per uur), exporteerbaar als JSON of HTML met thema.
- Maakt back-ups (compressie + automatische bewaring), handmatig of elke nacht via geplande back-ups, herstelt (samenvoegen of overschrijven, met veiligheidsback-up) en schoont logbestanden op (ter plaatse inkorten of verwijderen), altijd met uitdrukkelijke bevestiging.
- Controleert de gezondheid van de logs (rechten, stille of beschadigde logs, schijfruimte, back-ups) en zegt bij elke bevinding wat er te doen is.
- Past zich via `omega-lib` automatisch aan de mogelijkheden van de terminal aan (kleuren, grootte), zoals de rest van de suite.

### Wat Omega-log niet doet

| Functie | Verantwoordelijk hulpmiddel |
|---|---|
| Firewall, netwerkregels, inbraakdetectie | OMEGA-FIRE |
| Webserver, reverse proxy, WAF, Active Defense | OMEGA-SERV |
| Poortscan, identificatie van netwerkdiensten | OMEGA-CHECK |
| Netwerkobservatie, digitale identiteit van een doelwit | OMEGA-TRACK |

(Nog) geen CLI met volledige gelijkwaardigheid aan de TUI (de huidige opdrachtregelmodus dekt alleen de dienstscan, zie §3.2), geen centrale aggregatie over meerdere machines, geen realtime alarmering bij drempels — Omega-log blijft een hulpmiddel voor lokale inspectie en onderhoud, geen SIEM.

### Waarschuwing bij gebruik

De onderhoudsacties (**Opschonen**, **Rotate → Herstellen in de modus Overschrijven**) wijzigen of wissen de werkelijke inhoud van uw logbestanden definitief — altijd voorafgegaan door een uitdrukkelijke bevestiging met de betrokken bestanden, nooit automatisch gestart. Maak bij twijfel eerst een back-up (**Rotate → Nu back-uppen**).

## 2. Installatie

### Vereisten

- Python 3.10+
- Linux (getest op Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` op het systeem geïnstalleerd, alleen voor de viewer die meerdere bestanden samenvoegt (de twee andere viewers werken ook zonder):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Installatie

```bash
[ -d omega-log ] && echo "ℹ️ Hier al uitgepakt, stap overgeslagen." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Maakt de virtuele omgeving `.venv` aan als die nog niet bestaat.
2. Installeert de afhankelijkheden (eerst de meegeleverde `omega-lib` indien aanwezig, daarna `pip install -e .` — `pyproject.toml` blijft de enige bron van waarheid).
3. Maakt `omega-log.sh` en `install.sh` uitvoerbaar.
4. Controleert of `lnav` aanwezig is (informatieve waarschuwing als het ontbreekt, nooit blokkerend).
5. Voegt de alias `log` toe aan `~/.bashrc` en `~/.zshrc` (zonder dubbele regel als die al aanwezig is).

### Afhankelijkheden

Gedeclareerd in `pyproject.toml` (geen aparte `requirements.txt`):
- `omega-lib`: gedeelde bibliotheek van de suite (TUI- en exportthema's, terminaldetectie, opslag van instellingen)
- `textual`: TUI-interface
- `jinja2`: HTML-export met thema (statistieken, archieven)
- `pyte`: terminalemulatie voor de `lnav`-viewer (weergave in een ingebedde pty)
- Ontwikkelafhankelijkheden (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Gebruik

### 3.1. Interactieve modus (TUI)

Aanbevolen voor dagelijks gebruik — gestart zonder argument:

```bash
./omega-log.sh
```
als u de alias hebt aangemaakt, typ dan gewoon `log` in een nieuwe terminal:
```bash
log
```

Algemeen verloop: opstartscherm → hoofdmenu (twee kolommen — Capaciteitenregister/Bibliotheek/Logs bekijken/Favorieten/IP bekijken en behandelen/Statistieken aan de ene kant, Rotate/Opschonen/Exporteren/Loggezondheid/Opties/Help aan de andere) → scherm van de gekozen functie → terug naar het menu (`Esc`). De volledige help (`a`) beschrijft elk scherm, elke viewer en de overkoepelende begrippen (eenmalige sudo-verhoging, toestanden van de logs, selectie via nummers) — zie §4 voor de hoofdzaken.

#### Sneltoetsen

| Toets | Actie |
|---|---|
| `↑` / `↓` | Navigeren tussen de elementen van een scherm |
| `Tab` / `Shift+Tab` | Navigeren tussen de velden van een formulier |
| `Esc` | Terug naar het vorige scherm (bevestiging van afsluiten op het startscherm) |
| `t` | Volgend thema (direct toegepast, zonder bevestiging) |
| `r` | Terminaldetectie vernieuwen |
| `a` | Help tonen (volledig, één hoofdstuk per scherm) |
| `q` | Afsluiten (met bevestiging) |

### 3.2. Opdrachtregelmodus (CLI)                                                              

Nog geen volledige gelijkwaardigheid met de TUI (favorieten, opschonen... volgen in hun eigen fasen, zie `plan_omega_log.md` §12):

```bash
# Detecteert de actieve diensten en hun bekende logs
python -m omega_log scan

# + handmatige scan van een extra map
python -m omega_log scan --path /var/log

# Geïnstalleerde versie, en vergelijking met de laatst gepubliceerde versie
python -m omega_log version --check

# Geplande back-ups die aan de beurt zijn (elke nacht gestart door de systemd-timer of de crontab)
python -m omega_log rotate run-automations
```

### 3.3. Omgevingsvariabelen

| Variabele | Effect |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Wijzigt de locatie van de map met de toepassingsstatus (standaard `./var`, relatief aan de startmap) |
| `OMEGA_LOG_LANG` | Dwingt de taal van de interface af voor de sessie (bv. `en`, `de`, `ja`) zonder de opgeslagen instelling te wijzigen |

## 4. Functies

| Scherm | Beschrijving |
|---|---|
| **Capaciteitenregister** | Detecteert de actieve diensten op de machine en biedt aan hun bekende logs te importeren, afzonderlijk of allemaal. Aanvullend handmatige scan van een map. |
| **Bibliotheek** | Centrale hub die alle te behandelen logs verwijst — gevoed door het Register, door handmatige import, door de bekende logs van Omega-Serv of door een via SSH opgehaalde kopie. |
| **Logs bekijken** | Selectie van één of meerdere logs uit de Bibliotheek + keuze van de viewer (1 log → de 3 viewers; 2+ logs → alleen `lnav`). |
| **Favorieten** | Combinaties van logs + viewer opgeslagen onder een naam, om ze direct te starten. |
| **IP bekijken en behandelen** | Top 10 van IP's per periode (24 u/7 d/30 d/alles), of zoeken naar een specifiek IP (IPv4 of IPv6), en gericht verwijderen van een IP uit één of meerdere logs. |
| **Statistieken (toegang)** | Volume, unieke IP's, foutpercentage, top-IP's, verdeling per uur — export als JSON/HTML met 5 thema's. |
| **Rotate** | Gecomprimeerde back-up van een log + automatische bewaring van overtollige archieven + herstel (samenvoegen of overschrijven, met veiligheidsback-up). **Geplande back-ups**: een log dat elke dag, week of maand wordt geback-upt, elke nacht uitgevoerd door een systemd-timer of een regel in uw crontab (OpenRC, runit), onder uw account, nooit als root. |
| **Opschonen** | Maakt de inhoud van een log leeg (ter plaatse inkorten, veilig voor een dienst die het nog open heeft) of verwijdert één of meerdere bestanden volledig — altijd met bevestiging. |
| **Exporteren** | Export van de lijst met archieven (Rotate) als JSON of HTML met thema. |
| **Loggezondheid** | Alleen-lezen controle van de logs in de Bibliotheek, de schijf, de back-ups en de geplande back-ups: rechten, stille of beschadigde logs, datums, logrotate, dagen tot de schijf vol is, met de te nemen stap. Correctie van te ruime rechten (met sudo indien nodig), export als JSON/HTML/TXT. |
| **Opties** | Thema, weergaveprofiel, taal van de interface en taal van de exports (17 talen), opschonen van de toepassingsmappen (exports/screenshots). |

### De 3 viewers

1. **Eenvoudig** — live volgen met generieke parsing (tijdstempel, IP, niveau, dienst) en een kleine statistiektabel. Voor een herkend HTTP-toegangslog extra kolommen HTTP-code / latentie, gekleurd per drempel.
2. **Klassiek** — lezen van de laatste ruwe regels + schakelaar "Live volgen", zonder parsing: het eenvoudigst en het betrouwbaarst, ongeacht het formaat.
3. **lnav** — samenvoegen van meerdere bestanden in een ingebedde terminal (pty), voor een kruisanalyse. Themawissel (`t`), markeren + kopiëren naar het klembord (`Ctrl+C`, OSC 52), afsluiten (`Ctrl+Q`) — allemaal onderschept voordat `lnav` zelf ze krijgt.

## 5. Terminalcompatibiliteit

De TUI (Textual) detecteert automatisch de mogelijkheden van de terminal (emulator, grootte) en past zijn structurele stylesheet daarop aan (`complete`/`standard`/`reduced`/`mono`), zonder handmatige vlag — hetzelfde beleid voor de hele `omega-`-suite (`omega-lib`, `terminal/policies.py`). Live te vernieuwen met de toets `r`.

### Profiel volgens de gedetecteerde emulator

| Emulator | Beginprofiel |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, moderne SSH | `reduced` |
| Linux-TTY, oudere SSH | `mono` |
| Niet-herkende emulator | `reduced` (standaardterugval) |

### Profiel volgens de grootte van de terminal

| Minimale grootte (kolommen × regels) | Profielplafond |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| kleiner | `mono` |

Het uiteindelijk gekozen profiel is **het meest beperkende van de twee** (emulator en grootte).

## 6. Architectuur

Clean Architecture (domein / toepassing / infrastructuur / interfaces), dezelfde conventie als de rest van de OMEGA-suite:

```text
src/omega_log/
├── core/            Capaciteitenregister (detectie van diensten)
├── domain/          Pure bedrijfslogica (parsing, statistieken, rotatie, opschonen)
├── ports/           Contracten (Protocol)
├── application/     Use-cases
├── infrastructure/  Echte implementaties (probes, opslag, archieven, export, lnav, gelijktijdigheid)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

Hangt af van [`omega-lib`](../../../../LIB/omega-lib) voor het thema (10 TUI-thema's + 5 exportthema's), de terminaldetectie en de opslag van instellingen — dezelfde basis als de rest van de suite. De zware berekeningen (top-IP's, toegangsstatistieken) draaien in een eigen `ProcessPoolExecutor` (`infrastructure/concurrency/`), nooit op de interfacethread, zodat alles reactief blijft, zelfs bij een bestand van honderdduizenden regels.

## 7. Tests

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 tests
ruff check .
mypy src
```

Structuur: `tests/unit/` (domein en toepassing, zonder echte I/O), `tests/integration/` (echte bestanden, headless TUI via de `Pilot`-API van Textual).

## 8. Stand van de ontwikkeling

De 10 fasen van het ontwikkelplan zijn afgerond: basis, domein, basis-TUI, viewers, favorieten/bibliotheek/IP, onderhoud, statistieken/export, afwerking, eenmalige sudo-verhoging, CPU-intensieve berekeningen uitbesteed aan een apart proces — zie `plan_omega_log.md` voor de details van elke overzettingsbeslissing. Sinds 1.6.0 zijn de nieuwigheden van het logbeheer van omega-serv 2.6.0 overgenomen: Loggezondheid, geplande back-ups, zoeken naar een specifiek IP, weergave van de versie en controle op updates.

## 9. Licentie

MIT — zie [LICENSE](../../../LICENSE).

---

> Omega-log — Detecteren, centraliseren, lezen, analyseren, onderhouden.
> Uw logs blijven van u: geen verhoging van rechten zonder echte noodzaak, geen destructieve actie zonder bevestiging.
