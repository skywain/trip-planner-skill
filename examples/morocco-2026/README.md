# Morocco 2026 · glass

**Toronto → Marrakech · Aït Benhaddou · Merzouga · Fes · Chefchaouen · Casablanca**, 6–15 Nov 2026, 10 days
**Language** English · **Theme** `glass` · **Cover** "Ochre Road"

Frosted-glass app chrome floating over six ochre desert plates — the itinerary reads like
a native travel app, one pane per world, from the red rooftops to the blue mountain.

**Reproduce** (run from the repo root)

    python3 themes/render_glass2.py examples/morocco-2026/morocco.geo.json -o out.html

`morocco.art.json` sits beside the plan, so `--art` is implicit. From anywhere else pass
`--art examples/morocco-2026/morocco.art.json` — the art file's folder joins the asset search path.

Images resolve from `themes/assets/` (this trip's stems are prefixed `morocco-`), so no
`--assets` flag is needed. `morocco.kml` is the offline pin set for Google Earth / Maps.me.

**Cost** $0.3624 of image generation — 11 `gpt-image-2` calls. This trip also produced a video "portal" theme
(21 GPU min on a local 5090); that variant and its `.mp4` clips are **not** shipped here, though `morocco.art.json` keeps its `themes.portal` block.
