<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**サーバーログの管理・閲覧ツール**

> [kraynux](https://github.com/kraynux) が [Omega-Server](https://kraynux.snake-mackarel.ts.net) のために開発

公式ページ：[OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/ja/) &nbsp; プレビュー：[スクリーンショット](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 インターフェース、ドキュメント、エクスポートは **17 言語** に対応しています。  
**言語：**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** は `omega-` スイートのツールで、サーバーのログファイルの管理・閲覧・分析を TUI で行います — 稼働中のサービスとそのログの自動検出、中央ライブラリ、3 つの閲覧モード（シンプルな追跡、クラシックな閲覧、`lnav` による複数ファイルのマージ）、IP の処理、統計、ローテーション/バックアップ/復元、安全な削除、エクスポートを備えています。ゼロから書き直すのではなく、すでに成熟した [omega-fire](https://github.com/kraynux) と [omega-serv](https://github.com/kraynux) のコードを **移植・適応** して作られています。

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-log/D.png" width="24%" />
</p>

## 1. ビジョンと範囲

Omega-log はシンプルな問いに答えます：「ログの中で何が起きていて、それをどう扱えばよいのか？」— 既知のパスの固定リストに頼らず、デフォルトで root として動作することは決してなく、実際のログファイルを黙って失ったり壊したりすることも決してありません。

### Omega-log ができること

- マシン上で稼働中のサービス（Web サーバー、データベース、メール、DNS、セキュリティ、`omega-serv`...）を自動検出し、それらの既知のログを個別または一括でインポートできます — 任意のフォルダーの手動スキャンも併用できます。
- 処理するログを 1 つのライブラリに集約します。ライブラリは他のすべての画面の入口です。
- 用途に応じて 3 つのモードでログを読みます：解析と統計付きのシンプルな追跡、ライブ追跡付きの生データのクラシックな閲覧、または `lnav` を組み込んだ複数ファイルのマージ。
- ログとビューアーの組み合わせをお気に入りとして記憶し、直接起動できます。
- 期間ごとの IP 上位 10 件を算出したり、特定の IP を検索したりして、1 つまたは複数のファイルからその IP を対象を絞って削除できます。
- アクセス統計（量、ユニーク IP、エラー率、時間帯別の分布）を算出し、JSON またはテーマ付き HTML でエクスポートできます。
- ログファイルのバックアップ（圧縮 + 自動保持）を手動または定期バックアップで毎晩行い、復元（マージまたは上書き、安全のためのバックアップ付き）と削除（その場での切り詰めまたは削除）を行います。いずれも必ず明示的な確認を経ます。
- ログの健全性（権限、出力のない・破損したログ、ディスク容量、バックアップ）を点検し、各指摘に対して何をすべきかを示します。
- スイートの他のツールと同様に、`omega-lib` を通じてターミナルの能力（色、サイズ）に自動で適応します。

### Omega-log がしないこと

| 機能 | 担当ツール |
|---|---|
| ファイアウォール、ネットワークルール、侵入検知 | OMEGA-FIRE |
| Web サーバー、リバースプロキシ、WAF、Active Defense | OMEGA-SERV |
| ポートスキャン、ネットワークサービスの識別 | OMEGA-CHECK |
| ネットワーク観測、対象のデジタルアイデンティティ | OMEGA-TRACK |

TUI と完全に同等の CLI は（まだ）ありません（現在のコマンドラインモードはサービスのスキャンのみに対応、§3.2 を参照）。複数マシンの集中集約も、しきい値によるリアルタイムのアラートもありません — Omega-log はローカルの点検・保守ツールであり、SIEM ではありません。

### 使用上の注意

保守操作（**削除**、**Rotate → 上書きモードで復元**）は、ログファイルの実際の内容を変更または完全に消去します — 必ず対象ファイルを詳しく示す明示的な確認を経て行われ、自動で実行されることは決してありません。迷ったら、操作の前にバックアップしてください（**Rotate → 今すぐバックアップ**）。

## 2. インストール

### 前提条件

- Python 3.10+
- Linux（Arch/Manjaro、Debian/Ubuntu、RHEL/Fedora でテスト済み）
- システムにインストールされた `lnav`。複数ファイルをマージするビューアーにのみ必要です（他の 2 つのビューアーはなくても普通に動作します）：

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### インストール

```bash
[ -d omega-log ] && echo "ℹ️ ここに展開済みのため、この手順はスキップします。" || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh` は：

1. 仮想環境 `.venv` がまだなければ作成します。
2. 依存関係をインストールします（同梱の `omega-lib` があれば先にインストールし、次に `pip install -e .` — `pyproject.toml` が唯一の情報源です）。
3. `omega-log.sh` と `install.sh` を実行可能にします。
4. `lnav` の有無を確認します（ない場合は情報としての警告のみで、決して処理を止めません）。
5. `~/.bashrc` と `~/.zshrc` にエイリアス `log` を追加します（既にあれば重複しません）。

### 依存関係

`pyproject.toml` で宣言されています（別の `requirements.txt` はありません）：
- `omega-lib`：スイートの共有ライブラリ（TUI とエクスポートのテーマ、ターミナル検出、設定の保存）
- `textual`：TUI インターフェース
- `jinja2`：テーマ付き HTML エクスポート（統計、アーカイブ）
- `pyte`：`lnav` ビューアー用のターミナルエミュレーション（組み込み pty 内での描画）
- 開発用の依存関係（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`ruff`、`mypy`

## 3. 使い方

### 3.1. 対話モード（TUI）

日常の利用に推奨 — 引数なしで起動します：

```bash
./omega-log.sh
```
エイリアスを作成した場合は、新しいターミナルで `log` と入力するだけです：
```bash
log
```

全体の流れ：起動画面 → メインメニュー（2 列 — 片側に 機能レジストリ/ライブラリ/ログを表示/お気に入り/IP の表示と処理/統計（アクセス）、もう片側に Rotate/削除/エクスポート/ログの健全性/オプション/ヘルプ）→ 選んだ機能の画面 → メニューに戻る（`Esc`）。完全なヘルプ（`a`）では、各画面、各ビューアー、そして横断的な概念（一時的な sudo 昇格、ログの状態、番号による選択）を詳しく説明しています — 要点は §4 を参照してください。

#### キーボードショートカット

| キー | 操作 |
|---|---|
| `↑` / `↓` | 画面内の項目間を移動 |
| `Tab` / `Shift+Tab` | フォームのフィールド間を移動 |
| `Esc` | 前の画面に戻る（ホームでは終了の確認） |
| `t` | 次のテーマ（確認なしで即座に適用） |
| `r` | ターミナル検出を更新 |
| `a` | ヘルプを表示（網羅的、画面ごとに 1 章） |
| `q` | 終了（確認あり） |

### 3.2. コマンドラインモード（CLI）

TUI との完全な同等性はまだありません（お気に入り、削除... はそれぞれのフェーズで追加予定、`plan_omega_log.md` §12 を参照）：

```bash
# 稼働中のサービスとその既知のログを検出
python -m omega_log scan

# + 追加フォルダーの手動スキャン
python -m omega_log scan --path /var/log

# インストール済みのバージョンと、最新の公開バージョンとの比較
python -m omega_log version --check

# 期限が来た定期バックアップ（systemd タイマーまたは crontab により毎晩実行）
python -m omega_log rotate run-automations
```

### 3.3. 環境変数

| 変数 | 効果 |
|---|---|
| `OMEGA_LOG_VAR_DIR` | アプリケーションの状態フォルダーの場所を変更（デフォルトは `./var`、起動したフォルダーからの相対パス） |
| `OMEGA_LOG_LANG` | 保存された設定を変えずに、そのセッションのインターフェース言語を強制（例：`en`、`de`、`ja`） |

## 4. 機能

| 画面 | 説明 |
|---|---|
| **機能レジストリ** | マシン上で稼働中のサービスを検出し、それらの既知のログを個別または一括でインポートできます。フォルダーの手動スキャンも併用できます。 |
| **ライブラリ** | 処理するすべてのログを登録する中央ハブ — 機能レジストリ、手動インポート、Omega-Serv の既知のログ、または SSH で取得したコピーから追加されます。 |
| **ログを表示** | ライブラリから 1 つまたは複数のログを選び、ビューアーを選択（ログ 1 つ → 3 つのビューアー；2 つ以上 → `lnav` のみ）。 |
| **お気に入り** | 名前を付けて保存したログとビューアーの組み合わせで、直接起動できます。 |
| **IP の表示と処理** | 期間ごと（24h/7d/30d/すべて）の IP 上位 10 件、または特定の IP（IPv4 または IPv6）の検索、そして 1 つまたは複数のログからの IP の対象を絞った削除。 |
| **統計（アクセス）** | 量、ユニーク IP、エラー率、上位 IP、時間帯別の分布 — 5 つのテーマで JSON/HTML にエクスポート。 |
| **Rotate** | ログの圧縮バックアップ + 超過したアーカイブの自動保持管理 + 復元（マージまたは上書き、安全のためのバックアップ付き）。**定期バックアップ**：ログを毎日、毎週、または毎月バックアップし、systemd タイマーまたは crontab の 1 行（OpenRC、runit）で毎晩実行します。実行はあなたのアカウントで、決して root ではありません。 |
| **削除** | ログの内容を空にする（その場での切り詰め。まだファイルを開いているサービスにも安全）か、1 つまたは複数のファイルを完全に削除 — 必ず確認を経ます。 |
| **エクスポート** | アーカイブ一覧（Rotate）を JSON またはテーマ付き HTML でエクスポート。 |
| **ログの健全性** | ライブラリのログ、ディスク、バックアップ、定期バックアップを読み取り専用で点検：権限、出力のない・破損したログ、日付、logrotate、ディスクが満杯になるまでの日数、そして取るべき対処。開きすぎた権限の修正（必要なら sudo で）、JSON/HTML/TXT でのエクスポート。 |
| **オプション** | テーマ、描画プロファイル、インターフェースの言語とエクスポートの言語（17 言語）、アプリケーションフォルダー（exports/screenshots）の削除。 |

### 3 つのビューアー

1. **シンプル** — 汎用的な解析（タイムスタンプ、IP、レベル、サービス）と小さな統計表を備えたライブ追跡。認識された HTTP アクセスログでは、HTTP コード / レイテンシの列が追加され、しきい値ごとに色分けされます。
2. **クラシック** — 解析なしで最後の生の行を読み、「ライブ追跡」に切り替えられます：形式を問わず、最もシンプルで最も確実です。
3. **lnav** — 組み込みターミナル（pty）内で複数のファイルをマージし、横断的に分析します。テーマの切り替え（`t`）、選択 + クリップボードへのコピー（`Ctrl+C`、OSC 52）、終了（`Ctrl+Q`）— いずれも `lnav` 自体より先に処理されます。

## 5. ターミナルの互換性

TUI（Textual）はターミナルの能力（エミュレーター、サイズ）を自動検出し、それに応じて構造用のスタイルシート（`complete`/`standard`/`reduced`/`mono`）を適応させます。手動のフラグは不要です — `omega-` スイート全体で共有される同じ方針です（`omega-lib`、`terminal/policies.py`）。`r` キーでその場で更新できます。

### 検出されたエミュレーターによるプロファイル

| エミュレーター | 初期プロファイル |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, 最新の SSH | `reduced` |
| Linux TTY, 旧式の SSH | `mono` |
| 認識されないエミュレーター | `reduced`（デフォルトのフォールバック） |

### ターミナルのサイズによるプロファイル

| 最小サイズ（列 × 行） | プロファイルの上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| それ未満 | `mono` |

最終的に採用されるプロファイルは **2 つ（エミュレーターとサイズ）のうち最も制限の強いほう** です。

## 6. アーキテクチャ

クリーンアーキテクチャ（ドメイン / アプリケーション / インフラストラクチャ / インターフェース）で、OMEGA スイートの他のツールと同じ規約です：

```text
src/omega_log/
├── core/            機能レジストリ（サービスの検出）
├── domain/          純粋なビジネスロジック（解析、統計、ローテーション、削除）
├── ports/           契約（Protocol）
├── application/     ユースケース
├── infrastructure/  実際の実装（プローブ、保存、アーカイブ、エクスポート、lnav、並行処理）
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

テーマ（TUI 用 10 テーマ + エクスポート用 5 テーマ）、ターミナル検出、設定の保存は [`omega-lib`](../../../../LIB/omega-lib) に依存しています — スイートの他のツールと同じ基盤です。重い計算（上位 IP、アクセス統計）は専用の `ProcessPoolExecutor`（`infrastructure/concurrency/`）で実行され、インターフェースのスレッドで実行されることは決してないため、数十万行のファイルでも応答性を保ちます。

## 7. テスト

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 件のテスト
ruff check .
mypy src
```

構成：`tests/unit/`（ドメインとアプリケーション、実際の I/O なし）、`tests/integration/`（実際のファイル、Textual の `Pilot` API によるヘッドレス TUI）。

## 8. 開発状況

開発計画の 10 フェーズはすべて完了しています：基盤、ドメイン、基本 TUI、ビューアー、お気に入り/ライブラリ/IP、保守、統計/エクスポート、仕上げ、一時的な sudo 昇格、CPU 負荷の高い計算の別プロセスへの移行 — 各移植の判断の詳細は `plan_omega_log.md` を参照してください。1.6.0 以降、omega-serv 2.6.0 のログマネージャーの新機能を取り込んでいます：ログの健全性、定期バックアップ、特定の IP の検索、バージョン表示と更新の確認。

## 9. ライセンス

MIT — [LICENSE](../../../LICENSE) を参照。

---

> Omega-log — 検出し、集約し、読み、分析し、保守する。
> あなたのログはあなたのもの：本当に必要な場合を除いて権限昇格はせず、確認なしの破壊的操作も一切ありません。
