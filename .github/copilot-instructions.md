# Netbox Infrastructure Lifecycle Management Lab

## Project Purpose
A dual-mode network infrastructure lifecycle management system using **Netbox** as the authoritative source of truth for multi-vendor devices (Cisco, Arista, Fortinet). Supports both **offline** (EVE-NG simulated) and **online** (real devices) operation.

## Stack
- **Netbox** — IPAM and device inventory (Docker container, http://localhost:8000)
- **PostgreSQL** — Netbox backend database (Docker container, data persisted to `Data/postgres/`)
- **Redis** — Netbox cache layer
- **Python 3.11** — Device health checks, SNMP/SSH polling, Netbox API automation
- **Ansible** — Network device configuration management, uses Netbox as dynamic inventory
- **Docker Desktop** (on macOS/Windows) — Orchestrates all containers via `Docker/docker-compose.yml`

## Folder Structure
```
Docker/             → docker-compose.yml (full stack)
Code/
  python/scripts/   → Python automation scripts
  ansible/          → Playbooks, roles, inventory
  netbox/plugins/   → Netbox plugin customizations
Data/
  postgres/         → PostgreSQL persistent data
  netbox/           → Netbox media/config data
logs/
  python/           → Python script logs
  ansible/          → Ansible execution logs
  netbox/           → Netbox application logs
config/             → Global config files
docs/               → Human-readable documentation
.github/
  skills/netbox-infrastructure-management/SKILL.md  → Full domain skill
  instructions/     → File-specific Copilot instructions
```

## Operational Modes
- **Offline**: EVE-NG emulates Cisco/Arista/Fortinet devices; all traffic stays on Docker network
- **Online**: Python/Ansible containers connect directly to real devices via SSH/SNMP

## Lifecycle Tracking (netbox-lifecycle plugin)
- **Hardware EOL/EOS** — Tracked at DeviceType level via `netbox-lifecycle` plugin (DanSheps)
- **Support Contracts** — Start/end date, Active/Future/Expired status, assigned per Device or VM
- **Licenses** — Assigned to Devices and Virtual Machines
- Custom fields (`eos`, `service_start_date`, `service_end_date`, `service_tags`) replaced by the plugin

## Key Conventions
- All credentials and env vars in `Docker/.env` — never hardcode secrets
- Python scripts interact with Netbox via the `pynetbox` REST API client
- Ansible inventory is pulled dynamically from Netbox
- Logs go to the appropriate `logs/<component>/` directory
- Docker commands are run from the `Docker/` directory: `docker compose up -d`

## Default Credentials (dev/lab only)
- Netbox admin: `admin / Cisco123!`
- Netbox URL: `http://localhost:8000`
