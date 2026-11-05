# راهنمای راه‌اندازی اولیه پروژه‌ها (Project Bootstrap Guide)
## سیستم فروشگاهی آنلاین — از صفر تا اسکلت اجراپذیر

**نوع سند:** Execution Guide — عملیاتی‌سازی Phase 0 سند معماری اصلی
**نقش تدوین‌کننده:** Software Engineer / Software Architect / Tech Lead
**اسناد مرجع بالادستی:** تمام اسناد قبلی، به‌ویژه `architecture-decision-records.md` (ADR-010)، `coding-style-guide.md`، `git-workflow-branching-guideline.md`
**نسخه:** 1.0

---

## کنترل سند

| فیلد | مقدار |
|---|---|
| وضعیت | Draft — اولین سندی که باید اجرا شود، پیش از هر خط کد کسب‌وکاری |
| تاریخ بررسی نسخه‌های ابزار | ۲۵ اوت ۲۰۲۶ — نسخه‌های بخش ۴ به‌صورت زنده از PyPI و npm Registry استعلام شده‌اند |
| هشدار حیاتی | نسخه‌ها ذاتاً به‌سرعت تغییر می‌کنند؛ پیش از اجرای هر مرحله، عدد دقیق نسخه را مجدداً با دستورات بخش ۴ راستی‌آزمایی کنید |

---

## ۱. هدف سند

سایر اسناد پروژه (معماری، ERD، API، Git Workflow، Coding Style) **چه چیزی** و **چرا** را مشخص کرده‌اند. این سند پاسخ به «**چطور همین امروز شروع کنم؟**» است — یک مسیر اجرایی، خطی و کپی‌پیست‌پذیر برای ساخت اسکلت هر سه Repository (طبق ADR-010) تا در پایان آن، سه پروژه خالی اما **قابل اجرا، قابل تست، و به‌هم متصل** داشته باشید و آماده شروع پیاده‌سازی اولین ماژول کسب‌وکاری (Auth) باشید.

---

## ۲. پیش‌نیازهای محیط توسعه

| ابزار | نسخه موردنیاز | نکته |
|---|---|---|
| Node.js | `^22.22.3` یا `^24.15.0` یا `>=26.0.0` | این محدوده دقیقاً از `engines` بسته رسمی `@angular/cli@22` استخراج شده؛ نسخه‌های قدیمی‌تر Node (مثل ۱۸/۲۰) با Angular 22 کار **نمی‌کنند** |
| npm | `^6.11 \|\| ^7.5.6 \|\| >=8.0.0` | همراه Node نصب می‌شود |
| Python | `3.13+` (پیشنهاد) | آخرین نسخه پایدار خط ۳.۱۳ یا ۳.۱۴؛ پیش از نصب در `python.org` بررسی شود |
| Docker + Docker Compose | آخرین نسخه پایدار | برای اجرای Postgres/Redis محلی |
| Git | آخرین نسخه پایدار | |
| مدیریت نسخه Node | `nvm` (پیشنهادی) | برای سوییچ راحت بین نسخه‌های Node در آینده |

> **توصیه:** از `nvm install 24 && nvm use 24` برای نصب یک نسخه LTS فعال Node استفاده کنید که در محدوده موردنیاز Angular 22 قرار دارد.

---

## ۳. نکته حیاتی درباره «آخرین نسخه بودن» — قبل از هر چیز بخوانید

در حین تدوین این سند، نسخه‌های واقعی از PyPI و npm Registry استعلام شد و یک نکته مهم کشف شد که باید همیشه رعایت کنید:

> **«آخرین نسخه» یعنی آخرین نسخه‌ای که با بقیه اکوسیستم سازگار است، نه لزوماً بالاترین عدد نسخه هر پکیج به‌تنهایی.**

**مثال واقعی:** در بررسی مستقیم Registry، آخرین نسخه بسته `typescript` روی npm عدد `7.0.2` بود. اما بررسی `peerDependencies` بسته `@angular-devkit/build-angular@22` (که واقعاً پروژه Angular را می‌سازد) نشان داد:

```
"typescript": ">=6.0 <6.1"
```

یعنی اگر دستی `npm install typescript@latest` بزنید، پروژه Angular 22 شما را **می‌شکند**. راه‌حل درست: هرگز نسخه TypeScript/وابستگی‌های اصلی فریم‌ورک را دستی و جدا از خود CLI نصب نکنید؛ بگذارید `ng new` و `ng update` این هماهنگی را خودشان مدیریت کنند. همین اصل برای Backend هم صادق است: نسخه `pydantic`/`sqlalchemy`/`fastapi` را با هم و از طریق فایل قفل (Lock file) به‌روز نگه دارید، نه با نصب دستی پراکنده هرکدام.

