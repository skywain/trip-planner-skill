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
           "drivers", "languages", "must_see", "notes"},   // Phase 0 intake — see §Intake prefs
 "meta": {"dates", "party", "route", "budget_total", "fx", "generated", "self_check", "review"},
 "decisions": ["one line per decision made for the traveller — each vetoable", ...],
 "checklist": [{"item", "deadline", "price", "link", "link_text", "note", "refundable"}],
 "legs":      [{"type", "date", "carrier", "from", "to", "dep", "arr", "price", "bags",
                "link", "note", "backup", "refundable"}],
 "days": [{"date", "city", "label", "sun", "sun_stop", "day_map", "ribbon", "rain_alt",
           "late_cut", "walking_km", "travel_day", "tz",
           "decision_points": [{"t", "what", "check", "if_no", "by", "src", "date"}],
           "timeline": [{"t", "what", "kind", "price", "note", "tag", "verify",
                         "link", "map", "tour", "sub_map", "hours",
                         "sub_stops": [{"name", "query", "lat", "lon", "tier", "stand",
                                        "walk_min", "must", "confirmed", "link"}]}],
           "hop_links": ["url", ...],           // written by links --write when parked
           "stops": [{"name", "query", "lat", "lon", "mode", "driver"}]}],
 "hotels": [{"base", "area", "why", "options": [{"name", "band", "link", "checkout", "bag_hold"}]}],
 "budget": [{"cat", "per_person", "total", "note"}],   // a LIST of rows, not {rows:[]}
 "brief":  {"visa", "emergency", "safety", "health", "holidays", "weather", "money",
            "connectivity", "insurance", "baggage"},   // in this order — §Brief templates;
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
- `meta.review` (optional) — the record behind the review clause: `{"mode":
  "reviewers" | "single pass", "lenses": [{"lens", "note"}], "confirmed": [...],
  "refuted": [...]}`. `lens` ∈ `safety` | `driving` | `timing` | `rules` | `hazards`,
  three or more distinct, each note saying what was checked against what, `driving`
  whenever a self-drive option exists; `confirmed` / `refuted` the findings a refuter
  confirmed / dropped (what each holds: phase-6-assemble.md §Independent review step
  4); with `reviewers` the clause's C and R equal the two lists' lengths, with `single
  pass` the clause reads "single pass" and `refuted` may be absent. Procedure and
  clause: phase-6-assemble.md §Independent review. `plan_lint.py` checks the shape
  and the clause agreement wherever the key is present, and under `--strict`
  requires both whenever the trigger set in its docstring holds.
- `hotels[].options[].checkout` / `bag_hold` (optional, per property — the base row
  is a shortlist): one string each, naming its source — `"11:00 · property FAQ · as of
  2026-10"`, `"held at the desk until 18:00 · ask at check-in"` (not `bags`: that is
  the baggage allowance on `legs[]`). Written once the property's own policies page was
  read, or once the traveller names the booked property (SKILL.md Phase 5 has the
  rule); scheduling.md §Day types times the leaving day from it. `plan_lint.py` fails
  an empty one and warns when `checkout` carries no HH:MM.
- `refundable: false` on a checklist or legs row — the explicit flag for a
  non-refundable booking or fare, set when the row is written (phase-3-legs.md
  §Record for every leg; hotel rows in §Booking-artifact conventions); `true` is
  allowed, any other value fails, and the lint never infers it from the row's text.
  It is one of the independent review's triggers (`plan_lint.py` docstring).
- `meta.generated` — the date the plan was written or last handed off, `YYYY-MM-DD`,
  re-stamped on every hand-off (phase-6-assemble.md §Deliver) and whenever a re-read
  writes `hours`. `plan_lint.py --strict`
  measures the hours window from it (or from `--asof`), so a date copied from
  `assets/plan.example.json` switches that check off.
- Field-level meaning of the `days[]` object (timeline `kind`/`tag`/`verify`,
  `map:false`, `stops` ↔ hop rows, `sub_stops`/`tour`, `hours`, `decision_points`,
  `driver`) is in §city-block right below — the day objects are byte-identical in
  both places.

