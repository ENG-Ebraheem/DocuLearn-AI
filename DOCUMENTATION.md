 # توثيق نظام DocuLearn AI الشامل (Technical Documentation)

مرحباً بك في التوثيق التقني الشامل لنظام **DocuLearn AI** — منصة التعليم الذكي وإدارة المستندات المدعومة بالذكاء الاصطناعي والمعمارية النظيفة (Clean Architecture / DDD).

---

## 1. نظرة عامة على المشروع (Project Overview)

### وصف المشروع
**DocuLearn AI** هو تطبيق تفاعلي ذكي مبني باستخدام **Python** و **Streamlit**، يهدف إلى تحويل المستندات التعليمية والكتب (PDF, DOCX, XLSX, TXT) إلى بيئة تعليمية تفاعلية شخصية. يعتمد النظام على تقنية **الاسترجاع المدعوم بالوليد (RAG - Retrieval-Augmented Generation)** الهجينة لاستخراج الإجابات الدقيقة من المستندات مع الهوامش والمراجع، إضافة إلى محرك تعليمي متكامل يولد الملخصات، المفاهيم الأساسية، الاختبارات التفاعلية (Quizzes)، والبطاقات الاستذكارية (Flashcards) المدعومة بالتكرار المتباعد (Spaced Repetition).

### الميزات الرئيسية (Key Features)
* **المعالجة الذكية للمستندات (Smart Document Ingestion & Quality Analysis)**:
  * دعم استخراج النصوص من ملفات PDF (عبر PyMuPDF)، Word (عبر python-docx)، Excel (عبر pandas/openpyxl)، والملفات النصية.
  * نظام تطهير وتطبيع خاص باللغة العربية (`ArabicNormalizer`) لإزالة التشكيل والتطويل وتوحيد صيغ الألف والياء والتاء المربوطة.
  * تحليل جودة النص المُستخرج تلقائياً (`TextQualityAnalyzer`) واكتشاف الملفات الممسوخة ضوئياً التي تحتاج إلى OCR.
* **تقسيم النصوص الذكي (Page-Aware Chunking)**:
  * تقسيم النصوص بنظام النافذة المنزلقة (Sliding Window) مع الحفاظ على حدود الصفحات والروابط المرجعية (Metadata).
* **البحث الهجين (Hybrid RAG Retrieval)**:
  * دمج البحث المتجهي الدلالي (Dense Vector Search) باستخدام نموذج `SentenceTransformers` (`all-MiniLM-L6-v2`) وفهرس `FAISS`.
  * دمج البحث اللفظي (Lexical Search - BM25).
  * الدمج الخوارزمي بين البحثين باستخدام رتبة الانصهار المتبادل (RRF - Reciprocal Rank Fusion) أو الأوزان المرجحة (Weighted Score Fusion).
* **توليد الإجابات الذكي (Context-Aware Q&A)**:
  * تقييم مدى كفاية السياق (Context Sufficiency Analysis) قبل إرسال الاستعلام للموديل.
  * الاستعانة بـ Google Gemini LLM عبر الحزمة الرسمية `google-genai` مع خيار المزود البديل (Fallback Provider).
* **المحرك التعليمي المتكامل (AI Learning Engine)**:
  * توليد ملخصات متعددة المستويات (شاملة، تنفيذية، نقاط رئيسية).
  * استخراج المصطلحات والمفاهيم الأساسية مع تعريفاتها.
  * توليد أسئلة واختبارات تفاعلية متعددة الخيارات (MCQ) وصح/خطأ وأسئلة مقالية، مع محرك تصحيح ذكي وإعطاء تغذية راجعة تفصيلية.
  * توليد بطاقات بطاقات خاطفة (Flashcards) ومتابعة مستوى إتقان الطالب ومعدل المراجعة.
* **إدارة المواد والتقدم (Course Management & Analytics Dashboard)**:
  * تنظيم المستندات في مواد دراسية (Courses) وعزل الاستعلامات بين المستندات.
  * لوحة تحكم وإحصائيات شامِلة لنسب الإتقان والاختبارات المنجزة وساعات الدراسة.

