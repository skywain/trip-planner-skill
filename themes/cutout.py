#!/usr/bin/env python3
"""White-background removal for flat illustration stickers.

Flood-fills near-white regions connected to the image border (so interior
whites survive), erodes 1px to kill halo, feathers the edge, autocrops,
and writes <name>.cut.png + <name>.cut.webp with real alpha.

Usage: python3 cutout.py file1.png [file2.png ...] [--outdir DIR]
Outputs land beside each input (<stem>.cut.png / <stem>.cut.webp) — the
input's own directory, whatever the cwd — or in --outdir DIR (created if
missing).
"""
import argparse
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter

MARKER = (255, 0, 255)
THRESH = 48  # max summed channel distance treated as "same as background"


def cutout(path, outdir=None):
    """Write <stem>.cut.png / .cut.webp beside `path` (or into `outdir`)."""
    src = Image.open(path).convert("RGB")
    w, h = src.size
    work = src.copy()
    # Seed flood fills from border points; background may touch any edge.
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
             (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for xy in seeds:
        if work.getpixel(xy) != MARKER:
            ImageDraw.floodfill(work, xy, MARKER, thresh=THRESH)
    # Second pass: enclosed background holes (pure-white pockets the edge
    # fill can't reach, e.g. under a bridge deck). Only components that are
    # large AND near-pure white get cleared; painted creams stay.
    px = work.load()
    visited = bytearray(w * h)
    for sy in range(h):
        for sx in range(w):
            if visited[sy * w + sx]:
                continue
            p = px[sx, sy]
            if p == MARKER or min(p) < 250:
                visited[sy * w + sx] = 1
                continue
            stack = [(sx, sy)]
            comp = []
            visited[sy * w + sx] = 1
            while stack:
                x, y = stack.pop()
                comp.append((x, y))
                for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if 0 <= nx < w and 0 <= ny < h and not visited[ny * w + nx]:
                        q = px[nx, ny]
                        if q != MARKER and min(q) >= 250:
                            visited[ny * w + nx] = 1
                            stack.append((nx, ny))
            if len(comp) >= 1000:
                mean_min = sum(min(px[x, y]) for x, y in comp) / len(comp)
                if mean_min >= 252:
                    for x, y in comp:
                        px[x, y] = MARKER
                    print(f"  cleared enclosed hole: {len(comp)}px")
    # Alpha: opaque everywhere except the marker region.
    alpha = Image.new("L", (w, h), 255)
    px_work = work.load()
    px_alpha = alpha.load()
    for y in range(h):
        for x in range(w):
            if px_work[x, y] == MARKER:
                px_alpha[x, y] = 0
    # Erode 1px (kill white halo), then feather.
    alpha = alpha.filter(ImageFilter.MinFilter(3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))
    out = src.convert("RGBA")
    out.putalpha(alpha)
    bbox = alpha.getbbox()
    if bbox:
        pad = 8
        bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                min(w, bbox[2] + pad), min(h, bbox[3] + pad))
        out = out.crop(bbox)
    src_path = pathlib.Path(path)
    stem = (pathlib.Path(outdir) / src_path.stem) if outdir else src_path.with_suffix("")
    out.save(f"{stem}.cut.png")
    out.save(f"{stem}.cut.webp", quality=90, method=6)
    a = out.getchannel("A")
    lo, hi = a.getextrema()
    transparent = sum(1 for v in a.getdata() if v < 16)
    pct = 100.0 * transparent / (out.width * out.height)
    kb = pathlib.Path(f"{stem}.cut.webp").stat().st_size // 1024
    print(f"{pathlib.Path(path).name}: {out.width}x{out.height} "
          f"alpha[{lo},{hi}] transparent={pct:.1f}% webp={kb}KB")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 epilog=__doc__.split("\n\n", 1)[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", metavar="PNG")
    ap.add_argument("--outdir", metavar="DIR", default=None,
                    help="where the .cut.png/.cut.webp go (default: beside each input; "
                         "created if missing)")
    args = ap.parse_args()
    if args.outdir:
        pathlib.Path(args.outdir).mkdir(parents=True, exist_ok=True)
    for f in args.inputs:
        cutout(f, args.outdir)


if __name__ == "__main__":
    main()
