# Vietnam 2026 · zine

**Shenzhen (SZX) → Hanoi · Ha Long Bay · Hoi An / Da Nang · Ho Chi Minh City**,
12–21 Dec 2026, 10 days · **Language** Chinese (zh) · **Theme** `zine` · **Cover** 人海 / A SEA OF FACES

A cut-and-paste photocopy zine: film-grain plates, chapter posters and hand-set headlines,
built around the one leg where the night train genuinely beats the flight.

**Reproduce** (run from the repo root)

    python3 themes/render_zine.py examples/vietnam-2026/vietnam.geo.json -o out.html

`vietnam.art.json` sits beside the plan, so `--art` is implicit. From anywhere else pass
`--art examples/vietnam-2026/vietnam.art.json` — the art file's folder joins the asset search path.

Images resolve from `themes/assets/` (this trip's stems are prefixed `vietnam-`), so no
`--assets` flag is needed. `vietnam.kml` is the offline pin set for Google Earth / Maps.me.

**Cost** $0.4566 of image generation — 11 `gpt-image-2` calls → 28 webp. No GPU time
(stills only; only the video "portal" theme needs a GPU).
