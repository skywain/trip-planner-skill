# Examples

Seven finished trips, one per theme, plus the plain-page sample. Each folder holds only
the two source files and the page they produce — `<trip>.geo.json` (the facts),
`<trip>.art.json` (what the trip looks and sounds like) and `<trip>-<theme>.html`
(self-contained: every picture is an inlined webp, so the page opens by double-click with
no network). Re-running the render command below rewrites the shipped page **byte for
byte**, which is what makes these examples a regression test as well as a showcase.

The eighth theme, `portal`, is a video fly-through. Its page **is** here
(`morocco-2026/morocco-portal.html`, 13 KB — the markup is small because the footage is not
inlined), but its nine clips are ~16 MB and are not committed; they are published as the
`demo-assets-v1` release asset `morocco-portal-clips.zip`, which `scripts/build_site.py`
downloads when it builds the demo site. So the portal page renders complete online and
warns about missing `portal/*.mp4` when you open the repo copy locally.

## Open them without cloning

Every page below is served from the demo site, built by `scripts/build_site.py` and
deployed by `.github/workflows/pages.yml`. Each one is the real deliverable — ~1.5 MB,
self-contained, no server:

Eleven pages are live. Eight are the gallery's cards — one per theme, all English, each
one matching the frames in the root README's Showcase. Three of those eight are **not
stored in the repo**: `china-clay`, `mexico-noir` and `japan-zine` are rendered at build
time by `scripts/build_site.py`, straight from the committed `geo.json` + `art.json` (each
art file carries its trip's second theme, so nothing extra is needed). The remaining three
rows are the shipped Chinese editions of those same themes.

| Trip · theme | Lang | Live page | On disk |
|---|---|---|---|
| `japan-2026` · `illustrated` | en | <https://skywain.github.io/trip-planner-skill/examples/japan-2026/japan-illustrated.html> | shipped |
| `china-2026` · `clay` | en | <https://skywain.github.io/trip-planner-skill/examples/china-2026/china-clay.html> | rendered at build time |
| `mexico-2026` · `noir` | en | <https://skywain.github.io/trip-planner-skill/examples/mexico-2026/mexico-noir.html> | rendered at build time |
| `morocco-2026` · `glass` | en | <https://skywain.github.io/trip-planner-skill/examples/morocco-2026/morocco-glass.html> | shipped |
| `mexico-2026` · `journal` | en | <https://skywain.github.io/trip-planner-skill/examples/mexico-2026/mexico-journal.html> | shipped |
| `japan-2026` · `zine` | en | <https://skywain.github.io/trip-planner-skill/examples/japan-2026/japan-zine.html> | rendered at build time |
| `china-2026` · `splash` | en | <https://skywain.github.io/trip-planner-skill/examples/china-2026/china-splash.html> | shipped |
| `morocco-2026` · `portal` | en | <https://skywain.github.io/trip-planner-skill/examples/morocco-2026/morocco-portal.html> | shipped (16 MB of video, fetched) |
| `turkey-2026` · `clay` | zh | <https://skywain.github.io/trip-planner-skill/examples/turkey-2026/turkey-clay.html> | shipped |
| `nordic-2026` · `noir` | zh | <https://skywain.github.io/trip-planner-skill/examples/nordic-2026/nordic-noir.html> | shipped |
| `vietnam-2026` · `zine` | zh | <https://skywain.github.io/trip-planner-skill/examples/vietnam-2026/vietnam-zine.html> | shipped |

The gallery that links all of them: <https://skywain.github.io/trip-planner-skill/>. Each
trip's `geo.json` and `art.json` sit next to its page there too, so the sources are one
click away.

## The seven trips

| Trip | Theme | Origin → route | Dates | Lang | Cover title | Image generation |
|---|---|---|---|---|---|---|
| `japan-2026` | `illustrated` | London → Tokyo · Hakone · Kyoto · Osaka (KIX, open-jaw) | 21–28 Nov 2026 · 8 days | en | "Late Maples" | $0.4090 · 10 `gpt-image-2` calls → 18 webp via sheet splitting |
| `turkey-2026` | `clay` | Shanghai (PVG) → Istanbul · Cappadocia · Pamukkale · Istanbul | 1–9 Oct 2026 · 9 days | zh | 九万里风 / NINETY THOUSAND MILES OF WIND | $0.2594 · 7 calls → 19 webp via sheet splitting |
| `nordic-2026` | `noir` | Beijing (PEK) → Oslo · Bergen Railway · Flåm / Nærøyfjord · Bergen | 1–8 Oct 2026 · 8 days | zh | 天接云涛 / SEA OF CLOUDS | $0.2484 · 7 calls → 17 webp |
| `morocco-2026` | `glass` | Toronto → Marrakech · Aït Benhaddou · Merzouga · Fes · Chefchaouen · Casablanca | 6–15 Nov 2026 · 10 days | en | "Ochre Road" | $0.3624 · 11 calls; plus a `portal` variant at 21 GPU min on a local 5090 |
| `mexico-2026` | `journal` | Berlin (BER) → Mexico City · Teotihuacán · Oaxaca | 28 Oct – 6 Nov 2026 · 10 days | en | "Marigold" | $0.2820 · 8 calls → 18 webp |
| `vietnam-2026` | `zine` | Shenzhen (SZX) → Hanoi · Ha Long Bay · Hoi An / Da Nang · Ho Chi Minh City | 12–21 Dec 2026 · 10 days | zh | 人海 / A SEA OF FACES | $0.4566 · 11 calls → 28 webp |
| `china-2026` | `splash` | New York (JFK) → Beijing · Xi'an · Beijing | 11–18 Nov 2026 · 8 days | en | "MOON OF QIN" | $0.2991 · 7 calls → 23 stems |

$2.32 of image generation for all seven pages. No GPU time anywhere except the Morocco
`portal` variant — the stills-only themes never need one.

### In one line each

- **japan · illustrated** — a paper picture-book: the cover is the menu, each day gets a
  tinted riso plate with a ghost numeral and polaroid stickers, and the whole scroll
  exports as one long image.
- **turkey · clay** — one continuous claymation landscape scrolled end to end: modelled
  minarets, fairy chimneys and travertine terraces, with the overnight bus to Pamukkale
  sculpted in as its own scene.
- **nordic · noir** — a night-flight cinema: five stacked full-bleed negatives that
  cross-fade as you scroll, with the aurora odds argued down to an honest 5–10% instead
  of sold as a headline.
- **morocco · glass** — frosted-glass app chrome floating over six ochre desert plates;
  the itinerary reads like a native travel app, one pane per world, from the red rooftops
  to the blue mountain.
- **mexico · journal** — an open travel journal on one continuous sheet: vintage
  photographs taped down, torn ticket stubs, marigold ephemera, and a Day-of-the-Dead
  week that plans around the crowd.
- **vietnam · zine** — a cut-and-paste photocopy zine: film-grain plates, chapter posters
  and hand-set headlines, built around the one leg where the night train genuinely beats
  the flight.
- **china · splash** — a game splash poster stretched into a scroll: an abstract light
  field falling past floating day-islands, routed Xi'an-first so the Wall and the
  Forbidden City both land on weekdays.

## Render them

Run from the repo root; every line rewrites the shipped page exactly.

```
python3 themes/render_theme2.py  examples/japan-2026/japan.geo.json     -o japan-illustrated.html
python3 themes/render_clay2.py   examples/turkey-2026/turkey.geo.json   -o turkey-clay.html
python3 themes/render_noir2.py   examples/nordic-2026/nordic.geo.json   -o nordic-noir.html
python3 themes/render_glass2.py  examples/morocco-2026/morocco.geo.json -o morocco-glass.html
python3 themes/render_journal.py examples/mexico-2026/mexico.geo.json   -o mexico-journal.html
python3 themes/render_zine.py    examples/vietnam-2026/vietnam.geo.json -o vietnam-zine.html
python3 themes/render_splash.py  examples/china-2026/china.geo.json     -o china-splash.html
```

`cmp japan-illustrated.html examples/japan-2026/japan-illustrated.html` exits 0, and so does
the same check on the other six — that is the regression gate. Three conventions keep the
commands that short:

- **`--art` is implicit.** A renderer picks up `<plan>.art.json` sitting beside the plan.
  Running from somewhere else, or with an art file kept elsewhere, pass
  `--art examples/japan-2026/japan.art.json` — the art file's own folder joins the asset
  search path, so its pictures come along.
- **Pictures resolve from `themes/assets/`.** Every trip's stems are prefixed with the
  trip name (`japan-…`, `nordic-…`), so `--assets` is never needed here and a library
  size-variant can't shadow a trip's own picture.
- **The page language follows the plan** (`lang` / `meta.lang`); `--lang zh|en` on any
  renderer overrides the chrome, while art copy renders in whatever language it was
  written in.

## Two themes per art file

Each `art.json` carries the shipped theme's block **and a second theme's block**, so one
extra command gets a completely different page out of the same trip — the cheapest way to
see how far apart the themes really are.

| Art file | Shipped page | Second theme | Render it |
|---|---|---|---|
| `japan.art.json` | `illustrated` | `zine` | `python3 themes/render_zine.py examples/japan-2026/japan.geo.json -o japan-zine.html` |
| `turkey.art.json` | `clay` | `illustrated` | `python3 themes/render_theme2.py examples/turkey-2026/turkey.geo.json -o turkey-illustrated.html` |
| `nordic.art.json` | `noir` | `journal` | `python3 themes/render_journal.py examples/nordic-2026/nordic.geo.json -o nordic-journal.html` |
| `morocco.art.json` | `glass` | `portal` | `python3 themes/render_portal.py examples/morocco-2026/morocco.geo.json -o morocco-portal.html` |
| `mexico.art.json` | `journal` | `noir` | `python3 themes/render_noir2.py examples/mexico-2026/mexico.geo.json -o mexico-noir.html` |
| `vietnam.art.json` | `zine` | `splash` | `python3 themes/render_splash.py examples/vietnam-2026/vietnam.geo.json -o vietnam-splash.html` |
| `china.art.json` | `splash` | `clay` | `python3 themes/render_clay2.py examples/china-2026/china.geo.json -o china-clay.html` |

Morocco's `portal` block is the one that cannot render fully here: the page builds, but it
warns that nine `.mp4` clips are missing, because the video (~16 MB) is not shipped. The
shipped `morocco-portal.html` is that same page — see it running, footage and all, at
<https://skywain.github.io/trip-planner-skill/examples/morocco-2026/morocco-portal.html>.
The other six second themes render complete pages — and three of them, `china-clay`,
`mexico-noir` and `japan-zine`, are exactly what the demo site serves for those themes,
rendered by these same commands on every deploy.

## Maps and the KML

The offline pin set is generated, not stored — one command per trip:

```
python3 scripts/route_tools.py kml examples/japan-2026/japan.geo.json -o trip.kml
```

The output imports into Organic Maps, Google Earth, My Maps or Maps.me. `kyoto-sample.kml`
is kept in the repo as the sample of what that file looks like. Several of these plans
mention their own `<trip>.kml` in the traveller advice ("import the trip KML in Organic
Maps") — that is exactly the file the command above writes, and a real delivery ships it
next to the page; only the repo keeps it out, because it is one command away.

## The plain page and the style picker

`kyoto-sample.plan.geo.json` → `kyoto-sample.html` is the plain, un-themed page (printable,
checkbox checklist, offline route sketch per day) — the extra deliverable, not the default:

```
python3 scripts/render_plan.py examples/kyoto-sample.plan.geo.json -o kyoto.html
```

The style picker builds a one-page chooser of all eight themes: it links all eight editions
by name — `<prefix>-<theme>.html`, the same naming these examples use — and marks the ones
not on disk with `—` in the size column:

```
python3 themes/render_picker.py examples/japan-2026/japan.geo.json \
    --prefix japan --products examples/japan-2026 -o picker.html
```

Full manual for the theme system: [`../references/themes.md`](../references/themes.md);
the art.json field contract: [`../themes/ART-SCHEMA.md`](../themes/ART-SCHEMA.md).
