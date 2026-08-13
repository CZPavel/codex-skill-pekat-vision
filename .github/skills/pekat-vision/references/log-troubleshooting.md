# PEKAT project log troubleshooting

## Primary logs

Project-local logs use the observed family:

```text
<project>\logs\output.log
<project>\logs\output.log.YYYY_MM_DD.log
```

Ask the user for the relevant `output.log`, or analyze the project `logs/`
directory when it is locally accessible. Logs can contain private paths, device
identities, endpoints and values; summarize/redact before sharing or committing.

Use the read-only standard-library helper:

```powershell
python scripts/analyze_pekat_log.py <project>\logs\output.log
python scripts/analyze_pekat_log.py <project>\logs --json
```

It groups multiline tracebacks and repeated normalized error families, reports
first occurrence and terminal exception, and classifies likely subsystem. It
does not modify the log or project.

## Diagnostic method

1. Identify the exact project and relevant session/time range.
2. Find the **first meaningful ERROR**, not merely the last traceback line.
3. Group repeated normalized exceptions; hundreds of repeats can be one incident.
4. Separate a root-cause candidate from later secondary errors.
5. Correlate the first failure with camera, model, filesystem, Code/FLOW,
   folder source, network or project-start state.
6. Propose a project change only after the evidence identifies the layer.

For camera failures, follow:

```text
provider → device discovery → selected camera → initialization → acquisition → grab
```

An observed chain such as:

```text
CameraSearchError: No camera connections detected
→ CameraConnectionError: Camera is not initialized
→ grab error
```

usually makes the search/discovery error the better first root-cause candidate.
Check power/network/driver/device ownership before changing FLOW.

## Category routing

| Category | Typical evidence | Next check |
|---|---|---|
| camera | no connections, init, feature access, grab/acquisition | stop at the first failed camera stage; avoid dual ownership |
| model | loading, loaded, not loaded yet, inference error | model ID/path, load completion/readiness, then input/inference |
| filesystem | missing Image Saver root, invalid path, permission/disk | configured path, ownership, permissions and space; do not auto-create/delete |
| code_flow | Python traceback, Error analyzing image, user Code/FLOW failure | first traceback, module/context and ordering; do not execute stored Code to inspect it |
| folder source | watcher/source startup | watched path, permissions and file arrival |
| network | refusal/reset/timeout/HTTP failure | owner process, host/port and transport versus valid application NOK |
| project start | server startup/port conflict | package metadata, command line, port and earliest startup error |

## State boundary

Keep these separate:

```text
project server running
!= camera connected
!= camera initialized
!= camera acquiring
!= FLOW evaluating
```

A running server plus a camera-init error is not a contradiction. Likewise, a
model-load success does not prove camera acquisition or FLOW evaluation.

## Safe response pattern

When the user says only “PEKAT does not work”, ask for/derive in this order:

1. exact version and project identity;
2. observable symptom and time;
3. current/rotated project log;
4. camera/model/filesystem state;
5. process and configured/listening port if locally accessible;
6. FLOW/Code only when the earlier evidence points there.
