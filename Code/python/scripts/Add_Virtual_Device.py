#!/usr/bin/env python3
"""Add a virtual Arista switch to Netbox as a Virtual Machine.

Virtual network devices (cEOS, vEOS-lab, etc.) are modelled under
Netbox's Virtualization module rather than DCIM, because they have no
physical chassis.

Usage:
  python Add_Virtual_Device.py
  python Add_Virtual_Device.py --name arista-ceos-01 --site LAB-OSL --cluster "Lab Docker"
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, Optional

import requests


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def get_first(
    session: requests.Session, endpoint: str, params: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    response = session.get(endpoint, params=params, timeout=30)
    response.raise_for_status()
    results = response.json().get("results", [])
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
    resp = session.post(endpoint, data=json.dumps(payload), timeout=30)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register a virtual Arista switch in Netbox (Virtualization module)"
    )
    parser.add_argument("--name", default="arista-ceos-01", help="VM name")
    parser.add_argument("--site", default="LAB-OSL", help="Site name")
    parser.add_argument(
        "--cluster", default="Lab Docker", help="Cluster name (e.g. 'Lab Docker')"
    )
    parser.add_argument(
        "--cluster-type", default="Docker", help="Cluster type (e.g. 'Docker', 'EVE-NG')"
    )
    parser.add_argument("--role", default="leaf-switch", help="Device role")
    parser.add_argument(
        "--platform", default="EOS", help="Platform / OS (e.g. EOS, IOS-XE)"
    )
    parser.add_argument("--vcpus", type=int, default=2, help="vCPU count")
    parser.add_argument("--memory", type=int, default=2048, help="Memory in MB")
    parser.add_argument("--disk", type=int, default=4096, help="Disk in MB")
    parser.add_argument(
        "--interface", default="Management0", help="Primary interface name"
    )
    parser.add_argument("--ip", default="", help="Management IP (CIDR, e.g. 10.0.0.10/24)")
    args = parser.parse_args()

    token = os.getenv("NETBOX_API_TOKEN")
    if not token:
        print("ERROR: NETBOX_API_TOKEN missing from environment", file=sys.stderr)
        return 1

    base = build_base_url()
    session = session_with_auth(token)

    try:
        # 1. Site
        site = get_or_create(
            session,
            f"{base}/dcim/sites/",
            {"slug": slugify(args.site)},
            {"name": args.site, "slug": slugify(args.site), "status": "active"},
        )
        print(f"Site: {site['name']} (id={site['id']})")

        # 2. Cluster type (Docker / EVE-NG / etc.)
        cluster_type = get_or_create(
            session,
            f"{base}/virtualization/cluster-types/",
            {"slug": slugify(args.cluster_type)},
            {"name": args.cluster_type, "slug": slugify(args.cluster_type)},
        )
        print(f"Cluster type: {cluster_type['name']} (id={cluster_type['id']})")

        # 3. Cluster
        cluster = get_or_create(
            session,
            f"{base}/virtualization/clusters/",
            {"name": args.cluster},
            {
                "name": args.cluster,
                "type": cluster_type["id"],
                "site": site["id"],
                "status": "active",
            },
        )
        print(f"Cluster: {cluster['name']} (id={cluster['id']})")

        # 4. Role
        role = get_or_create(
            session,
            f"{base}/dcim/device-roles/",
            {"slug": slugify(args.role)},
            {"name": args.role, "slug": slugify(args.role), "color": "00aa00", "vm_role": True},
        )
        print(f"Role: {role['name']} (id={role['id']})")

        # 5. Platform (optional but useful for Ansible)
        platform = get_or_create(
            session,
            f"{base}/dcim/platforms/",
            {"slug": slugify(args.platform)},
            {"name": args.platform, "slug": slugify(args.platform)},
        )
        print(f"Platform: {platform['name']} (id={platform['id']})")

        # 6. Virtual Machine — skip if already exists
        existing_vm = get_first(
            session, f"{base}/virtualization/virtual-machines/", {"name": args.name}
        )
        if existing_vm:
            print(f"\nVM already exists: {existing_vm['name']} (id={existing_vm['id']})")
            return 0

        vm_payload: Dict[str, Any] = {
            "name": args.name,
            "cluster": cluster["id"],
            "site": site["id"],
            "role": role["id"],
            "platform": platform["id"],
            "status": "active",
            "vcpus": args.vcpus,
            "memory": args.memory,
            "disk": args.disk,
        }
        vm_resp = session.post(
            f"{base}/virtualization/virtual-machines/",
            data=json.dumps(vm_payload),
            timeout=30,
        )
        vm_resp.raise_for_status()
        vm = vm_resp.json()
        print(f"\nCreated virtual machine:")
        print(f"  id      : {vm['id']}")
        print(f"  name    : {vm['name']}")
        print(f"  cluster : {vm['cluster']['name']}")
        print(f"  site    : {vm['site']['name']}")
        print(f"  role    : {vm['role']['name']}")
        print(f"  platform: {vm['platform']['name']}")
        print(f"  vCPUs   : {vm['vcpus']}")
        print(f"  Memory  : {vm['memory']} MB")

        # 7. Management interface
        iface_payload = {
            "virtual_machine": vm["id"],
            "name": args.interface,
            "type": "virtual",
        }
        iface_resp = session.post(
            f"{base}/virtualization/interfaces/",
            data=json.dumps(iface_payload),
            timeout=30,
        )
        iface_resp.raise_for_status()
        iface = iface_resp.json()
        print(f"  interface: {iface['name']} (id={iface['id']})")

        # 8. Assign IP if provided
        if args.ip:
            ip_payload = {
                "address": args.ip,
                "status": "active",
                "assigned_object_type": "virtualization.vminterface",
                "assigned_object_id": iface["id"],
            }
            ip_resp = session.post(
                f"{base}/ipam/ip-addresses/",
                data=json.dumps(ip_payload),
                timeout=30,
            )
            ip_resp.raise_for_status()
            ip_obj = ip_resp.json()
            print(f"  IP address: {ip_obj['address']} (id={ip_obj['id']})")

            # Set as primary IPv4 on the VM
            session.patch(
                f"{base}/virtualization/virtual-machines/{vm['id']}/",
                data=json.dumps({"primary_ip4": ip_obj["id"]}),
                timeout=30,
            ).raise_for_status()
            print("  Primary IP set.")

        return 0

    except requests.HTTPError as exc:
        body = exc.response.text if exc.response is not None else str(exc)
        print(f"HTTP error: {body}", file=sys.stderr)
        return 2
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
