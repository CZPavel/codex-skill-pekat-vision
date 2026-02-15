# PEKAT Vision - user workflow for Code module scripts

## 1) Insert Code module in flow
1. Open project.
2. Add module in required position.
3. Select `Enhancements -> Code`.

## 2) Paste script
1. Open `Source Code`.
2. Remove default snippet.
3. Paste script with required entrypoint:
   - `main(context, module_item=None)`

Tip: start from `scripts/code_module_template.py`.

## 3) Configure Form Editor (optional)
1. Add fields in Form Editor (input/select/slider/checkbox).
2. Access values in script via `module_item` dict.

## 4) Validate with Console
Check:
- selected form values,
- printed debug lines,
- final `context` fields.

Do not print full images/large arrays in loops.

## 5) Typical safe patterns
- Early branch stop:
  - set `context["exit"] = True`
- ROI crop:
  - read rectangle from `context["detectedRectangles"]`
  - crop `context["image"]` with bounds clipping
- Conditional save:
  - check `context.get("result")`
  - save NG frame only when needed

## 6) Troubleshooting
- `KeyError` / `IndexError`:
  - missing keys or empty lists
  - add guards and `.get(...)`
- Import error:
  - copy library payload into server path
  - append path to `sys.path` when required
- No visible output change:
  - confirm module order and active branch
  - verify you update `context["image"]` with valid ndarray

## 7) REST client usage
Use `scripts/rest_api_client_demo.py` for external integrations:
- PNG/JPG bytes via `/analyze_image`
- raw numpy bytes via `/analyze_raw_image`
- robust parsing for both context transport variants
