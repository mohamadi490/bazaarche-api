# سند شماره ۴ — راهنمای Git Workflow و Branching Strategy
## سیستم فروشگاهی آنلاین

**نوع سند:** Engineering Process Document
**نقش تدوین‌کننده:** Tech Lead / DevOps
**اسناد مرجع بالادستی:** `product-development-document.md`
**نسخه:** 1.0

---

## کنترل سند

| فیلد | مقدار |
|---|---|
| وضعیت | Draft — الزامی از Phase 0 (راه‌اندازی Repository) |
| مدل Branching | Trunk-Based Development با Feature Branch کوتاه‌مدت |
| ابزار میزبانی پیشنهادی | GitHub (هم‌راستا با GitHub Actions در سند معماری اصلی) |

---

## ۱. هدف سند

مشخص‌کردن یک قرارداد یکسان برای کار با Git بین همه اعضای تیم (Backend، Frontend، هر تعداد نفر در آینده) تا:
- تاریخچه کد خوانا و قابل‌ردیابی به Ticket/Requirement بماند.
- فرآیند Merge به `main` همیشه ایمن و از طریق بازبینی کد باشد.
- Deploy از روی Branch مشخص و قابل‌پیش‌بینی انجام شود.

---

## ۲. ساختار Repository

**تصمیم (به‌روزرسانی‌شده — طبق ADR-010 در سند شماره ۴ - ADR):** به‌جای Nx Monorepo برای Frontend، **سه Repository کاملاً مستقل** ایجاد می‌شود تا از پیچیدگی ابزار Monorepo در مرحله شروع پرهیز شود:

| Repository | محتوا | دلیل جدا بودن |
|---|---|---|
| `backend-api` | پروژه FastAPI (تمام ماژول‌های دامنه‌ای) | استک Python، Migration دیتابیس، چرخه Deploy مستقل |
| `storefront-frontend` | پروژه مستقل Angular CLI — سایت مشتری | چرخه Release/Deploy مستقل از Admin Panel |
| `admin-panel-frontend` | پروژه مستقل Angular CLI — پنل مدیریت | چرخه Release/Deploy مستقل از Storefront |

> **نکته هماهنگی:** چون هر دو Frontend به OpenAPI سرویس Backend وابسته‌اند، خروجی OpenAPI هر Release از Backend باید به‌صورت Artifact قابل‌دسترس (مثلاً انتشار در یک مسیر مشخص یا Endpoint عمومی `/openapi.json` در Staging/Production) باشد تا Pipeline کدجنریتور **هر دو** Frontend به‌صورت مستقل از آن بخوانند (جزئیات در سند CI/CD). تکرار جزئی کد (مثل تولید کلاینت Type-safe در هر دو Repo) پذیرفته‌شده و آگاهانه است — چون این کد به‌صورت خودکار تولید می‌شود، نه دستی نوشته می‌شود. **شرط بازبینی این تصمیم:** اگر در آینده تکرار کد دستی‌نویس (نه Generated) بین دو Frontend به یک نقطه دردناک نگهداری تبدیل شود، تیم باید گزینه Nx Monorepo یا یک بسته npm خصوصی مشترک را طبق ADR-010 بازبینی کند.

---

## ۳. چرا Trunk-Based به‌جای GitFlow کامل؟

با توجه به رویکرد MVP-first و Deploy مکرر (نه انتشار فصلی)، GitFlow سنتی (با شاخه‌های `develop`, `release/*` طولانی‌عمر) سربار غیرضروری ایجاد می‌کند. مدل انتخاب‌شده:

- یک شاخه اصلی همیشه Deploy-پذیر: **`main`**
- شاخه‌های کاری **کوتاه‌عمر** (حداکثر چند روز) که مستقیماً از `main` جدا و به `main` برمی‌گردند.
- بدون شاخه `develop` جداگانه — سادگی بیشتر برای تیم کوچک تا متوسط.

---

## ۴. انواع Branch و قرارداد نام‌گذاری

| نوع Branch | الگوی نام‌گذاری | مبدأ | مقصد Merge |
|---|---|---|---|
| اصلی | `main` | — | Protected، مستقیماً Push ممنوع |
| ویژگی جدید | `feature/<ticket-id>-<kebab-description>` | از `main` | به `main` |
| رفع باگ (غیر urgent) | `fix/<ticket-id>-<kebab-description>` | از `main` | به `main` |
| رفع اضطراری Production | `hotfix/<kebab-description>` | از Tag آخرین نسخه Production | به `main` + Deploy فوری |
| تغییرات زیرساختی/CI | `chore/<kebab-description>` | از `main` | به `main` |

**مثال:** `feature/SHOP-142-cart-merge-on-login`, `fix/SHOP-155-inventory-race-condition`

