# How this skill was hardened

Every rule in `references/` exists because something broke. This is the record of what
broke, so the rules do not get "simplified" back out later.

The skill was reviewed in three rounds by seven independent agents, each given a
different job and no knowledge of the others' findings: a script torture-tester, an
external fact-checker, a veteran-tour-leader realism attacker, a cross-file coherence
reviewer, and two fresh agents told to *actually build a day plan* from the skill and
report every place the instructions fought them. All script claims below were verified
by running the scripts, not by reading them.

## The most valuable single technique

**Make a fresh agent use the skill for real, and treat its confusion as the primary
deliverable.** The two end-to-end runs (Kyoto on a Monday, Rome on a Sunday) produced
28 friction points between them — including three defects that every static review had
missed, because they only appear when someone tries to follow the instructions in
order with a real deadline.

## What the reviews caught

### Examples get copied, so a wrong example is a bug

The illustrative day in `scheduling.md` violated the chain-arithmetic rule printed
twenty lines above it — zero minutes allotted for a 1.2 km walk — and named the wrong
subway line while stamping the row `(verified)`. Both canonical examples also offered a
rain alternative (Kyoto National Museum) that is closed on the very Monday the example
is set on: the model answer contained the exact bug the self-check exists to catch.

*Fix:* the example day is now one an end-to-end agent actually verified, it passes the
whole verification list, and the file says so explicitly.

### National holiday feeds miss the closures that ruin days

Local festivals close streets and triple hotel rates while every holiday API reports an
ordinary day. So do seasonal operating windows (cable cars, mountain huts, gardens),
per-venue annual maintenance, and Ramadan. The Rome run found that 2026-10-04 was
simultaneously Italy's free-museum Sunday — the busiest day of the month — and a
reinstated national holiday.

*Fix:* a budgeted festival search per city, and a closure scan that covers all of it.

### A timed ticket buys a place in the security line, not entry

A flat 15-minute early-arrival margin is badly undersized at exactly the venues where
pinned tickets matter: Vatican, Eiffel, Sagrada Família, Forbidden City, teamLab all
run 30-45 minutes from joining the queue to standing inside.

*Fix:* tiered margins, plus a rule against ever planning a door purchase at a flagship.

### A base-change day is a luggage problem, not a buffer problem

Checkout is 10:00, check-in is 15:00, and the whole middle of the day is spent carrying
bags. Large station lockers sell out by mid-morning; Japanese takkyubin forwarding is
next-day and must be arranged the evening before.

*Fix:* moving days are their own day type, capped at one anchor, with the bag solution
required in writing before anything is scheduled.

### Distance alone cannot tell walking from riding

`check` counted a 1.4 km metro ride as walking — under its walk threshold — and `links`
emitted walking directions for it, so a traveller tapping the link would have got
twenty minutes of walking instructions for a two-stop ride.

*Fix:* an optional `"mode": "walk"|"transit"` on each stop drives both the walking
total and the link's travel mode, and `check` reports on-foot and ridden separately.

### Hand-transcribing URLs is where plans silently break

The Rome run's most tedious and highest-risk step was pasting seven 180-character
Google Maps URLs into the plan by hand; one mis-paste puts the wrong directions on a
stop and nothing catches it.

*Fix:* `route_tools.py links --write` injects each URL into the matching hop row.

### Verifying a date you cannot verify

Nobody publishes a specific day's opening hours fourteen months out. The honest answer
is the seasonal pattern plus the closure rule, stamped with a date — and a re-confirm
task on the checklist. (Admission fees move on their own schedule: one run wrote ¥500
for a temple whose fee had risen to ¥1,000, from memory, in a skill whose first rule
forbids exactly that.)

### Script defects that only a hostile tester finds

- Every `read_text`/`write_text` omitted `encoding=` — under `LC_ALL=C` the script's own
  CJK example failed to read, and the KML writer crashed while its XML prolog claimed
  UTF-8.
- `geocode` silently overwrote hand-entered coordinates — the very coordinates its own
  error message tells you to add.
- The flight scanner's grid truncation dropped the departure date the user actually
  asked about, keeping only the edges of the date range.
- A negative geocode result was cached forever, making the documented retry impossible,
  when the real fix is almost always re-querying with the local-language name.

### Cross-file drift is the failure mode of a multi-file skill

A tag added to one file (`[opener]`, for a crowd-window anchor that is movable but
expensive to move) existed in the rules and the renderer but was missing from all four
places that *define* the tag vocabulary — including the hand-off format that parallel
city researchers are told to return verbatim. They would never have emitted it.

*Fix:* one canonical plan JSON consumed by every script, and a coherence pass whose
only job is to hunt for exactly this.

## Externally fact-checked claims

