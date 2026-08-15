# China 2026 · splash

**New York (JFK) → Beijing · Xi'an · Beijing**, 11–18 Nov 2026, 8 days
**Language** English · **Theme** `splash` (闪屏版) · **Cover** "MOON OF QIN"

A game splash poster stretched into a scroll: an abstract light field falling past floating
day-islands, routed Xi'an-first so the Wall and the Forbidden City both land on weekdays.

**Reproduce** (run from the repo root)

    python3 themes/render_splash.py examples/china-2026/china.geo.json -o out.html

`china.art.json` sits beside the plan, so `--art` is implicit. From anywhere else pass
`--art examples/china-2026/china.art.json` — the art file's folder joins the asset search path.

Images resolve from `themes/assets/` (this trip's stems are prefixed `china-`), so no
`--assets` flag is needed. `china.kml` is the offline pin set for Google Earth / Maps.me.

**Cost** $0.2991 of image generation — 7 `gpt-image-2` calls → 23 stems. No GPU time
(stills only; only the video "portal" theme needs a GPU).
