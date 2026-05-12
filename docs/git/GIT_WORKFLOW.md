# Git Workflow and Backup Guide

## Git Repository Setup

Your Netbox Infrastructure Lab is now a Git repository for version control and backup.

### Repository Location
```
<PROJECT_ROOT>
```

### What's Tracked
- **Documentation**: README.md, SKILL.md, CODE_STRUCTURE.md, SETUP_GUIDE.md, etc.
- **Source Code**: Python scripts, Ansible playbooks, Dockerfiles
- **Configuration**: docker-compose.yml, Ansible configs, Python config files

### What's NOT Tracked (via .gitignore)
- **Data**: PostgreSQL database files (`Data/postgres/*`)
- **Logs**: All log files (`logs/**/*.log`)
- **Environment Secrets**: `.env` files, SSH keys, passwords
- **Build Artifacts**: Python cache, compiled files, node_modules
- **OS Files**: Thumbs.db, .DS_Store

## Git Workflow

### Initial Setup (First Time)
```bash
cd <PROJECT_ROOT>

# Initialize repository (if not already done)
git init

# Configure user info
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all tracked files
git add .

# Create initial commit
git commit -m "Initial commit: Infrastructure Lab design documentation

- Netbox infrastructure design for multi-vendor device management
- Architecture supporting offline (EVE-NG) and online (real devices) modes
- Documentation for setup and implementation phases

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Daily Workflow

#### Add and Commit Changes
```bash
# See what changed
git status

# Stage specific files
git add Code/python/scripts/health_check.py

# Or stage all changes
git add .

# Commit with descriptive message
git commit -m "Add Python health check script

- Implements ICMP ping and SSH connectivity checks
- Logs results to Data/volumes/health_check_results.json
- Compatible with both simulated and real devices"
```

#### View History
```bash
# View commit log
git log --oneline

# View recent changes
git log -5

# See what changed in a commit
git show <commit-hash>

# View file history
git log --oneline -- Code/python/scripts/health_check.py
```

#### Working with Branches

**Always branch before making changes.** This keeps `main` stable and lets you compare or discard work safely.

**VS Code task (recommended):** Open the Command Palette (`Cmd+Shift+P`) → `Tasks: Run Task` → choose:
- **Git: New Feature Branch** — pulls latest main and creates a named branch (prompts you for the name)
- **Git: Commit and Push** — stages all changes, commits with a message, and pushes the branch
- **Git: Merge Branch to Main** — merges the current branch into main, pushes, and deletes the branch

**Manual steps:**
```bash
# 1. Start fresh from main
git checkout main && git pull

# 2. Create your branch (use a prefix that matches the change type)
git checkout -b feature/eve-ng-integration   # new functionality
git checkout -b fix/pynetbox-auth-error      # bug fix
git checkout -b chore/update-docker-compose  # config/infra change
git checkout -b experiment/snmp-polling      # exploratory work

# 3. Make changes and commit regularly
git add .
git commit -m "Add EVE-NG device discovery"

# 4. Push branch to GitHub for backup / review
git push --set-upstream origin $(git branch --show-current)

# 5. When done, merge back to main and clean up
git checkout main
git merge feature/eve-ng-integration
git push
git branch -d feature/eve-ng-integration
```

**Branch naming conventions:**

| Prefix | Example | Use case |
|--------|---------|----------|
| `feature/` | `feature/lifecycle-plugin-migration` | New functionality |
| `fix/` | `fix/pynetbox-auth-error` | Bug fixes |
| `chore/` | `chore/update-docker-compose` | Config/infra changes |
| `experiment/` | `experiment/snmp-polling` | Exploratory/throwaway work |

## Backup Strategy

### Local Backup
Git stores all history locally in `.git/` directory. To backup:
```bash
# Windows
xcopy "<PROJECT_ROOT>" "E:\Backup\Netbox" /E /I

# macOS/Linux
cp -R "<PROJECT_ROOT>" /path/to/backup/Netbox
```

### Remote Backup (Recommended)
Set up a remote repository on GitHub, GitLab, or similar:

#### GitHub Setup
1. Create new repository on GitHub (https://github.com/new)
2. Name it: `netbox-infrastructure-lab`
3. In your local repo, add remote:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/netbox-infrastructure-lab.git
   git branch -M main
   git push -u origin main
   ```
4. Future pushes: `git push`

#### GitLab Setup
```bash
git remote add origin https://gitlab.com/YOUR_USERNAME/netbox-infrastructure-lab.git
git branch -M main
git push -u origin main
```

## Commit Message Guidelines

Use clear, descriptive commit messages following this format:

```
[TYPE]: Brief description (under 50 chars)

Optional detailed explanation (72 char width)
- Bullet point for each change
- Keep it concise but informative

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

### Types
- **docs**: Documentation changes
- **feat**: New feature or component
- **fix**: Bug fixes
- **refactor**: Code reorganization
- **config**: Configuration changes
- **test**: Test additions or updates

### Examples
```
feat: Add Netbox docker compose setup

- PostgreSQL backend with volume persistence
- Environment variable configuration
- Network setup for offline testing

docs: Update SETUP_GUIDE with Phase 1 instructions

fix: Correct Ansible inventory path in docker-compose.yml

config: Add production docker-compose.override.yml template
```

## Useful Git Commands

| Command | Purpose |
|---------|---------|
| `git status` | See what changed |
| `git add <file>` | Stage changes |
| `git commit -m "msg"` | Commit staged changes |
| `git log --oneline` | View history |
| `git diff` | View unstaged changes |
| `git diff --cached` | View staged changes |
| `git checkout -- <file>` | Discard changes to file |
| `git reset HEAD <file>` | Unstage file |
| `git branch` | List branches |
| `git branch -b <name>` | Create new branch |
| `git checkout <branch>` | Switch branch |
| `git merge <branch>` | Merge branch |
| `git push` | Push to remote |
| `git pull` | Fetch and merge from remote |

## .gitignore Reference

The repository includes a `.gitignore` file that prevents these from being tracked:

### Data and Logs
- `Data/postgres/*` — Live database files
- `Data/netbox/*` — Runtime application data
- `logs/**/*.log` — Application logs

### Secrets
- `.env` files — Environment variables with secrets
- `*.pem`, `*.key` — SSH keys and certificates

### Build Artifacts
- `__pycache__/` — Python cache
- `*.pyc` — Compiled Python
- `venv/`, `env/` — Virtual environments

### IDE Files
- `.vscode/` — VS Code settings
- `.idea/` — JetBrains IDE settings

## Collaborative Development

If working with team members:

```bash
# Add team member's SSH key
git config --global user.name "Team Member Name"

# Before pushing, always pull latest changes
git pull

# If conflicts, resolve manually then:
git add <resolved-files>
git commit -m "Merge conflict resolution"
git push
```

## Disaster Recovery

If you need to restore from backup:

```bash
# Clone from remote backup
git clone https://github.com/YOUR_USERNAME/netbox-infrastructure-lab.git

# Or restore from local backup and re-establish remote
cd restored-repo
git remote add origin https://github.com/YOUR_USERNAME/netbox-infrastructure-lab.git
git push -u origin main
```

---

**Backup Recommendation**: Set up GitHub/GitLab remote backup AND periodic local backups to external drive.
