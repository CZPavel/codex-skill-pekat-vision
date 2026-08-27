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

Use this decision sequence before writing communication code:

1. Is the consumer another module in the same evaluation? Use Context/FLOW.
2. Is it another Code tool in the same PEKAT 4 project? Use GlobalData with explicit key ownership and lifetime.
3. Is it another PEKAT project? Use Cross-PEKAT only when project-to-project state transfer is the requirement.
4. Is an external client sending images to a running project? Use project REST or the exact-version official SDK.
5. Is an external controller managing project lifecycle? Use Projects Manager HTTP or Simple TCP.
6. Is PEKAT only emitting a simple result or command? Prefer the native Output HTTP, CMD, TCP, or S7 module that matches the destination.
7. Use Code networking only when the native route cannot express the required protocol or transformation, and bound its latency/failure behavior.

## Running-project REST

Observed/documented families include:

- `POST /analyze_image` for an encoded image body;
- `POST /analyze_raw_image` for raw image bytes, with exact dimensions and pixel format supplied as required by that version;
- `GET /ping` for a bounded availability check;
- `GET /last_image` for the most recently available image/result representation;
- `GET /stop` for a lifecycle mutation only when explicitly approved and documented for the target version.

Analysis responses are selected with the documented `response_type`; observed choices include `context`, `image`, `annotated_image`, and `heatmap`. Treat names, accepted combinations, headers, body encoding, and error payloads as exact-version contracts. Do not silently substitute one response for another, and do not call `/stop` as a health probe.

Bundled minimal client:

```powershell
python scripts/rest_api_client_demo.py image.png --url http://127.0.0.1:8100/analyze_image
```

Use image bytes in `data=`, an appropriate `Content-Type`, bounded connect/read timeout, `raise_for_status()`, and guarded JSON/payload parsing. Test success, timeout, connection error, HTTP error, invalid JSON/payload, and missing/invalid headers or Context.

Do not automatically add retry. Add it only when the operation is safe/idempotent and a concrete reliability requirement or observed transient failure justifies it. Then bound attempts/backoff and test terminal behavior. Treat persistent remote state with freshness/sequence/validity only when the use case requires it.

### Exact PEKAT 4.0.3 public runtime

The tested public REST surface confirmed:

- `GET /ping` and `GET /last_image`;
- `POST /analyze_image` and `POST /analyze_raw_image`;
- response forms `context`, `image`, `annotated_image`, and `heatmap`;
- `ContextBase64utf`, `context_in_body`, `ImageLen`, and exact string `data`
  in their tested request/response contracts.

Keep parameter placement/encoding exact to the target endpoint rather than
mixing these named fields into one invented universal payload. Runtime quirks:

| Invalid input | Observed 4.0.3 response |
|---|---|
| analyze `response_type` | HTTP 400 |
| `/last_image` `response_type` | HTTP 200, `image/png`, zero-byte body |
| missing/invalid analyze image | HTTP 400 with internal OpenCV traceback details |

Guard status, content type, body length, and parse separately. Treat traceback
text as diagnostic data and avoid exposing internal details unnecessarily. Do
not reinterpret the zero-byte PNG as a valid image.

## Official SDK

Prefer the official Python, C, or .NET SDK for an external application when it provides the exact running-project path needed. Keep SDK version separate from PEKAT application version; verify compatibility rather than inferring it. REST may be sufficient for a small custom integration that does not benefit from an SDK wrapper.

For external Python, use the application's interpreter and SDK package. For Code inside PEKAT, match embedded Python ABI/architecture and available libraries. A read-only fingerprint on one PC observed `cp310` for 3.19.3 and `cp312` for 4.0.1; re-probe elsewhere.

## Projects Manager

Projects Manager owns lifecycle; it is not the image-analysis API. Exact-version documented operations can cover listing, status, start, stop, and project switching. `scripts/projects_manager_tcp_demo.py` is a deliberately small bounded client. Before start/stop/switch/restart decide ownership:

- Manager owns lifecycle;
- external application owns lifecycle; or
- explicit hybrid with one authority per transition.

