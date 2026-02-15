"""Jak přidat knihovny do sys.path v Code modulu

Použij, když jsi zkopíroval knihovnu do složky:
C:\\Program Files\\PEKAT VISION X.X.X\\server\\my_libs

a import nefunguje.
"""

import sys
from pathlib import Path


def add_lib_dir(path_str: str) -> None:
    p = Path(path_str)
    if p.exists():
        sys.path.insert(0, str(p))


def main(context, module_item=None):
    # Uprav podle reálné cesty
    add_lib_dir(r"C:\Program Files\PEKAT VISION 3.19.0\server\my_libs")

    # Pak můžeš importovat
    # import my_library

    return
