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
 "tz": "Asia/Tokyo",                            // optional IANA default; days[].tz
                                                // overrides — cross-tz plans need one
                                                // of the two set or `sun` refuses
 "prefs": {"theme", "pictures", "travel_style", "lodging", "scenery", "pace", "budget",
           "notes"},                            // Phase 0 intake — see §Intake prefs
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
                                                // extra keys become their own card
                                                // inside the Country-brief section;
                                                // titles from theme_common.BRIEF_TITLES
                                                // (fallback: the raw key; art
                                                // brief_titles overrides) — see
                                                // §Booking-artifact conventions
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

### §Intake prefs — top-level `prefs`

What Phase 0 (Intake) learned or **assumed**, written down once so Phases 2-6 and any
later replan read one place instead of re-asking the user. Renderers ignore the whole
block (it is not in `theme_common.PLAN_SHAPE`, and adding it leaves every rendered page
byte-identical) — it is a note the planning agent leaves for itself.

```json
"prefs": {
  "theme": "illustrated",
  "pictures": "stock",
  "travel_style": "public",
  "lodging": "hotel · mid-range, refundable",
  "scenery": ["city", "nature"],
  "pace": 3,
  "budget": "mid",
  "notes": "assumed origin PVG (zh request, no origin given)"
}
```

- `theme` ∈ `illustrated|clay|noir|glass|journal|zine|splash|portal` — which of the
  eight themed pages is the deliverable. Default **illustrated 插画版**.
- `pictures` ∈ `native|key|stock` — the result of Phase 0's picture-capability check:
  a native image-generation tool · `themes/.auth_header` (an OpenRouter key, never read
  or printed) · neither, so the built-in stock kit supplies the pictures. It decides how
  the art file gets built at Phase 6, and `stock` is what puts the picture notice into
  the chat summary and the page's fine print.
- `travel_style` ∈ `public|self-drive|group-tour|mixed` (default `public`) — Phase 2
  shapes the legs from it and Phase 3 adds a rental leg for `self-drive`.
- `lodging` — free text: type + band (default mid-range hotel, refundable), read by
  Phase 5.
- `scenery` ⊂ `nature|city|beach|forest|lake|mountain` — Phase 2 scores the longlist
  against it.
- `pace` — anchors per day (2/3/4, default 3); `budget` — a band word or a number.
- `notes` — every value that was **inferred rather than told**, in one string, so the
  assumptions block at checkpoint (a) can be written straight from this object.

Only what is known or defensibly assumed goes in; a key the user never touched and the
agent never needed is simply absent. An intake that asked nothing (the request already
carried destination + dates) still fills `prefs` — from the defaults it chose.

### §Intake message — the one question block (only when a core fact is missing)

Shape: a bold one-line lead, **必答 / Must answer** then **选答 / Optional**, numbered
continuously, one option list per line with the default named, and at most two footer
lines (ℹ️ stock-picture note, only in stock mode; 💡 "all defaults" shortcut, only when
optional items are shown). **Only items the user has not already given** appear — a
heading with nothing under it is dropped. A guessed core value is asked as a
confirmation, not an open question. One message, never a follow-up. Markdown, in the
user's language.

**zh sample** — request was "帮我规划一次日本之旅" (destination known, everything else
missing, no image generator in the session):

```
**先确认几件事 —— 一条消息回我,写序号+答案;没写的按默认**

**必答**
1. 出发城市 —— 我猜是上海(你用中文问的),对吗?
2. 玩多久、大概什么时候 —— 例:10.1–10.7,或「7 天 · 10 月 · 前后可挪 2 天」

**选答(不答走默认)**
3. 页面风格:插画(默认)· 黏土 · 夜航 · 玻璃 · 手账 · Zine · 闪屏 · 穿越 —— 样子见 https://skywain.github.io/trip-planner-skill/
4. 出行方式:公共交通+步行(默认)· 自驾 · 跟团
5. 住宿:中档酒店(默认)· 青旅 · 民宿 · 公寓 · 温泉旅馆
6. 偏好:城市 · 自然风光 · 海滩 · 森林 · 湖泊 · 山 —— 默认按目的地定
7. 人数 / 预算 / 节奏:默认 2 成人 · 中档 · 每天 3 个主要点

ℹ️ 本次会话没有生图能力,页面会用内置插画素材(仍是成品页,只是不如定制图贴合);有 OpenRouter key 的话放进 themes/.auth_header 再告诉我,就能为这趟生成。
💡 回「默认」= 全部按默认,直接开工。
```

