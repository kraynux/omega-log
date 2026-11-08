<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**Gestore e visualizzatore di log del server**

> Sviluppato da [kraynux](https://github.com/kraynux) per [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Pagina ufficiale: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/it/) &nbsp; Panoramica: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 Interfaccia, documentazione ed esportazioni disponibili in **17 lingue**.  
**Lingue:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** è lo strumento della suite `omega-` dedicato alla gestione, alla lettura e all'analisi dei file di log del server in TUI — rilevamento automatico dei servizi attivi e dei loro log, libreria centrale, tre modalità di lettura (monitoraggio semplice, lettura classica, unione di più file tramite `lnav`), gestione degli IP, statistiche, rotazione/backup/ripristino, eliminazione sicura ed esportazione. Costruito tramite **porting e adattamento** del codice già maturo di [omega-fire](https://github.com/kraynux) e [omega-serv](https://github.com/kraynux) invece di essere riscritto da zero.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/it/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/it/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/it/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/it/omega-log/D.png" width="24%" />
</p>

## 1. Visione e ambito

Omega-log risponde a una domanda semplice: «cosa succede nei miei log, e come me ne occupo?» — senza dipendere da un elenco fisso di percorsi noti, senza mai girare come root per impostazione predefinita e senza mai perdere o corrompere silenziosamente un file di log reale.

### Cosa fa Omega-log

- Rileva automaticamente i servizi attivi sulla macchina (server web, database, posta, DNS, sicurezza, `omega-serv`...) e propone l'importazione dei loro log noti, singolarmente o tutti insieme — in aggiunta a una scansione manuale di qualsiasi cartella.
- Centralizza i log da gestire in un'unica Libreria, punto di accesso di tutte le altre schermate.
- Legge un log in tre modalità a seconda delle esigenze: monitoraggio semplice con parsing e statistiche, lettura classica grezza con monitoraggio in tempo reale, oppure unione di più file incapsulando `lnav`.
- Memorizza combinazioni di log + visualizzatore come Preferiti, per un avvio diretto.
- Calcola la top 10 degli IP per periodo, o cerca un IP preciso, e ne consente la rimozione mirata in uno o più file.
- Calcola statistiche di accesso (volume, IP unici, tasso di errore, distribuzione oraria) esportabili in JSON o HTML con tema.
- Esegue il backup (compressione + conservazione automatica), a mano o ogni notte tramite i backup pianificati, ripristina (unione o sovrascrittura, con backup di sicurezza) ed elimina (troncamento sul posto o cancellazione) i file di log, sempre con conferma esplicita.
- Controlla la salute dei log (permessi, log muti o danneggiati, spazio su disco, backup) e indica cosa fare per ogni rilievo.
- Si adatta automaticamente alle capacità del terminale (colori, dimensioni) tramite `omega-lib`, come il resto della suite.

### Cosa non fa Omega-log

| Funzione | Strumento responsabile |
|---|---|
| Firewall, regole di rete, rilevamento delle intrusioni | OMEGA-FIRE |
| Server web, reverse proxy, WAF, Active Defense | OMEGA-SERV |
| Scansione delle porte, identificazione dei servizi di rete | OMEGA-CHECK |
| Osservazione di rete, identità digitale di un obiettivo | OMEGA-TRACK |

Non c'è (ancora) una CLI alla pari con la TUI (l'attuale modalità a riga di comando copre solo la scansione dei servizi, vedi §3.2), né aggregazione centralizzata di più macchine, né avvisi in tempo reale su soglia — Omega-log resta uno strumento di ispezione e manutenzione locale, non un SIEM.

### Avvertenza d'uso

Le azioni di manutenzione (**Elimina**, **Rotate → Ripristina in modalità Sovrascrittura**) modificano o cancellano definitivamente il contenuto reale dei tuoi file di log — sempre precedute da una conferma esplicita che elenca i file interessati, mai avviate automaticamente. In caso di dubbio, esegui un backup (**Rotate → Esegui backup ora**) prima di agire.

## 2. Installazione

### Prerequisiti

