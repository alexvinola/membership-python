# membership-api

A membership and subscription management REST API built with **Python** and **FastAPI**.

## Why I built this

I'm a .NET developer by trade and wanted to push myself outside my comfort zone by building a real, production-oriented backend in Python. Rather than following a tutorial, I took a domain I already understand well — membership and subscription management — and rebuilt it from scratch using the Python ecosystem.

The goal was to learn how Python's idioms, tooling, and framework conventions compare to the .NET world (ASP.NET Core, Entity Framework, MediatR, etc.) by solving the same problems I solve every day, just with different tools.

## Tech stack

| Concern | Tool |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy 2.0](https://docs.sqlalchemy.org/) |
| Database | PostgreSQL ([Neon](https://neon.tech/)) |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Auth | JWT via `python-jose` + `passlib` (bcrypt) |
| Email | SMTP + Jinja2 HTML templates |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Testing | `pytest` + `pytest-asyncio` |

## Architecture

The project follows a layered architecture, intentionally mirroring patterns familiar from .NET:

```
app/
├── api/routes/        # Controllers — thin, only wires HTTP in/out
├── services/          # Application logic (AuthService, VerificationService...)
├── repositories/      # Data access layer (UserRepository, VerificationRepository)
├── models/            # SQLAlchemy ORM models
├── schemas/           # Pydantic request/response models (DTOs)
├── uow/               # Unit of Work pattern
├── core/              # Config, database, security, logging, exceptions
└── templates/         # Jinja2 email templates
```

The **Unit of Work** pattern and **Repository** pattern should feel familiar to anyone coming from Entity Framework / Clean Architecture in .NET.

## Domain model

| Model | Description |
|---|---|
| `User` | Core user with subscription plan (`FREE`, `PRO`, `PREMIUM`) and status |
| `Account` | OAuth provider accounts (NextAuth-compatible) |
| `UserSession` | Database sessions |
| `VerificationCode` | 6-digit OTP codes for email verification and password reset |
| `WebhookEvent` | Stripe webhook events log |

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Login, returns JWT |
| `GET` | `/api/v1/users/me` | Get current user (JWT required) |
| `PATCH` | `/api/v1/users/me` | Update current user (JWT required) |

Interactive docs available at `/docs` (Swagger UI) and `/redoc` once the server is running.

## Getting started

**1. Clone and create a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```


**3. Run the server**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## What I learned

- FastAPI's dependency injection system is elegant and surprisingly close in spirit to ASP.NET Core's `IServiceCollection`
- SQLAlchemy 2.0's `Mapped` / `mapped_column` API feels closer to EF Core's fluent configuration than the old declarative style
- Pydantic v2 is a great replacement for FluentValidation — fast and expressive
- Python's lack of interfaces means leaning on duck typing and abstract base classes instead of explicit contracts
- The ecosystem around async Python (asyncio, async SQLAlchemy) is powerful but requires more deliberate design decisions than in .NET

## A note on architecture

The current architecture — Repository pattern, Unit of Work, strict layering — is heavily influenced by my background in .NET and languages where this kind of structure is the norm. I'm fully aware that a Python developer would likely raise an eyebrow at the amount of boilerplate and the over-engineering relative to what FastAPI projects typically look like.

This is intentional for now: it was the fastest way for me to get productive while learning the language and ecosystem. However, the plan is to keep evolving this project towards a more idiomatic Python architecture — flatter, less ceremony, leaning into what makes FastAPI and SQLAlchemy powerful on their own terms rather than forcing .NET patterns onto them.
