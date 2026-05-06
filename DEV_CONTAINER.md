# Dev Container Setup Guide

## What is Included?

The `.devcontainer/devcontainer.json` provides a complete development environment for the Netbox Infrastructure Lab automation tasks.

### Pre-installed Tools
- **Python 3.11** with pip, setuptools, wheel
- **Ansible 2.19.9** - Infrastructure automation framework
- **Dependencies**: netaddr, jinja2, pyyaml, requests
- **Code Quality**: black (formatter), pylint (linter), pytest (testing)
- **Git**: Full git support with SSH key access
- **Docker**: Docker-in-Docker for container operations

### VS Code Extensions
- **Python**: Full language support, debugging, linting
- **Pylance**: Advanced Python type checking
- **Ansible**: YAML/playbook syntax highlighting and validation
- **Black Formatter**: Code formatting on save
- **GitLens**: Git history and blame annotations
- **Makefile Tools**: Run build/test tasks

### Environment Setup

All configuration is automatically applied when you open the container:

```json
PYTHONUNBUFFERED=1          # Real-time output logging
PYTHONDONTWRITEBYTECODE=1   # Skip .pyc generation
NETBOX_URL=http://netbox:8080
NETBOX_API_TOKEN=<from .env>
NETBOX_ADMIN_PASSWORD=<from .env>
```

### Mounted Directories

| Host Path | Container Path | Purpose |
|-----------|------------------|---------|
| `~/.ssh` | `/root/.ssh` | SSH keys for git operations (read-only) |
| `~/.config/ansible` | `/root/.ansible` | Ansible configuration cache |
| `Code/ansible` | `/workspace/ansible` | Ansible playbooks |
| `Code/python/scripts` | `/workspace/python` | Python automation scripts |
| `Docker/logs/ansible` | Shared logs | Execution logs |
| `Docker/.env` | `/workspace/.env` | Environment configuration |

### Port Forwarding

- **8000**: Netbox web UI (from Docker host)
- **8080**: Netbox API (internal container)

## How to Use

### Option 1: Reopen in Dev Container (Recommended)

1. In VS Code, press **Cmd+Shift+P**
2. Type "Dev Containers: Reopen in Container"
3. Wait for the environment to initialize
4. Terminal automatically opens in `/workspace`

### Option 2: Attach to Running Container

If the container is already running:

1. Press **Cmd+Shift+P**
2. Type "Dev Containers: Attach to Running Container"
3. Select `netbox-automation`

### Option 3: Command Line Setup

```bash
# Build and open in the dev container
docker run -it --rm \
  -v $(pwd):/workspace \
  -v ~/.ssh:/root/.ssh:ro \
  -v ~/.config/ansible:/root/.ansible \
  -w /workspace \
  python:3.11-slim bash
```

## Working with Python Scripts

### Example: Query Netbox Devices

Create `Code/python/scripts/get_devices.py`:

```python
#!/usr/bin/env python3
"""Query Netbox devices via API"""

import os
import requests

# Disable SSL warnings (safe for lab)
requests.packages.urllib3.disable_warnings()

url = os.getenv("NETBOX_URL") + "/api/dcim/devices/"
token = os.getenv("NETBOX_API_TOKEN")

response = requests.get(
    url,
    headers={"Authorization": f"Token {token}"},
    verify=False
)

devices = response.json()
print(f"Total devices: {devices.get('count', 0)}")

for device in devices.get("results", []):
    print(f"  - {device['name']}: {device.get('device_type', {}).get('model', 'N/A')}")
```

Run it:
```bash
docker exec netbox-automation python python/scripts/get_devices.py
# Or from within the container:
python python/scripts/get_devices.py
```

## Working with Ansible Playbooks

### Example: Simple Inventory Query

Create `Code/ansible/playbooks/netbox_demo.yml`:

```yaml
---
- name: Query Netbox Devices
  hosts: localhost
  gather_facts: no
  vars:
    netbox_url: "{{ lookup('env', 'NETBOX_URL') }}"
    netbox_token: "{{ lookup('env', 'NETBOX_API_TOKEN') }}"
  
  tasks:
    - name: Get devices from Netbox
      uri:
        url: "{{ netbox_url }}/api/dcim/devices/"
        method: GET
        headers:
          Authorization: "Token {{ netbox_token }}"
        validate_certs: no
        return_content: yes
      register: devices

    - name: Display device count
      debug:
        msg: "Total devices: {{ devices.json.count }}"
```

Run it:
```bash
docker exec netbox-automation ansible-playbook ansible/playbooks/netbox_demo.yml
# Or from within the container:
ansible-playbook ansible/playbooks/netbox_demo.yml
```

## Development Workflow

### 1. Edit and Test Python Code

```bash
# In VS Code terminal (inside container)
python python/scripts/my_script.py

# Or with debugging
python -m pdb python/scripts/my_script.py
```

### 2. Format and Lint

```bash
# Format with Black
black python/scripts/

# Check with Pylint
pylint python/scripts/my_script.py

# Run tests
pytest python/tests/
```

### 3. Git Operations

All git commands work normally (SSH keys are mounted):

```bash
git add .
git commit -m "Add automation script"
git push origin main
```

## Troubleshooting

### Container won't start
```bash
# Check Docker daemon is running
docker ps

# Rebuild the image
docker compose down && docker compose up -d automation
```

### Python dependencies missing
```bash
# From container terminal
pip install <package_name>

# Make it permanent: Add to postCreateCommand in devcontainer.json
```

### Can't access Netbox API
```bash
# Test connectivity from container
curl -s http://netbox:8080/api/ | head -20

# Verify environment variables
env | grep NETBOX
```

### SSH keys not available
```bash
# Verify SSH key mounting
ls -la ~/.ssh/
ssh -T git@github.com  # Test git SSH access
```

## Tips & Tricks

1. **Use environment variables** in all scripts - they're loaded from `.env` automatically
2. **SSH keys are read-only** - commits must be pushed, not done in container
3. **Logs are persistent** - check `Docker/logs/ansible/` for execution history
4. **Ansible playbooks** can be run ad-hoc or scheduled via cron in the container
5. **Python virtual environments** not needed - container IS the isolated environment

## Next Steps

- Create your first automation script in `Code/python/scripts/`
- Develop Ansible playbooks in `Code/ansible/playbooks/`
- Use VS Code debugging to step through code
- Push changes to GitHub when ready
