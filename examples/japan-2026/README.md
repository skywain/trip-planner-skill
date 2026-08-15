# Japan 2026 · illustrated

**London → Tokyo · Hakone · Kyoto · Osaka (KIX, open-jaw)**, 21–28 Nov 2026, 8 days
**Language** English · **Theme** `illustrated` (插画版) · **Cover** "Late Maples"

A paper picture-book: the cover is the menu, each day gets a tinted riso plate with a
ghost numeral and polaroid stickers, and the whole scroll exports as one long image.

**Reproduce** (run from the repo root)

    python3 themes/render_theme2.py examples/japan-2026/japan.geo.json -o out.html

`japan.art.json` sits beside the plan, so `--art` is implicit. From anywhere else pass
`--art examples/japan-2026/japan.art.json` — the art file's folder joins the asset search path.

Images resolve from `themes/assets/` (this trip's stems are prefixed `japan-`), so no
`--assets` flag is needed. `japan.kml` is the offline pin set for Google Earth / Maps.me.

**Cost** $0.4090 of image generation — 10 `gpt-image-2` calls → 18 webp via sheet splitting.
No GPU time (stills only; only the video "portal" theme needs a GPU).
