<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**Pengelola dan penampil log server**

> Dibuat oleh [kraynux](https://github.com/kraynux) untuk [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Halaman resmi: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/id/) &nbsp; Pratinjau: [Tangkapan layar](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 Antarmuka, dokumentasi, dan ekspor tersedia dalam **17 bahasa**.  
**Bahasa:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** adalah alat dalam rangkaian `omega-` yang ditujukan untuk mengelola, membaca, dan menganalisis berkas log server melalui TUI — deteksi otomatis layanan yang aktif beserta log-nya, pustaka pusat, tiga mode pembacaan (pemantauan sederhana, pembacaan klasik, penggabungan multi-berkas melalui `lnav`), penanganan IP, statistik, rotasi/pencadangan/pemulihan, pembersihan yang aman, dan ekspor. Dibangun dengan **memindahkan dan menyesuaikan** kode yang sudah matang dari [omega-fire](https://github.com/kraynux) dan [omega-serv](https://github.com/kraynux), alih-alih menulis ulang dari nol.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-log/D.png" width="24%" />
</p>

## 1. Visi dan cakupan

Omega-log menjawab satu pertanyaan sederhana: « apa yang terjadi di log saya, dan bagaimana saya menanganinya? » — tanpa bergantung pada daftar jalur tetap yang sudah dikenal, tanpa pernah berjalan sebagai root secara bawaan, dan tanpa pernah menghilangkan atau merusak berkas log sungguhan secara diam-diam.

### Apa yang dilakukan Omega-log

- Mendeteksi otomatis layanan yang aktif di mesin (server web, basis data, surel, DNS, keamanan, `omega-serv`...) dan menawarkan impor log-log yang dikenal, satu per satu atau sekaligus — sebagai pelengkap pemindaian manual folder mana pun.
- Memusatkan log yang akan ditangani dalam satu Pustaka, titik masuk ke semua layar lainnya.
- Membaca log dalam tiga mode sesuai kebutuhan: pemantauan sederhana dengan parsing dan statistik, pembacaan klasik mentah dengan pemantauan langsung, atau penggabungan multi-berkas yang membungkus `lnav`.
- Menyimpan kombinasi log + viewer sebagai Favorit, untuk dijalankan langsung.
- Menghitung 10 IP teratas per periode, atau mencari IP tertentu, dan memungkinkan penghapusan terarah di satu atau beberapa berkas.
- Menghitung statistik akses (volume, IP unik, tingkat galat, distribusi per jam) yang dapat diekspor ke JSON atau HTML bertema.
- Mencadangkan (kompresi + retensi otomatis), secara manual atau setiap malam melalui cadangan terjadwal, memulihkan (penggabungan atau timpa, dengan cadangan pengaman) dan membersihkan (pemotongan di tempat atau penghapusan) berkas log, selalu dengan konfirmasi eksplisit.
- Memeriksa kesehatan log (hak akses, log yang diam atau rusak, ruang disk, cadangan) dan memberi tahu apa yang harus dilakukan untuk setiap temuan.
- Menyesuaikan diri otomatis dengan kemampuan terminal (warna, ukuran) melalui `omega-lib`, seperti alat lain dalam rangkaian ini.

### Apa yang tidak dilakukan Omega-log

| Fungsi | Alat yang bertanggung jawab |
|---|---|
| Firewall, aturan jaringan, deteksi intrusi | OMEGA-FIRE |
| Server web, reverse proxy, WAF, Active Defense | OMEGA-SERV |
| Pemindaian port, identifikasi layanan jaringan | OMEGA-CHECK |
| Pengamatan jaringan, identitas digital suatu target | OMEGA-TRACK |

Belum ada CLI yang setara penuh dengan TUI (mode baris perintah saat ini hanya mencakup pemindaian layanan, lihat §3.2), tidak ada agregasi terpusat dari banyak mesin, tidak ada peringatan waktu nyata berdasarkan ambang batas — Omega-log tetap alat inspeksi dan pemeliharaan lokal, bukan SIEM.

### Peringatan penggunaan

Tindakan pemeliharaan (**Bersihkan**, **Rotate → Pulihkan dalam mode Timpa**) mengubah atau menghapus secara permanen isi sebenarnya dari berkas log Anda — selalu didahului konfirmasi eksplisit yang merinci berkas terkait, tidak pernah dipicu secara otomatis. Jika ragu, cadangkan dulu (**Rotate → Cadangkan sekarang**) sebelum bertindak.

## 2. Instalasi

### Prasyarat

- Python 3.10+
- Linux (diuji di Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` terpasang di sistem, hanya untuk viewer penggabungan multi-berkas (dua viewer lainnya berfungsi normal tanpanya):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Instalasi

```bash
[ -d omega-log ] && echo "ℹ️ Sudah diekstrak di sini, langkah dilewati." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Membuat lingkungan virtual `.venv` jika belum ada.
2. Memasang dependensi (`omega-lib` yang disertakan (vendored) lebih dulu jika ada, lalu `pip install -e .` — `pyproject.toml` tetap satu-satunya sumber kebenaran).
3. Membuat `omega-log.sh` dan `install.sh` dapat dieksekusi.
4. Memeriksa keberadaan `lnav` (peringatan informatif jika tidak ada, tidak pernah memblokir).
5. Menambahkan alias `log` ke `~/.bashrc` dan `~/.zshrc` (tanpa duplikat jika sudah ada).

### Dependensi

Dideklarasikan di `pyproject.toml` (tanpa `requirements.txt` terpisah):
- `omega-lib`: pustaka bersama rangkaian ini (tema TUI + ekspor, deteksi terminal, penyimpanan pengaturan)
- `textual`: antarmuka TUI
- `jinja2`: ekspor HTML bertema (statistik, arsip)
- `pyte`: emulasi terminal untuk viewer `lnav` (dirender dalam pty yang dibungkus)
- Dependensi pengembangan (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Penggunaan

### 3.1. Mode interaktif (TUI)

Disarankan untuk penggunaan sehari-hari — dijalankan tanpa argumen:

```bash
./omega-log.sh
```
jika Anda sudah membuat alias, cukup ketik `log` di terminal baru:
```bash
log
```

Alur umum: layar pembuka → menu utama (dua kolom — Registri kapabilitas/Pustaka/Lihat log/Favorit/Lihat dan tangani IP/Statistik (akses) di satu sisi, Rotate/Bersihkan/Ekspor/Kesehatan log/Opsi/Bantuan di sisi lain) → layar fungsi yang dipilih → kembali ke menu (`Esc`). Bantuan lengkap (`a`) merinci setiap layar, setiap viewer, dan konsep lintas fungsi (elevasi sudo sesekali, status log, pemilihan dengan nomor) — lihat §4 untuk intinya.

#### Pintasan keyboard

| Tombol | Aksi |
|---|---|
| `↑` / `↓` | Berpindah antar elemen di layar |
| `Tab` / `Shift+Tab` | Berpindah antar kolom formulir |
| `Esc` | Kembali ke layar sebelumnya (konfirmasi keluar di layar awal) |
| `t` | Tema berikutnya (langsung diterapkan, tanpa konfirmasi) |
| `r` | Segarkan deteksi terminal |
| `a` | Tampilkan bantuan (lengkap, satu bab per layar) |
| `q` | Keluar (dengan konfirmasi) |

### 3.2. Mode baris perintah (CLI)

Belum setara penuh dengan TUI (favorit, pembersihan... akan hadir dalam fasenya masing-masing, lihat `plan_omega_log.md` §12):

```bash
# Mendeteksi layanan aktif dan log-log yang dikenal
python -m omega_log scan

# + pemindaian manual folder tambahan
python -m omega_log scan --path /var/log

# Versi terpasang, dan perbandingan dengan versi terbaru yang diterbitkan
python -m omega_log version --check

# Cadangan terjadwal yang sudah jatuh tempo (dijalankan setiap malam oleh timer systemd atau crontab)
python -m omega_log rotate run-automations
```

### 3.3. Variabel lingkungan

| Variabel | Efek |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Mengubah lokasi folder status aplikasi (bawaan `./var`, relatif terhadap folder tempat dijalankan) |
| `OMEGA_LOG_LANG` | Memaksa bahasa antarmuka untuk sesi tersebut (mis. `en`, `de`, `ja`) tanpa mengubah pengaturan yang tersimpan |

## 4. Fitur

| Layar | Deskripsi |
|---|---|
| **Registri kapabilitas** | Mendeteksi layanan yang aktif di mesin dan menawarkan impor log-log yang dikenal, satu per satu atau sekaligus. Pemindaian manual folder sebagai pelengkap. |
| **Pustaka** | Hub pusat yang merujuk semua log yang akan ditangani — diisi oleh Registri, impor manual, log yang dikenal dari Omega-Serv, atau salinan yang diambil lewat SSH. |
| **Lihat log** | Pemilihan satu atau beberapa log dari Pustaka + pilihan viewer (1 log → ketiga viewer; 2+ log → hanya `lnav`). |
| **Favorit** | Kombinasi log + viewer yang disimpan dengan sebuah nama, untuk dijalankan langsung. |
| **Lihat dan tangani IP** | 10 IP teratas per periode (24 jam/7 hari/30 hari/semua), atau pencarian IP tertentu (IPv4 atau IPv6), dan penghapusan terarah suatu IP dari satu atau beberapa log. |
| **Statistik (akses)** | Volume, IP unik, tingkat galat, IP teratas, distribusi per jam — ekspor JSON/HTML dengan 5 tema. |
| **Rotate** | Cadangan terkompresi suatu log + retensi otomatis arsip berlebih + pemulihan (penggabungan atau timpa, dengan cadangan pengaman). **Cadangan terjadwal**: sebuah log dicadangkan setiap hari, minggu, atau bulan, dijalankan setiap malam oleh timer systemd atau satu baris di crontab Anda (OpenRC, runit), di bawah akun Anda, tidak pernah root. |
| **Bersihkan** | Mengosongkan isi suatu log (pemotongan di tempat, aman untuk layanan yang masih membukanya) atau menghapus sepenuhnya satu atau beberapa berkas — selalu dengan konfirmasi. |
| **Ekspor** | Ekspor daftar arsip (Rotate) ke JSON atau HTML bertema. |
| **Kesehatan log** | Pemeriksaan hanya-baca atas log di Pustaka, disk, cadangan, dan cadangan terjadwal: hak akses, log yang diam atau rusak, tanggal, logrotate, hari sebelum disk penuh, beserta tindakan yang perlu dilakukan. Perbaikan hak akses yang terlalu terbuka (dengan sudo bila perlu), ekspor JSON/HTML/TXT. |
| **Opsi** | Tema, profil tampilan, bahasa antarmuka dan bahasa ekspor (17 bahasa), pembersihan folder aplikasi (exports/screenshots). |

### 3 viewer

1. **Sederhana** — pemantauan langsung dengan parsing generik (stempel waktu, IP, level, layanan) dan tabel statistik mini. Untuk access log HTTP yang dikenali, kolom tambahan Kode HTTP / latensi, diwarnai menurut ambang batas.
2. **Klasik** — pembacaan baris mentah terakhir + sakelar « Ikuti langsung », tanpa parsing: paling sederhana dan paling andal apa pun formatnya.
3. **lnav** — penggabungan beberapa berkas dalam terminal yang dibungkus (pty), untuk analisis silang. Siklus tema (`t`), penandaan + salin ke papan klip (`Ctrl+C`, OSC 52), keluar (`Ctrl+Q`) — semuanya dicegat sebelum sampai ke `lnav` itu sendiri.

## 5. Kompatibilitas terminal

TUI (Textual) mendeteksi otomatis kemampuan terminal (emulator, ukuran) dan menyesuaikan lembar gaya strukturalnya (`complete`/`standard`/`reduced`/`mono`), tanpa flag manual — kebijakan yang sama untuk seluruh rangkaian `omega-` (`omega-lib`, `terminal/policies.py`). Dapat disegarkan langsung dengan tombol `r`.

### Profil menurut emulator yang terdeteksi

| Emulator | Profil awal |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH modern | `reduced` |
| TTY Linux, SSH lama | `mono` |
| Emulator tidak dikenal | `reduced` (cadangan bawaan) |

### Profil menurut ukuran terminal

| Ukuran minimum (kolom × baris) | Batas atas profil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| di bawahnya | `mono` |

Profil akhir yang dipakai adalah **yang paling ketat dari keduanya** (emulator dan ukuran).

## 6. Arsitektur

Clean Architecture (domain / application / infrastructure / interfaces), konvensi yang sama dengan rangkaian OMEGA lainnya:

```text
src/omega_log/
├── core/            Registri kapabilitas (deteksi layanan)
├── domain/          Logika bisnis murni (parsing, statistik, rotasi, pembersihan)
├── ports/           Kontrak (Protocol)
├── application/     Kasus penggunaan
├── infrastructure/  Implementasi nyata (probe, penyimpanan, arsip, ekspor, lnav, konkurensi)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

Bergantung pada [`omega-lib`](../../../../LIB/omega-lib) untuk tema (10 tema TUI + 5 tema ekspor), deteksi terminal, dan penyimpanan pengaturan — fondasi yang sama dengan rangkaian lainnya. Perhitungan berat (IP teratas, statistik akses) dijalankan di `ProcessPoolExecutor` khusus (`infrastructure/concurrency/`), tidak pernah di thread antarmuka, agar tetap responsif bahkan pada berkas berisi ratusan ribu baris.

## 7. Pengujian

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 pengujian
ruff check .
mypy src
```

Struktur: `tests/unit/` (domain dan application, tanpa I/O nyata), `tests/integration/` (berkas nyata, TUI headless melalui API `Pilot` milik Textual).

## 8. Status pengembangan

Ke-10 fase rencana pengembangan telah selesai: fondasi, domain, TUI dasar, viewer, favorit/pustaka/IP, pemeliharaan, statistik/ekspor, finalisasi, elevasi sudo sesekali, perhitungan berat CPU dipindahkan ke proses terpisah — lihat `plan_omega_log.md` untuk rincian setiap keputusan pemindahan kode. Sejak 1.6.0, fitur baru pengelola log omega-serv 2.6.0 ikut diambil: Kesehatan log, cadangan terjadwal, pencarian IP tertentu, tampilan versi, dan pemeriksaan pembaruan.

## 9. Lisensi

MIT — lihat [LICENSE](../../../LICENSE).

---

> Omega-log — Deteksi, pusatkan, baca, analisis, pelihara.
> Log Anda tetap milik Anda: tanpa elevasi hak istimewa tanpa kebutuhan nyata, tanpa tindakan destruktif tanpa konfirmasi.
