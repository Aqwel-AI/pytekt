"""CLI for ``aion vision`` subcommands."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Tuple


def _parse_size(value: Optional[str]) -> Optional[Tuple[int, int]]:
    if not value:
        return None
    text = value.lower().replace("x", " ").replace(",", " ")
    parts = [p for p in text.split() if p]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("size must look like WxH, e.g. 256x256")
    w, h = int(parts[0]), int(parts[1])
    if w < 1 or h < 1:
        raise argparse.ArgumentTypeError("size dimensions must be positive")
    return w, h


def vision_main(args: argparse.Namespace) -> None:
    """Dispatch ``aion vision`` actions."""
    action = getattr(args, "vision_action", None)
    if action == "info":
        from .io import image_info

        info = image_info(args.path)
        for key in ("path", "width", "height", "mode", "format", "n_frames"):
            print(f"{key}: {info[key]}")
        return

    if action == "convert":
        from .io import read_image, write_image
        from .transforms import resize

        mode = args.mode if args.mode != "none" else None
        img = read_image(args.input, mode=mode)
        size = _parse_size(args.size)
        if size:
            img = resize(img, size)
        out = write_image(args.output, img)
        print(f"wrote {out} shape={img.shape}")
        return

    if action == "edges":
        from .filters import canny
        from .io import read_image, write_image

        img = read_image(args.input, mode="RGB")
        edges = canny(img, args.t1, args.t2)
        out = write_image(args.output, edges)
        print(f"wrote {out} shape={edges.shape}")
        return

    print("Usage: aion vision {info,convert,edges} …")
    print("  aion vision info <path>")
    print("  aion vision convert <in> <out> [--mode RGB|L|none] [--size WxH]")
    print("  aion vision edges <in> <out> [--t1 100] [--t2 200]")


def build_vision_parser(parser: argparse.ArgumentParser) -> None:
    """Attach vision subcommands to an argparse parser."""
    sub = parser.add_subparsers(dest="vision_action", help="Vision actions")

    info_p = sub.add_parser("info", help="Show image metadata")
    info_p.add_argument("path", type=Path, help="Image path")

    conv = sub.add_parser("convert", help="Convert / resize an image")
    conv.add_argument("input", type=Path, help="Input image")
    conv.add_argument("output", type=Path, help="Output image")
    conv.add_argument(
        "--mode",
        default="RGB",
        choices=["RGB", "L", "RGBA", "none"],
        help="Color mode (none = keep file mode)",
    )
    conv.add_argument("--size", default=None, help="Resize to WxH, e.g. 256x256")

    edges = sub.add_parser("edges", help="Canny edge detection")
    edges.add_argument("input", type=Path, help="Input image")
    edges.add_argument("output", type=Path, help="Output image")
    edges.add_argument("--t1", type=float, default=100.0, help="Canny threshold1")
    edges.add_argument("--t2", type=float, default=200.0, help="Canny threshold2")
