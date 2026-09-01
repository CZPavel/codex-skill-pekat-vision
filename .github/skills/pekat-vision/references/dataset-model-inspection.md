# Dataset, Image Library, and model inspection (exact 4.0.3)

## Safe offline helper

Use the packaged helper before writing an ad-hoc parser:

```powershell
python scripts/inspect_dataset_model.py <project-directory> --output dataset-model-report.json
```

It supports an explicit `pekat_package.json` version of **4.0.3** only. It
uses the bundled non-executing protocol-4 Pickle reader on an allowlist of
image, tag, module, and model registries. It reports image/tag inventory,
model records, train/test provenance, bounded Detector annotation rows and
`ABSENT` / `PRESENT_EMPTY` / `PRESENT_NONEMPTY` serialized annotation states.
It also lists Detector artifact-relative paths and sizes; SHA-256 is produced
only for files at most 1 MiB. It never loads model weights.

The helper is read-only. Keep an output file outside the project directory if
the project must remain byte-for-byte unchanged.

## Image Library and tags

Image/tag/model inventory is read knowledge. Exact 4.0.3 Assistant evidence
also established a narrow one-local-PNG, empty-tags workflow, but that accepted
Assistant automation is **not** a public skill executor. This public skill has
no image upload, tag editor, image delete, annotation, or direct database
writer. In particular, generic existing-image deletion is intentionally
unsupported.

## Train/test provenance

`TRAIN_RATIO`, `TRAIN_TAGS`, `TEST_TAGS`, and `DATA_SPLIT_SEED` are training
configuration inputs. A completed model can retain `trainingImages` and
`testImages`; those are the resolved training-derived provenance snapshot, not
independent manually editable memberships. The inspector recognizes observed
alias fields, reports the selected source field, and fails closed when aliases
conflict. It does not produce a train/test writer.

Known exact-4.0.3 Detector configuration includes `IMG_WIDTH`, `IMG_HEIGHT`,
`ITERS`, `MODEL_TYPE`, `MOSAIC`, and `SCALE_FACTOR`, as well as the split and
tag controls above. Other augmentation controls (flip/shear/rotate/brightness/
contrast/saturation and classification/helper options) must be read from the
target UI/version; this reference does not invent ranges or defaults.

## Detector annotations and Smart Mask

The observed 4.0.3 Detector ground truth is a rectangle record. A fresh Image
Library image can have an `ABSENT` `imageRectangles[imageId]` key. The UI can
send `[]` after deleting a final rectangle, but retained evidence does not show
whether the backend persists that as `PRESENT_EMPTY` or prunes it to `ABSENT`.
That distinction is forensic read knowledge, not a safe writer recipe.

Detector **Smart Mask** is an editor annotation assist: user point/click ->
segmentation proposal -> local bounding-box preview -> user-confirmed Detector
rectangle. It is not a FLOW `MASK`. SAM2 association is USER_OBSERVED plus
packaged-installation evidence; it does not prove a runtime backend SAM2
handler or no-write semantics. Do not automate Smart Mask or rectangle writes.

## Model lifecycle and artifacts

The standard exact-4.0.3 new-Detector-training request starts with
`modelId: null`; configuration is already stored in the module. Completed
records can contain status, progress, `trainingParams`, `trainingImages`,
`testImages`, and evaluation. Observed project-local artifacts can include
`detector/models/<modelId>/best.pt`, `last.pt`, `data.json`, and `step.csv`.

The backend-created model/job identity, model delete cleanup, module binding
cleanup, and stop-as-rollback semantics are unproven. Do not start training,
activate/delete a model, load weights, or treat stop as rollback.

## Training workflow and quiescence

The normal GUI workflow is: edit Detector -> Detector editor -> Training tab ->
configure -> start training. Exact static 4.0.3 evidence shows a running Live
Stream blocks the editor body and offers Turn Off. The broader requirement to
turn off Analyze Incoming before edit/training is USER_OBSERVED workflow
choreography. Neither proves a backend `detector_start_training` rejection.

## Mask taxonomy

- **Static/manual FLOW `MASK`:** historical exact-4.0.1 `heatmap=false` with
  COCO compressed RLE.
- **Result-driven FLOW `MASK`:** historical exact-4.0.1 `heatmap=true` and
  `rle=null`, using incoming `detectedRectangles`. It does not prove support
  for arbitrary incoming heatmaps.
- **Detector Smart Mask:** editor assist, not FLOW MASK.
- **Supervised mask:** a distinct family-specific annotation/training contract.
