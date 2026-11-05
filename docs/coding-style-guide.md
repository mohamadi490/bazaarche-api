# سند شماره ۱۲ — راهنمای استانداردهای کدنویسی (Coding Style Guide)
## سیستم فروشگاهی آنلاین

**نوع سند:** Engineering Standards Document
**نقش تدوین‌کننده:** Tech Lead / Software Architect
**اسناد مرجع بالادستی:** `product-development-document.md`، `api-design-guideline.md`، `git-workflow-branching-guideline.md`
**نسخه:** 1.0

---

## کنترل سند

| فیلد | مقدار |
|---|---|
| وضعیت | Draft — الزامی برای هر خط کد از Phase 0 |
| اجرای خودکار | Pre-commit Hook (محلی) + Job اجباری در CI (بدون عبور از Lint، PR مسدود می‌شود — طبق سند شماره ۴/۵) |
| دامنه | Backend (Python/FastAPI) و Frontend (TypeScript/Angular) |

---

## ۱. هدف و فلسفه سند

قوانین این سند برای یک هدف واحد‌اند: **کدی که هر عضو تیم، بدون توضیح شفاهی نویسنده، بتواند در ۵ دقیقه بفهمد چه می‌کند.** اولویت‌ها به ترتیب:

1. **خوانایی** بر «باهوش بودن» کد ارجحیت دارد.
2. **سازگاری (Consistency)** در کل پروژه مهم‌تر از ترجیح شخصی هر توسعه‌دهنده است.
3. قوانین **خودکار اجرا** می‌شوند (Formatter/Linter)، نه با بحث دستی در Code Review — بحث روی سبک کد در PR اتلاف وقت است؛ ابزار باید قبل از باز شدن PR این را حل کرده باشد.
4. **YAGNI** — انتزاع/Generic-سازی زودهنگام برای نیازی که هنوز وجود ندارد ممنوع است (هم‌راستا با رویکرد MVP-first سند معماری اصلی).

---

# بخش A — راهنمای Python / FastAPI (Backend)

## A.1 ابزار (اجباری، نه پیشنهادی)

| ابزار | نقش | زمان اجرا |
|---|---|---|
| `black` | فرمت‌دهی خودکار کد | Pre-commit + CI |
| `ruff` | Lint (جایگزین flake8/isort/pyupgrade) | Pre-commit + CI |
| `mypy` | بررسی نوع استاتیک | CI (اجازه هشدار در Phase 1، اجباری‌شدن کامل در Phase 2) |
| `pip-audit` | بررسی آسیب‌پذیری Dependency | CI (طبق سند شماره ۵) |

پیکربندی هر ابزار در `pyproject.toml` نگه‌داری می‌شود، نه در فایل جدا و پراکنده.

## A.2 قرارداد نام‌گذاری

| نوع | قرارداد | مثال |
|---|---|---|
| متغیر، تابع | `snake_case` | `calculate_total_price` |
| کلاس | `PascalCase` | `OrderService` |
| ثابت (Constant) | `UPPER_SNAKE_CASE` | `MAX_CART_ITEMS` |
| متد/متغیر داخلی (Private) | پیشوند `_` | `_reserve_stock` |
| فایل/ماژول | `snake_case` | `order_service.py` |
| نام Boolean | پیشوند `is_`/`has_`/`should_` | `is_active`, `has_stock` |

## A.3 Type Hint — اجباری، بدون استثنا

هر تابع باید نوع پارامترها و مقدار بازگشتی را مشخص کند. کد بدون Type Hint در Code Review رد می‌شود.

```python
# ❌ نادرست
def get_price(variant, qty):
    return variant.price * qty

# ✅ درست
def get_price(variant: ProductVariant, qty: int) -> Decimal:
    return variant.price * qty
```

- برای مبلغ همیشه `Decimal`، هرگز `float` (هم‌راستا با تصمیم `NUMERIC` در سند شماره ۲).
- از `Optional[X]` صریح استفاده شود، نه فرض ضمنی None بودن.

## A.4 ساختار ماژول (یادآوری از سند معماری اصلی)

هر ماژول دامنه‌ای دقیقاً همین فایل‌ها را دارد و منطق نباید بین لایه‌ها جابه‌جا نوشته شود:

```
catalog/
├── router.py        # فقط HTTP: دریافت Request، فراخوانی service، بازگرداندن Response
├── schemas.py        # Pydantic DTOها — بدون منطق کسب‌وکار
├── models.py          # SQLAlchemy models
├── service.py         # منطق کسب‌وکار — تنها لایه‌ای که «تصمیم» می‌گیرد
├── repository.py      # فقط Query — بدون منطق کسب‌وکار
└── exceptions.py       # Exceptionهای اختصاصی این دامنه
```

