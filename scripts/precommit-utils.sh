#!/bin/bash

# Utility functions for pre-commit management
# This script provides helper functions for managing pre-commit hooks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run pre-commit on specific files
run_on_files() {
    local files="$1"
    echo -e "${BLUE}[INFO]${NC} Running pre-commit on specific files: $files"
    pre-commit run --files $files
}

# Function to run pre-commit on all files
run_all() {
    echo -e "${BLUE}[INFO]${NC} Running pre-commit on all files..."
    pre-commit run --all-files
}

# Function to update pre-commit hooks
update_hooks() {
    echo -e "${BLUE}[INFO]${NC} Updating pre-commit hooks..."
    pre-commit autoupdate
    echo -e "${GREEN}[SUCCESS]${NC} Hooks updated!"
}

# Function to clean pre-commit cache
clean_cache() {
    echo -e "${BLUE}[INFO]${NC} Cleaning pre-commit cache..."
    pre-commit clean
    echo -e "${GREEN}[SUCCESS]${NC} Cache cleaned!"
}

# Function to show pre-commit status
show_status() {
    echo -e "${BLUE}[INFO]${NC} Pre-commit status:"
    pre-commit --version
    echo ""
    echo -e "${BLUE}[INFO]${NC} Installed hooks:"
    pre-commit install --install-hooks --overwrite
    echo ""
    echo -e "${BLUE}[INFO]${NC} Available hooks:"
    pre-commit run --help
}

# Function to run specific hook
run_hook() {
    local hook_name="$1"
    if [ -z "$hook_name" ]; then
        echo -e "${RED}[ERROR]${NC} Please specify a hook name"
        echo -e "${BLUE}[INFO]${NC} Available hooks:"
        pre-commit run --help
        return 1
    fi

    echo -e "${BLUE}[INFO]${NC} Running hook: $hook_name"
    pre-commit run $hook_name --all-files
}

# Function to skip hooks for current commit
skip_hooks() {
    echo -e "${YELLOW}[WARNING]${NC} Skipping pre-commit hooks for this commit"
    git commit --no-verify "$@"
}

# Function to run pre-commit in CI mode
run_ci() {
    echo -e "${BLUE}[INFO]${NC} Running pre-commit in CI mode..."
    pre-commit run --all-files --show-diff-on-failure
}

# Function to validate commit message
validate_commit() {
    local commit_msg="$1"
    if [ -z "$commit_msg" ]; then
        echo -e "${RED}[ERROR]${NC} Please provide a commit message"
        return 1
    fi

    echo -e "${BLUE}[INFO]${NC} Validating commit message: $commit_msg"
    echo "$commit_msg" | pre-commit run commitizen --hook-stage commit-msg
}

# Main function to handle commands
main() {
    case "$1" in
        "run")
            if [ -n "$2" ]; then
                run_on_files "$2"
            else
                run_all
            fi
            ;;
        "update")
            update_hooks
            ;;
        "clean")
            clean_cache
            ;;
        "status")
            show_status
            ;;
        "hook")
            run_hook "$2"
            ;;
        "skip")
            shift
            skip_hooks "$@"
            ;;
        "ci")
            run_ci
            ;;
        "validate-commit")
            validate_commit "$2"
            ;;
        *)
            echo -e "${BLUE}Pre-commit Utilities${NC}"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  run [files]     - Run pre-commit on files (or all files)"
            echo "  update          - Update pre-commit hooks"
            echo "  clean           - Clean pre-commit cache"
            echo "  status          - Show pre-commit status"
            echo "  hook <name>     - Run specific hook"
            echo "  skip [args]     - Skip hooks for current commit"
            echo "  ci              - Run in CI mode"
            echo "  validate-commit <msg> - Validate commit message"
            echo ""
            echo "Examples:"
            echo "  $0 run app/main.py"
            echo "  $0 hook ruff"
            echo "  $0 skip -m 'WIP: temporary commit'"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
