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

- `SQLITE_URL`: Database connection string
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

## Logs

```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f app
```