**قانون سخت‌گیرانه:** `router.py` هرگز مستقیماً با `models.py`/دیتابیس کار نمی‌کند؛ همیشه از طریق `service.py` عبور می‌کند. `repository.py` هرگز تصمیم کسب‌وکاری (مثل رد کردن سفارش به‌دلیل موجودی) نمی‌گیرد؛ فقط داده می‌خواند/می‌نویسد.

## A.5 Async/Await

- هر تابعی که I/O انجام می‌دهد (DB، HTTP خارجی، Redis) باید `async def` باشد.
- ممنوعیت استفاده از کتابخانه‌های Sync مسدودکننده (مثل `requests`) داخل مسیر Async — به‌جای آن `httpx.AsyncClient`.
- عملیات CPU-bound سنگین (در صورت وجود، مثل پردازش تصویر) نباید مستقیم در مسیر Async اجرا شود؛ به Background Job (طبق سند معماری اصلی، بخش ۴.۴) واگذار شود.

## A.6 مدیریت خطا

```python
# exceptions.py
class InsufficientStockError(DomainError):
    """وقتی موجودی کافی برای رزرو وجود ندارد."""

# service.py
if available_qty < requested_qty:
    raise InsufficientStockError(variant_id=variant.id)

# در سطح مرکزی main.py: یک Exception Handler عمومی
# که DomainError را به فرمت Error Envelope سند شماره ۳ تبدیل می‌کند
```

- `except Exception:` بدون‌قید و بدون Re-raise **ممنوع** است — خطا را قورت‌دادن (Swallow) اشکال را مخفی می‌کند.
- هر دامنه، Exceptionهای اختصاصی خودش را در `exceptions.py` تعریف می‌کند؛ Exception Handler سراسری FastAPI مسئول نگاشت این خطاها به کد HTTP و `error.code` مطابق سند شماره ۳ است.

## A.7 Pydantic Schemas

- هیچ منطق کسب‌وکاری در `schemas.py` نباید باشد — فقط اعتبارسنجی شکل داده (`Field`, `field_validator` برای اعتبارسنجی فرمتی مثل شماره موبایل).
- استفاده از `alias_generator` برای camelCase در خروجی API (طبق تصمیم سند شماره ۳)، بدون نیاز به نام‌گذاری camelCase در خود کد Python.
- نام‌گذاری دقیقاً طبق قرارداد سند شماره ۳ بخش ۱۶ (`XCreateRequest`, `XResponse`, ...).

## A.8 دسترسی داده (SQLAlchemy)

- مدل‌ها با `Mapped[]` و Type Annotation کامل (سبک SQLAlchemy 2.0)، نه سبک قدیمی `Column()` بدون Type.
- هرگز SQL خام (Raw String) در کد نوشته نشود مگر برای Query بسیار خاص با بررسی Performance؛ حتی در آن حالت باید Parameterized باشد (هرگز f-string داخل SQL — خطر SQL Injection).
- بارگذاری روابط (Relationship) همیشه صریح (`selectinload`/`joinedload`)، هرگز به Lazy Loading پیش‌فرض در مسیر پرترافیک متکی نشوید (طبق سند شماره ۲، بخش ۱۲).

## A.9 لاگ‌گذاری (Logging)

- استفاده از لاگ ساختاریافته (JSON) به‌جای `print()`.
- **ممنوعیت مطلق ثبت داده حساس در لاگ:** رمز عبور، توکن، اطلاعات کامل کارت پرداخت هرگز Log نمی‌شوند (طبق NFR-004 سند شماره ۱).
- هر لاگ خطای سطح Service باید شامل شناسه قابل‌ردیابی (مثل `order_id`) باشد، نه فقط پیام کلی.

## A.10 مدیریت Config

- تمام مقادیر پیکربندی (Connection String، کلید JWT، آدرس Redis) از طریق `pydantic-settings` و متغیر محیطی خوانده می‌شوند؛ هیچ مقدار Hardcode در کد نیست.

## A.11 اندازه توابع و فایل‌ها (راهنما، نه قانون سخت)

- طول هدف هر تابع: زیر ~۴۰ خط. عبور از این عدد نشانه نیاز به تفکیک مسئولیت است، نه قانون شکستنی خودکار.
- هر تابع/کلاس یک مسئولیت مشخص (Single Responsibility) — اگر توضیح یک تابع نیاز به «و» زیاد دارد («این تابع قیمت را حساب می‌کند **و** موجودی را رزرو می‌کند **و** ایمیل می‌فرستد») باید تفکیک شود.

