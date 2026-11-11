<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="512">
</div>

# 📜 OMEGA-LOG

**Menedżer i przeglądarka logów serwera**

> Stworzony przez [kraynux](https://github.com/kraynux) dla [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Strona oficjalna: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/pl/) &nbsp; Podgląd: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 Interfejs, dokumentacja i eksporty dostępne w **17 językach**.  
**Języki:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** to narzędzie z pakietu `omega-` przeznaczone do zarządzania plikami logów serwera, ich odczytu i analizy w TUI — automatyczne wykrywanie aktywnych usług i ich logów, centralna biblioteka, trzy tryby odczytu (proste śledzenie, klasyczny odczyt, scalanie wielu plików przez `lnav`), obsługa adresów IP, statystyki, rotacja/kopia zapasowa/przywracanie, bezpieczne czyszczenie i eksport. Zbudowany przez **przeniesienie i dostosowanie** dojrzałego już kodu [omega-fire](https://github.com/kraynux) i [omega-serv](https://github.com/kraynux) zamiast pisania go od zera.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pl/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pl/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pl/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pl/omega-log/D.png" width="24%" />
</p>

## 1. Wizja i zakres

Omega-log odpowiada na proste pytanie: „co dzieje się w moich logach i jak mam się nimi zająć?” — bez polegania na sztywnej liście znanych ścieżek, bez domyślnego działania jako root i bez cichej utraty czy uszkodzenia prawdziwego pliku logu.

### Co robi Omega-log

- Automatycznie wykrywa aktywne usługi na maszynie (serwery WWW, bazy danych, poczta, DNS, bezpieczeństwo, `omega-serv`...) i proponuje import ich znanych logów, pojedynczo lub wszystkich naraz — jako uzupełnienie ręcznego skanowania dowolnego katalogu.
- Gromadzi logi do obsługi w jednej Bibliotece, punkcie wejścia do wszystkich pozostałych ekranów.
- Odczytuje log w jednym z trzech trybów, zależnie od potrzeby: proste śledzenie z parsowaniem i statystykami, klasyczny surowy odczyt ze śledzeniem na żywo lub scalanie wielu plików z osadzonym `lnav`.
- Zapamiętuje zestawy logi + przeglądarka jako Ulubione, do bezpośredniego uruchamiania.
- Wylicza top 10 adresów IP w danym okresie albo wyszukuje konkretny adres IP i pozwala go usunąć z jednego lub kilku plików.
- Wylicza statystyki dostępu (wolumen, unikalne IP, odsetek błędów, rozkład godzinowy), które można eksportować do JSON lub HTML z motywem.
- Tworzy kopie zapasowe (kompresja + automatyczna retencja), ręcznie lub co noc w ramach zaplanowanych kopii zapasowych, przywraca (scalenie lub nadpisanie, z kopią bezpieczeństwa) i czyści (obcięcie w miejscu lub usunięcie) pliki logów, zawsze z wyraźnym potwierdzeniem.
- Sprawdza kondycję logów (uprawnienia, logi milczące lub uszkodzone, miejsce na dysku, kopie zapasowe) i dla każdego ustalenia mówi, co zrobić.
- Automatycznie dostosowuje się do możliwości terminala (kolory, rozmiar) przez `omega-lib`, jak reszta pakietu.

### Czego Omega-log nie robi

| Funkcja | Odpowiedzialne narzędzie |
|---|---|
| Zapora sieciowa, reguły sieciowe, wykrywanie włamań | OMEGA-FIRE |
| Serwer WWW, reverse proxy, WAF, Active Defense | OMEGA-SERV |
| Skanowanie portów, identyfikacja usług sieciowych | OMEGA-CHECK |
| Obserwacja sieci, tożsamość cyfrowa celu | OMEGA-TRACK |

Brak (na razie) CLI o pełnej zgodności z TUI (obecny tryb wiersza poleceń obejmuje tylko skanowanie usług, zob. §3.2), brak centralnej agregacji z wielu maszyn, brak alertów w czasie rzeczywistym po przekroczeniu progu — Omega-log pozostaje narzędziem do lokalnej inspekcji i utrzymania, a nie systemem SIEM.

### Ostrzeżenie dotyczące użycia

Działania konserwacyjne (**Wyczyść**, **Rotate → Przywróć w trybie Nadpisanie**) trwale zmieniają lub usuwają rzeczywistą zawartość plików logów — zawsze poprzedza je wyraźne potwierdzenie z listą plików, których dotyczą, i nigdy nie są uruchamiane automatycznie. W razie wątpliwości najpierw utwórz kopię (**Rotate → Utwórz kopię teraz**).

## 2. Instalacja

### Wymagania

- Python 3.10+
- Linux (testowany na Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` zainstalowany w systemie, wyłącznie dla przeglądarki scalającej wiele plików (dwie pozostałe przeglądarki działają bez niego):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Instalacja

```bash
[ -d omega-log ] && echo "ℹ️ Już tu rozpakowane, krok pominięty." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Tworzy środowisko wirtualne `.venv`, jeśli jeszcze nie istnieje.
2. Instaluje zależności (najpierw dołączoną `omega-lib`, jeśli jest obecna, potem `pip install -e .` — `pyproject.toml` pozostaje jedynym źródłem prawdy).
3. Nadaje `omega-log.sh` i `install.sh` prawo wykonywania.
4. Sprawdza obecność `lnav` (ostrzeżenie informacyjne w razie braku, nigdy blokujące).
5. Dodaje alias `log` do `~/.bashrc` i `~/.zshrc` (bez duplikatu, jeśli już istnieje).

### Zależności

Zadeklarowane w `pyproject.toml` (bez osobnego `requirements.txt`):
- `omega-lib`: wspólna biblioteka pakietu (motywy TUI + eksportu, wykrywanie terminala, przechowywanie ustawień)
- `textual`: interfejs TUI
- `jinja2`: eksport HTML z motywem (statystyki, archiwa)
- `pyte`: emulacja terminala dla przeglądarki `lnav` (renderowanie w osadzonym pty)
- Zależności deweloperskie (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Użycie

### 3.1. Tryb interaktywny (TUI)

Zalecany do codziennej pracy — uruchamiany bez argumentów:

```bash
./omega-log.sh
```
jeśli utworzono alias, wpisz po prostu `log` w nowym terminalu:
```bash
log
```

Ogólny przebieg: ekran startowy → menu główne (dwie kolumny — Rejestr możliwości/Biblioteka/Podgląd logów/Ulubione/Podgląd i obsługa IP/Statystyki (dostęp) po jednej stronie, Rotate/Wyczyść/Eksportuj/Kondycja logów/Opcje/Pomoc po drugiej) → ekran wybranej funkcji → powrót do menu (`Esc`). Pełna pomoc (`a`) opisuje szczegółowo każdy ekran, każdą przeglądarkę i pojęcia przekrojowe (jednorazowe podniesienie uprawnień przez sudo, stany logów, wybór po numerach) — najważniejsze informacje w §4.

#### Skróty klawiszowe

| Klawisz | Działanie |
|---|---|
| `↑` / `↓` | Poruszanie się między elementami ekranu |
| `Tab` / `Shift+Tab` | Poruszanie się między polami formularza |
| `Esc` | Powrót do poprzedniego ekranu (na ekranie głównym potwierdzenie wyjścia) |
| `t` | Następny motyw (stosowany natychmiast, bez potwierdzenia) |
| `r` | Odświeżenie wykrywania terminala |
| `a` | Wyświetlenie pomocy (wyczerpującej, jeden rozdział na ekran) |
| `q` | Wyjście (z potwierdzeniem) |

### 3.2. Tryb wiersza poleceń (CLI)                                                              

Na razie bez pełnej zgodności z TUI (ulubione, czyszczenie... pojawią się w swoich własnych fazach, zob. `plan_omega_log.md` §12):

```bash
# Wykrywa aktywne usługi i ich znane logi
python -m omega_log scan

# + ręczne skanowanie dodatkowego katalogu
python -m omega_log scan --path /var/log

# Zainstalowana wersja i porównanie z najnowszą opublikowaną wersją
python -m omega_log version --check

# Zaplanowane kopie zapasowe, których termin nadszedł (uruchamiane co noc przez timer systemd lub crontab)
python -m omega_log rotate run-automations
```

### 3.3. Zmienne środowiskowe

| Zmienna | Efekt |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Zmienia położenie katalogu stanu aplikacji (domyślnie `./var`, względem katalogu uruchomienia) |
| `OMEGA_LOG_LANG` | Wymusza język interfejsu na czas sesji (np. `en`, `de`, `ja`) bez zmiany zapisanego ustawienia |

## 4. Funkcje

| Ekran | Opis |
|---|---|
| **Rejestr możliwości** | Wykrywa aktywne usługi na maszynie i proponuje import ich znanych logów, pojedynczo lub wszystkich naraz. Uzupełniająco ręczne skanowanie katalogu. |
| **Biblioteka** | Centralny hub z odwołaniami do wszystkich logów do obsługi — zasilany przez Rejestr, ręczny import, znane logi Omega-Serv lub kopię pobraną przez SSH. |
| **Podgląd logów** | Wybór jednego lub kilku logów z Biblioteki + wybór przeglądarki (1 log → 3 przeglądarki; 2+ logi → tylko `lnav`). |
| **Ulubione** | Zestawy logi + przeglądarka zapisane pod nazwą, do bezpośredniego uruchamiania. |
| **Podgląd i obsługa IP** | Top 10 adresów IP w danym okresie (24h/7d/30d/wszystko) lub wyszukiwanie konkretnego adresu IP (IPv4 lub IPv6) i ukierunkowane usunięcie adresu IP z jednego lub kilku logów. |
| **Statystyki (dostęp)** | Wolumen, unikalne IP, odsetek błędów, top IP, rozkład godzinowy — eksport JSON/HTML z 5 motywami. |
| **Rotate** | Skompresowana kopia zapasowa logu + automatyczna retencja nadmiarowych archiwów + przywracanie (scalenie lub nadpisanie, z kopią bezpieczeństwa). **Zaplanowane kopie zapasowe**: log kopiowany codziennie, co tydzień lub co miesiąc, wykonywane co noc przez timer systemd lub wiersz w Twoim crontabie (OpenRC, runit), na Twoim koncie, nigdy jako root. |
| **Wyczyść** | Opróżnia zawartość logu (obcięcie w miejscu, bezpieczne dla usługi, która wciąż ma go otwartego) lub całkowicie usuwa jeden lub kilka plików — zawsze z potwierdzeniem. |
| **Eksportuj** | Eksport listy archiwów (Rotate) do JSON lub HTML z motywem. |
| **Kondycja logów** | Kontrola tylko do odczytu logów z Biblioteki, dysku, kopii zapasowych i zaplanowanych kopii zapasowych: uprawnienia, logi milczące lub uszkodzone, daty, logrotate, dni do zapełnienia dysku, wraz z zalecanym działaniem. Naprawa zbyt szerokich uprawnień (w razie potrzeby przez sudo), eksport JSON/HTML/TXT. |
| **Opcje** | Motyw, profil renderowania, język interfejsu i język eksportów (17 języków), czyszczenie katalogów aplikacji (exports/screenshots). |

### 3 przeglądarki

1. **Prosta** — śledzenie na żywo z ogólnym parsowaniem (znacznik czasu, IP, poziom, usługa) i małą tabelą statystyk. Dla rozpoznanego logu dostępu HTTP dodatkowe kolumny kod HTTP / opóźnienie, kolorowane według progów.
2. **Klasyczna** — odczyt ostatnich surowych wierszy + przełącznik „Śledź na żywo”, bez parsowania: najprostsza i najbardziej niezawodna niezależnie od formatu.
3. **lnav** — scalanie kilku plików w osadzonym terminalu (pty) do analizy krzyżowej. Przełączanie motywu (`t`), zaznaczanie + kopiowanie do schowka (`Ctrl+C`, OSC 52), wyjście (`Ctrl+Q`) — wszystko przechwytywane przed samym `lnav`.

## 5. Zgodność z terminalami

TUI (Textual) automatycznie wykrywa możliwości terminala (emulator, rozmiar) i odpowiednio dostosowuje swój arkusz stylów (`complete`/`standard`/`reduced`/`mono`), bez ręcznej flagi — ta sama polityka obowiązuje w całym pakiecie `omega-` (`omega-lib`, `terminal/policies.py`). Odświeżanie na żywo klawiszem `r`.

### Profil według wykrytego emulatora

| Emulator | Profil początkowy |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, nowoczesne SSH | `reduced` |
| TTY Linux, starsze SSH | `mono` |
| Nierozpoznany emulator | `reduced` (domyślny wariant zapasowy) |

### Profil według rozmiaru terminala

| Minimalny rozmiar (kolumny × wiersze) | Pułap profilu |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| poniżej | `mono` |

Ostatecznie wybierany jest **bardziej restrykcyjny z dwóch** profili (emulator i rozmiar).

## 6. Architektura

Clean Architecture (domena / aplikacja / infrastruktura / interfejsy), ta sama konwencja co w reszcie pakietu OMEGA:

```text
src/omega_log/
├── core/            Rejestr możliwości (wykrywanie usług)
├── domain/          Czysta logika biznesowa (parsowanie, statystyki, rotacja, czyszczenie)
├── ports/           Kontrakty (Protocol)
├── application/     Przypadki użycia
├── infrastructure/  Rzeczywiste implementacje (sondy, przechowywanie, archiwa, eksport, lnav, współbieżność)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

Zależy od [`omega-lib`](../../../../LIB/omega-lib) w zakresie motywów (10 motywów TUI + 5 motywów eksportu), wykrywania terminala i przechowywania ustawień — ta sama podstawa co w reszcie pakietu. Ciężkie obliczenia (top IP, statystyki dostępu) wykonują się w dedykowanym `ProcessPoolExecutor` (`infrastructure/concurrency/`), nigdy w wątku interfejsu, aby zachować responsywność nawet przy pliku liczącym kilkaset tysięcy wierszy.

## 7. Testy

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 testy
ruff check .
mypy src
```

Struktura: `tests/unit/` (domena i aplikacja, bez rzeczywistego I/O), `tests/integration/` (prawdziwe pliki, TUI bez wyświetlania przez API `Pilot` z Textual).

## 8. Stan rozwoju

Wszystkie 10 faz planu rozwoju zostało ukończonych: podstawa, domena, bazowe TUI, przeglądarki, ulubione/biblioteka/IP, utrzymanie, statystyki/eksport, finalizacja, jednorazowe podniesienie uprawnień przez sudo, obliczenia obciążające CPU przeniesione do osobnego procesu — szczegóły każdej decyzji dotyczącej przenoszenia w `plan_omega_log.md`. Od wersji 1.6.0 przejęto nowości z menedżera logów omega-serv 2.6.0: Kondycja logów, zaplanowane kopie zapasowe, wyszukiwanie konkretnego adresu IP, wyświetlanie wersji i sprawdzanie aktualizacji.

## 9. Licencja

MIT — zob. [LICENSE](../../../LICENSE).

---

> Omega-log — Wykrywać, gromadzić, czytać, analizować, utrzymywać.
> Twoje logi pozostają Twoje: żadnego podnoszenia uprawnień bez rzeczywistej potrzeby, żadnego działania destrukcyjnego bez potwierdzenia.
