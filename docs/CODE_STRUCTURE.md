# Project Folder Structure

```
Netbox/
├── Code/                          # Source code and configurations
│   ├── netbox/                    # Netbox application files
│   │   ├── docker-compose.yml     # Netbox + PostgreSQL orchestration
│   │   ├── .env                   # Netbox environment variables
│   │   └── plugins/               # Netbox plugins directory
│   ├── python/                    # Python automation scripts
│   │   ├── scripts/               # Health checks, polling, API updates
│   │   ├── requirements.txt       # Python dependencies
│   │   └── Dockerfile             # Python container image
│   ├── ansible/                   # Ansible playbooks
│   │   ├── playbooks/             # Playbook collection
│   │   ├── inventory/             # Device inventory files
│   │   ├── roles/                 # Ansible roles
│   │   └── ansible.cfg            # Ansible configuration
│   └── docker/                    # Docker compose and config files
│       ├── docker-compose.yml     # Full stack orchestration
│       ├── docker-compose.override.yml  # Local dev overrides
│       └── .dockerignore          # Docker build exclusions
├── logs/                          # Application logs
│   ├── netbox/                    # Netbox logs
│   ├── python/                    # Python script logs
│   └── ansible/                   # Ansible execution logs
├── Data/                          # Persistent data
│   ├── postgres/                  # PostgreSQL data volume
│   ├── netbox/                    # Netbox data (configs, media)
│   └── volumes/                   # Named Docker volumes mount points
├── config/                        # Configuration files
│   ├── netbox.config.yml          # Netbox settings
│   ├── python.config.yml          # Python scripts settings
│   └── ansible.config.yml         # Ansible settings
├── READ.md                        # Project overview and setup
├── SKILL.md                       # Skill definitions and procedures
├── CODE_STRUCTURE.md              # This file
└── docker-compose.yml             # Root orchestration file
```

## Directory Purposes

### Code/
All source code, scripts, and configurations separated by component.

- **netbox/**: Netbox-specific Docker setup and plugins
- **python/**: Python scripts for automation (device polling, health checks, API calls)
- **ansible/**: Ansible playbooks and roles for network device configuration
- **docker/**: Docker Compose files for full stack orchestration

### logs/
Runtime logs organized by component for easy troubleshooting.

- **netbox/**: Netbox application logs
- **python/**: Python script execution logs
- **ansible/**: Ansible run logs

### Data/
Persistent data persisted to Windows filesystem via Docker volumes.

- **postgres/**: PostgreSQL database files (Netbox backend)
- **netbox/**: Netbox application data (media uploads, configs)
- **volumes/**: Named Docker volume mount points

### config/
Global configuration files for the entire infrastructure.

## Volume Mounts (Docker to Windows)

```
Docker Container → Windows Path (Mounted)
/app/data → Data/volumes/
/var/log/netbox → logs/netbox/
/var/log/python → logs/python/
/var/log/ansible → logs/ansible/
/var/lib/postgresql → Data/postgres/
/app/scripts → Code/python/scripts/
```

## How to Use

1. Place Netbox Docker setup in `Code/netbox/`
2. Place Python scripts in `Code/python/scripts/`
3. Place Ansible playbooks in `Code/ansible/playbooks/`
4. Configure docker-compose.yml to mount Windows paths
5. Logs and data automatically persist to Windows filesystem
6. View logs in `logs/` directory on Windows
7. Query database in `Data/postgres/` via Netbox UI or direct connection
