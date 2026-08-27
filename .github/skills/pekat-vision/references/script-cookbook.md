# Minimal PEKAT Code cookbook

These are small patterns, not universal modules. Select the exact-version entrypoint from `version-context.md`; examples without Form use `main(context)`. Declare Context inputs/outputs and side effects. Prefer a native PEKAT tool/Gate before Code.

Before importing a non-standard library, route the exact PEKAT 4.0.x target
through `code-runtime-pekat401.md` or `code-runtime-pekat403.md`. Prefer native PEKAT → simple FLOW → NumPy/OpenCV →
SciPy/skimage/sklearn → bounded communication → heavy ML/GPU → a new dependency.
For `.ptool`/`.pmodule`, apply the external dependency rule in
`code-library-installation.md`.

## Stop the current branch

STOP_IF_OK:

```python
def main(context):
    if context.get("result") is True:
        context["exit"] = True
```

STOP_IF_NOK:

```python
def main(context):
    if context.get("result") is False:
        context["exit"] = True
```

Custom branch condition:

```python
def main(context):
    if context.get("still_ok") is True:
        context["exit"] = True
```

`exit=True` terminates only the current branch in Parallelism. Distinguish explicit `True`, `False`, and possible `None`.

## Conditional FLOW with a custom Context flag

```python
def main(context):
    detections = context.get("detectedRectangles", [])
    context["has_candidates"] = isinstance(detections, list) and bool(detections)
```

Route later work with a native Filter/Conditional Gate over `has_candidates`. Document who creates/resets the flag; Context is per evaluation.

In PEKAT 4.0.1, this custom flag is safe for downstream sequential steps. Do not expect a branch-local flag to survive a true multi-branch Parallelism join. For mutually exclusive routing, place the Conditional Gate before branch work and ensure exactly one branch continues. For parallel inspection OK/NOK, prefer native `result` rather than custom A/B booleans.

## GlobalData within one PEKAT 4 project

```python
def main(context):
    global_data = context.get("globalData")
    if not isinstance(global_data, dict):
        context["code_error"] = "globalData unavailable"
        return
    global_data["accepted_count"] = int(global_data.get("accepted_count", 0)) + 1
```

Use only for 4.x where the exact contract is confirmed. It is not Cross-PEKAT
or durable storage: values persist only in the same project-server process and
reset on project restart. Do not use GlobalData automatically to work around
custom Context behavior at a parallel join.

For Parallelism, use branch-owned keys and merge explicitly:

```python
def main(context):
    global_data = context.get("globalData")
    if not isinstance(global_data, dict):
        context["code_error"] = "globalData unavailable"
        return
    global_data["branch_a_result"] = context.get("result")
```

Independent keys may survive in exact 4.0.3 tests. Same-key collision was
branch-order dependent rather than wall-clock dependent, so never use a shared
key as an automatic last-finisher merge.

## Read the Classifier winner

Recommended PEKAT 4 Classifier extraction:

```python
def main(context):
    rectangles = context.get("detectedRectangles")
    if not isinstance(rectangles, list) or not rectangles:
        context["classifier_label"] = None
        return
    rect = rectangles[0] if isinstance(rectangles[0], dict) else {}
    classes = rect.get("classNames", []) or []
    winner = classes[0] if classes else None
    label = winner.get("label") if isinstance(winner, dict) else None
    context["classifier_label"] = label
```

`classNames` may contain every candidate. The reproduced PEKAT 4 winner is the
first element, so `any(c.get("label") == wanted for c in classes)` is an
anti-pattern for winner selection. Keep Classifier ranking separate from
Detector semantics and confirm producer-specific rectangle structure.

## Filter detections defensively

```python
def main(context):
    detections = context.get("detectedRectangles")
    if not isinstance(detections, list):
        context["code_error"] = "detectedRectangles is not a list"
        return
    kept = []
    for item in detections:
        if not isinstance(item, dict):
            continue
        try:
            confidence = float(item.get("confidence", 0))
        except (TypeError, ValueError):
            continue
        if confidence >= 0.8:
            kept.append(item)
    context["detectedRectangles"] = kept
```

Confirm producer-specific keys and whether changing detections should also change `result`; do not couple them accidentally.

## Result handling

Diagnostic capture without mutation:

```python
def main(context):
    value = context.get("result")
    context["result_state"] = "OK" if value is True else "NOK" if value is False else "UNSET"
```

Only if the explicit business rule owns final result:

```python
def main(context):
    context["result"] = context.get("required_feature_count") == 1
```

Place result ownership and any Gate/Parallelism merge behavior in the FLOW contract.

## Simple image operation

```python
def main(context):
    image = context.get("image")
    if image is None or not hasattr(image, "copy"):
        context["code_error"] = "missing image"
        return
    context["image"] = image.copy()
    context["code_status"] = "image copied"
```

