#!/usr/bin/env python3
"""Create a mock device in NetBox using API token auth.

Usage:
  python Add_Device.py
  python Add_Device.py --name mock-edge-02 --site LAB-OSL
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, Optional

import requests


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


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


def get_first(session: requests.Session, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    response = session.get(endpoint, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])
    return results[0] if results else None


def get_or_create(
    session: requests.Session,
    endpoint: str,
    lookup_params: Dict[str, Any],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    existing = get_first(session, endpoint, lookup_params)
    if existing:
        return existing

    create_response = session.post(endpoint, data=json.dumps(payload), timeout=30)
    create_response.raise_for_status()
    return create_response.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create mock device data in NetBox")
    parser.add_argument("--name", default="mock-edge-01", help="Device name")
    parser.add_argument("--site", default="LAB-OSL", help="Site name")
    parser.add_argument("--role", default="edge-router", help="Device role")
    parser.add_argument("--manufacturer", default="Cisco", help="Manufacturer name")
    parser.add_argument("--model", default="ISR-4331", help="Device model")
    args = parser.parse_args()

    token = os.getenv("NETBOX_API_TOKEN")
    if not token:
        print("ERROR: NETBOX_API_TOKEN is missing in environment", file=sys.stderr)
        return 1

    base = build_base_url()
    session = session_with_auth(token)

    try:
        manufacturer = get_or_create(
            session,
            f"{base}/dcim/manufacturers/",
            {"slug": slugify(args.manufacturer)},
            {"name": args.manufacturer, "slug": slugify(args.manufacturer)},
        )

        role = get_or_create(
            session,
            f"{base}/dcim/device-roles/",
            {"slug": slugify(args.role)},
            {
                "name": args.role,
                "slug": slugify(args.role),
                "color": "00aa00",
            },
        )

        site = get_or_create(
            session,
            f"{base}/dcim/sites/",
            {"slug": slugify(args.site)},
            {
                "name": args.site,
                "slug": slugify(args.site),
                "status": "active",
            },
        )

        device_type = get_or_create(
            session,
            f"{base}/dcim/device-types/",
            {
                "slug": slugify(args.model),
                "manufacturer_id": manufacturer["id"],
            },
            {
                "manufacturer": manufacturer["id"],
                "model": args.model,
                "slug": slugify(args.model),
            },
        )

        existing_device = get_first(
            session,
            f"{base}/dcim/devices/",
            {"name": args.name},
        )
        if existing_device:
            print(f"Device already exists: {existing_device['name']} (id={existing_device['id']})")
            return 0

        payload = {
            "name": args.name,
            "device_type": device_type["id"],
            "role": role["id"],
            "site": site["id"],
            "status": "active",
        }

        create_resp = session.post(f"{base}/dcim/devices/", data=json.dumps(payload), timeout=30)
        create_resp.raise_for_status()
        device = create_resp.json()

        print("Created device successfully")
        print(f"  id: {device['id']}")
        print(f"  name: {device['name']}")
        print(f"  site: {device['site']['name']}")
        print(f"  role: {device['role']['name']}")
        print(f"  type: {device['device_type']['model']}")
        return 0

    except requests.HTTPError as exc:
        response_text = exc.response.text if exc.response is not None else str(exc)
        print(f"HTTP error: {response_text}", file=sys.stderr)
        return 2
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
