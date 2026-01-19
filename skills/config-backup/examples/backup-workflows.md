# Config Backup Workflow Examples

This document provides detailed examples of common backup workflows using the config-backup skill.

## Example 1: Basic Backup to Current Directory

**Scenario**: User wants to backup all Claude configs to current working directory.

**Trigger**: "save my claude settings"

**Expected Workflow**:

```
Assistant: "I'll backup your Claude configurations.

Target directory: /Users/choi/work/claude-config
Is this correct, or would you like to specify a different location?"

User: "Yes, that's correct."

Assistant: "Which directories would you like to backup?
- commands/
- skills/
- agents/

Backup all three, or specify which ones to include?"

User: "All three."

Assistant: [Executes backup script]
"Creating target directory: /Users/choi/work/claude-config
Using rsync for efficient backup
Backing up from /Users/choi/.claude to /Users/choi/work/claude-config

[rsync output...]

✅ Backup complete!

Copied directories:
  - commands/ (15 files, 1 directories)
  - skills/ (8 directories, 42 files)
  - agents/ (23 files)

Total: 80 files in 51 directories
Target: /Users/choi/work/claude-config"
```

**Command Used**:
```bash
~/.claude/skills/config-backup/scripts/backup.sh /Users/choi/work/claude-config
```

## Example 2: Selective Backup (Commands and Skills Only)

**Scenario**: User only wants to backup commands and skills, excluding agents.

**Trigger**: "backup my commands and skills"

**Expected Workflow**:

```
Assistant: "I'll backup your Claude configurations.

Target directory: /Users/choi/work/project
Is this correct, or would you like to specify a different location?"

User: "Yes."

Assistant: "Which directories would you like to backup?
- commands/
- skills/
- agents/

Backup all three, or specify which ones to include?"

User: "Just commands and skills."

Assistant: [Executes backup script with selective directories]
"Creating target directory: /Users/choi/work/project
Using rsync for efficient backup
Backing up from /Users/choi/.claude to /Users/choi/work/project

✅ Backup complete!

Copied directories:
  - commands/ (15 files, 1 directories)
  - skills/ (8 directories, 42 files)

Total: 57 files in 51 directories
Target: /Users/choi/work/project"
```

**Command Used**:
```bash
~/.claude/skills/config-backup/scripts/backup.sh /Users/choi/work/project commands skills
```

## Example 3: Backup to Custom Location

**Scenario**: User wants to backup to a specific external directory.

**Trigger**: "copy ~/.claude to ~/backups/claude-config"

**Expected Workflow**:

```
Assistant: "I'll backup your Claude configurations.

Target directory: /Users/choi/work/claude-config
Is this correct, or would you like to specify a different location?"

User: "No, use ~/backups/claude-config instead."

Assistant: "Got it. Which directories would you like to backup?
- commands/
- skills/
- agents/

Backup all three, or specify which ones to include?"

User: "All three."

Assistant: [Executes backup to custom location]
"Creating target directory: /Users/choi/backups/claude-config
Using rsync for efficient backup
Backing up from /Users/choi/.claude to /Users/choi/backups/claude-config

✅ Backup complete!

Copied directories:
  - commands/ (15 files, 1 directories)
  - skills/ (8 directories, 42 files)
  - agents/ (23 files)

Total: 80 files in 51 directories
Target: /Users/choi/backups/claude-config"
```

**Command Used**:
```bash
~/.claude/skills/config-backup/scripts/backup.sh ~/backups/claude-config
```

## Example 4: Backup Before Major Changes

**Scenario**: User is about to make significant changes and wants a safety backup.

**Trigger**: "archive claude settings before making changes"

**Expected Workflow**:

```
Assistant: "I'll backup your Claude configurations.

Target directory: /Users/choi/work/claude-config
Is this correct, or would you like to specify a different location?"

User: "Actually, let's use a timestamped backup."

Assistant: "Good idea. I'll create a timestamped backup in ~/backups/.

[Executes: backup.sh ~/backups/claude-$(date +%Y%m%d-%H%M%S)]

Creating target directory: /Users/choi/backups/claude-20250119-144530
Using rsync for efficient backup
Backing up from /Users/choi/.claude to /Users/choi/backups/claude-20250119-144530

✅ Backup complete!

Copied directories:
  - commands/ (15 files, 1 directories)
  - skills/ (8 directories, 42 files)
  - agents/ (23 files)

Total: 80 files in 51 directories
Target: /Users/choi/backups/claude-20250119-144530

Your configs are now safely backed up. Proceed with your changes!"
```

