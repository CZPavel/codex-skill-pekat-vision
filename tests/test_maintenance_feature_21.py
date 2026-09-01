from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".github" / "skills" / "pekat-vision"


def test_smart_mask_is_not_routed_as_flow_mask_or_backend_proof() -> None:
    text = (SKILL / "references" / "dataset-model-inspection.md").read_text(encoding="utf-8")
    assert "Smart Mask" in text and "not a FLOW `MASK`" in text
    assert "does not prove a runtime backend SAM2" in text
    assert "Do not automate Smart Mask or rectangle writes" in text


def test_flow_mask_taxonomy_keeps_static_dynamic_and_heatmap_boundary() -> None:
    text = (SKILL / "references" / "dataset-model-inspection.md").read_text(encoding="utf-8")
    assert "Static/manual FLOW `MASK`" in text and "COCO compressed RLE" in text
    assert "Result-driven FLOW `MASK`" in text and "arbitrary incoming heatmaps" in text


def test_train_test_and_training_quiescence_remain_non_writer_knowledge() -> None:
    text = (SKILL / "references" / "dataset-model-inspection.md").read_text(encoding="utf-8")
    assert "not\nindependent manually editable memberships" in text
    assert "Live\nStream blocks the editor body" in text
    assert "Neither proves a backend `detector_start_training` rejection" in text


def test_dataset_reference_is_retrievable_from_skill_and_has_exact_version_boundary() -> None:
    workflow = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    text = (SKILL / "references" / "dataset-model-inspection.md").read_text(encoding="utf-8")
    assert "inspect_dataset_model.py" in workflow
    assert "exact-4.0.3" in text
    assert "no image upload, tag editor, image delete, annotation, or direct database\nwriter" in text