Default to read-only status/listing. Require exact protocol evidence and approval before a lifecycle mutation. Avoid adding a state machine/watchdog unless the operating requirement calls for one.

For readiness, neither `running.db`, `cameraIsRunning`, nor saved provider state
is sufficient. Correlate process/PID → listening port → `/ping` →
inference/model ready → camera/provider live. Basic lifecycle evidence does not
close repeated clean startup distribution or stuck `Stopping`/`Starting` cases;
do not use restart as universal recovery.

## Cross-PEKAT

Use Cross-PEKAT only for explicit project-to-project communication. Observed practical calls include client registration and asynchronous GlobalData updates. They create edges outside local FLOW and need endpoint, key/type, writer ownership, consumer behavior, and failure policy.

Simple non-critical transfer can remain simple. For a critical persistent remote result, define freshness only as needed (for example timestamp, sequence, validity, or reset ownership); do not impose all mechanisms on every transfer. Test disconnect/reconnect and stale behavior before production claims.

## Native Outputs and Code networking

Prefer a native PEKAT Output when the requirement is simple emission:

- **HTTP Output** for a bounded HTTP request to an external service;
- **CMD Output** for a deliberately approved local command boundary;
- **TCP Output** for a configured application payload to an external TCP peer;
- **S7 Output** for the supported Siemens PLC mapping.

Projects Manager **Simple TCP** is a lifecycle/control protocol. It is not the same service as **TCP Output**, which sends application results. Keep their ports, ownership, payloads, and failure handling separate.

The PEKAT 4.0.1 Code environment directly tested on one Windows AMD64 installation imported `requests`, `websocket`, `socketio`, `paramiko`, `snap7`, `win32api`, `openpyxl`, and `yaml`. Those imports show local availability, not that Code is the preferred integration layer and not that every dependency was functionally exercised. Consult `code-runtime-pekat401.md` for the exact evidence class and `code-library-installation.md` before depending on a package on another PC.

For any external communication choice, state what moves, who initiates, whether a response must return into FLOW, whether persistence/retry is required, and the required failure behavior. Distinguish transport timeout, connection failure, HTTP/protocol error, invalid payload, stale data, and a valid application-level NOK result. Add retry/reconnect/fallback only where the operating requirement needs it.

REST analysis success and output persistence are separate. In exact 4.0.3, a
native Image Saver with a missing configured root could leave REST at HTTP 200
and Context `error=false` while the failure appeared only in project logs and no
file persisted. Check the filesystem/log outcome when persistence matters.

## Network Code boundary

Per-evaluation Code may use a small bounded call only when latency and failure semantics fit the FLOW. Otherwise prefer an external poller/bridge or native Output. Never use an unbounded timeout, infinite loop, hidden credential, or private endpoint in a reusable example.

Use `127.0.0.1` or TEST-NET addresses in public examples. Keep credentials outside source/Form defaults. Classify fail-open/fail-closed from the control risk rather than choosing automatically.

## Capability routing

- IFM/IO-Link: use PEKAT integration guidance plus `ifm-io-link` if installed; otherwise exact current IODD/vendor docs.
- Basler/pylon: use PEKAT-side architecture here and `basler-cameras` if installed.
- Kepware, ThingWorx/FIOT, or enterprise middleware: use the corresponding specialized skill/tool if available; otherwise current primary vendor docs. Specialized capability is runtime-optional, not a prerequisite for PEKAT guidance.

Internal Socket.IO observations are diagnostic evidence, not a supported public
API. Do not add browser/Socket.IO FLOW authoring, `update_flow`/`set_store`
automation, or autonomous lifecycle control to the normal skill workflow.

Open gates: REST variants beyond the exact 4.0.3 cases above, exact current SDK release matrix, Projects Manager TCP repeated-readiness/stuck-state regression, and Cross-PEKAT reconnect/failure/stale-state acceptance.

Legacy public evidence ID retained for regression routing: `pekat-kb-4-0-1-page-1513133459`.
