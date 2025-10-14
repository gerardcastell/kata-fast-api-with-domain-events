#!/bin/bash

# Docker Debug Helper Script for FastAPI Events App
# Usage: ./debug.sh [command]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    echo "Docker Debug Helper for FastAPI Events App"
    echo ""
    echo "Usage: ./debug.sh [command]"
    echo ""
    echo "Commands:"
    echo "  dev         Start development environment with hot reload"
    echo "  debug       Start debug environment (waits for debugger)"
    echo "  logs        Show logs for dev service"
    echo "  shell       Access container shell"
    echo "  db          Access database shell"
    echo "  status      Show container status"
    echo "  stop        Stop all services"
    echo "  clean       Stop and remove all containers/volumes"
    echo "  build       Rebuild containers"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./debug.sh dev      # Start dev environment"
    echo "  ./debug.sh logs     # View logs"
    echo "  ./debug.sh shell    # Access container"
}

# Function to start development environment
start_dev() {
    print_status "Starting development environment..."
    docker-compose --profile dev up --build -d
    print_success "Development environment started!"
    print_status "Application available at: http://localhost:8001"
    print_status "View logs with: ./debug.sh logs"
}

# Function to start debug environment
start_debug() {
    print_status "Starting debug environment..."
    print_warning "This will wait for a debugger to attach on port 5678"
    docker-compose --profile debug up --build
}

# Function to show logs
show_logs() {
    print_status "Showing logs for development service..."
    docker-compose --profile dev logs -f app-dev
}

# Function to access container shell
access_shell() {
    print_status "Accessing container shell..."
    docker-compose --profile dev exec app-dev /bin/bash
}

# Function to access database
access_db() {
    print_status "Accessing database shell..."
    docker-compose --profile dev exec app-dev sqlite3 /app/data/app.db
}

# Function to show status
show_status() {
    print_status "Container status:"
    docker-compose --profile dev ps
}

# Function to stop services
stop_services() {
    print_status "Stopping all services..."
    docker-compose --profile dev down
    docker-compose --profile debug down
    print_success "All services stopped!"
}

# Function to clean up
clean_up() {
    print_warning "This will remove all containers and volumes (including database data)"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        docker-compose --profile dev down -v
        docker-compose --profile debug down -v
        docker system prune -f
        print_success "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to rebuild containers
rebuild_containers() {
    print_status "Rebuilding containers..."
    docker-compose --profile dev build --no-cache
    docker-compose --profile debug build --no-cache
    print_success "Containers rebuilt!"
}

# Main script logic
case "${1:-help}" in
    "dev")
        start_dev
        ;;
    "debug")
        start_debug
        ;;
    "logs")
        show_logs
        ;;
    "shell")
        access_shell
        ;;
    "db")
        access_db
        ;;
    "status")
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "clean")
        clean_up
        ;;
    "build")
        rebuild_containers
        ;;
    "help"|*)
        show_help
        ;;
esac