> `<ticket-id>` باید متناظر با شناسه Task در ابزار مدیریت پروژه (Jira/Linear) یا شناسه FR سند شماره ۱ در نبود ابزار رسمی باشد؛ هر Branch باید به یک نیازمندی قابل‌ردیابی باشد.

---

## ۵. قرارداد Commit — Conventional Commits

فرمت الزامی:
```
<type>(<scope>): <short description>

[optional body]

[optional footer, e.g. Refs: FR-ORD-003 / SHOP-142]
```

| type | استفاده |
|---|---|
| `feat` | افزودن قابلیت جدید |
| `fix` | رفع باگ |
| `refactor` | بازنویسی بدون تغییر رفتار |
| `perf` | بهبود کارایی |
| `test` | افزودن/اصلاح تست |
| `docs` | مستندات |
| `chore` | تغییرات جانبی (dependency، تنظیمات) |
| `ci` | تغییر Pipeline |
| `style` | فرمت‌بندی، بدون تغییر منطق |

`scope` نام ماژول دامنه‌ای است: `auth`, `catalog`, `cart`, `orders`, `payments`, `admin-orders`, `inventory` و...

**مثال:**
```
feat(cart): add merge of guest cart into user cart on login

Refs: FR-CART-003
```

**مزیت مستقیم:** امکان تولید خودکار Changelog بین نسخه‌ها از روی این پیام‌ها.

---

## ۶. فرآیند Pull Request (PR)

### ۶.۱ قالب PR (اجباری)

هر PR باید شامل بخش‌های زیر در توضیحات باشد:

```markdown
## چه چیزی تغییر کرد؟
## چرا؟ (ارجاع به Ticket/FR-ID)
## نحوه تست
## اسکرین‌شات (در صورت تغییر UI)
## چک‌لیست
- [ ] تست‌های مرتبط نوشته/به‌روزرسانی شده
- [ ] مطابق API Design Guideline (در صورت تغییر Endpoint)
- [ ] Migration دیتابیس همراه است (در صورت تغییر مدل)
- [ ] مستندات OpenAPI به‌روزرسانی شده
```

### ۶.۲ قوانین Merge

- حداقل **۱ بازبین (Reviewer)** برای پروژه‌های کوچک، **۲ بازبین** برای تغییرات روی ماژول‌های حساس (`payments`, `inventory`, `auth`).
- تمام Statusهای CI (Lint، Test، Build) باید سبز باشند — Merge بدون عبور از CI مسدود است (Branch Protection).
- شاخه PR باید پیش از Merge با آخرین `main` به‌روز (Rebase یا Merge) شده باشد تا Conflict زودتر مشخص شود.
- روش Merge: **Squash Merge** — تاریخچه `main` تمیز و هر PR معادل یک Commit با پیام Conventional Commit می‌ماند.
- Branch منبع پس از Merge به‌صورت خودکار حذف شود.

### ۶.۳ اندازه PR

PRهای بزرگ (بیش از ~۴۰۰ خط تغییر) بازبینی دقیق را دشوار می‌کنند. توصیه: تقسیم ویژگی‌های بزرگ به چند PR کوچک‌تر و پیوسته (مثلاً ابتدا Migration + Model، سپس Service، سپس Router).

---

## ۷. راهنمای Code Review

**بازبین باید بررسی کند:**
- درستی منطقی و پوشش Edge Caseها (مثلاً موجودی صفر، ورودی نامعتبر)
- هم‌راستایی با سند معماری، API Design Guideline و Data Dictionary
- وجود تست کافی برای منطق جدید
- ملاحظات امنیتی (اعتبارسنجی ورودی، بررسی دسترسی RBAC)
- خوانایی کد و نام‌گذاری، نه فقط «درست کار کردن»

**آداب بازبینی:**
- کامنت‌ها سازنده و مشخص باشند (نه فقط «این درست نیست»، بلکه «چرا» و پیشنهاد جایگزین)
- تفکیک کامنت‌های الزامی (Blocking) از پیشنهادی (Nit/Optional) — مثلاً با پیشوند `Nit:`
- زمان پاسخ هدف به PR: حداکثر یک روز کاری تا اولین بازخورد

---

## ۸. قوانین Branch Protection (روی `main`)

| قانون | مقدار |
|---|---|
| Push مستقیم به `main` | غیرمجاز برای همه (حتی Admin، مگر شرایط اضطراری مستند) |
| نیازمند Pull Request | بله |
| نیازمند حداقل تعداد Approval | ۱ (۲ برای مسیرهای حساس طبق CODEOWNERS) |
| نیازمند عبور Statusهای CI | بله (Lint, Unit Test, Build) |
| نیازمند Branch به‌روز پیش از Merge | بله |
| اجازه Force Push روی `main` | خیر |
| استفاده از فایل `CODEOWNERS` | بله — مسیرهای `payments/`, `auth/`, `inventory/` نیازمند تأیید Tech Lead |

---