- Python 3.10+
- Linux (testato su Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` installato sul sistema, solo per il visualizzatore di unione di più file (gli altri due visualizzatori funzionano normalmente senza):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Installazione

```bash
[ -d omega-log ] && echo "ℹ️ Già estratto qui, passaggio ignorato." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Crea l'ambiente virtuale `.venv` se non esiste già.
2. Installa le dipendenze (prima `omega-lib` incluso, se presente, poi `pip install -e .` — `pyproject.toml` resta l'unica fonte di verità).
3. Rende eseguibili `omega-log.sh` e `install.sh`.
4. Verifica la presenza di `lnav` (avviso informativo se assente, mai bloccante).
5. Aggiunge l'alias `log` a `~/.bashrc` e `~/.zshrc` (senza duplicati se già presente).

### Dipendenze

Dichiarate in `pyproject.toml` (nessun `requirements.txt` separato):
- `omega-lib`: libreria condivisa della suite (temi TUI + esportazione, rilevamento del terminale, salvataggio delle impostazioni)
- `textual`: interfaccia TUI
- `jinja2`: esportazione HTML con tema (statistiche, archivi)
- `pyte`: emulazione di terminale per il visualizzatore `lnav` (rendering in un pty incapsulato)
- Dipendenze di sviluppo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Utilizzo

### 3.1. Modalità interattiva (TUI)

Consigliata per l'uso quotidiano — avviata senza argomenti:

```bash
./omega-log.sh
```
se hai creato l'alias, digita semplicemente `log` in un nuovo terminale:
```bash
log
```

Percorso generale: schermata di avvio → menu principale (due colonne — Registro delle capacità/Libreria/Vedi i log/Preferiti/Vedi e gestisci IP/Statistiche (accesso) da un lato, Rotate/Elimina/Esporta/Salute dei log/Opzioni/Aiuto dall'altro) → schermata della funzione scelta → ritorno al menu (`Esc`). La guida completa (`a`) descrive in dettaglio ogni schermata, ogni visualizzatore e i concetti trasversali (elevazione sudo puntuale, stati dei log, selezione per numeri) — vedi §4 per l'essenziale.

#### Scorciatoie da tastiera

| Tasto | Azione |
|---|---|
| `↑` / `↓` | Spostarsi tra gli elementi di una schermata |
| `Tab` / `Maiusc+Tab` | Spostarsi tra i campi di un modulo |
| `Esc` | Tornare alla schermata precedente (conferma di uscita dalla home) |
| `t` | Tema successivo (applicato subito, senza conferma) |
| `r` | Aggiornare il rilevamento del terminale |
| `a` | Mostrare la guida (completa, un capitolo per schermata) |
| `q` | Uscire (con conferma) |

### 3.2. Modalità a riga di comando (CLI)

Non ancora alla pari con la TUI (preferiti, eliminazione... arriveranno con le loro fasi, vedi `plan_omega_log.md` §12):

```bash
# Rileva i servizi attivi e i loro log noti
python -m omega_log scan

# + scansione manuale di una cartella aggiuntiva
python -m omega_log scan --path /var/log

# Versione installata, e confronto con l'ultima versione pubblicata
python -m omega_log version --check

# Backup pianificati giunti a scadenza (avviato ogni notte dal timer systemd o dalla crontab)
python -m omega_log rotate run-automations
```

### 3.3. Variabili d'ambiente

| Variabile | Effetto |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Cambia la posizione della cartella di stato dell'applicazione (`./var` per impostazione predefinita, relativa alla cartella di avvio) |
| `OMEGA_LOG_LANG` | Forza la lingua dell'interfaccia per la sessione (es. `en`, `de`, `ja`) senza modificare l'impostazione salvata |

## 4. Funzionalità

| Schermata | Descrizione |
|---|---|
| **Registro delle capacità** | Rileva i servizi attivi sulla macchina e propone l'importazione dei loro log noti, singolarmente o tutti insieme. Scansione manuale di una cartella in aggiunta. |
| **Libreria** | Hub centrale che raccoglie tutti i log da gestire — alimentata dal Registro, dall'importazione manuale, dai log noti di Omega-Serv o da una copia recuperata via SSH. |
| **Vedi i log** | Selezione di uno o più log della Libreria + scelta del visualizzatore (1 log → i 3 visualizzatori; 2+ log → solo `lnav`). |
| **Preferiti** | Combinazioni di log + visualizzatore salvate con un nome, per un avvio diretto. |
| **Vedi e gestisci IP** | Top 10 degli IP per periodo (24h/7g/30g/tutto), o ricerca di un IP preciso (IPv4 o IPv6), e rimozione mirata di un IP da uno o più log. |
| **Statistiche (accesso)** | Volume, IP unici, tasso di errore, top IP, distribuzione oraria — esportazione JSON/HTML con 5 temi. |
| **Rotate** | Backup compresso di un log + conservazione automatica degli archivi in eccesso + ripristino (unione o sovrascrittura, con backup di sicurezza). **Backup pianificati**: un log salvato ogni giorno, settimana o mese, eseguito ogni notte da un timer systemd o da una riga della tua crontab (OpenRC, runit), con il tuo account, mai come root. |
| **Elimina** | Svuota il contenuto di un log (troncamento sul posto, sicuro per un servizio che lo tiene ancora aperto) o cancella completamente uno o più file — sempre con conferma. |
| **Esporta** | Esportazione dell'elenco degli archivi (Rotate) in JSON o HTML con tema. |
| **Salute dei log** | Controllo in sola lettura dei log della Libreria, del disco, dei backup e dei backup pianificati: permessi, log muti o danneggiati, date, logrotate, giorni prima che il disco sia pieno, con l'azione da compiere. Correzione dei permessi troppo aperti (con sudo se necessario), esportazione JSON/HTML/TXT. |
| **Opzioni** | Tema, profilo di rendering, lingua dell'interfaccia e lingua delle esportazioni (17 lingue), svuotamento delle cartelle dell'applicazione (exports/screenshots). |

### I 3 visualizzatori

1. **Semplice** — monitoraggio in tempo reale con parsing generico (data e ora, IP, livello, servizio) e mini-tabella di statistiche. Per un access log HTTP riconosciuto, colonne aggiuntive Codice HTTP / latenza, colorate in base a soglie.
2. **Classico** — lettura delle ultime righe grezze + interruttore «Segui in tempo reale», senza parsing: il più semplice e il più affidabile, qualunque sia il formato.
3. **lnav** — unione di più file in un terminale incapsulato (pty), per un'analisi incrociata. Ciclo dei temi (`t`), selezione + copia negli appunti (`Ctrl+C`, OSC 52), uscita (`Ctrl+Q`) — tutti intercettati prima di `lnav` stesso.

## 5. Compatibilità dei terminali

La TUI (Textual) rileva automaticamente le capacità del terminale (emulatore, dimensioni) e adatta di conseguenza il proprio foglio di stile strutturale (`complete`/`standard`/`reduced`/`mono`), senza flag manuali — la stessa politica condivisa da tutta la suite `omega-` (`omega-lib`, `terminal/policies.py`). Aggiornabile in tempo reale con il tasto `r`.

### Profilo in base all'emulatore rilevato

| Emulatore | Profilo iniziale |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH legacy | `mono` |
| Emulatore non riconosciuto | `reduced` (ripiego predefinito) |

### Profilo in base alle dimensioni del terminale

| Dimensione minima (colonne × righe) | Tetto del profilo |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| al di sotto | `mono` |

Il profilo finale adottato è **il più restrittivo dei due** (emulatore e dimensioni).

## 6. Architettura

Clean Architecture (dominio / applicazione / infrastruttura / interfacce), la stessa convenzione del resto della suite OMEGA:

```text
src/omega_log/
├── core/            Registro delle capacita (rilevamento dei servizi)
├── domain/          Logica di business pura (parsing, statistiche, rotazione, eliminazione)
├── ports/           Contratti (Protocol)
├── application/     Casi d'uso
├── infrastructure/  Implementazioni reali (probes, salvataggio, archivi, esportazione, lnav, concorrenza)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

Dipende da [`omega-lib`](../../../../LIB/omega-lib) per il tema (10 temi TUI + 5 temi di esportazione), il rilevamento del terminale e il salvataggio delle impostazioni — la stessa base del resto della suite. I calcoli pesanti (top IP, statistiche di accesso) vengono eseguiti in un `ProcessPoolExecutor` dedicato (`infrastructure/concurrency/`), mai sul thread dell'interfaccia, per restare reattiva anche su un file di diverse centinaia di migliaia di righe.

## 7. Test

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 test
ruff check .
mypy src
```

Struttura: `tests/unit/` (dominio e applicazione, senza I/O reale), `tests/integration/` (file reali, TUI headless tramite l'API `Pilot` di Textual).

## 8. Stato dello sviluppo

Le 10 fasi del piano di sviluppo sono completate: base, dominio, TUI di base, visualizzatori, preferiti/libreria/IP, manutenzione, statistiche/esportazione, finalizzazione, elevazione sudo puntuale, calcoli CPU-bound spostati in un processo separato — vedi `plan_omega_log.md` per il dettaglio di ogni decisione di porting. Dalla 1.6.0 sono state riprese le novità del gestore di log di omega-serv 2.6.0: Salute dei log, backup pianificati, ricerca di un IP preciso, versione visualizzata e verifica degli aggiornamenti.

## 9. Licenza

MIT — vedi [LICENSE](../../../LICENSE).

---

> Omega-log — Rilevare, centralizzare, leggere, analizzare, mantenere.
> I tuoi log restano tuoi: nessuna elevazione di privilegi senza reale necessità, nessuna azione distruttiva senza conferma.