This preserves dtype/shape. In PEKAT 4.0.1 a direct sequential test also
confirmed that a new ndarray with a different shape propagates to the next Code
tool. A bounded resize pattern is therefore valid when the changed resolution
is intentional:

```python
import cv2


def main(context):
    image = context.get("image")
    if image is None or getattr(image, "ndim", 0) not in {2, 3}:
        context["code_error"] = "invalid image"
        return
    output = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    context["image"] = output
    context["image_shape"] = tuple(output.shape)
```

Confirm dtype/channel contract and every downstream consumer. This changed-shape
evidence is sequential. In Parallelism, an empty branch may intentionally preserve
the original/pre-transform raster while other branches crop or preprocess for
native detection. Native boxes/heatmaps remain overlays unless Code explicitly
draws them into pixels. Prefer a native PEKAT operation when it already provides
the required transform; verify coordinates after rotation, Unifier, custom resize
or warp.

## Explicit image save side effect

```python
from pathlib import Path
import cv2


def main(context, form):
    values = form if isinstance(form, dict) else {}
    output_dir = values.get("output_dir")
    image = context.get("image")
    if not output_dir or image is None:
        context["save_status"] = "not configured"
        return
    destination = Path(str(output_dir)) / "inspection.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(destination), image):
        context["save_status"] = "write failed"
        return
    context["save_status"] = "written"
```

Use only when a filesystem write is requested and authorized. Replace the naming/collision/retention policy for the real application; do not embed a customer path. Prefer native Image Saver when it meets the need. Exact 4.0.3 evidence covers native `ALL` + local + `by_days` + `image_only`: the root must already exist, a missing root may be reported only in project logs, and HTTP/context success does not prove persistence. Do not claim the untested OK/NOK, overlay/rectangle, heatmap, or exact source-versus-processed matrix.

## Folder provider filename

In exact PEKAT 4.0.3 Folder-provider F1/F2/F3 tests, `context["data"]`
was a filename-only `str`, not a full path or structured object:

```python
def main(context):
    name = context.get("data")
    if not isinstance(name, str) or not name:
        context["code_error"] = "4.0.3 Folder filename unavailable"
        return
    context["folder_filename"] = name
```

Keep this scoped to the tested 4.0.3 Folder provider. Do not reconstruct or
trust a filesystem path without an independently configured, validated root.

## Barcode add-on boundary

Recipes using `zxingcpp` or `pyzbar` **require a local add-on dependency**.
Neither is bundled: both were locally added in tested 4.0.1 and both were
`NOT_PRESENT` in clean tested 4.0.3. A `.ptool` does not carry them. Before use,
follow `code-library-installation.md` and verify import plus one bounded decoder
call inside the exact destination Code runtime.

## Own neural inference

Do not assume `onnxruntime`. In clean tested 4.0.3, Torch 2.7.1+cu128 completed
a real CUDA calculation, FAISS 1.14.1 passed CPU add/search, ONNX 1.20.1 passed
model create/check/serialize only, and TensorRT 10.13.0.35 passed Runtime object
creation only. Choose a path from the exact proven operation, not package name
presence, and keep the Code wrapper small rather than creating a general model
orchestration framework.

## Form normalization

Copy only the required helper from `scripts/form_normalization.py`:

```python
def main(context, form):
    values = form if isinstance(form, dict) else {}
    try:
        raw = values.get("threshold", 12)
        if isinstance(raw, bool):
            raise ValueError
        threshold = float(raw)
        if not 0 <= threshold <= 255:
            raise ValueError
    except (TypeError, ValueError):
        context["code_error"] = "threshold outside 0..255"
        return
    context["threshold_used"] = threshold
```

PEKAT 4.0.1 number defaults may be strings and edited values integers; select defaults may be index strings and edited values text.

## Cross-PEKAT state

Use the exact installed-version `pekat_communication.PEKAT` contract. Keep client registration/remote update in a bounded adapter, expose connection/freshness state, and render it as a dependency outside local FLOW. Do not fabricate API arguments from a historical script and do not substitute local GlobalData.

## IFM read/write pointer

For PEKAT Code, first discover the AL13xx master/port/device identity and preserve raw PDIn plus quality. Decode only from the exact IODD. Default writes to locked/dry-run and route detailed AL1304/AL1306, O1D110, DV2131, OPD101, PDOut/ISDU work to `ifm-io-link` when available. See `industrial-hardware.md`.

## Historical anti-patterns

Do not use historical owner scripts as defaults when they contain process-global `__main__` state, hard-coded paths/endpoints, unbounded I/O, direct detection `[0]`, direct `form[...]`, mixed `operatorInput`/Form, hidden writes, or implicit result changes. Extract only the smallest validated behavior required by the current FLOW.

Legacy catalog IDs retained for regression routing: `03_script_cookbook_module_schema`, `curated-script-pyzbar-barcode-reader`.
