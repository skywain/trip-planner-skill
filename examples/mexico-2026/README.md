# Mexico 2026 · journal

**Berlin (BER) → Mexico City · Teotihuacán · Oaxaca**, 28 Oct – 6 Nov 2026, 10 days
**Language** English · **Theme** `journal` · **Cover** "Marigold"

An open travel journal on one continuous sheet: vintage photographs taped down, torn
ticket stubs, marigold ephemera, and a Day-of-the-Dead week that plans around the crowd.

**Reproduce** (run from the repo root)

    python3 themes/render_journal.py examples/mexico-2026/mexico.geo.json -o out.html

`mexico.art.json` sits beside the plan, so `--art` is implicit. From anywhere else pass
`--art examples/mexico-2026/mexico.art.json` — the art file's folder joins the asset search path.

Images resolve from `themes/assets/` (this trip's stems are prefixed `mexico-`), so no
`--assets` flag is needed. `mexico.kml` is the offline pin set for Google Earth / Maps.me.

**Cost** $0.2820 of image generation — 8 `gpt-image-2` calls → 18 webp. No GPU time
(stills only; only the video "portal" theme needs a GPU).
