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
    # EOL/EOS at DeviceType level (model-wide hardware lifecycle)
    # Support Contracts (start/end date, Active/Future/Expired) assigned per device
    # service_tags tracked via the plugin's contract metadata
    "netbox_lifecycle": {
        "lifecycle_card_position": "right_page",   # Options: left_page, right_page, full_width_page
        "contract_card_position": "right_page",    # Options: left_page, right_page, full_width_page
    },

    # ── netbox_inventory ───────────────────────────────────────────────────
    # "netbox_inventory": {
    #     "used_status_name": "active",
    #     "stored_status_name": "offline",
    # },
}