### §Brief templates — canonical order, required keys, and the fixed-line cards

`brief` renders in **insertion order**, one card per key, titled from
`theme_common.BRIEF_TITLES` — so write the keys in this order and keep every card
≤ 8 lines: **visa → emergency → safety → health → holidays → weather → money →
connectivity → insurance → baggage**, then the triggered cards (`season`, `altitude`,
`navigation`, `lookalikes`, `packing`, `driving`) only when the trip has the trigger. Required
on every plan: `visa`, `safety`, `holidays`, `weather`, `money`, `connectivity`,
`insurance`, `emergency`, `health`.
**Sources for `emergency` and `health`** (phase-1-brief.md §Emergency card and §Health
line): the traveller's own foreign-ministry advisory page, the mission's own site,
the CDC / TravelHealthPro page, the insurer's schedule and the browser Google Maps
place card (ER only) are the only sources; a fact none of them carries → that line
reads "n/a — see advisory" next to the URL it read, never numbers from memory.
A key that is not in `BRIEF_TITLES` prints as its raw English key on a zh page —
add the title there (or via the art file's `brief_titles`) before inventing a key.

Three cards have fixed lines. Fill every line; "n/a" is an answer, silence is not.

**`brief.money` — five lines, then the origin block when it applies**
1. DCC: at any terminal or ATM choose "pay in local currency", never the machine's
   home-currency conversion (3-8 % per swipe).
2. Card FX fee: prefer a zero-FX card; otherwise the budget's buffer row gets
   +1.5-3 % with that reason in its note.
3. ATM: bank-lobby machines, few large withdrawals; state the typical local fee and
   per-withdrawal cap ⚡ (unknown → "check on arrival").
4. Cash: one number — "carry ≈ {home currency} X for {N} days of small spend" —
   sized to how cash-first the destination is; add the cash-declaration threshold
   on entry when the trip's cash reaches it (EU ≥ €10,000 · US > $10,000 ·
   JP > ¥1,000,000 ⚡).
5. Acceptance: Visa / Mastercard / UnionPay / Alipay+ / WeChat Pay — which of them
   work where, in one line.
Origin block, **mainland-China departure only**: UnionPay vs Visa/MC acceptance at
the destination (a single-brand UnionPay card stalls in Europe and North America —
carry a Visa/MC too); Alipay+ / WeChat cross-border coverage ⚡; foreign cash needs
a 1-2 day bank pre-order at home. Other origins get a block only when a documented
rule exists for them. The recipes behind these lines: data-sources.md §FX → Money
safety.

**`brief.connectivity` — the handset line, eSIM ballpark, plug type, then the
digital-safety line**: the handset line comes first — every phone in the party by model
and market variant, and whether it takes an eSIM, a physical SIM or both; the eSIM
ballpark says whether a voice- and SMS-capable local number is needed (operators and
small lodgings confirm by phone) and whether the eSIM activates only in-country
(phase-1-brief.md §The fact lines, Money & connectivity). Then: the roaming / eSIM setup must still receive SMS from the home number (bank 2FA;
12306 too for a mainland-China origin); a phone-theft plan (Find My / SIM PIN /
eSIM lock, cards freezable from
a second device); no banking on public Wi-Fi; passport, visa and policy as cloud +
offline copies. Last, only when the traveller wants to keep the local number after the
trip: the carrier's cheapest keep-alive plan and what keeps it alive, whether Wi-Fi
calling works from abroad and what it needs set up first, and that a store / play
account's region follows the account's country (the dated US case:
country-quick-notes.md §USA, Phone); that line's action is the "Before leaving
<country>" checklist row (§On-trip re-audit rows).

**`brief.safety` — the advisory line, then six named lines** (one set per trip, with
per-base detail where the bases differ):
0. Advisory: `{level} · {source} · as-of {date} (second source: {level})` —
   phase-1-brief.md §Advisory line; a Level-4 / "do not travel" hit never reaches this
   card, it stops the pipeline.
