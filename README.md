[English](README.md) | [简体中文](README.zh-CN.md)

# Trip Planner Skill

**One sentence in, a verified, hour-by-hour, bookable trip plan out — delivered as a
designed page in one of eight visual themes.** An open-format Agent Skill (`SKILL.md`)
that runs inside whichever coding agent you already use — Claude Code, Codex, Gemini CLI,
Cursor, GitHub Copilot, OpenCode, Qwen Code, Deep Code, Goose, Kiro, Roo Code, or any
other harness that loads Agent Skills: it checks opening hours, prices and holidays with
tools instead of guessing, hands you a link for every booking, and never books or pays
for you.

![Agent Skills: open format](https://img.shields.io/badge/Agent%20Skills-open%20format-0A7B83.svg)
![Agents: Claude Code · Codex · Gemini CLI · Cursor · GitHub Copilot · OpenCode · Qwen Code · Deep Code · Goose · Kiro · Roo Code](https://img.shields.io/badge/agents-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Gemini%20CLI%20%C2%B7%20Cursor%20%C2%B7%20GitHub%20Copilot%20%C2%B7%20OpenCode%20%C2%B7%20Qwen%20Code%20%C2%B7%20Deep%20Code%20%C2%B7%20Goose%20%C2%B7%20Kiro%20%C2%B7%20Roo%20Code-4C51BF.svg)

[![Live demos](https://img.shields.io/badge/live%20demos-skywain.github.io-0A7B83.svg)](https://skywain.github.io/trip-planner-skill/)
![Verified in: Claude Code (others untested)](https://img.shields.io/badge/verified%20in-Claude%20Code%20%28others%20untested%29-8A63D2.svg)
![Models: any](https://img.shields.io/badge/models-any-informational.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)

<p align="center">
  <img src="docs/showcase/hero-grid.webp" alt="The eight themes, one cover each: illustrated, clay, noir, glass, journal, zine, splash, portal" width="900">
</p>

## Showcase

Eight themes across four real trips (two themes per trip). Every trip below was planned
end-to-end by a fresh agent session using this skill, then rendered from its `plan.geo.json`
+ `art.json`; the three frames per row are the cover, one day module (what the share buttons
export on the seven still themes) and the end of the scroll — the checklist and closing
spread. Four of the eight pages ship verbatim under [`examples/`](examples/); three of the
other four render from the same example folders with one command (each example's `art.json`
carries both of its trip's themes); portal additionally needs footage (see below).

Every page below is live: **[open the demo site](https://skywain.github.io/trip-planner-skill/)**
or click a theme's *Live page* link.

**illustrated** — Japan · London → Tokyo → Hakone → Kyoto → Osaka (open-jaw) → London,
21–28 Nov 2026 · a painted picture-book on paper: the cover is the menu, each day a tinted
riso plate with a ghost numeral, the whole scroll exports as one long image ·
[examples/japan-2026](examples/japan-2026/) ·
**[Live page ↗](https://skywain.github.io/trip-planner-skill/examples/japan-2026/japan-illustrated.html)**

| cover | a day | the end |
|---|---|---|
| <img src="docs/showcase/illustrated-cover.webp" width="280"> | <img src="docs/showcase/illustrated-day.webp" width="280"> | <img src="docs/showcase/illustrated-end.webp" width="280"> |

**clay** — China · New York → Beijing → Xi'an → Beijing → New York, 11–18 Nov 2026 · one
continuous claymation landscape with a road threading the milestone stones ·
render it: `python3 themes/render_clay2.py examples/china-2026/china.geo.json -o china-clay.html` ·
**[Live page ↗](https://skywain.github.io/trip-planner-skill/examples/china-2026/china-clay.html)**
(Chinese-language clay example: [examples/turkey-2026](examples/turkey-2026/) ·
[live ↗](https://skywain.github.io/trip-planner-skill/examples/turkey-2026/turkey-clay.html))

| cover | a day | the end |
|---|---|---|
| <img src="docs/showcase/clay-cover.webp" width="280"> | <img src="docs/showcase/clay-day.webp" width="280"> | <img src="docs/showcase/clay-end.webp" width="280"> |

**noir** — Mexico · Berlin → Mexico City → Oaxaca → Berlin, 28 Oct – 6 Nov 2026 (Día de
Muertos) · one night-negative tracking shot, monospace body, days dissolving into each
other · render it: `python3 themes/render_noir2.py examples/mexico-2026/mexico.geo.json -o mexico-noir.html` ·
**[Live page ↗](https://skywain.github.io/trip-planner-skill/examples/mexico-2026/mexico-noir.html)**
(Chinese-language noir example: [examples/nordic-2026](examples/nordic-2026/) ·
[live ↗](https://skywain.github.io/trip-planner-skill/examples/nordic-2026/nordic-noir.html))

| cover | a day | the end |
|---|---|---|
| <img src="docs/showcase/noir-cover.webp" width="280"> | <img src="docs/showcase/noir-day.webp" width="280"> | <img src="docs/showcase/noir-end.webp" width="280"> |

**glass** — Morocco · Toronto → Marrakech → Aït Benhaddou → Merzouga → Fes → Chefchaouen →
Casablanca → Toronto, 6–15 Nov 2026 · liquid-glass panes floating over a fixed world of
cross-fading photographs, one pane per world · [examples/morocco-2026](examples/morocco-2026/) ·
**[Live page ↗](https://skywain.github.io/trip-planner-skill/examples/morocco-2026/morocco-glass.html)**

| cover | a day | the end |
|---|---|---|
| <img src="docs/showcase/glass-cover.webp" width="280"> | <img src="docs/showcase/glass-day.webp" width="280"> | <img src="docs/showcase/glass-end.webp" width="280"> |

**journal** — Mexico · Berlin → Mexico City → Oaxaca → Berlin, 28 Oct – 6 Nov 2026 · a
vintage travel journal on a dark desk: tape, stamps, postmarks, polaroids, and a Day of the
Dead week planned around the crowd · [examples/mexico-2026](examples/mexico-2026/) ·
**[Live page ↗](https://skywain.github.io/trip-planner-skill/examples/mexico-2026/mexico-journal.html)**

| cover | a day | the end |
|---|---|---|
| <img src="docs/showcase/journal-cover.webp" width="280"> | <img src="docs/showcase/journal-day.webp" width="280"> | <img src="docs/showcase/journal-end.webp" width="280"> |

**zine** — Japan · London → Tokyo → Hakone → Kyoto → Osaka (open-jaw) → London,
21–28 Nov 2026 · torn riso-poster collage with giant vertical two-colour glyphs, built like a
photocopied fan zine · render it: `python3 themes/render_zine.py examples/japan-2026/japan.geo.json -o japan-zine.html` ·
**[Live page ↗](https://skywain.github.io/trip-planner-skill/examples/japan-2026/japan-zine.html)**
(Chinese-language zine example: [examples/vietnam-2026](examples/vietnam-2026/) ·
[live ↗](https://skywain.github.io/trip-planner-skill/examples/vietnam-2026/vietnam-zine.html))

| cover | a day | the end |
|---|---|---|
| <img src="docs/showcase/zine-cover.webp" width="280"> | <img src="docs/showcase/zine-day.webp" width="280"> | <img src="docs/showcase/zine-end.webp" width="280"> |

**splash** — China · New York → Beijing → Xi'an → Beijing → New York, 11–18 Nov 2026 · a
game splash screen stretched into a scroll: floating day-islands under a chained sky, routed
Xi'an-first so the Wall and the Forbidden City both land on weekdays ·
[examples/china-2026](examples/china-2026/) ·
**[Live page ↗](https://skywain.github.io/trip-planner-skill/examples/china-2026/china-splash.html)**

| cover | a day | the end |
|---|---|---|
| <img src="docs/showcase/splash-cover.webp" width="280"> | <img src="docs/showcase/splash-day.webp" width="280"> | <img src="docs/showcase/splash-end.webp" width="280"> |

**portal** — Morocco · Toronto → Marrakech → Aït Benhaddou → Merzouga → Fes → Chefchaouen →
Casablanca → Toronto, 6–15 Nov 2026 · scrolling is flying: five 3D worlds in one unbroken
take, dive → frame-chained link → dive, with the day's plan laid over the footage; let go and
it holds, scroll back and it flies in reverse. The only theme that needs video (nine clips
here, rendered on a local GPU; an agent with native video generation or `themes/genvideo.py`
produces the same chain). Footage is not shipped with the example, so the page in the repo
is screenshots only; the demo site serves the nine clips from a release asset, which makes
the live link below the real thing — the motion capture is recorded from it ·
[examples/morocco-2026](examples/morocco-2026/) ·
**[Live page ↗](https://skywain.github.io/trip-planner-skill/examples/morocco-2026/morocco-portal.html)**
(16 MB of video)

<p align="center">
  <img src="docs/showcase/portal-motion.webp" alt="Portal theme in motion: dive into a world, link to the next, day overlay on top (animated)" width="640">
</p>

| cover | a day | the end |
|---|---|---|
| <img src="docs/showcase/portal-cover.webp" width="280"> | <img src="docs/showcase/portal-day.webp" width="280"> | <img src="docs/showcase/portal-end.webp" width="280"> |

Every render command, cost and file for the seven trips is listed in
[`examples/README.md`](examples/README.md). The plain, un-themed page — the printable
extra, never the default deliverable — looks like
[`examples/kyoto-sample.html`](examples/kyoto-sample.html) (a Chinese-language sample; the
same renderer produces the English UI from a `"lang": "en"` plan);
`themes/render_picker.py` builds a style-chooser page linking every rendered edition of a
trip as `<prefix>-<theme>.html`.

## What you get

Say *"Japan, 12–15 days in October, mid budget, history and food."* The skill returns:

- **A route across cities** — 2–3 skeletons to pick from, then real flight prices for a grid
  of dates and a train-vs-fly call for every intercity leg.
- **An hour-level plan for every day** — opening hours and closure days checked with tools,
  dwell times and buffers from a written scheduling method, a holiday and festival collision
  scan, and a tappable map link on every hop.
- **A designed page as the deliverable, not a wall of text** — the plan is rendered
  through one of the **eight themed renderers** above (default **illustrated**) into one
  self-contained, phone-friendly file: `trip-<theme>.html`. The seven still themes carry
  offline share-image buttons (*Save this day* / *Save appendix* / *One long image*;
  whole-page export on five of the eight — noir and glass export day modules only), and
  portal (video) has no share buttons — screenshot it. The plain printable page is an
  extra you can ask for.
- **`plan.geo.json`, the single source of truth** — the themed page, the map links and an
  offline KML for Organic Maps / Google My Maps all come out of that one file.
- **A hotel shortlist by neighbourhood** (dated deep links, not invented nightly rates), a
  budget rollup in your home currency, a travel-insurance line calibrated to the
  destination, and a **booking checklist sorted by deadline** — with date-locked gates
  (ticket-release instants, decision deadlines, on-trip re-checks) also delivered as a
  **`.ics` calendar file**: dual alarms per gate, the full action list in the event
  body, and floating local times so an on-trip reminder rings wherever you are.
- **Pictures, whatever your agent can do** — three rungs, checked silently before the
  page style ever comes up: your agent's **native** image generation → your own
  OpenRouter **key** → the built-in **stock kit**. The last rung still ships a themed
  page, and says so in plain words (see *No image generator?* below).

What it will not do: book, pay, hold, or enter personal data. You click the links.

## Quick start

**1. Install** — agents that support Agent Skills discover them by directory, so clone
straight into your skills folder (Claude Code's path is shown; other agents: see
[Compatibility](#compatibility)):

```bash
git clone https://github.com/skywain/trip-planner-skill.git ~/.claude/skills/trip-planner
pip3 install --user fast-flights Pillow   # optional: flight price scanner · asset pipeline
```

Everything else is Python 3.9+ standard library. Without `fast-flights` the scanner degrades
to a Google Flights link; without Pillow you can still render every theme from the shipped
picture library. If `pip3 install --user` is refused with `externally-managed-environment`
(PEP 668: Homebrew / Debian Python 3.11+), install into a `python3 -m venv` instead, or add
`--break-system-packages`.

**Try it in 30 s** — no key, no agent needed, from the repo root:

```bash
python3 scripts/render_plan.py examples/kyoto-sample.plan.geo.json -o kyoto.html          # the plain page (Chinese-language sample)
python3 themes/render_clay2.py examples/china-2026/china.geo.json -o china-clay.html \
  && python3 themes/qc.py china-clay.html                                                 # an English themed page + its QC (exit 0)
```

(For a Chinese-language themed page swap in `examples/turkey-2026/turkey.geo.json`; the
other six trips and their commands are in [`examples/README.md`](examples/README.md).)

**2. Plan a trip** — in your agent, one sentence. The skill triggers on its own for trip /
flight / itinerary requests, or explicitly:

```
/trip-planner Japan, 12-15 days in October from London, mid budget, history and food, dates ±3 days
```

The plan's UI language follows the language you ask in (`"lang": "zh"|"en"` in the plan;
`--lang` overrides on every renderer). Four modes are picked from what you ask:

| Mode | Trigger | What runs |
|---|---|---|
| **Full trip** | "plan me 12 days in Japan" | All phases: intake → country brief → route skeleton → flights → day plans → hotels → assemble + self-check |
| **Single day** | "we have one day in Rome" | Holiday/festival check + that day + self-check; flights and hotels skipped |
| **Gap filler** | "I'm near X with 2 free hours" | 2–3 options within a 15-min radius, each with walk time, map link, turn-back deadline |
| **Live replan** | "missed the train / it's pouring" | Rebuilds only the affected day from its degradation tags |

**3. The designed page** — this is the deliverable the skill hands over, in the theme you
picked (default **illustrated** = `render_theme2.py`), never a plain text page. Three
commands, from the repo root (full manual: [`themes/README.md`](themes/README.md),
[`references/themes.md`](references/themes.md)):

```bash
# optional: a <plan>.art.json beside the plan is picked up automatically — cover title, per-day titles, which pictures go where
python3 themes/render_<theme>.py plan.geo.json -o trip-<theme>.html   # theme2 clay2 noir2 glass2 journal zine splash portal
python3 themes/qc.py trip-<theme>.html                                # exit 0 = clean; exit code = FAIL count
themes/xprobe.sh trip-<theme>.html module '#d5' out.png              # click the real share button headlessly, look at out.png (macOS + Chrome only)
```

The art contract is [`themes/ART-SCHEMA.md`](themes/ART-SCHEMA.md); every field is optional
and an empty art file must still render. Pictures resolve `--assets` → art dir → plan dir →
`themes/assets/`.

**4. Pictures and video: three rungs, best first.** The skill walks this ladder itself,
silently, before it ever mentions a page style:

1. **Native** — the agent running the skill can already generate images or video, so it
   uses that: art drawn for this trip, **no key to set up** (same specs and prompts, same
   `split_sheet.py` → `cutout.py` → `towebp.py` → trip-manifest steps; the contract is the
   generator-choice section of `themes/ART-SCHEMA.md`).
2. **One key** — no native generation: create `themes/.auth_header` containing one line —
   `Authorization: Bearer <your OpenRouter key>` — (gitignored, read only from that
   directory; both scripts pass it to curl as a header file, so it must be the full header
   line, not the bare key). `--dry-run` prints the credential path it would read:

   ```bash
   python3 themes/gen.py <trip>/jobs.json --outdir <trip> --manifest <trip>/manifest.<trip>.json      # gpt-image-2; --dry-run first
   python3 themes/genvideo.py jobs.json --outdir <trip>/portal --manifest <trip>/manifest.<trip>.json  # veo-3.1-lite by default; --models for prices
   ```

3. **Stock kit** — neither of the above: the pictures come from the kit bundled in this
   repo, and the page is still a themed page (next block).

On every rung the shipped library comes first —
[`themes/assets/IMAGE-LIBRARY.md`](themes/assets/IMAGE-LIBRARY.md) indexes 355 stems
(515 webp, 30 MB) by subject, and its rules draw the line: generic props are reusable,
while anything destination-specific (covers, hero plates, title stickers, terrain bands,
splash islands, journal photos) must belong to the trip it is on. Real costs from the
shipped examples: **$0.25–0.46 of image generation per trip** (7–11 `gpt-image-2` calls).
The **portal** theme is the one that needs footage: either `genvideo.py` in the cloud
(`google/veo-3.1-lite`, 720p, ≈ $0.03/s → roughly $3 for a ten-world chain; smoke-tested
on one 4 s clip, $0.12) or a local GPU (the author's regression footage comes from ComfyUI
on an RTX 5090 via `themes/build_portal_jobs.py`). The US chain that drove the design
(19 clips, ~35 MB) is the style reference and a [release asset](https://github.com/skywain/trip-planner-skill/releases/download/demo-assets-v1/us-portal-clips.zip),
not part of the tree — one `curl` + `unzip` restores it into `themes/assets/portal/`
([how](themes/assets/portal/README.md)). The shipped portal case is Morocco, live on the
demo site; another trip needs its own chain.

**No image generator? Still a designed page.** Two commands, and the plan comes out in a
real theme instead of degrading to plain text:

```bash
python3 themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
python3 themes/render_theme2.py plan.geo.json --art plan.art.json \
        --assets themes/assets/stock -o trip-illustrated.html   # --assets is required here
```

The kit (`themes/assets/stock/`, 80 stems / 161 webp / 5.2 MB, all in the illustrated
gouache style) holds 14 region cover paintings, 30 generic scene cut-outs and 36
world-landmark cut-outs; `stock_art.py` picks the cover from the destination country and
one hero per day by keyword score, leaves the words (cover title, day titles, captions) to
the agent, and writes the notice — *"Pictures: built-in stock kit — no image generator or
key was available; provide one and the art is generated for this trip."* — into the page's
fine print, where it must stay, and into the chat summary. Coverage: complete for
**illustrated**, works for **clay**; the other six themes need generated pictures.
Details: [`themes/assets/stock/README.md`](themes/assets/stock/README.md).

## How it works

**Pipeline.** `SKILL.md` is the playbook the agent follows: Phase 0 intake (one message,
only for what is missing) → Phase 1 country brief (visa from official sources, holiday API +
a budgeted festival search, weather, money, safety) → Phase 2 route skeletons → checkpoint
→ Phase 3 flights and intercity legs (`scripts/flight_scan.py`) → Phase 4 city day-plans
(parallel city subagents with an explicit search budget) → Phase 5 hotels → Phase 6
assemble, adversarial self-check, deliver. Three moments with the user at most, usually
two: an intake message only when a core fact is missing and cannot be inferred, the
route-skeleton pick, and delivery.

**Intake: no questions when the request already carries the facts.** *"Plan my Germany
trip, 1–7 Oct this year"* has the destination and the dates, so nothing is asked — the
origin and the rest are inferred and listed as assumptions at the first checkpoint. Only a
genuinely missing core fact (destination, when / how long, an origin that cannot be
inferred) triggers a single intake message, and the optional preferences ride along in that
same message, each one marked *skip = default*: travel style (public transport ·
self-drive · group tour), lodging habit and band, scenery taste (nature / city / beach /
forest / lake / mountain), pace, party size, budget, ranked interests, date flexibility.
Whatever you answer or the skill assumes is written into the plan's `prefs` block
([`assets/plan.example.json`](assets/plan.example.json)) so a later replan does not re-ask.
Say *"just plan it, don't ask"* and both the intake and the route checkpoint are skipped,
with every assumption stated at the top of the result.

**One file, one truth.** `plan.geo.json` is written once and read by everything:
`scripts/route_tools.py` (`geocode` · `check` · `links --write` · `kml` · `sun`) produces
the map links and the KML from its `stops`; `scripts/render_plan.py` produces the plain
HTML; every themed renderer reads the same file plus its `art.json`. That is what stops
the written plan, the map links and the pretty version from drifting apart. Schema
template: [`assets/plan.example.json`](assets/plan.example.json) — copy it, fill the
`PLACEHOLDER`s, then render (`render_plan.py` refuses an unfilled copy unless `--force`).

**Hard rules** (distilled from [`SKILL.md`](SKILL.md) and `references/`):

1. Never books, pays, holds, or enters personal data — links and a checklist only.
2. Prices and hours come from tools, never from memory; a missing price is "—, check link".
3. Cheap before expensive: bundled scripts and keyless APIs first, browser second; never
   curl OTA or airline sites.
4. Search budgets are explicit and written into every subagent prompt.
5. Estimates stay estimates: transit durations ship as `(est.)` ranges unless verified.
6. Beyond ~3 months out nobody publishes that day's hours — verify the seasonal pattern,
   stamp "as of {date}", put a re-confirm task on the checklist.
7. The plan must survive the self-check before delivery: closure scans, chain arithmetic,
   last-entry times, walking totals, open-jaw consistency.

**Data sources** — all keyless and free; prices are comparison-grade and the deep links
in the plan are the source of truth ([`references/data-sources.md`](references/data-sources.md)):

| Source | Used for | Notes |
|---|---|---|
| Google Flights (via `fast-flights`) | flight price grids | outbound legs listed; return times back-computed |
| Nominatim / OpenStreetMap | venue coordinates | 1 req/s + User-Agent enforced in-script; weak on non-Latin names |
| Nager.Date | public holidays | no religious / lunar holidays — a budgeted festival search covers the gap |
| Open-Meteo | weather and climate for the dates | first call can take ~10 s |
| sunrise-sunset.org | golden-hour scheduling | **requires visible attribution** in the plan footer |
| frankfurter.dev → open.er-api.com | FX | ECB daily, ~30 majors; minor / closed currencies fall back to open.er-api.com |
| Google Maps / Booking / operator sites | hotel bands, transit detail, tickets | browser, deep links only |

Hotels have no usable keyless API, so the skill recommends neighbourhoods and produces
dated deep links rather than quoting a nightly price it cannot verify.

## Compatibility

- **Format, not a product integration.** This is an [Agent Skill](https://agentskills.io)
  — an open format: a `SKILL.md` playbook plus `references/`, `scripts/` and `themes/`.
  Any harness that loads Agent Skills can load this one; nothing here is tied to one
  vendor's agent.
- **The agents.** Claude Code, Codex, Gemini CLI, Cursor, GitHub Copilot, OpenCode,
  Qwen Code, Deep Code (DeepSeek), Goose, Kiro and Roo Code all declare support for
  `SKILL.md` skills, and the scripts here are stdlib-only Python 3.9+. The only difference
  between them, from this repo's point of view, is where they expect skills to live — so
  the `git clone` target in Quick start is the one line you adapt.
- **Verified in Claude Code; the rest are untested.** Every trip, render and export in
  this repository was produced in Claude Code, and the install path above is its skills
  directory. **We have not run the other harnesses one by one — reports welcome**,
  including the skills directory each one expects.
- **What the harness needs.** A shell that can run Python 3.9+ (the scripts), and web
  search / fetch tools (the country brief, day plans and hotel phases verify hours, prices
  and holidays online). Nice-to-have: subagents (Phase 4 fans out one agent per city — a
  harness without them plans the cities in sequence), a browser tool (the flight and hotel
  price fallbacks when the keyless scripts fail), and native image / video generation (else
  an OpenRouter key, else the bundled stock kit — the page stays themed either way).
- **Any model.** The skill is instructions plus scripts; whatever model your harness runs
  (Claude, GPT, Gemini, Qwen, DeepSeek, Mistral, …) executes it. Stronger models follow the
  verification rules more faithfully; the scripts behave the same regardless.
- **Native generation is optional.** Pictures and portal footage use the agent's own image /
  video generation when it has one; otherwise `themes/gen.py` / `themes/genvideo.py` with a
  single OpenRouter key; otherwise `themes/stock_art.py` and the bundled stock kit.
  Rendering from the shipped library or the stock kit needs no key at all.

## Repository layout

```
README.md  README.zh-CN.md    this page, English and Chinese
THIRD-PARTY-NOTICES.md        license texts for the redistributed font and icons (Caveat OFL, Lucide ISC)
SKILL.md                      the playbook: phases, hard rules, quick modes
references/
  data-sources.md             every API + URL recipe, with fallback chains
  scheduling.md               dwell times, buffers, day types, traps, verification list
  navigation.md               map links, hop-row format, verify-vs-estimate policy
  country-quick-notes.md      per-country passes, sell-outs, closure patterns (+ "destination not listed" checklist)
  output-template.md          the city-block hand-off + final deliverable structure
  phase-0-intake.md           Phase 0 procedure: core vs optional facts, origin inference, intake message, prefs, picture-capability check, exit criteria
  phase-1-brief.md            Phase 1 procedure: fact lines, advisory line, emergency card, health line + yellow-fever audit, hazard line, exit criteria
  phase-3-legs.md             Phase 3 procedure: plan shape, price-source ladder, separate-tickets audit, rail vs fly, driving legs, leg fields, exit criteria
  phase-4-days.md             Phase 4 procedure: city-agent contract, six per-city steps, route_tools order, sun / check rules, exit criteria
  phase-6-assemble.md         Phase 6 procedure: assembly, adversarial self-check, delivery, themed-render flow, exit criteria
  cover-titles.md             bilingual poetic cover-title library + cliché blacklist
  themes.md                   themed-render manual: the eight themes, adding one, defect checklist
  art-schema.md               pointer to themes/ART-SCHEMA.md
scripts/
  flight_scan.py              Google Flights grid scanner (keyless, centre-out)
  route_tools.py              geocode → distance check → map links → KML → gates .ics → sun times
  plan_lint.py                the plan's content gate before rendering: brief, placeholders, self-check line, art, .ics + .kml; --strict adds a stop and a sun --write string per day (exit = FAIL count)
  render_plan.py              plan JSON → self-contained printable HTML
  build_site.py               examples + showcase → the GitHub Pages demo site (_site/)
.github/workflows/
  pages.yml                   builds and deploys that site on every push to main
themes/
  README.md                   what is here, the three commands, where pictures come from
  render_theme2.py …          eight renderers: theme2 (illustrated) · clay2 · noir2 · glass2 · journal · zine · splash · portal
  render_picker.py            style-chooser page (links <prefix>-<theme>.html)
  theme_common.py             shared helpers, i18n, the offline share-image engine
  qc.py  xprobe.sh  xt.sh     static QC · headless export probes
  gen.py  genvideo.py         fallback generators (OpenRouter gpt-image-2 / video, one key) for agents without native generation
  stock_art.py                no generator, no key: builds the picture side of art.json from the stock kit
  towebp.py cutout.py split_sheet.py build_manifest.py build_portal_jobs.py
                              asset pipeline (png→webp, cut-outs, sheet splitting, manifest, portal jobs)
  ART-SCHEMA.md               the art.json contract (the only copy)
  assets/                     picture library: 444 webp (301 stems), Caveat font, manifest.json,
                              IMAGE-LIBRARY.md (index by subject), portal/ (footage sidecar dir —
                              empty in the tree, README.md has the restore command)
    stock/                    the stock kit: 14 region covers + 66 cut-outs (161 webp, 5.2 MB),
                              index.json (lookup: archetypes, 225 ISO2, keywords, notice), README.md
assets/plan.example.json      schema template — copy it, fill the PLACEHOLDERs, then render (or --force to preview)
examples/
  README.md                   the seven trips: themes, routes, costs, every render command
  japan-2026/ …               one folder per trip: <trip>.geo.json + <trip>.art.json + <trip>-<theme>.html
  kyoto-sample.*              the plain page's sample plan, its HTML and its KML
docs/
  showcase/                   README images (hero grid, per-theme cover / day / end frames, portal motion capture)
  verification.md             how the skill was hardened, and what the reviews caught
  KNOWN-ISSUES.md             30 defects and hard limits (29 open / planned, 1 resolved), each with a source pointer, plus the roadmap
```

Not in the repo: personal trip data (`trips/`), PNG originals, the US portal reference
chain (`themes/assets/portal/*.mp4` — a `demo-assets-v1` release asset), and the OpenRouter
credential file `themes/.auth_header` that `gen.py` / `genvideo.py` read. A clone is
**~48 MB tracked**.

## Verification

- **Static QC** — `themes/qc.py page.html` checks the offline contract (no network, no
  external fetches), no-JS survival, print, focus order and link hygiene; exit code is the
  FAIL count. The seven themed examples re-render byte-identically from the commands in
  [`examples/README.md`](examples/README.md) and pass; the plain `render_plan.py` page
  (`examples/kyoto-sample.html`) passes too.
- **Export probes** — `themes/xprobe.sh` / `xt.sh` drive a headless Chrome to click the
  page's real share button and write the image it produces, so export defects are seen,
  not assumed. macOS with Google Chrome in `/Applications` only (the path is hardcoded in
  the probes). Run them serially.
- **Friction testing** — the most valuable technique: give a fresh agent that has never
  seen the skill a real trip request, let it follow the instructions in order, and treat
  every place it got confused as the primary deliverable. Eleven test trips (Australia,
  Nordic, Japan, China, Italy, Mexico, Morocco, Turkey, Vietnam, Yunnan, Peru) were
  planned this way, each by a fresh agent session, on top of the earlier Kyoto and Rome
  runs; the friction points became rules in `references/` and entries in
  `country-quick-notes.md`.
- **Adversarial review** — three rounds by seven independent agents (script torture-tester,
  external fact-checker, tour-leader realism attacker, cross-file coherence reviewer, two
  end-to-end builders). What they caught, and the rules that came out of it:
  [`docs/verification.md`](docs/verification.md).

## Status and known issues

Working, personal-use software under active development, and **harness-agnostic on
purpose**: an Agent Skill, not a Claude Code plugin — verified end-to-end in Claude Code,
expected to run in the ten other agents listed under [Compatibility](#compatibility), and
untested there until someone files a report. Every defect and hard limit in the current
tree is listed in [`docs/KNOWN-ISSUES.md`](docs/KNOWN-ISSUES.md) — 30 entries (29 open or
planned, 1 resolved) across export/renderers, planning scripts, assets and scope, each with
a symptom, workaround and source pointer, plus a short roadmap (whole-page export sizing,
journal `zh` cover fix, picker copy, a portrait portal chain, a post-trip photo album,
affiliate rails for a hosted version).

**Requirements.** Python 3.9+ (macOS system Python is fine); standard library only,
except optional `fast-flights` (flight scanner) and Pillow (asset pipeline: `towebp.py`,
`cutout.py`, `split_sheet.py`, `gen.py`). `gen.py` / `genvideo.py` need `themes/.auth_header`
(one line: `Authorization: Bearer <OpenRouter key>`) — and only when the agent has no native
image/video generation of its own; with neither, `stock_art.py` and the bundled stock kit
still produce a themed page. The export probes need macOS with Google Chrome in
`/Applications` (path hardcoded). Rendering any theme from the shipped library or the stock
kit needs none of these.

**Limitations and non-goals.**

- **Personal-use posture.** The browser and scraping steps are what one traveller would do
  by hand. A hosted service for others would need affiliate rails (Travelpayouts, an
  Amadeus production key, Viator/GetYourGuide APIs) — the free sources here are not
  licensed for redistribution.
- **Not real-time.** It plans; it does not track delays or rebook.
- **Prices move.** Every figure carries an as-of date for exactly that reason.
- **Portal needs footage** you generate or render yourself; the shipped chain is one trip's.

## Contributing

Issues and pull requests are welcome. The four most useful contributions:

- **A compatibility report** — run the skill in a harness other than Claude Code and tell
  us what worked, what did not, and where that harness expects skills to live.
- **A new country** — add a section to
  [`references/country-quick-notes.md`](references/country-quick-notes.md) following the
  "Destination not listed?" checklist at the top of that file (passes, sell-outs, closure
  patterns, holiday feed gaps), ideally after planning a real trip there with the skill.
- **A new theme** — read [`references/themes.md`](references/themes.md) §4 (adding a theme)
  and §5 (the recurring-defect checklist, every item on every new theme); the art contract
  is `themes/ART-SCHEMA.md`, and shared helpers live in `themes/theme_common.py`.
- **A friction report** — plan a trip with the skill as a first-time user and file every
  place the instructions fought you. That is how most of the current rules were found.

Before opening a PR: `python3 themes/qc.py` on any themed page you rendered (exit 0), one
`xprobe.sh` export looked at with your own eyes, and re-render one of the `examples/`
trips to confirm it is still byte-identical.

## Credits

- [Caveat](https://fonts.google.com/specimen/Caveat) (SIL Open Font License 1.1) — the handwriting
  webfont embedded in the journal theme (`themes/assets/caveat-vf.woff2`).
- [Lucide](https://lucide.dev/) (ISC) — the icon sprite in `themes/lucide-icons.json`.
  License texts for both: [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
- [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors and
  [Nominatim](https://operations.osmfoundation.org/policies/nominatim/) — geocoding, under
  its usage policy (1 req/s, identifying User-Agent).
- [sunrise-sunset.org](https://sunrise-sunset.org/) — sun times; attribution is required
  wherever the data is shown, and the rendered plan pages print it in the footer.
- [Nager.Date](https://date.nager.at/), [Open-Meteo](https://open-meteo.com/),
  [frankfurter.dev](https://frankfurter.dev/), [open.er-api.com](https://www.exchangerate-api.com/)
  — holidays, weather, FX.
- Generated pictures: `openai/gpt-image-2` via [OpenRouter](https://openrouter.ai/).
  The US portal reference chain (19 mp4, a `demo-assets-v1` release asset) and the Morocco
  portal footage in the showcase were rendered locally with MiniMax-H3 in ComfyUI; the cloud alternative
  in `genvideo.py` is `google/veo-3.1-lite` (default) or `minimax/hailuo-3` via OpenRouter.

## License

MIT — see [LICENSE](LICENSE). © 2026 skywain.
