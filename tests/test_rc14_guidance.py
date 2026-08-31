import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / ".github" / "skills" / "pekat-vision"
REFS = SKILL / "references"


def read(relative: str) -> str:
    return (SKILL / relative).read_text(encoding="utf-8")


def compact(text: str) -> str:
    return " ".join(text.split())


def test_403_version_and_clean_runtime_route_are_exact():
    skill = read("SKILL.md")
    runtime = read("references/code-runtime-pekat403.md")
    assert "common `4.0.x` contract with exact `4.0.1`/`4.0.3` evidence" in skill
    for value in (
        "CPython `3.12.12`",
        "`numpy` | `2.4.3`",
        "`cv2` | `4.10.0`",
        "`python-snap7` / import `snap7` | `3.1.0`",
        "`torch` | `2.7.1+cu128`",
        "`tensorrt` | `10.13.0.35`",
    ):
        assert value in runtime
    for missing in ("onnxruntime", "numba", "cupy", "transformers", "ultralytics", "pandas"):
        assert missing in runtime
    assert "no engine build/inference claim" in runtime
    assert "no FAISS GPU-index claim" in runtime
    assert "tooling, not inference" in runtime


def test_classifier_recipe_selects_first_class_not_any_candidate():
    cookbook = read("references/script-cookbook.md")
    assert 'classes = rect.get("classNames", []) or []' in cookbook
    assert "winner = classes[0] if classes else None" in cookbook
    assert 'label = winner.get("label") if isinstance(winner, dict) else None' in cookbook
    assert 'any(c.get("label") == wanted for c in classes)` is an anti-pattern' in compact(cookbook)
    assert "keep Detector" in cookbook or "Detector semantics" in cookbook


def test_barcode_packages_are_local_addons_not_vendor_regression():
    combined = read("references/code-runtime-pekat403.md") + read("references/code-library-installation.md")
    assert "not bundled PEKAT" in combined
    assert "local post-install additions" in compact(combined)
    assert "absent in this clean 4.0.3 baseline" in compact(combined)
    assert "not a vendor regression" in combined
    assert "A `.ptool` carries Code/Form configuration, not arbitrary third-party" in combined


def test_additional_library_workflow_uses_embedded_python_and_records_modification():
    guide = read("references/code-library-installation.md")
    assert "exact embedded Python + current package state" in guide
    assert "minimal approved install" in guide
    assert "import in PEKAT Code" in guide
    assert "minimal functional call in PEKAT Code" in guide
    assert "local-modification record" in guide
    assert "System Python success is not proof" in guide


def test_globaldata_restart_collision_and_inspection_side_effects():
    version = read("references/version-context.md")
    assert "resets on project-server restart" in version
    assert "not durable project storage" in version
    assert "same-key collision was branch-order dependent" in version
    assert "branch-specific keys and explicit merge" in version
    assert "inspection:getContext" in version and "inspection:getFlow" in version
    assert "not behaviorally passive reads" in version


def test_zero_survivor_continues_from_pre_parallel_context():
    version = read("references/version-context.md")
    flow = read("references/flow-database-projects.md")
    assert "zero_surviving_branches: downstream_can_continue_from_pre_parallel_context" in version
    assert "all branches exiting did not automatically terminate the whole FLOW" in flow
    assert "custom Context" in flow and "native" in flow and "raster" in flow


def test_generated_database_and_gate_encoding_stay_internal_and_exact():
    flow = read("references/flow-database-projects.md")
    for token in ("recursive `modules.sort`", "nested Parallelism", "`[]` empty branch", "Detector", "OCR", "`FILTER`", "Mask", "explicit `modelId`"):
        assert token in flow
    assert "classname = local_class_id * 2^42 + source_module_id" in flow
    assert "Do not reverse the IDs" in flow
    assert "exact-version, internal/offline, fixture-backed" in flow
    assert "not a stable public API" in compact(flow)


def test_ptool_403_roundtrip_keeps_the_later_accepted_target_guard():
    module = read("references/module-format.md")
    schema = json.loads((REFS / "module_spec.schema.json").read_text(encoding="utf-8"))
    assert "import → run → export → remove → reimport → run" in module
    assert "orphan direct-import probe did not establish a universal import contract" in compact(module)
    assert '`"visibility": ""`' in module
    assert schema["properties"]["target_version"]["enum"] == ["3.19.3", "4.0.1", "4.0.3"]
    assert "narrow accepted target scope" in module
    assert "no generic module writer" in module


def test_folder_scope_and_native_saver_persistence_contract():
    flow = read("references/flow-database-projects.md")
    cookbook = read("references/script-cookbook.md")
    assert "F1 new-file watcher" in flow
    assert "F2 `analyzeExisting`" in flow
    assert "F3 simulation" in flow
    assert '`context["data"]` was filename-only `str`' in flow
    assert "Keep this scoped to the tested 4.0.3 Folder provider" in cookbook
    assert "`ALL` + local + `by_days` + `image_only`" in flow
    assert "root had to exist and was not auto-created" in flow
    assert "HTTP 200 with `error=false`" in flow
    assert "Transport/analysis success is not persistence success" in flow


def test_rest_403_last_image_quirk_and_readiness_chain():
    rest = read("references/rest-sdk-runtime.md")
    diagnostics = read("references/project-diagnostics.md")
    assert "`GET /ping` and `GET /last_image`" in rest
    assert "`POST /analyze_image` and `POST /analyze_raw_image`" in rest
    assert "`ContextBase64utf`, `context_in_body`, `ImageLen`" in rest
    assert "HTTP 200, `image/png`, zero-byte body" in rest
    assert "HTTP 400 with internal OpenCV traceback details" in rest
    assert "process/PID → listening port → `/ping` → inference/model ready → camera/provider live" in compact(diagnostics)


def test_basler_addition_is_pekat_specific_and_routes_deep_work():
    hardware = read("references/industrial-hardware.md")
    assert "a2A2448-23gmBAS" in hardware
    assert "persistent PEKAT config, PEKAT live feature" in hardware
    assert "GenICam NodeMap" in hardware
    assert "may retain exclusive device ownership" in compact(hardware)
    assert "route detailed camera" in hardware.lower()
    assert "`basler-cameras`" in hardware


def test_no_skill2_socketio_authoring_or_general_framework_promotion():
    skill = read("SKILL.md")
    rest = read("references/rest-sdk-runtime.md")
    script_names = {path.name.lower() for path in (SKILL / "scripts").glob("*.py")}
    assert "Skill 2.0 orchestration" in skill
    assert "Do not promote internal Socket.IO" in skill
    assert "not a supported public API" in compact(rest)
    assert "Do not add browser/Socket.IO FLOW authoring" in rest
    assert not any("socket" in name or "browser" in name or "playwright" in name for name in script_names)
    cookbook = read("references/script-cookbook.md")
    assert "small patterns, not universal modules" in cookbook
    assert "rather than creating a general model orchestration framework" in compact(cookbook)