1. Named scams: the destination's 2-3 current scams by name, with the tell.
2. Pickpocket hotspots: the specific lines, stations and squares.
3. Taxi rule: which app, the official airport rank, never the arrivals-hall tout.
4. After-dark avoid list, per base, and the door-to-door rule for night moves.
5. When it happens: police report first — the report number is the insurance claim
   key; embassy and assistance numbers live in `brief.emergency`.
6. Legal & customs red lines: drones · vapes · food / biosecurity declarations ·
   alcohol / dress / blasphemy · photographing military or government sites ·
   same-sex relations law · medicines in luggage (the destination's rule for
   prescription drugs and for common cold-medicine ingredients it restricts —
   country-quick-notes.md §Medicines in luggage) — ≤ 3 lines copied from the advisory
   page's "Local laws and customs" section and the customs page, plus one line, from the
   home customs authority's allowance page (dated), for the home country's duty-free
   allowance on the way back when goods are bought on the trip (data-sources.md
   §Shopping requests), or "none beyond the usual".
Tone model only: `examples/vietnam-2026/vietnam.geo.json` → `brief.safety` (written
before this template — it covers lines 2-4 and lacks 0, 1, 5, 6; do not copy its
shape). Sources per line:
country-quick-notes.md (the destination's section, or the not-listed checklist's
"Street safety" line).

**`brief.emergency` — six lines, every number stamped as-of, none from memory**
(phase-1-brief.md §Emergency card): 1 local police · ambulance · fire numbers · 2 the
home consular hotline · 3 the nearest mission per base (name · address · phone · hours ·
link) · 4 insurer assistance line + policy-number placeholder + the first-call rule ·
5 lost-passport steps (police report → mission → exit-record rule) · 6 per base one
24-hour ER with an international department + the local word for pharmacy and one near
the hotel; a base > 2 h from an ER says so in the day note.

**`brief.health` — five lines from one official page** (phase-1-brief.md §Health line):
1 vaccines / prophylaxis "recommended for most / some travellers" + the travel-clinic
consult date (a checklist row; the plan never doses) · 2 vector-borne diseases and their
season · 3 water and food (tap water yes / bottled only · ice · raw and street food) ·
4 rabies and animals · 5 notice level + as-of + the page URL. Yellow-fever hits add the
ICVP checklist row.

**`brief.season` — triggered only** (phase-1-brief.md §Hazard line): the hazard · its
months · the official source URL · what the plan does about it (buffer day, refundable
rows, the gate) — ≤ 5 lines, absent when the window hits nothing.

**`brief.driving` — triggered whenever a self-drive option exists** (phase-1-brief.md
§Driving card is its only definition — the labelled line form, the five verdicts with
their zh forms, and what `plan_lint.py` checks on each legality line): one labelled
line per jurisdiction driven, then the insurance consequence once and, optionally, the
rules line (step 5) — written like every card, as one string with a line per
jurisdiction, never a nested object (the page prints that raw). `plan_lint.py` FAILs a
plan that has a self-drive option and no `driving` card, any card that is not a string,
and a legality line missing its verdict, desk part or as-of.

### §Intake prefs — top-level `prefs`

What Phase 0 (Intake) learned or **assumed**, written down once so Phases 2-6 and any
later replan read one place instead of re-asking the user. Renderers ignore the whole
block (it is not in `theme_common.PLAN_SHAPE`, and adding it leaves every rendered page
byte-identical) — it is a note the planning agent leaves for itself.

