# Output formats

Two formats, two jobs: **§city-block** is the machine hand-off from a city researcher
to the assembler, and the scheduling.md block is the human-facing rendering of the
same day. Both examples are written in mixed Chinese/English purely because that is
the sample trip — the deliverable always follows the user's own language. The
assembled file itself follows the **§Top-level plan skeleton** just below.

## §Top-level plan skeleton — the assembled `plan.geo.json`

`assets/plan.example.json` is the single source of truth for these keys (it runs
through every script as-is); the shape below is copied from it and from the schema
comment at the top of `scripts/render_plan.py`, which reads exactly these names.
Every key is optional except `days[].date` — an unfilled section simply does not
render — but a section of the **wrong shape** is not "optional": it renders as an
empty table with a WARN on stderr pointing here (the Vietnam test wrote `budget` as
`{note, rows[{item,pp,total}]}` and `legs` with invented keys — both renderers used
to crash on it, and `legs` still prints every cell blank).

```json
{
 "trip": "Japan 12 days",
 "lang": "zh",                                  // zh | en — see §Plan language
 "meta": {"dates", "party", "route", "budget_total", "fx", "generated", "self_check"},
 "decisions": ["one line per decision made for the traveller — each vetoable", ...],
 "checklist": [{"item", "deadline", "price", "link", "link_text", "note"}],
 "legs":      [{"type", "date", "carrier", "from", "to", "dep", "arr", "price", "bags",
                "link", "note", "backup"}],
 "days": [{"date", "city", "label", "sun", "sun_stop", "day_map", "ribbon", "rain_alt",
           "late_cut", "walking_km", "travel_day", "tz",
           "timeline": [{"t", "what", "kind", "price", "note", "tag", "verify",
                         "link", "map"}],
           "hop_links": ["url", ...],           // written by links --write when parked
           "stops": [{"name", "query", "lat", "lon", "mode"}]}],
 "hotels": [{"base", "area", "why", "options": [{"name", "band", "link"}]}],
 "budget": [{"cat", "per_person", "total", "note"}],   // a LIST of rows, not {rows:[]}
 "brief":  {"visa", "holidays", "weather", "money", "connectivity"},
 "unverified": ["anything that survived two searches unverified", ...]
}
```

- `budget` rows are `{cat, per_person, total, note}` (strings, already in the home
  currency; the buffer line is a row like any other). `legs` rows spell the airports
  `from`/`to` and the clock `dep`/`arr`; `backup` is a free-text second choice.
- `checklist` (top level, `{item, deadline, price, link, link_text, note}`) is the
  merged, urgency-sorted list; the city block's `checklist_items` (same row shape,
  minus `link_text`) is its **input** — the assembler copies those rows into
  `checklist` (renderers never read `checklist_items`), so both names are correct,
  each in its own file. Visa rows never come from a city block (SKILL Phase 1/4).
- `days[].sun_stop` (optional) — the `name` or 0-based index of the stop `sun --write`
  should key the day on, overriding its default (first stop; last stop on a moving
  day). Set it on a moving day whose sunrise anchor is at the *first* stop
  (Chefchaouen sunrise → fly to Casablanca; Erg Chebbi sunrise → Fes).
- `days[].tz` (optional, IANA name) overrides the plan-level `tz` for `sun`.
- Field-level meaning of the `days[]` object (timeline `kind`/`tag`/`verify`,
  `map:false`, `stops` ↔ hop rows) is in §city-block right below — the day objects
  are byte-identical in both places.

## §city-block — what each city researcher returns (fan-out or sequential)

Return **plan-JSON fragments, not a parallel dialect**. The assembler inserts your
`days` array elements into the plan file verbatim — on the first real multi-city run
the researchers returned YAML with different field names (`theme` for `label`,
`anchors` beside `timeline`, `book_ahead_list` for checklist rows) and every block had
to be transcribed by hand, which is exactly where errors breed. The day objects below
follow `scripts/render_plan.py`'s schema field-for-field.

