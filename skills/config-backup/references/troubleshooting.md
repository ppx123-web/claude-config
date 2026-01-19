# Troubleshooting Config Backup

This document covers common issues and solutions when backing up Claude Code configurations.

## Problem: Backup Fails with "Permission Denied"

**Symptoms:**
- Error message: "Permission denied writing to [target-dir]"
- Script exits without completing backup

**Causes:**
1. Target directory is not writable by current user
2. Target directory is owned by another user
3. File system permissions are too restrictive

**Solutions:**

### Option 1: Choose a Different Target Directory
Select a location where you have write permissions:
```bash
~/.claude/skills/config-backup/scripts/backup.sh ~/Documents/claude-backup
```

### Option 2: Fix Permissions (if you own the directory)
Change ownership or permissions:
```bash
# Take ownership of directory
sudo chown -R $USER:$USER /path/to/target

# Or make it writable
chmod u+w /path/to/target
```

### Option 3: Use Current Working Directory
The script defaults to current directory, which you likely own:
```bash
cd ~
~/.claude/skills/config-backup/scripts/backup.sh
```

## Problem: Some Files Not Copied

**Symptoms:**
- Backup completes but shows fewer files than expected
- Specific directories or files missing from target

**Causes:**
1. Source files are symlinks pointing outside ~/.claude/
2. Source files have special permissions (e.g., 000)
3. rsync encountered errors during transfer
4. Files were filtered out by rsync rules

**Solutions:**

### Check Source Files Exist
```bash
# Verify source files exist
ls -la ~/.claude/commands/
ls -la ~/.claude/skills/
ls -la ~/.claude/agents/
```

### Check for Symlinks
```bash
# Find symlinks in source
find ~/.claude -type l

# If symlinks exist, decide: copy link target or skip?
# rsync -a copies link targets by default
# rsync -al copies symlinks as links (not targets)
```

### Re-run with Verbose Output
The backup script already uses verbose mode. Check output for skipped files:
```bash
~/.claude/skills/config-backup/scripts/backup.sh /tmp/backup-test 2>&1 | grep -i "skipped\|error\|failed"
```

### Manual Verification
Compare source and target:
```bash
# Count files in source
find ~/.claude/commands -type f | wc -l

# Count files in target
find /tmp/backup-test/commands -type f | wc -l
```

## Problem: Target Directory is Messy with Old Backups

**Symptoms:**
- Target directory contains old files from previous backups
- Orphaned files not present in source anymore
- Confusion about which files are current

**Solutions:**

### Solution 1: Let rsync Clean Up (Default)
The script uses `rsync --delete` which removes orphaned files:
```bash
~/.claude/skills/config-backup/scripts/backup.sh /tmp/backup
# rsync will delete files in /tmp/backup that aren't in ~/.claude/
```

### Solution 2: Manual Clean Before Backup
Remove entire target directory before backup:
```bash
rm -rf /tmp/backup
~/.claude/skills/config-backup/scripts/backup.sh /tmp/backup
```

### Solution 3: Timestamped Backups
Keep multiple backup versions with timestamps:
```bash
~/.claude/skills/config-backup/scripts/backup.sh ~/backups/claude-$(date +%Y%m%d-%H%M%S)
```

## Problem: rsync Not Available, cp is Slow

**Symptoms:**
- Warning message: "rsync not available, using cp instead"
- Backup takes longer than expected
- No progress indication during copy

**Solutions:**

### Solution 1: Install rsync (Recommended)
```bash
# macOS (should already have rsync)
brew install rsync

# Linux
sudo apt-get install rsync  # Debian/Ubuntu
sudo yum install rsync      # RHEL/CentOS
```

### Solution 2: Add Progress Indicator to cp
Modify the script to show progress:
```bash
# Before cp command
echo "Copying $dir/..."

# Run cp
cp -rf "$SOURCE_PATH/"* "$TARGET_PATH/"

# After cp command
echo "Finished copying $dir/"
```

### Solution 3: Use pv (Pipe Viewer) for Progress
```bash
# Install pv
brew install pv  # macOS
sudo apt-get install pv  # Linux

# Use pv with tar for progress
tar cf - "$SOURCE_PATH" | pv | tar xf - -C "$TARGET_PATH"
```

## Problem: Backup Completes But Files Aren't There

**Symptoms:**
- Script reports success
- Target directory exists but is empty
- No error messages

**Causes:**
1. Copied to wrong target directory (user error)
2. Source directory was empty
3. Filesystem issues (disk full, mount problems)

**Solutions:**

### Verify Target Location
```bash
# Check actual target used by script
~/.claude/skills/config-backup/scripts/backup.sh /tmp/test-backup
ls -la /tmp/test-backup/commands/
```

### Check Disk Space
```bash
# macOS
df -h

# Linux
df -h
```

### Verify Source Has Files
```bash
# Count files in source
find ~/.claude/commands -type f | wc -l
find ~/.claude/skills -type f | wc -l
find ~/.claude/agents -type f | wc -l
```

## Problem: Script Hangs or Freezes

**Symptoms:**
- Script doesn't complete
- No output for long time
- Needs Ctrl+C to abort

**Causes:**
1. Large file transfer over slow filesystem (network drive)
2. Permission issue waiting for input
3. Filesystem corruption

**Solutions:**

### Run with Verbose Debugging
Add debug output to script:
```bash
# At top of script
set -x  # Enable debug mode

# Run backup
~/.claude/skills/config-backup/scripts/backup.sh /tmp/backup
```

### Check Filesystem Health
```bash
# macOS
diskutil verifyVolume /

# Linux
sudo fsck /dev/sda1  # Run on unmounted filesystem
```

### Avoid Network Filesystems
Don't backup directly to network drives (NFS, SMB). Backup locally first, then copy:
```bash
~/.claude/skills/config-backup/scripts/backup.sh /tmp/backup
rsync -av /tmp/backup/ /network/drive/claude-backup/
```

## Getting Help

If you encounter issues not covered here:

1. **Check the script**: `~/.claude/skills/config-backup/scripts/backup.sh`
2. **Review the main skill documentation**: `SKILL.md`
3. **Check rsync/cp documentation**:
   ```bash
   man rsync
   man cp
   ```
4. **Enable debug mode** in the script to see detailed execution
5. **Verify your environment**: macOS vs Linux, permissions, disk space

## Common Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `Source directory ~/.claude/ not found` | ~/.claude/ doesn't exist | Check if Claude Code is installed |
| `Permission denied writing to [target]` | No write permission | Choose different target or fix permissions |
| `rsync not available, using cp instead` | rsync not installed | Install rsync or accept cp fallback |
| `Failed to create target directory` | Can't create target dir | Check parent directory permissions |
| `Skipping [dir]/ (not found in source)` | Source subdirectory missing | Normal - skips missing dirs |

## Advanced Troubleshooting

### Enable Bash Debug Mode
Add `set -x` at the top of the script to see every command executed.

### Dry Run with rsync
Test what rsync would do without actually copying:
```bash
rsync -av --dry-run --delete ~/.claude/commands/ /tmp/test/
```

### Compare Source and Target
Find differences between source and target:
```bash
diff -qr ~/.claude/commands/ /tmp/backup/commands/
```

### Check File Integrity
Verify files copied correctly (compare checksums):
```bash
# Generate checksums
find ~/.claude/commands -type f -exec md5 {} \; > source.md5
find /tmp/backup/commands -type f -exec md5 {} \; > target.md5

# Compare
diff source.md5 target.md5
```
