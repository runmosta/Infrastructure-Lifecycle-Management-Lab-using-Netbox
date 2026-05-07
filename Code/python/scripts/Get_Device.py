#!/usr/bin/env python3
"""Read device information from NetBox by device name.

Usage:
  python Get_Device.py
  python Get_Device.py --name mock-edge-01
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

import requests


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
            "Accept": "application/json",
            "Host": host_header,
        }
    )
    session.verify = False
    requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
    return session


def get_device_by_name(session: requests.Session, base_url: str, name: str) -> Optional[Dict[str, Any]]:
    response = session.get(f"{base_url}/dcim/devices/", params={"name": name}, timeout=30)
    response.raise_for_status()
    results = response.json().get("results", [])
    return results[0] if results else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Read device info from NetBox")
    parser.add_argument("--name", default="mock-edge-01", help="Device name")
    args = parser.parse_args()

    token = os.getenv("NETBOX_API_TOKEN")
    if not token:
        print("ERROR: NETBOX_API_TOKEN is missing in environment", file=sys.stderr)
        return 1

    base = build_base_url()
    session = session_with_auth(token)

    try:
        device = get_device_by_name(session, base, args.name)
        if not device:
            print(f"Device not found: {args.name}")
            return 0

        output = {
            "id": device.get("id"),
            "name": device.get("name"),
            "status": (device.get("status") or {}).get("value"),
            "site": (device.get("site") or {}).get("name"),
            "role": (device.get("role") or {}).get("name"),
            "manufacturer": ((device.get("device_type") or {}).get("manufacturer") or {}).get("name"),
            "model": (device.get("device_type") or {}).get("model"),
            "primary_ip4": (device.get("primary_ip4") or {}).get("address"),
            "serial": device.get("serial"),
        }

        print(json.dumps(output, indent=2))
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
