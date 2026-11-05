# داکیومنت توسعه محصول (Product Development Document)
## سیستم فروشگاهی آنلاین — Backend: FastAPI | Frontend: Angular 22

**نسخه:** 1.0
**نوع سند:** Product & Technical Architecture Document
**رویکرد توسعه:** MVP-first → Iterative & Incremental

---

## پیش‌فرض‌ها و مفروضات (Assumptions)

چون جزئیات دقیق کسب‌وکار (بازار هدف، تک‌فروشنده یا مولتی‌ورندور، درگاه‌های پرداخت مدنظر و...) مشخص نشده بود، این سند بر پایه فرضیات زیر نوشته شده. اگر با نیاز واقعی شما فرق دارد، بگویید تا اصلاح شود:

| مورد | فرض در نظر گرفته‌شده |
|---|---|
| مدل کسب‌وکار | تک‌فروشنده (Single-vendor) B2C — قابل توسعه به Multi-vendor در فازهای بعد |
| دیتابیس اصلی | PostgreSQL |
| کش / صف پیام | Redis |
| مدیریت پروژه Angular | دو پروژه مستقل Angular CLI (نه Nx Monorepo)، هرکدام در Repository جدا — طبق ADR-010 (سند شماره ۴) |
| درگاه پرداخت | انتزاعی (Abstract Payment Gateway) — تا افزودن چند درگاه (زرین‌پال، آیدی‌پی، پی‌پال و...) ساده باشد |
| زیرساخت اولیه | Docker Compose روی یک یا چند سرور؛ مسیر تکاملی به سمت Kubernetes |

---

## ۱. هدف سند

این سند نقشه راه فنی و معماری توسعه یک سیستم فروشگاهی است که:
1. یک **MVP سریع، پایدار و قابل توسعه** را در کوتاه‌ترین زمان ممکن ارائه می‌دهد.
2. معماری‌ای طراحی می‌کند که افزودن ویژگی‌های جدید (Coupon، Multi-vendor، Search پیشرفته، Loyalty و...) نیاز به بازنویسی نداشته باشد.
3. مرز مشخصی بین سه پروژه اصلی ترسیم می‌کند: **Backend API**، **Storefront (سایت مشتری)**، **Admin Panel**.

---

## ۲. Technology Stack

| لایه | تکنولوژی | توضیح |
|---|---|---|
| Backend Framework | FastAPI (Python 3.12+) | Async, Type-safe, OpenAPI خودکار |
| ORM / DB Driver | SQLAlchemy 2.0 (Async) + asyncpg | |
| Validation | Pydantic v2 | Schema validation و serialization |
| Migration | Alembic | |
| Database | PostgreSQL 16+ | |
| Cache / Queue Broker | Redis | Cache، Session، Celery/ARQ broker |
| Background Jobs | Celery یا ARQ | ایمیل، فاکتور، پردازش‌های سنگین |
| Frontend Framework | Angular 22 | Standalone Components، Signals، New Control Flow |
| مدیریت پروژه Frontend | Angular CLI استاندارد (بدون Nx) | دو پروژه مستقل در دو Repository جدا — ADR-010 |
| Frontend State | Angular Signals (+ NgRx SignalStore برای Admin در موارد پیچیده) | |
| UI - Storefront | Tailwind CSS + کامپوننت‌های اختصاصی | برندینگ و تجربه کاربری اهمیت بالا دارد |
| UI - Admin Panel | PrimeNG یا Angular Material | سرعت توسعه CRUD و جدول‌ها |
| Auth | JWT (Access + Refresh Token) / OAuth2 Password Flow | |
| Containerization | Docker / Docker Compose | |
| CI/CD | GitHub Actions | Lint → Test → Build → Deploy |
| Monitoring (فاز بعد) | Sentry، Prometheus + Grafana | |
| Search (فاز بعد) | Meilisearch یا Elasticsearch | در MVP، Postgres Full-Text Search کافی است |

---

## ۳. اصول معماری کلی