| Claim | Verdict |
|---|---|
| Google Maps `api=1` dir links cap waypoints at 9 | confirmed — **and only 3 on mobile browsers** |
| Waypoints are ignored in `travelmode=transit` | confirmed |
| Organic Maps imports KML as bookmarks | confirmed |
| Nominatim requires ≤1 req/s and an identifying User-Agent | confirmed |
| Naver Map web search path | **refuted** — `/v5/` is legacy, current is `/p/search/` |
| sunrise-sunset.org is free | confirmed, but **requires visible attribution** and rate-limits with 429 |

## End-to-end friction testing (August 2026)

Reviews check the rules; friction tests check whether a stranger can *follow* them.
The method, run nine times so far:

1. A **fresh agent session that has never seen the skill** is asked to plan a trip and
   render two themes, using **only the shipped documents** — it may not edit code or
   docs, has a search budget (≤25 web searches, ≤10 Nominatim calls, one flight scan), a
   picture budget (≤$0.60–0.70 via `themes/gen.py`), and must return a friction report:
   what it could not find, what it had to guess, where the docs and the code disagreed,
   ranked by severity.
2. Each run deliberately changes **origin × destination × language** so no two runs share
   a country or a departure city, and Chinese and English pages are both exercised:
   Beijing→Australia (zh) · Beijing→Norway (zh) · London→Japan (en) · New York→China (en)
   · Singapore→Italy (zh, with the video theme) · Berlin→Mexico (en) · Toronto→Morocco (en,
   with the video theme) · Shanghai→Turkey (zh) · Shenzhen→Vietnam (zh). Every theme has
   now been rendered by at least two testers, in both languages.
3. Every friction item is fixed in the code or the docs *before the next batch*, and the
   trip's generated pictures are recycled into `themes/assets/` (indexed in
   `themes/assets/IMAGE-LIBRARY.md`) so the library grows with each destination.

What the batches found, in short: the first two exposed rendering and contract gaps
(hop/stop pairing, sunrise data sanity, art.json field roles, CJK-vs-Latin typography);
the third exposed **data-layer** gaps — an FX source that silently drops minor currencies,
a holiday source without religious holidays, a timezone change that shifted a whole day
by an hour, city sub-agents asserting stale visa rules, and an undocumented top-level plan
shape that crashed two renderers. All are closed; the residual list is
[`docs/KNOWN-ISSUES.md`](KNOWN-ISSUES.md). Seven of the nine trips ship as
[`examples/`](../examples/), each byte-reproducible from its `plan.geo.json` + `art.json`.

## What the owner's own read-through changed (2026-08-17)

Nine friction runs by fresh agents still missed two things, because every tester was
handed a destination, a departure city **and** a picture budget. A real user hands over
neither. Both rules below are now canonical in `SKILL.md` (Phase 0, Phase 6) and mirrored
in `references/output-template.md`, `references/themes.md`, `themes/ART-SCHEMA.md` and
`themes/README.md` — this is the record of why, so they do not get simplified back out.

### The skill opened by planning, not by asking

Every test prompt already carried origin, destination and dates, so the intake gap never
showed: asked "plan me a trip", the skill would invent an origin, a pace and a page style
in silence, and the user found out only at delivery. Asking about all of it is the other
failure — a round trip of questions for facts that were already in the request
("帮我安排今年 10.1 到 10.7 的德国之旅" needs zero questions).

*Fix:* Phase 0 is **one message or none** — ask only for a core fact that is missing *and*
not inferable, everything in a single message, optional lines marked "(skip = default)",
and write what was learned or assumed into the plan's top-level `prefs` block so Phases
2-6 and any later replan read one place instead of re-asking. Anything inferred is stated
in the assumptions block at checkpoint (a), where it costs one line to correct.

### "No key" silently downgraded the deliverable to a plain text page

The picture pipeline had exactly two states — generate, or don't — so a session without a
native image generator and without an OpenRouter key fell through to the plain
`render_plan.py` page. That is the same trip data in the least interesting form the repo
can produce, and nothing told the user *why* their page looked nothing like the showcase.

*Fix:* a **picture-capability check** at Phase 0 (native tool → `themes/.auth_header` →
neither) recorded as `prefs.pictures`, and a third state that still ships a themed page:
the built-in stock kit (`themes/assets/stock/` + `themes/stock_art.py`) fills the picture
slots, the agent writes the words, and one notice — in the chat summary and the page's fine
print — says the pictures are stock because no generator or key was available. The plain
page is now explicitly an extra: printable on request, or the last resort after one honest
fix attempt at the theme renderer.

**Not yet tested end-to-end:** a friction run with **no picture budget at all**, which is
the configuration stock mode exists for. Every run so far had a key. Stock coverage is
also uneven by design today — complete for illustrated, working for clay, six themes still
need generated pictures (KNOWN-ISSUES AST-7 / AST-8).
