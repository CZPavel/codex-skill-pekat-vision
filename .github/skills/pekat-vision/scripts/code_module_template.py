"""PEKAT Vision – Code module template (KB 3.19)

✅ Záměr: šablona, která je robustní proti KeyError/IndexError a drží typy v contextu.
✅ Entry point: main(context, module_item=None)
✅ module_item: slovník hodnot z Form Editoru (může být None)

Pozn.: V PEKATu se `context['image']` typicky předává jako numpy array.
"""

import __main__  # dovoluje držet stav napříč snímky
from typing import Any, Dict, Optional, Tuple

import numpy as np
import cv2


# ------------------------- Globální stav (per instance) -------------------------

def _init_globals() -> None:
    """Inicializace globálních proměnných – bezpečné pro opakované volání."""
    if "frame_counter" not in dir(__main__):
        __main__.frame_counter = 0


# ------------------------- Utility -------------------------

def _safe_get_image(context: Dict[str, Any]) -> Optional[np.ndarray]:
    img = context.get("image", None)
    if isinstance(img, np.ndarray):
        return img
    return None


def _iter_rectangles(context: Dict[str, Any]):
    rects = context.get("detectedRectangles", [])
    if isinstance(rects, list):
        for r in rects:
            if isinstance(r, dict):
                yield r


def _rect_label(rect: Dict[str, Any]) -> Optional[str]:
    """Preferuj top label z classNames[0]['label'] – dle KB příkladů."""
    class_names = rect.get("classNames")
    if isinstance(class_names, list) and class_names:
        top = class_names[0]
        if isinstance(top, dict):
            return top.get("label")
    return rect.get("label") or rect.get("className")


def _clip_roi(x1: int, y1: int, x2: int, y2: int, w: int, h: int) -> Tuple[int, int, int, int]:
    x1 = max(0, min(w, x1))
    x2 = max(0, min(w, x2))
    y1 = max(0, min(h, y1))
    y2 = max(0, min(h, y2))
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    return x1, y1, x2, y2


# ------------------------- Entry point -------------------------

def main(context: Dict[str, Any], module_item: Optional[Dict[str, Any]] = None) -> None:
    _init_globals()
    __main__.frame_counter += 1

    # ---- Program settings (upravuje uživatel) ----
    TARGET_LABEL = "My Rectangle"     # label, podle kterého se bude ořezávat (nebo None pro první rectangle)
    DO_EARLY_EXIT_IF_MISSING = False  # pokud True a rectangle chybí → nastaví context['exit']=True
    DRAW_DEBUG = False                # pokud True, vykreslí rectangle do obrázku
    # ---------------------------------------------

    img = _safe_get_image(context)
    if img is None:
        return

    # Najdi rectangle pro ořez
    selected = None
    for r in _iter_rectangles(context):
        if TARGET_LABEL is None or _rect_label(r) == TARGET_LABEL:
            selected = r
            break

    if selected is None:
        if DO_EARLY_EXIT_IF_MISSING:
            context["exit"] = True  # skip dalších modulů ve větvi
        return

    x = int(selected.get("x", 0))
    y = int(selected.get("y", 0))
    w = int(selected.get("width", 0))
    h = int(selected.get("height", 0))

    H, W = img.shape[:2]
    x1, y1, x2, y2 = _clip_roi(x, y, x + w, y + h, W, H)

    # Ořez – zachová typ (np.ndarray)
    cropped = img[y1:y2, x1:x2].copy()
    context["image"] = cropped

    if DRAW_DEBUG:
        # Pozn.: kreslíme do cropped, takže rectangle bude typicky na hraně obrazu
        cv2.rectangle(context["image"], (0, 0), (cropped.shape[1] - 1, cropped.shape[0] - 1), (0, 255, 0), 2)

    # Ukázka: práce s module_item (Form Editor)
    if isinstance(module_item, dict):
        context["debug_form_keys"] = list(module_item.keys())
