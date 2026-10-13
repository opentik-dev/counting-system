# Warehouse Vision Counting System

**اللغات / Languages:** [العربية](README.md) · [English](docs/README.en.md) · [Français](docs/README.fr.md) · [Español](docs/README.es.md) · [Türkçe](docs/README.tr.md) · [中文](docs/README.zh-CN.md)

[![CI](https://github.com/opentik-dev/counting-system/actions/workflows/ci.yml/badge.svg)](https://github.com/opentik-dev/counting-system/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](pyproject.toml)

نواة محلية صغيرة لنظام عد كراتين وطبليات المخازن. الإصدار الحالي لا يدّعي أنه نموذج رؤية؛ بل يثبت الجزء الذي يجب أن يبقى دقيقًا وقابلًا للتدقيق: تحويل عبور جسم متتبع لخط إلى حدث `IN/OUT`، منع التكرار، وتخزين الدليل في SQLite.

**الحالة:** MVP قيد التحقق الميداني — الاختبارات الأساسية ناجحة، لكن دقة الرؤية
الإنتاجية لم تعتمد بعد.

للمعمارية وسياسة التقييم وخارطة الطريق، راجع
[`docs/architecture.md`](docs/architecture.md)،
[`docs/evaluation.md`](docs/evaluation.md)، و[`ROADMAP.md`](ROADMAP.md).

## التشغيل

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m warehouse_counting.demo
```

لا توجد تبعيات تشغيلية خارج Python القياسي في هذه المرحلة. يتم استخدام `pytest` للاختبارات فقط.

## الحدود الحالية

- المدخلات: `TrackObservation` من أي كاشف/متتبع.
- الأنواع: `carton` و`pallet`.
- المسار: خط عد واحد واتجاهان.
- التخزين: SQLite محلي.
- الطبليات: لا تتحول إلى كراتين إلا بقاعدة صريحة مثل `30 كرتون/طبليّة`.
- المؤجل: RTSP/ONVIF، تتبع الفيديو في CVAT، تشغيل نموذج segmentation في الإنتاج، تعدد الكاميرات، API، لوحة العرض، ERP.

## دعوة مجتمع المطورين

المشروع مفتوح للمطورين والباحثين وأصحاب الخبرة التشغيلية في المستودعات. نرحب
بالمساهمات في منطق العد، أدوات الوسم، الاختبارات، التوثيق، الترجمة، وتجارب
البيانات الواقعية.

للمساهمة: راجع [`CONTRIBUTING.md`](CONTRIBUTING.md)، افتح Issue عند وجود فكرة
أو مشكلة، ثم أرسل Pull Request صغيرًا ومختبرًا. نبحث خصوصًا عن مساهمين يساعدون
في بناء فيديو قبول ثابت وحقيقة أرضية يدوية قبل اعتماد نموذج الرؤية للإنتاج.

## تقييم الفيديو الحالي

الملف `tests/كراتين الشحن.mp4` صالح تقنيًا: H.264، مدة تقارب 30 ثانية، `1920×1080`، و`904/904` إطار تم فكها بنجاح. بصريًا هو فيديو محمول عمودي داخل إطار عريض، يعرض رفوفًا ولقطات قريبة وأشخاصًا يحملون كراتين.

الحكم: مناسب كبداية لتجميع أمثلة فئة `carton`، وغير مناسب بعد لقياس `IN/OUT` أو دقة العد؛ لا توجد كاميرا ثابتة أو بوابة عبور أو حقيقة أرضية يدوية. لم يُشغّل كشف YOLO لأن اعتماد `ultralytics` ووزن النموذج غير موجودين، ولا ينبغي تثبيتهما قبل اعتماد مشهد الاختبار.

## تقييم مجموعة الفيديوهات

تم فحص 8 مقاطع في `tests/` وفكّها كاملة بنجاح. التصنيف التالي مبني على عينات زمنية موزعة، وليس على وسم إطار بإطار:

| المقطع | القيمة الأساسية | يصلح لاختبار خط العد؟ |
|---|---|---|
| `machine_ltd [DP48EK-kj6o]` | رفوف وتكديس كراتين، حجب جزئي | لا؛ تدريب كشف فقط |
| `maicon_serra [DMdyZ8xPnq0]` | مستودع واسع، ممرات وطبليات | محدود؛ سياق مستودع |
| `petercargoglobal [DTiUToSka5C]` | مستودع ومناولة/رافعة | لا؛ تدريب سياق ورافعة |
| `petercargoglobal [DVXCTWCkdsZ]` | منطقة تحميل، طبليات ورافعة | لا؛ لا يوجد مسار ثابت موثق |
| `petercargoglobal [DZwJW0vikja]` | كراتين مربوطة وأشخاص ولقطات قريبة | لا؛ كشف وحجب |
| `petercargoglobal [DaOZksso2Yu]` | تحميل/تفريغ حاوية وكراتين | لا؛ تدريب تنوع ومناولة |
| `rtechwelding [C-VXrx0opGg]` | عامل وكراتين وحمولة/منصة | لا؛ حالات صعبة ورافعة |
| `كراتين الشحن` | كراتين شحن قريبة | لا؛ أمثلة كشف أولية |

القرار: تُستخدم هذه المجموعة كمصادر تدريب/تنويع بعد التأكد من حق الاستخدام، ولا تُستخدم كحقيقة أرضية أو معيار دقة نهائي. معيار القبول يجب أن يأتي من كاميرا ثابتة في مستودعنا ومسار محدد وعدّ يدوي مطابق.

لاستخراج إطارات مراجعة وملف مصدر قابل للتتبع:

```bash
python3 scripts/extract_frames.py tests/*.mp4 --output datasets/seed --interval 1
```

تُستخدم الفئات الأولية الموجودة في [`annotation-classes.txt`](config/annotation-classes.txt) عند المراجعة والوسم. الإطارات المستخرجة غير موسومة بعد؛ لا يجوز تدريب نموذج نهائي منها قبل مراجعة الوسوم وفصل بيانات التدريب عن فيديو القبول.

## وسم الصور محليًا

يمكن تشغيل أداة رسومية خفيفة لوسم الصور المستخرجة دون تعديلها:

```bash
python3 scripts/annotate_images.py datasets/seed \
  --classes config/annotation-classes.txt \
  --labels-out datasets/seed/labels
```

اختر الفئة من الأزرار أو المفاتيح `1–5`، اسحب مستطيلًا حول الكائن الظاهر، ثم اضغط `Save / Next`. تحفظ الأداة ملفات YOLO منفصلة داخل `datasets/seed/labels`. هذه الأداة مناسبة لصور الكشف الأولية؛ تتبع الكائن عبر الفيديو ومراجعة الفرق يبقيان من اختصاص CVAT لاحقًا.

## أداة وسم المخازن متعددة الأشكال

مجلد الصور اختياري الآن. يمكن بدء مشروع فارغ، ثم استيراد مجلد أو صور محددة أو فتح مشروع سابق من الأزرار داخل الواجهة:

```bash
python3 scripts/annotate_warehouse.py \
  --classes config/warehouse-classes.txt \
  --workspace datasets/annotation-workspace
```

ينشئ المشروع مجلد `reference_images/` للصور المرجعية ومجلد `labels/` للوسوم. الأوضاع: `B` مستطيل، `C` دائرة/بيضاوي، `P` مضلع بالنقر ثم `Enter` أو زر الفأرة الأيمن، و`F` رسم حر غير منتظم بالسحب. يمكن أيضًا تمرير مجلد حقيقي عند البدء:

```bash
python3 scripts/annotate_warehouse.py /real/path/to/images \
  --classes config/warehouse-classes.txt \
  --workspace datasets/annotation-workspace
```

تُحفظ الأشكال بصيغة YOLO-Segmentation، ولا تُعدّل الصور الأصلية. زر `Import folder` يستورد مجلدًا كاملًا، و`Import images` يستورد مجموعة ملفات، و`Open project` يفتح مشروعًا يحتوي `reference_images/` و`labels/`.

لتجميع المشروع في حزمة COCO و`manifest.csv` و`data.yaml`:

```bash
python3 scripts/build_warehouse_dataset.py datasets/annotation-workspace/reference_images \
  --labels datasets/annotation-workspace/labels \
  --classes config/warehouse-classes.txt \
  --output datasets/warehouse-seg-v1 --exclude-empty
python3 scripts/validate_segmentation_dataset.py \
  --images datasets/warehouse-seg-v1/images \
  --labels datasets/warehouse-seg-v1/labels \
  --classes config/warehouse-classes.txt --require-complete
```

قائمة الفئات الموسعة في [`warehouse-classes.txt`](config/warehouse-classes.txt) تشمل الكرتون، الطبليّة، الرافعة، الأشخاص، المركبات، الجالون المعدني، الحاوية، الرف، الراك، عربة الطبليات، والسير الناقل. يمكن إضافة فئة من الملف دون تعديل الكود.

## جمع مادة خام جديدة

لجمع مادة خام جديدة، استخدم [`annotate_warehouse.py`](scripts/annotate_warehouse.py) على مجلد الصور:

```bash
python3 scripts/annotate_warehouse.py /path/to/raw-images \
  --classes config/warehouse-classes.txt \
  --labels-out datasets/raw-warehouse/labels
```

الأوضاع: `B` مستطيل، `C` دائرة/بيضاوي، `P` مضلع بالنقر ثم `Enter` أو زر الفأرة الأيمن، و`F` رسم حر غير منتظم بالسحب. اختر الفئة من الأزرار أو المفاتيح `1–9`. تحفظ الأشكال بصيغة YOLO-Segmentation، ولا تُعدّل الصور الأصلية.

لتجميع الصور والوسوم في حزمة تدريب مع `COCO annotations.json` و`manifest.csv` و`data.yaml`:

```bash
python3 scripts/build_warehouse_dataset.py /path/to/raw-images \
  --labels datasets/raw-warehouse/labels \
  --classes config/warehouse-classes.txt \
  --output datasets/warehouse-seg-v1 --exclude-empty
python3 scripts/validate_segmentation_dataset.py \
  --images datasets/warehouse-seg-v1/images \
  --labels datasets/warehouse-seg-v1/labels \
  --classes config/warehouse-classes.txt --require-complete
```

قائمة الفئات الموسعة موجودة في [`warehouse-classes.txt`](config/warehouse-classes.txt) وتشمل الكرتون، الطبليّة، الرافعة، الأشخاص، المركبات، الجالون المعدني، الحاوية، الرف، الراك، عربة الطبليات، والسير الناقل. يمكن إضافة فئة في هذا الملف دون تعديل الأداة. حُوّلت المجموعة الحالية ذات الصناديق إلى `datasets/warehouse_seg_v1` تلقائيًا بصيغة مضلعات رباعية، واجتازت الفحص (`217` صورة و`1458` مضلعًا).

لتدقيق الناتج قبل التدريب:

```bash
python3 scripts/validate_yolo_dataset.py \
  --images datasets/seed \
  --labels datasets/seed/labels \
  --classes config/annotation-classes.txt
```

المدقق يفحص الصيغة، والنطاقات، وأسماء الملفات، وتوزيع الفئات. لا يغني عن مراجعة الصناديق فوق الصور. أُبعدت خاتمتا CapCut إلى `datasets/seed/excluded/capcut_outro`، وأصبحت المجموعة الفعالة `217` صورة و`1458` صندوقًا بلا ملفات مفقودة أو زائدة.

لتجهيز نسخة YOLO قابلة لإعادة البناء مع فصل المقاطع حسب المصدر:

```bash
python3 scripts/prepare_yolo_dataset.py
```

الناتج في `datasets/yolo_v1`: `118` تدريب، `66` تحقق، `33` اختبار، مع `data.yaml` و`split_manifest.csv`. هذا تقسيم تمهيدي لبيانات تنويع خارجية، وليس معيار قبول للمستودع؛ لا تزال هناك حاجة إلى فيديو ثابت من موقع العمل وحقيقة أرضية يدوية.

المراجعة البصرية الأولية فحصت 3 عينات من كل تقسيم مع إظهار الصناديق فوق الصور؛ لم يظهر انزياح هندسي واضح، وتوجد بعض التداخلات الطبيعية بين `pallet` و`carton`. تبقى مراجعة بشرية شاملة قبل التدريب النهائي، خصوصًا لتثبيت قاعدة هل نريد كشف الطبليّة والصناديق معًا.

بيئة التدريب CPU قابلة لإعادة الإنشاء من [`requirements-cpu.txt`](requirements-cpu.txt) داخل `.venv`. لتجربة قصيرة:

```bash
YOLO_CONFIG_DIR=/tmp/Ultralytics MPLCONFIGDIR=/tmp/mpl-cache \
  .venv/bin/python scripts/train_yolo.py --epochs 1 --imgsz 320 --batch 16 --device cpu \
  --name baseline_cpu_1epoch
```

استخدم `yolo11n.pt` للتدريب المسبق عند توفر الوزن؛ واستخدم `yolo11n.yaml` لاختبار المسار من الصفر دون تنزيل وزن. تجربة الصفر الحالية أكملت حقبة واحدة ونتيجتها `mAP=0`، وهي تحقق تشغيل فقط وليست تقييمًا للنموذج.

تم تشغيل خط أساس مسبق التدريب لخمس حقب على CPU. على التحقق: `mAP50=0.0412` و`mAP50-95=0.0207`، وعلى الاختبار: `mAP50=0.0324` و`mAP50-95=0.0105`. فئة `carton` على الاختبار بلغت `mAP50=0.113`، بينما `truck=0`. المعاينة التنبؤية لم تُظهر صناديق مفيدة عند عتبات `0.25` و`0.05` في العينات المعروضة؛ لذلك هذا وزن مقارنة فقط، ولا يصلح للعد أو التشغيل.

تم التحقق من ملف Compose الرسمي لـCVAT، لكن لم تُشغّل خدماته بعد بسبب حاجته إلى عدة صور Docker والمساحة الحرة المحدودة. يمكن استخدام الأداة الخفيفة الآن لوسم الصور، ثم الانتقال إلى CVAT عند الحاجة إلى تتبع الفيديو أو العمل الجماعي.

## خريطة العمل

القرارات والمتطلبات في [`spec.md`](specs/001-mvp-counting/spec.md)، والخطة في [`plan.md`](specs/001-mvp-counting/plan.md)، وقائمة التنفيذ في [`tasks.md`](specs/001-mvp-counting/tasks.md). أوامر Spec-Kit موجودة في `.specify/commands/`.

## تسليم الوكلاء

آخر حالة: اكتملت `T001–T016` و`T018–T027`، وفُحصت مجموعة من 8 مقاطع في `T017` بنجاح تقني، واستُخرج منها `219` إطارًا في `datasets/seed` مع `manifest.csv`. أُبعدت لقطتا CapCut غير المرتبطتين، وبُني `datasets/yolo_v1` بتقسيم مصدرّي: `118/66/33` للتدريب/التحقق/الاختبار. أضيفت أداة وسم متعددة الأشكال مع استيراد مجلد/صور وفتح مشروع مرجعي، ومجمّع YOLO-Segmentation/COCO، وفاحص مستقل؛ حُوّلت الوسوم الحالية إلى `datasets/warehouse_seg_v1` وفازت بـ`PASS` (`217` صورة و`1458` مضلعًا)، كما اجتاز المشروع `13` اختبارًا. ثُبّتت بيئة CPU محلية وشُغّل خط أساس مسبق التدريب لخمس حقب؛ النتيجة منخفضة (`mAP50=0.0412` تحقق، `0.0324` اختبار) والوزن للمقارنة فقط. المجموعة تدريب/تنويع وليست معيار عد نهائيًا؛ الأولوية التالية تنفيذ `T017`: فيديو ثابت من الموقع وحقيقة أرضية يدوية قبل إضافة محول الرؤية.

عند نهاية كل جلسة، حدّث `tasks.md` وبدّل هذه الفقرة إلى: ما تم، أمر التحقق ونتيجته، المشكلة/الافتراض، والخطوة التالية الدقيقة. عند وجود فشل معماري أو اختلاف في المتطلبات، أوقف التوسع وأعد القرار إلى وكيل Codex الأساسي للمراجعة.
