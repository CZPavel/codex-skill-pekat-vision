from pathlib import Path

import pytest

from industrial_io_guard import decode_u16_be, extract_bits, guarded_write
from projects_manager_tcp_demo import build_command, send_command
from runtime_fingerprint import fingerprint_installation


def test_industrial_write_is_fail_closed():
    calls = []
    writer = lambda value: calls.append(value) or "ok"
    assert guarded_write(writer, 7)["reason"] == "dry_run"
    assert calls == []
    with pytest.raises(PermissionError):
        guarded_write(writer, 7, dry_run=False)
    assert guarded_write(writer, 7, dry_run=False, approved=True)["executed"] is True
    assert calls == [7]


def test_decode_guards():
    assert decode_u16_be(b"\x01\x02", 0) == 258
    assert extract_bits(0b101100, bit_offset=2, bit_length=3) == 0b011
    with pytest.raises(ValueError):
        decode_u16_be(b"\x01", 0)


def test_projects_manager_mutation_requires_approval():
    assert build_command("status", r"C:\TEST\Project") == r"status:C:\TEST\Project"
    with pytest.raises(PermissionError):
        send_command("localhost", 7002, "stop", r"C:\TEST\Project")


def test_runtime_fingerprint_is_filesystem_only(tmp_path):
    install = tmp_path / "PEKAT VISION 4.0.1"
    (install / "server" / "numpy-2.4.3.dist-info").mkdir(parents=True)
    (install / "server" / "python312.dll").write_bytes(b"")
    result = fingerprint_installation(install, "4.0.1")
    assert result["python_abi"] == "cp312"
    assert result["packages"]["numpy"] == "2.4.3"
    assert result["probe_mode"] == "read_only_filesystem"
