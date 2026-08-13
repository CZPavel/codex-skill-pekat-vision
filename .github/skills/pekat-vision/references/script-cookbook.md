# Minimal PEKAT Code cookbook

These are small patterns, not universal modules. Select the exact-version entrypoint from `version-context.md`; examples without Form use `main(context)`. Declare Context inputs/outputs and side effects. Prefer a native PEKAT tool/Gate before Code.

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

## GlobalData within one PEKAT 4 project

```python
def main(context):
    global_data = context.get("globalData")
    if not isinstance(global_data, dict):
        context["code_error"] = "globalData unavailable"
        return
    global_data["accepted_count"] = int(global_data.get("accepted_count", 0)) + 1
```

Use only for 4.x where the exact contract is confirmed. It is not Cross-PEKAT. Define initialization and reset; restart/concurrent-write behavior remains an acceptance gate.

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

This preserves dtype/shape. Add an actual transform only after confirming channel count, dtype/range and whether a native PEKAT tool already provides it.

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

Use only when a filesystem write is requested and authorized. Replace the naming/collision/retention policy for the real application; do not embed a customer path. Prefer native Image Saver when it meets the need.

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