- **Modular Monolith در Backend**: به‌جای Microservices از ابتدا (که برای MVP overhead غیرضروری دارد)، یک مونولیت با مرزبندی دامنه‌ای (Domain Modules) طراحی می‌شود که در آینده هرکدام از ماژول‌ها در صورت نیاز واقعی قابل استخراج به سرویس مجزا هستند.
- **جدایی کامل Backend از Frontend**: ارتباط صرفاً از طریق REST API + OpenAPI Contract.
- **دو Frontend مستقل، یک Backend مشترک**: Storefront و Admin Panel هر دو از همان API استفاده می‌کنند اما با Scope/Permission متفاوت.
- **API-first Design**: هر ویژگی جدید ابتدا با تعریف Schema/Contract طراحی می‌شود، سپس پیاده‌سازی.
- **Feature-based نه Layer-based**: کد بر اساس دامنه کسب‌وکار (products، orders، cart) سازمان‌دهی می‌شود، نه صرفاً لایه‌های فنی.

---

## ۴. معماری Backend (FastAPI)

### ۴.۱ ساختار پروژه (Domain-Driven Modular Monolith)

```
backend/
├── app/
│   ├── core/                  # config, security, dependencies, exceptions
│   ├── db/                    # session, base model, migrations (alembic)
│   ├── modules/
│   │   ├── auth/               # login, refresh token, register
│   │   ├── users/               # profile, addresses
│   │   ├── catalog/             # products, categories, brands, attributes
│   │   ├── inventory/           # stock management
│   │   ├── cart/
│   │   ├── orders/
│   │   ├── payments/            # abstract gateway + implementations
│   │   ├── discounts/           # coupons, campaigns (Phase 2)
│   │   ├── reviews/             # (Phase 2)
│   │   ├── notifications/       # email/sms/push
│   │   ├── media/               # upload/CDN
│   │   ├── search/
│   │   └── admin_dashboard/     # aggregated stats for admin
│   ├── shared/                 # shared schemas, utils, pagination
│   └── main.py
├── tests/
├── alembic/
└── pyproject.toml
```

هر ماژول (مثلاً `catalog`) به‌صورت داخلی این لایه‌بندی را دارد:

```
catalog/
├── router.py         # API endpoints
├── schemas.py        # Pydantic DTOs (Request/Response)
├── models.py          # SQLAlchemy models
├── service.py         # Business logic
├── repository.py      # Data access layer
└── exceptions.py
```

**دلیل این ساختار:** جداسازی Router (لایه HTTP) از Service (منطق کسب‌وکار) و Repository (دسترسی داده) باعث می‌شود تست‌نویسی، جایگزینی دیتابیس، و افزودن ویژگی جدید بدون دست‌زدن به سایر ماژول‌ها ممکن باشد.

### ۴.۲ ماژول‌های دامنه‌ای فروشگاه (Domain Modules)

| ماژول | مسئولیت | فاز |
|---|---|---|
| `auth` | ثبت‌نام، ورود، Refresh Token، Forgot Password | MVP |
| `users` | پروفایل، آدرس‌ها | MVP |
| `catalog` | محصولات، دسته‌بندی، برند، ویژگی‌ها (Variant/Attribute) | MVP |
| `inventory` | موجودی، رزرو موجودی هنگام خرید | MVP |
| `cart` | سبد خرید (Guest + User) | MVP |
| `orders` | ثبت سفارش، وضعیت سفارش، تاریخچه | MVP |
| `payments` | Abstract Gateway Interface + پیاده‌سازی درگاه | MVP (یک درگاه) |
| `admin_dashboard` | آمار پایه، مدیریت سفارش/محصول | MVP |
| `discounts` | کد تخفیف، کمپین | Phase 2 |
| `reviews` | نظر و امتیاز محصول | Phase 2 |
| `notifications` | ایمیل/پیامک/پوش نوتیفیکیشن | Phase 2 |
| `search` | جستجوی پیشرفته (Meilisearch/Elasticsearch) | Phase 2/3 |
| `media` | مدیریت آپلود تصاویر، CDN | MVP (ساده) → Phase 2 (کامل) |

### ۴.۳ لایه داده (Data Layer)

