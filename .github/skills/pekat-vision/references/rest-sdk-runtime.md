# REST, SDK, Projects Manager, runtime, and barcode

## REST

Route endpoints and response fields to the exact PEKAT version. Examples use only `localhost` or TEST-NET.

The official 4.0.1 REST page distinguishes POST image analysis from GET ping/last-image operations. `analyze_image` accepts PNG bytes. `analyze_raw_image` accepts raw NumPy bytes plus required dimensions and optional Bayer information. Documented response types are `context`, `image`, `annotated_image`, and `heatmap`; only one image is sent per request. Source: `[pekat-kb-4-0-1-page-1513133459]`.

For PNG:

```python
response = requests.post(
    "http://localhost:8080/analyze_image?response_type=context",
    data=png_bytes,
    headers={"Content-Type": "application/octet-stream"},
    timeout=(3.0, 20.0),
)
response.raise_for_status()
```

Guard JSON decoding, response shape, `ImageLen`, `ContextBase64utf`, UTF-8 decoding, and malformed headers. Use `scripts/rest_api_client_demo.py`; it accepts an injected session for mocks.

## SDK and Projects Manager

- Prefer the official version-compatible SDK over custom lifecycle commands.
- Treat project port/path/key as configuration, never as a hard-coded internal identifier.
- `scripts/projects_manager_tcp_demo.py` defaults to `status` only. Start/stop/switch require `allow_mutation=True` and explicit user approval.
- Use socket connect/read timeouts and validate response size/encoding.
- Never start, stop, or switch a running production project during automated tests.

## External libraries and ABI

Native wheels must match the PEKAT embedded Python ABI, Windows architecture, and dependencies. The audited installations reported `cp310` for 3.19.3 and `cp312` for 4.0.1. Re-probe every target; never copy a venv between PCs. Source: `[local-runtime-fingerprint-2026]`.

Stage libraries outside PEKAT, retain hashes and rollback, and test in an isolated project. Do not modify a running runtime. `scripts/add_libs_to_sys_path.py` only validates/adds an explicitly supplied directory; it contains no installation path default.

## Barcode

Prefer a runtime-matched `zxing-cpp` wheel when available. `pyzbar` can require a native ZBar library and is not dependency-free. Test DataMatrix ECC200 and QR samples for rotation, blur, low contrast, empty image, and decode failure. Sources: `[local-runtime-fingerprint-2026]`, `[curated-script-pyzbar-barcode-reader]`.