```json
"prefs": {
  "theme": "illustrated",
  "pictures": "stock",
  "travel_style": "mixed",
  "lodging": "hotel · mid-range, refundable",
  "scenery": ["city", "nature"],
  "pace": 3,
  "budget": "mid",
  "drivers": [{"who": "traveller 1", "licence_country": "CN"}],
  "languages": ["zh"],
  "must_see": [{"name": "Fushimi Inari", "tier": "overlook"}, {"name": "Kinkaku-ji"}],
  "notes": "assumed origin PVG (zh request, no origin given); car-first park segment undecided"
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
  shapes the legs from it and Phase 3 adds a rental leg for `self-drive` (where
  `brief.driving` reads not legal / unverified, the priced pair instead —
  phase-1-brief.md §Driving card step 4). A car-first
  segment the traveller has not decided is `mixed`, never defaulted to self-drive or to
  a tour (phase-0-intake.md) — so `mixed` means a self-drive option is on the table and
  `plan_lint.py` then requires `brief.driving`; public transport plus tours with no car
  is `public` or `group-tour`.
- `lodging` — free text: type + band (default mid-range hotel, refundable), read by
  Phase 5.
- `scenery` ⊂ `nature|city|beach|forest|lake|mountain` — Phase 2 scores the longlist
  against it.
- `pace` — anchors per day (2/3/4, default 3); `budget` — a band word or a number.
- `drivers` — present when a self-drive option exists: a list of `{"who",
  "licence_country"}` (ISO 3166 alpha-2 of the country that **issued** the licence, not
  the passport). `brief.driving` checks each one; a non-empty list makes `plan_lint.py`
  require that card.
- `languages` — present when a guided option may be priced: the language codes the
  party can follow spoken commentary in. Read where a tour is weighed against
  self-drive (phase-3-legs.md §Driving legs) and where any guided product is
  shortlisted (data-sources.md §Group tours).
- `must_see` — present when the traveller named must-sees: a list of `{"name",
  "tier"?}` — `name` as the anchor row's `what` will carry it, in `plan.lang`, without
  view words; `tier` ∈ eye-level · overlook · from-below (the sub-stop enum, one
  concept one name) only when the draw is a view. Phase 4 reads it (phase-4-days.md
  §City-agent contract), and `plan_lint.py` fails a tiered entry that no `must: true`
  sub-stop of that tier is named for (by its name / query, or by its row's `what`). A
  must-see the traveller drops, or a tier lowered after a written refusal, edits or
  removes the entry's `tier` and records the `decisions[]` row — the gate never
  relitigates a recorded decision.
- `notes` — every value that was **inferred rather than told**, in one string, so the
  assumptions block at checkpoint (a) can be written straight from this object; it
  names the locked must-sees and marks which tiers were assumed — the list itself is
  `must_see`.

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
   "decision_points": [
    {"t": "07:00", "what": "清水寺露台 or the indoor rain plan", "check": "rain radar + 清水寺官网公告",
     "if_no": "rain_alt", "by": "timed tickets refundable until 08:00 · ticket terms"}],
   "timeline": [
    {"t": "09:00-11:00", "what": "清水寺", "kind": "anchor", "price": "¥500",
     "hours": {"text": "最晚入场 17:30", "as_of": "2026-08-01", "src": "https://… the venue's own hours page"},
     "note": "开门即到避人流", "tag": "opener",
     "sub_stops": [
      {"name": "本堂舞台", "query": "Kiyomizu-dera Main Hall, Kyoto, Japan",
       "tier": "overlook", "stand": "舞台栏杆边,朝西看市区"},
      {"name": "奥之院", "query": "Okunoin, Kiyomizu-dera, Kyoto, Japan",
       "tier": "eye-level", "stand": "奥之院平台南端,回望整座舞台", "walk_min": 3,
       "must": true},
      {"name": "音羽瀑布", "query": "Otowa Waterfall, Kiyomizu-dera, Kyoto, Japan",
       "tier": "from-below", "stand": "瀑布前石阶下,仰看舞台木架", "walk_min": 4}]},
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
  city researcher verified. **No visa / entry / e-visa, health, advisory, hazard or
  insurance rows**: the assembler owns those facts (SKILL Phase 1) and overwrites any
  city-block claim about them (two Turkey city agents shipped an outdated "visa
  required" as item #1). The assembler merges these
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
- `sub_stops` (optional, on the `kind: anchor` row of one big sight) — the photo
  positions inside it, in walking order. Each needs `name` plus `query` or
  `lat`/`lon`; `name` and `stand` (where to stand, which way to face) follow
  `plan.lang`, `query` stays geocoder-friendly like `stops[].query`. `tier` =
  eye-level | overlook | from-below (English enum, like `tag`); `walk_min` = minutes
  on foot from the previous sub-stop (the first: from the drop-off); `must: true`
  marks the picture the traveller came for and requires a `tier`. Read
  phase-4-days.md §Per city step 2 before choosing them. **Never copy a sub-stop into
  `stops`**: stops drive geocode, check, the hop pairing, the KML route, `sun` and
  the day art, and one extra stop shifts every hop link after it.
- `tour: true` on a row (never on the day object — the lint fails a day-level `tour`)
  = a guided tour owns that block, so the operator decides which
  tier it reaches (data-sources.md §Group tours). Every `must: true` sub-stop on such
  a row carries `confirmed`: `in writing · <date> · <channel>`, or `pending · <the item
  text of the checklist row that asks it>` — that row is the one drafted message to
  the operator (data-sources.md §Group tours), and `plan_lint.py` fails a `pending`
  that names no checklist row — the two prefixes stay English, like the enums. A written
  refusal is not `in writing`: switch product, day or mode (data-sources.md §Group
  tours), or, when the traveller keeps the tour, drop `must` from that sub-stop, edit or
  remove that entry's `tier` in `prefs.must_see` with its `decisions[]` row
  (phase-0-intake.md §`prefs` and the assumptions block), and say in the row which tier
  the tour reaches.
- `link` on each sub-stop and the row's `sub_map` (one walking-mode chain through the
  sub-stops in order, when there are two or more) are script-owned: `links --write`
  builds them from `lat,lon`, else from `query` (no geocoding), and rewrites them on
  every run — never by hand (Korea aside, navigation.md step 0). Each of these keys
  is absent when unused, never `null`; `plan_lint.py` fails a wrong shape of
  `sub_stops`, `tour`, `must` or `tier` wherever they are present and a missing or
  unprefixed `confirmed` on a `tour: true` row's must-sees, and warns on a `link` or
  `sub_map` that is not an http(s) URL.
- `hours` (optional, on a timeline row — normally an anchor): what the venue's own
  page says for this date, `{"text": "09:00-17:00 · last entry 16:30", "as_of":
  "YYYY-MM-DD", "src": "https://…"}`, or the literal `"unverified"`, or `"open access"`
  for a street, beach, public viewpoint or tour-owned block that has no opening hours.
  Never a bare string of hours. Once it is written the row's `what` / `note` drop the
  hours they carried (no double print); the renderers print it under the row with its
  as-of and source. `plan_lint.py` fails any other shape, warns on `"unverified"` on an
  anchor and, under `--strict`, requires it on every anchor from `--asof` (default
  `meta.generated`) through +14 days with an `as_of` no older than that day − 14 and not after the as-of date —
  the T-3 row and every on-trip re-audit row re-run it with `--asof <that row's date>`
  (§Pre-departure re-check ladder, T-3; §On-trip re-audit rows).
