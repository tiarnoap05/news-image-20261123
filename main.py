#!/usr/bin/env python3
"""Entry program for news-image-20261123 (Python 3.13 stdlib only).

Copies the entry.png sitting next to this file byte-for-byte into the
harness output directory ($MAKEFUN_OUTPUT_DIR, or /output when unset).
Verifies the PNG magic bytes first and fails closed when the image is
missing or corrupt.
"""

import os
import shutil
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    here = Path(__file__).resolve().parent
    src = here / "entry.png"
    if not src.is_file():
        print(f"error: entry.png not found next to main.py ({src})",
              file=sys.stderr)
        return 1

    with open(src, "rb") as fh:
        head = fh.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        print(f"error: {src} is not a valid PNG (bad magic bytes)",
              file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"
    shutil.copyfile(src, dst)
    print(f"wrote {dst} ({dst.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
