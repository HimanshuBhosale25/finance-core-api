# FinanceCore API

A production-ready REST API backend for managing financial records, built with **FastAPI**, **MySQL**, and **Redis**. Designed around role-based access control, it serves as a reliable backend for any finance dashboard or accounting system — handling everything from transaction management to aggregated analytics.

---

## Features

- **JWT Authentication** — secure login, token-based auth, real logout via Redis blacklisting
- **Role-Based Access Control** — three-tier permission model (Viewer / Analyst / Admin) enforced at the dependency layer
- **Financial Records Management** — full CRUD with soft delete, filtering, search, and pagination
- **Dashboard Analytics** — aggregated summary, category breakdowns, monthly trends, and recent activity — all via optimized single-pass SQL queries
- **Rate Limiting** — per-IP sliding window via Redis + SlowAPI
- **User Management** — create, update, activate/deactivate users with role assignment
- **Auto API Docs** — interactive Swagger UI and ReDoc out of the box

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (Python 3.11) |
| Database | MySQL |
| ORM | SQLAlchemy + Alembic |
| Cache / Auth Store | Redis |
| Auth | JWT via `python-jose` |
| Validation | Pydantic v2 |
| Package Manager | uv |
| Server | Uvicorn |

---

## Project Structure
```sh
finance-backend/
├── app/
│ ├── main.py # App entry point, middleware, error handlers
│ ├── core/
│ │ ├── config.py # Environment config via pydantic-settings
│ │ ├── security.py # JWT + bcrypt password utilities
│ │ └── dependencies.py # DI chain: get_db → get_current_user → require_roles
│ ├── db/
│ │ ├── base.py # SQLAlchemy declarative base
│ │ └── session.py # Engine + SessionLocal
│ ├── models/ # SQLAlchemy ORM models
│ │ ├── user.py
│ │ └── financial_record.py
│ ├── schemas/ # Pydantic request/response schemas
│ │ ├── auth.py
│ │ ├── user.py
│ │ ├── record.py
│ │ └── dashboard.py
│ ├── services/ # Business logic layer
│ │ ├── auth_service.py
│ │ ├── user_service.py
│ │ ├── record_service.py
│ │ └── dashboard_service.py
│ └── api/v1/
│ ├── router.py
│ └── endpoints/
│ ├── auth.py
│ ├── users.py
│ ├── records.py
│ └── dashboard.py
├── alembic/ # Database migrations
├── seed.py # Seeds the first admin user
├── .env.example
└── pyproject.toml
```

## Access Control

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| View records | ✅ | ✅ | ✅ |
| Filter / search records | ✅ | ✅ | ✅ |
| Create records | ❌ | ✅ | ✅ |
| Update records | ❌ | ❌ | ✅ |
| Delete records (soft) | ❌ | ❌ | ✅ |
| View dashboard & analytics | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

RBAC is enforced via FastAPI's dependency injection system. The `require_roles()` dependency factory chains onto `get_current_user`, which validates the JWT, checks the Redis blacklist, confirms the user exists, and verifies the account is active — before any route handler runs.

---

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- MySQL (local or remote instance)
- Redis (Docker recommended)

### 1. Clone and install

```bash
git clone https://github.com/your-username/finance-backend.git
cd finance-backend
uv sync
```

### 2. Start Redis

```bash
docker run -d --name finance-redis -p 6379:6379 redis:alpine
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
APP_ENV=development
APP_DEBUG=True
APP_NAME="Finance Backend"

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=finance_db

JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://localhost:6379
REDIS_RATE_LIMIT_PER_MINUTE=60
```

### 4. Create the database

In MySQL Workbench or any MySQL client:

```sql
CREATE DATABASE finance_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

### 5. Run migrations

```bash
uv run alembic upgrade head
```

### 6. Seed the first admin user

```bash
uv run python seed.py
```

This creates:
- **Email:** `admin@finance.com`
- **Password:** `admin123`
- **Role:** `ADMIN`

> Change these credentials immediately after first login.

### 7. Start the server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

---

## API Documentation

Once running, visit:

- **Swagger UI** → [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** → [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health check** → [http://localhost:8000/health](http://localhost:8000/health)

---

## API Reference

### Auth — `/api/v1/auth`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/register` | Public | Register a new user (default role: Viewer) |
| `POST` | `/login` | Public | Login and receive a JWT token |
| `POST` | `/logout` | Required | Invalidate current token via Redis blacklist |
| `GET` | `/me` | Required | Get current authenticated user |

