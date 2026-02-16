# User Registration API - Architecture

,
**Pattern**: Layered Clean Architecture (Pragmatic)

## Overview

A simple 3-layer architecture for user registration with email activation code (1-minute TTL).

**Flow**: `Client → API → Service → Repository → Database`

**Layers**:
- **API Layer** - HTTP interface (FastAPI routers)
- **Service Layer** - Business logic (password hashing, code generation, TTL validation)
- **Repository Layer** - Data access (raw SQL with asyncpg)
- **Client Layer** - External HTTP services (isolated HTTP client for Mailpit)

---

## Architecture Diagram

```
         CLIENT
           │
           ▼
    ┌──────────────┐
    │  API Layer   │  FastAPI routers + Pydantic validation
    └──────┬───────┘
           │ Depends()
           ▼
    ┌──────────────┐
    │Service Layer │  Business logic (hash, generate code, validate TTL)
    └──────┬───────┘
           │
      ┌────┴────┐
      ▼         ▼
 ┌─────────┐ ┌────────────┐
 │Repository│ │ Client    │  Data access + External service client
 └────┬────┘ │  Layer     │
      ▼      └─────┬──────┘
 ┌─────────┐      ▼
 │Postgres │ ┌────────────┐
 │   DB    │ │  Mailpit   │
 └─────────┘ │  (Email)   │
             └────────────┘
```

### Layer Responsibilities

| Layer | What It Does | What It Doesn't Do |
|-------|-------------|-------------------|
| **API** | Validate HTTP requests, Basic Auth, return JSON | ❌ No business logic, No SQL |
| **Service** | Hash passwords, generate codes, check TTL, orchestrate | ❌ No HTTP details, No raw SQL |
| **Repository** | Execute SQL queries, return dicts | ❌ No business logic, No password hashing |
| **Client** | Handle HTTP communication with external services | ❌ No business logic |

---

## Project Structure

```
user-registration-api/
│
├── app/
│   ├── main.py                    # FastAPI app entry point
│   │
│   ├── api/v1/                    # API Layer
│   │   ├── router.py
│   │   └── users.py
│   │
│   ├── schemas/user.py            # Pydantic models
│   ├── services/
│   │   ├── user_service.py        # Business logic
│   │   └── email_service.py       # Email sending orchestration
│   ├── repositories/user_repository.py  # SQL queries
│   ├── clients/mailpit_client.py  # Mailpit HTTP client
│   │
│   ├── db/pool.py                 # Database connection pool
│   ├── core/
│   │   ├── config.py              # Settings
│   │   └── security.py            # Password hashing, Basic Auth
│   │
│   ├── dependencies/deps.py       # FastAPI Depends
│   └── exceptions/                # Custom errors
│       ├── base.py
│       └── user.py
│
├── tests/
│   ├── conftest.py
│   ├── integration/test_users.py
│   ├── unit/
│   │   ├── clients/test_mailpit_client.py
│   │   ├── services/test_email_service.py
│   │   
│
├── migrations/init.sql
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── ARCHITECTURE.md
```

---

## Request Flow Example (Activation)

```
1. Client Request
   POST /api/v1/users/activate
   Authorization: Basic (email:password)
   Body: {"code": "1234"}

2. API Layer → Validates auth + JSON → Calls service

3. Service Layer → Checks:
   ✓ Code exists?
   ✓ Expired? (now > expires_at)
   ✓ Code matches?
   → Updates user.is_active = TRUE
   → Deletes used code

4. Repository Layer → Executes SQL (UPDATE + DELETE)

5. Response → 200 OK: {"message": "Account activated!"}
```

---

## Database Conception

### Entity-Relationship Diagram

```
┌─────────────────────────────────────┐
│             USERS                   │
├─────────────────────────────────────┤
│ PK  id              UUID            │
│ UK  email           VARCHAR(255)    │
│     hashed_password VARCHAR(255)    │
│     is_active       BOOLEAN         │
│     created_at      TIMESTAMP       │
└──────────────┬──────────────────────┘
               │
               │ 1:1 (optional)
               │
               ▼
┌─────────────────────────────────────┐
│      ACTIVATION_CODES               │
├─────────────────────────────────────┤
│ PK  id          UUID                │
│ FK  user_id     UUID ───────────┐   │
│ UK  user_id     (UNIQUE)        │   │
│     code        VARCHAR(4)      │   │
│     created_at  TIMESTAMP       │   │
│     expires_at  TIMESTAMP       │   │
└─────────────────────────────────────┘
                                  │
                     ON DELETE CASCADE
```