- SQLAlchemy 2.0 Async + `asyncpg`
- هر migration باید از طریق Alembic و با بررسی دستی (Auto-generate + Review) انجام شود.
- Repository Pattern برای جداسازی query از منطق کسب‌وکار.

### ۴.۴ Background Jobs

برای عملیات‌هایی که نباید Request کاربر را بلاک کنند (ارسال ایمیل تأیید سفارش، صدور فاکتور، ری‌ایندکس محصول در Search): استفاده از **Celery** یا **ARQ** با Redis به‌عنوان broker. برای MVP، ARQ به‌دلیل سبک‌تر بودن و سازگاری async پیشنهاد می‌شود.

### ۴.۵ Caching & Search

- **Cache**: Redis برای کش کردن دسته‌بندی‌ها، لیست محصولات پرتردد، Session Rate-limiting.
- **Search MVP**: PostgreSQL Full-Text Search (`tsvector`) کافی و بدون overhead زیرساختی است.
- **Search Phase 2/3**: مهاجرت به Meilisearch (سبک‌تر و ساده‌تر) یا Elasticsearch (در صورت نیاز به قابلیت‌های پیشرفته‌تر) وقتی حجم محصولات/ترافیک جستجو بالا رفت.

### ۴.۶ API Design Standards

- Versioning: `/api/v1/...`
- خروجی OpenAPI خودکار FastAPI به‌عنوان Single Source of Truth برای Contract بین Backend و هر دو Frontend.
- فرمت یکسان خطا (Error Envelope) در کل پروژه — پیشنهاد پیروی از الگوی مشابه RFC 7807 (Problem Details).
- Pagination استاندارد (`limit`/`offset` یا `cursor`) برای همه لیست‌ها.

---

## ۵. معماری Frontend (Angular 22)

### ۵.۱ ساختار Repository (به‌روزرسانی — Nx Monorepo کنار گذاشته شد)

> **به‌روزرسانی معماری (به‌همراه ADR-010 در سند شماره ۴ - ADR):** به‌جای Nx Monorepo، در نسخه فعلی دو پروژه Angular کاملاً مستقل و هرکدام در یک Git Repository جدا ایجاد می‌شوند تا از پیچیدگی و overhead راه‌اندازی/یادگیری Nx در مرحله شروع پرهیز شود.

```
storefront-frontend/         (Repository مستقل — Angular CLI استاندارد)
├── src/
│   ├── app/
│   │   ├── core/              # interceptors, guards, app config
│   │   ├── features/          # هر صفحه/دامنه (product, cart, checkout, ...)
│   │   └── shared/             # کامپوننت/utils مختص همین اپ
│   └── generated/              # کلاینت Type-safe تولیدشده از OpenAPI Backend
├── angular.json
└── package.json

admin-panel-frontend/         (Repository مستقل — Angular CLI استاندارد)
├── src/
│   ├── app/
│   │   ├── core/
│   │   ├── features/          # product-management, order-management, ...
│   │   └── shared/
│   └── generated/
├── angular.json
└── package.json
```

**پیامد این تصمیم:** کد مشترک بین دو اپ (عمدتاً مدل‌های TypeScript، که در هر حال از OpenAPI به‌صورت خودکار در هر Repo تولید می‌شوند نه دستی) دیگر از طریق `lib` مشترک به اشتراک گذاشته نمی‌شود؛ در ازای آن، هر دو اپ کاملاً مستقل Build/Test/Deploy می‌شوند و یادگیری/نگهداری ابزار Nx حذف می‌شود. جزئیات کامل این تصمیم، جایگزین‌های بررسی‌شده و شرط بازبینی آن در سند شماره ۴ (ADR-010) آمده است.

### ۵.۲ استفاده از قابلیت‌های Angular 22

- **Standalone Components** به‌صورت پیش‌فرض (بدون NgModule).
- **Signals** برای reactive state management سبک، به‌جای RxJS در بیشتر موارد.
- **New Control Flow** (`@if`, `@for`, `@switch`) به‌جای `*ngIf`/`*ngFor`.
- در صورت پایدار بودن **Zoneless Change Detection** در نسخه مورد استفاده، ارزیابی و احتمالاً فعال‌سازی برای بهبود Performance.

