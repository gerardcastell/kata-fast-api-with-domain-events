# Docker Setup

This project is fully dockerized and ready for deployment. Here's how to use it:

## Quick Start

### Production Mode

```bash
# Build and run the application
docker-compose up --build

# Run in background
docker-compose up -d --build
```

The application will be available at `http://localhost:8000`

### Development Mode

```bash
# Run with hot reload for development
docker-compose --profile dev up --build

# Run in background
docker-compose --profile dev up -d --build
```

The development server will be available at `http://localhost:8001`

## Environment Variables

Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

Key environment variables:

- `SQLITE_URL`: SQLite Database connection string
- `POSTGRES_URL`: SQLite Database connection string
- `DEBUG`: Enable debug mode (true/false)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ENVIRONMENT`: Environment name (development, production)

## Database

The SQLite database is persisted in the `./data` directory and will be created automatically on first run.

## Health Check

The application includes a health check endpoint at `/health` that Docker uses to monitor the service status.

## Building the Image

```bash
# Build the image
docker build -t events-with-fast-api .

# Run the container
docker run -p 8000:8000 events-with-fast-api
```

## Stopping the Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: This will delete the database)
docker-compose down -v
```

## Debugging

### Development Mode with Logs

```bash
# Run with hot reload for development
docker-compose --profile dev up --build

# View logs in real-time
docker-compose --profile dev logs -f app-dev

# View logs with timestamps
docker-compose --profile dev logs -f -t app-dev
```

### Interactive Debugging

```bash
# Access the running container shell
docker-compose --profile dev exec app-dev /bin/bash

# Or use sh if bash is not available
docker-compose --profile dev exec app-dev /bin/sh
```

### Remote Debugging with debugpy

```bash
# Run the debug service (waits for debugger to attach)
docker-compose --profile debug up --build

# The service will be available at http://localhost:8002
# Debug port is available at localhost:5678
```

To connect with VS Code:

1. Install the Python extension
2. Create a `.vscode/launch.json` file with:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

### Database Debugging

```bash
# Access the database directly
docker-compose --profile dev exec app-dev sqlite3 /app/data/app.db

# Or copy the database file to your local machine
docker cp $(docker-compose --profile dev ps -q app-dev):/app/data/app.db ./debug_app.db
```

## Logs

```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f app

# View logs for dev service
docker-compose --profile dev logs -f app-dev
```
