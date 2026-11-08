<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**서버 로그 관리 및 뷰어**

> [kraynux](https://github.com/kraynux)가 [Omega-Server](https://kraynux.snake-mackarel.ts.net)를 위해 개발

공식 페이지: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/ko/) &nbsp; 미리 보기: [스크린샷](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 인터페이스, 문서 및 내보내기를 **17개 언어**로 제공합니다.  
**언어:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log**는 `omega-` 제품군에서 서버 로그 파일의 관리, 읽기, 분석을 TUI로 담당하는 도구입니다 — 실행 중인 서비스와 그 로그의 자동 감지, 중앙 라이브러리, 세 가지 읽기 모드(단순 추적, 클래식 읽기, `lnav`를 통한 여러 파일 병합), IP 처리, 통계, 로테이션/백업/복원, 안전한 정리 및 내보내기를 제공합니다. 처음부터 다시 작성하지 않고, 이미 성숙한 [omega-fire](https://github.com/kraynux)와 [omega-serv](https://github.com/kraynux)의 코드를 **이식하고 조정**하여 만들었습니다.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-log/D.png" width="24%" />
</p>

## 1. 비전과 범위

Omega-log는 간단한 질문에 답합니다: "내 로그에서 무슨 일이 일어나고 있고, 어떻게 처리해야 할까?" — 알려진 경로의 고정 목록에 의존하지 않고, 기본적으로 root로 실행되는 일이 절대 없으며, 실제 로그 파일을 조용히 잃거나 손상시키는 일도 절대 없습니다.

### Omega-log가 하는 일

- 머신에서 실행 중인 서비스(웹 서버, 데이터베이스, 메일, DNS, 보안, `omega-serv`...)를 자동으로 감지하고, 알려진 로그를 개별 또는 전체로 가져오도록 제안합니다 — 임의 폴더의 수동 스캔도 함께 사용할 수 있습니다.
- 처리할 로그를 하나의 라이브러리에 모읍니다. 라이브러리는 다른 모든 화면의 진입점입니다.
- 필요에 따라 세 가지 모드로 로그를 읽습니다: 파싱과 통계가 있는 단순 추적, 실시간 추적이 있는 원시 클래식 읽기, 또는 `lnav`를 내장한 여러 파일 병합.
- 로그 + 뷰어 조합을 즐겨찾기로 저장하여 바로 실행할 수 있습니다.
- 기간별 상위 10개 IP를 계산하거나 특정 IP를 검색하고, 하나 이상의 파일에서 해당 IP를 골라 삭제할 수 있습니다.
- 접근 통계(요청량, 고유 IP, 오류율, 시간대별 분포)를 계산하고 JSON 또는 테마가 적용된 HTML로 내보낼 수 있습니다.
- 로그 파일을 백업(압축 + 자동 보존)하며, 수동으로 또는 예약 백업으로 매일 밤 실행합니다. 복원(병합 또는 덮어쓰기, 안전 백업 포함)과 정리(제자리 비우기 또는 삭제)도 하며, 항상 명시적인 확인을 거칩니다.
- 로그 상태(권한, 기록이 멈춘 로그나 손상된 로그, 디스크 공간, 백업)를 점검하고 각 결과마다 무엇을 해야 하는지 알려 줍니다.
- 제품군의 다른 도구와 마찬가지로 `omega-lib`를 통해 터미널의 기능(색상, 크기)에 자동으로 맞춥니다.

### Omega-log가 하지 않는 일

| 기능 | 담당 도구 |
|---|---|
| 방화벽, 네트워크 규칙, 침입 탐지 | OMEGA-FIRE |
| 웹 서버, 리버스 프록시, WAF, Active Defense | OMEGA-SERV |
| 포트 스캔, 네트워크 서비스 식별 | OMEGA-CHECK |
| 네트워크 관찰, 대상의 디지털 신원 | OMEGA-TRACK |

TUI와 완전히 동등한 CLI는 (아직) 없습니다(현재 명령줄 모드는 서비스 스캔만 지원, §3.2 참조). 여러 머신의 중앙 집계도, 임계값 기반 실시간 경보도 없습니다 — Omega-log는 로컬 점검 및 유지 관리 도구이며, SIEM이 아닙니다.

### 사용 시 주의

유지 관리 작업(**정리**, **Rotate → 덮어쓰기 모드로 복원**)은 로그 파일의 실제 내용을 변경하거나 영구적으로 지웁니다 — 항상 대상 파일을 자세히 보여 주는 명시적인 확인을 먼저 거치며, 자동으로 실행되는 일은 절대 없습니다. 확실하지 않다면 작업 전에 백업하세요(**Rotate → 지금 백업**).

## 2. 설치

### 사전 요구 사항

- Python 3.10+
- Linux(Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora에서 테스트됨)
- 시스템에 설치된 `lnav`. 여러 파일을 병합하는 뷰어에만 필요합니다(다른 두 뷰어는 없어도 정상 작동):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### 설치

```bash
[ -d omega-log ] && echo "ℹ️ 이미 여기에 압축이 풀려 있어 이 단계를 건너뜁니다." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`는:

1. 가상 환경 `.venv`가 아직 없으면 만듭니다.
2. 의존성을 설치합니다(함께 제공된 `omega-lib`가 있으면 먼저 설치한 뒤 `pip install -e .` — `pyproject.toml`이 유일한 기준입니다).
3. `omega-log.sh`와 `install.sh`를 실행 가능하게 만듭니다.
4. `lnav`가 있는지 확인합니다(없으면 안내용 경고만 표시하며, 절대 중단하지 않습니다).
5. `~/.bashrc`와 `~/.zshrc`에 별칭 `log`를 추가합니다(이미 있으면 중복하지 않음).

### 의존성

`pyproject.toml`에 선언되어 있습니다(별도의 `requirements.txt` 없음):
- `omega-lib`: 제품군의 공유 라이브러리(TUI 및 내보내기 테마, 터미널 감지, 설정 저장)
- `textual`: TUI 인터페이스
- `jinja2`: 테마가 적용된 HTML 내보내기(통계, 아카이브)
- `pyte`: `lnav` 뷰어용 터미널 에뮬레이션(내장 pty 안에서 렌더링)
- 개발용 의존성(`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. 사용법

### 3.1. 대화형 모드(TUI)

일상적인 사용에 권장 — 인수 없이 실행합니다:

```bash
./omega-log.sh
```
별칭을 만들었다면 새 터미널에서 `log`만 입력하면 됩니다:
```bash
log
```

전체 흐름: 시작 화면 → 주 메뉴(두 열 — 한쪽에 기능 레지스트리/라이브러리/로그 보기/즐겨찾기/IP 보기 및 처리/통계(접근), 다른 쪽에 Rotate/정리/내보내기/로그 상태/옵션/도움말) → 선택한 기능의 화면 → 메뉴로 돌아가기(`Esc`). 전체 도움말(`a`)은 각 화면, 각 뷰어, 그리고 공통 개념(일시적인 sudo 권한 상승, 로그 상태, 번호로 선택)을 자세히 설명합니다 — 핵심은 §4를 참조하세요.

#### 키보드 단축키

| 키 | 동작 |
|---|---|
| `↑` / `↓` | 화면의 항목 사이 이동 |
| `Tab` / `Shift+Tab` | 양식의 필드 사이 이동 |
| `Esc` | 이전 화면으로 돌아가기(홈에서는 종료 확인) |
| `t` | 다음 테마(확인 없이 즉시 적용) |
| `r` | 터미널 감지 새로 고침 |
| `a` | 도움말 표시(빠짐없이, 화면마다 한 장) |
| `q` | 종료(확인 후) |

### 3.2. 명령줄 모드(CLI)

아직 TUI와 완전히 동등하지 않습니다(즐겨찾기, 정리... 는 각자의 단계에서 추가될 예정, `plan_omega_log.md` §12 참조):

```bash
# 실행 중인 서비스와 알려진 로그를 감지
python -m omega_log scan

# + 추가 폴더의 수동 스캔
python -m omega_log scan --path /var/log

# 설치된 버전, 그리고 최신 공개 버전과의 비교
python -m omega_log version --check

# 기한이 된 예약 백업(systemd 타이머 또는 crontab이 매일 밤 실행)
python -m omega_log rotate run-automations
```

### 3.3. 환경 변수

| 변수 | 효과 |
|---|---|
| `OMEGA_LOG_VAR_DIR` | 애플리케이션 상태 폴더의 위치를 변경(기본값 `./var`, 실행한 폴더 기준 상대 경로) |
| `OMEGA_LOG_LANG` | 저장된 설정을 바꾸지 않고 해당 세션의 인터페이스 언어를 강제(예: `en`, `de`, `ja`) |

## 4. 기능

| 화면 | 설명 |
|---|---|
| **기능 레지스트리** | 머신에서 실행 중인 서비스를 감지하고, 알려진 로그를 개별 또는 전체로 가져오도록 제안합니다. 폴더의 수동 스캔도 함께 사용할 수 있습니다. |
| **라이브러리** | 처리할 모든 로그를 등록하는 중앙 허브 — 기능 레지스트리, 수동 가져오기, Omega-Serv의 알려진 로그, 또는 SSH로 가져온 사본으로 채워집니다. |
| **로그 보기** | 라이브러리에서 하나 이상의 로그를 선택하고 뷰어를 고릅니다(로그 1개 → 뷰어 3개 모두; 2개 이상 → `lnav`만). |
| **즐겨찾기** | 이름을 붙여 저장한 로그 + 뷰어 조합으로, 바로 실행할 수 있습니다. |
| **IP 보기 및 처리** | 기간별(24h/7d/30d/전체) 상위 10개 IP, 또는 특정 IP(IPv4 또는 IPv6) 검색, 그리고 하나 이상의 로그에서 IP를 골라 삭제. |
| **통계(접근)** | 요청량, 고유 IP, 오류율, 상위 IP, 시간대별 분포 — 5가지 테마로 JSON/HTML 내보내기. |
| **Rotate** | 로그의 압축 백업 + 초과 아카이브의 자동 보존 관리 + 복원(병합 또는 덮어쓰기, 안전 백업 포함). **예약 백업**: 로그를 매일, 매주 또는 매월 백업하며, systemd 타이머나 crontab의 한 줄(OpenRC, runit)로 매일 밤 실행합니다. 실행은 사용자 계정으로 하며, 절대 root로 하지 않습니다. |
| **정리** | 로그의 내용을 비우거나(제자리 비우기, 아직 파일을 열고 있는 서비스에도 안전) 하나 이상의 파일을 완전히 삭제 — 항상 확인을 거칩니다. |
| **내보내기** | 아카이브 목록(Rotate)을 JSON 또는 테마가 적용된 HTML로 내보내기. |
| **로그 상태** | 라이브러리의 로그, 디스크, 백업, 예약 백업을 읽기 전용으로 점검: 권한, 기록이 멈춘 로그나 손상된 로그, 날짜, logrotate, 디스크가 가득 찰 때까지 남은 일수, 그리고 해야 할 조치. 너무 열린 권한 수정(필요하면 sudo로), JSON/HTML/TXT 내보내기. |
| **옵션** | 테마, 렌더링 프로필, 인터페이스 언어와 내보내기 언어(17개 언어), 애플리케이션 폴더(exports/screenshots) 정리. |

### 뷰어 3가지

1. **단순** — 범용 파싱(타임스탬프, IP, 수준, 서비스)과 작은 통계표가 있는 실시간 추적. 인식된 HTTP 접근 로그에서는 HTTP 코드 / 지연 시간 열이 추가되며, 임계값에 따라 색이 표시됩니다.
2. **클래식** — 파싱 없이 마지막 원시 줄을 읽고 "실시간 추적"으로 전환: 형식과 관계없이 가장 단순하고 가장 신뢰할 수 있습니다.
3. **lnav** — 내장 터미널(pty)에서 여러 파일을 병합하여 교차 분석. 테마 순환(`t`), 선택 + 클립보드 복사(`Ctrl+C`, OSC 52), 종료(`Ctrl+Q`) — 모두 `lnav` 자체보다 먼저 가로챕니다.

## 5. 터미널 호환성

TUI(Textual)는 터미널의 기능(에뮬레이터, 크기)을 자동으로 감지하고 그에 맞게 구조 스타일시트(`complete`/`standard`/`reduced`/`mono`)를 조정합니다. 수동 플래그는 필요 없습니다 — `omega-` 제품군 전체가 공유하는 같은 정책입니다(`omega-lib`, `terminal/policies.py`). `r` 키로 실시간 새로 고침할 수 있습니다.

### 감지된 에뮬레이터별 프로필

| 에뮬레이터 | 초기 프로필 |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, 최신 SSH | `reduced` |
| Linux TTY, 구형 SSH | `mono` |
| 인식되지 않은 에뮬레이터 | `reduced`(기본 대체값) |

### 터미널 크기별 프로필

| 최소 크기(열 × 행) | 프로필 상한 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 그 미만 | `mono` |

최종 프로필은 **두 가지(에뮬레이터와 크기) 중 더 제한적인 쪽**입니다.

## 6. 아키텍처

클린 아키텍처(도메인 / 애플리케이션 / 인프라스트럭처 / 인터페이스)로, OMEGA 제품군의 다른 도구와 같은 규칙을 따릅니다:

```text
src/omega_log/
├── core/            기능 레지스트리(서비스 감지)
├── domain/          순수 비즈니스 로직(파싱, 통계, 로테이션, 정리)
├── ports/           계약(Protocol)
├── application/     유스케이스
├── infrastructure/  실제 구현(프로브, 저장, 아카이브, 내보내기, lnav, 동시성)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

테마(TUI 테마 10개 + 내보내기 테마 5개), 터미널 감지, 설정 저장은 [`omega-lib`](../../../../LIB/omega-lib)에 의존합니다 — 제품군의 다른 도구와 같은 기반입니다. 무거운 계산(상위 IP, 접근 통계)은 전용 `ProcessPoolExecutor`(`infrastructure/concurrency/`)에서 실행되며, 인터페이스 스레드에서는 절대 실행되지 않으므로 수십만 줄의 파일에서도 반응성을 유지합니다.

## 7. 테스트

```bash
source .venv/bin/activate
pytest tests/ -q      # 테스트 243개
ruff check .
mypy src
```

구성: `tests/unit/`(도메인과 애플리케이션, 실제 I/O 없음), `tests/integration/`(실제 파일, Textual의 `Pilot` API를 통한 헤드리스 TUI).

## 8. 개발 현황

개발 계획의 10단계가 모두 완료되었습니다: 기반, 도메인, 기본 TUI, 뷰어, 즐겨찾기/라이브러리/IP, 유지 관리, 통계/내보내기, 마무리, 일시적인 sudo 권한 상승, CPU 집약적 계산의 별도 프로세스 분리 — 각 이식 결정의 자세한 내용은 `plan_omega_log.md`를 참조하세요. 1.6.0부터 omega-serv 2.6.0 로그 관리자의 새 기능을 가져왔습니다: 로그 상태, 예약 백업, 특정 IP 검색, 버전 표시 및 업데이트 확인.

## 9. 라이선스

MIT — [LICENSE](../../../LICENSE)를 참조하세요.

---

> Omega-log — 감지하고, 모으고, 읽고, 분석하고, 유지 관리합니다.
> 로그는 여러분의 것입니다: 꼭 필요한 경우가 아니면 권한 상승은 없고, 확인 없는 파괴적 작업도 없습니다.
