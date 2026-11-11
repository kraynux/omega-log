<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="512">
</div>

# 📜 OMEGA-LOG

**Trình quản lý và xem log máy chủ**

> Được xây dựng bởi [kraynux](https://github.com/kraynux) cho [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Trang chính thức: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/vi/) &nbsp; Xem trước: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 Giao diện, tài liệu và bản xuất có sẵn bằng **17 ngôn ngữ**.  
**Ngôn ngữ:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** là công cụ của bộ `omega-` chuyên dùng để quản lý, đọc và phân tích các tệp log máy chủ trong TUI — tự động phát hiện các dịch vụ đang hoạt động và log của chúng, thư viện trung tâm, ba chế độ đọc (theo dõi đơn giản, đọc cổ điển, hợp nhất nhiều tệp qua `lnav`), xử lý IP, thống kê, xoay vòng/sao lưu/khôi phục, dọn dẹp an toàn và xuất dữ liệu. Được xây dựng bằng cách **chuyển và điều chỉnh** mã nguồn đã hoàn thiện của [omega-fire](https://github.com/kraynux) và [omega-serv](https://github.com/kraynux) thay vì viết lại từ đầu.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/vi/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/vi/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/vi/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/vi/omega-log/D.png" width="24%" />
</p>

## 1. Tầm nhìn và phạm vi

Omega-log trả lời một câu hỏi đơn giản: « chuyện gì đang xảy ra trong log của tôi, và tôi xử lý nó thế nào? » — không phụ thuộc vào một danh sách cố định các đường dẫn đã biết, không bao giờ chạy bằng root theo mặc định, và không bao giờ âm thầm làm mất hay làm hỏng một tệp log thật.

### Omega-log làm được gì

- Tự động phát hiện các dịch vụ đang hoạt động trên máy (máy chủ web, cơ sở dữ liệu, mail, DNS, bảo mật, `omega-serv`...) và đề xuất nhập các log đã biết của chúng, từng cái một hoặc toàn bộ — bổ sung cho việc quét thủ công bất kỳ thư mục nào.
- Tập trung các log cần xử lý vào một Thư viện duy nhất, điểm vào của mọi màn hình khác.
- Đọc một log theo ba chế độ tùy nhu cầu: theo dõi đơn giản có phân tích và thống kê, đọc thô cổ điển có theo dõi trực tiếp, hoặc hợp nhất nhiều tệp bằng cách nhúng `lnav`.
- Ghi nhớ các tổ hợp log + trình xem dưới dạng Yêu thích, để khởi chạy trực tiếp.
- Tính top 10 IP theo khoảng thời gian, hoặc tìm một IP cụ thể, và cho phép xóa có chọn lọc chúng khỏi một hoặc nhiều tệp.
- Tính thống kê truy cập (lưu lượng, IP duy nhất, tỷ lệ lỗi, phân bố theo giờ), có thể xuất ra JSON hoặc HTML có giao diện.
- Sao lưu (nén + tự động lưu giữ), thủ công hoặc mỗi đêm qua các bản sao lưu theo lịch, khôi phục (hợp nhất hoặc ghi đè, kèm bản sao lưu an toàn) và dọn dẹp (cắt ngắn tại chỗ hoặc xóa) các tệp log, luôn có xác nhận rõ ràng.
- Kiểm tra tình trạng log (quyền, log im lặng hoặc bị hỏng, dung lượng đĩa, bản sao lưu) và cho biết cần làm gì với từng phát hiện.
- Tự động thích ứng với khả năng của terminal (màu sắc, kích thước) qua `omega-lib`, giống phần còn lại của bộ công cụ.

### Omega-log không làm gì

| Chức năng | Công cụ phụ trách |
|---|---|
| Tường lửa, quy tắc mạng, phát hiện xâm nhập | OMEGA-FIRE |
| Máy chủ web, reverse proxy, WAF, Active Defense | OMEGA-SERV |
| Quét cổng, nhận diện dịch vụ mạng | OMEGA-CHECK |
| Quan sát mạng, danh tính số của một mục tiêu | OMEGA-TRACK |

(Chưa) có CLI tương đương hoàn toàn với TUI (chế độ dòng lệnh hiện tại chỉ bao gồm việc quét dịch vụ, xem §3.2), không có tổng hợp tập trung nhiều máy, không có cảnh báo thời gian thực theo ngưỡng — Omega-log vẫn là một công cụ kiểm tra và bảo trì cục bộ, không phải một SIEM.

### Cảnh báo khi sử dụng

Các thao tác bảo trì (**Dọn**, **Rotate → Khôi phục ở chế độ Ghi đè**) sửa đổi hoặc xóa vĩnh viễn nội dung thật của các tệp log — luôn có một bước xác nhận rõ ràng liệt kê chi tiết các tệp liên quan, không bao giờ tự động kích hoạt. Nếu còn phân vân, hãy sao lưu (**Rotate → Sao lưu ngay**) trước khi thao tác.

## 2. Cài đặt

### Yêu cầu

- Python 3.10+
- Linux (đã thử trên Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` được cài trên hệ thống, chỉ cần cho trình xem hợp nhất nhiều tệp (hai trình xem còn lại hoạt động bình thường mà không cần nó):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Cài đặt

```bash
[ -d omega-log ] && echo "ℹ️ Đã giải nén ở đây, bỏ qua bước này." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Tạo môi trường ảo `.venv` nếu nó chưa tồn tại.
2. Cài đặt các phụ thuộc (bản `omega-lib` đi kèm trước nếu có, sau đó `pip install -e .` — `pyproject.toml` vẫn là nguồn chuẩn duy nhất).
3. Cấp quyền thực thi cho `omega-log.sh` và `install.sh`.
4. Kiểm tra sự có mặt của `lnav` (cảnh báo mang tính thông tin nếu thiếu, không bao giờ chặn).
5. Thêm alias `log` vào `~/.bashrc` và `~/.zshrc` (không trùng lặp nếu đã có).

### Phụ thuộc

Khai báo trong `pyproject.toml` (không có `requirements.txt` riêng):
- `omega-lib`: thư viện dùng chung của bộ công cụ (giao diện TUI + xuất, phát hiện terminal, lưu trữ cài đặt)
- `textual`: giao diện TUI
- `jinja2`: xuất HTML có giao diện (thống kê, bản lưu trữ)
- `pyte`: giả lập terminal cho trình xem `lnav` (hiển thị trong một pty nhúng)
- Phụ thuộc phát triển (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Sử dụng

### 3.1. Chế độ tương tác (TUI)

Khuyên dùng hằng ngày — khởi chạy không kèm tham số:

```bash
./omega-log.sh
```
nếu bạn đã tạo alias, chỉ cần gõ `log` trong một terminal mới:
```bash
log
```

Luồng chung: màn hình khởi động → menu chính (hai cột — một bên là Sổ đăng ký khả năng/Thư viện/Xem log/Yêu thích/Xem và xử lý IP/Thống kê, bên kia là Rotate/Dọn/Xuất/Tình trạng log/Tùy chọn/Trợ giúp) → màn hình của chức năng đã chọn → quay lại menu (`Esc`). Trợ giúp đầy đủ (`a`) mô tả chi tiết từng màn hình, từng trình xem và các khái niệm chung (nâng quyền sudo tạm thời, trạng thái của log, chọn theo số) — xem §4 để biết những điểm chính.

#### Phím tắt

| Phím | Hành động |
|---|---|
| `↑` / `↓` | Di chuyển giữa các phần tử của màn hình |
| `Tab` / `Shift+Tab` | Di chuyển giữa các trường của biểu mẫu |
| `Esc` | Quay lại màn hình trước (xác nhận thoát ở màn hình chính) |
| `t` | Giao diện tiếp theo (áp dụng ngay, không cần xác nhận) |
| `r` | Làm mới việc phát hiện terminal |
| `a` | Hiện trợ giúp (đầy đủ, mỗi màn hình một chương) |
| `q` | Thoát (có xác nhận) |

### 3.2. Chế độ dòng lệnh (CLI)                                                              

Chưa tương đương hoàn toàn với TUI (yêu thích, dọn... sẽ có trong các giai đoạn riêng, xem `plan_omega_log.md` §12):

```bash
# Phát hiện các dịch vụ đang hoạt động và các log đã biết của chúng
python -m omega_log scan

# + quét thủ công thêm một thư mục
python -m omega_log scan --path /var/log

# Phiên bản đã cài, và so sánh với phiên bản mới nhất đã phát hành
python -m omega_log version --check

# Các bản sao lưu theo lịch đã đến hạn (chạy mỗi đêm bởi timer systemd hoặc crontab)
python -m omega_log rotate run-automations
```

### 3.3. Biến môi trường

| Biến | Tác dụng |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Thay đổi vị trí thư mục trạng thái của ứng dụng (`./var` theo mặc định, tương đối so với thư mục khởi chạy) |
| `OMEGA_LOG_LANG` | Buộc dùng ngôn ngữ giao diện cho phiên làm việc (vd. `en`, `de`, `ja`) mà không đổi cài đặt đã lưu |

## 4. Tính năng

| Màn hình | Mô tả |
|---|---|
| **Sổ đăng ký khả năng** | Phát hiện các dịch vụ đang hoạt động trên máy và đề xuất nhập các log đã biết của chúng, từng cái một hoặc toàn bộ. Bổ sung quét thủ công một thư mục. |
| **Thư viện** | Trung tâm tham chiếu mọi log cần xử lý — được nạp từ Sổ đăng ký, nhập thủ công, các log đã biết của Omega-Serv hoặc một bản sao lấy về qua SSH. |
| **Xem log** | Chọn một hoặc nhiều log trong Thư viện + chọn trình xem (1 log → cả 3 trình xem; 2+ log → chỉ `lnav`). |
| **Yêu thích** | Các tổ hợp log + trình xem được lưu dưới một tên, để khởi chạy trực tiếp. |
| **Xem và xử lý IP** | Top 10 IP theo khoảng thời gian (24h/7 ngày/30 ngày/tất cả), hoặc tìm một IP cụ thể (IPv4 hoặc IPv6), và xóa có chọn lọc một IP khỏi một hoặc nhiều log. |
| **Thống kê (truy cập)** | Lưu lượng, IP duy nhất, tỷ lệ lỗi, top IP, phân bố theo giờ — xuất JSON/HTML với 5 giao diện. |
| **Rotate** | Sao lưu nén một log + tự động lưu giữ, loại bỏ các bản lưu trữ dư thừa + khôi phục (hợp nhất hoặc ghi đè, kèm bản sao lưu an toàn). **Sao lưu theo lịch**: một log được sao lưu mỗi ngày, tuần hoặc tháng, chạy mỗi đêm bởi một timer systemd hoặc một dòng trong crontab của bạn (OpenRC, runit), dưới tài khoản của bạn, không bao giờ là root. |
| **Dọn** | Làm trống nội dung một log (cắt ngắn tại chỗ, an toàn với dịch vụ vẫn đang mở nó) hoặc xóa hẳn một hoặc nhiều tệp — luôn có xác nhận. |
| **Xuất** | Xuất danh sách bản lưu trữ (Rotate) ra JSON hoặc HTML có giao diện. |
| **Tình trạng log** | Kiểm tra chỉ đọc các log trong Thư viện, ổ đĩa, bản sao lưu và các bản sao lưu theo lịch: quyền, log im lặng hoặc bị hỏng, ngày tháng, logrotate, số ngày trước khi đầy đĩa, kèm việc cần làm. Sửa các quyền quá rộng (dùng sudo nếu cần), xuất JSON/HTML/TXT. |
| **Tùy chọn** | Giao diện, hồ sơ hiển thị, ngôn ngữ giao diện và ngôn ngữ bản xuất (17 ngôn ngữ), dọn các thư mục của ứng dụng (exports/screenshots). |

### 3 trình xem

1. **Đơn giản** — theo dõi trực tiếp với phân tích chung (dấu thời gian, IP, mức độ, dịch vụ) và một bảng thống kê nhỏ. Với một access log HTTP được nhận diện, có thêm cột Mã HTTP / độ trễ, tô màu theo ngưỡng.
2. **Cổ điển** — đọc các dòng thô cuối cùng + chuyển sang « Theo dõi trực tiếp », không phân tích: đơn giản và đáng tin cậy nhất bất kể định dạng.
3. **lnav** — hợp nhất nhiều tệp trong một terminal nhúng (pty), để phân tích chéo. Đổi giao diện (`t`), đánh dấu + sao chép vào bộ nhớ tạm (`Ctrl+C`, OSC 52), thoát (`Ctrl+Q`) — tất cả đều được chặn trước khi tới chính `lnav`.

## 5. Tương thích terminal

TUI (Textual) tự động phát hiện khả năng của terminal (trình giả lập, kích thước) và điều chỉnh bảng kiểu cấu trúc tương ứng (`complete`/`standard`/`reduced`/`mono`), không cần cờ thủ công — cùng một chính sách dùng chung cho cả bộ `omega-` (`omega-lib`, `terminal/policies.py`). Có thể làm mới trực tiếp bằng phím `r`.

### Hồ sơ theo trình giả lập được phát hiện

| Trình giả lập | Hồ sơ ban đầu |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH hiện đại | `reduced` |
| TTY Linux, SSH cũ | `mono` |
| Trình giả lập không nhận diện được | `reduced` (dự phòng mặc định) |

### Hồ sơ theo kích thước terminal

| Kích thước tối thiểu (cột × dòng) | Mức hồ sơ tối đa |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| nhỏ hơn | `mono` |

Hồ sơ cuối cùng được chọn là **hồ sơ hạn chế nhất trong hai** (trình giả lập và kích thước).

## 6. Kiến trúc

Clean Architecture (miền / ứng dụng / hạ tầng / giao diện), cùng quy ước với phần còn lại của bộ OMEGA:

```text
src/omega_log/
├── core/            Sổ đăng ký khả năng (phát hiện dịch vụ)
├── domain/          Logic nghiệp vụ thuần (phân tích, thống kê, xoay vòng, dọn dẹp)
├── ports/           Hợp đồng (Protocol)
├── application/     Ca sử dụng
├── infrastructure/  Triển khai thực tế (thăm dò, lưu trữ, bản lưu trữ, xuất, lnav, đồng thời)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

Phụ thuộc vào [`omega-lib`](../../../../LIB/omega-lib) cho giao diện (10 giao diện TUI + 5 giao diện xuất), phát hiện terminal và lưu trữ cài đặt — cùng nền tảng với phần còn lại của bộ công cụ. Các phép tính nặng (top IP, thống kê truy cập) chạy trong một `ProcessPoolExecutor` riêng (`infrastructure/concurrency/`), không bao giờ trên luồng giao diện, để luôn phản hồi nhanh ngay cả với một tệp vài trăm nghìn dòng.

## 7. Kiểm thử

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 bài kiểm thử
ruff check .
mypy src
```

Cấu trúc: `tests/unit/` (miền và ứng dụng, không có I/O thật), `tests/integration/` (tệp thật, TUI không giao diện qua API `Pilot` của Textual).

## 8. Tình trạng phát triển

10 giai đoạn của kế hoạch phát triển đã hoàn tất: nền tảng, miền, TUI cơ bản, trình xem, yêu thích/thư viện/IP, bảo trì, thống kê/xuất, hoàn thiện, nâng quyền sudo tạm thời, chuyển các phép tính nặng về CPU sang tiến trình riêng — xem `plan_omega_log.md` để biết chi tiết từng quyết định chuyển mã. Từ bản 1.6.0, các tính năng mới của trình quản lý log trong omega-serv 2.6.0 được đưa vào: Tình trạng log, sao lưu theo lịch, tìm một IP cụ thể, hiển thị phiên bản và kiểm tra cập nhật.

## 9. Giấy phép

MIT — xem [LICENSE](../../../LICENSE).

---

> Omega-log — Phát hiện, tập trung, đọc, phân tích, bảo trì.
> Log của bạn vẫn là của bạn: không nâng quyền khi không thật sự cần, không thao tác phá hủy nào mà không có xác nhận.
