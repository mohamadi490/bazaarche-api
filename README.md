# Bazaarche API

A modern, scalable e-commerce backend API built with **FastAPI** and **PostgreSQL**. Bazaarche is designed as an MVP-first, single-vendor (extensible to multi-vendor) B2C platform with clean architecture, async operations, and production-ready features.

## 🎯 Overview

Bazaarche is a comprehensive e-commerce platform with three main repositories:
- **Bazaarche API** (Backend) - This repository
- **Bazaarche Storefront** (Angular Customer Portal)
- **Bazaarche Admin** (Angular Admin Dashboard)

The backend provides RESTful APIs for managing catalogs, inventory, orders, payments, user authentication, and administrative operations with a robust database schema and async task processing.

---

## ✨ Key Features

- **User Authentication & Management**: Secure JWT-based auth with role-based access control
- **Product Catalog**: Browse, filter, and search products with inventory tracking
- **Shopping Cart**: Add/remove products with real-time updates
- **Order Management**: Complete order lifecycle from checkout to fulfillment
- **Payment Processing**: Abstract payment gateway architecture (extensible to multiple providers)
- **Inventory Management**: Real-time stock tracking and updates
- **Admin Dashboard**: Comprehensive backend for managing products, users, orders, and system health
- **Async Task Processing**: Background job processing via ARQ/Celery
- **Caching**: Redis integration for performance optimization
- **CORS & Security**: Built-in security middleware and cross-origin support

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.141+ |
| **Language** | Python 3.14+ |
| **Database** | PostgreSQL 16+ |
| **ORM** | SQLAlchemy 2.0+ (Async) |
| **Database Migrations** | Alembic |
| **Authentication** | JWT (PyJWT) |
| **Validation** | Pydantic v2 |
| **Async Driver** | asyncpg |
| **Caching & Queue** | Redis 5.3+ |
| **Password Hashing** | Argon2 |
| **Task Queue** | ARQ 0.28+ |
| **Code Quality** | Ruff, Black, MyPy |
| **Testing** | Pytest, pytest-asyncio |
| **Containerization** | Docker & Docker Compose |

---

## 📋 Prerequisites

Before getting started, ensure you have the following installed:

- **Python**: 3.14+ (recommended latest stable)
- **PostgreSQL**: 16+ 
- **Redis**: Latest stable version
- **Docker & Docker Compose**: Latest stable versions
- **Git**: Latest stable version
- **pip/uv**: Python package manager (uv recommended for performance)

### Environment Setup

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/bazaarche

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:4200","http://localhost:4201"]

# Environment
ENVIRONMENT=development
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bazaarche-api.git
cd bazaarche-api
```

### 2. Set Up Development Environment

```bash
# Create virtual environment (using uv)
uv sync

# Or using pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Start PostgreSQL and Redis

Using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL**: Available at `localhost:5432`
- **Redis**: Available at `localhost:6379`

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Run the Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

- **Interactive API Docs** (Swagger UI): `http://localhost:8000/docs`
- **Alternative Docs** (ReDoc): `http://localhost:8000/redoc`

### 6. Verify Health Check

```bash
curl http://localhost:8000/health
```

Expected response: `{"status": "ok"}`

---

## 📁 Project Structure

```
bazaarche-api/
├── alembic/                          # Database migrations
│   ├── env.py
│   ├── versions/                     # Migration scripts
│   └── script.py.mako
├── app/                              # Main application
│   ├── __init__.py
│   ├── main.py                       # FastAPI app initialization
│   ├── core/
│   │   └── config.py                 # Settings and configuration
│   ├── db/
│   │   ├── base.py                   # Database base model
│   │   └── model_registry.py         # Model registration
│   └── modules/                      # Feature modules (layered architecture)
│       ├── auth/                     # Authentication & authorization
│       ├── users/                    # User management
│       ├── catalog/                  # Product catalog
│       ├── cart/                     # Shopping cart
│       ├── inventory/                # Inventory management
│       ├── orders/                   # Order management
│       ├── payments/                 # Payment processing
│       └── admin_dashboard/          # Admin operations
│
├── docs/                             # Documentation
│   ├── product-development-document.md
│   ├── architecture-decision-records.md
│   ├── coding-style-guide.md
│   ├── git-workflow-branching-guideline.md
│   └── testing-strategy-qa-plan.md
│
├── tests/                            # Test suite
│   └── test_health.py
│
├── alembic.ini                       # Alembic configuration
├── docker-compose.yml                # Docker services
├── pyproject.toml                    # Project metadata & dependencies
├── README.md                         # This file
└── LICENSE                           # Project license
```

