# USER GUIDE

## 1. Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure

1. Copy `.env.example` to `.env`.
2. Fill:
   - `THINGWORX_BASE_URL`
   - `THINGWORX_APP_KEY`
   - `THINGWORX_THING`
   - optional `THINGWORX_PROPERTY`, `THINGWORX_SERVICE`
3. Keep `THINGWORX_DRY_RUN=true` for first run.

## 3. First run (healthcheck)

```bash
python src/main.py --healthcheck
```

Expected:
- command runs without network/auth errors
- output contains dry-run metadata or valid server response

## 4. First property write skeleton

```bash
python src/main.py --write-property --value 12.34
```

## 5. First service invoke skeleton

```bash
python src/main.py --invoke-service --service-payload "{\"value\": 12.34, \"source\": \"connector\"}"
```

## 6. Switch to real mode

After validation:
1. Set `THINGWORX_DRY_RUN=false`.
2. Re-run healthcheck.
3. Execute write/invoke against test Thing first.

## 7. mTLS (if required)

Set:
- `THINGWORX_CLIENT_CERT`
- `THINGWORX_CLIENT_KEY`

Then re-run healthcheck and inspect TLS/client-certificate acceptance.
