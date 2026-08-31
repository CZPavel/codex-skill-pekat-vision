# Exact PEKAT VISION 4.0.3 source state

This reference separates stored evidence from runtime truth. It does not authorize a provider, camera or project write.

## Stored mappings

| Meaning | Exact stored field | Boundary |
|---|---|---|
| Analyze incoming images | `running.processing` | Not auto capture/save |
| Save incoming images / auto capture | `running.save` | Not Project Production/Simulation |
| Folder Production/Simulation | `camera.imageFolderWatcher.simulationMode` | Folder source only: `false` Production, `true` Simulation |
| Live Stream persistent flag | `camera.cameraIsRunning` | Not proof of acquisition |

Also inspect source/provider, `currentCamera`, `cameraStatus`, Folder path, Analyze existing, Delete images, configured port and the process/port/`/ping` evidence separately.

```text
PROJECT SERVER RUNNING
!= CAMERA CONNECTED
!= CAMERA INITIALIZED
!= CAMERA ACQUIRING
!= FLOW EVALUATING
```

There is no universal `running` boolean. Stored/persistent configuration is not runtime truth.

## Project Production/Simulation boundary

No separate supported project-wide Production/Simulation control was proved for exact 4.0.3. Do not map `running.save`, Folder `simulationMode`, or `context["production_mode"]` to a project-wide mode. The tested `running.save false -> true -> false` change did not change `context["production_mode"]`.

Treat project-wide mode as `UNSUPPORTED_CONTRACT_GAP`. Reopen only for a changed PEKAT build or new concrete vendor/UI evidence; do not infer a writer from readable state.

## Safe inspection

```powershell
python scripts/analyze_source_state_403.py <project>
```

The helper is exact-4.0.3 version-gated and uses only the bundled restricted primitive/container Pickle parser on `camera.db` and `running.db`. It never uses `pickle.load`, PEKAT, Socket.IO or network access. Its runtime section is intentionally `not_checked`/`unknown_live_state`.

## Provider and stale-status safety

Do not switch a selected physical camera to Folder as a troubleshooting step unless the original camera selection can demonstrably be restored. An unavailable device can make that transition non-reversible. Direct database repair is not a supported recovery method.

`camera.status.notAvailable` may remain a stale persisted/UI inconsistency even when process, port, `/ping` or source evidence differs. Diagnose each layer; do not directly edit a database to normalize the status.