---

## 2. المتطلبات والتشغيل (Installation & Setup)

### المتطلبات الأساسية (Prerequisites)
* **Python 3.10+** أو إصدار أحدث.
* بيئة افتراضية (Virtual Environment) تضمن استقرار المكتبات.
* مفتاح تطبيق Google Gemini API (`GEMINI_API_KEY`).

### التثبيت (Installation Steps)

1. **إنشاء وتفعيل البيئة الافتراضية**:
   ```bash
   python -m venv app/.venv
   # على Windows PowerShell:
   app\.venv\Scripts\Activate.ps1
   # على Linux/macOS:
   source app/.venv/bin/activate
   ```

2. **تثبيت المكتبات المطلوبة**:
   ```bash
   pip install -r requirements.txt
   ```

3. **إعداد متغيرات البيئة**:
   قم بإنشاء ملف `.env` في المجلد الرئيسي بناءً على `.env.example`:
   ```env
   APP_NAME="DocuLearn AI"
   ENVIRONMENT="development"
   DATABASE_URL="sqlite:///data/app.db"
   UPLOADS_DIR="data/uploads"
   VECTOR_STORE_PATH="data/vector_store"
   EMBEDDING_MODEL="all-MiniLM-L6-v2"
   LLM_PROVIDER="gemini"
   LLM_MODEL="gemini-3.5-flash"
   GEMINI_API_KEY="your_actual_gemini_api_key_here"
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=150
   TOP_K=5
   RAG_MIN_CONTEXT_SCORE=0.42
   MAX_UPLOAD_SIZE_MB=50
   LOG_LEVEL="INFO"
   ```

### كيفية التشغيل (Running the Application)

تشغيل التطبيق باستخدام Streamlit:
```bash
python -m streamlit run app/main.py
```
أو تشغيل السكريبت المباشر:
```bash
python run.py
```
سيكون التطبيق متاحاً عبر المتصفح على العنوان: `http://localhost:8501`.

---

## 3. هيكلية المجلدات (Directory Structure)

```text
DEV_Doculearn_AI/
├── app/                                  # مجلد التطبيق الرئيسي
│   ├── main.py                           # نقطة الانطلاق لتطبيق Streamlit وإدارة الصفحات
│   ├── bootstrap.py                      # جذر التكوين (Composition Root) لربط الحقن وحفظ الكائنات الثقيلة
│   ├── health.py                         # فحص صحة وجاهزية النظام (Health Checks)
│   ├── config/                           # إعدادات النظام وتكوين متغيرات البيئة
│   │   └── settings.py                   # صنف Settings المبني على Pydantic BaseSettings
│   ├── core/                             # النواة والاستثناءات المخصصة
│   │   └── exceptions.py                 # تعريف تسلسل الاستثناءات (Custom Exceptions Hierarchy)
│   ├── domain/                           # طبقة النطاق (Domain Layer - DDD)
│   │   ├── entities/                     # كيانات النطاق النقية (Document, Chunk, Course, Quiz, etc.)
│   │   └── repositories/                 # الواجهات المجرّدة لمستودعات البيانات والمزودات
│   ├── application/                      # طبقة التطبيق والتنفيذ (Application Use Cases)
│   │   └── services/                     # الخدمات المركزية وواجهة التعامل Facade
│   │       ├── platform_service.py       # واجهة PlatformService الشاملة للتطبيق
│   │       ├── document_processing_pipeline.py # خط معالجة المستندات وفهرستها
│   │       ├── learning/                 # حالات استخدام المحرك التعليمي (Summaries, Quizzes, Flashcards)
│   │       └── rag/                      # حالات استخدام استرجاع الأسئلة والإجابات (Hybrid RAG, Q&A)
│   ├── infrastructure/                   # طبقة البنية التحتية والتقنيات الخارجية (Infrastructure)
│   │   ├── database/                     # نماذج SQLAlchemy واستجابة مستودعات البيانات SQLite
│   │   ├── document_processing/          # استخراج النصوص (PDF, DOCX, XLSX, TXT)
│   │   ├── embeddings/                   # مزود التجهيز المتجهي (SentenceTransformers)
│   │   ├── llm/                          # مزودات نماذج اللغة الكبيرة (Gemini Provider & Fallback)
│   │   └── vector_store/                 # قاعدة البيانات المتجهية المعتمدة على FAISS
│   ├── presentation/                     # طبقة العرض والواجهات (Presentation Layer)
│   │   ├── pages/                        # صفحات التطبيق (Dashboard, Library, Chat, Study, Analytics)
│   │   ├── components/                   # المكونات التفاعلية والبطاقات للشاشة
│   │   ├── state/                        # إدارة حالة الجلسة (Session State Manager)
│   │   └── styles/                       # نسق وألوان الواجهة (Custom CSS Themes)
│   └── services/                         # خدمات مساعدة لتطهير وتقسيم النص
│       └── text_processing/              # تنظيف النصوص، المعالجة العربية، وتقسيم الصفحات
├── data/                                 # مجلد قواعد البيانات والملفات المرفوعة والمتجهات
├── tests/                                # الاختبارات الآلية (Unit & Integration Tests)
├── Dockerfile                            # ملف بناء حاوية Docker
├── requirements.txt                      # التبعيات والمكتبات المطلوبة
└── run.py                                # سكريبت تشغيل مباشر للتطبيق
```

