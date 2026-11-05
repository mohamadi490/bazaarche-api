# سند شماره ۵ — استراتژی تست و برنامه QA (Testing Strategy & QA Plan)
## سیستم فروشگاهی آنلاین

**نوع سند:** Engineering Quality Document
**نقش تدوین‌کننده:** Tech Lead / QA Lead
**اسناد مرجع بالادستی:** `product-development-document.md`، `requirements-document-BRS-PRD-SRS-FRS.md`، `api-design-guideline.md`
**نسخه:** 1.0

---

## کنترل سند

| فیلد | مقدار |
|---|---|
| وضعیت | Draft — الزامی از Phase 0 (تنظیم CI) |
| فلسفه تست | Test Pyramid — تکیه اصلی روی Unit/Integration سریع، E2E محدود به مسیرهای حیاتی |
| Gate ورود به `main` | هیچ PR بدون عبور از تست‌های Lint/Unit/Integration مربوطه Merge نمی‌شود (طبق سند شماره ۴) |

---

## ۱. هدف سند

مشخص‌کردن اینکه **چه چیزی، در چه سطحی، با چه ابزاری، و با چه معیار پذیرشی** تست می‌شود — تا کیفیت با رشد سریع محصول (طبق رودمپ فازبندی‌شده) حفظ شود و رگرسیون در ماژول‌های حساس (پرداخت، موجودی) رخ ندهد.

---

## ۲. فلسفه تست (Test Pyramid)

```
        ▲  E2E (تعداد کم — مسیرهای حیاتی کاربر)
       ╱ ╲
      ╱   ╲  Integration (متوسط — API + DB واقعی)
     ╱     ╲
    ╱       ╲ Unit (زیاد — منطق کسب‌وکار ایزوله، سریع)
   ╱_________╲
```

- **Unit** سریع‌ترین و ارزان‌ترین بازخورد را می‌دهد؛ باید اکثریت تست‌ها را تشکیل دهد.
- **Integration** صحت تعامل واقعی بین لایه‌ها (API ↔ DB ↔ Redis) را تضمین می‌کند.
- **E2E** گران و کندتر است؛ فقط برای مسیرهای کسب‌وکاری حیاتی که شکست آن‌ها یعنی توقف کامل فروش.

---

## ۳. سطوح تست و ابزار

| سطح | Backend | Frontend |
|---|---|---|
| Unit | `pytest` — تست توابع Service/منطق کسب‌وکار ایزوله (بدون DB واقعی، با Mock Repository) | Vitest/Jest — تست Component/Service ایزوله با Angular Testing Utilities |
| Integration | `pytest` + `pytest-asyncio` + `httpx.AsyncClient` روی یک دیتابیس تست واقعی (Postgres در Docker/Testcontainers) | تست تعامل Component + HTTP Mock (`HttpClientTestingModule`) |
| Contract | اعتبارسنجی خودکار خروجی OpenAPI در برابر Schema مورد انتظار (جلوگیری از Breaking Change ناخواسته) | Type-checking خودکار از طریق کلاینت Generated (خطای Compile در صورت Mismatch) |
| E2E | — (E2E از منظر کاربر، نه Backend مجزا) | Playwright — روی Storefront و Admin Panel، در برابر Backend واقعی (محیط Staging/CI) |
| Performance/Load | `locust` یا `k6` برای سناریوهای بحرانی (Checkout همزمان) | Lighthouse CI برای Core Web Vitals (Phase 2) |
| Security (پایه) | `pip-audit` (آسیب‌پذیری Dependency)، بررسی OWASP Top10 دستی در Code Review | `npm audit` |

---

## ۴. استراتژی داده تست (Test Data Strategy)

