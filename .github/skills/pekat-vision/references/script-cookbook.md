Document ID: [03_script_cookbook_module_schema]

> Public-safe curated derivative. Facts cite document IDs in square brackets; an inference is explicitly labeled. Never substitute this file for the exact device/runtime manual.

# Script cookbook and module export schema

## Safe generation contract

Ask for target version, flow position, input/output context keys, image dtype/shape, result semantics, permitted external libraries and whether device writes are allowed. Default to no device writes. Return standalone Python, a form table, a generated import file, and isolated import/test instructions.

The catalog below is a static description of owner-provided legacy examples, not an endorsement of every dependency or state pattern. Do not copy `__main__` state, private endpoints, unchecked device writes, or legacy signatures into new code. Rebuild each solution under the v2 rules in `SKILL.md`.

An export contains `type=CODE`, `module`, `version`; module fields include label/id/type/note/sourceCode/form/formValues/gpuSettings/softDeletedDate/editDate/showImagePreview/isActive. `number` accepts numeric source strings but exports normalized numeric values; checkbox is boolean; select default/value must match an option. [pekat-module-export-schema-v1]

## Curated catalog

### AI_TRIGGER_V06_TESTED [curated-script-ai-trigger-v06-tested]

Trigger an AI/remote inference branch with diagnostics. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `ai_trigger_state, exit`. Dependencies: `__main__`. Risks: Context schema and image dtype must be verified in an isolated project.

### AUTO_HDR [curated-script-auto-hdr]

Create an HDR-like image representation. Flow: Code module; confirm ordering from required context reads and writes. Reads: `image, operatorInput`. Writes: `auto_exposure_error, image`. Dependencies: `__main__, cv2, numpy`. Risks: Context schema and image dtype must be verified in an isolated project.

### CUT_ON_DETECTED [curated-script-cut-on-detected]

Crop an image around detected rectangles. Flow: Code module; confirm ordering from required context reads and writes. Reads: `detectedRectangles, image`. Writes: `exit, image, image_original`. Dependencies: `cv2, numpy, skimage`. Risks: Context schema and image dtype must be verified in an isolated project.

### DEL_CLASS [curated-script-del-class]

Filter detections by class. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `detectedRectangles, heatmaps, rectangles_mode, rectangles_remaining, rectangles_removed`. Dependencies: `typing`. Risks: Context schema and image dtype must be verified in an isolated project.

### FLOW_ON_DETECTED [curated-script-flow-on-detected]

Select flow routing from detections. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `exit`. Dependencies: `runtime only`. Risks: Context schema and image dtype must be verified in an isolated project.

### LOGO_DATE_TIME_TO_IMAGE [curated-script-logo-date-time-to-image]

Overlay logo/date/time information. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `image, overlay_info`. Dependencies: `__main__, cv2, datetime, numpy`. Risks: Context schema and image dtype must be verified in an isolated project.

### MEASURE_DETECTED_DISTANCE [curated-script-measure-detected-distance]

Measure distances between detections. Flow: Code module; confirm ordering from required context reads and writes. Reads: `measurement`. Writes: `distance_mm, distance_px, image, label_measurement, measurement, result, signed_distance_mm, signed_distance_px`. Dependencies: `__main__, cv2`. Risks: Changes context['result']; place deliberately in the flow.

### OVLADANI_MAJAKU_IFMDV2131 [curated-script-ovladani-majaku-ifmdv2131]

Control an IFM DV2131 signal light through an IO-Link master. Flow: Code module; confirm ordering from required context reads and writes. Reads: `result`. Writes: `none detected`. Dependencies: `requests`. Risks: Original contained a private IP; curated variant uses TEST-NET 192.0.2.10. Network/device operations require timeout, error handling, dry-run and operator approval.

### PYZBAR_BARCODE_READER [curated-script-pyzbar-barcode-reader]

Read barcodes; legacy pyzbar example, prefer zxing-cpp where available. Flow: Code module; confirm ordering from required context reads and writes. Reads: `barcode, barcode_debug, image`. Writes: `barcode, barcode_debug`. Dependencies: `cv2, datetime, numpy, os, pyzbar.pyzbar, time`. Risks: pyzbar may require an external native ZBar DLL; prefer the runtime-matched zxing-cpp wheel.

### RESULT_FILTER [curated-script-result-filter]

Filter or aggregate result state. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `false_counter, final_result, result, true_counter`. Dependencies: `__main__`. Risks: Changes context['result']; place deliberately in the flow.

### RESULT_MAKER [curated-script-result-maker]

Set result state from context conditions. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `result`. Dependencies: `runtime only`. Risks: Changes context['result']; place deliberately in the flow.

### ROZSIRENI_SNIMKU_OKRAJE [curated-script-rozsireni-snimku-okraje]

Pad image borders. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `image, label_border_error, label_image_size`. Dependencies: `cv2, numpy`. Risks: Context schema and image dtype must be verified in an isolated project.

### SAVE_IMAGE_OKNOK_SIMPLE [curated-script-save-image-oknok-simple]

Save images according to OK/NOK result. Flow: Code module; confirm ordering from required context reads and writes. Reads: `detectedRectangles, image, result`. Writes: `none detected`. Dependencies: `cv2, datetime, numpy, os, time`. Risks: Context schema and image dtype must be verified in an isolated project.

### SAVE_IMAGE_W_ANOT_OKNOK [curated-script-save-image-w-anot-oknok]

Save annotated OK/NOK images. Flow: Code module; confirm ordering from required context reads and writes. Reads: `detectedRectangles, image, result`. Writes: `none detected`. Dependencies: `cv2, datetime, numpy, os, time`. Risks: Context schema and image dtype must be verified in an isolated project.

### SJEDNOCENI_2_UNIFIER [curated-script-sjednoceni-2-unifier]

Unify two processing branches. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `image`. Dependencies: `cv2, math, numpy`. Risks: Context schema and image dtype must be verified in an isolated project.

### SOBEL_IMAGE_FILTER [curated-script-sobel-image-filter]

Apply a Sobel image filter. Flow: Code module; confirm ordering from required context reads and writes. Reads: `image`. Writes: `image`. Dependencies: `cv2, numpy`. Risks: Context schema and image dtype must be verified in an isolated project.

### STOP_IF_NOK [curated-script-stop-if-nok]

Stop/reroute when result is NOK. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `exit`. Dependencies: `runtime only`. Risks: Context schema and image dtype must be verified in an isolated project.

### STOP_IF_OK [curated-script-stop-if-ok]

Stop/reroute when result is OK. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `exit`. Dependencies: `runtime only`. Risks: Context schema and image dtype must be verified in an isolated project.

### UNSHARP_LAPLAC [curated-script-unsharp-laplac]

Apply Laplacian/unsharp enhancement. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `image`. Dependencies: `cv2, numpy`. Risks: Context schema and image dtype must be verified in an isolated project.

### VAIT_FOR_BUTTON [curated-script-vait-for-button]

Wait for a device/button state with bounded polling. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `exit`. Dependencies: `requests`. Risks: Original contained a private IP; curated variant uses TEST-NET 192.0.2.10. Network/device operations require timeout, error handling, dry-run and operator approval.

### ZASTAVENI_VETVE [curated-script-zastaveni-vetve]

Stop a flow branch. Flow: Code module; confirm ordering from required context reads and writes. Reads: `none detected`. Writes: `exit`. Dependencies: `runtime only`. Risks: Context schema and image dtype must be verified in an isolated project.
