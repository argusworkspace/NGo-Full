# NGO Backend — FastAPI

Modular monolith backend for the NGO Platform built with **FastAPI**, **SQLAlchemy 2 (async)**, **Pydantic v2**, and **PostgreSQL**.

---

## Tech Stack

| Layer | Library |
|---|---|
| Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2 (async) |
| Validation | Pydantic v2 |
| Auth | python-jose (JWT) + passlib (bcrypt) |
| DB Driver | asyncpg (PostgreSQL) |
| Migrations | Alembic |
| Testing | pytest + pytest-asyncio |

---

## Folder Structure

```
app/
├── main.py                     # FastAPI app entry point + CORS middleware
│
├── core/
│   ├── config.py              # Pydantic-settings (reads .env)
│   ├── database.py            # Async SQLAlchemy engine + session + Base
│   └── security.py            # JWT creation/decoding, bcrypt hashing
│
├── modules/                   # Modular monolith — each module owns its slice
│   ├── auth/
│   │   ├── models.py          # SQLAlchemy User model
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── service.py         # Business logic
│   │   ├── router.py          # FastAPI router (POST /auth/login, etc.)
│   │   ├── dependencies.py    # get_current_user dependency
│   │   └── __init__.py
│   ├── donors/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── router.py
│   │   └── __init__.py
│   ├── programs/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── router.py
│   │   └── __init__.py
│   ├── volunteers/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── router.py
│   │   └── __init__.py
│   └── surveys/                # Projects (dynamic JSONB questions) + Responses
│       ├── models.py           # Project, Response
│       ├── schemas.py          # Question/Option/Answer + request/response schemas
│       ├── service.py          # Create/publish/archive, response validation
│       ├── router.py           # project_router (/projects) + response_router (/responses)
│       └── __init__.py
│
└── shared/
    ├── responses.py           # ApiResponse, PaginatedResponse generics
    └── exceptions.py          # AppException subclasses, each with an error_code

alembic/
├── env.py                     # async migration runner, wired to Base.metadata
└── versions/                  # migration scripts (committed — see note below)

tests/
├── conftest.py                 # NullPool test engine, per-test SAVEPOINT rollback, httpx client
├── modules/
│   ├── auth/
│   └── surveys/
└── __init__.py
```

### Modular Monolith Rules

- **A module's router/service never imports from another module's service** — only via shared layer or direct DB query.
- **`shared/`** holds cross-cutting concerns (responses, exceptions).
- **Add a new module** by creating `app/modules/<name>/{models,schemas,service,router,__init__}.py` and registering the router in `main.py`.

---

## API Routes

All routes are prefixed with `/api/v1`.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/login` | No | Get access token |
| POST | `/api/v1/auth/register` | No | Create account |
| GET | `/api/v1/auth/me` | Yes | Current user |
| GET | `/api/v1/donors` | Yes | List donors (paginated) |
| POST | `/api/v1/donors` | Yes | Create donor |
| GET | `/api/v1/donors/{id}` | Yes | Get donor |
| PATCH | `/api/v1/donors/{id}` | Yes | Update donor |
| DELETE | `/api/v1/donors/{id}` | Yes | Delete donor |
| GET | `/api/v1/programs` | Yes | List programs |
| POST | `/api/v1/programs` | Yes | Create program |
| GET | `/api/v1/volunteers` | Yes | List volunteers |
| POST | `/api/v1/volunteers` | Yes | Create volunteer |
| POST | `/api/v1/projects` | ADMIN | Create a project + its question form (starts as `DRAFT`) |
| GET | `/api/v1/projects` | Yes | List projects — ADMIN sees all, VOLUNTEER sees only `PUBLISHED` |
| GET | `/api/v1/projects/{id}` | Yes | Get a project — VOLUNTEER gets 404 for non-published ones |
| PUT | `/api/v1/projects/{id}` | ADMIN | Replace name/description/questions |
| DELETE | `/api/v1/projects/{id}` | ADMIN | Delete a project (cascades to its responses) |
| PATCH | `/api/v1/projects/{id}/publish` | ADMIN | `DRAFT`/`ARCHIVED` → `PUBLISHED` |
| PATCH | `/api/v1/projects/{id}/archive` | ADMIN | → `ARCHIVED`, blocks new submissions |
| POST | `/api/v1/projects/{id}/responses` | Yes | Submit a response to a `PUBLISHED` project |
| GET | `/api/v1/projects/{id}/responses` | ADMIN | List all responses for a project |
| GET | `/api/v1/responses/{id}` | Yes | Get one response — ADMIN any, VOLUNTEER only their own |
| GET | `/health` | No | Health check |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Survey Module

### JWT payload

```json
{ "sub": "<user id>", "role": "ADMIN" | "VOLUNTEER", "exp": 1234567890 }
```

`role` is read from the `users.role` column at login time and embedded directly — the token is the source of truth for authorization on every request; `get_current_user` still re-fetches the user row so a revoked/deleted account is rejected even with a still-valid token.

### Role permissions

| Operation | ADMIN | VOLUNTEER |
|---|---|---|
| Login / register | Yes | Yes (register always creates `VOLUNTEER`, never `ADMIN` — there is no admin self-registration; the single admin account is seeded, see below) |
| Create / update / delete project | Yes | No (403) |
| Publish / archive project | Yes | No (403) |
| View published project | Yes | Yes |
| View draft/archived project by id | Yes | No (404, not 403 — existence isn't leaked) |
| Submit a response | Yes | Yes |
| List all responses for a project | Yes | No (403) |
| View a specific response | Any | Only their own (403 otherwise) |

### Example project (request body for `POST /api/v1/projects`)

```json
{
  "name": "School Health Survey 2026",
  "description": "Survey conducted across government schools",
  "questions": [
    { "id": "q1", "question": "What is the school name?", "type": "text", "required": true },
    { "id": "q2", "question": "Does the school have a library?", "type": "boolean", "required": true },
    {
      "id": "q3",
      "question": "Which facilities are available?",
      "type": "multiple_choice",
      "required": false,
      "options": [
        { "id": "opt1", "label": "Library" },
        { "id": "opt2", "label": "Laboratory" }
      ]
    }
  ]
}
```

Supported `type` values: `text`, `number`, `date`, `single_choice`, `multiple_choice`, `boolean`, `textarea`, `rating`. `single_choice`/`multiple_choice` require a non-empty `options` array; every other type must omit it. `rating` answers must be an integer from 1 to 5.

### Example response submission (`POST /api/v1/projects/{id}/responses`)

```json
{
  "answers": [
    { "questionId": "q1", "answer": "ABC School" },
    { "questionId": "q2", "answer": true },
    { "questionId": "q3", "answer": ["opt1"] }
  ]
}
```

The server validates, per answer, against the project's *current* question definitions — not just anything the client sends: unknown `questionId`s are rejected (`UNKNOWN_QUESTION`), missing required questions are rejected (`MISSING_REQUIRED_ANSWER`), and the answer's shape/type must match the question (`single_choice`/`multiple_choice` values must be real option ids) or it's rejected with `VALIDATION_ERROR`.

### API-wide conventions

- **Survey JSON over the wire is camelCase** (`createdBy`, `submittedAt`, `questionId`) even though the Python/SQLAlchemy layer uses `snake_case` internally — handled via Pydantic's `alias_generator=to_camel` in `app/modules/surveys/schemas.py`. Both casings are accepted on input for leniency, but responses always serialize as camelCase. **Exception:** `POST /api/v1/auth/login`'s `TokenResponse` (`access_token`/`token_type`) is deliberately kept snake_case — that's the OAuth2-style pair the frontend's `AuthTokens` type and `localStorage` key already integrate against.
- **The `{success, message, data}` / `{success, message, error}` envelope applies globally**, including successful responses — see the `wrap_success_envelope` middleware in `app/main.py` for the success side and `app/shared/exceptions.py`'s `error_code` attributes / the exception handlers in `app/main.py` for the error side. The whole API — auth, donors, programs, volunteers, projects, responses — is consistent for the frontend.

---

## Getting Started

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit DATABASE_URL, APP_SECRET_KEY

# 4. Run migrations
alembic upgrade head

# 5. Seed dev data (see "Seed Data" below)
python -m app.seed

# 6. Start the server
uvicorn app.main:app --reload --port 8000
```

