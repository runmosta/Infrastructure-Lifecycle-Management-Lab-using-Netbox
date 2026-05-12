# Design Decisions — Add_Device Bulk CSV Import

Captured via structured design interview. Each entry documents what was chosen, what alternatives were considered, why the choice was made, and what trade-offs exist.

---

## 1. Input Format: Manual CSV (not .xlsx)

**Chosen:** Script reads `.csv` only. User exports to CSV from Excel manually before running.

**Alternatives considered:**
- Accept `.xlsx` directly using `openpyxl`
- Accept both and auto-detect by extension

**Rationale:** Vendor asset sheets are received as Excel, but CSV is universally readable, has no dependency on a library for parsing, and avoids dealing with merged cells, multiple sheets, or formatting quirks in vendor-provided files. Manual export is a one-step operation.

**Trade-offs:** Adds a manual step between receiving the vendor file and running the import. If the Excel format becomes stable and consistent, adding `openpyxl` support later is low-risk.

---

## 2. CSV Structure: Per-Vendor Files

**Chosen:** One CSV file per vendor: `cisco_devices.csv`, `arista_devices.csv`, `fortinet_devices.csv`.

**Alternatives considered:**
- One CSV for all devices (all vendors mixed)
- One CSV per site

**Rationale:** Vendor is a mandatory field in Netbox (`manufacturer`). Per-vendor files make the manufacturer implicit — it is derived from the filename — eliminating a repetitive column and reducing input errors. Also mirrors how vendor asset sheets are typically delivered.

**Trade-offs:** Importing devices of mixed vendors in a single run requires multiple invocations. A device accidentally placed in the wrong file gets the wrong manufacturer.

---

## 3. Manufacturer Derived from Filename

**Chosen:** The script infers the manufacturer from the CSV filename. `cisco_devices.csv` → `manufacturer=Cisco`. Mapping is: `cisco` → `Cisco`, `arista` → `Arista`, `fortinet` → `Fortinet`.

**Alternatives considered:**
- Pass `--manufacturer` as a CLI argument on every run
- Include a `manufacturer` column in every CSV row

**Rationale:** Avoids a repetitive column with 100% identical values per file. Keeps CSV files smaller and reduces copy-paste errors when maintaining them.

**Trade-offs:** Filename must match the expected pattern. A file named `new_cisco_batch.csv` won't be automatically recognized — user must follow the naming convention `<vendor>_devices.csv`.

---

## 4. CSV Column Headers

**Chosen:**

```
name,site,role,model,serial,ip,eol_date
```

| Column | Required by Netbox | Notes |
|--------|-------------------|-------|
| `name` | Yes | Unique device name |
| `site` | Yes | Netbox site slug/name; created if absent |
| `role` | Yes | Device role; created if absent |
| `model` | Yes | Device type model; created if absent |
| `serial` | No | Serial number |
| `ip` | No | Management IP in CIDR notation (e.g. `192.168.1.1/24`) |
| `eol_date` | No | Hardware End-of-Life date (ISO 8601: `YYYY-MM-DD`) |

`manufacturer` is omitted — derived from filename (see §3).

**Alternatives considered:**
- Include `tenant`, `support_contract_start`, `support_contract_end` columns (mentioned in interview but deferred)
- Use Netbox's native CSV import format

**Rationale:** Minimal required set that maps directly to current `Add_Device.py` arguments, plus the additional fields the user identified. Tenant and support contracts can be added in a later iteration once the lifecycle plugin integration is fully tested.

**Trade-offs:** Support contract and tenant data from vendor sheets cannot be imported in this first version — must be added manually or via a future extension.

---

## 5. Existing Device Behavior: Upsert

**Chosen:** If a device already exists in Netbox, update its changed fields (upsert).

**Alternatives considered:**
- Skip silently (current single-device behavior)
- Error out — treat duplicate as a mistake
- Configurable per-run via `--mode` flag

**Rationale:** Bulk CSV imports are often re-run when the source data is refreshed. An upsert allows the CSV to be the ongoing source of truth for the fields it manages, rather than requiring manual deduplication.

**Trade-offs:** A typo in the CSV that changes a field (e.g. wrong site) will silently overwrite the correct Netbox value. Dry-run mode (see §6) mitigates this risk.

---

## 6. Dry-Run Mode

**Chosen:** `--dry-run` flag. When set, the script prints all planned changes without touching Netbox. Changes are applied by default (no flag needed). This is the same pattern as `migrate_to_lifecycle_plugin.py --apply`.

**Alternatives considered:**
- No dry-run
- Invert default: dry-run is default, require `--apply` to execute

**Rationale:** Bulk operations are high-risk. A dry-run pass before applying changes is standard practice in this codebase (see `migrate_to_lifecycle_plugin.py`). Defaulting to *apply* (no flag needed) was chosen for operational convenience — most runs will be intentional.

**Trade-offs:** A user who forgets to add `--dry-run` first will apply changes immediately. Mitigated by logging (see §9).

---

## 7. Error Handling: API-Delegated Validation

**Chosen:** No pre-flight validation of CSV rows. The Netbox API will reject invalid rows and the script will log the error and continue.

**Alternatives considered:**
- Fail-fast: stop the entire run on the first invalid row
- Skip + warn: collect all errors, log them, continue with valid rows