**قانون عملی برای این سند و آینده پروژه:**
- برای CLIها (`@angular/cli`, ابزار Python) همیشه از آخرین نسخه استفاده کنید (`npx @angular/cli@latest`).
- برای وابستگی‌های داخلی که خود CLI نصب می‌کند، به تصمیم CLI اعتماد کنید، آن‌ها را دستی Override نکنید.
- برای کتابخانه‌های مستقل (FastAPI, SQLAlchemy, Tailwind) از محدوده Compatible (`^`) استفاده کنید، نه Pin دقیق، مگر جایی که ناسازگاری خاصی کشف شود (مثل مورد بالا).

---

## ۴. Snapshot نسخه‌های بررسی‌شده (در تاریخ نگارش سند)

### Backend (PyPI)

| پکیج | نسخه |
|---|---|
| fastapi | 0.141.1 |
| uvicorn | 0.52.4 |
| sqlalchemy | 2.0.52 |
| alembic | 1.19.1 |
| pydantic | 2.13.4 |
| pydantic-settings | 2.15.0 |
| asyncpg | 0.31.0 |
| httpx | 0.28.1 |
| redis (کلاینت پایتون) | 8.1.0 |
| arq | 0.28.0 |
| pyjwt | 2.13.0 |
| argon2-cffi | 25.1.0 |
| ruff | 0.16.4 |
| black | 26.5.1 |
| mypy | 2.3.1 |
| pytest | 9.1.1 |
| pytest-asyncio | 1.4.0 |

### Frontend (npm)

| پکیج | نسخه |
|---|---|
| @angular/cli، @angular/core، @angular/ssr | 22.1.x |
| tailwindcss | 4.3.3 |
| @tailwindcss/postcss | 4.3.3 |
| rxjs | 7.8.2 |
| zone.js | 0.16.2 |
| primeng | 22.1.0 |
| @hey-api/openapi-ts | 0.99.0 |
| eslint | 10.9.1 |
| angular-eslint | 22.1.0 |
| prettier | 3.9.6 |
| husky | 9.1.7 |
| lint-staged | 17.3.0 |

> دستور راستی‌آزمایی سریع پیش از شروع: `curl -s https://pypi.org/pypi/fastapi/json | python3 -c "import json,sys;print(json.load(sys.stdin)['info']['version'])"` و `npm view @angular/cli version`

---

## ۵. مرحله ۱ — ایجاد سه Repository (طبق ADR-010)

```bash
# روی Git Host انتخابی (GitHub، طبق سند Git Workflow) سه Repository خالی بسازید:
# backend-api
# storefront-frontend
# admin-panel-frontend

# سپس در سیستم محلی:
mkdir -p ~/projects/shop && cd ~/projects/shop
git clone git@github.com:<org>/backend-api.git
git clone git@github.com:<org>/storefront-frontend.git
git clone git@github.com:<org>/admin-panel-frontend.git
```

پیش از رفتن به مرحله بعد، طبق `git-workflow-branching-guideline.md` بخش ۸، Branch Protection را روی شاخه `main` هر سه Repository فعال کنید (حتی وقتی هنوز خالی‌اند — تنظیم زودهنگام بهتر از فراموشی بعدی است).

---

## ۶. مرحله ۲ — اسکلت Backend (`backend-api`)

### ۶.۱ ابزار مدیریت پکیج: `uv`

