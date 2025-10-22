#!/bin/bash

# Setup script for pre-commit hooks
# This script installs and configures pre-commit hooks for the project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}[INFO]${NC} Setting up pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}[WARNING]${NC} pre-commit not found. Installing..."

    # Check if we're in a virtual environment or using uv
    if command -v uv &> /dev/null; then
        echo -e "${BLUE}[INFO]${NC} Using uv to install pre-commit..."
        uv add --group dev pre-commit
    elif [ -n "$VIRTUAL_ENV" ]; then
        echo -e "${BLUE}[INFO]${NC} Installing pre-commit in virtual environment..."
        pip install pre-commit
    else
        echo -e "${RED}[ERROR]${NC} No virtual environment detected. Please activate your virtual environment first."
        echo -e "${BLUE}[INFO]${NC} Or install pre-commit globally: pip install pre-commit"
        exit 1
    fi
fi

# Install pre-commit hooks
echo -e "${BLUE}[INFO]${NC} Installing pre-commit hooks..."
pre-commit install

# Install commit-msg hook for commitizen
echo -e "${BLUE}[INFO]${NC} Installing commit-msg hook..."
pre-commit install --hook-type commit-msg

# Install pre-push hooks
echo -e "${BLUE}[INFO]${NC} Installing pre-push hooks..."
pre-commit install --hook-type pre-push

# Update hooks to latest versions
echo -e "${BLUE}[INFO]${NC} Updating hooks to latest versions..."
pre-commit autoupdate

# Run pre-commit on all files to test
echo -e "${BLUE}[INFO]${NC} Running pre-commit on all files (this may take a while)..."
if pre-commit run --all-files; then
    echo -e "${GREEN}[SUCCESS]${NC} Pre-commit setup completed successfully!"
    echo -e "${BLUE}[INFO]${NC} All hooks are now active and will run on commits."
else
    echo -e "${YELLOW}[WARNING]${NC} Some hooks failed. Please fix the issues and try again."
    echo -e "${BLUE}[INFO]${NC} You can run 'pre-commit run --all-files' to see detailed output."
fi

echo -e "${BLUE}[INFO]${NC} Pre-commit hooks are now configured!"
echo -e "${BLUE}[INFO]${NC} Hooks will run automatically on:"
echo -e "  - ${GREEN}git commit${NC} (pre-commit hooks)"
echo -e "  - ${GREEN}git push${NC} (pre-push hooks)"
echo -e "  - ${GREEN}commit messages${NC} (commit-msg hooks)"