### Module Structure

Each feature module follows a standardized layered architecture:

```
module/
├── __init__.py
├── models.py                         # SQLAlchemy ORM models
├── schemas.py                        # Pydantic request/response schemas
├── repository.py                     # Data access layer (queries)
├── service.py                        # Business logic layer
├── router.py                         # API route handlers
└── exceptions.py                     # Module-specific exceptions
```

---

## 🔄 Module Overview

### **auth**
Handles user authentication, JWT token generation, login/logout, and session management.

### **users**
User profile management, registration, password reset, and user data operations.

### **catalog**
Product browsing, filtering, searching, and category management.

### **cart**
Shopping cart operations: add items, remove items, update quantities, view cart.

### **inventory**
Real-time stock management, availability checks, and inventory updates.

### **orders**
Order creation, tracking, status management, and order history.

### **payments**
Payment processing with abstract gateway pattern for easy integration of multiple payment providers.

### **admin_dashboard**
Administrative operations for managing products, users, orders, and system analytics.

---

## 💻 Development Workflow

### Code Quality

The project uses industry-standard tools for code quality:

- **Ruff**: Fast Python linter (line-length: 100, target: Python 3.13+)
- **Black**: Code formatter (line-length: 100)
- **MyPy**: Static type checker
- **Pytest**: Testing framework

Run linting and formatting:

```bash
# Check code with Ruff
ruff check app/

# Format code with Black
black app/

# Type checking
mypy app/

# Run tests
pytest tests/ -v
```

### Pre-commit Hooks

The project uses pre-commit for automated code quality checks:

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### Git Workflow

Follow the project's branching guidelines:

```bash
# Create a feature branch
git checkout -b feature/feature-name

# Push and create a Pull Request
git push origin feature/feature-name
```

Refer to [git-workflow-branching-guideline.md](docs/git-workflow-branching-guideline.md) for detailed guidelines.

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[Product Development Document](docs/product-development-document.md)** - Business requirements and feature specifications
- **[Architecture Decision Records](docs/architecture-decision-records.md)** - Technical decisions and rationale
- **[Coding Style Guide](docs/coding-style-guide.md)** - Code standards and best practices
- **[Git Workflow & Branching](docs/git-workflow-branching-guideline.md)** - Version control guidelines
- **[Testing Strategy & QA Plan](docs/testing-strategy-qa-plan.md)** - Quality assurance approach
- **[Project Bootstrap Guide](docs/project-bootstrap-guide.md)** - Setup and initialization instructions

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_health.py -v

# Run with coverage
pytest --cov=app tests/
```

Test files are located in the `tests/` directory following pytest conventions.

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t bazaarche-api:latest .
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services included:
- **PostgreSQL** (port 5432)
- **Redis** (port 6379)

---

## 📖 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check Endpoint

```bash
GET /health
```

Response:
```json
{
  "status": "ok"
}
```

---

## 🔐 Security

- **JWT Authentication**: Secure token-based authentication with expiration
- **Password Hashing**: Argon2 algorithm for secure password storage
- **CORS Protection**: Configured CORS middleware
- **Input Validation**: Pydantic-based request validation
- **Async Safety**: All database operations are async-safe

---

## 🚦 Environment Variables

Create a `.env` file with the following variables:

```env
# Core Settings
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/bazaarche

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:4200", "http://localhost:4201"]

# Email (optional for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# Payment Gateway (to be configured)
PAYMENT_GATEWAY_KEY=your-payment-key
```

---

## 📝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) (if exists)
2. Follow the [Coding Style Guide](docs/coding-style-guide.md)
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Commit changes: `git commit -m "feat: add your feature"`
5. Push to branch: `git push origin feature/your-feature`
6. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **M. Mohamadi** - Initial development and architecture

---

## 🤝 Support & Questions

For questions, issues, or suggestions:

- **Email**: m.mohamadi490@gmail.com
- **Open an Issue**: GitHub Issues
- **Documentation**: See `/docs` folder

---

## 🗺️ Roadmap

### Phase 1 (MVP)
- ✅ Core API setup
- ✅ Authentication system
- ✅ Product catalog
- ✅ Shopping cart
- ✅ Order management
- ✅ Payment gateway integration

### Phase 2
- Multi-vendor support
- Advanced search and filtering
- Product recommendations
- Loyalty program
- Discount and coupon system

### Phase 3
- Analytics and reporting
- Mobile app integration
- Advanced shipping options
- Marketplace features

---

**Last Updated**: August 30, 2026
**Version**: 0.1.0 (MVP)