- **Backend:** استفاده از الگوی Factory (مثل `factory-boy` یا Fixtureهای دستی pytest) برای ساخت داده تست خوانا؛ هر تست Integration در یک Transaction اجرا و در پایان Rollback می‌شود تا تست‌ها مستقل و بدون اثر جانبی روی هم باشند.
- **دیتابیس تست:** یک نمونه Postgres مجزا (Container موقت در CI) — هرگز روی دیتابیس `dev`/`staging` تست اجرا نمی‌شود.
- **Frontend:** داده Mock مطابق دقیق Schema واقعی (Generated Types) تا از Drift بین Mock و API واقعی جلوگیری شود.
- **E2E:** یک محیط Staging با داده Seed ثابت و قابل‌بازنشانی (Reset) پیش از هر اجرای کامل مجموعه E2E.

---

## ۵. پوشش تست هدف (Coverage Targets)

| دسته ماژول | هدف Coverage | دلیل |
|---|---|---|
| ماژول‌های حساس مالی/موجودی (`orders`, `payments`, `inventory`, `cart`) | ≥ 85% | مستقیماً روی درآمد و صحت مالی اثر دارد |
| ماژول‌های کسب‌وکاری عمومی (`catalog`, `users`, `auth`) | ≥ 70% | |
| ماژول‌های Admin کم‌ریسک‌تر (`dashboard`) | ≥ 50% | عمدتاً Read-only، ریسک پایین‌تر |
| Frontend — Component‌های منطقی (Cart, Checkout Form) | ≥ 70% | |
| Frontend — Componentهای صرفاً نمایشی (Presentational) | پوشش کمتر قابل‌قبول است | ارزش تست پایین نسبت به هزینه |

> عدد Coverage به‌تنهایی معیار کیفیت نیست — تست‌هایی که فقط برای رد کردن آستانه Coverage نوشته شوند (بدون Assertion معنادار) در Code Review رد می‌شوند.

---

## ۶. استراتژی تست ماژول‌های حساس (تمرکز ویژه)

### ۶.۱ موجودی و همزمانی (Inventory Concurrency)

- تست Integration اختصاصی: شبیه‌سازی **دو درخواست همزمان خرید آخرین واحد موجودی یک Variant** → فقط یکی باید موفق شود، دیگری باید خطای `PRODUCT_OUT_OF_STOCK` (طبق سند شماره ۳) دریافت کند.
- تست باید الگوی `SELECT FOR UPDATE` + `version` توضیح‌داده‌شده در سند شماره ۲ (بخش ۸) را واقعاً زیر بار همزمان تأیید کند، نه صرفاً منطق ترتیبی.

### ۶.۲ پرداخت (Payments)

- Mock/Sandbox Gateway برای تمام تست‌های خودکار — تست هرگز به درگاه واقعی متصل نمی‌شود.
- سناریوهای الزامی: پرداخت موفق، پرداخت ناموفق، Webhook تکراری (بررسی Idempotency طبق سند شماره ۳ بخش ۱۱)، Webhook با امضای نامعتبر (باید Reject شود).
- تست اطمینان از عدم ذخیره اطلاعات کامل کارت در هیچ لایه (Log، DB، Response) — NFR-004.

### ۶.۳ احراز هویت و RBAC

- تست هر نقش ادمین باید تأیید کند که دسترسی به Endpointهای خارج از Permission آن نقش با `403` رد می‌شود (نه فقط مخفی‌شدن دکمه در UI) — پوشش FR-ADMUSER-002.
- تست انقضا و Revoke شدن Refresh Token.

---

## ۷. سناریوهای کلیدی E2E (مسیرهای حیاتی کاربر)

