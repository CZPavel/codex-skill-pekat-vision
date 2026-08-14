from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".github" / "skills" / "pekat-vision"
VERSION_CONTEXT = SKILL / "references" / "version-context.md"


def _contract() -> dict:
    text = VERSION_CONTEXT.read_text(encoding="utf-8")
    blocks = re.findall(r"```yaml\s*(.*?)```", text, flags=re.DOTALL)
    documents = [yaml.safe_load(block) for block in blocks]
    matches = [
        document["pekat_4_0_1_parallelism_contract"]
        for document in documents
        if isinstance(document, dict)
        and "pekat_4_0_1_parallelism_contract" in document
    ]
    assert len(matches) == 1
    return matches[0]


def test_custom_context_join_contract_is_not_a_writer_or_consensus_merge():
    contract = _contract()
    custom = contract["custom_context"]
    assert custom["sequential_propagation"] == "runtime_verified"
    assert custom["true_multi_branch_join"] == "branch_changes_not_propagated"
    assert custom["equal_values_consensus_merge"] is False
    assert custom["first_or_last_writer"] is False
    assert custom["single_surviving_conditional_gate_branch"] == "propagation_runtime_verified"


def test_empty_gate_and_disabled_branches_remain_distinct():
    branches = _contract()["branches"]
    assert branches == {
        "conditional_gate_false_equals_empty": False,
        "empty_can_pass_original_image": True,
        "empty_contributes_to_custom_multi_branch_join": True,
        "disabled_noop_equals_gate_false": False,
    }


def test_native_results_and_image_raster_are_separate_layers():
    contract = _contract()
    assert contract["native_results"] == {
        "use_result_for_parallel_ok_nok": True,
        "detections_classes_heatmaps_are_custom_context": False,
    }
    assert contract["image"]["native_overlay_automatically_rasterized"] is False
    assert contract["image"]["standard_crop_mapping"] == "practical_observation"
    assert contract["image"]["arbitrary_transform_mapping"] == "verify_or_transform_coordinates"


def test_globaldata_is_not_claimed_as_a_parallel_merge_workaround():
    assert _contract()["globaldata"] == {
        "concurrent_write_semantics": "open",
        "automatic_parallel_merge_workaround": False,
    }


def test_unresolved_parallelism_cases_are_machine_readable():
    assert set(_contract()["open"]) == {
        "zero_surviving_gate_branches",
        "branch_local_a1_to_a2",
        "generalized_native_result_merge",
        "arbitrary_geometry_remap",
    }


def test_public_guidance_does_not_leak_private_runtime_provenance():
    public_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in SKILL.rglob("*")
        if path.is_file()
    ).lower()
    forbidden = (
        "src-pekat401-parallelism",
        "pekat401_parallelism_context_image_runtime_report",
        "c:\\users\\p_j",
        "\\downloads\\",
        "reverse engineering report",
    )
    assert all(term not in public_text for term in forbidden)
