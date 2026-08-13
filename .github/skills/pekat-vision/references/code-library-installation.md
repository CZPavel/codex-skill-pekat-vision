# Adding Python libraries to PEKAT Code

## Contents

1. [Safety and scope](#safety-and-scope)
2. [Compatibility workflow](#compatibility-workflow)
3. [PEKAT 4.0.1 ABI](#pekat-401-abi)
4. [Installation boundary](#installation-boundary)
5. [PTool/PModule dependencies](#ptoolpmodule-dependencies)

## Safety and scope

Do not install into Program Files during ordinary diagnosis or skill validation.
Treat a package change as an explicit modification: identify the target project
and version, preserve the current state, use an isolated target when possible,
and define rollback. Never call a copied folder or successful installer process
proof that PEKAT Code can use the library.

The documented PEKAT Code guidance says that files produced by a Python package
installation must be placed in the PEKAT `server` folder (default product path
`C:\Program Files\PEKAT VISION X.X.X\server`). The exact package command and
staging method are environment-specific: do not invent a direct `pip` command
for the embedded server. Prefer staging outside Program Files, inspecting the
result, backing up the target, then copying only through an approved method.

## Compatibility workflow

1. Identify the exact PEKAT version; do not reuse the 4.0.1 matrix for 3.x.
2. Fingerprint the Code runtime ABI/architecture with
   `scripts/runtime_fingerprint.py` or direct Code runtime evidence.
3. Test whether the import already works inside Code.
4. Determine whether the package is pure Python or contains a native wheel,
   `.pyd`, `.dll` or compiled dependency.
5. Inspect all transitive dependencies and native-runtime requirements.
6. Check exact Python, ABI and Windows architecture tags.
7. Select an evidence-backed staging/install method for the target server;
   preserve a rollback copy and avoid overwriting unrelated vendor files.
8. Restart only the relevant isolated project/server if the approved method
   requires it; do not restart a production project as a generic diagnostic.
9. Run a direct Code import probe.
10. Run one minimal functional call appropriate to the library.
11. Record PEKAT version/build, package version, origin and test boundary.

Success gate:

```text
files copied < import in PEKAT Code < minimal functional call in PEKAT Code
```

## PEKAT 4.0.1 ABI

The directly tested Windows runtime is:

```text
CPython 3.12.12
cp312
AMD64 / win_amd64
embedded PEKAT server environment
```

Native `cp310`, `cp311`, `win32`, ARM/ARM64 or other incompatible wheels do not
fit this tested runtime. A `py3-none-any` wheel is only a likely pure-Python
candidate: its dependencies and Python 3.12 behavior still require inspection.
An `abi3` wheel may be a tag-compatible candidate when its Python/platform tags
also match, but native DLL dependencies can still make the import fail.

Use the read-only checker:

```powershell
python scripts/check_pekat_library_compat.py `
  --pekat-version 4.0.1 `
  --package zxing-cpp `
  --wheel some_package-cp312-cp312-win_amd64.whl
```

Possible results include `COMPATIBLE_TAGS`, `LIKELY_COMPATIBLE`, `WRONG_ABI`,
`WRONG_ARCH`, and `UNKNOWN_TEST_REQUIRED`. Tag compatibility is never the final
runtime success gate.

## Installation boundary

- `zxingcpp`/zxing-cpp 3.1.0 was an additional user-confirmed installation on
  the tested PC and its native decoder call worked in Code.
- `pyzbar` 0.1.9 was likely added locally; installer evidence corroborated it
  and native ZBar decode worked in Code.
- Neither package is guaranteed in a clean PEKAT 4.0.1 installation.
- `imageio` demonstrates why copied files are insufficient: it is present but
  import fails because flattened distribution metadata is unavailable.
- `vmbpy` demonstrates the native-runtime gate: the Python layer is present but
  Vimba X native runtime configuration is incomplete.

If the exact installation invocation is not documented or preserved in a
trusted local installer log, provide this workflow and stop before mutation.
Ask for explicit approval and a rollback plan before executing an install.

## PTool/PModule dependencies

A `.ptool` or `.pmodule` stores PEKAT Code/Form/export data; it does **not**
package an arbitrary external Python dependency. For example:

```python
import zxingcpp
```

requires a compatible `zxingcpp` installation in the target PEKAT runtime.
When generating an export with a non-standard dependency, state:

- required import/package;
- target PEKAT version and ABI;
- tested/required package version when known;
- whether evidence is functional, import-only or unknown;
- the import/functional acceptance step on the destination PC.

Do not assume a 4.0.1 dependency/version works in 3.19.3 merely because the
export source is syntactically similar.
