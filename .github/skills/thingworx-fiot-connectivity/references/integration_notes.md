# Integration Notes

## Discovery contract (collect before coding)

Collect these values first:
- `THINGWORX_BASE_URL` (exact base URL, including scheme).
- `THINGWORX_APP_KEY` (secret, never commit).
- Target entities:
  - `THINGWORX_THING`
  - `THINGWORX_PROPERTY` (for first write test)
  - `THINGWORX_SERVICE` (for first invoke test)
- Payload contract:
  - JSON schema
  - units
  - timestamp and timezone convention
- Network/security:
  - TLS policy (`verify=true` by default)
  - mTLS requirement (client cert/key)
  - DNS, proxy, and firewall constraints

## Endpoint patterns (MVP)

Use these patterns as default skeletons and verify against target version:
- Healthcheck/auth/entity reachability:
  - `GET /Thingworx/Things/{thingName}`
- Write property:
  - `PUT /Thingworx/Things/{thingName}/Properties/{propertyName}`
- Invoke service:
  - `POST /Thingworx/Things/{thingName}/Services/{serviceName}`

Use request headers:
- `appKey: <secret>`
- `x-thingworx-session: false`
- `Accept: application/json`
- `Content-Type: application/json` (for body requests)

## Retry, timeout, and logging baseline

- Timeout per request: 5-15 seconds (start with 10).
- Retries: 2-4 (start with 3).
- Backoff: 0.5s, 1.0s, 2.0s style.
- Retry on:
  - timeout
  - connection reset
  - 429/5xx
- Log:
  - endpoint
  - status code
  - latency
  - retry count
  - correlation id (if available)

## mTLS / client certificate flow

When customer environment requires client certificates:
1. Obtain client certificate and key from customer PKI.
2. Store paths outside repo or in secured runtime mount.
3. Configure connector with:
   - `THINGWORX_CLIENT_CERT=<path-to-cert.pem>`
   - `THINGWORX_CLIENT_KEY=<path-to-key.pem>` (optional if bundled)
4. Keep `verify=true` and use trusted CA bundle.
5. Test with read-only call first (`healthcheck`) before any write.

## Kepware integration modes

Use one of these patterns:
- Native mode:
  - KEPServerEX ThingWorx connectivity/agent writes data directly.
- Bridge mode:
  - Connector reads Kepware-exposed data (for example OPC UA, plugin output) and writes to ThingWorx REST.

In both modes, enforce tag-to-property mapping with:
- stable property names
- unit metadata
- timestamp policy
- alarm thresholds and deadbands

## Extensions and deploy safety

Treat extension import as controlled change:
- Confirm maintenance window and rollback plan.
- Check `PlatformSubsystem.importEnabled`.
- Confirm required platform restart implications.
- Avoid deploying extensions without explicit user approval.

## Troubleshooting checklist

- [ ] DNS resolves ThingWorx/FIOT host.
- [ ] Port is reachable (usually `443` unless customized).
- [ ] TLS chain validates from integration host.
- [ ] Client certificate is accepted (if mTLS enabled).
- [ ] `appKey` has rights to target Thing/Property/Service.
- [ ] `x-thingworx-session=false` is present in each request.
- [ ] First read call succeeds before write/invoke.
- [ ] Secrets are not present in repository history.