## ۹. ارتباط Branch با محیط‌های Deploy

| Branch/Tag | محیط | نحوه Deploy |
|---|---|---|
| هر `feature/*` (اختیاری) | Preview Environment (در صورت پیکربندی CI) یا اجرای محلی با Docker Compose | خودکار/محلی |
| `main` | Staging | Deploy خودکار پس از هر Merge موفق |
| Git Tag با فرمت `vX.Y.Z` روی `main` | Production | Deploy با تأیید دستی (Manual Approval در Pipeline) |

جزئیات کامل Pipeline در سند جداگانه CI/CD Pipeline Document آورده می‌شود.

---

## ۱۰. فرآیند Hotfix اضطراری

1. ایجاد Branch `hotfix/<desc>` از Tag آخرین نسخه Production (نه از `main`، اگر `main` تغییرات تست‌نشده جدید دارد).
2. رفع سریع مشکل + تست هدفمند حداقلی.
3. PR با بازبینی فوری (حداقل ۱ نفر، حتی خارج از ساعت کاری در موارد بحرانی).
4. Merge به `main`، صدور Tag جدید Patch (مثلاً `v1.2.1`) و Deploy فوری به Production.
5. اطمینان از اینکه تغییر Hotfix در `main` نیز اعمال شده (نه فقط روی Production) تا در Deploy بعدی گم نشود.

---

## ۱۱. نسخه‌بندی (Semantic Versioning)

هر دو Repository به‌صورت مستقل نسخه‌بندی می‌شوند: `MAJOR.MINOR.PATCH`

- **MAJOR**: تغییر Breaking (مثلاً `/api/v2`)
- **MINOR**: افزودن قابلیت جدید سازگار با نسخه قبل
- **PATCH**: رفع باگ بدون تغییر رفتار API/UI

Tag گذاری روی `main` هنگام هر Promote به Production انجام می‌شود؛ Changelog از روی Commitهای Conventional از Tag قبلی تا Tag جدید تولید می‌شود.

---

## ۱۲. ملاحظات خاص کار با سه Repository مستقل (طبق ADR-010)

از آنجا که هر سه Repository (`backend-api`, `storefront-frontend`, `admin-panel-frontend`) کاملاً مستقل‌اند، این قوانین این سند (Branch Protection، Conventional Commits، PR Template) عیناً و **به‌صورت جداگانه** روی هرکدام اعمال می‌شود؛ نکات هماهنگی بین آن‌ها:

- هر Repository چرخه CI/Deploy مستقل خودش را دارد؛ Merge در یک Repo به‌خودی‌خود Pipeline Repo دیگر را اجرا نمی‌کند.
- در صورتی‌که یک تغییر Backend (مثلاً افزودن فیلد جدید به یک Response) نیاز به هماهنگی با هر دو Frontend داشته باشد، PR مربوطه در `backend-api` باید در توضیحات به Ticket/PR مرتبط در Repo(های) Frontend ارجاع دهد (چون Git به‌تنهایی این ارتباط بین‌Repoی را ردیابی نمی‌کند).
- تغییرات Breaking در API (طبق سیاست بخش ۱۷ سند شماره ۳) باید پیش از Merge در `backend-api`، در هر دو Repo Frontend هماهنگ و آماده شوند تا از ناسازگاری موقت جلوگیری شود.
- `scope` در Conventional Commits همچنان طبق ماژول دامنه‌ای همان Repo نوشته می‌شود (مثلاً در `storefront-frontend`: `feat(cart): ...`؛ نیازی به پیشوند نام اپ نیست چون هر Repo فقط یک اپ دارد).

---

## ۱۳. مدیریت Secrets و فایل‌های حساس

- فایل‌های `.env` **هرگز** Commit نمی‌شوند؛ `.env.example` بدون مقدار واقعی در Repo نگه‌داری می‌شود.
- اجرای ابزار Secret Scanning (مثل `gitleaks`) به‌عنوان یکی از Jobهای CI روی هر PR، برای جلوگیری از نشت تصادفی کلید/رمز.
- در صورت Commit تصادفی یک Secret، صرفاً حذف فایل کافی نیست — باید Secret فوراً باطل/چرخانده (Rotate) شود، حتی پس از پاک‌سازی تاریخچه Git.

---

## پیوست — Cheat Sheet دستورات پرکاربرد

```bash
# شروع یک ویژگی جدید
git checkout main && git pull
git checkout -b feature/SHOP-142-cart-merge

# قبل از باز کردن PR: به‌روزرسانی با آخرین main
git fetch origin
git rebase origin/main

# پس از تأیید PR (روی GitHub انجام می‌شود): Squash Merge
# سپس محلی:
git checkout main && git pull
git branch -d feature/SHOP-142-cart-merge

# Hotfix
git checkout v1.2.0
git checkout -b hotfix/fix-inventory-lock
```