**Command Used**:
```bash
~/.claude/skills/config-backup/scripts/backup.sh ~/backups/claude-$(date +%Y%m%d-%H%M%S)
```

## Example 5: Backup for Version Control

**Scenario**: User wants to add Claude configs to git repository.

**Trigger**: "version control my claude config"

**Expected Workflow**:

```
Assistant: "I'll backup your Claude configurations to version control.

Target directory: /Users/choi/work/claude-config
Is this correct, or would you like to specify a different location?"

User: "Yes, this is my git repo."

Assistant: "Which directories would you like to backup?
- commands/
- skills/
- agents/

Backup all three, or specify which ones to include?"

User: "All three."

Assistant: [Executes backup]

✅ Backup complete!

Copied directories:
  - commands/ (15 files, 1 directories)
  - skills/ (8 directories, 42 files)
  - agents/ (23 files)

Total: 80 files in 51 directories
Target: /Users/choi/work/claude-config

Would you like me to create a .gitignore file to exclude sensitive settings?"

User: "Yes."

Assistant: [Creates .gitignore]
"Created .gitignore excluding:
- .local.md files (local settings)
- settings.local.json (personal config)
- Other sensitive local files

You can now commit with:
git add .
git commit -m 'Add Claude Code configurations'
"
```

**Commands Used**:
```bash
# Backup
~/.claude/skills/config-backup/scripts/backup.sh .

# Create .gitignore
cat > .gitignore << 'EOF'
# Exclude local settings
*.local.md
**/.local.md
.claude/settings.local.json

# Exclude sensitive data
**/secrets/
**/credentials/
**/.env
EOF

# Commit
git add .
git commit -m 'Add Claude Code configurations'
```

## Example 6: Backup for Sharing with Team

**Scenario**: User wants to share useful commands and skills with team members.

**Trigger**: "export my commands and skills to share with team"

**Expected Workflow**:

```
Assistant: "I'll backup your Claude configurations for sharing.

Target directory: /Users/choi/work/claude-config
Is this correct, or would you like to specify a different location?"

User: "Yes."

Assistant: "Which directories would you like to backup?
- commands/
- skills/
- agents/

Backup all three, or specify which ones to include?"

User: "Just commands and skills - I don't want to share my custom agents."

Assistant: [Executes backup with commands and skills only]

✅ Backup complete!

Copied directories:
  - commands/ (15 files, 1 directories)
  - skills/ (8 directories, 42 files)

Total: 57 files in 51 directories
Target: /Users/choi/work/claude-config

Consider creating a README to explain your setup:
- What each command does
- How skills work together
- Any dependencies or setup required

Would you like me to create a README template?"
```

## Example 7: Migration to New Machine

**Scenario**: User is setting up a new machine and wants to transfer configurations.

**Trigger**: "I need to copy my claude config to my new laptop"

**Expected Workflow**:

```
User: "I need to copy my claude config to my new laptop."

Assistant: "Here's the migration process:

**Step 1**: Backup from current machine

[Executes backup to external drive or cloud storage]
~/.claude/skills/config-backup/scripts/backup.sh /Volumes/USB/claude-config-backup

✅ Backup complete!

**Step 2**: Transfer to new machine

Copy the backup directory to your new machine using:
- USB drive
- Cloud storage (Google Drive, Dropbox, etc.)
- Network transfer (scp, rsync over ssh)

**Step 3**: Restore on new machine

On your new machine, copy the files:
cp -r /path/to/backup/commands/* ~/.claude/commands/
cp -r /path/to/backup/skills/* ~/.claude/skills/
cp -r /path/to/backup/agents/* ~/.claude/agents/

**Step 4**: Verify

Check that everything works:
- List commands in Claude Code
- Trigger skills to ensure they load
- Test custom agents

Your new machine is now configured identically to your old one!"
```

## Example 8: Automated Scheduled Backups

**Scenario**: User wants to set up automated regular backups.