```json
{
 "days": [
  {"date": "2026-10-05", "city": "Kyoto", "label": "East Kyoto classics",
   "sun": "天亮 05:28 · ☀ 05:53 / 🌇 17:38 · JST · sunrise-sunset.org",
   "travel_day": false,
   "rain_alt": "Sanjusangendo (open daily, indoor — closure-checked for THIS date)",
   "late_cut": "running >1 h late → drop Yasaka Shrine",
   "ribbon": "清水寺 →步行10′→ 八坂神社 →巴士25′→ 银阁寺",
   "walking_km": {"total": 5.4, "how": "on-foot 2.4×1.3 + 散步 1.5 + 馆内 ~0.8"},
   "timeline": [
    {"t": "09:00-11:00", "what": "清水寺", "kind": "anchor", "price": "¥500",
     "note": "开门即到避人流;最晚入场 17:30 — 官网核 2026-08-01", "tag": "opener"},
    {"t": "11:00-11:25", "what": "步行 清水寺→二年坂 1.2 km · 25分", "kind": "hop",
     "verify": "est"},
    {"t": "12:00-13:15", "what": "午餐 · 锦市场周边", "kind": "meal",
     "tag": "swap→先斗町"},
    {"t": "13:15-13:45", "what": "地铁 乌丸线(往竹田方向) 4站/9分 ¥260 · 四条→京都 · 出口2",
     "kind": "hop", "verify": "verified"},
    {"t": "15:55", "what": "JAL 起飞 → …", "kind": "hop", "verify": "verified",
     "map": false}
   ],
   "stops": [
    {"name": "清水寺", "query": "Kiyomizu-dera, Kyoto, Japan"},
    {"name": "银阁寺", "query": "Ginkaku-ji, Kyoto, Japan", "mode": "transit"}
   ]}
 ],
 "hotels": [
  {"base": "Kyoto 3 晚", "area": "四条乌丸", "why": "…",
   "options": [{"name": "…", "band": "…", "link": "…带日期深链…"}]}
 ],
 "tour_options": [
  {"name": "…", "price": "…含单房差/门票包/非居民费/小费口径…", "schedule": "班期 —
    静态可核则给核实结论,JS 日历给链接标 unverified", "pickup": "…", "link": "…"}
 ],
 "checklist_items": [
  {"item": "…", "deadline": "…", "price": "…", "link": "…", "note": "…"}
 ],
 "unverified": ["anything that survived 2 searches unverified"],
 "searches_used": 7
}
```

