# Turkey 2026 · clay

**Shanghai (PVG) → Istanbul · Cappadocia · Pamukkale · Istanbul**, 1–9 Oct 2026, 9 days
**Language** Chinese (zh) · **Theme** `clay` (黏土版) · **Cover** 九万里风 / NINETY THOUSAND MILES OF WIND

One continuous claymation landscape scrolled end to end: modelled minarets, fairy chimneys
and travertine terraces, with the overnight bus to Pamukkale sculpted in as its own scene.

**Reproduce** (run from the repo root)

    python3 themes/render_clay2.py examples/turkey-2026/turkey.geo.json -o out.html

`turkey.art.json` sits beside the plan, so `--art` is implicit. From anywhere else pass
`--art examples/turkey-2026/turkey.art.json` — the art file's folder joins the asset search path.

Images resolve from `themes/assets/` (this trip's stems are prefixed `turkey-`), so no
`--assets` flag is needed. `turkey.kml` is the offline pin set for Google Earth / Maps.me.

**Cost** $0.2594 of image generation — 7 `gpt-image-2` calls → 19 webp via sheet splitting.
No GPU time (stills only; only the video "portal" theme needs a GPU).