| # | سناریو | اپلیکیشن | اولویت |
|---|---|---|---|
| E2E-01 | خرید کامل توسط کاربر مهمان (مرور → سبد → Checkout → پرداخت موفق → تأییدیه) | Storefront | حیاتی |
| E2E-02 | خرید کامل توسط کاربر عضو با ادغام سبد مهمان پس از ورود | Storefront | حیاتی |
| E2E-03 | تلاش خرید محصول با موجودی صفر → پیام خطای مناسب | Storefront | بالا |
| E2E-04 | پرداخت ناموفق → امکان تلاش مجدد بدون از‌دست‌رفتن سفارش | Storefront | بالا |
| E2E-05 | ورود ادمین و تغییر وضعیت یک سفارش | Admin Panel | حیاتی |
| E2E-06 | ایجاد محصول جدید با تصویر و Variant توسط ادمین | Admin Panel | بالا |
| E2E-07 | ورود کاربر با نقش محدود و تلاش دسترسی به بخش غیرمجاز → رد دسترسی | Admin Panel | بالا |
| E2E-08 | مشاهده تاریخچه سفارش توسط مشتری | Storefront | متوسط |

این مجموعه در هر Deploy به Staging (پیش از Promote به Production) اجرا می‌شود (Smoke Test خودکار).

---

## ۸. محیط‌های تست

| محیط | هدف | داده |
|---|---|---|
| Local (Docker Compose) | توسعه و اجرای Unit/Integration محلی توسط توسعه‌دهنده | داده Seed دلخواه توسعه‌دهنده |
| CI (Ephemeral) | اجرای خودکار کل Suite Unit/Integration روی هر PR — Container تازه Postgres/Redis برای هر Run | داده Factory-generated، از بین می‌رود پس از هر Run |
| Staging | اجرای E2E/Smoke Test پس از هر Merge به `main` پیش از تأیید Production | داده Seed ثابت و قابل Reset |
| Production | فقط Smoke Test بسیار محدود و غیرمخرب پس از Deploy (health-check، نه تست کامل) | داده واقعی — هیچ تست مخرب/نویسنده روی این محیط اجرا نمی‌شود |

---

## ۹. یکپارچگی با CI Pipeline

ترتیب اجرای Job ها (Fail-fast — توقف در اولین شکست):

```
1. Lint (Backend: ruff/black --check | Frontend: eslint/prettier --check)
2. Unit Tests (Backend + Frontend، موازی)
3. Integration Tests (Backend با DB واقعی موقت)
4. Build (Backend Docker Image | Frontend nx build --affected)
5. [فقط روی main، پس از Deploy به Staging] E2E/Smoke Tests
6. Promote به Production (تأیید دستی)
```

- از آنجا که Storefront و Admin Panel هرکدام Repository/Pipeline کاملاً مستقل خودشان را دارند (طبق ADR-010، سند شماره ۴)، نیازی به بهینه‌سازی نوع `nx affected` نیست — هر Pipeline صرفاً همان یک پروژه را Lint/Test/Build می‌کند.
- نتیجه Coverage هر PR به‌صورت خودکار روی PR کامنت/نمایش داده می‌شود.

---

## ۱۰. تست‌های غیرعملکردی (NFR Testing)

| NFR مرتبط (سند ۱) | نوع تست | روش |
|---|---|---|
| NFR-001 (زمان پاسخ API) | Load Test هدفمند | `k6`/`locust` روی Endpointهای پرترافیک (`GET /products`, `POST /cart/checkout`) پیش از هر Release بزرگ |
| NFR-002 (زمان بارگذاری صفحه) | Performance Audit | Lighthouse CI روی صفحات کلیدی Storefront (Phase 2) |
| NFR-003/004/005 (امنیت) | Static/Dependency Scan | `pip-audit`, `npm audit`, بررسی OWASP Top 10 در Code Review Checklist |
| NFR-011 (همزمانی موجودی) | Concurrency Test | بخش ۶.۱ همین سند |
| NFR-006 (Uptime) | Health-check پس از هر Deploy | Endpoint `/health` بررسی خودکار در Pipeline پیش از تکمیل Deploy |

---

## ۱۱. مدیریت باگ و Defect Triage

