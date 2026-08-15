#!/usr/bin/env python3
"""PNG → embeddable webp, plus the sized variants data_uri() knows about.

The renderers only ever inline webp (theme_common.data_uri). cutout.py and
split_sheet.py already write `<stem>.cut.webp` for transparent stickers; this
is the missing step for everything else — an opaque 16:9 night plate, a
poster, a postcard — and for the sm/md/lg thumbnails IMAGE-LIBRARY.md talks
about (until now those were made by hand).

Usage:
  python3 towebp.py in.png [more.png ...] [--quality 82] [--sizes md,sm,lg]
                    [--outdir DIR]

Naming (matches cutout.py / IMAGE-LIBRARY.md so data_uri finds the files):
  RGB input   → <stem>.webp          (opaque; noir/glass/zine plates)
  RGBA input  → <stem>.cut.webp      (alpha kept; same name cutout.py writes)
  --sizes X   → <stem>.<X>.webp      per size, longest side capped at
                sm 128 / md 480 / lg 640 (alpha kept). A size that would not
                shrink the source is skipped (data_uri falls through to the
                cut/full file, so a same-size copy is pure waste). A size that
                shrinks the pixels but comes out MORE BYTES than the base
                <stem>.webp / <stem>.cut.webp is also skipped (and the reason
                printed) — a heavier "smaller" file only bloats the page,
                since data_uri would prefer it over the lighter base file.
                `band` / `strip` are hand-cut shapes, not sizes — not here.
                Sheet cells (split_sheet.py) are ~300–560 px, so a sheet stem
                usually ends up with only two files: sm + cut. That is normal;
                md/lg slots fall through to the cut file.
An input already named foo.cut.png keeps its stem: foo.cut.png → foo.cut.webp
(not foo.cut.cut.webp), and its sizes are foo.sm.webp etc.

--outdir defaults to the input's own directory. Existing files are
overwritten. Prints "<file>: WxH  N KB" per output.
Quality 82 / method 6 is the recipe the AU test used for the noir plates
(≈50–100 KB for a 2K 16:9); the transparent variants use 90 like cutout.py.
"""
import argparse
import pathlib
import sys

from PIL import Image

SIZES = {"sm": 128, "md": 480, "lg": 640}


def _save(im, path, quality):
    im.save(path, "WEBP", quality=quality, method=6)
    kb = path.stat().st_size / 1024
    print(f"{path.name}: {im.width}x{im.height}  {kb:.0f} KB")


def convert(src, quality, sizes, outdir):
    src = pathlib.Path(src)
    im = Image.open(src)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    im = im.convert("RGBA" if has_alpha else "RGB")
    stem = src.stem
    if stem.endswith(".cut"):
        stem = stem[:-4]
    out = outdir or src.parent
    out.mkdir(parents=True, exist_ok=True)
    base = out / (f"{stem}.cut.webp" if has_alpha else f"{stem}.webp")
    _save(im, base, max(quality, 90) if has_alpha else quality)
    base_bytes = base.stat().st_size
    for s in sizes:
        cap = SIZES[s]
        if max(im.size) <= cap:
            # data_uri falls back to the cut/full file anyway; a same-size
            # copy would only double the bytes on disk
            print(f"{stem}.{s}.webp: skipped (source {im.width}x{im.height} "
                  f"already ≤ {cap})")
            continue
        v = im.copy()
        v.thumbnail((cap, cap), Image.LANCZOS)
        vp = out / f"{stem}.{s}.webp"
        _save(v, vp, max(quality, 90) if has_alpha else quality)
        vb = vp.stat().st_size
        if vb >= base_bytes:
            # fewer pixels but more bytes (small sheet cells re-encoded at
            # q90 do this): data_uri would pick it over the lighter base
            # file, so drop it and let the slot fall through to the base
            vp.unlink()
            print(f"{vp.name}: dropped — {vb / 1024:.0f} KB is not smaller than "
                  f"{base.name} ({base_bytes / 1024:.0f} KB); the {s} slot "
                  f"falls through to {base.name}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("inputs", nargs="+", metavar="PNG")
    ap.add_argument("--quality", type=int, default=82,
                    help="webp quality for opaque output (default 82; alpha "
                         "outputs use at least 90)")
    ap.add_argument("--sizes", default="",
                    help="comma list of extra variants: sm,md,lg (longest side "
                         "128/480/640)")
    ap.add_argument("--outdir", type=pathlib.Path, default=None,
                    help="write here instead of beside each input")
    args = ap.parse_args()
    sizes = [s.strip() for s in args.sizes.split(",") if s.strip()]
    bad = [s for s in sizes if s not in SIZES]
    if bad:
        sys.exit(f"unknown size(s) {bad}; choose from {sorted(SIZES)}")
    for f in args.inputs:
        convert(f, args.quality, sizes, args.outdir)


if __name__ == "__main__":
    main()