### ۵.۳ مدیریت State

| اپلیکیشن | راهکار پیشنهادی | دلیل |
|---|---|---|
| Storefront | Signals + Service-based state ساده | State ساده‌تر (Cart، User، Filters) |
| Admin Panel | Signals + NgRx SignalStore برای بخش‌های پیچیده (جدول‌ها، فیلترهای چندگانه، Bulk Actions) | پیچیدگی بیشتر داده و تعامل |

### ۵.۴ UI / Design System

- **Storefront**: Tailwind CSS + کامپوننت‌های اختصاصی طراحی‌شده — چون تجربه بصری و نرخ تبدیل (Conversion Rate) مستقیماً به برندینگ وابسته است.
- **Admin Panel**: استفاده از یک کتابخانه کامپوننت آماده (**PrimeNG** پیشنهاد اول به‌دلیل پشتیبانی خوب از جدول‌ها و فرم‌های پیچیده مدیریتی، یا **Angular Material**) برای سرعت بالاتر توسعه.

### ۵.۵ SSR / SEO

- Storefront باید با **Angular SSR** رندر شود (سئو و Core Web Vitals حیاتی برای فروشگاه است).
- Admin Panel نیازی به SSR ندارد؛ SPA معمولی کافی است.

### ۵.۶ ارتباط با Backend

- تولید خودکار Typed HTTP Client از OpenAPI Spec (مثلاً با `ng-openapi-gen` یا `openapi-typescript`) تا Type Safety بین دو سمت حفظ شود و از Drift جلوگیری شود.
- HTTP Interceptors برای: پیوست Token، Refresh خودکار، مدیریت متمرکز خطا.

---

## ۶. دیتابیس و مدل داده (Core Entities)

| Entity | توضیح |
|---|---|
| User | مشتری/ادمین با فیلد role |
| Role / Permission | برای RBAC پنل ادمین |
| Address | آدرس‌های کاربر |
| Category | دسته‌بندی محصول (سلسله‌مراتبی) |
| Brand | برند |
| Product | اطلاعات پایه محصول |
| ProductVariant | نوع/سایز/رنگ محصول با قیمت و موجودی مستقل |
| ProductImage | تصاویر محصول |
| Attribute / AttributeValue | ویژگی‌های قابل فیلتر |
| Inventory | موجودی هر Variant |
| Cart / CartItem | سبد خرید (مهمان و کاربر لاگین‌شده) |
| Order / OrderItem | سفارش‌ها |
| Payment / Transaction | تراکنش‌های مالی، وضعیت پرداخت |
| Coupon / Discount | (Phase 2) |
| Review / Rating | (Phase 2) |
| Notification | (Phase 2) |

> پیشنهاد: تهیه یک **ERD کامل** به‌عنوان سند مجزا (بخش ۱۴ را ببینید) پیش از شروع پیاده‌سازی جدول‌ها.

---

## ۷. احراز هویت و کنترل دسترسی

- **مشتری**: JWT با Access Token کوتاه‌مدت + Refresh Token (ذخیره در httpOnly cookie یا secure storage).
- **ادمین**: همان مکانیزم JWT، اما با scope/role متفاوت و صفحه ورود جداگانه.
- **RBAC برای Admin Panel**: نقش‌هایی مانند `super_admin`, `product_manager`, `order_manager`, `support` — با جدول Permission قابل توسعه (نه hardcode).
- رمزنگاری پسورد با bcrypt/argon2؛ Rate limiting روی endpointهای auth.

---

## ۸. زیرساخت و DevOps