- `decision_points` (optional, on the day): the go / no-go calls taken on the day or
  the evening before — `[{"t": "06:30", "what", "check", "if_no", "by", "src", "date"}]`.
  `t` HH:MM; `what`, `check` (words only — the camera or feed URL goes in `src`) and
  `if_no` required; `by` the terms that keep the fallback free; `date` optional (ISO),
  the day's date by default or the day before. A gate days ahead is a checklist row,
  not a decision point (scheduling.md rule 10), so `route_tools.py ics` never emits a
  gate twice: it writes one VEVENT per point at `date` + `t` (§Booking-artifact
  conventions); no two points on one day share a `what` (the UID is built from it).
  Absent, never null or empty; `plan_lint.py` fails the shape, a `t` that is not
  HH:MM, a missing `what` / `check` / `if_no`, a non-http(s) `src`, a `date` that is
  neither the day nor the day before, two points on one day with the same `what`,
  and a day date that is not YYYY-MM-DD.
- `stops[].driver` ∈ `self` | `hired` | `taxi` | `tour` (English enum, like `mode`),
  meaningful on a `mode: drive` stop: `self` = the traveller drives, `hired` = a car
  with driver or a pre-booked transfer, `taxi` = taxi or ride-hail, `tour` = the
  tour's vehicle. `driver: self` on every drive stop the traveller drives is what makes
  the plan a self-drive plan for `plan_lint.py` (phase-1-brief.md §Driving
  card lists the four conditions); the lint fails any other value and warns on
  `driver` off a drive stop and on a day that mixes `driver: self` with drive stops
  carrying none. `route_tools.py` leaves the field alone.