### Users — `/api/v1/users`

| Method | Endpoint | Role | Description |
|---|---|---|---|
| `GET` | `/` | Admin | List all users |
| `POST` | `/` | Admin | Create a user with a specific role |
| `GET` | `/{id}` | Admin | Get user by ID |
| `PATCH` | `/{id}` | Admin | Update name or role |
| `PATCH` | `/{id}/status` | Admin | Activate or deactivate a user |
| `DELETE` | `/{id}` | Admin | Delete a user |

### Financial Records — `/api/v1/records`

| Method | Endpoint | Role | Description |
|---|---|---|---|
| `GET` | `/` | Viewer+ | List records with filters and pagination |
| `POST` | `/` | Analyst+ | Create a new financial record |
| `GET` | `/{id}` | Viewer+ | Get a single record by ID |
| `PUT` | `/{id}` | Admin | Update a record |
| `DELETE` | `/{id}` | Admin | Soft delete a record |

**Query parameters for `GET /records`:**

| Param | Type | Description |
|---|---|---|
| `type` | `INCOME` \| `EXPENSE` | Filter by record type |
| `category` | string | Filter by category (partial match) |
| `start_date` | `YYYY-MM-DD` | Filter from date |
| `end_date` | `YYYY-MM-DD` | Filter to date |
| `search` | string | Search within notes |
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Results per page (default: 20, max: 100) |

### Dashboard — `/api/v1/dashboard`

| Method | Endpoint | Role | Description |
|---|---|---|---|
| `GET` | `/` | Analyst+ | Full dashboard in one response |
| `GET` | `/summary` | Analyst+ | Total income, expenses, net balance |
| `GET` | `/category-breakdown` | Analyst+ | Totals grouped by category and type |
| `GET` | `/trends` | Analyst+ | Monthly income vs expense trends |
| `GET` | `/recent-activity` | Analyst+ | Latest N records (default: 10) |

---

## Data Models

### User
``` sh
id, name, email, password_hash,
role: VIEWER | ANALYST | ADMIN,
status: ACTIVE | INACTIVE,
created_at, updated_at
``` 

### FinancialRecord
```sh
id, created_by (FK → users),
amount (DECIMAL 15,2), type: INCOME | EXPENSE,
category, date, notes,
deleted_at (soft delete),
created_at, updated_at
```

## Design Decisions & Assumptions

**Soft delete over hard delete** — financial records are never physically removed. `deleted_at` is set on deletion and all queries filter it out globally. This preserves audit trails.

**JWT blacklisting via Redis** — since JWTs are stateless, real logout requires server-side invalidation. On logout, the token is stored in Redis with TTL equal to its remaining lifetime. Zero stale data, zero DB queries on auth.

**Decimal over Float for amounts** — all monetary values use `DECIMAL(15, 2)` in MySQL to avoid floating-point precision errors.

**Service layer separation** — routes contain zero business logic. All logic lives in services, making it independently testable and easy to maintain.

**Role hierarchy via explicit lists** — roles are not hierarchical by inheritance. Each endpoint explicitly declares which roles are permitted (`require_roles(ANALYST, ADMIN)`), keeping access rules visible and auditable at the route level.

**Single aggregation query for dashboard** — the summary endpoint uses a single SQL query with conditional `SUM` via SQLAlchemy `case()` rather than multiple queries, minimizing DB round trips.

**Public registration defaults to Viewer** — anyone can self-register but gets the most restricted role. Elevating to Analyst or Admin requires an existing Admin.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `APP_ENV` | Environment name | `development` |
| `DB_HOST` | MySQL host | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_USER` | MySQL username | — |
| `DB_PASSWORD` | MySQL password | — |
| `DB_NAME` | Database name | — |
| `JWT_SECRET_KEY` | JWT signing key (min 32 chars) | — |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `30` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `REDIS_RATE_LIMIT_PER_MINUTE` | Max requests per minute per IP | `60` |