- **Dev**: Docker Compose (backend + postgres + redis + frontend apps).
- **CI/CD**: GitHub Actions — pipeline شامل Lint → Unit Test → Build → (در صورت موفقیت) Deploy به Staging/Production.
- **Environments**: `dev` → `staging` → `production`، با کانفیگ مجزا (`.env` per environment، در آینده مهاجرت به Vault/Secrets Manager).
- **Reverse Proxy**: Nginx یا Traefik جلوی هر دو Frontend و Backend، با SSL از Let's Encrypt.
- **مسیر آینده**: در صورت رشد ترافیک، مهاجرت تدریجی به Kubernetes و جداسازی ماژول‌های پرترافیک (مثلاً `catalog`، `search`) به سرویس مستقل.

---

## ۹. الزامات غیرعملکردی (NFRs)

| دسته | اقدامات |
|---|---|
| امنیت | رعایت OWASP Top 10، اعتبارسنجی کامل ورودی با Pydantic، CORS محدود، Rate Limiting، عدم ذخیره اطلاعات کارت (تفویض به درگاه) |
| کارایی | Caching با Redis، Pagination اجباری روی همه لیست‌ها، Lazy loading تصاویر در Frontend، Index مناسب روی جداول پرکوئری |
| مانیتورینگ | Structured Logging از روز اول، Sentry برای Error Tracking، Health-check endpoint (`/health`) |
| مقیاس‌پذیری | طراحی Stateless برای API (امکان افزایش Replica)، Connection Pooling در دیتابیس |
| قابلیت نگهداری | تست خودکار، Code Review اجباری، مستندسازی مداوم |

---

## ۱۰. استراتژی تست

| لایه | ابزار |
|---|---|
| Backend Unit/Integration | `pytest` + `pytest-asyncio` + `httpx.AsyncClient` |
| Frontend Unit | Vitest یا Jest |
| Frontend E2E | Playwright |
| CI Gate | هیچ Merge به main بدون عبور از تست‌ها و Lint مجاز نیست |

---

## ۱۱. تعریف دقیق MVP

### ✅ در MVP هست:

**Storefront:**
- مشاهده دسته‌بندی و لیست محصولات + فیلتر ساده
- صفحه جزئیات محصول
- سبد خرید (مهمان + کاربر عضو)
- ثبت‌نام / ورود
- فرآیند Checkout با یک درگاه پرداخت
- تاریخچه سفارش‌ها

**Admin Panel:**
- مدیریت محصولات/دسته‌بندی‌ها (CRUD)
- مدیریت سفارش‌ها (تغییر وضعیت)
- مدیریت موجودی پایه
- مدیریت کاربران
- داشبورد آماری ساده

### ❌ خارج از MVP (فازهای بعد):

کد تخفیف، نظرات و امتیازدهی، جستجوی پیشرفته، Multi-vendor، اعلان‌های چندکاناله، پیشنهاد محصول مشابه/هوشمند، Loyalty/Wishlist، چندزبانه/چندارزی، اپلیکیشن موبایل.

---

## ۱۲. رودمپ فازبندی‌شده

| فاز | تمرکز | خروجی |
|---|---|---|
| **Phase 0** | راه‌اندازی زیرساخت | ایجاد ۳ Repository (backend-api، storefront-frontend، admin-panel-frontend)، CI/CD پایه هرکدام، Docker Compose، اسکلت FastAPI و دو پروژه Angular CLI |
| **Phase 1 — MVP** | حداقل محصول قابل عرضه | موارد بخش ۱۱ (بالا) |
| **Phase 2** | تکمیل تجربه خرید | کد تخفیف، نظرات/امتیاز، Wishlist، جستجوی پیشرفته (Meilisearch)، اعلان‌های ایمیل/پیامک، چند درگاه پرداخت |
| **Phase 3** | مقیاس و مدیریت پیشرفته | گزارش‌گیری پیشرفته Admin، مدیریت چند انبار، احتمالاً Multi-vendor، بهینه‌سازی Performance (CDN، Read Replica) |
| **Phase 4** | شخصی‌سازی و رشد | پیشنهاد محصول هوشمند، برنامه وفاداری، چندزبانه/چندارزی، آماده‌سازی API برای اپ موبایل |

---

## ۱۳. استانداردهای کدنویسی (خلاصه)

