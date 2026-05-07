"""
NetBox Plugin Configuration
Loaded automatically by the netbox container at startup.
Add or remove plugins here and restart the container to apply.
"""

PLUGINS = [
    # Lifecycle: EoL / EoS date tracking on devices
    "netbox_lifecycle",

    # Physical inventory / asset tracking (uncomment to enable)
    # "netbox_inventory",
]

PLUGINS_CONFIG = {
    # ── netbox_lifecycle ───────────────────────────────────────────────────
    "netbox_lifecycle": {
        # Default notice days before EoL/EoS to flag devices as "warning"
        "hw_eol_notice_days": 365,
        "sw_eol_notice_days": 180,
    },

    # ── netbox_inventory ───────────────────────────────────────────────────
    # "netbox_inventory": {
    #     "used_status_name": "active",
    #     "stored_status_name": "offline",
    # },
}