---

## 4. المعمارية وتدفق العمل (Architecture & Workflow)

يعتمد المشـروع على نمط **المعمارية النظيفة (Clean Architecture / Domain-Driven Design)** حيث تكون تفاصيل البنية التحتية (مثل FAISS, SQLAlchemy, Gemini) فصلت تماماً عن منطق العمل الأساسي (Domain Logic).

### مخطط تدفق العمل المعماري (Architectural Data Flow)



### خط سير عملية رفع وفهرسة مستند (Document Ingestion Pipeline)

1. **الرفع (Upload)**: يرفع المستخدم الملف عبر صفحة المكتبة (`library.py`).
2. **التحقق والاستخراج (Validation & Extraction)**: يتحقق `PlatformService` من الحجم والامتداد، ثم يُستخرج النص بواسطة `DocumentExtractor`.
3. **التنظيف والتحليل (Clean & Quality Analysis)**: يمر النص بـ `TextCleaner` ثم يُحلل بواسطة `TextQualityAnalyzer`. إذا كانت الجودة ضعيفة (نسبة استبدال عالية أو شواهد ضئيلة)، يُعلم المستند بـ `NEEDS_OCR`.
4. **التقسيم (Chunking)**: يُقسم النص بـ `TextChunker` مع مراعاة الصفحات.
5. **التضمين المتجهي والتخزين (Embedding & Vector Storage)**: يُنشئ `SentenceTransformerEmbeddingProvider` مصفوفات التضمين (`all-MiniLM-L6-v2` بأبعاد 384)، وتُخزن المتجهات في `FAISSVectorStore` والنصوص في قاعدة البيانات SQLite.
6. **التحديث (State Update)**: تتحول حالة المستند إلى `INDEXED`.

---

## 5. تفاصيل الخوارزميات والمنطق الأساسي (Core Logic & Algorithms)

### 1. خوارزمية التطبيع والمعالجة العربية (`ArabicNormalizer`)
تعتمد على تعابير نمطية (Regex) لتطبيع النصوص العربية دون المساس بصحة التوثيق الاقتباسي:
* **حذف التشكيل**: إزالة الحركات `[\u0617-\u061a\u064b-\u065f\u0670]`.
* **تطبيع الألف والياء والتاء المربوطة**: تحويل (`أ`, `إ`, `آ`) إلى `ا`؛ تحويل `ى` إلى `ي`؛ تحويل `ة` إلى `ه`.
* **حذف التطويل (Tatweel)**: إزالة الرمز `\u0640`.

### 2. خوارزمية تحليل جودة النص (`TextQualityAnalyzer`)
تولد خوارزمية التحليل مؤشر جودة $QualityScore \in [0, 1]$ بناءً على المقاييس التالية:
$$\text{ArabicRatio} = \frac{\text{Count}(\text{Arabic Chars})}{\text{Total Chars}}$$
$$\text{ReplacementRatio} = \frac{\text{Count}(\text{Unprintable / } \text{\ufffd})}{\text{Total Chars}}$$
إذا كان المؤشر أقل من العتبة المحددة، يُصنّف المستند بـ `NEEDS_OCR`.

