# Third-party notices

The skill's own code and documentation are MIT-licensed (see [LICENSE](LICENSE)).
The repository also **redistributes** the following third-party assets, each under
its own licence, which travels with them:

| What | Where in this repo | Licence | Notice text |
|---|---|---|---|
| **Caveat** variable font (embedded as a data-URI `@font-face` in the journal / zine pages) | `themes/assets/caveat-vf.woff2` | SIL Open Font License 1.1 — Copyright 2014 The Caveat Project Authors | [themes/assets/OFL-Caveat.txt](themes/assets/OFL-Caveat.txt) |
| **Lucide** icon paths (inlined as SVG sprites by the themed renderers) | `themes/lucide-icons.json` | ISC — Copyright (c) Lucide Icons and Contributors; some icons derive from Feather (MIT, Cole Bemis) | [themes/LICENSE-lucide.txt](themes/LICENSE-lucide.txt) |

Generated images and video (`themes/assets/*.webp`, `themes/assets/portal/*.mp4`) were
produced for this project with `openai/gpt-image-2` (via OpenRouter) and MiniMax-H3
(ComfyUI, local GPU); they are published under the repository's MIT licence. Their
prompts, parameters and cost are recorded in `themes/assets/manifest.json`.

Runtime data sources (Nominatim / OpenStreetMap, sunrise-sunset.org, Nager.Date,
Open-Meteo, frankfurter.dev, open.er-api.com, Google Flights via `fast-flights`) are
queried live and are **not** redistributed; their terms — including OpenStreetMap
attribution, the Nominatim usage policy (1 request/s, identifying User-Agent, cache)
and the sunrise-sunset.org attribution requirement — are honoured in the scripts and
printed on the rendered pages where required. See `references/data-sources.md`.
