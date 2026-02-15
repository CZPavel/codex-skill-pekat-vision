# User Guide: Industrial IMS Integration

## 1) What this package gives you

- A connector skeleton in `src/industrial_ims_bridge.py`.
- A smoke test in `tests/test_industrial_ims_bridge.py`.
- Configuration template in `.env.example`.
- Project docs and context files for handover and governance.

## 2) Prerequisites

- Python 3.10+.
- Access details for ThingWorx/FIOT and IMS endpoint.
- Approved test endpoint (do not start with production).

## 3) Configure environment

Copy `.env.example` values into your runtime environment:

- `INTEGRATION_MODE` (`zos_connect` or `ims_jdbc`)
- `IMS_ENDPOINT`
- `IMS_TIMEOUT_SECONDS`
- `IMS_MAX_RETRIES`
- `IMS_BACKOFF_SECONDS`
- `IMS_DRY_RUN`
- `IMS_PROGRAMVIEW`
- `IMS_DATABASE`
- `IMS_TRANSACTION`

## 4) Run dry-run first

Example:

```powershell
python src/industrial_ims_bridge.py --payload-json "{\"tag\":\"line1.station2.temp\",\"value\":72.4,\"quality\":\"GOOD\"}"
```

Dry-run does not call remote systems. It validates mapping and correlation-id handling.

## 5) Execute real call

Set `IMS_DRY_RUN=false`, then run:

```powershell
python src/industrial_ims_bridge.py --payload-json "{\"tag\":\"line1.station2.temp\",\"value\":72.4,\"quality\":\"GOOD\",\"timestamp\":\"2026-02-15T14:00:00Z\"}"
```

## 6) Run tests

```powershell
pytest tests/test_industrial_ims_bridge.py -q
```

## 7) Decide integration path

- Use `z/OS Connect` when API governance and OpenAPI contracts are required.
- Use `IMS Connect + ODBM + JDBC/DL/I` when direct DB path is required and approved.
- Use IMS consumer mode when IMS must call external REST APIs.

## 8) Production safety checklist

- Confirm PSB and ACB alignment after every PSB/DBD change.
- Confirm timeout and retry limits are explicitly set.
- Confirm secrets are injected from a secure store.
- Confirm logs include correlation ids.
- Confirm change approvals before enabling writes in production.
