# Config Restore - Troubleshooting Guide

This guide helps you troubleshoot common issues when restoring Claude Code configurations.

## Table of Contents

1. [Source Directory Issues](#source-directory-issues)
2. [Target Directory Issues](#target-directory-issues)
3. [Permission Issues](#permission-issues)
4. [Conflict Handling](#conflict-handling)
5. [Partial Restores](#partial-restores)
6. [Tool Availability](#tool-availability)
7. [Verification After Restore](#verification-after-restore)

---

## Source Directory Issues

### Problem: "Source directory not found"

**Error Message**:
```
❌ Error: Source directory /path/to/source not found
```

**Causes**:
- Specified directory doesn't exist
- Typo in directory path
- Backup is in a different location

**Solutions**:

1. **Verify backup location**:
   ```bash
   ls -la ~/backups/claude-config
   ls -la /path/to/backup
   ```

2. **Use current directory if unsure**:
   ```bash
   # Navigate to backup directory first
   cd /path/to/backup
   # Then run restore without arguments
   ```

3. **Check if backup was created**:
   ```bash
   # Look for backup directories
   find ~ -type d -name "*claude*backup*" 2>/dev/null
   ```

---

## Target Directory Issues

### Problem: "Target directory ~/.claude not found"

**Error Message**:
```
❌ Error: Target directory ~/.claude not found. Claude Code may not be installed.
```

**Causes**:
- Claude Code is not installed
- `~/.claude/` was deleted
- Running in wrong user context

**Solutions**:

1. **Verify Claude Code installation**:
   ```bash
   which cc
   ls -la ~/.claude/
   ```

2. **Install Claude Code** if not installed:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

3. **Check if running as correct user**:
   ```bash
   whoami
   echo $HOME
   ```

**Important**: The restore script will **not** create `~/.claude/` automatically. This is intentional to prevent accidental creation in wrong locations.

---

## Permission Issues

### Problem: "Permission denied" when copying

**Error Messages**:
```
❌ Error: Failed to create /path/to/directory
cp: cannot create regular file '/path/to/file': Permission denied
```

**Causes**:
- Target directory not writable
- Source directory not readable
- File ownership issues

**Solutions**:

1. **Check source permissions**:
   ```bash
   ls -la /path/to/backup
   ```

2. **Check target permissions**:
   ```bash
   ls -la ~/.claude/
   ```

3. **Fix permissions if needed**:
   ```bash
   # Make source readable
   chmod -R +r /path/to/backup

   # Make target writable (use with caution)
   chmod -R u+w ~/.claude/
   ```

4. **Check ownership**:
   ```bash
   ls -la ~/.claude/
   # Should show your username as owner
   ```

---

## Conflict Handling

### Problem: Worried about overwriting important files

**Scenario**: You're prompted to overwrite existing files but aren't sure.

**Solutions**:

1. **Backup current state first**:
   ```bash
   # Use config-backup skill to save current state
   ~/.claude/skills/config-backup/scripts/backup.sh ~/tmp/pre-restore-backup
   ```

2. **Compare directories before restoring**:
   ```bash
   # Compare commands
   diff -r ~/.claude/commands /path/to/backup/commands

   # Compare skills
   diff -r ~/.claude/skills /path/to/backup/skills
   ```

3. **Decline overwrite** when prompted:
   ```
   ❓ Overwrite commands/ in ~/.claude/?
   Answer: no  # This skips that directory
   ```

4. **Selective restore**: Only restore directories you're confident about:
   ```
   "Just restore skills/, I'll keep my current commands"
   ```

---

## Partial Restores

### Problem: Some directories not restored

**Scenario**: Summary shows fewer directories than expected.

**Possible Causes**:

1. **Directory not in source**:
   ```
   ⚠️ Skipping agents/ (not found in source)
   ```

2. **User declined overwrite**:
   ```
   ❓ Overwrite commands/ in ~/.claude/?
   Answer: no
   Skipping commands/
   ```

3. **Directory not specified** in selective restore

**Solutions**:

1. **Verify source contents**:
   ```bash
   ls -la /path/to/backup/
   ```

2. **Check which directories exist**:
   ```bash
   find /path/to/backup -maxdepth 1 -type d
   ```

3. **Restore missing directories only**:
   ```bash
   ~/.claude/skills/config-restore/scripts/restore.sh /path/to/backup agents
   ```

---

## Tool Availability

### Problem: rsync not available

**Warning Message**:
```
⚠️ rsync not available, using cp instead
```

**Impact**: Restore still works, just less efficient for large backups.

**Solutions**:

1. **Install rsync** (recommended):
   ```bash
   # macOS
   brew install rsync

   # Linux (Ubuntu/Debian)
   sudo apt-get install rsync

   # Linux (CentOS/RHEL)
   sudo yum install rsync
   ```

2. **Or continue with cp**: The script automatically falls back to `cp -rf`, which works fine for most cases.

---

## Verification After Restore

### Problem: How to verify restore succeeded?

**Solutions**:

1. **Check directory contents**:
   ```bash
   ls -la ~/.claude/commands/
   ls -la ~/.claude/skills/
   ls -la ~/.claude/agents/
   ```

2. **Count files**:
   ```bash
   find ~/.claude/commands -type f | wc -l
   find ~/.claude/skills -type f | wc -l
   find ~/.claude/agents -type f | wc -l
   ```

3. **Test commands**: Try using a custom command
   ```
   /your-custom-command
   ```

4. **Test skills**: Ask Claude something that triggers your skill
   ```
   "Help me with [task that uses your skill]"
   ```

5. **List available commands**:
   ```
   /help
   ```

6. **Compare with backup**:
   ```bash
   # Should show no differences if restore successful
   diff -r /path/to/backup/commands ~/.claude/commands
   ```

---

## Common Error Scenarios

### Scenario 1: Restore to Wrong Location

**Symptom**: Restored files not appearing in Claude Code

**Cause**: Specified wrong target or running in wrong environment

**Solution**:
```bash
# Verify target directory
echo $HOME/.claude

# Should match what restore script reported
# Target: /Users/username/.claude
```

### Scenario 2: Backup Incomplete

**Symptom**: Some files missing after restore

**Cause**: Original backup was incomplete

**Solution**:
```bash
# Check backup completeness
find /path/to/backup -type f | wc -l
find ~/.claude -type f | wc -l

# Numbers should be similar for full backup
```

### Scenario 3: Mixed Results

**Symptom**: Some directories restored, others skipped

**Cause**: User declined some overwrite prompts

**Solution**:
```bash
# Re-run restore for skipped directories only
~/.claude/skills/config-restore/scripts/restore.sh /path/to/backup commands
```

---

## Getting Help

If you encounter issues not covered here:

1. **Check the main skill documentation**: `../SKILL.md`
2. **Review example workflows**: `../examples/restore-workflows.md`
3. **Inspect the script**: `../scripts/restore.sh`
4. **Check Claude Code documentation**: https://docs.anthropic.com/claude-code

---

## Best Practices to Avoid Issues

1. **Always backup first** before restoring to a different location
2. **Verify source directory** before starting restore
3. **Read prompts carefully** before confirming overwrites
4. **Test after restore** to verify everything works
5. **Keep multiple backups** in different locations
6. **Document your backup locations** for easy reference

---

## Quick Reference

### Common Commands

```bash
# Restore all from current directory
~/.claude/skills/config-restore/scripts/restore.sh

# Restore all from specific location
~/.claude/skills/config-restore/scripts/restore.sh /path/to/backup

# Restore specific directories
~/.claude/skills/config-restore/scripts/restore.sh /path/to/backup commands skills

# Check what would be restored (dry run)
ls -la /path/to/backup/
```

### Verification Commands

```bash
# Check restored files
ls -la ~/.claude/commands/
ls -la ~/.claude/skills/
ls -la ~/.claude/agents/

# Count restored files
find ~/.claude/commands -type f | wc -l
find ~/.claude/skills -type f | wc -l
find ~/.claude/agents -type f | wc -l
```