**Rationale:** User explicitly chose to delegate validation to the API. This avoids duplicating Netbox's validation logic in the script and keeps the script simple. The API's error messages are descriptive enough to diagnose problems.

**Trade-offs:** You only discover row-level errors at runtime, not before. If rows 1–50 succeed and rows 51+ fail, you have a partial import state. The log file (see §9) records exactly what succeeded and what failed, making recovery tractable.

---

## 8. IP Address Format

**Chosen:** CIDR notation in the CSV: `192.168.1.1/24`. User is responsible for ensuring the corresponding prefix exists in Netbox before import.

**Alternatives considered:**
- Host-only notation with automatic `/32` padding
- Skip IP entirely for first version

**Rationale:** Netbox requires prefix length for IP address objects. CIDR is the native Netbox format. Automatic `/32` would be wrong for management IPs on shared subnets.

**Trade-offs:** User must pre-create prefixes in Netbox, or the IP create call will fail (handled per §7 — API rejects it, logged, import continues for that field).

---

## 9. Logging

**Chosen:** Log to `logs/python/add_devices.log`. No stdout logging from the script itself (or minimal stdout for interactive feedback).

**Alternatives considered:**
- stdout only
- Both stdout and file

**Rationale:** `logs/python/` already exists and is gitignored. File logging provides a persistent audit trail of every bulk import run, which is essential for recovering from partial imports (see §7).

**Trade-offs:** No log output visible unless the user checks the file. Consider adding at least a summary line to stdout at the end of a run.

---

## 10. CSV File Location

**Chosen:** `Data/inputs/` in the project root.

**Alternatives considered:**
- `config/import/` (would need explicit `.gitignore` entry)
- Path outside the repo entirely

**Rationale:** `Data/` is already covered by the `.gitignore` pattern `Data/postgres/*` and `Data/netbox/media/*`. The `Data/inputs/` path falls under the same intent — runtime data, not source code. A `.gitkeep` ensures the directory exists in Git without exposing actual data files.

**Trade-offs:** The `.gitignore` patterns currently use specific subdirectory wildcards (`Data/postgres/*`, `Data/netbox/media/*`), not a blanket `Data/`. Must verify `Data/inputs/*.csv` is actually ignored (see §11).

---

## 11. Git Exclusion of CSV Files

**Chosen:** Add `Data/inputs/*.csv` explicitly to `.gitignore`. A template file `Data/inputs/<vendor>_devices.template.csv` (headers + one sample row) **is** committed to Git to document the expected format.

**Alternatives considered:**
- Ignore all of `Data/inputs/`
- Document format in README only

**Rationale:** The template documents the contract between the script and the input data without exposing real device data. Real CSVs (with serial numbers, IPs) are excluded because they contain infrastructure details that should not be in version control.

**Trade-offs:** Template must be kept in sync with the actual column set as the script evolves.

**Implementation note:** The `.gitignore` pattern `Data/inputs/*.csv` also matches `*.template.csv`. An explicit exception `!Data/inputs/*.template.csv` is required and has been added. The rule order in `.gitignore` matters: ignore-all comes before the exception.

---

## 12. Script Architecture: Extend Add_Device.py

**Chosen:** `Add_Device.py` is extended with a `--csv` argument. Existing `--name`, `--site`, `--role`, `--manufacturer`, `--model` CLI arguments continue to work for single-device use.

**Alternatives considered:**
- New separate script `Bulk_Add_Devices.py`
- Replace CLI args entirely with CSV-only mode

**Rationale:** The shared helper functions (`get_or_create`, `session_with_auth`, `slugify`, etc.) are reused. Keeping one script reduces maintenance surface. The `--csv` flag clearly signals bulk mode; absence of `--csv` means single-device mode.

**Trade-offs:** The script grows in complexity. If CSV mode and single-device mode diverge significantly in future, splitting into separate scripts is the right call.

---

## 13. Docker: python-scripts Service

**Chosen:** Add a `python-scripts` service to `docker-compose.yml` with `Data/inputs/` bind-mounted at `/app/data/inputs` and `logs/python/` mounted at `/app/logs`.

**Alternatives considered:**
- Run scripts directly on Mac host connecting to `localhost:8000`

**Rationale:** Keeps execution environment consistent (same Python version, same packages, same network namespace as other containers). Scripts connect to Netbox via the internal Docker network (`http://netbox:8080`) rather than exposing ports to the host.

**Trade-offs:** Requires `docker compose run python-scripts python Add_Device.py ...` syntax instead of `python Add_Device.py ...`. A `Makefile` or shell wrapper could simplify this.

---

## Open Questions (Deferred)

| Topic | Decision Needed |
|-------|----------------|
| Tenant support | Add `tenant` column to CSV in a future iteration |
| Support contracts | `contract_start`, `contract_end` columns — tie into netbox-lifecycle plugin |
| Filename pattern validation | Should the script refuse to run if filename doesn't match `<vendor>_devices.csv`? |
| Prefix pre-check | Should the script warn if an IP's prefix doesn't exist in Netbox before attempting create? |
| Multi-sheet Excel | If vendor sheets gain multiple tabs (e.g. active vs. decommissioned), reconsider xlsx support |
