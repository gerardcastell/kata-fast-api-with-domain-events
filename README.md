# Insurance API with FastAPI

A modern FastAPI application demonstrating domain-driven design patterns, dependency injection, and event-driven architecture. This project showcases clean architecture principles with a focus on maintainability and scalability.

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **uv** (Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Docker & Docker Compose** (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd events-with-fast-api
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

4. **Run the application**

   ```bash
   # Development mode with hot reload
   fastapi dev app/main.py

   # Or using uvicorn directly
   uv run uvicorn app.main:app --reload
   ```

5. **Access the application**
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health/live

## 🐳 Docker Setup

### Production Mode

```bash
# Build and run the application
docker-compose up --build

# Run in background
docker-compose up -d --build
```

Access at: http://localhost:8000

### Development Mode

```bash
# Run with hot reload for development
docker-compose --profile dev up --build

# Run in background
docker-compose --profile dev up -d --build
```

Access at: http://localhost:8001

### Docker Commands

```bash
# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild without cache
docker-compose build --no-cache
```

## 📁 Project Structure

```
app/
├── config/                 # Configuration management
│   ├── settings.py        # Pydantic settings
│   └── default.yml        # Default configuration
├── contexts/              # Domain contexts (DDD)
│   ├── customers/         # Customer domain
│   │   ├── application/   # Application services
│   │   ├── domain/        # Domain entities & repositories
│   │   └── infrastructure/ # External concerns
│   └── policy_procurement/ # Policy procurement domain
├── shared/                # Shared infrastructure
│   ├── containers/        # Dependency injection
│   └── infrastructure/    # Cross-cutting concerns
└── main.py               # FastAPI application entry point
```

## 🏗️ Architecture

This project follows **Domain-Driven Design (DDD)** principles with clean architecture:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and application services
- **Infrastructure Layer**: External concerns (database, APIs, etc.)
- **Dependency Injection**: Using `dependency-injector` for IoC

## 🛠️ Development

### Available Commands

```bash
# Install dependencies
uv sync

# Run development server
fastapi dev app/main.py

# Run with uvicorn
uv run uvicorn app.main:app --reload

# Run tests (if available)
uv run pytest

# Code formatting
uv run ruff format .

# Code linting
uv run ruff check .
```

### Code Quality & Pre-commit Hooks

This project includes comprehensive pre-commit hooks for code quality:

```bash
# Setup pre-commit hooks (first time)
make precommit-setup

# Run pre-commit on all files
make precommit-run

# Update pre-commit hooks
make precommit-update

# Clean pre-commit cache
make precommit-clean
```

**Pre-commit hooks include:**

- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanning
- **Commitizen**: Conventional commit message validation
- **Custom hooks**: Test coverage, Docker build validation

For detailed pre-commit documentation, see [PRE_COMMIT.md](./PRE_COMMIT.md).

## 📊 API Health Check

- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe (includes DB check)

## 🗄️ Database

The application uses **SQLite** with **SQLModel** for ORM functionality:

- Database file: `./app.db` (local) or `./data/app.db` (Docker)
- Tables are created automatically on startup (configurable)
- Async SQLAlchemy with aiosqlite driver

## 🔧 Configuration

Configuration is managed through:

- **Pydantic Settings**: Environment variable handling
- **YAML files**: Default configuration values
- **Dependency Injection**: Runtime configuration binding

## 📚 Documentation

- **API Documentation**: Available at `/docs` (Swagger UI)
- **Docker Guide**: See `docs/DOCKER.md` for detailed Docker usage
- **Testing Guide**: See `docs/TESTING.md` for detailed testing usage

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
