# 🚀 Phase 1 Quick Reference Card

## One-Command Startup

```bash
cd <PROJECT_ROOT>
docker compose -f Docker/docker-compose.yml up -d
```

## Access Netbox
```
http://localhost:8000
Username: admin
Password: (from .env file)
```

## Common Commands

| Command | Purpose |
|---------|---------|
| `docker compose -f Docker/docker-compose.yml up -d` | Start all services (background) |
| `docker compose -f Docker/docker-compose.yml ps` | Show container status |
| `docker compose -f Docker/docker-compose.yml logs -f netbox` | View Netbox logs |
| `docker compose -f Docker/docker-compose.yml down` | Stop all services |
| `docker compose -f Docker/docker-compose.yml restart netbox` | Restart Netbox |

## Files Modified
- ✅ `Docker/docker-compose.yml` — Docker orchestration
- ✅ `.env` — Environment configuration

## Data Locations
- **Database**: `Data/postgres/` — Lives on Windows
- **Logs**: `logs/netbox/` — Lives on Windows
- **Media**: `Data/netbox/` — Lives on Windows

## Next Steps
1. Edit `.env` with secure passwords (optional for testing)
2. Run startup command above
3. Wait 1-2 minutes
4. Visit http://localhost:8000
5. Follow PHASE_1_STARTUP.md for full guide

## Issues?
See "Common Issues & Solutions" in PHASE_1_STARTUP.md

---

**Ready to start? Run:**
```
docker compose -f Docker/docker-compose.yml up -d
```
