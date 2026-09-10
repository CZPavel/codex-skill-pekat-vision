# Training-history diagnostics (exact PEKAT 4.0.3)

## Safe helper

Use the bundled standalone analyzer before writing a parser:

```powershell
python scripts/analyze_training_history.py <project> --family detector
python scripts/analyze_training_history.py <project> --family detector --model-id 42 --output <outside-project>\training.json
```

It is version-gated to an explicit `pekat_package.json` version of 4.0.3 and
uses the restricted non-executing protocol-4 Pickle reader. Supported registry
routes are Detector, Classifier, Supervised, Anomaly/Unsupervised and OCR. The
families deliberately remain separate because their fields, artifact layouts,
metrics and annotation contracts are not interchangeable.

The helper may parse numeric `step.csv`, an explicit registry `loss` list and
bounded JSON metadata. It inventories `.pt`, `.pth`, `.tm`, `.npy` and `.npz`
files by relative path and size only. It never imports PEKAT, executes stored
Code, loads model weights or deserializes binary model/array artifacts. Report
output is rejected when it resolves inside the PEKAT project.

Persisted evidence observed in the tested exact-4.0.3 models differs by family:

| Family | Persisted history boundary |
|---|---|
| Detector | registry `loss`/`lossCount`; named `step.csv` fields `epoch,box,cls,dfl` |
| Classifier | no per-step curve in the tested model |
| Supervised | headerless five-column `step.csv`; meaning remains unknown and is reported only as `column_N` |
| Anomaly/Unsupervised | no persisted loss curve in the tested model |
| OCR | no per-step history in the tested model |

Do not use Detector field names to identify a particular YOLO version. `data.json`
is metadata, not training history, and automatic best-validation-epoch selection
is not generally available from the currently established evidence.

## Evidence and interpretation rules

- Preserve source provenance for every curve and metric. A column name states
  a field label, not undocumented PEKAT semantics or cadence.
- Completed-model train/test IDs are training-derived provenance, not editable
  membership controls.
- A training loss series alone is descriptive. It cannot establish validation
  divergence, generalization, overfitting or production acceptance.
- Only compare train and validation curves when their provenance, metric,
  direction and step alignment match. Shape classifications are compatible
  evidence, never proof.
- Flat curves can be compatible with underfitting; a widening train/validation
  gap can be compatible with overfitting; repeated validation reversals can be
  compatible with noise. Check split leakage, representativeness, label quality,
  class balance and independent examples before changing training.
- Final evaluation metrics do not replace per-class error review or an
  independent representative holdout.
- Classification threshold selection is an evaluation/deployment decision, not
  evidence that training improved. For imbalanced classes inspect precision,
  recall and their trade-off rather than accuracy alone.
- Before changing a model, review annotation consistency, acquisition settings,
  optics/lighting, product mix and domain shift between training, validation and
  production images.
- Early stopping is a next-run control only when a compatible validation metric
  and exact family parameter contract exist; it is not inferred from training
  loss or used to rewrite a completed model.

If the required validation series or metric definition is absent, return
`INSUFFICIENT_EVIDENCE`/`TRAIN_LOSS_ONLY` and recommend the smallest next
read-only check. Never invent hyperparameter ranges, start/stop training,
activate/delete models, or treat Stop as rollback.

## Model lifecycle boundary

Exact 4.0.3 evidence can describe stored model status, progress, timestamps,
configuration, resolved image provenance, evaluation metadata and artifact
presence. It does not expose the backend-created job identity, start/stop
writer, activation writer, delete cleanup or artifact/runtime binding contract.
Those remain intentionally unsupported in this public skill.

Progress scale and terminal success are family-specific: do not normalize
progress across families. An acknowledgement is not the created model identity;
terminal success requires correlated registry, artifact and error evidence for
that family. A timeout is neither automatic failure nor authorization to Stop,
and Stop is not a universal rollback. Annotation preparation is not training.
Model selection, activation and training can affect production behavior; model
deletion has no general safe public capability here.

## General diagnostic references

The interpretation discipline is consistent with learning-curve and
cross-validation guidance in scikit-learn, precision-recall evaluation for
imbalanced classification, and established learning-curve/early-stopping
literature. These general sources do not define PEKAT persistence:

- https://scikit-learn.org/stable/modules/learning_curve.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html
- https://arxiv.org/abs/1405.0312
