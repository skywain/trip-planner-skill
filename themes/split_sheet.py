#!/usr/bin/env python3
"""Split one generated sprite SHEET into individual cut-out assets.

Why: gpt-image-2 bills per image, so N small props cost N × $0.053 when
generated one by one. Asking for ONE sheet with N props laid out on a white
grid costs $0.053 total — then this script finds the white gutters, crops
each cell, and runs the same white-background cutout used elsewhere, so the
result is indistinguishable from N separately generated transparent assets.

Usage:
  python3 split_sheet.py sheet.png name1 name2 name3 ...    # names in reading order
  python3 split_sheet.py sheet.png --probe                  # just report the grid it sees
  python3 split_sheet.py sheet.png --grid 3x2 name1 ... name6
      # escape hatch: force COLSxROWS equal cells (reading order) instead of
      # detecting gutters. Use it when a sparkle / star / drop shadow lands in
      # a gutter and merges two columns in the projection (--probe shows
      # fewer cells than props). Each forced cell is still autocropped by the
      # cut-out, so a little slack around a prop is harmless.

Writes <name>.png (cropped RGB), <name>.cut.png / .cut.webp (alpha) per cell
BESIDE THE SHEET (its directory), or into --outdir DIR (created if missing) —
so `python3 themes/split_sheet.py trips/x/x-sheet.png a b c` from the repo
root lands the cells in trips/x/ without a cd. Cells are usually 300–560 px,
so downstream only sm + cut variants make sense (see towebp.py).
"""
import argparse
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter

MARKER = (255, 0, 255)
THRESH = 48          # flood-fill tolerance, same as cutout.py
CONTENT = 246        # a pixel darker than this on any channel counts as content
MIN_RUN = 12         # ignore content bands thinner than this (noise/JPEG fringe)
PAD = 10


def content_profile(px, w, h, axis):
    """Count content pixels per row (axis=0) or per column (axis=1)."""
    prof = []
    if axis == 0:
        for y in range(h):
            c = 0
            for x in range(0, w, 2):          # stride 2 — plenty for gutter finding
                r, g, b = px[x, y][:3]
                if r < CONTENT or g < CONTENT or b < CONTENT:
                    c += 1
            prof.append(c)
    else:
        for x in range(w):
            c = 0
            for y in range(0, h, 2):
                r, g, b = px[x, y][:3]
                if r < CONTENT or g < CONTENT or b < CONTENT:
                    c += 1
            prof.append(c)
    return prof


def bands(prof, min_run=MIN_RUN, floor=2):
    """Contiguous runs where the profile exceeds `floor`."""
    out, start = [], None
    for i, v in enumerate(prof):
        if v > floor and start is None:
            start = i
        elif v <= floor and start is not None:
            if i - start >= min_run:
                out.append((start, i))
            start = None
    if start is not None and len(prof) - start >= min_run:
        out.append((start, len(prof)))
    return out


def cutout(img):
    """White-background removal — same recipe as cutout.py (border flood +
    enclosed-hole sweep + 1px erode + feather + autocrop)."""
    src = img.convert("RGB")
    w, h = src.size
    work = src.copy()
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
             (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for xy in seeds:
        if work.getpixel(xy) != MARKER:
            ImageDraw.floodfill(work, xy, MARKER, thresh=THRESH)
    alpha = Image.new("L", (w, h), 255)
    pw, pa = work.load(), alpha.load()
    for y in range(h):
        for x in range(w):
            if pw[x, y] == MARKER:
                pa[x, y] = 0
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = src.convert("RGBA")
    out.putalpha(alpha)
    bbox = alpha.getbbox()
    if bbox:
        bbox = (max(0, bbox[0] - 6), max(0, bbox[1] - 6),
                min(w, bbox[2] + 6), min(h, bbox[3] + 6))
        out = out.crop(bbox)
    return out


def parse_grid(spec):
    try:
        c, r = spec.lower().replace("×", "x").split("x")
        c, r = int(c), int(r)
        if c < 1 or r < 1:
            raise ValueError
        return c, r
    except ValueError:
        raise argparse.ArgumentTypeError(f"--grid wants COLSxROWS, e.g. 3x2 (got {spec!r})")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("Usage:", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheet", metavar="sheet.png")
    ap.add_argument("names", nargs="*", metavar="name",
                    help="output stems in reading order (left→right, top→bottom); "
                         "default <sheet>-<i>")
    ap.add_argument("--probe", action="store_true",
                    help="only report the grid detected (or forced), write nothing")
    ap.add_argument("--grid", type=parse_grid, metavar="CxR", default=None,
                    help="force COLSxROWS equal cells instead of gutter detection")
    ap.add_argument("--outdir", metavar="DIR", default=None,
                    help="where the cells go (default: beside the sheet; created if missing)")
    args = ap.parse_intermixed_args()   # names may follow --grid/--probe
    sheet_path = pathlib.Path(args.sheet)
    probe = args.probe
    names = args.names
    outdir = pathlib.Path(args.outdir) if args.outdir else sheet_path.parent
    if not probe:
        outdir.mkdir(parents=True, exist_ok=True)

    sheet = Image.open(sheet_path).convert("RGB")
    w, h = sheet.size
    px = sheet.load()

    cells = []
    if args.grid:
        cols_n, rows_n = args.grid
        cw, ch = w / cols_n, h / rows_n
        for r in range(rows_n):
            for c in range(cols_n):
                cells.append((int(round(c * cw)), int(round(r * ch)),
                              int(round((c + 1) * cw)), int(round((r + 1) * ch))))
        print(f"{sheet_path.name}: {w}x{h} → forced grid {cols_n}x{rows_n}, "
              f"{len(cells)} cell(s)")
    else:
        rows = bands(content_profile(px, w, h, 0))
        for y0, y1 in rows:
            strip = sheet.crop((0, y0, w, y1))
            cols = bands(content_profile(strip.load(), w, y1 - y0, 1))
            for x0, x1 in cols:
                cells.append((max(0, x0 - PAD), max(0, y0 - PAD),
                              min(w, x1 + PAD), min(h, y1 + PAD)))
        print(f"{sheet_path.name}: {w}x{h} → {len(rows)} row band(s), {len(cells)} cell(s)")
    for i, c in enumerate(cells):
        print(f"  cell {i}: {c[2]-c[0]}x{c[3]-c[1]} at {c[0]},{c[1]}")
    if probe:
        return
    if names and len(names) != len(cells):
        print(f"!! {len(names)} names but {len(cells)} cells — pass --probe and adjust "
              f"the sheet prompt (bigger gutters) or the name list, or force the "
              f"layout with --grid CxR")
        return

    for i, box in enumerate(cells):
        name = names[i] if names else f"{sheet_path.stem}-{i}"
        stem = outdir / name
        crop = sheet.crop(box)
        crop.save(f"{stem}.png")
        cut = cutout(crop)
        cut.save(f"{stem}.cut.png")
        cut.save(f"{stem}.cut.webp", quality=90, method=6)
        a = cut.getchannel("A")
        transparent = sum(1 for v in a.getdata() if v < 16)
        pct = 100.0 * transparent / (cut.width * cut.height)
        print(f"  → {stem}: {cut.width}x{cut.height} transparent={pct:.0f}% "
              f"webp={pathlib.Path(f'{stem}.cut.webp').stat().st_size // 1024}KB")


if __name__ == "__main__":
    main()
