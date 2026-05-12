#!/usr/bin/env python3
"""Update device dates in Netbox from a vendor CSV file.

Looks up each device by serial number and updates (step 1 — dates only):
  - Hardware EOL date  → HardwareLifecycle on the device's DeviceType
  - Service start/end  → SupportContract + SupportContractAssignment

Supported vendors: arista, cisco, fortinet
Default CSV path:   Data/inputs/{vendor}_devices.csv

Usage:
  python Update_Vendor.py --vendor arista
  python Update_Vendor.py --vendor arista --dry-run
  python Update_Vendor.py --vendor arista --csv /path/to/custom.csv
"""

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# ---------------------------------------------------------------------------
# Paths — env var takes priority; otherwise walk up from the script location
# until a Data/inputs sibling is found (works on host and inside Docker).
# ---------------------------------------------------------------------------
def _resolve_inputs_dir() -> Path:
    env = os.getenv("INPUTS_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent
    for _ in range(6):
        candidate = here / "Data" / "inputs"
        if candidate.is_dir():
            return candidate
        here = here.parent
    # Final fallback: /workspace/data/inputs (Docker convention)
    return Path("/workspace/data/inputs")


DATA_INPUTS_DIR = _resolve_inputs_dir()
LOG_FILE = Path(os.getenv("LOG_DIR", "/workspace/logs")) / "update_vendor.log"

# ---------------------------------------------------------------------------
# Vendor configuration
# ---------------------------------------------------------------------------
VENDOR_MAP: Dict[str, str] = {
    "arista": "Arista",
    "cisco": "Cisco",
    "fortinet": "Fortinet",
}

# Maps logical field names to the actual CSV column headers per vendor.
# Add a new dict here when onboarding a new vendor.
COLUMN_MAPS: Dict[str, Dict[str, str]] = {
    "arista": {
        "serial":        "SERIAL NUMBER",
        "eol_date":      "EOL DATE",
        "service_start": "SERVICE START DATE",
        "service_end":   "SERVICE END DATE",
    },
}


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def setup_logging(log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("update_vendor")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
        logger.addHandler(fh)
    return logger


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------
def parse_vendor_date(value: str) -> Optional[str]:
    """Convert M/D/YY or MM/DD/YY → YYYY-MM-DD. Returns None if blank/invalid."""
    value = value.strip()
    if not value or value.upper() == "N/A":
        return None
    try:
        return datetime.strptime(value, "%m/%d/%y").strftime("%Y-%m-%d")
    except ValueError:
        pass
    try:
        # Accept ISO format if already correct
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Netbox session
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Netbox lookups
# ---------------------------------------------------------------------------
def find_device_by_serial(
    session: requests.Session, base: str, serial: str
) -> Optional[Dict[str, Any]]:
    resp = session.get(f"{base}/dcim/devices/", params={"serial": serial}, timeout=30)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None


def get_or_create_vendor(
    session: requests.Session,
    base: str,
    name: str,
    dry_run: bool,
    logger: logging.Logger,
) -> Optional[int]:
    url = f"{base}/plugins/lifecycle/vendor/"
    resp = session.get(url, params={"name": name}, timeout=30)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if results:
        return results[0]["id"]
    if dry_run:
        logger.info("[dry-run] Would create lifecycle vendor: %s", name)
        return None
    created = session.post(url, data=json.dumps({"name": name}), timeout=30)
    created.raise_for_status()
    vendor = created.json()
    logger.info("Created lifecycle vendor: %s (id=%s)", vendor["name"], vendor["id"])
    return vendor["id"]


# ---------------------------------------------------------------------------
# Date updates
# ---------------------------------------------------------------------------
def upsert_hardware_lifecycle(
    session: requests.Session,
    base: str,
    device_type_id: int,
    eol_date: str,
    dry_run: bool,
    logger: logging.Logger,
    device_name: str,
) -> None:
    """Create or update the HardwareLifecycle end_of_support date for a DeviceType."""
    url = f"{base}/plugins/lifecycle/hardwarelifecycle/"
    resp = session.get(url, params={"device_type_id": device_type_id}, timeout=30)
    resp.raise_for_status()
    results = resp.json().get("results", [])

    if dry_run:
        action = "update" if results else "create"
        logger.info(
            "[dry-run] Would %s HardwareLifecycle for device_type=%s: end_of_support=%s (%s)",
            action, device_type_id, eol_date, device_name,
        )
        return

    if results:
        record_id = results[0]["id"]
        patch_resp = session.patch(
            f"{url}{record_id}/",
            data=json.dumps({"end_of_support": eol_date}),
            timeout=30,
        )
        patch_resp.raise_for_status()
        logger.info("Updated HardwareLifecycle for %s: end_of_support=%s", device_name, eol_date)
    else:
        post_resp = session.post(
            url,
            data=json.dumps({
                "assigned_object_type": "dcim.devicetype",
                "assigned_object_id": device_type_id,
                "end_of_support": eol_date,
            }),
            timeout=30,
        )
        post_resp.raise_for_status()
        logger.info("Created HardwareLifecycle for %s: end_of_support=%s", device_name, eol_date)


def upsert_support_contract(
    session: requests.Session,
    base: str,
    device: Dict[str, Any],
    vendor_id: Optional[int],
    start: Optional[str],
    end: Optional[str],
    dry_run: bool,
    logger: logging.Logger,
) -> None:
    """Create or update SupportContract + assignment for a device."""
    if not start and not end:
        return

    device_id = device["id"]
    device_name = device["name"]

    # Check for existing assignment on this device
    assign_url = f"{base}/plugins/lifecycle/supportcontractassignment/"
    assign_resp = session.get(
        assign_url,
        params={"device_id": device_id},
        timeout=30,
    )
    assign_resp.raise_for_status()
    assignments = assign_resp.json().get("results", [])

    if assignments:
        # Patch the existing contract's dates
        existing_contract_id = assignments[0]["contract"]["id"]
        patch: Dict[str, Any] = {}
        if start:
            patch["start"] = start
        if end:
            patch["end"] = end
        if dry_run:
            logger.info(
                "[dry-run] Would update contract id=%s for %s: start=%s end=%s",
                existing_contract_id, device_name, start, end,
            )
            return
        patch_resp = session.patch(
            f"{base}/plugins/lifecycle/supportcontract/{existing_contract_id}/",
            data=json.dumps(patch),
            timeout=30,
        )
        patch_resp.raise_for_status()
        logger.info(
            "Updated contract id=%s for %s: start=%s end=%s",
            existing_contract_id, device_name, start, end,
        )
        return

    # No existing assignment — look up or create the contract, then assign
    if dry_run:
        logger.info(
            "[dry-run] Would create/find contract for %s: start=%s end=%s",
            device_name, start, end,
        )
        return

    # Look up an existing contract with the same contract_id to avoid duplicate errors
    contract_url = f"{base}/plugins/lifecycle/supportcontract/"
    existing_contracts = session.get(
        contract_url, params={"contract_id": device_name}, timeout=30
    )
    existing_contracts.raise_for_status()
    contract_results = existing_contracts.json().get("results", [])

    if contract_results:
        contract = contract_results[0]
        # Update dates on the existing contract
        patch: Dict[str, Any] = {}
        if start:
            patch["start"] = start
        if end:
            patch["end"] = end
        if patch:
            patch_resp = session.patch(
                f"{contract_url}{contract['id']}/",
                data=json.dumps(patch),
                timeout=30,
            )
            patch_resp.raise_for_status()
        logger.info("Found existing contract id=%s for %s, updating dates", contract["id"], device_name)
    else:
        contract_payload: Dict[str, Any] = {"contract_id": device_name}
        if vendor_id:
            contract_payload["vendor"] = vendor_id
        if start:
            contract_payload["start"] = start
        if end:
            contract_payload["end"] = end

        c_resp = session.post(
            contract_url,
            data=json.dumps(contract_payload),
            timeout=30,
        )
        c_resp.raise_for_status()
        contract = c_resp.json()
        logger.info("Created contract '%s' (id=%s)", device_name, contract["id"])

    a_resp = session.post(
        assign_url,
        data=json.dumps({"contract": contract["id"], "device": device_id}),
        timeout=30,
    )
    a_resp.raise_for_status()
    logger.info("Assigned contract to %s", device_name)


STATUS_IMPORTED = "Imported"
STATUS_MISSING  = "Missing"
STATUS_ERROR    = "Error"
STATUS_COL      = "import_status"


# ---------------------------------------------------------------------------
# CSV loader / saver
# ---------------------------------------------------------------------------
def load_csv(csv_path: Path) -> List[Dict[str, str]]:
    """Read CSV, ensuring import_status column exists on every row."""
    # utf-8-sig strips Excel BOM if present
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        if STATUS_COL not in row:
            row[STATUS_COL] = ""
    return rows


def save_csv(csv_path: Path, rows: List[Dict[str, str]]) -> None:
    """Write rows back to the same CSV, preserving column order."""
    if not rows:
        return
    # Preserve original column order; add import_status at end if not present
    fieldnames = list(rows[0].keys())
    if STATUS_COL not in fieldnames:
        fieldnames.append(STATUS_COL)
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update device EOL and service contract dates from vendor CSV"
    )
    parser.add_argument(
        "--vendor",
        required=True,
        choices=list(VENDOR_MAP.keys()),
        help="Vendor name (arista, cisco, fortinet)",
    )
    parser.add_argument(
        "--csv",
        help="Override CSV file path (default: Data/inputs/{vendor}_devices.csv)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without modifying Netbox",
    )
    args = parser.parse_args()

    vendor: str = args.vendor
    manufacturer_name = VENDOR_MAP[vendor]
    csv_path = Path(args.csv) if args.csv else DATA_INPUTS_DIR / f"{vendor}_devices.csv"

    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        print(
            f"  Save your vendor data as: {DATA_INPUTS_DIR / f'{vendor}_devices.csv'}",
            file=sys.stderr,
        )
        print(
            f"  Template: {DATA_INPUTS_DIR / f'{vendor}_devices.template.csv'}",
            file=sys.stderr,
        )
        return 1

    logger = setup_logging(LOG_FILE)
    mode = "DRY-RUN" if args.dry_run else "APPLY"
    logger.info("=== update_vendor [%s] vendor=%s csv=%s ===", mode, vendor, csv_path)

    token = os.getenv("NETBOX_API_TOKEN")
    if not token:
        print("ERROR: NETBOX_API_TOKEN is missing in environment", file=sys.stderr)
        return 1

    base = build_base_url()
    session = session_with_auth(token)

    col = COLUMN_MAPS.get(vendor)
    if col is None:
        print(f"ERROR: No column map defined for vendor '{vendor}'", file=sys.stderr)
        return 1

    rows = load_csv(csv_path)
    print(f"=== Update vendor dates [{mode}] vendor={vendor} rows={len(rows)} ===\n")
    logger.info("Loaded %d rows", len(rows))

    vendor_id = get_or_create_vendor(session, base, manufacturer_name, args.dry_run, logger)

    ok = skipped = errors = 0

    for row in rows:
        serial = row.get(col["serial"], "").strip()
        if not serial:
            logger.warning("Row missing serial, skipping: %s", row)
            row[STATUS_COL] = STATUS_ERROR
            skipped += 1
            continue

        try:
            device = find_device_by_serial(session, base, serial)
        except requests.HTTPError as exc:
            logger.error("HTTP error looking up serial %s: %s", serial, exc)
            row[STATUS_COL] = STATUS_ERROR
            errors += 1
            continue

        if not device:
            msg = f"SKIP  serial={serial!r} — not found in Netbox"
            print(f"  {msg}")
            logger.warning(msg)
            row[STATUS_COL] = STATUS_MISSING
            skipped += 1
            continue

        device_name = device["name"]
        eol_date = parse_vendor_date(row.get(col["eol_date"], ""))
        svc_start = parse_vendor_date(row.get(col["service_start"], ""))
        svc_end = parse_vendor_date(row.get(col["service_end"], ""))

        print(f"  {device_name}  serial={serial}")
        print(f"    eol={eol_date}  contract={svc_start} → {svc_end}")

        try:
            if eol_date:
                upsert_hardware_lifecycle(
                    session, base, device["device_type"]["id"],
                    eol_date, args.dry_run, logger, device_name,
                )
            upsert_support_contract(
                session, base, device, vendor_id,
                svc_start, svc_end, args.dry_run, logger,
            )
            row[STATUS_COL] = STATUS_IMPORTED
            ok += 1
        except requests.HTTPError as exc:
            body = exc.response.text if exc.response is not None else str(exc)
            msg = f"ERROR {device_name}: {body}"
            print(f"    {msg}", file=sys.stderr)
            logger.error(msg)
            row[STATUS_COL] = STATUS_ERROR
            errors += 1

    if not args.dry_run:
        save_csv(csv_path, rows)
        logger.info("Wrote import_status back to %s", csv_path)

    summary = f"\nDone: {ok} updated, {skipped} skipped, {errors} errors."
    print(summary)
    logger.info(summary.strip())

    if args.dry_run:
        print("Dry-run complete — no changes applied. Remove --dry-run to apply.")

    return 0 if errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
