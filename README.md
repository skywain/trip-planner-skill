# Travel Planner Skill(工作名,品牌待定)

**Hour-by-hour, verified, bookable trip plans — as a Claude Code skill.**

You say *"Japan, 12-15 days, October, mid budget, history and food."* You get back a
route across cities, real flight prices for a grid of dates, an hour-level plan for
every day with opening hours and closures checked, a tappable map link for every hop,
an offline KML, a hotel shortlist, a budget, and a booking checklist sorted by
deadline. It never books anything — you click the links.

> **中文摘要**:把"我要去某国玩 10-15 天"变成一份**可直接照着订**的行程。核心不是文采,
> 是**核实**:价格和营业时间一律来自工具而非模型记忆,每条都带来源和查询日期;查不到的
> 明确标 ⚠️,绝不假装查到了。产出是一个离线可看、可打印、手机友好的 HTML + 离线地图 KML。

See [`examples/kyoto-sample.html`](examples/kyoto-sample.html) for what the output
looks like (open it in a browser — it is fully self-contained).

## Why this exists

Dedicated AI travel products plan a pretty day and then quietly hand you a museum that
is closed on Mondays. Claude Code on its own reasons about routes well but has no
price or opening-hours data. **The bottleneck is data acquisition and verification
discipline, not LLM orchestration** — so that is what this skill encodes: a playbook of
keyless data sources, a scheduling method with the failure modes written down, and an
adversarial self-check the plan has to survive before it is delivered.

## Install

Claude Code discovers skills by directory, so clone it straight into place:

```bash
git clone git@gh-skywain:skywain/travel-planner-skill.git ~/.claude/skills/travel-planner
```

Optional — enables the flight price scanner (everything else is stdlib only):

```bash
pip3 install --user fast-flights
```

The skill then triggers on its own for trip/flight/itinerary requests, or explicitly
with `/travel-planner`.

## Usage

```
/travel-planner 10月从上海出发,日本12-15天,中等预算,历史+美食,日期可±3天,中国护照
```

Four modes, picked automatically from what you ask:

| Mode | Trigger | What runs |
|---|---|---|
| **Full trip** | "plan me 12 days in Japan" | All six phases: intake → country brief → route skeleton → flights → day plans → assemble + self-check |
| **Single day** | "we have one day in Rome" | Holiday/festival check + that day + self-check; flights and hotels skipped |
| **Gap filler** | "I'm near X with 2 free hours" | 2-3 options within a 15-min radius, each with walk time, map link, turn-back deadline |
| **Live replan** | "missed the train / it's pouring" | Rebuilds only the affected day from its degradation tags |

## What's inside

```
SKILL.md                      six-phase pipeline, hard rules, quick modes
references/
  data-sources.md             every API + URL recipe, with fallback chains
  scheduling.md               dwell times, buffers, day types, traps, verification list
  navigation.md               map links, hop-row format, verify-vs-estimate policy
  country-quick-notes.md      per-country passes, sell-outs, closure patterns
  output-template.md          the city-block hand-off + final deliverable structure
scripts/
  flight_scan.py              Google Flights grid scanner (keyless, centre-out)
  route_tools.py              geocode → distance check → map links → KML
  render_plan.py              plan JSON → self-contained printable HTML
assets/plan.example.json      runnable schema example — copy it and fill it in
examples/                     a rendered sample plan + its source JSON and KML
docs/verification.md          how this was hardened, and what the reviews caught
```

One file, `plan.geo.json`, is the single source of truth: `route_tools.py` reads its
`stops` to produce maps and the KML, `render_plan.py` reads everything else to produce
the HTML. That is deliberate — it is what stops the written plan and the map links from
drifting apart.

## Data sources

All keyless and free. Prices are comparison-grade; the deep links in the plan are the
source of truth.

| Source | Used for | Status |
|---|---|---|
| Google Flights (via `fast-flights`) | flight price grids | live-tested |
| Nominatim / OpenStreetMap | venue coordinates | live-tested — 1 req/s + User-Agent enforced in-script |
| Nager.Date | public holidays | live-tested |
| Open-Meteo | weather and climate for the dates | live-tested |
| sunrise-sunset.org | golden-hour scheduling | live-tested — **requires visible attribution** |
| frankfurter.dev | FX (ECB daily) | live-tested |
| Google Maps / Booking / operator sites | hotel bands, transit detail, tickets | browser, deep links only |

Hotels have no usable keyless API, so the skill recommends neighborhoods and produces
dated deep links rather than quoting a nightly price it cannot verify.

## The rules that make it different

1. **Never books, pays, or enters personal data.** It produces links and a checklist.
2. **Prices and hours come from tools, never from memory.** A missing price is written
   "—, check link", never guessed.
3. **Search budgets are explicit** — unbounded research agents hang and burn money.
4. **Estimates stay estimates.** Transit durations ship as ranges marked `(est.)`
   unless the hop was actually verified; anything unverified is listed visibly.
5. **Beyond ~3 months out, nobody publishes that day's hours** — so it verifies the
   seasonal pattern, stamps "as of {date}", and puts a re-confirm task on the checklist
   instead of claiming a certainty it cannot have.
6. **The plan must survive an adversarial self-check** before delivery: closure scans,
   chain arithmetic, last-entry times, walking totals, open-jaw consistency.

## Requirements

Python 3.9+ (macOS system Python is fine). Standard library only, except the optional
`fast-flights` for the flight scanner — and the scanner degrades to a browser link if
it is missing.

## Limitations and non-goals

- **Personal-use posture.** The browser and scraping steps are what one traveller would
  do by hand. Turning this into a service for others would need affiliate rails
  (Travelpayouts, an Amadeus production key, Viator/GetYourGuide APIs) — the free
  sources here are not licensed for redistribution.
- **Not real-time.** It plans; it does not track delays or rebook.
- **Prices move.** Every figure carries an as-of date for exactly that reason.

## License

MIT — see [LICENSE](LICENSE).
