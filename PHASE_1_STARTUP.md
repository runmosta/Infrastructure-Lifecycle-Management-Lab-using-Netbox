# Phase 1: Netbox + PostgreSQL Docker Setup — Getting Started

## Overview
This phase sets up Netbox as your network source of truth with:
- **Netbox**: IPAM and device inventory
- **PostgreSQL**: Database backend (persists to Windows)
- **Redis**: Cache for better performance
- **Netbox Worker**: Background task processing

## Files Created
- `Docker/docker-compose.yml` — Complete stack orchestration
- `.env` — Environment variables (passwords, API tokens)

## Prerequisites
✅ Docker Desktop installed and running  
✅ Git repository initialized  
✅ Folder structure created (Code/, logs/, Data/)  

## Step 1: Configure Environment Variables

Edit the `.env` file in the root directory:

```
<PROJECT_ROOT>\.env
```

**IMPORTANT**: Change these values:

### Option A: Quick Start (for testing)
Keep defaults for now, change before production.

### Option B: Secure Setup (recommended)
Generate secure values:

```bash
# Option 1: Generate SECRET_KEY using Python
python -c "from secrets import token_urlsafe; print(token_urlsafe(32))"

# Option 2: Or just use a strong passphrase
NETBOX_SECRET_KEY=your_very_long_random_string_here_at_least_32_chars

# Generate API Token
python -c "import secrets; print(secrets.token_hex(20))"
NETBOX_API_TOKEN=your_generated_token_here
```

Update `.env` with your values:
```
NETBOX_SECRET_KEY=your_generated_key
NETBOX_ADMIN_PASSWORD=your_admin_password
NETBOX_API_TOKEN=your_api_token
```

## Step 2: Start Netbox Stack

Navigate to project root and start containers:

```bash
cd <PROJECT_ROOT>

# Start all services in background
docker compose -f Docker/docker-compose.yml up -d

# Or start with logs visible (Ctrl+C to stop)
docker compose -f Docker/docker-compose.yml up
```

**Expected output:**
```
Creating netbox-postgres    ... done
Creating netbox-redis       ... done
Creating netbox-app         ... done
Creating netbox-worker      ... done
```

## Step 3: Verify Services Are Running

```bash
# Check container status
docker compose -f Docker/docker-compose.yml ps

# All containers should show "Up" status
# Example output:
#   NAME               COMMAND              STATUS
#   netbox-postgres    postgres             Up 2 minutes (healthy)
#   netbox-redis       redis-server         Up 2 minutes (healthy)
#   netbox-app         gunicorn ...         Up 2 minutes (healthy)
#   netbox-worker      python manage ...    Up 2 minutes
```

## Step 4: Access Netbox UI

Wait 30-60 seconds for Netbox to fully start, then open browser:

```
http://localhost:8000
```

**Login credentials:**
```
Username: admin
Password: (from NETBOX_ADMIN_PASSWORD in .env)
```

## Step 5: Verify Database Persistence

Check that data is persisting to Windows:

```bash
# List files in Data/postgres/
dir Data/postgres\

# Should show PostgreSQL database files:
#   global/
#   pg_stat_tmp/
#   pg_tblspc/
#   etc.
```

## Step 6: Check Logs

View application logs:

```bash
# View Netbox logs
docker compose -f Docker/docker-compose.yml logs -f netbox

# View PostgreSQL logs
docker compose -f Docker/docker-compose.yml logs -f postgres

# View Redis logs
docker compose -f Docker/docker-compose.yml logs -f redis

# Ctrl+C to stop following logs
```

## Common Issues & Solutions

### Issue: "Connection refused" when accessing http://localhost:8000
**Solution**: Netbox takes time to start. Wait 1-2 minutes, then refresh.

### Issue: "Port 8000 already in use"
**Solution**: Stop any existing Netbox containers:
```bash
docker compose -f Docker/docker-compose.yml down
docker ps  # Check for any running containers
```

### Issue: "PostgreSQL connection failed"
**Solution**: Check PostgreSQL logs:
```bash
docker compose -f Docker/docker-compose.yml logs postgres
```

### Issue: Database not persisting
**Solution**: Verify volume mount:
```bash
docker compose -f Docker/docker-compose.yml inspect netbox-postgres | grep Mounts  # Windows: use findstr Mounts
```

## Next Steps After Verification

### 1. Create Custom Device Fields
In Netbox UI:
- Navigate to: Administration → Custom Fields
- Create fields:
  - **EOS** (Boolean) — End of Service flag
  - **Service Start Date** (Date) — Deployment date
  - **Service End Date** (Date) — Retirement date
  - **Service Tags** (Choice) — Cost center mapping

### 2. Add Test Data
- Add sample routers, switches, firewalls
- Assign IPs and device types
- Populate custom fields

### 3. Get API Token for Python Scripts
- In Netbox UI: Administration → Authentication Tokens
- Create token for Python scripts
- Copy token value to use in Phase 2

### 4. Document API Endpoints
- Base URL: `http://localhost:8000/api/`
- Test in browser: `http://localhost:8000/api/dcim/devices/`

## Stopping Services

```bash
# Stop all containers (data persists)
docker compose -f Docker/docker-compose.yml down

# Stop and remove volumes (WARNING: deletes data)
docker compose -f Docker/docker-compose.yml down -v
```

## Backup & Version Control

```bash
# Commit docker compose setup to Git
git add Docker/docker-compose.yml .gitignore
git commit -m "feat: Add Netbox + PostgreSQL Docker setup

- PostgreSQL backend with volume persistence
- Netbox with Redis caching
- Netbox worker for background tasks
- All data persists to Windows filesystem
- Environment variables for configuration"

# Push to GitHub
git push
```

---

## ✅ Phase 1 Complete When:
- [ ] Docker containers start without errors
- [ ] Netbox UI accessible at http://localhost:8000
- [ ] Can log in with admin credentials
- [ ] Database files in Data/postgres/
- [ ] Logs visible in logs/netbox/
- [ ] Custom fields created
- [ ] Changes committed to Git

**Estimated time: 30-45 minutes**

Next phase: Python automation scripts (Phase 2)
