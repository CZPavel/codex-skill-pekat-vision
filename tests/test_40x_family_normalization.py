import copy
import json
from pathlib import Path

import pytest

from generate_code_module import ModuleSpec, ModuleSpecError


ROOT = Path(__file__).resolve().parents[1]


def common_form_spec(version: str) -> dict:
    value = json.loads((ROOT / "tests" / "fixtures" / "module_spec_4_0_3.json").read_text(encoding="utf-8"))
    value["target_version"] = version
    return value


def test_401_and_403_use_one_common_40x_form_serializer() -> None:
    payload_401 = ModuleSpec.from_mapping(common_form_spec("4.0.1")).build_payload(epoch_ms=1700000000000)
    payload_403 = ModuleSpec.from_mapping(common_form_spec("4.0.3")).build_payload(epoch_ms=1700000000000)
    normalized_401 = copy.deepcopy(payload_401)
    normalized_403 = copy.deepcopy(payload_403)
    normalized_401.pop("version")
    normalized_403.pop("version")
    assert normalized_401 == normalized_403


def test_40x_visibility_and_403_narrow_acceptance_boundary_remain_explicit() -> None:
    value = common_form_spec("4.0.1")
    value["form"][0]["visibility"] = "conditional"
    with pytest.raises(ModuleSpecError, match="4.0.x"):
        ModuleSpec.from_mapping(value)
    value = common_form_spec("4.0.3")
    value["form"] = []
    with pytest.raises(ModuleSpecError, match="form-bearing"):
        ModuleSpec.from_mapping(value)
    value = common_form_spec("4.1.0")
    with pytest.raises(ModuleSpecError, match="unsupported PEKAT version"):
        ModuleSpec.from_mapping(value)