Field discipline (the merge breaks without it):
- `checklist_items` = sell-outs, timed tickets, date-locked rail, tours — things the
  city researcher verified. **No visa / entry / e-visa rows**: the assembler owns that
  fact (SKILL Phase 1) and overwrites any city-block claim about it (two Turkey city
  agents shipped an outdated "visa required" as item #1). The assembler merges these
  rows into the top-level `checklist` (§Top-level plan skeleton).
- `sun` is filled by the assembler's `sun --write`, not by you; if the day's sunrise
  anchor is at its first stop on a moving day, add `"sun_stop": "<that stop's name>"`
  so the assembler's run keys the day there.
- `timeline` rows: `kind` = anchor|hop|meal|free;anchors/meals carry `tag`
  (pinned|opener|skippable|swap→X);hops carry `verify` (verified|est);flight/rail
  hops already covered by the legs table carry `"map": false`. Never mix tag/verify.
- N mapped `stops` ⇒ N−1 hop rows without `map:false` — that alignment is what lets
  `links --write` place every URL automatically. Lodging→first-stop and
  last-stop→lodging rows, and rides that are themselves the sight (cruise, scenic
  train, ferry) are the two places this slips — see navigation.md step 1.
- `sun` is written by `route_tools.py sun --write` in the canonical shape
  `天亮 HH:MM · ☀ HH:MM / 🌇 HH:MM[ · TZ · sunrise-sunset.org]` — for an `en` plan
  (`plan.lang`, or `sun --lang en`) the dawn word is `dawn`:
  `dawn HH:MM · ☀ HH:MM / 🌇 HH:MM[ · TZ · sunrise-sunset.org]`; the renderers accept
  either spelling. If you hand-write it, keep a space after every time (no
  `18:00(AEST`).
- `walking_km` is the honest total (`{"total", "how"}` form preferred).
- Do NOT run geocoding — the assembler runs route_tools once, centrally (five agents
  in parallel would break Nominatim's 1 req/s policy).
- Verified facts carry source + as-of date in `note`; everything else is `est` and,
  if load-bearing, also listed in `unverified`.

## Plan language — top-level `"lang"`

The assembled plan JSON carries one top-level key `"lang": "zh" | "en"` (default
`zh` when absent; `meta.lang` is read as a fallback). It is a **plan fact**: set it
in Phase 0 from the language the user asked in, and never mix it with the content —
`lang` only says which language the rendered page's own chrome speaks (section names,
buttons, tags, weekdays, the "天亮/dawn" word, `<html lang>`), while every string you
wrote into the plan (labels, notes, stops, brief) is printed exactly as written.
`scripts/render_plan.py`, every `themes/render_*.py` and `route_tools.py sun --write`
read it (`--lang zh|en` overrides per run); the shared word table lives in
`themes/theme_common.STRINGS`. An `en` plan whose `sun` was written by hand uses the
`dawn …` form (see the `sun` bullet above).

```json
{"trip": "Japan 12 days", "lang": "en", "meta": {"dates": "…", "route": "…"}, "days": [ … ]}
```

## Final deliverable

One self-contained HTML file — inline CSS, no external assets, printable, readable on
a phone — produced by `scripts/render_plan.py` from the plan JSON. The JSON is the
editable source; there is no separate Markdown copy to keep in sync. Structure, in
order:

1. **Header**: route one-liner, dates, party, total budget in home currency, FX rate +
   date.
2. **Decisions made for you**: 3-5 bullets (jaw direction, pass math, pace calls…) —
   each one vetoable by the user.
3. **Booking checklist** (the action list lives near the top on purpose), sorted by
   urgency: visa → sell-outs → intl flights → date-locked rail → refundable hotels →
   the rest. Each row: item · deadline/lead time · price + as-of date · deep link ·
   checkbox.
4. **Flights & intercity table**: pick + backup per leg with all Phase 3 fields.
5. **Day-by-day cards**: one card per day — header (date/city/label + sunrise/sunset),
   then the hour-level timeline as a two-column table: 时间 · 内容. Hops are their own
   rows, styled dimmer, written in the canonical hop-row format from navigation.md
   (mode, line + direction, stops/duration, fare, boarding→alighting station, exit
   number) with the tappable link on the row; price and notes sit under the activity
   name; tags ([pinned]/[opener]/[skippable]/[swap→…]) and hop markers
   ((verified)/(est.)) render as pills at the end of the row.
   render_plan.py also draws a small offline route schematic per day straight from
   `stops` — one more reason to fill `stops` even for days you already mapped.
   Below the table: the whole-day map link, the honest walking total, the rain
   alternative, the `ribbon` one-liner (Stop1 →walk 12′→ Stop2 →metro 9′→ …) and the
   late_cut line. Travel days are marked visually by `travel_day: true`.
6. **Hotels**: per base — neighborhood rationale, 2-3 properties, band, dated links.
7. **Budget table**: category rows (flights/lodging/intercity/local/entries/food),
   per-person and total columns, 10-15% buffer line, FX note, as-of dates.
8. **Country brief**: visa summary, holiday collisions, weather line, money +
   connectivity notes.
9. **Footer**: generation date · "prices move — links are the source of truth" ·
   self-check result (N issues found and fixed) · ⚠️ unverified list · offline tip:
   import the delivered trip.kml into Organic Maps / Google My Maps · data credits
   (sunrise-sunset.org for sun times — required attribution; © OpenStreetMap
   contributors when OSM geocoding fed the map links).

The accompanying chat summary: route one-liner, total budget, the 3 biggest decisions,
and which checklist item needs the user's action first.

HTML style: system font stack, max-width 720px, day cards with a left border, the
checklist as a real `<table>`, print CSS (no shadows; page breaks between days are
fine). No JS required; a tiny inline script persisting checkbox state to localStorage
is welcome.
