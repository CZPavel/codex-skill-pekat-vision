from check_pekat_library_compat import check, check_wheel, find_package, load_matrix


def test_direct_runtime_matrix_has_expected_scope_and_counts():
    matrix = load_matrix()
    assert matrix["product_version"] == "4.0.1"
    assert matrix["python"] == {
        "implementation": "CPython",
        "version": "3.12.12",
        "abi": "cp312",
        "architecture": "AMD64",
        "wheel_platform": "win_amd64",
        "host_executable": "pekat_vision_server.exe",
        "prefix": r"C:\Program Files\PEKAT VISION 4.0.1\server",
    }
    assert matrix["probe_summary"] == {
        "targeted_imports": 58,
        "import_pass": 46,
        "present_import_failed": 2,
        "unavailable": 10,
        "functional_tests": 24,
        "functional_pass": 24,
    }
    states = {state: sum(item["status"] == state for item in matrix["packages"]) for state in {
        "functionally_verified", "import_verified", "present_import_failed", "unavailable"
    }}
    assert states == {
        "functionally_verified": 22,
        "import_verified": 24,
        "present_import_failed": 2,
        "unavailable": 10,
    }


def test_package_lookup_and_local_addition_boundary():
    matrix = load_matrix()
    expected_versions = {
        "numpy": "2.4.3", "cv2": "4.13.0", "scipy": "1.17.1",
        "torch": "2.7.1+cu128", "torchvision": "0.22.1+cu128", "timm": "0.6.7",
        "onnx": "1.20.1", "tensorrt": "10.13.0.35", "faiss": "1.14.1",
        "snap7": "2.0.2", "requests": "2.32.5", "openpyxl": "3.1.4",
        "zxingcpp": "3.1.0", "pyzbar": "0.1.9",
    }
    assert {name: find_package(matrix, name)["version"] for name in expected_versions} == expected_versions
    scipy = find_package(matrix, "scipy")
    zxing = find_package(matrix, "zxingcpp")
    assert scipy["version"] == "1.17.1"
    assert scipy["status"] == "functionally_verified"
    assert zxing["library"] == "zxing-cpp"
    assert "local installation" in zxing["notes"]
    for missing in ("pandas", "onnxruntime", "tensorflow"):
        assert check("4.0.1", missing)["status"] == "NOT_AVAILABLE_ON_TESTED_INSTALLATION"


def test_wheel_tag_classification_is_conservative():
    assert check_wheel("demo-1.0-cp312-cp312-win_amd64.whl")["status"] == "COMPATIBLE_TAGS"
    assert check_wheel("demo-1.0-cp312-abi3-win_amd64.whl")["status"] == "COMPATIBLE_TAGS"
    assert check_wheel("demo-1.0-py3-none-any.whl")["status"] == "LIKELY_COMPATIBLE"
    assert check_wheel("demo-1.0-cp311-cp311-win_amd64.whl")["status"] == "WRONG_ABI"
    assert check_wheel("demo-1.0-cp312-cp312-win32.whl")["status"] == "WRONG_ARCH"
    assert check_wheel("not-a-wheel.zip")["status"] == "UNKNOWN_TEST_REQUIRED"


def test_matrix_is_not_applied_to_pekat_3():
    report = check("3.19.3", package="scipy", wheel="demo-1.0-cp310-cp310-win_amd64.whl")
    assert report["matrix_applied"] is False
    assert report["status"] == "UNKNOWN_TEST_REQUIRED"
    assert report["wheel"]["status"] == "UNKNOWN_TEST_REQUIRED"
