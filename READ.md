# Infrastructure Lifecycle Management Lab

## Overview
A dual-mode network infrastructure management system using **Netbox** for inventory and IPAM, supporting both offline (simulated) and online (real device) operations on your Windows machine.

## Vision
Use Netbox as a **centralized lifecycle management system** for multi-vendor network devices (Cisco, Arista, Fortinet routers/switches/firewalls) with custom tracking fields and automated data enrichment.

## Applications & Technologies
- **Visual Studio Code** (✓ installed) — Development IDE
- **Docker Desktop** (✓ installed) — Container runtime
- **Netbox** (Docker container) — IPAM + device inventory + API
- **PostgreSQL** (Docker container) — Netbox backend database
- **Python** (Docker container) — Automation scripts
- **Ansible** (Docker container) — Configuration management
- **Git** (✓ installed) — Version control
- **EVE-NG** (future) — Network device emulation

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
Netbox/
├── Code/           # Source code, Dockerfiles, scripts
├── logs/           # Application logs (netbox, python, ansible)
├── Data/           # Database and persistent data
└── config/         # Configuration files
```
See `CODE_STRUCTURE.md` for detailed structure.

## Next Steps
1. Create docker-compose.yml for Netbox + PostgreSQL
2. Create custom device fields (EOS, Service dates, tags)
3. Write Python scripts to read/update device fields via API
4. Create Python script for device health monitoring
5. Create Ansible playbooks for device management
6. Test with EVE-NG emulated devices (offline)
7. Test with real devices (online)