| شدت (Severity) | تعریف | زمان پاسخ هدف |
|---|---|---|
| Critical | توقف فرآیند خرید/پرداخت، از‌دست‌رفتن داده | فوری — Hotfix طبق سند شماره ۴ |
| High | نقص در یک ماژول اصلی بدون مسدودکردن کامل خرید | همان Sprint |
| Medium | مشکل غیرمسدودکننده در تجربه کاربری | Sprint بعد |
| Low | مسائل بصری جزئی | Backlog، اولویت پایین |

هر باگ کشف‌شده در QA باید یک Ticket با ارجاع به FR-ID مرتبط (سند شماره ۱) و در صورت امکان یک تست Regression جدید برای جلوگیری از تکرار داشته باشد.

---

## ۱۲. تست دستی و UAT (Phase 1)

با توجه به اینکه Suite خودکار E2E از ابتدا کامل نخواهد بود، پیش از هر Release به Production در فاز MVP:

- اجرای یک **چک‌لیست رگرسیون دستی** روی سناریوهای بخش ۷ توسط QA/Tech Lead.
- **تأیید نهایی (UAT Sign-off)** توسط صاحب کسب‌وکار پیش از هر Release مهم (به‌ویژه اولین انتشار MVP) — طبق Definition of Done سند شماره ۱ (بخش G).

---

## ۱۳. قرارداد نام‌گذاری تست

**Backend (pytest):**
```python
def test_checkout_fails_when_stock_insufficient():
    ...

def test_webhook_ignores_duplicate_gateway_reference():
    ...
```
الگو: `test_<چیزی_که_تست_می‌شود>_<سناریو>_<نتیجه_مورد_انتظار>`

**Frontend (Vitest/Jest):**
```typescript
describe('CartService', () => {
  it('should merge guest cart into user cart after login', () => { ... });
});
```

---

## ۱۴. Mock کردن سرویس‌های خارجی

| سرویس خارجی | روش Mock در تست |
|---|---|
| درگاه پرداخت | `payment_gateways` با `code='mock'` طبق طراحی سند شماره ۲ — پاسخ موفق/ناموفق قابل‌کنترل در تست |
| ارسال ایمیل/پیامک (Phase 2) | Provider Mock که پیام را فقط لاگ می‌کند، ارسال واقعی نمی‌کند در محیط تست/CI |

هرگز در Pipeline خودکار به سرویس واقعی خارجی (حتی Sandbox آن با هزینه/Rate Limit) وابسته نمی‌شویم مگر در تست دستی از پیش هماهنگ‌شده.

---

## ۱۵. گزارش‌دهی و متریک‌های کیفیت

- گزارش Coverage در هر PR (خودکار در CI).
- روند Coverage در طول زمان رصد می‌شود (نه فقط عدد لحظه‌ای) تا افت تدریجی کیفیت زود تشخیص داده شود.
- **سیاست تست ناپایدار (Flaky Test):** تستی که بدون تغییر کد گاهی Fail می‌شود، بلافاصله `skip` نمی‌شود؛ باید Ticket با اولویت مشخص برای ریشه‌یابی باز شود؛ Skip موقت فقط با تأیید Tech Lead و Ticket مرتبط مجاز است.

---

## پیوست — الگوی نمونه Test Case (برای تست دستی/UAT)

| فیلد | مقدار نمونه |
|---|---|
| شناسه | TC-ORD-001 |
| مرتبط با | FR-ORD-003, E2E-01 |
| عنوان | تکمیل موفق خرید مهمان با یک آیتم |
| پیش‌شرط | حداقل یک محصول با موجودی کافی موجود است |
| مراحل | ۱) افزودن محصول به سبد ۲) ورود به Checkout ۳) وارد کردن آدرس ۴) پرداخت با Mock Gateway (حالت موفق) |
| نتیجه مورد انتظار | سفارش با وضعیت «در حال پردازش» ثبت و صفحه تأیید نمایش داده می‌شود؛ موجودی به‌درستی کسر شده |
| وضعیت | Pass / Fail |
