# PEKAT 4.0.1 Code runtime and libraries

## Contents

1. [Exact tested runtime](#exact-tested-runtime)
2. [Evidence levels](#evidence-levels)
3. [Functionally verified](#functionally-verified)
4. [Import verified](#import-verified)
5. [Broken or unavailable](#broken-or-unavailable)
6. [Code generation routing](#code-generation-routing)

## Exact tested runtime

The local PEKAT VISION `4.0.1` Code runtime was directly tested:

| Property | Value |
|---|---|
| Python | CPython `3.12.12` |
| Architecture / ABI | AMD64 / `cp312` / Windows `win_amd64` |
| Host | embedded in `pekat_vision_server.exe` |
| Prefix | `C:\Program Files\PEKAT VISION 4.0.1\server` |
| Import probe | 58 targeted; 46 pass, 2 present/import failed, 10 unavailable |
| Functional smoke | 24/24 operations passed |

This is evidence for the tested installation, not a guarantee for every clean or
later PEKAT 4.0.1 build. Re-probe after an installation, driver, GPU or package
change. Do not apply this package matrix to PEKAT 3.18.x or 3.19.3.

Flattened packaging exposed only 24 distributions although 46 targeted imports
passed. Do not rely on `pip list` or `importlib.metadata` alone. Prefer an import
inside PEKAT Code and, where consequential, one minimal functional call.

Machine-readable source: [`data/pekat401_code_libraries.json`](data/pekat401_code_libraries.json).

## Evidence levels

| State | What Codex may claim |
|---|---|
| functionally verified | the named minimal operation passed in PEKAT 4.0.1 Code |
| import verified | import passed; the requested operation remains untested |
| present/import failed | files were present but the import did not complete |
| unavailable | targeted import was unavailable on the tested Code path |

Never turn package presence into usability, or a generic functional test into a
claim that a PEKAT tool uses that library/model.

## Functionally verified

| Import | Version | Direct test and exact boundary |
|---|---:|---|
| `numpy` | 2.4.3 | matrix calculation |
| `cv2` | 4.13.0 | synthetic BGR image → grayscale → Canny |
| `scipy` | 1.17.1 | Gaussian filter |
| `skimage` | 0.24.0 | connected-component labeling |
| `sklearn` | 1.5.2 | KNN fit/predict on synthetic data |
| `torch` | 2.7.1+cu128 | CPU tensor and real synchronized CUDA tensor calculation |
| `torchvision` | 0.22.1+cu128 | `ResNet18(weights=None)` construction; not PEKAT classifier attribution |
| `timm` | 0.6.7 | `mobilenetv3_small_050(pretrained=False)` construction |
| `faiss` | 1.14.1 | CPU `IndexFlatL2` search; GPU count `1` is visibility, not GPU search |
| `onnx` | 1.20.1 | graph/model creation, checker and RAM serialization; no inference |
| `tensorrt` | 10.13.0.35 | Runtime object creation; no engine build/inference |
| `zxingcpp` | 3.1.0 | native blank-image decoder call; additional local installation on tested PC |
| `pyzbar` | 0.1.9 | native ZBar blank-image decode; likely additional local installation |
| `pypylon` | unknown | `TlFactory` + device enumeration; zero devices, no acquisition |
| `harvesters` | 1.4.2 | `Harvester` object creation; no CTI/device acquisition |
| `snap7` | 2.0.2 | native Client construction/destruction; no PLC communication |
| `requests` | 2.32.5 | `Session` construction; no network request |
| `openpyxl` | 3.1.4 | in-memory workbook and cell access |
| `yaml` | 6.0.3 | `safe_load` |
| `psutil` | 5.9.5 | current PEKAT process query |
| `win32api` | unknown | native Windows API query |
| `cryptography` | 46.0.3 | SHA-256 operation |

GPU details for this test were PyTorch `2.7.1+cu128`, CUDA `12.8`, cuDNN
runtime `90701`, CUDA available `True`, and an NVIDIA RTX A5000 Laptop GPU
(16 GiB, compute capability 8.6). A real CUDA computation passed. This permits
purposeful Torch CUDA Code on the tested installation; it does not mean ordinary
Code or every PEKAT tool automatically runs on the GPU.

## Import verified

| Area | Imports and versions |
|---|---|
| numeric/vision | `sympy` 1.14.0; `PIL` 11.0.0; `tifffile` 2026.5.15; `albumentations` 2.0.8; `matplotlib` 3.10.9 |
| ML | `detectron2` 0.6; `sam2`; `pytorch_grad_cam`; `pekat_yolo` |
| camera | `genicam` 1.5.1; `pytelicam` 1.1.1 |
| communication | `urllib3` 2.7.0; `websocket` 1.9.0; `socketio`; `engineio`; `paramiko` 3.5.0; `flask` 2.2.2; `gevent` 24.11.1 |
| system/data | `win32com`; `watchdog`; `regex` 2026.5.9; `tqdm` 4.67.3; `pydantic` 2.12.5; `apscheduler` 3.10.4 |

An import pass does not establish model inference, camera access, network
communication or other operation-specific behavior.

## Broken or unavailable

| State | Imports | Practical response |
|---|---|---|
| present/import failed | `imageio` | flattened package metadata is missing; do not present it as usable |
| present/import failed | `vmbpy` | native `VmbC.dll`/Vimba X runtime is missing or not configured |
| unavailable | `torchaudio`, `onnxruntime`, `tensorflow`, `keras`, `cupy`, `numba`, `pycuda`, `pylibdmtx`, `qrcode`, `pandas` | do not generate a solution that assumes availability |

For tabular/data tasks prefer `numpy`, standard `csv`/`json`, or `openpyxl`
when suitable. For ONNX, distinguish installed `onnx` model tooling from the
unavailable `onnxruntime` inference package.

## Code generation routing

Choose the smallest adequate path:

```text
native PEKAT tool
→ simple FLOW/Gate
→ NumPy/OpenCV Code
→ SciPy/scikit-image/scikit-learn
→ bounded communication library
→ heavy ML/GPU
→ new third-party package only when justified
```

For direct camera SDK access, prefer the normal PEKAT camera provider when it
solves the problem. Use pypylon/GenICam/Harvesters from Code only for a special
ownership requirement. Never let PEKAT and custom Code compete for the same
acquisition camera without an explicit design.

For `.ptool`/`.pmodule`, read `code-library-installation.md`: an export does not
carry arbitrary external dependencies to another PC.
