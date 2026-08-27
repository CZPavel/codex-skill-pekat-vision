# PEKAT 4.0.3 Code runtime and libraries

## Exact tested clean runtime

This matrix belongs to one clean tested PEKAT VISION `4.0.3` Windows Code
runtime. It is exact-version runtime evidence, not a vendor promise for every
4.0.x build or a package list for 3.19.x.

| Property | Value |
|---|---|
| Python | CPython `3.12.12` |
| ABI | `cp312` / Windows AMD64 |
| `numpy` | `2.4.3` |
| `cv2` | `4.10.0` |
| Pillow | `11.0.0` |
| `scipy` | `1.17.1` |
| `skimage` | `0.24.0` |
| `requests` | `2.32.5` |
| `python-snap7` / import `snap7` | `3.1.0` |

The tested 4.0.1 installation had the same Python version but different exact
package state, including `cv2 4.13.0`, `snap7 2.0.2`, and locally added barcode
packages. Do not call an exact package delta an application incompatibility
unless the requested operation fails.

## ML/GPU evidence

| Import | Version | Verified boundary |
|---|---:|---|
| `torch` | `2.7.1+cu128` | real CUDA computation PASS; function verified GPU |
| `torchvision` | `0.22.1+cu128` | available at the tested scope; do not attribute a PEKAT model |
| `timm` | `0.6.7` | available at the tested scope; no pretrained-model claim |
| `faiss` | `1.14.1` | CPU add/search PASS; no FAISS GPU-index claim |
| `onnx` | `1.20.1` | model create/check/serialize PASS; tooling, not inference |
| `tensorrt` | `10.13.0.35` | Runtime object creation only; no engine build/inference claim |

Imports were also verified for `sklearn`, `openpyxl`, `psutil`, and `pypylon`.
An import does not establish training, inference, device acquisition, PLC
communication, or production suitability.

## Not present in the clean tested installation

The following targeted imports were `NOT_PRESENT`:

```text
onnxruntime
numba
cupy
transformers
ultralytics
pandas
zxingcpp
pyzbar
```

Do not assume ONNX inference merely because `onnx` tooling exists. Choose a
model execution path only after checking the exact runtime: Torch CUDA is
directly proven here, FAISS is CPU-proven, ONNX is tooling-proven, and TensorRT
is Runtime-construction-only.

## Barcode provenance and exports

`zxingcpp` and `pyzbar` are not bundled PEKAT libraries. Both were local
post-install additions in the tested 4.0.1 installation and were absent in this
clean 4.0.3 baseline. This is not a vendor regression. Recipes that use either
package remain valid only when marked **requires local add-on dependency**.

A `.ptool` carries Code/Form configuration, not arbitrary third-party Python
packages or model assets. Recheck the dependency in Code on every destination.

## Additional-library workflow

Use `code-library-installation.md` and keep this order:

```text
exact embedded PEKAT Python/ABI
→ current package/import state
→ minimal approved install or staging only if needed
→ direct import inside PEKAT Code
→ one bounded functional smoke
→ record the installation as a local modification
```

Do not install during ordinary diagnosis or skill synchronization. Do not use
system Python success as proof for embedded PEKAT Python, and account for Python
3.12, CUDA, wheel tags, native DLLs, and transitive dependencies.
