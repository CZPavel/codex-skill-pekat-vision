from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".github" / "skills" / "pekat-vision"


def read(relative: str) -> str:
    return (SKILL / relative).read_text(encoding="utf-8")


def test_existing_behavior_is_reconstructed_and_preserved_before_redesign():
    text = read("SKILL.md")
    for value in (
        "complete relevant FLOW",
        "behavioral contract",
        "MUST PRESERVE",
        "INTENTIONAL CHANGE",
        "filenames/folders",
        "compression",
        "annotations",
        "Form controls",
        "feature-equivalent",
    ):
        assert value in text
    assert "Do not request a test that merely reconfirms" in text


def test_form_signature_stays_exact_and_form_none_is_not_native_contract():
    text = read("SKILL.md")
    assert "`main(context)` without Form" in text
    assert "`main(context, form)` with Form" in text
    assert "form=None" not in text


def test_cap_raw_result_is_sequential_or_branch_local_not_join_merge():
    text = read("SKILL.md") + read("references/flow-database-projects.md")
    assert 'context["cap_raw_result"]' in text
    assert "sequential downstream" in text
    assert "branch-local" in text
    assert "not a mechanism for propagating custom Context" in text


def test_cross_pekat_robustness_is_requirement_driven():
    text = read("SKILL.md") + read("references/script-cookbook.md")
    assert "simple current-state" in text.lower()
    assert "stale-state detection" in text
    assert "communication-loss detection" in text
    assert "exact pairing" in text
    assert "only" in text


def test_skill2_and_live_socketio_remain_excluded():
    text = read("SKILL.md")
    assert "Skill 2.0 orchestration" in text
    assert "Do not promote internal Socket.IO" in text