### Neon DB connection notes

- Use `postgresql+asyncpg://...` (not `postgresql://`) — this app uses the async SQLAlchemy engine.
- Drop `channel_binding=require` from Neon's copy-paste connection string — that's a libpq-only parameter and asyncpg errors on it. `sslmode=require` isn't understood by this SQLAlchemy/asyncpg version either; TLS is instead forced via `connect_args={"ssl": True}` in `app/core/database.py` and `alembic/env.py` whenever the host contains `neon.tech`.
- **Use Neon's direct (non-`-pooler`) hostname**, not the PgBouncer-pooled one. This app already pools connections itself via SQLAlchemy's async engine, and stacking Neon's transaction-mode pooler underneath it causes `asyncpg.exceptions.InvalidCachedStatementError` on the dialect's explicit server-side `PREPARE` calls (most visible right after schema changes). If you only have a pooled connection string, just remove the `-pooler` segment from the hostname.

### Seed data

```bash
python -m app.seed
```

Creates (idempotent — safe to re-run):

- ADMIN: `admin@gmail.com` / `admin123`
- VOLUNTEER: `user@example.com` / `User@123`
- One sample published project ("School Health Survey 2026") with one question of each supported type

**These are development credentials only — change or remove them before any production deployment.**

### Migrations

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
alembic downgrade -1   # roll back one revision
```

Migration files under `alembic/versions/` are committed to version control (the original scaffold's `.gitignore` excluded them, which would have silently dropped migration history from the repo — fixed).

### Tests

```bash
pytest -v
```

Tests run against the **real** `DATABASE_URL` from `.env` — there's no separate test database or mocking. Each test gets its own connection (`NullPool`, to avoid asyncpg connections crossing pytest-asyncio's per-test event loops) wrapped in an outer transaction that's rolled back at teardown via `SAVEPOINT`, so nothing persists even though the app's own `commit()` calls run for real during the request. Because every test opens a fresh network connection to Neon, the full suite takes a few minutes — this is a deliberate correctness-over-speed tradeoff for a small test suite; a CI setup with a closer/local Postgres would be much faster.

---

## CORS

CORS is configured in `app/main.py` via `CORSMiddleware`. Allowed origins are read from the `CORS_ORIGINS` env var (comma-separated):

```
CORS_ORIGINS=http://localhost:3000,https://your-production-domain.com
```

`allow_credentials=True` is set so the frontend can send cookies and `Authorization` headers.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `development` or `production` |
| `APP_SECRET_KEY` | — | JWT signing secret (required) — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `APP_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT expiry |
| `DATABASE_URL` | — | PostgreSQL async URL (`postgresql+asyncpg://...`) — see Neon notes above |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins (this is how the frontend's dev URL gets configured) |

---

## Branch Strategy

- `main` — production-ready releases
- `dev` — integration branch; all features merge here first
- Feature branches cut from `dev`: `feat/<name>`, `fix/<name>`, `chore/<name>`
