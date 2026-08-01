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
