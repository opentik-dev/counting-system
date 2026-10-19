# دليل البدء والاستئناف من جهاز جديد

هذا الدليل يعيد تشغيل مشروع **Warehouse Vision Counting System** من آخر حالة
موثقة في GitHub.

المستودع:

```text
git@github.com:opentik-dev/counting-system.git
```

الفرع الحالي: `main`  
آخر حالة منشورة: `822edd3`  
حالة المشروع: نواة MVP مكتملة، وبوابة التحقق الميداني `T017` ما زالت قيد التنفيذ.

## 1. تجهيز حساب GitHub وSSH

على الجهاز الجديد، أنشئ مفتاحًا جديدًا بدل نقل المفتاح الخاص من الجهاز القديم:

```bash
ssh-keygen -t ed25519 -C "opentik-dev@opentik.win"
cat ~/.ssh/id_ed25519.pub
```

انسخ المفتاح العام فقط إلى:

```text
GitHub → Settings → SSH and GPG keys → New SSH key
```

ثم اختبر الاتصال:

```bash
ssh -T git@github.com
```

لا ترفع ملف `id_ed25519` أو ترسله لأي شخص. الملف الذي ينتهي بـ `.pub` هو
المفتاح العام المسموح بإضافته إلى GitHub.

## 2. استنساخ المشروع

```bash
git clone git@github.com:opentik-dev/counting-system.git
cd counting-system
git status
```

يجب أن يظهر الفرع `main` متتبعًا لـ `origin/main`.

## 3. إعداد بيئة Python للنواة

يتطلب المشروع Python 3.11 أو أحدث. يفضل إنشاء بيئة منفصلة داخل المشروع:

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

اختبر التثبيت:

```bash
.venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python -m warehouse_counting.demo
```

النتيجة المتوقعة حاليًا: `13 passed`، ثم ظهور حدثي `CARTON_IN` و`PALLET_OUT`.

## 4. بيئة الرؤية والتدريب — اختيارية

لا تحتاج النواة إلى PyTorch أو YOLO. عند الانتقال إلى أدوات التدريب فقط:

```bash
.venv/bin/python -m pip install -r requirements-cpu.txt
```

هذه التبعيات كبيرة وتحتاج مساحة واتصالًا بالإنترنت. لا تثبتها لمجرد تشغيل
الاختبارات الأساسية.

## 5. نقل فيديوهات المستودع والبيانات

الفيديوهات والبيانات والأوزان غير مرفوعة إلى GitHub عمدًا، بسبب الحجم والخصوصية
وحقوق الاستخدام. انقلها بشكل منفصل إلى قرص خارجي أو تخزين خاص، ثم نظمها مثلًا:

```text
<data-root>/warehouse-site-001/
├── raw-videos/
├── frames/
├── labels/
├── ground-truth/
└── manifests/
```

لا تضع فيديوهات الموقع داخل `tests/`. هذا المجلد مخصص للاختبارات البرمجية،
والفيديوهات الموجودة فيه في الجهاز القديم ليست جزءًا من النسخة المنشورة.

لاستخراج إطارات من فيديو القبول:

```bash
python3 scripts/extract_frames.py \
  <data-root>/warehouse-site-001/raw-videos/*.mp4 \
  --output <data-root>/warehouse-site-001/frames \
  --interval 1
```

## 6. نقطة الاستئناف الحالية

المهمة التالية هي `T017` في
[`specs/001-mvp-counting/tasks.md`](../specs/001-mvp-counting/tasks.md):

1. تصوير فيديو ثابت من موقع العمل.
2. تحديد الكاميرا وخط العد واتجاه `IN/OUT`.
3. إعداد سجل عد يدوي للحقيقة الأرضية.
4. فصل فيديو القبول عن بيانات التدريب.
5. تحديد نسبة الخطأ المقبولة قبل بناء محول YOLO/Segmentation.

لا ينبغي إضافة كاميرا مباشرة أو نموذج إنتاجي قبل إكمال هذه البوابة.

## 7. سير العمل اليومي

ابدأ كل جلسة بـ:

```bash
git checkout main
git pull --ff-only
git status
```

أنشئ فرعًا لكل مهمة:

```bash
git switch -c feature/fixed-view-evaluation
```

بعد التعديل:

```bash
.venv/bin/python -m pytest -q
git diff --check
git status
git add <files>
git commit -m "Document fixed-view evaluation protocol"
git push -u origin feature/fixed-view-evaluation
```

ثم افتح Pull Request إلى `main`. لا ترفع ملفات الفيديو أو الأوزان أو مجلد
`.venv`.

## 8. ملفات يجب قراءتها قبل التطوير

- [`README.md`](../README.md): التعريف والتشغيل العام.
- [`docs/architecture.md`](architecture.md): حدود المعمارية.
- [`docs/evaluation.md`](evaluation.md): سياسة التقييم.
- [`ROADMAP.md`](../ROADMAP.md): المراحل التالية.
- [`CONTRIBUTING.md`](../CONTRIBUTING.md): قواعد المساهمة.
- [`specs/001-mvp-counting/spec.md`](../specs/001-mvp-counting/spec.md): المتطلبات.
- [`specs/001-mvp-counting/plan.md`](../specs/001-mvp-counting/plan.md): القرارات الفنية.