### 3. خوارزمية البحث الهجين وانصهار الدرجات (Hybrid RRF & Weighted Score Fusion)

#### أ. Fusion الموزون (Weighted Score Fusion):
يتم تحجيم درجات البحث اللفظي والبحث المتجهي بين 0 و 1 ثم دمجها:
$$Score_{fused}(d) = w_{dense} \cdot \frac{S_{dense}(d)}{S_{max,dense}} + w_{lexical} \cdot \frac{S_{lexical}(d)}{S_{max,lexical}}$$
حيث $w_{dense} = 0.7$ و $w_{lexical} = 0.3$.

#### ب. رتبة الانصهار المتبادل (Reciprocal Rank Fusion - RRF):
تعتمد RRF على ترتيب العناصر وليس على قيم الدرجات المطلقة:
$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
حيث $r_m(d)$ هي رتبة المستند $d$ في الخوارزمية $m$، و $k = 60$.

### 4. خوارزمية الفهرسة والتصفية في FAISS (`FAISSVectorStore`)
* يتم استخدام فهرس ضرب داخلي مسطح (`faiss.IndexFlatIP`) بأبعاد 384.
* لضمان عمل الفلترة بحسب المستند (`document_id`) دون الحاجة لإعادة إنشاء الفهرس كلياً في كل استعلام، تحسب الخوارزمية `_filtered_search` مصفوفة ضرب المتجهات بالنقط المتطابقة (Dot Product) وتستخرج أفضل $K$ نتائج مصفاة في الزمن $O(N_{doc} \cdot D)$.

### 5. تعقيد الخوارزميات (Time & Space Complexity)

| الخوارزمية / العملية | التعقيد الزمني (Time Complexity) | التعقيد المكاني (Space Complexity) | ملاحظات |
| :--- | :--- | :--- | :--- |
| **Normalizer / Cleaner** | $O(N)$ | $O(N)$ | حيث $N$ طول النص |
| **Sliding Window Chunker** | $O(N)$ | $O(N)$ | تقسيم النص مع تداخل ثابت |
| **Dense Vector Encoding** | $O(M \cdot L)$ | $O(M \cdot D)$ | $M$ عدد المقاطع، $D=384$ الأبعاد |
| **FAISS Flat Search** | $O(K \cdot D + N_{total} \cdot D)$ | $O(N_{total} \cdot D)$ | بحث دقيق عبر ضرب المتجهات |
| **Weighted/RRF Fusion** | $O(C \log C)$ | $O(C)$ | $C$ عدد المرشحين المسترجعين |

---

## 6. توثيق الوحدات والأصناف (Modules & API Documentation)

### 1. وحدة التكوين والجذر [`app/bootstrap.py`](file:///c:/Development/Projects/python/DEV_Doculearn_AI/app/bootstrap.py)

#### `create_platform_service() -> PlatformService`
* **الغرض**: إنشاء جلسة قاعدة بيانات مفردة لكل طلب مع الاستفادة من الموارد الثقيلة المشتركة.
* **المخرجات**: كائن `PlatformService` الجاهز للاستخدام من طبقة العرض.

---

### 2. وحدة الواجهة الرئيسية [`app/application/services/platform_service.py`](file:///c:/Development/Projects/python/DEV_Doculearn_AI/app/application/services/platform_service.py)

#### `PlatformService`
الصنف المحوري (Facade Pattern) الذي يستدعي جميع حالات الاستخدام للنظام.

##### الدوال الرئيسية:
* **`ingest_uploaded_document(file_name: str, content: bytes, course_id: str | None = None) -> IngestionResult`**
  * **المدخلات**: اسم الملف، المحتوى بالبايت، ومعرف المادة الاختياري.
  * **الغرض**: التحقق من الملف وإمراره عبر خط المعالجة وحفظه في SQLite و FAISS.
