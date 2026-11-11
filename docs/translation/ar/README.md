<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="512">
</div>

# 📜 OMEGA-LOG

**مدير وعارض سجلات الخادم**

> طوّره [kraynux](https://github.com/kraynux) من أجل [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

الصفحة الرسمية: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/ar/) &nbsp; معاينة: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 الواجهة والتوثيق والتصدير متاحة بـ **17 لغة**.  
**اللغات:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](README.md)

---

**Omega-log** هو أداة مجموعة `omega-` المخصّصة لإدارة ملفات سجلات الخادم وقراءتها وتحليلها في واجهة TUI — كشف تلقائي للخدمات النشطة وسجلاتها، ومكتبة مركزية، وثلاثة أوضاع للقراءة (متابعة بسيطة، وقراءة كلاسيكية، ودمج عدة ملفات عبر `lnav`)، ومعالجة عناوين IP، وإحصائيات، وتدوير/نسخ احتياطي/استعادة، وتنظيف آمن، وتصدير. بُني عبر **نقل وتكييف** الشيفرة الناضجة أصلًا من [omega-fire](https://github.com/kraynux) و[omega-serv](https://github.com/kraynux) بدلًا من إعادة كتابتها من الصفر.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ar/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ar/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ar/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ar/omega-log/D.png" width="24%" />
</p>

## 1. الرؤية والنطاق

يجيب Omega-log عن سؤال بسيط: «ماذا يحدث في سجلاتي، وكيف أتعامل معها؟» — دون الاعتماد على قائمة ثابتة من المسارات المعروفة، ودون العمل أبدًا بصلاحيات root افتراضيًا، ودون أن يفقد أو يُفسد بصمت أي ملف سجل حقيقي.

### ما يفعله Omega-log

- يكشف تلقائيًا الخدمات النشطة على الجهاز (خوادم الويب، وقواعد البيانات، والبريد، وDNS، والأمان، و`omega-serv`...) ويقترح استيراد سجلاتها المعروفة، فرادى أو دفعة واحدة — إلى جانب الفحص اليدوي لأي مجلد.
- يجمع السجلات المطلوب معالجتها في مكتبة واحدة، هي نقطة الدخول إلى جميع الشاشات الأخرى.
- يقرأ السجل بأحد ثلاثة أوضاع حسب الحاجة: متابعة بسيطة مع التحليل والإحصائيات، أو قراءة كلاسيكية خام مع المتابعة المباشرة، أو دمج عدة ملفات بتضمين `lnav`.
- يحفظ تركيبات السجلات + العارض في المفضلة، لتشغيلها مباشرة.
- يحسب أعلى 10 عناوين IP حسب الفترة، أو يبحث عن IP محدد، ويتيح حذفها بشكل موجّه من ملف واحد أو أكثر.
- يحسب إحصائيات الوصول (الحجم، وعناوين IP الفريدة، ومعدل الأخطاء، والتوزيع حسب الساعة) القابلة للتصدير بصيغة JSON أو HTML بسمة.
- ينسخ ملفات السجلات احتياطيًا (ضغط + احتفاظ تلقائي)، يدويًا أو كل ليلة عبر النسخ الاحتياطية المجدولة، ويستعيدها (دمج أو استبدال، مع نسخة أمان) وينظّفها (اقتطاع في المكان أو حذف)، دائمًا بعد تأكيد صريح.
- يفحص صحة السجلات (الصلاحيات، والسجلات الصامتة أو التالفة، والمساحة على القرص، والنسخ الاحتياطية) ويوضح ما يجب فعله لكل ملاحظة.
- يتكيّف تلقائيًا مع قدرات الطرفية (الألوان، والحجم) عبر `omega-lib`، مثل بقية المجموعة.

### ما لا يفعله Omega-log

| الوظيفة | الأداة المسؤولة |
|---|---|
| جدار الحماية، وقواعد الشبكة، وكشف التسلل | OMEGA-FIRE |
| خادم الويب، والوكيل العكسي، وWAF، وActive Defense | OMEGA-SERV |
| فحص المنافذ، وتحديد خدمات الشبكة | OMEGA-CHECK |
| مراقبة الشبكة، والهوية الرقمية لهدف ما | OMEGA-TRACK |

لا يوجد (بعد) CLI مكافئ تمامًا لواجهة TUI (وضع سطر الأوامر الحالي لا يغطي سوى فحص الخدمات، انظر §3.2)، ولا تجميع مركزي لعدة أجهزة، ولا تنبيهات فورية عند تجاوز عتبة — يبقى Omega-log أداة فحص وصيانة محلية، وليس SIEM.

### تحذير الاستخدام

إجراءات الصيانة (**تنظيف**، و**Rotate ← استعادة في وضع استبدال (overwrite)**) تعدّل المحتوى الحقيقي لملفات سجلاتك أو تمحوه نهائيًا — ويسبقها دائمًا تأكيد صريح يفصّل الملفات المعنية، ولا تُطلق تلقائيًا أبدًا. عند الشك، خذ نسخة احتياطية (**Rotate ← النسخ الاحتياطي الآن**) قبل التصرف.

## 2. التثبيت

### المتطلبات المسبقة

- Python 3.10+
- Linux (مُختبر على Arch/Manjaro وDebian/Ubuntu وRHEL/Fedora)
- `lnav` مثبّت على النظام، فقط لعارض دمج عدة ملفات (يعمل العارضان الآخران بشكل طبيعي بدونه):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### التثبيت

```bash
[ -d omega-log ] && echo "ℹ️ مستخرج هنا مسبقًا، تم تخطي هذه الخطوة." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. ينشئ البيئة الافتراضية `.venv` إن لم تكن موجودة.
2. يثبّت الاعتماديات (`omega-lib` المضمّنة أولًا إن وُجدت، ثم `pip install -e .` — يبقى `pyproject.toml` المصدر الوحيد للحقيقة).
3. يجعل `omega-log.sh` و`install.sh` قابلين للتنفيذ.
4. يتحقق من وجود `lnav` (تحذير إعلامي إن غاب، ولا يمنع التثبيت أبدًا).
5. يضيف الاسم المستعار `log` إلى `~/.bashrc` و`~/.zshrc` (دون تكرار إن كان موجودًا).

### الاعتماديات

مُعلنة في `pyproject.toml` (لا يوجد `requirements.txt` منفصل):
- `omega-lib`: المكتبة المشتركة للمجموعة (سمات TUI + التصدير، وكشف الطرفية، وتخزين الإعدادات)
- `textual`: واجهة TUI
- `jinja2`: تصدير HTML بسمة (الإحصائيات، والأرشيفات)
- `pyte`: محاكاة الطرفية لعارض `lnav` (العرض داخل pty مضمّن)
- اعتماديات التطوير (`pip install -e ".[dev]"`): `pytest` و`pytest-asyncio` و`ruff` و`mypy`

## 3. الاستخدام

### 3.1. الوضع التفاعلي (TUI)

موصى به للاستخدام اليومي — يُشغَّل دون وسائط:

```bash
./omega-log.sh
```
إذا أنشأت الاسم المستعار، فاكتب فقط `log` في طرفية جديدة:
```bash
log
```

المسار العام: شاشة البدء ← القائمة الرئيسية (عمودان — سجل القدرات/المكتبة/عرض السجلات/المفضلة/عرض ومعالجة IP/الإحصائيات (الوصول) في جهة، وRotate/تنظيف/تصدير/صحة السجلات/الخيارات/مساعدة في الجهة الأخرى) ← شاشة الوظيفة المختارة ← العودة إلى القائمة (`Esc`). تشرح المساعدة الكاملة (`a`) كل شاشة وكل عارض والمفاهيم المشتركة (رفع صلاحيات sudo عند الحاجة، وحالات السجلات، والاختيار بالأرقام) — انظر §4 للأساسيات.

#### اختصارات لوحة المفاتيح

| المفتاح | الإجراء |
|---|---|
| `↑` / `↓` | التنقل بين عناصر الشاشة |
| `Tab` / `Shift+Tab` | التنقل بين حقول النموذج |
| `Esc` | العودة إلى الشاشة السابقة (تأكيد الخروج في شاشة الاستقبال) |
| `t` | السمة التالية (تُطبَّق فورًا، دون تأكيد) |
| `r` | تحديث كشف الطرفية |
| `a` | عرض المساعدة (شاملة، فصل لكل شاشة) |
| `q` | الخروج (مع تأكيد) |

### 3.2. وضع سطر الأوامر (CLI)

لا يوجد بعد تكافؤ كامل مع TUI (المفضلة، والتنظيف... ستأتي في مراحلها الخاصة، انظر `plan_omega_log.md` §12):

```bash
# يكشف الخدمات النشطة وسجلاتها المعروفة
python -m omega_log scan

# + فحص يدوي لمجلد إضافي
python -m omega_log scan --path /var/log

# الإصدار المثبّت، ومقارنته بآخر إصدار منشور
python -m omega_log version --check

# النسخ الاحتياطية المجدولة التي حان موعدها (تُشغَّل كل ليلة عبر مؤقّت systemd أو crontab)
python -m omega_log rotate run-automations
```

### 3.3. متغيرات البيئة

| المتغير | التأثير |
|---|---|
| `OMEGA_LOG_VAR_DIR` | يغيّر موقع مجلد حالة التطبيق (`./var` افتراضيًا، نسبةً إلى مجلد التشغيل) |
| `OMEGA_LOG_LANG` | يفرض لغة الواجهة طوال الجلسة (مثل `en` و`de` و`ja`) دون تغيير الإعداد المحفوظ |

## 4. الميزات

| الشاشة | الوصف |
|---|---|
| **سجل القدرات** | يكشف الخدمات النشطة على الجهاز ويقترح استيراد سجلاتها المعروفة، فرادى أو دفعة واحدة. مع فحص يدوي لمجلد كإضافة. |
| **المكتبة** | المحور المركزي الذي يضم جميع السجلات المطلوب معالجتها — تُغذّى من سجل القدرات، أو بالاستيراد اليدوي، أو بسجلات Omega-Serv المعروفة، أو بنسخة مُسترجعة عبر SSH. |
| **عرض السجلات** | اختيار سجل واحد أو أكثر من المكتبة + اختيار العارض (سجل واحد ← العارضات الثلاثة؛ سجلّان أو أكثر ← `lnav` فقط). |
| **المفضلة** | تركيبات سجلات + عارض محفوظة باسم، للتشغيل المباشر. |
| **عرض ومعالجة IP** | أعلى 10 عناوين IP حسب الفترة (24 س/7 أيام/30 يومًا/الكل)، أو البحث عن IP محدد (IPv4 أو IPv6)، وحذف موجّه لعنوان IP من سجل واحد أو أكثر. |
| **الإحصائيات (الوصول)** | الحجم، وعناوين IP الفريدة، ومعدل الأخطاء، وأعلى عناوين IP، والتوزيع حسب الساعة — تصدير JSON/HTML بـ 5 سمات. |
| **Rotate** | نسخة احتياطية مضغوطة لسجل + احتفاظ تلقائي بالأرشيفات الزائدة + استعادة (دمج أو استبدال، مع نسخة أمان). **النسخ الاحتياطية المجدولة**: نسخ سجل احتياطيًا كل يوم أو أسبوع أو شهر، يُنفَّذ كل ليلة عبر مؤقّت systemd أو سطر في crontab الخاص بك (OpenRC، runit)، بحسابك، وليس بصلاحيات root أبدًا. |
| **تنظيف** | يفرغ محتوى سجل (اقتطاع في المكان، آمن لخدمة لا تزال تفتحه) أو يحذف ملفًا واحدًا أو أكثر بالكامل — دائمًا مع تأكيد. |
| **تصدير** | تصدير قائمة الأرشيفات (Rotate) بصيغة JSON أو HTML بسمة. |
| **صحة السجلات** | فحص للقراءة فقط لسجلات المكتبة، والقرص، والنسخ الاحتياطية، والنسخ الاحتياطية المجدولة: الصلاحيات، والسجلات الصامتة أو التالفة، والتواريخ، وlogrotate، والأيام المتبقية قبل امتلاء القرص، مع الإجراء الواجب اتخاذه. تصحيح الصلاحيات المفتوحة أكثر من اللازم (مع sudo عند الحاجة)، وتصدير JSON/HTML/TXT. |
| **الخيارات** | السمة، وملف العرض، ولغة الواجهة ولغة التصدير (17 لغة)، وتنظيف مجلدات التطبيق (exports/screenshots). |

### العارضات الثلاثة

1. **بسيط** — متابعة مباشرة مع تحليل عام (الطابع الزمني، وIP، والمستوى، والخدمة) وجدول إحصائيات مصغّر. لسجل وصول HTTP معروف، أعمدة إضافية لرمز HTTP / زمن الاستجابة، ملوّنة حسب العتبة.
2. **كلاسيكي** — قراءة آخر الأسطر الخام + مفتاح «متابعة مباشرة»، دون تحليل: الأبسط والأكثر موثوقية أيًّا كان التنسيق.
3. **lnav** — دمج عدة ملفات داخل طرفية مضمّنة (pty)، لتحليل متقاطع. تبديل السمة (`t`)، والتحديد + النسخ إلى الحافظة (`Ctrl+C`، OSC 52)، والخروج (`Ctrl+Q`) — كلها تُعترض قبل `lnav` نفسه.

## 5. توافق الطرفيات

تكشف واجهة TUI (Textual) قدرات الطرفية تلقائيًا (المحاكي، والحجم) وتكيّف ورقة أنماطها الهيكلية وفقًا لذلك (`complete`/`standard`/`reduced`/`mono`)، دون أي خيار يدوي — وهي السياسة نفسها التي تتشاركها مجموعة `omega-` بأكملها (`omega-lib`، `terminal/policies.py`). يمكن تحديثها مباشرة بالمفتاح `r`.

### الملف حسب المحاكي المكتشف

| المحاكي | الملف الأولي |
|---|---|
| Ghostty وAlacritty وWezTerm وKitty | `complete` |
| Konsole وGNOME Terminal وTerminator وXfce4 Terminal | `standard` |
| xterm وurxvt وSSH حديث | `reduced` |
| TTY لينكس، وSSH قديم | `mono` |
| محاكي غير معروف | `reduced` (الخيار الافتراضي البديل) |

### الملف حسب حجم الطرفية

| الحجم الأدنى (أعمدة × أسطر) | سقف الملف |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| أقل من ذلك | `mono` |

الملف المعتمد في النهاية هو **الأكثر تقييدًا بين الاثنين** (المحاكي والحجم).

## 6. البنية

Clean Architecture (النطاق / التطبيق / البنية التحتية / الواجهات)، بالاصطلاح نفسه المتّبع في بقية مجموعة OMEGA:

```text
src/omega_log/
├── core/            سجل القدرات (كشف الخدمات)
├── domain/          منطق الأعمال الصرف (التحليل، والإحصائيات، والتدوير، والتنظيف)
├── ports/           العقود (Protocol)
├── application/     حالات الاستخدام
├── infrastructure/  التنفيذات الفعلية (probes، والتخزين، والأرشيفات، والتصدير، وlnav، والتزامن)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

يعتمد على [`omega-lib`](../../../../LIB/omega-lib) للسمات (10 سمات TUI + 5 سمات تصدير)، وكشف الطرفية، وتخزين الإعدادات — الأساس نفسه لبقية المجموعة. تُنفَّذ الحسابات الثقيلة (أعلى عناوين IP، وإحصائيات الوصول) داخل `ProcessPoolExecutor` مخصّص (`infrastructure/concurrency/`)، وليس أبدًا على خيط الواجهة، لتبقى الواجهة سريعة الاستجابة حتى مع ملف من مئات الآلاف من الأسطر.

## 7. الاختبارات

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 اختبارًا
ruff check .
mypy src
```

البنية: `tests/unit/` (النطاق والتطبيق، دون I/O حقيقي)، و`tests/integration/` (ملفات حقيقية، وTUI دون واجهة عبر واجهة `Pilot` البرمجية في Textual).

## 8. حالة التطوير

اكتملت المراحل العشر لخطة التطوير: الأساس، والنطاق، وTUI الأساسية، والعارضات، والمفضلة/المكتبة/IP، والصيانة، والإحصائيات/التصدير، والإنهاء، ورفع صلاحيات sudo عند الحاجة، ونقل الحسابات كثيفة المعالج إلى عملية منفصلة — انظر `plan_omega_log.md` لتفاصيل كل قرار نقل. منذ الإصدار 1.6.0، أُدرجت مستجدات مدير السجلات في omega-serv 2.6.0: صحة السجلات، والنسخ الاحتياطية المجدولة، والبحث عن IP محدد، وعرض الإصدار، والتحقق من التحديثات.

## 9. الترخيص

MIT — انظر [LICENSE](../../../LICENSE).

---

> Omega-log — اكتشف، اجمع، اقرأ، حلّل، صُن.
> تبقى سجلاتك ملكك: لا رفع للصلاحيات دون حاجة حقيقية، ولا إجراء مدمّر دون تأكيد.
