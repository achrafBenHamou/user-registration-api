# User Registration API

A RESTful API for user registration with email-based account activation
(activation code TTL: **1 minute**).

------------------------------------------------------------------------

## Tech Stack

-   **Python** 3.14
-   **FastAPI** 0.129.0
-   **Poetry** -- Dependency management
-   **Docker & Docker Compose** -- Containerization & orchestration
-   **PostgreSQL** -- Relational database

------------------------------------------------------------------------

## Project Structure

    user-registration-api/
    ├── app/
    │   └── main.py              # Main FastAPI application (standalone)
    ├── migrations/
    │   └── init.sql             # Initial database schema
    ├── Dockerfile               # Application image definition
    ├── docker-compose.yml       # Multi-container setup
    ├── pyproject.toml           # Poetry configuration & dependencies
    └── README.md

------------------------------------------------------------------------

## Quick Start

### Prerequisites

-   Docker
-   Docker Compose

### Run the Application

``` bash
# Navigate to the project directory
cd user-registration-api

# Build and start services
docker-compose up --build -d

# Verify the application is running
curl http://localhost:8000/health
```

------------------------------------------------------------------------

## Running Tests

### Run Tests

``` bash
docker-compose exec api pytest
```

### Run Tests with Coverage

``` bash
docker-compose exec api poetry run pytest --cov=app --cov-report=term-missing
```

------------------------------------------------------------------------

## Database

-   PostgreSQL runs in a dedicated container.
-   Database schema is initialized automatically using:
```
migrations/init.sql
```
-   No migration framework is included (for simplicity).
-   Upgrade/downgrade scripts can be added later if needed.

### Connect to the Database

``` bash
docker-compose exec db psql -U postgres -d user_registration_db

# List tables
\dt
```

Expected tables:

    Schema |       Name       | Type  |  Owner
    -------+------------------+-------+---------
    public | activation_codes | table | postgres
    public | users            | table | postgres

------------------------------------------------------------------------

## Available Services


  Service              URL
  -------------------- -----------------------------
  - API                  http://localhost:8000
  - Swagger Docs         http://localhost:8000/docs
  - ReDoc                http://localhost:8000/redoc
  - Mailpit (Email UI)   http://localhost:8025

------------------------------------------------------------------------

## API Workflow

### 1. Register a User

**Endpoint:** `POST /api/v1/users/register`

``` bash
curl -X POST 'http://localhost:8000/api/v1/users/register'   -H 'Content-Type: application/json'   -d '{
    "email": "test@example.com",
    "password": "MySecurePass123!"
  }'
```

------------------------------------------------------------------------

### 2. Retrieve Activation Code

-   Check Mailpit at: http://localhost:8025 
-   Code is also logged in the console (for testing).

If expired (TTL: 1 minute):

**Endpoint:** `POST /api/v1/users/activation-code`

``` bash
curl -X POST 'http://localhost:8000/api/v1/users/activation-code'   -u 'test@example.com:MySecurePass123!'
```

------------------------------------------------------------------------

### 3. Activate the User

**Endpoint:** `POST /api/v1/users/activate`

``` bash
curl -X POST 'http://localhost:8000/api/v1/users/activate'   -H 'Content-Type: application/json'   -u 'test@example.com:MySecurePass123!'   -d '{
    "code": "1234"
  }'
```

------------------------------------------------------------------------

## Notes

-   Basic Authentication is required for activation-related endpoints.
-   Activation codes expire after **1 minute** (Could be modified on application settings).
-   Users can request a new activation code if needed.

------------------------------------------------------------------------

## Author

Made with ❤️ by **Achraf Ben Hamou**