**Trigger**: "set up automatic backups of my claude config"

**Expected Workflow**:

```
Assistant: "I'll help you set up automated backups.

**Option 1: Launchd (macOS)**

Create ~/Library/LaunchAgents/com.user.claude-backup.plist:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.claude-backup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>-c</key>
        <string>~/.claude/skills/config-backup/scripts/backup.sh ~/backups/claude-$(date +\%Y\%m\%d)</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>0</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

Load with: launchctl load ~/Library/LaunchAgents/com.user.claude-backup.plist

**Option 2: Cron (Linux/macOS)**

Add to crontab (crontab -e):
```
0 0 * * * ~/.claude/skills/config-backup/scripts/backup.sh ~/backups/claude-$(date +\%Y\%m\%d)
```

Backups will run daily at midnight with timestamps.

Would you like me to create the automation file for you?"
```

## Example 9: Backup Specific Skill Only

**Scenario**: User wants to backup just one specific skill.

**Trigger**: "backup my code-reviewer skill"

**Expected Workflow**:

```
User: "backup my code-reviewer skill"

Assistant: "I'll backup the code-reviewer skill.

Target directory: /Users/choi/work/claude-config
Is this correct, or would you like to specify a different location?"

User: "Yes."

Assistant: [Uses rsync directly for specific skill]
"Backing up skills/code-reviewer/ to /Users/choi/work/claude-config/skills/code-reviewer/

✅ Backup complete!

Copied:
  - skills/code-reviewer/SKILL.md
  - skills/code-reviewer/references/best-practices.md
  - skills/code-reviewer/examples/review-workflow.md

Total: 3 files
Target: /Users/choi/work/claude-config/skills/code-reviewer"
```

**Command Used**:
```bash
# Backup specific skill directory
rsync -av ~/.claude/skills/code-reviewer/ /target/skills/code-reviewer/
```

## Example 10: Error Recovery

**Scenario**: Backup fails with permission error.

**Trigger**: "backup my claude config"

**Expected Workflow**:

```
Assistant: "I'll backup your Claude configurations.

Target directory: /Users/choi/work/claude-config
Is this correct?"

User: "Yes."

Assistant: [Executes backup]

❌ Error: Permission denied writing to /Users/choi/work/claude-config

"The target directory isn't writable. Let's try a different location.

How about:
1. Current home directory: ~/
2. Temp directory: /tmp/claude-backup
3. Custom location: [you specify]

Which would you prefer?"

User: "Use ~/backups"

Assistant: [Retries with ~/backups]
"Creating target directory: /Users/choi/backups
Using rsync for efficient backup
Backing up from /Users/choi/.claude to /Users/choi/backups

✅ Backup complete!

Copied directories:
  - commands/ (15 files, 1 directories)
  - skills/ (8 directories, 42 files)
  - agents/ (23 files)

Total: 80 files in 51 directories
Target: /Users/choi/backups

Problem solved! Your backup is complete."
```

## Best Practices

1. **Always confirm target directory** before copying
2. **Use timestamps** for backup rotation (e.g., claude-20250119)
3. **Verify backup** by checking file counts and sizes
4. **Test restore** periodically to ensure backups work
5. **Backup before major changes** (updates, refactoring, experiments)
6. **Use version control** for configurations you want to track over time
7. **Exclude sensitive files** when sharing (.local.md, settings.local.json)
8. **Document your setup** in README for team sharing
9. **Automate backups** for peace of mind
10. **Monitor backup size** to detect unexpected growth

## Quick Reference Commands

```bash
# Backup all to current dir
~/.claude/skills/config-backup/scripts/backup.sh

# Backup all to custom dir
~/.claude/skills/config-backup/scripts/backup.sh /path/to/target

# Backup specific directories
~/.claude/skills/config-backup/scripts/backup.sh /path/to/target commands skills

# Timestamped backup
~/.claude/skills/config-backup/scripts/backup.sh ~/backups/claude-$(date +%Y%m%d)

# Backup specific skill
rsync -av ~/.claude/skills/skill-name/ /target/skills/skill-name/

# Verify backup (compare file counts)
find ~/.claude/commands -type f | wc -l
find /target/commands -type f | wc -l
```