- `sun` is written by `route_tools.py sun --write` in the canonical shape
  `天亮 HH:MM · ☀ HH:MM / 🌇 HH:MM · TZ · sunrise-sunset.org` — for an `en` plan
  (`plan.lang`, or `sun --lang en`) the dawn word is `dawn`:
  `dawn HH:MM · ☀ HH:MM / 🌇 HH:MM · TZ · sunrise-sunset.org`; the renderers accept
  either spelling. Never hand-write it — `plan_lint --strict` fails any other shape;
  a day `sun --write` skipped is re-run with `--only DATE` once the day has a stop.
  Polar day / night (Tromsø in December, Nordkapp in June): `sun --write` refuses the
  day (exit 3, "polar day/night … remove this day's sun key") and writes nothing for
  it — the other days are still written; remove the `sun` key from that day yourself
  (the key is absent — not `null`, not `""`: absent is the schema's own shape for a day
  without sun — `assets/plan.example.json` day 2 has no `sun` key — and renderer
  copies older than 2026-09-05 crash on `null` or print a literal "None"), put the
  polar note in the day's `note`, and expect `--strict` to fail that day until the
  tool writes a polar shape (KNOWN-ISSUES PLN-11; phase-6-assemble.md names it as the
  one tolerated FAIL).
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
`themes/theme_common.STRINGS`. An `en` plan gets the `dawn …` form from `sun --write`
(see the `sun` bullet above).

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
   urgency: visa → travel-clinic consult → sell-outs → intl flights → date-locked
   rail → refundable hotels → the rest (the pre-departure ladder closes the pre-departure rows; on-trip re-audit rows follow it). Each row: item · deadline/lead time · price + as-of date · deep link ·
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
8. **Country brief**: cards in the canonical order of §Brief templates — visa ·
   emergency · safety · health · holidays · weather · money · connectivity ·
   insurance · baggage — then the triggered cards (season, altitude, navigation,
   lookalikes, packing, driving) only when the trip has the trigger.
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
- **A non-refundable booking is flagged, not described**: `"refundable": false` on its
  checklist row (and on a non-refundable fare's `legs[]` row — phase-3-legs.md §Record
  for every leg) is what triggers the independent review; the lint reads the flag,
  never the row's text.
- **Date-locked rows also ship as a calendar file** — always (the ladder rows are
  gates): every checklist gate (a ticket-release instant, a decision deadline, an
  on-trip re-check) and each day's `decision_points` go into the `.ics` beside the
  page (worked example: `examples/gates-sample.ics`)
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
  "delete the old events, then import the new file". A decision point's event follows
  the same rules with its own alarms (`-PT12H` — the evening-before read — and
  `-PT30M`), a 30-minute slot and a UID from the owning day and `what`, so re-timing it
  to the evening before keeps the UID (§city-block, `decision_points`).

### §Pre-departure re-check ladder — four fixed checklist rows, always with the .ics

Every plan's pre-departure rows end with the same four rows (a trip of seven days or
more continues with §On-trip re-audit rows), each naming what it re-checks
(the brief lines and the `legs` by number), so re-verification is one ladder instead
of five unrelated "re-confirm" lines. They are date-locked gates, so the ladder alone
makes the gates `.ics` mandatory (floating 09:00, rules above) — generated with
`python3 scripts/route_tools.py ics plan.geo.json -o gates.ics`, which reads each row's
ISO date or `T-N` marker; write deadlines as `T-14 · 2026-10-31` so both parse, with the
date = `days[0].date` − N (`plan_lint.py` checks it: WARN, FAIL under `--strict`; the
`.ics` trusts the date).

