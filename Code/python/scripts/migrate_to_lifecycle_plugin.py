#!/usr/bin/env python3
"""Migrate custom lifecycle fields to netbox-lifecycle plugin.

Reads existing custom fields (eos, service_start_date, service_end_date,
service_tags) from each Device, creates a SupportContract + SupportContractAssignment
via the netbox-lifecycle plugin, then removes the old custom fields.

Plugin API structure (DanSheps/netbox-lifecycle):
  vendor        → the contract vendor (created once as "Migrated")
  supportcontract → the contract record (vendor, contract_id, start, end)
  supportcontractassignment → links contract to a device

Usage:
  python migrate_to_lifecycle_plugin.py              # dry-run (no changes)
  python migrate_to_lifecycle_plugin.py --apply      # apply changes
  python migrate_to_lifecycle_plugin.py --apply --delete-custom-fields
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

import requests

CUSTOM_FIELDS = ["eos", "service_start_date", "service_end_date", "service_tags"]
VENDOR_NAME = "Migrated"


def build_base_url() -> str:
    base = os.getenv("NETBOX_URL", "http://netbox:8080").rstrip("/")
    if not base.endswith("/api"):
        base = f"{base}/api"
    return base


def session_with_auth(token: str) -> requests.Session:
    session = requests.Session()
    host_header = os.getenv("NETBOX_HOST_HEADER", "localhost:8000")
    session.headers.update(
        {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Host": host_header,
        }
    )
    session.verify = False
    requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
    return session


def paginate(session: requests.Session, url: str) -> List[Dict[str, Any]]:
    """Fetch all pages from a Netbox list endpoint."""
    results = []
    while url:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        results.extend(data.get("results", []))
        url = data.get("next")
    return results


def get_or_create_vendor(
    session: requests.Session, base: str, name: str, apply: bool
) -> Optional[int]:
    """Get or create a Vendor in the lifecycle plugin."""
    url = f"{base}/plugins/lifecycle/vendor/"
    resp = session.get(url, params={"name": name}, timeout=30)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if results:
        return results[0]["id"]
    if not apply:
        print(f"  [dry-run] Would create vendor: {name}")
        return None
    create = session.post(url, data=json.dumps({"name": name}), timeout=30)
    create.raise_for_status()
    vendor = create.json()
    print(f"  Created vendor: {vendor['name']} (id={vendor['id']})")
    return vendor["id"]


def create_support_contract(
    session: requests.Session,
    base: str,
    device: Dict[str, Any],
    vendor_id: Optional[int],
    apply: bool,
) -> Optional[int]:
    """Create a SupportContract from the device's custom fields.

    Returns the contract id if created, else None.
    """
    cf = device.get("custom_fields") or {}
    start = cf.get("service_start_date")
    end = cf.get("service_end_date")
    tags = cf.get("service_tags") or ""
    device_name = device["name"]

    if not start and not end:
        print(f"  Skipping {device_name} — no service_start_date or service_end_date set")
        return None

    contract_id_str = f"MIGRATED-{device_name}"
    comments = f"Migrated service_tags: {tags}" if tags else "Migrated from custom fields"

    if not apply:
        print(
            f"  [dry-run] Would create contract '{contract_id_str}': "
            f"start={start} end={end} tags={tags}"
        )
        return None

    payload: Dict[str, Any] = {
        "vendor": vendor_id,
        "contract_id": contract_id_str,
        "comments": comments,
    }
    if start:
        payload["start"] = start
    if end:
        payload["end"] = end

    url = f"{base}/plugins/lifecycle/supportcontract/"
    resp = session.post(url, data=json.dumps(payload), timeout=30)
    if resp.status_code == 201:
        contract = resp.json()
        print(f"  Created contract '{contract_id_str}' (id={contract['id']})")
        return contract["id"]
    print(
        f"  ERROR creating contract for {device_name}: {resp.status_code} {resp.text}",
        file=sys.stderr,
    )
    return None


def create_contract_assignment(
    session: requests.Session,
    base: str,
    contract_id: int,
    device: Dict[str, Any],
    apply: bool,
) -> None:
    """Assign a SupportContract to a device."""
    device_name = device["name"]
    if not apply:
        print(f"  [dry-run] Would assign contract to device {device_name}")
        return

    payload = {"contract": contract_id, "device": device["id"]}
    url = f"{base}/plugins/lifecycle/supportcontractassignment/"
    resp = session.post(url, data=json.dumps(payload), timeout=30)
    if resp.status_code == 201:
        print(f"  Assigned contract to {device_name}")
    else:
        print(
            f"  ERROR assigning contract to {device_name}: {resp.status_code} {resp.text}",
            file=sys.stderr,
        )


def clear_custom_fields(
    session: requests.Session,
    base: str,
    device: Dict[str, Any],
    apply: bool,
) -> None:
    """Null out the old lifecycle custom fields on a device."""
    device_name = device["name"]
    patch = {"custom_fields": {f: None for f in CUSTOM_FIELDS}}

    if not apply:
        print(f"  [dry-run] Would clear custom fields on {device_name}")
        return

    url = f"{base}/dcim/devices/{device['id']}/"
    resp = session.patch(url, data=json.dumps(patch), timeout=30)
    if resp.status_code == 200:
        print(f"  Cleared custom fields on {device_name}")
    else:
        print(
            f"  ERROR clearing fields on {device_name}: {resp.status_code} {resp.text}",
            file=sys.stderr,
        )


def delete_custom_field_definitions(
    session: requests.Session, base: str, apply: bool
) -> None:
    """Delete the old custom field definitions from Netbox entirely."""
    url = f"{base}/extras/custom-fields/"
    for field_name in CUSTOM_FIELDS:
        resp = session.get(url, params={"name": field_name}, timeout=30)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            print(f"  Custom field '{field_name}' not found — already removed")
            continue
        cf_id = results[0]["id"]
        if not apply:
            print(f"  [dry-run] Would delete custom field definition: {field_name}")
            continue
        del_resp = session.delete(f"{url}{cf_id}/", timeout=30)
        if del_resp.status_code == 204:
            print(f"  Deleted custom field definition: {field_name}")
        else:
            print(
                f"  ERROR deleting '{field_name}': {del_resp.status_code} {del_resp.text}",
                file=sys.stderr,
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate lifecycle custom fields to netbox-lifecycle plugin")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument(
        "--delete-custom-fields",
        action="store_true",
        help="Also delete the old custom field definitions from Netbox (use after verifying migration)",
    )
    args = parser.parse_args()

    token = os.getenv("NETBOX_API_TOKEN")
    if not token:
        print("ERROR: NETBOX_API_TOKEN is missing in environment", file=sys.stderr)
        return 1

    base = build_base_url()
    session = session_with_auth(token)
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== Lifecycle migration [{mode}] ===")
    print(f"Netbox: {base}\n")

    # 1. Ensure a default vendor exists for migrated contracts
    vendor_id = get_or_create_vendor(session, base, VENDOR_NAME, args.apply)

    # 2. Fetch all devices
    print("Fetching all devices...")
    devices = paginate(session, f"{base}/dcim/devices/?limit=100")
    print(f"Found {len(devices)} devices\n")

    # 3. Migrate each device
    for device in devices:
        print(f"Device: {device['name']}")
        contract_id = create_support_contract(session, base, device, vendor_id, args.apply)
        if contract_id:
            create_contract_assignment(session, base, contract_id, device, args.apply)
        if args.apply:
            clear_custom_fields(session, base, device, args.apply)
        print()

    # 4. Optionally delete custom field definitions
    if args.delete_custom_fields:
        print("=== Deleting custom field definitions ===")
        delete_custom_field_definitions(session, base, args.apply)

    if not args.apply:
        print("\nDry-run complete — no changes made. Re-run with --apply to migrate.")
    else:
        print("\nMigration complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
