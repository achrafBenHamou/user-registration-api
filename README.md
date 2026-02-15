# User Registration API 

REST API for user registration with email activation code (1-minute TTL).

## Tech Stack

- **Python** 3.14
- **FastAPI** 0.129.0  
- **Poetry** - Dependency management
- **Docker & Docker Compose** - Containerization

## Project Structure

```
user-registration-api/
├── app/
│   └── main.py              # Complete application (standalone)
├── migrations/
│   └── init.sql      # Database schema
├── Dockerfile               # Docker image for the application
├── docker-compose.yml       # Service orchestration
├── pyproject.toml           # Poetry dependencies
└── README.md
```

## Quick Start

### Prerequisites
- Docker & Docker Compose installed

### Launch

```bash
# 1. Clone the project
cd user-registration-api
# 2. Build and start services
docker-compose up --build -d
# 3. Check everything is working
curl http://localhost:8000/health
```
### Running Tests
Run tests using pytest inside the app container
```bash
# Run tests inside the app container
# Note: Ensure the app service is running before executing tests
docker-compose exec app pytest
```
Run tests with coverage report
```bash
# Run tests with coverage report inside the app container
docker-compose exec api poetry run pytest --cov=app --cov-report=term-missing
```
### Database
- **PostgreSQL** running in a separate container
- Migrations are located in the `migrations/` directory 
- The first migration on `migrations/init.sql` sets up tables and indexes automatically when the database container starts.
- Migration framework (not included in this project for simplicity).
- Upgrade/ downgrade scripts can be added in the future for better schema management.
- To show tables in the database, you can connect to the PostgreSQL container using this commands :
```bash
    # Connect to the PostgreSQL container
    docker-compose exec db psql -U postgres -d user_registration_db
    # List tables in the database
    \dt
```
You  should see these tables in the database :
```
     Schema |       Name       | Type  |  Owner   
    --------+------------------+-------+----------
     public | activation_codes | table | postgres
     public | users            | table | postgres
    (2 rows)
````

---

- **Available services:**
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs || http://localhost:8000/redoc


**Made with ❤️ by Achraf Ben Hamou**

