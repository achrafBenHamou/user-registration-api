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
│   └── 001_initial.sql      # Database schema
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

```bash
# Run tests inside the app container
# Note: Ensure the app service is running before executing tests
docker-compose exec app pytest
```

**Available services:**
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs || http://localhost:8000/redoc


**Made with ❤️ by Achraf Ben Hamou**

