# Git Setup Instructions — Step by Step

## Prerequisites
- Git is installed (`git` command available)
- You're in `c:\Users\runem\Nextcloud\Code\Netbox` directory

## Step 1: Initialize Git Repository

Open Command Prompt or PowerShell in the Netbox directory:

```cmd
cd c:\Users\runem\Nextcloud\Code\Netbox
git init
```

**Output should be**: `Initialized empty Git repository in c:\Users\runem\Nextcloud\Code\Netbox\.git\`

## Step 2: Configure Git User

Set up your identity for commits:

```cmd
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

To verify:
```cmd
git config --list
```

## Step 3: Create Folder Structure

You'll need to create the folder structure manually. Here's a PowerShell script:

```powershell
$base = "c:\Users\runem\Nextcloud\Code\Netbox"

$dirs = @(
  "Code\netbox", "Code\python", "Code\python\scripts",
  "Code\ansible", "Code\ansible\playbooks", "Code\ansible\roles",
  "Code\ansible\inventory", "Code\docker",
  "logs\netbox", "logs\python", "logs\ansible",
  "Data\postgres", "Data\netbox", "Data\volumes",
  "config"
)

foreach ($dir in $dirs) {
  $path = "$base\$dir"
  if (-not (Test-Path $path)) {
    New-Item -ItemType Directory -Path $path -Force | Out-Null
    # Add .gitkeep to preserve empty directories
    Add-Content -Path "$path\.gitkeep" -Value ""
  }
}

Write-Host "✓ Folder structure created"
```

**Or manually using CMD/File Explorer:**
```
mkdir Code\netbox
mkdir Code\python\scripts
mkdir Code\ansible\playbooks
mkdir Code\ansible\roles
mkdir Code\ansible\inventory
mkdir Code\docker
mkdir logs\netbox
mkdir logs\python
mkdir logs\ansible
mkdir Data\postgres
mkdir Data\netbox
mkdir Data\volumes
mkdir config
```

## Step 4: Add Files to Git

Stage all documentation and configuration files:

```cmd
git add .
```

To see what will be committed:
```cmd
git status
```

## Step 5: Create Initial Commit

```cmd
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

```cmd
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

```cmd
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/netbox-infrastructure-lab.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Verify Everything Works

```cmd
# Check repository status
git status

# View commit history
git log --oneline

# Check remote (if set up)
git remote -v
```

## Next: Using Git During Development

For each change:
```cmd
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
```cmd
xcopy "c:\Users\runem\Nextcloud\Code\Netbox" "E:\Backup\Netbox" /E /I /Y
```

### Push to Remote
```cmd
git push origin main
```

---

**Once you've completed these steps, your project is version controlled and ready for backup!**

See `GIT_WORKFLOW.md` for detailed Git workflow documentation.
