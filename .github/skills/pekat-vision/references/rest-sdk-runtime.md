# REST, SDK, Projects Manager, and Cross-PEKAT

## Select the communication layer

| Need | Mechanism |
|---|---|
| Send an image/data to a running project and obtain analysis | official PEKAT SDK when exact-version/use-case fits; otherwise project REST |
| Start/stop/list/manage projects | Projects Manager HTTP or Simple TCP |
| Share state between two PEKAT projects | Cross-PEKAT (`pekat_communication`) |
| Share state between Code tools in one running PEKAT 4 project | GlobalData |
| Simple value/image/result to an external consumer | appropriate PEKAT Output |
| PLC/enterprise integration | native Output or a bounded external bridge; do not force it into per-image Code |

Do not confuse Projects Manager TCP with a project Output TCP endpoint, or local GlobalData with Cross-PEKAT.

## Running-project REST

Observed/documented families include encoded-image and raw-image analysis plus GET status/data operations. Confirm exact endpoint, headers, payload shape, raw dimensions/pixel format, and `response_type` from exact-version documentation.

Bundled minimal client:

```powershell
python scripts/rest_api_client_demo.py image.png --url http://127.0.0.1:8100/analyze_image
```

Use image bytes in `data=`, an appropriate `Content-Type`, bounded connect/read timeout, `raise_for_status()`, and guarded JSON/payload parsing. Test success, timeout, connection error, HTTP error, invalid JSON/payload, and missing/invalid headers or Context.

Do not automatically add retry. Add it only when the operation is safe/idempotent and a concrete reliability requirement or observed transient failure justifies it. Then bound attempts/backoff and test terminal behavior. Treat persistent remote state with freshness/sequence/validity only when the use case requires it.

## Official SDK

Prefer official SDK for an external Python/.NET/C application when it provides the exact running-project/lifecycle path needed. Keep SDK version separate from PEKAT runtime version; verify compatibility rather than inferring it.

For external Python, use the application's interpreter and SDK package. For Code inside PEKAT, match embedded Python ABI/architecture and available libraries. A read-only fingerprint on one PC observed `cp310` for 3.19.3 and `cp312` for 4.0.1; re-probe elsewhere.

## Projects Manager

Projects Manager owns lifecycle; it is not the image-analysis API. `scripts/projects_manager_tcp_demo.py` is a deliberately small bounded client. Before start/stop/restart decide ownership:

- Manager owns lifecycle;
- external application owns lifecycle; or
- explicit hybrid with one authority per transition.

Default to read-only status/listing. Require exact protocol evidence and approval before a lifecycle mutation. Avoid adding a state machine/watchdog unless the operating requirement calls for one.

## Cross-PEKAT

Use Cross-PEKAT only for explicit project-to-project communication. Observed practical calls include client registration and asynchronous GlobalData updates. They create edges outside local FLOW and need endpoint, key/type, writer ownership, consumer behavior, and failure policy.

Simple non-critical transfer can remain simple. For a critical persistent remote result, define freshness only as needed (for example timestamp, sequence, validity, or reset ownership); do not impose all mechanisms on every transfer. Test disconnect/reconnect and stale behavior before production claims.

## Network Code boundary

Per-evaluation Code may use a small bounded call only when latency and failure semantics fit the FLOW. Otherwise prefer an external poller/bridge or native Output. Never use an unbounded timeout, infinite loop, hidden credential, or private endpoint in a reusable example.

Use `127.0.0.1` or TEST-NET addresses in public examples. Keep credentials outside source/Form defaults. Classify fail-open/fail-closed from the control risk rather than choosing automatically.

## Capability routing

- IFM/IO-Link: use PEKAT integration guidance plus `ifm-io-link` if installed; otherwise exact current IODD/vendor docs.
- Basler/pylon: use PEKAT-side architecture here and `basler-cameras` if installed.
- Kepware, ThingWorx/FIOT, or enterprise middleware: use the corresponding specialized skill/tool if available; otherwise current primary vendor docs. Specialized capability is runtime-optional, not a prerequisite for PEKAT guidance.

Open gates: live REST smoke on current installs, exact current SDK release matrix, Projects Manager TCP regression, and Cross-PEKAT reconnect/failure/stale-state acceptance.

Legacy public evidence ID retained for regression routing: `pekat-kb-4-0-1-page-1513133459`.
