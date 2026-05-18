# Infrastructure Lifecycle Management Lab

## 🚀 Getting Started (5 Minutes)

**Prerequisite:** Docker Desktop must be running

```bash
# 1. Start all containers
cd Docker/
docker compose up -d

# 2. Open Netbox in browser
# → http://localhost:8000
# → Login: admin / Cisco123!

# 3. Option A: Use dev container in VS Code
# → Cmd+Shift+P → "Dev Containers: Reopen in Container"
# → Full Python/Ansible IDE ready

# 4. Option B: Run scripts directly
docker exec netbox-automation python python/scripts/my_script.py
docker exec netbox-automation ansible-playbook ansible/playbooks/my_playbook.yml
```

**What you get:**
- Netbox IPAM web UI (http://localhost:8000)
- PostgreSQL database
- Redis cache
- Python 3.11 with Ansible in isolated container
- Full VS Code IDE with debugging
- All credentials in `Docker/.env`

---

## Overview
A dual-mode network infrastructure management system using **Netbox** for inventory and IPAM, supporting both offline (simulated) and online (real device) operations on your Windows machine.

## Vision
Use Netbox as a **centralized lifecycle management system** for multi-vendor network devices (Cisco, Arista, Fortinet routers/switches/firewalls) with custom tracking fields and automated data enrichment.

## Applications & Technologies

### ✅ Currently Running (in Docker)
- **Netbox** (v4.0) — IPAM + device inventory + API (Container: `netbox`)
- **PostgreSQL** (15-alpine) — Netbox database (Container: `netbox-postgres`)
- **Redis** (7-alpine) — Cache & job queue (Container: `netbox-redis`)
- **Python** (3.11) — Automation scripts (Container: `netbox-automation`)
- **Ansible** (2.19.9) — Configuration management (Container: `netbox-automation`)
- **RQ Worker** — Background job processor (Container: `netbox-worker`)
- **Arista cEOS** (4.36.0F) — Containerized EOS virtual switch (Container: `arista-ceos-01`)

### ✅ Installed on Host
- **Visual Studio Code** — Development IDE with Dev Containers support
- **Docker Desktop** — Container runtime and orchestration
- **Git** — Version control (local repo + GitHub sync)

### 🔮 Future (Optional)
- **EVE-NG** — Network device emulation for offline testing
- **Jenkins** — CI/CD automation
- **Prometheus/Grafana** — Monitoring and metrics

## Goals

### Primary: Lifecycle Tracking
Extend Netbox with custom device fields for lifecycle management:
- **EOS (End of Service)** — Binary flag or date
- **Service End Date** — Date field for planned retirement
- **Service Start Date** — Date field for deployment tracking
- **Service Tags** — Cost center / work order tagging

### Secondary: Data Enrichment
Create automation to populate and maintain device data:
- **Device Health Monitoring** — Ping/reachability checks
- **Device Discovery & Updates** — Sync device data from network (SNMP, API)
- **Netbox API Integration** — Python scripts to read/write device data
- **Configuration Management** — Optional: store device configs in Netbox

### Tertiary: Validation & Testing
- Test Netbox capabilities for your infrastructure use case
- Develop Python scripts that integrate with Netbox API
- Create Ansible playbooks for network automation
- Support both offline testing (simulated devices) and online operations (real devices)

## Operational Modes

### Offline Mode (Development)
- Run Netbox + Python + Ansible in Docker containers
- Use EVE-NG to simulate network devices
- Test scripts and automation without affecting production
- All containers on same Docker network for easy testing

### Online Mode (Production)
- Netbox and Python/Ansible containers run on Windows
- Python/Ansible containers reach real network devices (Cisco, Arista, Fortinet)
- Real devices on your lab network or work environment
- Containers access devices via SSH, SNMP, or API calls

## Architecture Summary
- **Netbox**: Docker container, PostgreSQL backend, source of truth for device inventory
- **Python Container**: Health checks, API calls to Netbox, device data polling
- **Ansible Container**: Playbooks for configuration, bulk updates
- **Data Persistence**: All logs and data mount to Windows filesystem (Code/, logs/, Data/)
- **Container Networking**: Internal Docker network for offline testing; direct network access for real devices

## File Organization
```
Infrastructure-Lifecycle-Management-Lab-using-Netbox/
├── Docker/                          # Docker runtime files (gitignored)
│   ├── docker-compose.yml          # Main orchestration file
│   ├── .env                        # Environment variables (gitignored)
│   ├── Data/
│   │   ├── postgres/               # PostgreSQL persistent data
│   │   ├── netbox/                 # Netbox data volumes
│   │   └── volumes/redis/          # Redis cache data
│   └── logs/
│       ├── netbox/                 # Netbox application logs
│       └── ansible/                # Ansible playbook execution logs
├── Code/                            # Source code for automation
│   ├── ansible/
│   │   ├── inventory/              # Ansible inventory files
│   │   ├── playbooks/              # Ansible playbooks
│   │   └── roles/                  # Ansible roles
│   ├── python/scripts/             # Python automation scripts
│   └── netbox/plugins/             # Netbox custom plugins
├── .devcontainer/                  # VS Code dev container config
│   └── devcontainer.json          # Environment & extension setup
├── DEV_CONTAINER.md                # Dev container usage guide
├── DOCKER_CHECK.md                 # Docker verification steps
├── DOCKER_TROUBLESHOOT.md          # Docker troubleshooting guide
├── PHASE_1_QUICK_START.md          # Quick start instructions
├── GIT_WORKFLOW.md                 # Git workflow guide
└── README.md                       # This file
```

See `CODE_STRUCTURE.md` for detailed structure.

## Quick Start: 5 Minutes to Working Netbox

### 1. Start the Containers
```bash
cd Docker/
docker compose up -d
```

This starts:
- **netbox-postgres** — PostgreSQL 15 database (port 5432)
- **netbox-redis** — Redis cache (port 6379)
- **netbox** — Netbox web UI & API (port 8000)
- **netbox-worker** — Background job processor
- **netbox-automation** — Python/Ansible automation node
- **arista-ceos-01** — Arista cEOS 4.36.0F virtual switch (~2 min to boot)

### 2. Access Netbox Web UI
Open browser: **http://localhost:8000**

**Default Credentials:**
- Username: `admin`
- Password: `Cisco123!` (from Docker/.env)

### 3. Access via VS Code Dev Container

**Option A: Reopen in Container (Recommended)**
1. In VS Code: Cmd+Shift+P
2. Search: "Dev Containers: Reopen in Container"
3. Wait for setup to complete (~30 seconds)
4. Full development environment in VS Code terminal

**Option B: Attach to Running Container**
1. Cmd+Shift+P → "Dev Containers: Attach to Running Container"
2. Select `netbox-automation`
3. Instant access without rebuild

### 4. Run Your First Automation Script

From VS Code terminal (in dev container) or from host:
```bash
# Test Netbox connectivity
docker exec netbox-automation python python/test_config.py

# Access Netbox API from Python
docker exec netbox-automation python python/scripts/my_script.py

# Run Ansible playbook
docker exec netbox-automation ansible-playbook ansible/playbooks/my_playbook.yml
```

## System Architecture

### Container Network
All containers run on an isolated `netbox-network` bridge:

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                       │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  netbox      │  │ netbox-     │  │ netbox-    │  │
│  │ (Django App) ├──┤ postgres    │  │ redis      │  │
│  └──────────────┘  │ (Database)  │  │ (Cache)    │  │
│   ↓                └──────────────┘  └─────────────┘  │
│  Port 8000                                             │
│   ↑                ┌──────────────┐                    │
│   └────────────────┤  netbox-     │                    │
│                    │  worker      │                    │
│                    │ (RQ Jobs)    │                    │
│                    └──────────────┘                    │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │     netbox-automation (Python/Ansible)          │ │
│  │  - Can reach all services                       │ │
│  │  - Access .env credentials                      │ │
│  │  - Run scripts & playbooks                      │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │     arista-ceos-01 (Arista cEOS 4.36.0F)        │ │
│  │  - Virtual Arista EOS switch                    │ │
│  │  - eAPI on port 443, SSH on port 22             │ │
│  │  - Reachable by hostname from other containers  │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
        ↓
   Port Forwarding
        ↓
   localhost:8000
   (Your Host)
```

### Service Endpoints

| Service | Internal URL | External |
|---------|--------------|----------|
| Netbox Web UI | `http://netbox:8080` | `http://localhost:8000` |
| Netbox API | `http://netbox:8080/api/` | `http://localhost:8000/api/` |
| PostgreSQL | `postgres:5432` | `localhost:5432` |
| Redis | `redis:6379` | Not exposed |
| Arista cEOS SSH | `arista-ceos-01:22` | Not exposed |
| Arista cEOS eAPI | `arista-ceos-01:443` | Not exposed |

## How to Use Each Component

### 🌐 Netbox Web Interface

**Access:** http://localhost:8000

**Default User:** `admin` / `Cisco123!` (from Docker/.env)

**Common Tasks:**
- Add devices to inventory
- Manage IP addresses and IPAM
- Create custom fields for lifecycle tracking
- View device connections
- API documentation: http://localhost:8000/api/docs/

### 🐍 Python Automation Scripts

**Location:** `Code/python/scripts/`

**Example: Query Devices via API**
```python
#!/usr/bin/env python3
import os
import requests

# Environment variables automatically available
url = os.getenv("NETBOX_URL") + "/api/dcim/devices/"
token = os.getenv("NETBOX_API_TOKEN")

response = requests.get(
    url,
    headers={"Authorization": f"Token {token}"},
    verify=False
)

devices = response.json()
for device in devices["results"]:
    print(f"{device['name']}: {device['device_type']['model']}")
```

**Run from host:**
```bash
docker exec netbox-automation python python/scripts/query_devices.py
```

**Run from dev container:**
```bash
# In VS Code terminal (inside container)
python python/scripts/query_devices.py
```

### 🌿 Arista cEOS Virtual Switch

**Container:** `arista-ceos-01` (Arista EOS 4.36.0F)

cEOS is a fully containerized Arista EOS switch. It runs the same software as physical Arista hardware, making it ideal for testing Ansible playbooks and Python automation before applying them to real devices.

**cEOS boots in ~2 minutes.** Wait for it before running CLI commands.

**Access the EOS CLI:**
```bash
# Interactive CLI session
docker exec -it arista-ceos-01 /usr/bin/CliShell

# Single command
docker exec arista-ceos-01 /usr/bin/CliShell -c "show version"
docker exec arista-ceos-01 /usr/bin/CliShell -c "show interfaces"
docker exec arista-ceos-01 /usr/bin/CliShell -c "show ip interface brief"
```

**SSH to cEOS (from automation container or host):**
```bash
# Get the cEOS IP on the Docker network
docker inspect arista-ceos-01 --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'

# SSH in (credentials from startup-config)
ssh admin@<ip>   # password: admin
```

**Register cEOS in Netbox as a Virtual Machine:**
```bash
docker exec netbox-automation python /workspace/python/Add_Virtual_Device.py \
  --name arista-ceos-01 \
  --site LAB-OSL \
  --cluster "Lab Docker" \
  --platform EOS \
  --role leaf-switch \
  --ip 192.168.100.10/24
```

**How the image is built:**

The `arista/ceos:latest` image (imported from the Arista `.tar.xz` download) requires the `tun` kernel module and several EOS-specific modules (`rbfd`, etc.). On Docker Desktop for macOS these modules are either built into the linuxkit kernel (no `.ko` file) or simply not present, causing `EosStage2` to abort before any EOS agents start.

A custom `Dockerfile.ceos` bakes in a `modprobe` wrapper that returns success for missing/built-in modules, allowing EOS to boot fully. This fix is automatic — you never need to apply it manually.

```
Docker/
├── Dockerfile.ceos              # Builds arista/ceos-lab:latest
└── scripts/
    └── modprobe_wrapper.sh      # modprobe shim for Docker Desktop / macOS
```

**To add a second cEOS switch**, duplicate the `arista-ceos-01` service block in `docker-compose.yml`, change the container name, hostname, and `CEOS_SYSTEM_MAC`.

---

### 📋 Ansible Playbooks

**Location:** `Code/ansible/playbooks/`

#### Sync Virtual Device (cEOS) to Netbox

`sync_ceos_to_netbox.yml` — Connects to the `arista-ceos-01` container, collects EOS facts, and updates the matching Netbox VM record (Virtualization → Virtual Machines).

```bash
docker exec -e ANSIBLE_CONFIG=/workspace/ansible/ansible.cfg netbox-automation \
  ansible-playbook /workspace/ansible/playbooks/sync_ceos_to_netbox.yml
```

Per run, for each cEOS device:
- **Reachable** → collect EOS version + serial, update Netbox, mark active
- **Unreachable** → set Netbox status to `offline`, log it
- **Serial blank** → write serial to Netbox
- **Serial match** → log OK, no change
- **Serial mismatch** → log warning, **do not overwrite** (manual review required)

Log: `Docker/logs/ansible/ceos_sync.log`

---

#### Sync Physical Devices to Netbox

`sync_physical_to_netbox.yml` — Connects to real Arista/Cisco devices via SSH, collects facts, and updates the matching **DCIM device** record in Netbox.

**Prerequisites:**

1. Add device IPs to `Code/ansible/inventory/physical_devices.ini`:
   ```ini
   [arista_physical]
   your-arista-device ansible_host=<management-ip>

   [cisco_physical]
   your-cisco-device ansible_host=<management-ip>
   ```

2. Set SSH credentials in `Docker/.env`:
   ```
   DEVICE_SSH_USER=admin
   DEVICE_SSH_PASSWORD=<password>
   DEVICE_SSH_ENABLE=<enable-password>   # Cisco only; leave blank for Arista
   ```

3. Ensure the device is registered in Netbox first:
   ```bash
   docker exec netbox-automation python /workspace/python/Add_Device.py \
     --name <device-name> \
     --site <site-name> \
     --role <role> \
     --manufacturer <Arista|Cisco|Fortinet> \
     --model <model>
   ```

**Run:**
```bash
# All physical devices
docker exec -e ANSIBLE_CONFIG=/workspace/ansible/ansible.cfg netbox-automation \
  ansible-playbook /workspace/ansible/playbooks/sync_physical_to_netbox.yml

# Arista only
docker exec -e ANSIBLE_CONFIG=/workspace/ansible/ansible.cfg netbox-automation \
  ansible-playbook /workspace/ansible/playbooks/sync_physical_to_netbox.yml \
  --limit arista_physical

# Cisco only
docker exec -e ANSIBLE_CONFIG=/workspace/ansible/ansible.cfg netbox-automation \
  ansible-playbook /workspace/ansible/playbooks/sync_physical_to_netbox.yml \
  --limit cisco_physical
```

Same reachability / serial / version logic as the cEOS playbook. Log: `Docker/logs/ansible/physical_sync.log`

**Run both sync playbooks from VS Code:** Terminal → Run Task → `Ansible: Sync cEOS to Netbox` or `Ansible: Sync Physical Devices to Netbox`

---

#### Example: Query Netbox Inventory
```yaml
---
- name: Get Devices from Netbox
  hosts: localhost
  gather_facts: no
  
  tasks:
    - name: Query Netbox API
      uri:
        url: "{{ lookup('env', 'NETBOX_URL') }}/api/dcim/devices/"
        headers:
          Authorization: "Token {{ lookup('env', 'NETBOX_API_TOKEN') }}"
        validate_certs: no
      register: devices
    
    - name: Display devices
      debug:
        msg: "{{ devices.json.count }} devices found"
```

**Run from host:**
```bash
docker exec netbox-automation ansible-playbook ansible/playbooks/query_netbox.yml
```

**Run from dev container:**
```bash
# In VS Code terminal
ansible-playbook ansible/playbooks/query_netbox.yml
```

### 🛠️ Dev Container Development

**Open dev container:**
1. Cmd+Shift+P → "Dev Containers: Reopen in Container"
2. Automatic setup of Python 3.11, Ansible, all dependencies
3. VS Code extensions: Python, Ansible, Black formatter, GitLens

**Development workflow:**
```bash
# In dev container terminal
python python/scripts/my_script.py          # Run script
black python/scripts/                        # Auto-format
pylint python/scripts/my_script.py          # Lint check
pytest python/tests/                        # Run tests
ansible-playbook ansible/playbooks/demo.yml # Run playbooks
git push origin main                        # Commit changes
```

**Full debugging support:**
- Python breakpoints (F9)
- Step through code (F10/F11)
- Variable inspection
- Watch expressions

See **[DEV_CONTAINER.md](DEV_CONTAINER.md)** for complete dev container guide.

## Environment Configuration

**Configuration file:** `Docker/.env`

Available variables in all containers:
```
NETBOX_URL=http://netbox:8080           # Internal container endpoint
NETBOX_API_TOKEN=<token>                # API authentication
NETBOX_ADMIN_PASSWORD=<password>        # Admin credentials
NETBOX_SECRET_KEY=<key>                 # Django secret key
API_TOKEN_PEPPERS=<peppers>             # Token encryption
DB_HOST=postgres                        # Database host
DB_NAME=netbox                          # Database name
REDIS_HOST=redis                        # Redis host
CEOS_SSH_USER=admin                     # cEOS SSH username
CEOS_SSH_PASSWORD=admin                 # cEOS SSH password
DEVICE_SSH_USER=admin                   # Physical device SSH username
DEVICE_SSH_PASSWORD=                    # Physical device SSH password (fill in)
DEVICE_SSH_ENABLE=                      # Cisco enable password (fill in; blank for Arista)
```

These are **automatically available** as environment variables in:
- Python scripts (via `os.getenv()`)
- Ansible playbooks (via `lookup('env', 'VAR_NAME')`)
- Dev container

## Troubleshooting

### Containers won't start
```bash
# Check Docker is running
docker ps

# View logs
docker compose logs netbox

# Restart everything
docker compose down
docker compose up -d
```

### Can't access http://localhost:8000
```bash
# Check containers are running
docker compose ps

# Verify port 8000 is listening
lsof -i :8000

# Check netbox health
docker compose logs netbox | tail -20
```

### Python scripts can't reach Netbox
```bash
# Test connectivity from automation container
docker exec netbox-automation curl http://netbox:8080/api/

# Verify environment variables
docker exec netbox-automation env | grep NETBOX
```

### Dev container won't start
```bash
# Rebuild the environment
Cmd+Shift+P → "Dev Containers: Rebuild Container"

# Or delete and restart
docker compose down
docker compose up -d automation
```

See **[DOCKER_TROUBLESHOOT.md](DOCKER_TROUBLESHOOT.md)** for detailed troubleshooting.

## Next Steps

1. ✅ **Docker setup complete** — Netbox is running
2. ✅ **Dev container configured** — Full IDE ready
3. ✅ **Arista cEOS running** — Virtual switch on Docker network
4. ✅ **Automation scripts ready** — Add devices, sync facts to Netbox
5. ✅ **Ansible playbooks ready** — cEOS + physical device sync with Netbox
6. 🔧 **Add custom fields** — Lifecycle tracking in Netbox
7. 🧪 **Test with real devices** — Fill in `DEVICE_SSH_PASSWORD` in `Docker/.env` and run physical sync
8. 📊 **Monitor & scale** — Production deployment
