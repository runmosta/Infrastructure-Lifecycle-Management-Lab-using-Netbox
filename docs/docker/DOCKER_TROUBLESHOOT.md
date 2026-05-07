# Docker Troubleshooting Guide

## Error: "unable to get image" / Docker Daemon Not Responding

**Cause**: Docker Desktop is not running or not properly connected.

---

## Step 1: Check if Docker Desktop is Running

### On Windows:
1. **Look for Docker icon in System Tray** (bottom right of taskbar)
   - If you see the whale icon 🐋, Docker is running
   - If you don't see it, Docker is NOT running

2. **Or check Task Manager**:
   - Press `Ctrl+Shift+Esc`
   - Look for "Docker Desktop" process
   - If not there, it's not running

3. **Or open File Explorer and look for**:
   ```
   C:\Program Files\Docker\Docker
   ```

---

## Step 2: Start Docker Desktop (if not running)

### Option A: Click the Icon
- Find Docker Desktop shortcut on your desktop or start menu
- Double-click to launch
- Wait 2-3 minutes for it to fully start
- You'll see the whale icon in system tray when ready

### Option B: Command Line
```bash
# Start Docker Desktop
"C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### Option C: Restart Windows
If Docker won't start:
1. Restart your Windows machine
2. Docker Desktop will auto-start
3. Wait for it to fully load (check system tray)

---

## Step 3: Verify Docker is Working

Once Docker Desktop is running, verify it's responsive:

```bash
# Check Docker version
docker --version

# Test Docker can pull images
docker run hello-world
```

**Expected output from `docker --version`**:
```
Docker version 25.x.x, build xxxxxxx
```

**Expected output from `docker run hello-world`**:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

---

## Step 4: Check Docker Daemon Status

```bash
# Get Docker info
docker info

# Look for this in output:
# - Server Version: 25.x.x
# - Containers: X
# - Images: X
# - Status: running
```

---

## Step 5: Retry Netbox Startup

Once Docker is confirmed working:

```bash
cd <PROJECT_ROOT>

# Try again
docker compose -f Docker/docker-compose.yml up -d

# Check status
docker compose -f Docker/docker-compose.yml ps
```

---

## Common Docker Desktop Issues & Solutions

### Issue: Docker Desktop Won't Start
**Solutions**:
1. Restart Windows
2. Check if "Windows Subsystem for Linux 2 (WSL2)" is installed
3. If not installed, reinstall Docker Desktop (it will install WSL2)

### Issue: "Cannot connect to Docker daemon"
**Solutions**:
```bash
# Try restarting Docker
# Option 1: Quit Docker Desktop and restart
# Option 2: Or restart Windows

# Option 3: Reset Docker (clears all images/containers!)
# WARNING: This deletes all Docker data
docker system prune -a
```

### Issue: "No space left on device"
**Solutions**:
```bash
# Check Docker disk usage
docker system df

# Clean up unused images
docker image prune -a

# Clean up unused containers
docker container prune
```

### Issue: Docker Desktop is using too much CPU/Memory
**Solutions**:
1. Open Docker Desktop settings (right-click whale icon → Settings)
2. Go to "Resources"
3. Reduce CPU cores and memory allocation
4. Click "Apply & Restart"

---

## WSL2 (Windows Subsystem for Linux 2) Check

Docker Desktop requires WSL2. Verify it's installed:

```bash
# Check if WSL2 is installed
wsl --list --verbose

# Expected output shows WSL 2
#   Ubuntu                   Running    2
```

If WSL2 is not installed:
1. Open a terminal as Administrator
2. Run: `wsl --install`
3. Restart Windows
4. Open Docker Desktop again

---

## Reinstall Docker Desktop (Last Resort)

If Docker still won't work:

1. **Uninstall Docker Desktop**:
   - Go to Settings → Apps → Apps & features
   - Search for "Docker"
   - Click "Uninstall"
   - Restart Windows

2. **Reinstall Docker Desktop**:
   - Download from: https://www.docker.com/products/docker-desktop
   - Run installer
   - Follow prompts
   - Restart Windows
   - Docker should auto-start

---

## After Docker is Working

Once `docker --version` works:

```bash
cd <PROJECT_ROOT>

# Start Netbox stack
docker compose -f Docker/docker-compose.yml up -d

# Wait 1-2 minutes for all services to start

# Check status
docker compose -f Docker/docker-compose.yml ps

# Access Netbox
# Open browser: http://localhost:8000
```

---

## Need Help?

If you're still stuck:

1. **Verify the error exactly**: Share the full error message
2. **Check Docker logs**:
   ```bash
   docker system df
   docker info
   ```
3. **Check Windows Event Viewer**: Right-click "This PC" → Manage → Event Viewer
4. **Consider VM approach**: If Docker Desktop won't work, could use Hyper-V VM with Linux

---

**Next**: Start or restart Docker Desktop, then run:
```bash
docker compose -f Docker/docker-compose.yml up -d
```
