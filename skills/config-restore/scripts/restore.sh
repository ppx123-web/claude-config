#!/bin/bash

# Config Restore Script
# Restores Claude Code configuration directories from backup to ~/.claude/
# Usage: restore.sh [source-dir] [directories...]
#   source-dir: Source directory containing backup (default: current directory)
#   directories: Space-separated list of directories to restore (default: commands skills agents)

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
TARGET_DIR="$HOME/.claude"
DEFAULT_SOURCE_DIR="$(pwd)"
DEFAULT_DIRECTORIES=("commands" "skills" "agents")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

confirm() {
    local prompt="$1"
    local response

    while true; do
        echo -ne "${BLUE}❓ $prompt${NC} "
        read -r response
        case "$response" in
            [yY][eE][sS]|[yY])
                return 0
                ;;
            [nN][oO]|[nN])
                return 1
                ;;
            *)
                warning "Please answer yes or no"
                ;;
        esac
    done
}

# Check if target directory exists
if [[ ! -d "$TARGET_DIR" ]]; then
    error "Target directory $TARGET_DIR not found. Claude Code may not be installed."
fi

# Parse arguments
if [[ $# -eq 0 ]]; then
    # No arguments: use current directory and all default directories
    SOURCE_DIR="$DEFAULT_SOURCE_DIR"
    DIRECTORIES=("${DEFAULT_DIRECTORIES[@]}")
elif [[ $# -eq 1 ]]; then
    # One argument: treat as source directory, restore all defaults
    SOURCE_DIR="$1"
    DIRECTORIES=("${DEFAULT_DIRECTORIES[@]}")
else
    # Multiple arguments: first is source, rest are directories
    SOURCE_DIR="$1"
    shift
    DIRECTORIES=("$@")
fi

# Validate source directory
if [[ ! -d "$SOURCE_DIR" ]]; then
    error "Source directory $SOURCE_DIR not found"
fi

# Check for rsync availability
if command -v rsync &> /dev/null; then
    COPY_CMD="rsync"
    info "Using rsync for efficient restore"
else
    COPY_CMD="cp"
    warning "rsync not available, using cp instead"
fi

# Perform restore
info "Restoring from $SOURCE_DIR to $TARGET_DIR"
echo

RESTORE_SUMMARY=()
TOTAL_FILES=0
TOTAL_DIRS=0
SKIPPED=0

for dir in "${DIRECTORIES[@]}"; do
    SOURCE_PATH="$SOURCE_DIR/$dir"
    TARGET_PATH="$TARGET_DIR/$dir"

    # Check if source directory exists
    if [[ ! -d "$SOURCE_PATH" ]]; then
        warning "Skipping $dir/ (not found in source)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Check if target directory exists
    if [[ -d "$TARGET_PATH" ]]; then
        # Count files in target
        TARGET_FILE_COUNT=$(find "$TARGET_PATH" -type f 2>/dev/null | wc -l | tr -d ' ')

        if [[ $TARGET_FILE_COUNT -gt 0 ]]; then
            echo
            warning "Target directory $dir/ already exists with $TARGET_FILE_COUNT files"

            if ! confirm "Overwrite $dir/ in ~/.claude/?"; then
                info "Skipping $dir/"
                SKIPPED=$((SKIPPED + 1))
                continue
            fi
        fi
    else
        # Create target directory
        mkdir -p "$TARGET_PATH" || error "Failed to create $TARGET_PATH"
    fi

    # Perform copy
    info "Restoring $dir/..."

    if [[ "$COPY_CMD" == "rsync" ]]; then
        # Use rsync with archive mode and verbose
        rsync -av "$SOURCE_PATH/" "$TARGET_PATH/" 2>&1 | while IFS= read -r line; do
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

    RESTORE_SUMMARY+=("$dir/ ($FILE_COUNT files, $DIR_COUNT directories)")
    TOTAL_FILES=$((TOTAL_FILES + FILE_COUNT))
    TOTAL_DIRS=$((TOTAL_DIRS + DIR_COUNT))
done

# Display summary
echo
success "Restore complete!"
echo
info "Restored directories:"
for summary in "${RESTORE_SUMMARY[@]}"; do
    info "  - $summary"
done

if [[ $SKIPPED -gt 0 ]]; then
    echo
    warning "Skipped $SKIPPED directories"
fi

echo
info "Total: $TOTAL_FILES files in $TOTAL_DIRS directories"
info "Target: $TARGET_DIR"

exit 0