| row | re-checks | how |
|---|---|---|
| **T-14** | opening hours + fees of every anchor (pattern-verified ones first) · advisory level · visa / entry rule · ticket-release dates still ahead | the row lists the anchors and the `legs` numbers it covers |
| **T-7** | weather: re-run the forecast recipe (data-sources.md §Weather) for every base and re-apply scheduling.md rule 10 to hot / wet / windy days · the route's hazard sources (season card) | swap rain alternatives into the main line where the odds say so; note the swaps in `decisions[]` |
| **T-3** | strikes / closures / protests on the route (rail operator + city transit notices) · advisory and forecast once more · timed tickets in the wallet · the hours of every anchor up to T-3 + 14 re-read and written as `hours` | one line per moving day, then re-stamp `meta.generated` and run `python3 scripts/plan_lint.py plan.geo.json --strict --asof <this row's date>` |
| **T-1** | eSIM active (or set to activate on landing, where the carrier only activates in-country) and receiving home-number SMS · paper + cloud copies · cash in hand per `brief.money` · cards unblocked for travel | — |

A **hazard gate** (phase-1-brief.md §Hazard line) is a fifth, named row when the
window hits a hazard season: it carries the official source URL and the decision it
gates, and gets its own VEVENT beside the ladder's.

Write the rows as `{item, deadline: "T-14 · <date>", note: <what it covers>}`, keep
them as one block at the end of the pre-departure rows — on-trip re-audit rows, when
the trip has them, come after it (anything else due inside T-14 — eSIM, cash, card notice — is
folded into the matching ladder row, not kept as its own row; a ticket drop inside
T-14 stays its own gate and sorts by date ahead of the block), and do not add a
separate "re-confirm opening hours" row — the T-14 row is that row. `assets/plan.example.json` carries the four rows as
placeholders.

### §On-trip re-audit rows — trips of seven days or more

The ladder stops at T-1, but facts keep moving after departure: carriers change
check-in cutoffs and move check-in lobbies, timetables switch with the season,
operators restate their check-in lead, a storm or a smoke plume arrives
(data-sources.md §Flights, Carrier rules and clocks move after booking; §Hazard feeds).
A trip of seven days or more therefore adds one checklist row every 3-4 days of travel,
written `{item: "On-trip re-audit · D+3", deadline: "D+3 · <date>", note}` (the item
in the plan language — a zh plan: "途中复核 · D+3") —
`route_tools.py ics` reads the ISO date and derives each event's UID from `item`, so
the D+N in the item is what keeps the rows from merging into one calendar event. Each row re-audits **only
the days still ahead**, and its `note` names what it covers:

- every remaining flight — departure time, check-in and bag-drop cutoff, terminal or lobby;
- every timed check-in — the operator's lead time and the real duration of the activity
  (scheduling.md rule 1);
- every landing-to-activity chain (scheduling.md §Day types, Arrival day);
- every self-drive day — `brief.driving`, the desk's hours, the no-car fallback
  (phase-3-legs.md §Driving legs);
- every anchor up to this row's date + 14 — its `hours` re-read and written (then re-stamp
  `meta.generated` and run `python3 scripts/plan_lint.py plan.geo.json --strict --asof
  <this row's date>`), and
  the days' `decision_points` re-read;
- the route's hazard feeds, and for view-dependent days the live visibility and smoke
  checks (scheduling.md rule 10);
- every item the plan still marks `est`, ⚠️ or "confirm on arrival" — those are the
  re-audit's worklist.

A finding that changes a choice the traveller already made goes back to them as facts
and options (SKILL.md Interaction contract). On the road this is the *On-trip re-audit*
quick mode in SKILL.md. `plan_lint.py --strict` fails a plan of seven days or more
with no row whose item carries `D+N` and whose deadline carries the ISO date.

A **"Before leaving <country>" row** (zh: 「离开<国家>前」) is a conditional named row
like the hazard gate, on any trip length: it exists when the connectivity card's last
line says the traveller keeps the local number (§Brief templates, `brief.connectivity`),
its deadline is the day before the last departure from that country, it sits after the
on-trip rows, and its `note` lists what only works while still in the country (the
keep-alive plan, the Wi-Fi-calling prerequisite, a store / play account's region —
country-quick-notes.md for the country). `ics` is its generator like any dated row.
