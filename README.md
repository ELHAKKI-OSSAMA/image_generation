# Ofotolab — AI Image Generation Platform

A full-stack web application for generating images from Stable Diffusion models, with
multi-tenant authentication, a granular permission system, organizations & events,
subscription plans and a billing/payment layer.

- **Frontend:** Vue 3 + Vite + Vuetify + TailwindCSS + Pinia
- **Backend:** FastAPI + async SQLAlchemy + PostgreSQL + Redis (optional in development)

> **Status:** active project / work in progress. The documented and supported way to run
> the backend is the FastAPI monolith (`backend/main.py`). A microservices split
> (`gateway`, `image_service`, `model_service`) and its `docker-compose.yml` are
> **experimental** and not fully wired up yet.

---

## Features

- **Authentication & accounts** — registration, login, JWT access/refresh tokens,
  Argon2 password hashing, e-mail verification and optional two-factor (TOTP/QR).
- **Role model** — super admin, organization owner/admin, organization member, and
  end user (event participant), each with its own onboarding flow.
- **Permissions** — fine-grained, cacheable permission checks (Redis-backed when available).
- **Organizations & events** — organizations manage members, events and participants.
- **Image generation** — manage Stable Diffusion models / versions and generate images.
- **Subscriptions & billing** — plans, subscriptions and a payment-gateway layer.
- **Admin** — user/model/permission management, analytics, logs and system settings.

## Tech stack

| Layer      | Technologies |
| ---------- | ------------ |
| Frontend   | Vue 3, Vite, Vuetify, TailwindCSS, Pinia (+ persisted state), Vue Router, axios, Chart.js |
| Backend    | FastAPI, SQLAlchemy 2 (async), asyncpg, Pydantic v2, Uvicorn |
| Database   | PostgreSQL 14 (+ `uuid-ossp` extension) |
| Cache      | Redis (optional in development, required when `ENV=production`) |
| Auth       | python-jose / PyJWT, passlib + argon2, fastapi-mail, qrcode (2FA) |
| Migrations | Alembic |

## Project structure

```
image_generation/
├── backend/                  # FastAPI application
│   ├── main.py               # App entry point (the supported way to run the backend)
│   ├── api/v1/               # Versioned API routes (auth, admin, organization, profile…)
│   ├── routers/              # Additional feature routers (models, events, billing…)
│   ├── services/             # Business logic (auth, email, image, organization…)
│   ├── core/                 # Database, Redis, security, permissions
│   ├── database/             # Models, schemas, seed data and schema docs
│   ├── migrations/           # Alembic migrations
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # Vue 3 single-page application
│   ├── src/                  # views, components, stores, services, router
│   ├── package.json
│   └── .env.example
├── postman/                  # Postman collections for the API
├── docker-compose.yml        # Experimental microservices stack
└── .env.example              # Values used by docker-compose
```

## Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [PostgreSQL 14+](https://www.postgresql.org/) with the `uuid-ossp` extension
- (Optional) [Redis](https://redis.io/) — only required when running with `ENV=production`

## Getting started

### 1. Database

Create a database and enable the UUID extension (the backend will create the database on
startup if it is missing, but the extension must exist):

```sql
CREATE DATABASE ofotolab;
\c ofotolab
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env        # then edit .env with your values
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

On first start the backend creates the schema, then seeds a default super-admin account
and a default plan, and loads the Stable Diffusion catalogue from
`database/data/init_model.json`.

- API: http://localhost:8000
- Interactive docs (Swagger UI): http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_URL defaults to http://localhost:8000
npm run dev
```

The app is served at http://localhost:5173.

## Environment variables

Configuration is loaded from `.env` files (never committed). Templates are provided:

- `backend/.env.example` — database, JWT secret, Redis, SMTP, CORS allow-list.
- `frontend/.env.example` — `VITE_API_URL`.
- `.env.example` (root) — values consumed by `docker-compose.yml`.

## Database & migrations

SQLAlchemy models live in `backend/database/models/`. The schema is created automatically
on startup; Alembic migrations (`backend/migrations/`) are available for incremental
changes:

```bash
cd backend
alembic upgrade head
```

## Docker (experimental)

A `docker-compose.yml` is provided for the experimental microservices stack. Copy
`.env.example` to `.env` first so the Postgres password is supplied, then:

```bash
docker compose up --build
```

> This path is a work in progress and not yet at parity with the monolith.

## Security notes

- All secrets come from environment variables — no credentials are committed.
- On first run a **default super-admin account is seeded** (see
  `backend/core/database.py`). Change its password immediately and never ship the
  defaults to a real environment.
- Set a strong, random `SECRET_KEY` and a real `POSTGRES_PASSWORD` before any deployment.

## License

Released under the [MIT License](LICENSE).
