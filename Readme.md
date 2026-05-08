# DCC User Model — Identity & Authentication Service

> **Distributed Cloud Computing — Team Project**  
> Part 1 of 4: Tenant & User Registration

---

## What this module does

Every other service in the DCC platform (compute, storage, networking) trusts the identities this module manages. This part covers:

- Creating organisations (tenants)
- Registering users under a tenant
- Listing users per tenant

**Coming in later parts:** Login (JWT issuance), Token Refresh, Logout (Redis blacklist), Profile management, Admin controls.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI (async) |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Validation | Pydantic v2 |
| Password Hashing | bcrypt (cost factor 12) |
| Containerisation | Docker + Compose |

---

## Project Structure

```
user_model/
├── app/
│   ├── config.py              # Environment variables
│   ├── database.py            # Async SQLAlchemy engine + session
│   ├── models.py              # Tenant, User ORM models
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── main.py                # FastAPI app + error handlers
│   ├── routers/
│   │   ├── auth.py            # POST /auth/register
│   │   ├── users.py           # GET /users
│   │   └── tenants.py         # POST /tenants, GET /tenants
│   └── services/
│       └── registration.py    # Registration business logic
├── migrations/
│   └── 0001_initial.py        # Alembic migration
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Running the project

### Option A — Docker (recommended)

Requires: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
cp .env.example .env
docker compose up --build   # first time only
docker compose up           # every time after
```

### Option B — Local (no Docker)

Requires: Python 3.12+, PostgreSQL running locally

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # edit DATABASE_URL to your local DB
uvicorn app.main:app --reload
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| POST | `/tenants` | Create a new tenant (organisation) |
| GET | `/tenants` | List all tenants |
| POST | `/auth/register` | Register a new user |
| GET | `/users` | List users (filter by `?tenant_id=`) |

Interactive docs: **http://localhost:8000/docs**

---

## Correct order of operations

Since every user must belong to a tenant, always create the tenant first:

### Step 1 — Create a tenant

`POST /tenants`
```json
{
  "name": "Acme Corp",
  "plan": "free"
}
```
Copy the `tenant_id` from the response.

### Step 2 — Register a user

`POST /auth/register`
```json
{
  "email": "alice@example.com",
  "username": "alice",
  "password": "Secure123",
  "tenant_id": "<tenant_id from step 1>"
}
```

### Step 3 — View registered users

`GET /users?tenant_id=<tenant_id>`

---

## Password rules

| Rule | Requirement |
|---|---|
| Minimum length | 8 characters |
| Uppercase | At least 1 uppercase letter |
| Digit | At least 1 number |

---

## Error format

All errors follow a consistent envelope:

```json
{
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "Email 'alice@example.com' is already registered.",
    "field": "email",
    "request_id": "uuid-for-tracing",
    "timestamp": "2025-04-28T10:00:00Z"
  }
}
```

---

## DCC Design Principles applied

| Principle | Status |
|---|---|
| Multi-tenancy (`tenant_id` isolation) | ✅ |
| Region-aware user assignment | ✅ |
| Stateless design (no server sessions) | ✅ |
| Distributed tracing (`X-Request-ID`) | ✅ |
| Standard error envelope across all nodes | ✅ |
| bcrypt password hashing (cost 12) | ✅ |
| Containerised & reproducible environment | ✅ |
| JWT stateless auth | ⏳ Part 2 |
| Redis token blacklist | ⏳ Part 3 |
| Admin controls | ⏳ Part 4 |