* **`delete_document(document_id: str) -> None`**
  * **المدخلات**: معرف المستند `document_id`.
  * **الغرض**: الحذف المتتابع (Cascade Delete) للمستند من قاعدة البيانات، الأجزاء، الفهرس المتجهي، الملفات المرفوعة، والدردشات المرتبطة.

---

### 3. وحدة البحث والاسترجاع الهجين [`app/application/services/rag/hybrid_retriever.py`](file:///c:/Development/Projects/python/DEV_Doculearn_AI/app/application/services/rag/hybrid_retriever.py)

#### `HybridRetriever`
تدمج بين البحث المتجهي واللفظي.

##### الدوال الرئيسية:
* **`retrieve(query: str, top_k: int | None = None, document_id: str | None = None) -> list[RetrievedChunk]`**
  * **المدخلات**: النص الاستعلامي `query`، عدد النتائج `top_k`، ومعرف المستند المفلتر `document_id`.
  * **المخرجات**: قائمة من `RetrievedChunk` مرتبة حسب الأفضلية.

---

### 4. وحدة الاستجابة الذكية [`app/application/services/rag/qa_service.py`](file:///c:/Development/Projects/python/DEV_Doculearn_AI/app/application/services/rag/qa_service.py)

#### `QAService`
تتولى الإجابة عن أسئلة المستخدم عبر RAG.

##### الدوال الرئيسية:
* **`answer(query: str, conversation_id: str | None = None, document_id: str | None = None) -> AnswerResponse`**
  * **المدخلات**: سؤال المستخدم، معرف المحادثة، ومعرف المستند.
  * **المخرجات**: كائن `AnswerResponse` يحتوي النص المولّد، المراجع (Sources)، ومدى كفاية السياق.

---

## 7. أمثلة الاستخدام (Usage Examples)

### مثال 1: معالجة وفهرسة مستند جديد برمجيًا
```python
from app.bootstrap import create_platform_service

# إنشاء خدمة المنصة
service = create_platform_service()

try:
    with open("sample_lecture.pdf", "rb") as f:
        file_bytes = f.read()

    # رفع وفهرسة المستند
    result = service.ingest_uploaded_document(
        file_name="sample_lecture.pdf",
        content=file_bytes
    )

    print(f"تمت الفهرسة بنجاح! معرف المستند: {result.document.id}")
    print(f"عدد الأجزاء المفهرسة: {len(result.chunks)}")
finally:
    service.close()
```

### مثال 2: إجراء استعلام RAG والإجابة عن سؤال
```python
from app.bootstrap import create_platform_service

service = create_platform_service()

try:
    # إجراء محادثة واستجابة دقيقة
    qa_service = service.qa_service()
    response = qa_service.answer(
        query="ما هي التعريفات الرئيسية الواردة في الفصل الأول؟",
        document_id="doc_12345"
    )

    print("الإجابة:", response.answer)
    print("المراجع والمصادر:")
    for src in response.sources:
        print(f"- صفحة {src.get('page')}: {src.get('document_name')}")
finally:
    service.close()
```

### مثال 3: توليد اختبار تفاعلي وتصحيحه
```python
from app.bootstrap import create_platform_service

service = create_platform_service()

try:
    # توليد اختبار من 5 أسئلة
    quiz = service.generate_quiz(
        document_id="doc_12345",
        num_questions=5,
        difficulty="medium"
    )

    print(f"تم توليد الاختبار: {quiz.title} برقم {quiz.id}")
    
    # تصحيح إجابات المستخدم
    user_answers = {quiz.questions[0].id: 0} # إجابة السؤال الأول
    result = service.submit_quiz(quiz.id, user_answers)
    print(f"النتيجة: {result.score_percentage}% - {result.feedback}")
finally:
    service.close()
```

---

> [!NOTE]
> هذا التوثيق التقني محين ويلتزم بجميع قواعد وحالات استخدام المشروع. يمكنك الرجوع لكل ملف عبر الروابط المدمجة أو تشغيل الاختبارات الآلية عبر `pytest tests/` للتأكد من السلامة البرمجية.
