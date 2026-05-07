# Git Setup Instructions — Step by Step

## Prerequisites
- Git is installed (`git` command available)
- You're in `<PROJECT_ROOT>` directory

## Step 1: Initialize Git Repository

Open a terminal in the repository root:

```bash
cd <PROJECT_ROOT>
git init
```

**Output should be**: `Initialized empty Git repository in <PROJECT_ROOT>\.git\`

## Step 2: Configure Git User

Set up your identity for commits:

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

To verify:
```bash
git config --list
```

## Step 3: Create Folder Structure

Use shell commands to create the folder structure. Example:

```bash
mkdir -p Code/{netbox,python/scripts,ansible/{playbooks,roles,inventory},docker}
mkdir -p logs/{netbox,python,ansible}
mkdir -p Data/{postgres,netbox,volumes}
mkdir -p config
```

Windows users can also create the same folders in PowerShell or File Explorer.

## Step 4: Add Files to Git

Stage all documentation and configuration files:

```bash
git add .
```

To see what will be committed:
```bash
git status
```

## Step 5: Create Initial Commit

```bash
git commit -m "Initial commit: Netbox Infrastructure Lab design

- Complete architecture design for multi-vendor device management
- Documentation: READ.md, SKILL.md, CODE_STRUCTURE.md
- Setup guide and Git workflow documentation
- Folder structure for Code, logs, and Data persistence
- Support for offline (EVE-NG) and online (real devices) modes

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Step 6: Verify Repository

Check your repository was created successfully:

```bash
git log --oneline
```

Should show your initial commit.

## Step 7 (Optional): Set Up Remote Backup

To backup to GitHub:

### Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `netbox-infrastructure-lab`
3. Description: `Infrastructure Lifecycle Management Lab using Netbox`
4. Make it Private if you want
5. Click "Create repository"

### Connect Local Repo to GitHub

After creating the repository, follow GitHub's instructions:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/netbox-infrastructure-lab.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Verify Everything Works

```bash
# Check repository status
git status

# View commit history
git log --oneline

# Check remote (if set up)
git remote -v
```

## Next: Using Git During Development

For each change:
```bash
# See what changed
git status

# Stage your changes
git add <filename>
# Or add everything:
git add .

# Commit with message
git commit -m "feat: Description of what you added"

# Push to remote (if configured)
git push
```

## Backup Routine

### Weekly Local Backup
```bash
# Windows
xcopy "<PROJECT_ROOT>" "E:\Backup\Netbox" /E /I /Y

# macOS/Linux
cp -R "<PROJECT_ROOT>" /path/to/backup/Netbox
```

### Push to Remote
```bash
git push origin main
```

---

**Once you've completed these steps, your project is version controlled and ready for backup!**

See `GIT_WORKFLOW.md` for detailed Git workflow documentation.