## A.12 کامنت‌نویسی

- کامنت باید **چرا** را توضیح دهد، نه **چه چیزی** (که از خود کد خوانا مشخص است).

```python
# ❌ بی‌فایده
# افزایش تعداد به‌اندازه یک واحد
qty += 1

# ✅ مفید
# رزرو موقت برای جلوگیری از Overselling طبق NFR-011؛
# در صورت لغو Checkout ظرف ۱۵ دقیقه آزاد می‌شود (job پس‌زمینه)
inventory.reserve(qty)
```

- Docstring (سبک Google) برای هر تابع Service با منطق غیربدیهی الزامی است؛ برای Getter/Setter ساده لازم نیست.

---

# بخش B — راهنمای TypeScript / Angular (Frontend)

## B.1 ابزار (اجباری)

| ابزار | نقش |
|---|---|
| ESLint (+ `angular-eslint`) | Lint |
| Prettier | فرمت‌دهی خودکار |
| TypeScript `strict: true` | جلوگیری از خطای نوع در زمان Compile |

## B.2 قرارداد نام‌گذاری

| نوع | قرارداد | مثال |
|---|---|---|
| متغیر، تابع، متد | `camelCase` | `calculateTotalPrice` |
| کلاس، Component، Interface، Type | `PascalCase` | `ProductCardComponent` |
| فایل | `kebab-case` مطابق قرارداد Angular | `product-card.component.ts` |
| ثابت سطح ماژول | `UPPER_SNAKE_CASE` | `MAX_CART_ITEMS` |
| Selector کامپوننت | پیشوند پروژه + kebab-case | `app-product-card` (Storefront)، `admin-order-table` (Admin) |
| Signal | بدون قرارداد پیشوند خاص، نام واضح از جنس State | `cartItems`, `isLoading` |

## B.3 قانون `any` ممنوع

استفاده از `any` در ESLint به‌عنوان خطا (Error، نه Warning) تنظیم می‌شود. در موارد واقعاً نامشخص از `unknown` + Type Narrowing استفاده شود.

```typescript
// ❌ ممنوع
function handleResponse(data: any) { ... }

// ✅ درست — از نوع Generated بر پایه OpenAPI استفاده شود
function handleResponse(data: ProductResponse) { ... }
```

## B.4 کامپوننت‌ها (Standalone + Signals)

- تمام کامپوننت‌ها Standalone (بدون NgModule) — طبق تصمیم معماری Angular 22.
- کامپوننت باید «کوچک و بی‌منطق» بماند؛ منطق کسب‌وکاری/فراخوانی API در Service، نه در کامپوننت.
- استفاده از Signals برای State محلی به‌جای متغیر ساده + `ChangeDetectorRef` دستی.
- کنترل‌جریان قالب صرفاً با نحو جدید: `@if`, `@for` (با `track` اجباری), `@switch` — استفاده از `*ngIf`/`*ngFor` قدیمی مجاز نیست.

```typescript
// ✅ الگوی پیشنهادی
@Component({
  selector: 'app-product-list',
  standalone: true,
  template: `
    @for (product of products(); track product.id) {
      <app-product-card [product]="product" />
    }
  `,
})
export class ProductListComponent {
  products = input.required<ProductSummaryResponse[]>();
}
```

## B.5 RxJS و مدیریت Subscription

- ترجیح با `async` pipe در Template یا تبدیل به Signal با `toSignal()` — نه `subscribe()` دستی در کامپوننت مگر ضروری.
- در صورت نیاز به `subscribe()` دستی، استفاده اجباری از `takeUntilDestroyed()` برای جلوگیری از Memory Leak — Subscription بدون مدیریت طول عمر در Code Review رد می‌شود.
- از تودرتو کردن `subscribe` داخل `subscribe` خودداری شود؛ از عملگرهای ترکیبی (`switchMap`, `forkJoin`) استفاده شود.

## B.6 ارتباط با API

- استفاده صرف از کلاینت Type-safe تولیدشده از OpenAPI (طبق سند شماره ۳، بخش ۱۵)؛ فراخوانی دستی `HttpClient` با URL/رشته Hardcode مجاز نیست.
- مدیریت خطا در یک HTTP Interceptor مرکزی، مطابق فرمت `error.code` سند شماره ۳ — کامپوننت‌ها نباید هرکدام جداگانه ساختار خطا را Parse کنند.

## B.7 استایل‌دهی

