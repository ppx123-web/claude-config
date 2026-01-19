# Config Restore Workflows - Examples

This document provides detailed examples of common restore workflows using the config-restore skill.

## Table of Contents

1. [Basic Restore - All Directories](#example-1-basic-restore-all-directories)
2. [Selective Restore - Specific Directories](#example-2-selective-restore-specific-directories)
3. [Custom Source Directory](#example-3-custom-source-directory)
4. [Handling Conflicts - User Declines](#example-4-handling-conflicts-user-declines)
5. [Restore from Different Machine](#example-5-restore-from-different-machine)
6. [Recovery from Accidental Deletion](#example-6-recovery-from-accidental-deletion)

---

## Example 1: Basic Restore - All Directories

**User Request**: "restore my claude config"

**Complete Workflow**:

```
Assistant: I'll restore your Claude configurations from backup.

Source directory: /Users/choi/work/claude-config
Is this correct, or would you like to specify a different location?

Which directories would you like to restore?
- commands/
- skills/
- agents/

Restore all three, or specify which ones?

User: Yes, restore all three.

Assistant: [Checking for conflicts...]

⚠️ Target directory commands/ already exists with 12 files
❓ Overwrite commands/ in ~/.claude/?
User: yes

[Restoring commands/...]

⚠️ Target directory skills/ already exists with 8 files
❓ Overwrite skills/ in ~/.claude/?
User: yes

[Restoring skills/...]

⚠️ Target directory agents/ already exists with 5 files
❓ Overwrite agents/ in ~/.claude/?
User: yes

[Restoring agents/...]

✅ Restore complete!

Restored directories:
  - commands/ (12 files, 0 directories)
  - skills/ (45 files, 8 directories)
  - agents/ (5 files, 0 directories)

Total: 62 files in 8 directories
Target: /Users/choi/.claude
```

**Key Points**:
- Confirmed source directory (default: current working directory)
- Restored all three directories
- Asked for confirmation for each conflict
- Provided detailed summary

---

## Example 2: Selective Restore - Specific Directories

**User Request**: "only restore my commands and skills, not agents"

**Complete Workflow**:

```
Assistant: I'll restore your Claude configurations from backup.

Source directory: /Users/choi/work/claude-config
Is this correct, or would you like to specify a different location?

Which directories would you like to restore?
- commands/
- skills/
- agents/

User: Just commands and skills, skip agents.

Assistant: [Checking for conflicts...]

⚠️ Target directory commands/ already exists with 12 files
❓ Overwrite commands/ in ~/.claude/?
User: yes

[Restoring commands/...]

⚠️ Target directory skills/ already exists with 8 files
❓ Overwrite skills/ in ~/.claude/?
User: yes

[Restoring skills/...]

✅ Restore complete!

Restored directories:
  - commands/ (12 files, 0 directories)
  - skills/ (45 files, 8 directories)

Total: 57 files in 8 directories
Target: /Users/choi/.claude
```

**Key Points**:
- User specified selective restore (commands + skills only)
- Skipped agents/ entirely
- Still asked for confirmation on conflicts

---

## Example 3: Custom Source Directory

**User Request**: "restore from ~/backups/claude-config-old"

**Complete Workflow**:

```
Assistant: I'll restore your Claude configurations from backup.

Source directory: ~/backups/claude-config-old
Is this correct, or would you like to specify a different location?

User: Yes, that's correct.

Which directories would you like to restore?
- commands/
- skills/
- agents/

Restore all three, or specify which ones?

User: All three.

Assistant: [Checking for conflicts...]

[Restoring commands/...]
[Restoring skills/...]
[Restoring agents/...]

✅ Restore complete!

Restored directories:
  - commands/ (10 files, 0 directories)
  - skills/ (32 files, 6 directories)
  - agents/ (3 files, 0 directories)

Total: 45 files in 6 directories
Target: /Users/choi/.claude
```

**Key Points**:
- User specified custom source directory
- Confirmed location before proceeding
- Restored all directories from that location

---

## Example 4: Handling Conflicts - User Declines

**User Request**: "restore from backup"

**Complete Workflow**:

```
Assistant: I'll restore your Claude configurations from backup.

Source directory: /Users/choi/work/claude-config
Is this correct, or would you like to specify a different location?

Which directories would you like to restore?
- commands/
- skills/
- agents/

Restore all three, or specify which ones?

User: All three.

Assistant: [Checking for conflicts...]

⚠️ Target directory commands/ already exists with 12 files
❓ Overwrite commands/ in ~/.claude/?
User: no

Skipping commands/

⚠️ Target directory skills/ already exists with 8 files
❓ Overwrite skills/ in ~/.claude/?
User: yes

[Restoring skills/...]

⚠️ Target directory agents/ already exists with 5 files
❓ Overwrite agents/ in ~/.claude/?
User: yes

[Restoring agents/...]

✅ Restore complete!

Restored directories:
  - skills/ (45 files, 8 directories)
  - agents/ (5 files, 0 directories)

Skipped: 1 directories

Total: 50 files in 8 directories
Target: /Users/choi/.claude
```

**Key Points**:
- User declined overwriting commands/
- Script respected choice and skipped that directory
- Continued with other directories
- Summary shows skipped count

---

## Example 5: Restore from Different Machine

**User Request**: "copy config from /Volumes/USB/claude-backup to my ~/.claude"

**Complete Workflow**:

```
Assistant: I'll restore your Claude configurations from backup.

Source directory: /Volumes/USB/claude-backup
Is this correct, or would you like to specify a different location?

User: Yes, that's my USB backup.

Which directories would you like to restore?
- commands/
- skills/
- agents/

Restore all three, or specify which ones?

User: All three.

Assistant: [Checking for conflicts...]

[Restoring commands/...]
[Restoring skills/...]
[Restoring agents/...]

✅ Restore complete!

Restored directories:
  - commands/ (18 files, 0 directories)
  - skills/ (52 files, 10 directories)
  - agents/ (8 files, 0 directories)

Total: 78 files in 10 directories
Target: /Users/choi/.claude
```

**Key Points**:
- User restoring from external drive
- Different machine or clean setup
- All directories restored successfully

---

## Example 6: Recovery from Accidental Deletion

**User Request**: "I accidentally deleted my custom commands, can I restore from yesterday's backup?"

**Complete Workflow**:

```
Assistant: I'll restore your Claude configurations from backup.

Source directory: /Users/choi/work/claude-config
Is this correct, or would you like to specify a different location?

User: Yes, that's where I backed up yesterday.

Which directories would you like to restore?
- commands/
- skills/
- agents/

Restore all three, or specify which ones?

User: Just commands, I only deleted those.

Assistant: [Checking for conflicts...]

[Restoring commands/...]

✅ Restore complete!

Restored directories:
  - commands/ (12 files, 0 directories)

Total: 12 files in 0 directories
Target: /Users/choi/.claude

Your commands have been restored from backup!
```

**Key Points**:
- Targeted restore of only affected directory
- Quick recovery from accidental deletion
- Clear confirmation of success

---

## Common Patterns

### Pattern 1: Full Restore After System Reinstall

```
User: "I just reinstalled my system, restore all my claude configs from the backup folder"
[Restores all three directories from backup]
```

### Pattern 2: Testing Changes with Rollback

```
User: "Restore my old skills to test something"
[Restores only skills/ directory]
```

### Pattern 3: Sync Multiple Machines

```
User: "Copy config from my work backup to home machine"
[Restores all directories from specified backup location]
```

---

## Tips for Users

1. **Know your backup location**: Always remember where you stored your backups
2. **Selective restore**: You can restore just what you need (commands, skills, or agents)
3. **Conflict handling**: You'll always be asked before overwriting existing files
4. **Check summary**: Review the summary to confirm what was restored
5. **Test after restore**: Verify your custom commands/skills work as expected

---

## Related Documentation

- Main skill documentation: `../SKILL.md`
- Troubleshooting guide: `../references/troubleshooting.md`
- Config backup skill (for creating backups): `~/.claude/skills/config-backup/`
