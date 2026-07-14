# Form Editor and ModuleSpec

## Contents

- [Entrypoints](#entrypoints)
- [ModuleSpec](#modulespec)
- [Form items](#form-items)
- [Envelope](#envelope)
- [Generation](#generation)

## Entrypoints

Use this pattern when a form exists:

```python
def main(context, form=None):
    values = form or {}
    threshold = float(values.get("threshold", 0.5))
    context["threshold_used"] = threshold
```

Without Form Editor items, `main(context)` is valid. Form values are not `context["operatorInput"]`. Sources: `[pekat-kb-3-19-3-page-1262551042]`, `[pekat-kb-4-0-1-page-1513132287]`, `[pekat-module-export-schema-v1]`.

## ModuleSpec

```json
{
  "target_version": "4.0.1",
  "label": "Threshold example",
  "note": "Isolated fixture",
  "source_code": "def main(context, form=None):\n    values = form or {}\n    context['threshold_used'] = float(values.get('threshold', 0.5))\n",
  "form": [],
  "form_values": {},
  "show_image_preview": true,
  "is_active": true
}
```

Required fields are `target_version`, `label`, and `source_code`. Optional `module_id` must be an integer. `formValues` may only contain declared `formKey` names.

## Form items

All items contain `type`, `formKey`, `label`, `defaultValue`, and optional `visibility`.

- `text`: default is a string.
- `number`: default accepts a number/numeric string and normalizes to a number; optional `min`/`max` must be ordered.
- `checkbox`: default/value normalizes to boolean.
- `select`: `options` is a non-empty semicolon-separated string; default/value must match an option.

Form keys are unique identifiers matching `^[A-Za-z_][A-Za-z0-9_]*$`.

## Envelope

The output contains `type="CODE"`, `module`, and exact `version`. Module data contains `label`, integer `id`, `type="CODE"`, `note`, `sourceCode`, `form`, `formValues`, `gpuSettings=[]`, `softDeletedDate=null`, integer `editDate`, `showImagePreview`, and `isActive`.

Routing is strict:

- `3.19.3` -> UTF-8 JSON `.pmodule`
- `4.0.1` -> UTF-8 JSON `.ptool`

IDs are monotonic epoch-millisecond integers. Static validation does not prove PEKAT UI compatibility.

## Generation

```powershell
python scripts/generate_code_module.py spec.json --output build/my_module
```

The extension is derived from `target_version`. Validate the result with `references/module_spec.schema.json`, then import it only into a new isolated project and perform display/edit/run/export round-trip testing.
