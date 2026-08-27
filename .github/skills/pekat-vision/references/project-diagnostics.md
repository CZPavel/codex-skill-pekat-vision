# PEKAT project diagnostics

## Read-only first pass

Start at the project root and read `pekat_package.json`. Where present, record:

- project `name` and exact PEKAT `version`;
- configured `port`;
- `gpuIndex` / `cpuIndex`;
- `createdAt` / `lastOpen`;
- `autoStart` and backup/upgrade metadata.

Then inventory, without loading models or unsafe serialized objects:

```text
database/        current configuration/FLOW/state
database_old/    historical/migration layer; analyze separately
logs/            output.log and rotations
classifier/, detector/, supervised/, unsupervised/   model workspaces
images/          project images
cache/           derived/runtime candidates; do not delete first
camera root files/config YAML                         persisted configuration
```

Run:

```powershell
python scripts/pekat_project_diagnostics.py <project>
python scripts/pekat_project_diagnostics.py <project> --runtime
python scripts/pekat_project_diagnostics.py <project> --runtime --probe-http
python scripts/pekat_project_diagnostics.py <project> --flow --json
```

Default mode is filesystem/log-only. `--runtime` explicitly performs read-only
Windows process-command-line correlation and a localhost TCP connect to the
configured port. `--probe-http` adds one explicit `HEAD /` request and requires
`--runtime`. `--flow` reuses `analyze_flow_database.py`; it does not introduce a
second FLOW parser.

## Runtime correlation

Never use `database/running.db` existence as a process-alive marker. It was
observed in inactive backups/clones as well as active projects. Correlate:

```text
project metadata + process command line + PID/start state + configured/listening port + /ping + inference/model state + camera/provider state + logs
```

These are independent conditions:

```text
PROJECT SERVER RUNNING
!= CAMERA CONNECTED
!= CAMERA INITIALIZED
!= CAMERA ACQUIRING
!= FLOW EVALUATING
```

Stored camera configuration and `cameraIsRunning` also do not prove current
camera connection or ownership. Use the readiness sequence process/PID →
listening port → `/ping` → inference/model ready → camera/provider live. A
reachable port or successful `/ping` alone does not prove valid acquisition or
successful evaluation.

## FLOW/database route

Use `scripts/analyze_flow_database.py <project-or-database.zip>` for `modules.db`,
recursive `modules.sort`, state, Filter/Gate, Code imports/side effects and
separate `database_old`. It uses a restricted primitive/container Pickle reader
and never executes Code or Pickle object construction. Do not use generic
`pickle.load()` on project/cache data.

## Troubleshooting order

1. Confirm exact project path, package metadata and version.
2. If runtime status matters, correlate process/PID, port, `/ping`, model/inference and provider/camera instead of reading disk flags alone.
3. Analyze the relevant log session and first error family.
4. Check camera provider/discovery/init/acquisition when indicated.
5. Check model identity/load/readiness when indicated.
6. Check Image Saver/folder/output paths and permissions when indicated.
7. Inspect FLOW/Code only after the evidence points there.
8. Make one approved change on an isolated copy/target and verify the result.

Do not delete cache/session/database files as a first troubleshooting step. Keep
backup/configuration files and establish ownership/rollback before any mutation.
