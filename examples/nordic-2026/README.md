# Nordic 2026 · noir

**Beijing (PEK) → Oslo · Bergen Railway · Flåm / Nærøyfjord · Bergen**, 1–8 Oct 2026, 8 days
**Language** Chinese (zh) · **Theme** `noir` (夜航版) · **Cover** 天接云涛 / SEA OF CLOUDS

A night-flight cinema: five stacked full-bleed negatives that cross-fade as you scroll,
with the aurora odds argued down to an honest 5–10% instead of sold as a headline.

**Reproduce** (run from the repo root)

    python3 themes/render_noir2.py examples/nordic-2026/nordic.geo.json -o out.html

`nordic.art.json` sits beside the plan, so `--art` is implicit. From anywhere else pass
`--art examples/nordic-2026/nordic.art.json` — the art file's folder joins the asset search path.

Images resolve from `themes/assets/` (this trip's stems are prefixed `nordic-`), so no
`--assets` flag is needed. `nordic.kml` is the offline pin set for Google Earth / Maps.me.

**Cost** $0.2484 of image generation — 7 `gpt-image-2` calls → 17 webp. No GPU time
(stills only; only the video "portal" theme needs a GPU).