### Tables Explanation

#### 1. **users** Table
Stores registered users.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| `id` | UUID | PRIMARY KEY | Auto-generated unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email (login) |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `is_active` | BOOLEAN | DEFAULT FALSE | Account activation status |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Registration timestamp |

**Indexes**:
- Primary key on `id`
- Unique index on `email` (fast lookup for login)

**Business Rules**:
- Email must be unique
- Password stored as bcrypt hash (never plain text)
- New users start with `is_active = FALSE`

---

#### 2. **activation_codes** Table
Stores temporary activation codes with 1-minute TTL.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| `id` | UUID | PRIMARY KEY | Auto-generated unique identifier |
| `user_id` | UUID | FOREIGN KEY, UNIQUE | References users(id) |
| `code` | VARCHAR(4) | NOT NULL | 4-digit activation code |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Code generation time |
| `expires_at` | TIMESTAMP | NOT NULL | Expiration time (created_at + 1 min) |

**Indexes**:
- Primary key on `id`
- Unique constraint on `user_id` (one active code per user)
- Index on `user_id` for fast lookup
- Index on `expires_at` for cleanup queries

**Business Rules**:
- One user can have only ONE activation code at a time (UNIQUE constraint)
- Code expires after 1 minute (`expires_at`)
- When user is deleted, activation codes are auto-deleted (ON DELETE CASCADE)
- After successful activation, code is deleted

---

### Data Lifecycle

```
1. User Registration
   INSERT INTO users → is_active = FALSE

2. Request Activation Code
   INSERT INTO activation_codes → expires_at = NOW() + 1 minute
   (If code already exists, DELETE old + INSERT new)

3. User Activates (within 1 minute)
   UPDATE users SET is_active = TRUE
   DELETE FROM activation_codes WHERE user_id = ?

4. Code Expires (after 1 minute)
   SELECT fails if NOW() > expires_at
   (Optional: Cleanup job to delete expired codes)
```

---

## API Endpoints

### 1. Register User
```http
POST /api/v1/users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
**Success (201)**: `{"id": "...", "email": "...", "is_active": false}`

### 2. Send Activation Code
```http
POST /api/v1/users/activation-code
Authorization: Basic base64(email:password)
```
**Success (200)**: `{"message": "Activation code sent to your email"}`  
**Email**: "Your activation code is: 1234. Expires in 1 minute."

### 3. Activate User
```http
POST /api/v1/users/activate
Authorization: Basic base64(email:password)
Content-Type: application/json

{
  "code": "1234"
}
```
**Success (200)**: `{"message": "Account activated successfully"}`  
**Errors**: `401` Wrong credentials, `400` Invalid/expired code

---

## Technology Stack

| Component | Choice         | Reason |
|-----------|----------------|--------|
| Framework | FastAPI        | Required + async + DI |
| Language | Python 3.14+   | Required |
| Database | PostgreSQL 15  | UUID support, async driver |
| DB Driver | asyncpg        | Fastest PostgreSQL driver |
| Passwords | bcrypt         | Industry standard |
| HTTP Client | httpx          | Async support |
| Validation | Pydantic v2    | Built into FastAPI |
| Testing | pytest         | Standard |
| Email (Dev) | Mailpit        | Local SMTP with web UI |
| Deployment | Docker Compose | Simple container orchestration |

---

## Testing Strategy

**3 Levels**:

1. **Unit Tests** - Business logic in isolation (mock repo + SMTP)
2. **Integration Tests** - Full HTTP → DB flow (real test DB)

---

## Why This Architecture Works

**Simple** - 3 layers, clear boundaries  
**Testable** - Easy to mock each layer  
**Maintainable** - Change one layer without breaking others  
**Scalable** - Can add event bus/workers later if needed  
**Production-ready** - Async, tested, containerized  


