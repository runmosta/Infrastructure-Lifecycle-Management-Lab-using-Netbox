# Netbox Infrastructure Lab — Setup Guide

## ✅ Design Phase Complete

You now have a complete design for your infrastructure lab. Three documentation files created:

### Documentation Files
1. **READ.md** — Project overview, goals, architecture, technologies
2. **SKILL.md** — Complete architecture, design decisions, implementation components
3. **CODE_STRUCTURE.md** — Detailed folder structure and file organization
4. **SETUP_GUIDE.md** — This file; step-by-step setup instructions

## 📁 Folder Structure to Create

Create this structure in `c:\Users\runem\Nextcloud\Code\Netbox`:

```
Netbox/
├── Code/                      # Source code and configurations
│   ├── netbox/               # Netbox Docker setup and configs
│   ├── python/               # Python automation scripts
│   │   └── scripts/          # Actual Python scripts
│   ├── ansible/              # Ansible playbooks
│   │   ├── playbooks/
│   │   ├── roles/
│   │   ├── inventory/
│   │   └── ansible.cfg
│   └── docker/               # Docker Compose files
├── logs/                     # Application logs
│   ├── netbox/
│   ├── python/
│   └── ansible/
├── Data/                     # Persistent data
│   ├── postgres/             # Database files
│   ├── netbox/               # Application data
│   └── volumes/              # Named Docker volume mounts
├── config/                   # Configuration files
│   ├── netbox.config.yml
│   ├── python.config.yml
│   └── ansible.config.yml
└── docker-compose.yml        # Main orchestration file
```

**PowerShell script to create structure:**
```powershell
$base = "c:\Users\runem\Nextcloud\Code\Netbox"
@(
  "Code\netbox", "Code\python\scripts", "Code\ansible\playbooks", 
  "Code\ansible\roles", "Code\ansible\inventory", "Code\docker",
  "logs\netbox", "logs\python", "logs\ansible",
  "Data\postgres", "Data\netbox", "Data\volumes", "config"
) | ForEach-Object {
  New-Item -ItemType Directory -Path "$base\$_" -Force | Out-Null
}
Write-Host "✓ Folder structure created"
```

## 🐳 Next Implementation Steps

### Phase 1: Netbox Setup
**Goal**: Get Netbox running in Docker with PostgreSQL

Files to create:
- `Code/docker/docker-compose.yml` — Main orchestration
- `Code/netbox/.env` — Netbox environment variables
- `config/netbox.config.yml` — Netbox settings

Tasks:
1. Create docker-compose.yml with Netbox + PostgreSQL services
2. Configure volume mounts to `Data/postgres/`, `Data/netbox/`, `logs/netbox/`
3. Set custom device fields: EOS, Service Start Date, Service End Date, Service Tags
4. Test: `docker-compose up` and verify Netbox starts

### Phase 2: Python Container Setup
**Goal**: Create Python automation container for device polling

Files to create:
- `Code/python/Dockerfile` — Python image with dependencies
- `Code/python/requirements.txt` — Python dependencies (netboxapi, paramiko, pysnmp)
- `Code/python/scripts/health_check.py` — Device health monitoring
- `Code/python/scripts/device_discovery.py` — SNMP/SSH device discovery
- `Code/python/scripts/netbox_api_client.py` — Netbox API integration

Tasks:
1. Create Python Dockerfile with netboxapi, paramiko, pysnmp
2. Build health check script: ping/SSH/SNMP reachability
3. Build device discovery script: auto-discover devices, update Netbox
4. Test: Run Python scripts against test devices

### Phase 3: Ansible Container Setup
**Goal**: Create Ansible automation container

Files to create:
- `Code/ansible/Dockerfile` — Ansible image
- `Code/ansible/ansible.cfg` — Ansible configuration
- `Code/ansible/inventory/hosts.yml` — Dynamic inventory (from Netbox)
- `Code/ansible/playbooks/health_check.yml` — Health check playbook
- `Code/ansible/roles/` — Reusable roles

Tasks:
1. Create Ansible Dockerfile
2. Create playbooks for device configuration
3. Integrate Netbox as dynamic inventory source
4. Test: Run playbooks

### Phase 4: Offline Testing with EVE-NG (Optional/Future)
**Goal**: Set up network emulation for testing

Tasks:
1. Install EVE-NG or use alternative (GNS3)
2. Create Cisco, Arista, Fortinet device templates
3. Configure EVE-NG network bridge to Docker network
4. Test Python/Ansible against emulated devices

### Phase 5: Online Testing with Real Devices
**Goal**: Connect to real network devices

Tasks:
1. Configure Python/Ansible containers to reach real network
2. Test health checks against real devices
3. Validate Netbox API integration with production data
4. Verify lifecycle tracking fields work

## 🎯 Key Milestones

- [ ] Folders created
- [ ] docker-compose.yml working (Netbox + PostgreSQL start)
- [ ] Python container runs health checks
- [ ] Ansible container executes playbooks
- [ ] Netbox lifecycle fields (EOS, Service dates, tags) populated
- [ ] Offline testing with EVE-NG (optional)
- [ ] Online testing with real devices

## 📋 Configuration Templates

### Basic docker-compose.yml structure
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: netbox
      POSTGRES_USER: netbox
      POSTGRES_PASSWORD: netbox
    volumes:
      - ./Data/postgres:/var/lib/postgresql/data
    
  netbox:
    image: netboxcommunity/netbox:latest
    depends_on:
      - postgres
    environment:
      DB_NAME: netbox
      DB_USER: netbox
      DB_PASSWORD: netbox
      DB_HOST: postgres
    ports:
      - "8000:8000"
    volumes:
      - ./logs/netbox:/var/log/netbox
      - ./Data/netbox:/app/data
    
  python:
    build: ./Code/python/
    volumes:
      - ./Code/python:/app
      - ./logs/python:/app/logs
    depends_on:
      - netbox
    
  ansible:
    build: ./Code/ansible/
    volumes:
      - ./Code/ansible:/etc/ansible
      - ./logs/ansible:/var/log/ansible
    depends_on:
      - netbox
```

### Python requirements.txt
```
netboxapi==1.0.0
paramiko==2.11.0
pysnmp==4.4.12
requests==2.28.0
pyyaml==6.0
```

### Ansible requirements.yml
```yaml
collections:
  - community.general
  - netbox.netbox
```

## 🚀 Quick Start Commands (Once Setup Complete)

```bash
# Create folder structure
mkdir -p Code/{netbox,python/scripts,ansible/{playbooks,roles,inventory},docker}
mkdir -p logs/{netbox,python,ansible}
mkdir -p Data/{postgres,netbox,volumes}
mkdir -p config

# Start all services
cd c:\Users\runem\Nextcloud\Code\Netbox
docker-compose up -d

# Access Netbox
# http://localhost:8000

# View logs
docker-compose logs -f netbox

# Stop all services
docker-compose down
```

## ✨ What's Next?

Once the design is approved, we can:
1. Create the docker-compose.yml file
2. Build Python scripts for device automation
3. Build Ansible playbooks for network configuration
4. Test against offline simulated devices
5. Deploy to real devices

**The design is solid and ready for implementation.**