**en sample** — request was "Plan me 10 days in Portugal in May, we're a family of four,
self-driving" (destination, duration, month, party and travel style already given → none
of them is asked; the session has a native image generator → no ℹ️ line):

```
**Two quick things before I plan — reply in one message, number + answer; anything you skip uses the default**

**Must answer**
1. Departure city — I'm guessing London (your timezone); right?

**Optional (skip = default)**
2. Page style: illustrated (default) · clay · noir · glass · journal · zine · splash · portal — see https://skywain.github.io/trip-planner-skill/
3. Lodging: mid-range hotel (default) · hostel · B&B / guesthouse · apartment
4. Taste: city · nature · beach · forest · lake · mountain — default: read from the destination
5. Budget / pace: default mid-range · 3 main stops a day

💡 Reply "defaults" and I start right away.
```

Answers land in `prefs` (above); what was guessed and not corrected goes into
`prefs.notes` and the assumptions block at checkpoint (a).

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
   "options": [{"name": "…", "band": "…", "link": "…deep link with dates…"}]}
 ],
 "tour_options": [
  {"name": "…",
   "price": "…include single supplement / fee package / non-resident surcharge / tipping basis…",
   "schedule": "departure days — with a
    browser, page the pricing calendar and read each date cell before giving a
    verified conclusion (the marketing 'Available Days' blurb doesn't count);
    without one, ship the calendar link marked unverified", "pickup": "…", "link": "…"}
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

**A themed HTML page, never a plain text one.** Phase 6 renders `plan.geo.json` through
the theme picked in Phase 0 (`prefs.theme`, default **illustrated 插画版**) into
`trip-<theme>.html` — one self-contained file (pictures inlined as data URIs, no
network, opens by double-click), phone-friendly, carrying its own share/export buttons
and the appendix — and ships the trip KML beside it for offline map apps
(`scripts/route_tools.py kml plan.geo.json -o trip.kml`). Details of the eight themes
and the art file: `references/themes.md`, `themes/ART-SCHEMA.md`.

The plain `scripts/render_plan.py` page — printable, checkbox checklist, a small offline
route sketch per day — is an **extra**, not the deliverable: render it when the user asks
for a printable or plain version, or as the last resort if the theme renderer still fails
after one honest fix attempt (then say which it is in the summary). `plan.geo.json` is
the single editable source for both, so a later change is a JSON edit plus
geocode → check → links → kml → render, never a rewrite; there is no separate Markdown
copy to keep in sync.

Both pages present the same material in the same order:

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
   then the hour-level timeline as a two-column table: 时间 · 内容 (time · activity).
   Hops are their own rows, styled dimmer, written in the canonical hop-row format
   from navigation.md (mode, line (toward …), stops/minutes, fare ·
   boarding→alighting stop · exit number) with the tappable link on the row; price
   and notes sit under the activity
   name; tags ([pinned]/[opener]/[skippable]/[swap→…]) and hop markers
   ((verified)/(est.)) render as pills at the end of the row.
   render_plan.py also draws a small offline route schematic per day straight from
   `stops` — one more reason to fill `stops` even for days you already mapped.
   Below the table: the whole-day map link, the honest walking total, the rain
   alternative, the `ribbon` one-liner (Stop1 →walk 12′→ Stop2 →metro 9′→ …
   authored by the planner in Phase 4 — no script writes it; the renderers only
   print it) and the late_cut line. Travel days are marked visually by `travel_day: true`.
6. **Hotels**: per base — neighborhood rationale, 2-3 properties, band, dated links.
7. **Budget table**: category rows (flights/lodging/intercity/local/entries/food),
   per-person and total columns, 10-15% buffer line, FX note, as-of dates.
8. **Country brief**: visa summary, holiday collisions, weather line, money +
   connectivity notes.
9. **Footer**: generation date · "prices move — links are the source of truth" ·
   the self-check result (N issues found and fixed) — write that line into
   `meta.self_check`, which the plain page's footer prints, **and** repeat it as the
   last `decisions[]` row, because that is the field the themed pages actually
   render: seven of the eight print `decisions` (illustrated, clay, noir, glass,
   journal, zine, splash) and only **journal** also prints `meta.self_check`, in its
   footer; **portal** shows neither — it is the video page, so there the chat summary
   carries the self-check · ⚠️ unverified list · offline tip:
   import the delivered trip.kml into Organic Maps / Google My Maps · data credits
   (sunrise-sunset.org for sun times — required attribution; © OpenStreetMap
   contributors when OSM geocoding fed the map links).

The accompanying chat summary: route one-liner, total budget, the 3 biggest decisions,
which checklist item needs the user's action first — and, when `prefs.pictures` is
`stock`, the one-line picture notice, in the plan's language:

> **en** — Pictures: built-in stock kit — no image generator or key was available;
> provide one and the art is generated for this trip.
>
> **zh** — 图片来自内置素材库(本次未接入生图能力);接入生图模型或 KEY 后可为本次行程定制生成。

The same notice sits in the page's fine print, where `stock_art.py` puts it — do not
delete it from either place.

**The assumptions block at checkpoint (a)** — one block at the top of the route-skeleton
message, written from `prefs`: the inferred origin (and what it was inferred from), every
optional field that fell back to a default, and the picture mode when it is not `native`.
It exists so a wrong guess costs the user one line to correct instead of a round trip of
questions. In "一次到位 / don't ask" mode there is no checkpoint (a), so the same block
goes at the top of the delivery instead.

HTML style of the **plain** page: system font stack, max-width 720px, day cards with a
left border, the checklist as a real `<table>`, print CSS (no shadows; page breaks
between days are fine). No JS required; a tiny inline script persisting checkbox state to
localStorage is welcome. The themed pages own their own visual language — do not restyle
them toward this one.

### §Booking-artifact conventions (checklist + hotels rows)

- **Dates ride inside every booking link** (`checkin=`/`checkout=` on hotel
  searches, date params on flight links) and place names carry their disambiguator
  (state / prefecture / full property name) — a link the user can mis-city is a
  bug, not a convenience. When the route contains collision-prone names
  (one-letter-apart airport codes, the same city name in several states, a
  same-name hotel airside AND landside in one airport, aggregators mixing nearby
  airports into a search), the brief gets a `lookalikes` entry naming each trap.
  Themed renderers title brief cards from `theme_common.BRIEF_TITLES` (fallback:
  the raw key; the art file's `brief_titles` overrides) — `lookalikes` is not in
  that table, so give it its display title via `brief_titles` (zh: 重名陷阱), or on
  a zh-only plan simply key the entry 重名陷阱 — unlike `altitude` and `navigation`,
  which are now built-in `BRIEF_TITLES` keys and need no override. The country files
  carry the known traps (see §USA).
- **Hotel stays are explicit local calendar dates** ("check-in D1 → check-out D3"
  = the nights of D1 and D2). Booking sites use the hotel's local calendar and
  never convert timezones — the mis-bookings are human, so pre-chew the two
  classics wherever the plan contains them, on the checklist row itself and not
  only in prose: a past-midnight arrival still sleeps the PREVIOUS calendar night
  (book the landing date + a "late arrival" note, never the clock date the guest
  walks in on); a date-line crossing books the ARRIVAL-local calendar date, not
  the departure date.
- **Date-locked rows also ship as a calendar file**: when the checklist carries
  gates (a ticket-release instant, a decision deadline, an on-trip re-check),
  offer a `.ics` beside the page (worked example: `examples/gates-sample.ics`)
  — one VEVENT per gate, with the FULL action
  list in DESCRIPTION (the user acts from the alarm, not from memory: what to
  do, the fallback if it fails, the linked bookings by number), two VALARMs
  (`-P1D` and `-PT30M`), and stable UIDs with an incremented SEQUENCE and
  fresh DTSTAMP on every plan change. Write times as FLOATING local times (no
  `Z`, no `TZID`): a pre-trip gate then fires on home wall-clock, and an
  on-trip gate at that hour in whatever timezone the traveller is standing in
  — which is what an on-trip re-check wants. The exception is a fixed-instant
  gate (a ticket drop at home-timezone clock time): schedule it on a pre-trip
  date when it is one, and when it can fall mid-trip give that one VEVENT a
  TZID-anchored DTSTART with its VTIMEZONE — RFC 5545 allows mixing anchored
  and floating events in one file. File mechanics are strict
  (RFC 5545): escape DESCRIPTION newlines as `\n`, fold long content lines at
  75 octets, include VERSION/PRODID and a DTSTAMP per event. Client caveats
  belong on the page, not in the user's lap: Google Calendar pins floating
  times to the calendar's timezone, skips same-UID re-imports instead of
  updating, and replaces VALARMs with its own default reminders (Apple/iOS
  Calendar honours floating times and VALARMs) — so open each DESCRIPTION
  with the intended hour ("09:00 local, wherever you are"), and after a plan
  change instruct
  "delete the old events, then import the new file".

