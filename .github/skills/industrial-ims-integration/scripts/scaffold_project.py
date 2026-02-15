#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold an industrial IMS integration project from skill templates."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Target directory for generated files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files if they already exist.",
    )
    return parser.parse_args()


def copy_template(template_root: Path, output_root: Path, force: bool) -> tuple[list[Path], list[Path]]:
    created: list[Path] = []
    skipped: list[Path] = []

    for source in sorted(template_root.rglob("*")):
        relative = source.relative_to(template_root)
        target = output_root / relative

        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not force:
            skipped.append(target)
            continue

        shutil.copy2(source, target)
        created.append(target)

    return created, skipped


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    template_root = script_dir.parent / "assets" / "project-template"
    output_root = Path(args.output).resolve()

    if not template_root.exists():
        print(f"[ERROR] Missing template directory: {template_root}", file=sys.stderr)
        return 1

    output_root.mkdir(parents=True, exist_ok=True)
    created, skipped = copy_template(template_root, output_root, args.force)

    print(f"[OK] Scaffold created in: {output_root}")
    print(f"[OK] Files created/overwritten: {len(created)}")
    print(f"[OK] Files skipped: {len(skipped)}")
    if skipped:
        print("[INFO] Re-run with --force to overwrite skipped files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
