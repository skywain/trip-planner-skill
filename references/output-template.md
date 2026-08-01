# Output formats

Two formats, two jobs: **§city-block** is the machine hand-off from a city researcher
to the assembler, and the scheduling.md block is the human-facing rendering of the
same day. Both examples are written in mixed Chinese/English purely because that is
the sample trip — the deliverable always follows the user's own language.

## §city-block — what each city researcher returns (fan-out or sequential)

Return exactly this structure so blocks merge cleanly into the final plan:

Field names match the plan JSON the scripts consume, so transcribing a block is a
rename-free copy: the block's `city` becomes each day's `city`, and a day's `theme`
becomes the plan JSON's `label`.

```yaml
city: Kyoto
dates: 2026-10-04 → 2026-10-07 (3 nights)
transit_note: bus day-pass ¥700 wins on temple days (est. 4+ rides); ICOCA otherwise
days:
  - date: 2026-10-05
    theme: East Kyoto classics
    anchors:
      - name: Kiyomizu-dera
        hours: "06:00-18:00, no closures that week — official site, checked 2026-08-01"
        price: "¥500"
        book_ahead: no
        cluster: Higashiyama
      # ≤ pace + 1 anchors per day
    route_order: Kiyomizu → Sannenzaka → Yasaka → Gion (walkable, one line)
    food_area: Nishiki side streets (lunch) / Pontocho (dinner)
    rain_alt: Sanjusangendo (open daily, indoor hall — verified for this date)
    timing_flags: "last entry Kiyomizu 17:30"
    sun: "☀ 05:53 / 🌇 17:38"
    timeline:                      # hour-level, per references/scheduling.md
      # kind: anchor|hop|meal|free
      # anchors/meals carry `tag` (pinned|opener|skippable|swap→X); hops carry
      # `verify` (verified|est) — never mix the two, or parallel blocks merge dirty
      - {t: "09:00-11:00", what: "Kiyomizu-dera", kind: anchor, price: "¥500",
         note: "at opening beats the queue; last entry 17:30", tag: opener}
      - {t: "11:00-11:25", what: "步行 清水寺→二年坂 1.2 km · 25分", kind: hop,
         link: "https://www.google.com/maps/dir/?api=1&…", verify: est}
      - {t: "12:00-13:15", what: "lunch · Nishiki side streets", kind: meal,
         tag: "swap→Pontocho"}
      - {t: "13:15-13:45", what: "地铁 乌丸线(往竹田方向) 4站/9分 ¥260 · 四条→京都 · 出口2",
         kind: hop, link: "https://www.google.com/maps/dir/?api=1&…", verify: verified}
    late_cut: "running >1 h late → drop Yasaka Shrine"
    travel_day: false          # true on a base-change day — rendered differently
    day_map: "https://www.google.com/maps/dir/?api=1&…&waypoints=…"  # route_tools links
    ribbon: "清水寺 →步行10′→ 高台寺 →步行5′→ 八坂神社 →巴士25′→ 银阁寺"
    walking_km: 5.4   # HONEST total: check's figure ×1.3 + strolls + in-venue —
                      # never the raw check number, which understates it several-fold
    stops: [{name: 清水寺, query: "Kiyomizu-dera, Kyoto, Japan"},
            {name: 银阁寺, query: "...", mode: transit}, ...]
                      # mirrors this day's anchors + modelled strolls in visit order;
                      # every map artifact is computed from it. `mode` marks a ridden
                      # hop so it leaves the walking total and gets transit directions
book_ahead_list:
  - {item: "...", lead_time: "...", where: official|Klook|GYG, note: "..."}
unverified:
  - "anything that survived 2 searches unverified"
searches_used: 7   # must be ≤ 8
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
5. **Day-by-day cards**: one card per day — header (date/city/theme + sunrise/sunset),
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
