---
name: netbox-infrastructure-management
description: Design and implement a network infrastructure lifecycle management system using Netbox for multi-vendor devices (Cisco, Arista, Fortinet) with dual-mode operation (offline simulated + online real devices) on Windows with Docker.
---

# Netbox Infrastructure Lifecycle Management Skill

## Architecture Overview

### Deployment Model
- **Host**: Windows machine with Docker Desktop
- **Netbox**: Docker container
- **Database**: PostgreSQL in Docker, persisted to Windows filesystem
- **Automation**: Python + Ansible containers
- **Container Network**: Internal Docker network (offline mode)
- **Physical Access**: Direct network connection to real devices (online mode)

### File Organization
```
Code/netbox/         → Netbox Docker setup + configurations
Code/python/         → Python automation scripts
Code/ansible/        → Ansible playbooks and roles
Docker/docker/         → Docker Compose orchestration files
logs/                → Application logs by component
Data/                → Persistent data (database, volumes)
config/              → Global configuration files
```

## Implementation Components

### 1. Netbox Container Setup
- **Service**: Netbox application
- **Backend**: PostgreSQL database
- **Volume Mounts**:
  - `Data/postgres/` ← PostgreSQL data
  - `logs/netbox/` ← Application logs
  - `Data/netbox/` ← Media uploads, configurations
- **Custom Fields**: EOS, Service dates, Service tags
- **API**: Expose for Python script integration

### 2. Python Container (Automation)
- **Purpose**: Device health checks, data polling, Netbox API updates
- **Features**:
  - Health monitoring (ping, SNMP, SSH reachability)
  - Device discovery and inventory sync
  - Netbox API integration (read/write device data)
  - Scheduled polling (cron-like)
- **Volume Mounts**:
  - `Code/python/scripts/` ← Script code
  - `logs/python/` ← Execution logs
  - `Data/volumes/` ← Data files (results, cache)

### 3. Ansible Container (Configuration Management)
- **Purpose**: Network device configuration, bulk updates
- **Features**:
  - Device configuration management
  - Playbook orchestration
  - Ansible roles for network tasks
  - Integration with Netbox inventory
- **Volume Mounts**:
  - `Code/ansible/` ← Playbooks, roles, inventory
  - `logs/ansible/` ← Execution logs

### 4. Networking Strategy

#### Offline Mode (Development)
- All containers on same internal Docker network
- EVE-NG (future) emulates physical devices
- Containers reach emulated devices via Docker network + EVE-NG bridge
- Ideal for testing scripts without affecting production

#### Online Mode (Production)
- Netbox container remains on Docker network
- Python/Ansible containers can reach real network devices
- Real devices on lab network or work environment
- Containers access devices via:
  - SSH (CLI commands, config management)
  - SNMP (device polling)
  - API (Netbox inventory queries)

## Key Design Decisions

1. **Docker Desktop** (not Linux VM): Simplifies setup; Docker Desktop manages Linux kernel
2. **Windows Filesystem Persistence**: Code, logs, data on Windows for easy access and backup
3. **docker compose** Orchestration: Single command to start/stop all services
4. **Shared Container Network** (Offline): All containers communicate via internal Docker network
5. **Custom Netbox Fields**: EOS, Service dates, Service tags for lifecycle tracking
6. **Python + Ansible Separation**: Python for automated polling; Ansible for config management

## Docker Compose Strategy

### Root docker-compose.yml
Orchestrates entire stack:
- Netbox service (with PostgreSQL backend)
- Python service
- Ansible service
- Volume definitions
- Network configuration

### Volume Mounts
```yaml
volumes:
  postgres_data: ./Data/postgres/
  netbox_data: ./Data/netbox/
  
services:
  netbox:
    volumes:
      - netbox_data:/app/data
      - ./logs/netbox/:/var/log/netbox/
  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data/
  python:
    volumes:
      - ./Code/python/:/app/scripts/
      - ./logs/python/:/app/logs/
  ansible:
    volumes:
      - ./Code/ansible/:/etc/ansible/
      - ./logs/ansible/:/var/log/ansible/
```

## Data Flow

### Offline Test Flow
1. EVE-NG emulates network devices
2. Python container discovers devices via SNMP/SSH
3. Python updates Netbox via API
4. Ansible container pulls inventory from Netbox
5. Ansible runs playbooks against emulated devices
6. Results logged to `logs/python/` and `logs/ansible/`

### Online Production Flow
1. Real devices exist on work network
2. Python container polls real devices (SNMP, SSH)
3. Python updates Netbox with current state
4. Ansible pulls production inventory from Netbox
5. Ansible applies configurations to real devices
6. Netbox becomes authoritative source of truth

## Lifecycle Management Fields

### Lifecycle Tracking (netbox-lifecycle plugin)
All lifecycle data is managed via the `netbox-lifecycle` plugin (DanSheps, Apache-2.0):
- **Hardware EOL/EOS**: Tracked at DeviceType level — applies model-wide (e.g. "Cisco ASR 1001-X EOL: 2026-01-01")
- **Support Contracts**: Start/end date per device, grouped as Active / Future / Expired
- **Licenses**: Assigned to Devices and Virtual Machines
- Custom fields (`eos`, `service_start_date`, `service_end_date`, `service_tags`) are replaced by the plugin

### Python Script Responsibilities
- Query plugin contract/EOL data via Netbox API (`pynetbox`)
- Monitor devices approaching contract expiry or EOL dates
- Sync contract metadata from external systems (CMDB, cost system)

## Testing Strategy

1. **Offline Testing**:
   - Use EVE-NG to simulate Cisco/Arista/Fortinet devices
   - Test Python scripts against simulated devices
   - Validate Netbox API integration
   - Test Ansible playbooks

2. **Online Testing**:
   - Run same scripts against real lab devices
   - Validate production readiness
   - Monitor performance and scaling