- **Python**: PEP8 + `ruff` (lint) + `black` (format) + type hints اجباری + Conventional Commits
- **TypeScript/Angular**: ESLint + Prettier + Angular Style Guide رسمی + Conventional Commits
- جزئیات کامل در سند جداگانه «راهنمای استانداردهای کدنویسی» (بخش بعد).

---

## ۱۴. جمع‌بندی

این سند نقطه شروع معماری است، نه یک سند بسته و ثابت. پیشنهاد می‌شود:
1. ابتدا Phase 0 و اسکلت پروژه پیاده‌سازی شود.
2. برای هر ماژول MVP، قبل از کدنویسی، Contract (OpenAPI Schema) تعریف شود.
3. سند به‌صورت زنده (Living Document) در کنار پیشرفت پروژه به‌روزرسانی شود.

---

---

# داکیومنت‌های تکمیلی مورد نیاز

برای پیش‌بردن درست پروژه، این سند به‌تنهایی کافی نیست. جدول زیر اسناد دیگری که برای یک تیم فنی حرفه‌ای لازم است را همراه با اولویت تهیه نشان می‌دهد:

| # | سند | هدف | زمان تهیه پیشنهادی |
|---|---|---|---|
| 1 | **PRD / SRS تفصیلی** | User Stories، Persona، فرآیندهای کسب‌وکار دقیق (مثلاً فرآیند مرجوعی، نحوه محاسبه مالیات/ارسال) | قبل از Phase 1 |
| 2 | **ERD و Data Dictionary** | مدل کامل دیتابیس، روابط، Index‌ها، Constraint‌ها | قبل از Phase 1 |
| 3 | **API Design Guideline** | قواعد نام‌گذاری endpoint، ساختار خطا، Pagination، Versioning Policy | قبل از Phase 1 |
| 4 | **Architecture Decision Records (ADR)** | ثبت تصمیمات معماری مهم و دلیل انتخاب (مثلاً چرا Modular Monolith، چرا Repositoryهای مستقل به‌جای Nx) | مستمر از Phase 0 |
| 5 | **UI/UX Design System** (Figma) | کامپوننت‌های بصری، رنگ، تایپوگرافی، Wireframe صفحات کلیدی | موازی با Phase 0/1 |
| 6 | **Git Workflow & Branching Guideline** | استراتژی Branch (Trunk-based/GitFlow)، قالب PR، قوانین Code Review | Phase 0 |
| 7 | **CI/CD Pipeline Document** | جزئیات Pipeline، مراحل Deploy، Rollback Strategy | Phase 0 |
| 8 | **Security & Compliance Checklist** | چک‌لیست OWASP، سیاست مدیریت اطلاعات پرداخت (عدم ذخیره PAN کارت)، حریم خصوصی داده کاربر | قبل از Phase 1 |
| 9 | **Testing Strategy & QA Plan** | هرم تست، پوشش تست هدف، فرآیند QA دستی/خودکار | Phase 0/1 |
| 10 | **Infrastructure / IaC Document** | جزئیات سرور، Terraform/Ansible (در صورت استفاده)، مدیریت Secrets | قبل از Production |
| 11 | **Monitoring & Observability Plan** | ابزارها (Sentry/Grafana)، تعریف Alert، SLA/SLO | قبل از Production |
| 12 | **Coding Style Guide** | قوانین دقیق‌تر کدنویسی Python و Angular، ساختار نام‌گذاری فایل‌ها | Phase 0 |
| 13 | **Onboarding Guide** | راهنمای راه‌اندازی محیط توسعه برای عضو جدید تیم | Phase 1 |
| 14 | **Runbook / Incident Response** | مراحل واکنش به Downtime، مسئولین، مسیر Escalation | قبل از Production |
| 15 | **Product Roadmap & Backlog Process** | فرآیند مدیریت Backlog (Jira/Linear)، تعریف Definition of Done | Phase 0 |

**پیشنهاد اولویت‌بندی برای شروع سریع**: اسناد شماره ۱، ۲، ۳، ۶ و ۹ بیشترین اثر مستقیم روی سرعت و کیفیت شروع کدنویسی Phase 1 دارند و بهتر است زودتر از بقیه آماده شوند.
