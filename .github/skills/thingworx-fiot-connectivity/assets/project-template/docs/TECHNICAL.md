# TECHNICAL

## Goal

Provide a minimal but production-oriented bridge between local software/PLC/monitoring and FIOT (ThingWorx-based).

## Components

- `src/thingworx_client.py`: REST client with:
  - appKey auth header
  - `x-thingworx-session=false`
  - timeout + retry/backoff
  - logging
  - TLS verify and optional client cert
  - dry-run mode
- `src/main.py`: CLI entrypoint for first healthcheck/write/invoke runs.

## Endpoint skeletons

Verify exact behavior against your ThingWorx version/entity model:
- Healthcheck/entity reachability:
  - `GET /Thingworx/Things/{thingName}`
- Write property:
  - `PUT /Thingworx/Things/{thingName}/Properties/{propertyName}`
- Invoke service:
  - `POST /Thingworx/Things/{thingName}/Services/{serviceName}`

## Authentication and session policy

- Use Application Key for application-to-platform integration.
- Send:
  - `appKey: <secret>`
  - `x-thingworx-session: false`
- Avoid creating user sessions from integration clients to reduce platform memory usage.

## TLS and mTLS

- Keep TLS verification enabled by default (`THINGWORX_VERIFY_TLS=true`).
- If customer requires client certificate:
  - `THINGWORX_CLIENT_CERT=/secure/path/client-cert.pem`
  - `THINGWORX_CLIENT_KEY=/secure/path/client-key.pem`
- Never commit certs/keys/app keys into git.

## Logging and retries

- Default timeout: 10s
- Default retries: 3
- Default backoff: 0.5s exponential
- Retry classes:
  - timeout
  - connection errors
  - 429 and 5xx responses

## Troubleshooting

- `401/403`: appKey missing/invalid/insufficient permissions.
- `404`: Thing/Property/Service name mismatch.
- `SSL error`: missing CA trust, wrong client cert, or hostname mismatch.
- `429/5xx`: apply retry/backoff and inspect platform load.

## Verification checklist

- [ ] DNS resolves ThingWorx/FIOT host.
- [ ] Port is reachable.
- [ ] TLS chain validates from connector host.
- [ ] appKey has required rights.
- [ ] Requests include `x-thingworx-session=false`.
- [ ] Dry-run works before first write.