**تصمیم:** استفاده از [`uv`](https://github.com/astral-sh/uv) (ابزار همان تیم سازنده `ruff`) به‌جای `pip` خام یا `poetry` — سریع‌ترین ابزار فعلی برای مدیریت وابستگی و محیط مجازی پایتون، با فایل قفل (`uv.lock`) برای بازتولیدپذیری دقیق نسخه‌ها.

```bash
cd backend-api

# نصب uv (در صورت نبود)
curl -LsSf https://astral.sh/uv/install.sh | sh

# مقداردهی اولیه پروژه با نسخه Python هدف
uv init --python 3.13 --name backend-api
```

### ۶.۲ افزودن وابستگی‌ها

```bash
# وابستگی‌های اصلی
uv add "fastapi[standard]" sqlalchemy asyncpg alembic pydantic-settings \
  pyjwt argon2-cffi httpx redis arq

# وابستگی‌های توسعه
uv add --dev ruff black mypy pytest pytest-asyncio pip-audit pre-commit
```

### ۶.۳ ساختار پوشه (دقیقاً طبق سند معماری اصلی، بخش ۴.۱)

```bash
mkdir -p app/core app/db app/shared app/modules/{auth,users,catalog,inventory,cart,orders,payments,admin_dashboard}
mkdir -p tests alembic
touch app/__init__.py app/main.py
for m in auth users catalog inventory cart orders payments admin_dashboard; do
  touch app/modules/$m/{__init__.py,router.py,schemas.py,models.py,service.py,repository.py,exceptions.py}
done
```

### ۶.۴ پیکربندی `pyproject.toml` برای ابزارها

```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.black]
line-length = 100
target-version = ["py313"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### ۶.۵ فایل `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.4
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/psf/black
    rev: 26.5.1
    hooks:
      - id: black
```

```bash
uv run pre-commit install
```

### ۶.۶ `app/core/config.py` — تنظیمات مبتنی بر Environment Variable

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_days: int = 30
    cors_origins: list[str] = []


settings = Settings()
```

### ۶.۷ `app/main.py` — اسکلت اجراپذیر اولیه با Health Check

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title="Shop Backend API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

### ۶.۸ `.env.example`

```
DATABASE_URL=postgresql+asyncpg://shop:shop@localhost:5432/shop
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=CHANGE_ME
CORS_ORIGINS=["http://localhost:4200","http://localhost:4300"]
```

(طبق `coding-style-guide.md` بخش C.1 — `.env` واقعی هرگز Commit نمی‌شود، فقط `.env.example`.)

### ۶.۹ `docker-compose.yml` — محیط توسعه محلی

```yaml
services:
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: shop
      POSTGRES_PASSWORD: shop
      POSTGRES_DB: shop
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:8-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

```bash
docker compose up -d
```

### ۶.۱۰ راه‌اندازی Alembic (Async)

```bash
uv run alembic init -t async alembic
```

در `alembic.ini`، خط `sqlalchemy.url` حذف و در `alembic/env.py` مقدار از `settings.database_url` خوانده شود (نه Hardcode).

فعال‌سازی اکستنشن UUID (طبق ADR-003) در اولین Migration:

```bash
uv run alembic revision -m "enable pgcrypto extension"
```

```python
def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
```

```bash
uv run alembic upgrade head
```

### ۶.۱۱ اولین تست

```python
# tests/test_health.py
from httpx import AsyncClient, ASGITransport
from app.main import app


async def test_health_check_returns_ok():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

```bash
uv run pytest
```

### ۶.۱۲ CI اولیه (`.github/workflows/ci.yml`)

```yaml
name: CI
on: [pull_request, push]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17-alpine
        env: { POSTGRES_USER: shop, POSTGRES_PASSWORD: shop, POSTGRES_DB: shop }
        ports: ["5432:5432"]
      redis:
        image: redis:8-alpine
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run ruff check .
      - run: uv run black --check .
      - run: uv run pytest
```

> این نسخه CI حداقلی است تا از همان روز اول PRها بازبینی خودکار شوند؛ نسخه کامل (Deploy، Staging/Production Promote) موضوع سند جداگانه CI/CD Pipeline خواهد بود.

### ۶.۱۳ Commit اولیه

```bash
echo -e ".venv/\n.env\n__pycache__/\n*.pyc" > .gitignore
git add .
git commit -m "chore: bootstrap FastAPI backend skeleton"
git push origin main
```

---

## ۷. مرحله ۳ — اسکلت Frontend (تکرار برای هر دو Repository)

این بخش برای **هر دو** Repository (`storefront-frontend` و `admin-panel-frontend`) به‌صورت مستقل اجرا می‌شود (طبق ADR-010، بدون Nx).

### ۷.۱ ایجاد پروژه Angular

**Storefront (با SSR، طبق سند اصلی بخش ۵.۵):**
```bash
npx @angular/cli@latest new storefront-frontend --routing --style=css --ssr --skip-git
```

**Admin Panel (بدون SSR):**
```bash
npx @angular/cli@latest new admin-panel-frontend --routing --style=css --skip-git
```

هنگام Prompt تعاملی `ng new`:
- **Strict mode:** بله (پیش‌فرض جدید Angular CLI است — بررسی کنید در `tsconfig.json`، `"strict": true` باشد)
- **Zoneless (Experimental):** برای این مرحله **گزینه پیش‌فرض با Zone.js** انتخاب شود، نه Zoneless. طبق سند اصلی (بخش ۵.۲) این قابلیت باید جداگانه ارزیابی شود؛ فعال‌سازی زودهنگام آن روی اسکلت اولیه ریسک ناپایداری غیرضروری در Phase 0 ایجاد می‌کند.

### ۷.۲ نصب Tailwind CSS v4

> توجه: روش نصب Tailwind v4 با نسخه ۳ که در آموزش‌های قدیمی‌تر رایج است متفاوت است — دیگر نیازی به `tailwind.config.js` با آرایه `content` یا دستور `npx tailwindcss init` نیست.

```bash
cd storefront-frontend   # (و مشابه آن در admin-panel-frontend)
npm install tailwindcss @tailwindcss/postcss postcss --save-dev
```

فایل `.postcssrc.json` در ریشه پروژه:
```json
{
  "plugins": {
    "@tailwindcss/postcss": {}
  }
}
```

در `src/styles.css`:
```css
@import "tailwindcss";
```

Auto Content Detection در Tailwind v4 فایل‌های پروژه را خودکار پیدا می‌کند؛ نیازی به پیکربندی مسیر نیست. در صورت نیاز به تم/رنگ اختصاصی برند (طبق Design System آینده)، از بلوک `@theme` مستقیم در همان فایل CSS استفاده شود:

```css
@theme {
  --color-brand-primary: #1e40af;
}
```

### ۷.۳ ESLint + Prettier (طبق `coding-style-guide.md` بخش B.1)

```bash
ng add @angular-eslint/schematics@latest
npm install --save-dev prettier eslint-config-prettier
```

فایل `.prettierrc.json`:
```json
{ "singleQuote": true, "printWidth": 100 }
```

### ۷.۴ Husky + lint-staged (طبق `coding-style-guide.md` بخش C.3)

```bash
npm install --save-dev husky lint-staged
npx husky init
echo "npx lint-staged" > .husky/pre-commit
```

در `package.json`:
```json
"lint-staged": {
  "*.ts": ["eslint --fix", "prettier --write"],
  "*.css": ["prettier --write"]
}
```

### ۷.۵ ساختار پوشه (طبق `coding-style-guide.md` بخش B.8، بدون Nx)

```bash
mkdir -p src/app/core src/app/features src/app/shared src/app/generated
```

### ۷.۶ تولید کلاینت Type-safe از OpenAPI

**تصمیم ابزار:** `@hey-api/openapi-ts` — جانشین فعال‌تر و به‌روزتر نسبت به `openapi-typescript-codegen` قدیمی.

```bash
npm install --save-dev @hey-api/openapi-ts
```

اسکریپت در `package.json`:
```json
"scripts": {
  "generate:api": "openapi-ts -i http://localhost:8000/openapi.json -o src/app/generated -c @hey-api/client-fetch"
}
```

> این دستور نیازمند اجرای Backend محلی (بخش ۶) پیش از اجراست — به همین دلیل ترتیب راه‌اندازی در بخش ۸ این سند اهمیت دارد.

### ۷.۷ Admin Panel — افزودن PrimeNG

```bash
# فقط در admin-panel-frontend
ng add primeng@latest
```

> از `ng add` به‌جای نصب دستی `primeng` و `@primeng/themes` استفاده کنید — این دستور خودش نسخه‌های سازگار را هماهنگ نصب می‌کند (طبق همان اصل بخش ۳ این سند).

### ۷.۸ فایل‌های Environment

```typescript
// src/environments/environment.development.ts
export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:8000/api/v1',
};
```

### ۷.۹ HTTP Interceptor پایه (اسکلت — منطق کامل در پیاده‌سازی Auth)

```typescript
// src/app/core/auth.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // TODO: پیوست Access Token و مدیریت خطای 401 — طبق api-design-guideline.md بخش ۱۰
  return next(req);
};
```

### ۷.۱۰ پاکسازی فایل نمونه

حذف محتوای دمو `app.component.html` پیش‌فرض Angular CLI و جایگزینی با یک `<router-outlet />` ساده.

### ۷.۱۱ CI اولیه (`.github/workflows/ci.yml`)

```yaml
name: CI
on: [pull_request, push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 24 }
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --watch=false --browsers=ChromeHeadless
      - run: npm run build
```

### ۷.۱۲ Commit اولیه

```bash
git add .
git commit -m "chore: bootstrap Angular app with Tailwind v4"
git push origin main
```

---

## ۸. مرحله ۴ — اتصال اولیه سه پروژه به هم (Smoke Integration)

```bash
# ۱) اجرای Backend
cd backend-api && docker compose up -d && uv run fastapi dev app/main.py
# در دسترس روی http://localhost:8000 — مستندات: http://localhost:8000/docs

# ۲) تولید کلاینت در هر دو Frontend (نیازمند Backend روشن)
cd storefront-frontend && npm run generate:api
cd admin-panel-frontend && npm run generate:api

# ۳) اجرای هر دو Frontend روی پورت‌های جدا
cd storefront-frontend && npm start   # پیش‌فرض 4200
cd admin-panel-frontend && npm start -- --port 4300
```

**تست دستی نهایی:** از هرکدام از دو اپ Angular، یک فراخوانی ساده به `GET /health` بزنید (مثلاً از یک کامپوننت موقت یا مستقیم از Console مرورگر با کلاینت Generated) و مطمئن شوید پاسخ `{"status": "ok"}` با موفقیت (بدون خطای CORS) دریافت می‌شود. این تأیید می‌کند زنجیره کامل (Frontend → CORS → Backend → پاسخ) درست کار می‌کند.

---

## ۹. چک‌لیست پایان اسکلت‌سازی (Definition of Done این سند)

- [ ] هر سه Repository ایجاد و Branch Protection روی `main` فعال شده
- [ ] Backend با `uv` راه‌اندازی شده، ساختار پوشه دامنه‌ای کامل است
- [ ] `docker compose up` بدون خطا Postgres و Redis را بالا می‌آورد
- [ ] Alembic راه‌اندازی شده و اولین Migration (`pgcrypto`) اجرا شده
- [ ] `GET /health` روی Backend پاسخ می‌دهد و تست خودکار آن سبز است
- [ ] هر دو Angular App ساخته شده، Tailwind v4 فعال و قابل استفاده است
- [ ] ESLint/Prettier/Husky در هر دو Frontend فعال است
- [ ] کلاینت Type-safe از OpenAPI در هر دو Frontend تولید شده
- [ ] هر دو Frontend می‌توانند بدون خطای CORS با Backend محلی صحبت کنند
- [ ] CI پایه (Lint + Test + Build) در هر سه Repository سبز است
- [ ] هر سه Repository حداقل یک Commit اولیه دارند و روی `main` Push شده‌اند

---

## ۱۰. مراحل بعدی (پس از این سند)

با تکمیل چک‌لیست بالا، اسکلت آماده است. ترتیب پیشنهادی گام بعدی:

1. **پیاده‌سازی ماژول Auth واقعی** — طبق `FR-AUTH-001..006` (سند شماره ۱) و Endpointهای بخش ۱۸.۱ (سند شماره ۳)؛ این ماژول پایه تمام ماژول‌های بعدی است (چون RBAC/شناسایی کاربر همه‌جا لازم است).
2. **نوشتن اولین Migrationهای واقعی جداول** (`users`, `roles`, ...) طبق سند شماره ۲.
3. **تکمیل CI/CD کامل** — این سند فقط CI حداقلی (Lint/Test/Build) را پوشش داد؛ سند مجزای **CI/CD Pipeline Document** (اشاره‌شده در لیست اسناد تکمیلی، هنوز نوشته نشده) باید Deploy خودکار به Staging و Promote دستی به Production را کامل کند.
4. **تنظیم Secrets واقعی** (JWT Secret تولیدشده امن، نه مقدار Placeholder) پیش از هر Deploy واقعی، طبق سند شماره ۲ بخش ۱۰.
5. در صورت تمایل، ثبت تصمیم انتخاب `uv` و `@hey-api/openapi-ts` به‌عنوان یک ADR جدید (مثلاً ADR-012) در سند شماره ۴، تا الگوی مستندسازی تصمیمات همچنان کامل بماند.

---

## پیوست — دستورات خلاصه (Quick Reference)

```bash
# Backend
cd backend-api && docker compose up -d && uv run fastapi dev app/main.py

# Storefront
cd storefront-frontend && npm start

# Admin Panel
cd admin-panel-frontend && npm start -- --port 4300

# بازتولید کلاینت API پس از هر تغییر Backend
npm run generate:api
```
