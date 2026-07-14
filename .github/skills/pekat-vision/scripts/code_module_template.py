"""Version-aware PEKAT Code module template with Form Editor values.

The template intentionally does not persist process-global state or mutate result.
"""
from __future__ import annotations

from typing import Any


def _first_rectangle(context: dict[str, Any], target_label: str | None) -> dict[str, Any] | None:
    rectangles = context.get("detectedRectangles", [])
    if not isinstance(rectangles, list):
        return None
    for rectangle in rectangles:
        if not isinstance(rectangle, dict):
            continue
        labels = rectangle.get("classNames", [])
        label = None
        if isinstance(labels, list) and labels and isinstance(labels[0], dict):
            label = labels[0].get("label")
        label = label or rectangle.get("label") or rectangle.get("className")
        if target_label in {None, ""} or label == target_label:
            return rectangle
    return None


def _crop(image: Any, rectangle: dict[str, Any]) -> Any | None:
    """Crop an array-like image while preserving its dtype through slicing/copy."""
    shape = getattr(image, "shape", None)
    if not shape or len(shape) < 2:
        return None
    height, width = int(shape[0]), int(shape[1])
    try:
        x = int(rectangle.get("x", 0))
        y = int(rectangle.get("y", 0))
        rect_width = int(rectangle.get("width", 0))
        rect_height = int(rectangle.get("height", 0))
    except (TypeError, ValueError):
        return None
    x1, y1 = max(0, min(width, x)), max(0, min(height, y))
    x2, y2 = max(0, min(width, x + rect_width)), max(0, min(height, y + rect_height))
    if x2 <= x1 or y2 <= y1:
        return None
    cropped = image[y1:y2, x1:x2]
    return cropped.copy() if hasattr(cropped, "copy") else cropped


def main(context: dict[str, Any], form: dict[str, Any] | None = None) -> None:
    """Optionally crop the image and write diagnostics without changing result."""
    values = form or {}
    target_label = values.get("target_label")
    crop_enabled = bool(values.get("crop_enabled", False))

    rectangle = _first_rectangle(context, None if target_label is None else str(target_label))
    context["code_template_status"] = "rectangle_not_found" if rectangle is None else "rectangle_found"
    if not crop_enabled or rectangle is None:
        return

    cropped = _crop(context.get("image"), rectangle)
    if cropped is None:
        context["code_template_status"] = "invalid_image_or_roi"
        return
    context["image"] = cropped
    context["code_template_status"] = "cropped"
