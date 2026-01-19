#!/bin/bash

# Config Backup Script
# Backs up Claude Code configuration directories from ~/.claude/ to target directory
# Usage: backup.sh [target-dir] [directories...]
#   target-dir: Target directory (default: current directory)
#   directories: Space-separated list of directories to backup (default: commands skills agents)

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
SOURCE_DIR="$HOME/.claude"
DEFAULT_TARGET_DIR="$(pwd)"
DEFAULT_DIRECTORIES=("commands" "skills" "agents")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
error() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

info() {
    echo "$1"
}

# Check if source directory exists
if [[ ! -d "$SOURCE_DIR" ]]; then
    error "Source directory $SOURCE_DIR not found"
fi

# Parse arguments
if [[ $# -eq 0 ]]; then
    # No arguments: use current directory and all default directories
    TARGET_DIR="$DEFAULT_TARGET_DIR"
    DIRECTORIES=("${DEFAULT_DIRECTORIES[@]}")
elif [[ $# -eq 1 ]]; then
    # One argument: treat as target directory, backup all defaults
    TARGET_DIR="$1"
    DIRECTORIES=("${DEFAULT_DIRECTORIES[@]}")
else
    # Multiple arguments: first is target, rest are directories
    TARGET_DIR="$1"
    shift
    DIRECTORIES=("$@")
fi

# Validate and create target directory
if [[ ! -d "$TARGET_DIR" ]]; then
    info "Creating target directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR" || error "Failed to create target directory $TARGET_DIR"
fi

# Check write permissions
if [[ ! -w "$TARGET_DIR" ]]; then
    error "Permission denied writing to $TARGET_DIR"
fi

# Check for rsync availability
if command -v rsync &> /dev/null; then
    COPY_CMD="rsync"
    info "Using rsync for efficient backup"
else
    COPY_CMD="cp"
    warning "rsync not available, using cp instead"
fi

# Perform backup
info "Backing up from $SOURCE_DIR to $TARGET_DIR"
echo

BACKUP_SUMMARY=()
TOTAL_FILES=0
TOTAL_DIRS=0

for dir in "${DIRECTORIES[@]}"; do
    SOURCE_PATH="$SOURCE_DIR/$dir"

    # Check if source directory exists
    if [[ ! -d "$SOURCE_PATH" ]]; then
        warning "Skipping $dir/ (not found in source)"
        continue
    fi

    TARGET_PATH="$TARGET_DIR/$dir"

    # Create target subdirectory if needed
    if [[ ! -d "$TARGET_PATH" ]]; then
        mkdir -p "$TARGET_PATH" || error "Failed to create $TARGET_PATH"
    fi

    # Perform copy
    if [[ "$COPY_CMD" == "rsync" ]]; then
        # Use rsync with archive mode, verbose, and delete orphaned files
        rsync -av --delete "$SOURCE_PATH/" "$TARGET_PATH/" 2>&1 | while IFS= read -r line; do
            if [[ "$line" =~ ^sent\ .*bytes\ .*received\ .*bytes.* ]]; then
                # Skip rsync summary line
                continue
            fi
            if [[ -n "$line" ]]; then
                info "$line"
            fi
        done
    else
        # Fallback to cp
        cp -rf "$SOURCE_PATH/"* "$TARGET_PATH/" 2>&1 | while IFS= read -r line; do
            if [[ -n "$line" ]]; then
                info "$line"
            fi
        done
    fi

    # Count files and directories
    FILE_COUNT=$(find "$TARGET_PATH" -type f 2>/dev/null | wc -l | tr -d ' ')
    DIR_COUNT=$(find "$TARGET_PATH" -type d 2>/dev/null | wc -l | tr -d ' ')

    BACKUP_SUMMARY+=("$dir/ ($FILE_COUNT files, $DIR_COUNT directories)")
    TOTAL_FILES=$((TOTAL_FILES + FILE_COUNT))
    TOTAL_DIRS=$((TOTAL_DIRS + DIR_COUNT))
done

# Display summary
echo
success "Backup complete!"
echo
info "Copied directories:"
for summary in "${BACKUP_SUMMARY[@]}"; do
    info "  - $summary"
done
echo
info "Total: $TOTAL_FILES files in $TOTAL_DIRS directories"
info "Target: $TARGET_DIR"

exit 0
