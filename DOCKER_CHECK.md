# 🐳 Docker Desktop Startup Checklist

## Quick Fix (Try These First)

### ✅ Step 1: Is Docker Desktop Running?
- [ ] Check system tray (bottom right) for Docker whale icon 🐋
- [ ] If no icon, Docker is NOT running

### ✅ Step 2: Start Docker Desktop
- [ ] Find Docker Desktop in start menu or desktop
- [ ] Double-click to launch
- [ ] Wait 2-3 minutes for startup
- [ ] Confirm whale icon appears in system tray

### ✅ Step 3: Verify Docker is Working
Open Command Prompt and run:

```cmd
docker --version
```

Should show: `Docker version 25.x.x, build xxxxxxx`

If you see this, Docker is working! ✅

### ✅ Step 4: Test Docker Can Pull Images
```cmd
docker run hello-world
```

Should show: `Hello from Docker!`

### ✅ Step 5: Try Netbox Again
```cmd
cd c:\Users\runem\Nextcloud\Code\Netbox
docker-compose -f Code/docker/docker-compose.yml up -d
```

Wait 1-2 minutes, then check:
```cmd
docker-compose -f Code/docker/docker-compose.yml ps
```

All containers should show "Up" ✅

---

## If Still Not Working

### ⚠️ Common Issues:

**"command not found: docker"**
- Docker Desktop not installed
- Need to restart Windows after installation
- Try reinstalling Docker Desktop from https://www.docker.com/products/docker-desktop

**"Cannot connect to Docker daemon"**
- Docker Desktop crashed
- Try restarting Docker Desktop
- Or restart Windows entirely

**"No such file or directory"**
- You're not in the right directory
- Make sure you're in: `c:\Users\runem\Nextcloud\Code\Netbox`
- Run: `cd c:\Users\runem\Nextcloud\Code\Netbox` first

**"Port 8000 already in use"**
- Another container is using that port
- Run: `docker ps` to see running containers
- Or: `docker-compose -f Code/docker/docker-compose.yml down` to stop

---

## Full Troubleshooting Guide

If quick fixes don't work, see: **DOCKER_TROUBLESHOOT.md**

---

## Success! ✅

Once Netbox starts successfully:

1. **Access Netbox UI**:
   ```
   http://localhost:8000
   ```

2. **Login**:
   ```
   Username: admin
   Password: (from .env file)
   ```

3. **Next**: Follow PHASE_1_STARTUP.md for remaining setup

---

**Status**: Ready to proceed once Docker Desktop is running!