- **Storefront:** Tailwind CSS، استفاده از Design Tokens محلی همان Repo (مثلاً `src/styles/design-tokens.ts` یا تنظیمات `tailwind.config.ts`) به‌جای رنگ/فاصله Hardcode در کامپوننت‌ها.
- **Admin Panel:** کتابخانه کامپوننت انتخابی (PrimeNG/Angular Material) + Tailwind برای تنظیمات جزئی؛ از بازنویسی کامپوننت‌های آماده خودداری شود مگر ضرورت.
- استفاده از `!important` ممنوع مگر در موارد اضطراری مستند.
- از آنجا که Storefront و Admin Panel در دو Repository مستقل‌اند (طبق ADR-010، سند شماره ۴)، هیچ Design Token/استایلی بین دو Repo به‌صورت خودکار Share نمی‌شود؛ در صورت نیاز واقعی به یکسان‌سازی برند در آینده، این مورد باید آگاهانه (مثلاً کپی مقادیر یا بسته npm خصوصی) مدیریت شود، نه به‌صورت ضمنی.

## B.8 ساختار پوشه هر Feature (درون هر Repository مستقل)

```
src/app/features/product/
├── product-list.component.ts
├── product-list.component.spec.ts
├── product.service.ts          # data-access — ارتباط با API
└── product-card.component.ts   # ui — کامپوننت نمایشی خالص
```

جداسازی منطقی همچنان رعایت می‌شود حتی بدون ابزار Nx: کامپوننت «نمایشی» (مثل `product-card`) هرگز مستقیم Service صدا نمی‌زند، فقط از طریق `input`/`output` با کامپوننت والد (Feature/Page) در تعامل است؛ فراخوانی API فقط در لایه Service (`*.service.ts`) انجام می‌شود.

## B.9 Barrel Files (`index.ts`)

استفاده از Barrel File محدود و هدفمند نگه‌داشته شود؛ در نبود ابزار Nx، ریسک اصلی Barrel بیش‌ازحد کندی Build/HMR در پروژه‌های بزرگ Angular CLI است، نه Circular Dependency بین `lib`ها — همان توصیه به احتیاط پابرجاست.

## B.10 دسترسی‌پذیری (Accessibility) — حداقل‌های الزامی

- تمام عناصر تعاملی (دکمه، لینک) باید `aria-label` مناسب در نبود متن قابل‌مشاهده داشته باشند.
- کنتراست رنگ متن/پس‌زمینه طبق حداقل WCAG AA.
- فرم‌ها باید `label` مرتبط با هر ورودی داشته باشند (نه فقط Placeholder).

---

# بخش C — قواعد مشترک Backend و Frontend

## C.1 متغیر محیطی

نام متغیرهای محیطی `UPPER_SNAKE_CASE` با پیشوند حوزه: `DB_`, `REDIS_`, `JWT_`, `PAYMENT_GATEWAY_`. مقدار پیش‌فرض حساس (مثل کلید JWT) هرگز در `.env.example` قرار نمی‌گیرد (فقط Placeholder مثل `CHANGE_ME`).

## C.2 متن‌های ثابت و آماده‌سازی برای i18n

در MVP رابط کاربری فارسی Hardcode مجاز است اما پیام‌های متنی (به‌ویژه پیام خطا) در یک فایل/Object متمرکز نگه‌داری شوند (نه پراکنده داخل هر کامپوننت/تابع)، تا مهاجرت به i18n واقعی در Phase 4 (طبق رودمپ سند معماری اصلی) بدون بازنویسی کامل ممکن باشد.

## C.3 اجرای خودکار پیش از Commit

استفاده از `pre-commit` (Backend: black/ruff) و `husky` + `lint-staged` (Frontend: eslint/prettier) روی فایل‌های Stage‌شده — تا خطای فرمت هرگز به مرحله Push/CI نرسد.

## C.4 پیوند با Code Review (سند شماره ۴)

بازبین PR **زمان خود را صرف اشکالات فرمتی نمی‌کند** (این وظیفه ابزار خودکار است)؛ تمرکز Code Review روی درستی منطقی، امنیت و هم‌راستایی معماری می‌ماند — طبق سند شماره ۴، بخش ۷.

---

## پیوست — چک‌لیست سریع پیش از باز کردن PR

- [ ] `black`/`ruff` یا `eslint`/`prettier` بدون خطا اجرا شده
- [ ] تمام تابع/متد جدید Type Hint یا نوع TypeScript صریح دارد (بدون `any`)
- [ ] منطق کسب‌وکاری در لایه درست (Service در Backend، `data-access`/Service در Frontend) قرار دارد، نه در Router/Component
- [ ] هیچ مقدار حساس/رمز/کلید در کد Hardcode نشده
- [ ] هیچ داده حساس در لاگ ثبت نمی‌شود
- [ ] نام‌گذاری فایل/کلاس/تابع مطابق قراردادهای این سند است
