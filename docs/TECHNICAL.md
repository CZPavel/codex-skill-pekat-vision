# PEKAT Vision - Technical notes for agent integration

Last verified: 2026-02-15

Primary public sources:
- https://pekat-vision.github.io/pekat-vision-sdk-python/
- https://pypi.org/project/pekat-vision-sdk/
- https://github.com/pekat-vision/pekat-vision-sdk-python
- https://github.com/pekat-vision/pekat-vision-examples

## 1) Code module runtime contract
- Use Python entrypoint: `main(context, module_item=None)`.
- Treat `context` as mutable shared structure flowing through modules.
- Keep existing key types stable:
  - `context["image"]` should stay `np.ndarray`
  - `context["detectedRectangles"]` should stay list-like
  - `context["result"]` should stay bool-like
- Guard every optional key with `.get(...)` or explicit checks.

## 2) REST API contract (current SDK-aligned behavior)
Common endpoints:
- `POST /analyze_image`
- `POST /analyze_raw_image?height=<h>&width=<w>`
- `POST /analyze_image_shared_memory` (local workflows, PEKAT >= 3.18)
- `GET /ping`
- `GET /stop`

Useful query args:
- `response_type=context|image|annotated_image|heatmap`
- `data=<string>` (available in flow under `context["data"]`)
- `context_in_body` flag

Response parsing:
- `response_type=context` -> JSON body only.
- `context_in_body=true` -> read `ImageLen` header, split body to image bytes + JSON text.
- `context_in_body=false` -> image bytes in body, context in `ContextBase64utf` header.

## 3) SDK specifics worth reflecting in generated code
- Package version currently available on PyPI: `pekat-vision-sdk==2.3.2`.
- SDK uses `requests.Session` and defaults to explicit request timeout handling.
- SDK supports analyze by file path, bytes, numpy array, and shared memory optimization.

## 4) Projects Manager integration
Known patterns in existing PEKAT materials/examples include:
- HTTP list endpoint on port 7000 (environment dependent).
- Simple TCP command workflows such as `start:`, `stop:`, `status:`, `switch:`.

Because deployment variants exist, generated integrations should:
- make host/port configurable,
- fail gracefully on unsupported command responses,
- include reconnect and timeout strategy.

## 5) External library deployment to PEKAT server
Preferred procedure:
1. Build package payload for matching platform/Python ABI:
   - `pip install --target <folder> <package>`
2. Copy payload into PEKAT server directory.
3. Import directly, or append path to `sys.path` when needed.

Warnings:
- Native wheels (`.pyd`/`.so`) must match target OS + architecture.
- Keep heavy ML runtimes external where possible and call via HTTP/CMD.
