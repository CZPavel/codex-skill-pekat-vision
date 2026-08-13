import pytest

from form_normalization import boolean, choice, number


def test_number_normalizes_untouched_string_and_edited_integer():
    assert number({"threshold": "12"}, "threshold", 5, 0, 100) == 12.0
    assert number({"threshold": 27}, "threshold", 5, 0, 100) == 27.0


def test_number_rejects_bool_and_out_of_range():
    with pytest.raises(ValueError, match="numeric"):
        number({"threshold": True}, "threshold", 5, 0, 100)
    with pytest.raises(ValueError, match="outside range"):
        number({"threshold": 101}, "threshold", 5, 0, 100)


def test_checkbox_normalization_does_not_use_bool_string_trap():
    assert boolean({"enabled": False}, "enabled") is False
    assert boolean({"enabled": "false"}, "enabled") is False
    assert boolean({"enabled": "true"}, "enabled") is True


def test_select_accepts_index_default_and_text_selection():
    choices = ["auto", "manual", "test"]
    assert choice({"mode": "0"}, "mode", "0", choices) == "auto"
    assert choice({"mode": "test"}, "mode", "0", choices) == "test"
