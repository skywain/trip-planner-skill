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

## Layering the playbook — the Phase 6 split and its probe A/B (2026-09-03)

SKILL.md had grown to 627 lines; the skill-authoring guideline is ~500, and the same rule
that keeps a memory index usable applies: the top level routes, the detail lives one level
down. Phase 6 (157 lines — assembly, self-check, delivery, themed renders) went first.

*What moved:* the procedure went **verbatim** into `references/phase-6-assemble.md` (H2s
plus an exit-criteria checklist); SKILL.md keeps a 30-line contract — inputs, outputs, the
gates that decide pass/fail — that opens with an imperative "Read
references/phase-6-assemble.md now". Red lines never fold into the reference file: a themed
page, never a plain one; the self-check runs in full; acceptance bars are exit codes and
eyes; `plan.geo.json` is the single source.

*How it was tested:* a probe A/B. Ten stateless agents — opus / sonnet × low / medium effort
and haiku × medium, each on the old tree and the new one — answered 16 Phase 6 questions
from the files alone, citing file:line; a grader marked PASS / PARTIAL / FAIL against an
answer key and classified every miss as MODEL_FAIL (text clear, model missed), SKILL_GAP
(text missing or buried) or ROUTE_MISS (answered without opening the reference file). Route
hits were counted from the agents' tool calls in their transcripts, not from self-reports.

*Result:* old tree 76.0 / 80, new tree 76.5 / 80; all five new-tree probes opened the
reference file, haiku included; 14 misses, all MODEL_FAIL. The stub's one-line acceptance
bar lifted Q6 (exit codes + "look at it") from 3.0 to 4.5, because the old tree kept those
two facts a hundred lines apart. One structural miss survived the first pass: on Q9
("besides the HTML, what is handed over?") sonnet dropped the chat summary 3 times in 6 on
the new tree and 0 in 6 on the old — a control run on the old tree proved the delta was
real. The cause was the stub's terse `Outputs: chat summary + html (+ kml; + ics)` line,
whose parenthesis read as the whole "besides" set. Naming the summary as deliverable (1)
with its required contents fixed it: 6 / 6 after the change.

*Rules that carry to the next phase:* the router line is an instruction, not a
description; a contract line that names an output must also say what it contains, or a
weak model reads the name as the whole thing; test a split with the same probe set on both
trees, and run a control before attributing any delta to the structure; count route hits
from tool calls. Next candidates by size: Phase 0 (97 lines), Phase 4 (92), Phase 3 (63).

## The unattended gap-fix program (2026-09-03)

The owner's brief was one sentence — check the skill for gaps in clothing / weather /
temperature, pests and disease, safety, and price comparison across domestic and foreign
sites — and the follow-up was "split the phases out, then probe A/B". Both ran as one
overnight program, gated at every step by the probe method above, and the whole of it is
one branch for review, never merged by the agent.

*Order and gates.* (1) Seven S-level audit items; (2) Phase 4 split; (3) Phase 1 split
carrying four new procedures (advisory line, emergency card, health line with the
yellow-fever audit, hazard line); (4) Phase 0 + Phase 3 splits; (5) a final wave. Each
step: an adversarial wording review (must-fix items applied verbatim), then a five-probe
matrix (opus / sonnet × low / medium effort, haiku × medium) answering scenario questions
from the files alone, graded PASS / PARTIAL / FAIL with every miss classified
MODEL_FAIL / SKILL_GAP / ROUTE_MISS; only SKILL_GAPs were fixed, and each fix was
retested on the combos that missed. Splits ran as A/B against a snapshot of the tree
taken the moment before; route hits were counted from the agents' tool calls.

| step | probe | score | FAIL | route hit | SKILL_GAP → fixed |
|---|---|---|---|---|---|
| S-level fixes | 10 q | 46 / 50 | 0 | — | 2 |
| Phase 4 split | A/B, 16 q | 74.5 → 72.0 / 80 | 0 | 5 / 5 | 1 |
| Phase 1 split + M-level | 10 q | 43 / 50 | 0 | 5 / 5 | 2 |
| Phase 0 + 3 splits | A/B, 16 q | 79.0 → 77.5 / 80 | 0 | 5 / 5, both files | 2 |
| Final wave A (P0 · P1 · templates) | 18 q | 82 / 90 | 0 | 5 / 5 | 2 |
| Final wave B (P3 · P4 · P6) | 18 q | 82 / 90 | 0 | 5 / 5, three files | 3 |

Every A/B delta was the same defect: a stub that restated a step and dropped a
qualifier ("per interest-fit", "silently" for the body's WARN, `lang` without "chrome
only", the optional-line defaults) — five probes take the majority wording. The rule
now: a contract line that restates the body keeps every qualifier verbatim.

*The end-to-end test that changed the tooling.* A fresh Haiku agent planned São Paulo →
Kenya, nine days, in Chinese, stock mode, and a Fable grader audited the artefacts.
The plan itself was mostly model failure (no `brief` at all, "awaiting qc.py" in
`meta.self_check`, a `## 总计` heading inside a budget cell, nine unfilled art
placeholders, English `decisions[]`), but three things were the skill's: `route_tools
check` and `themes/qc.py` both exited 0 on that plan — the required sections had no
machine gate; the yellow-fever audit named entry countries and transit airports but not
the departure country, so the tester audited by passport (China) instead of by origin
(Brazil, a WHO risk country) and wrote "no certificate needed"; and the gates `.ics`,
declared mandatory, was the one deliverable with no generator, so it was skipped. Fixes:
`scripts/plan_lint.py` (the content gate, `--strict` before any render; the seven examples
pass its default checks), `route_tools check` flags a declared transit / walk hop over
60 km (a Nairobi hotel had geocoded to Kisumu, 257 km, and `"mode": "transit"` had
silenced the flag), `route_tools ics` writes the calendar from the checklist rows, the
yellow-fever audit now starts from the departure country, `prefs.pictures` records how
the art was actually made, and the not-listed checklist asks about the headline seasonal
draw at skeleton time.

### Old main vs the PR head, seven model tiers (2026-09-05)

Every A/B above compared a split against the snapshot taken the moment before it, so
the question "is the whole PR better or worse than `main` for weak models?" had never
been asked directly. It was asked afterwards, as one run: two detached worktrees
(`main` at 624196a, the PR head at da061eb), the 36-question final-wave bank, and seven
model combinations — opus-5 and sonnet-5 at low and medium effort, haiku-4.5 at medium,
plus opus-4.6 and sonnet-4.6 at medium. Each combination answered the bank on both trees
(28 stateless probes); one Fable grader per combination and set graded the old and the
new sheet side by side, re-reading both trees (14 graders); every question on which any
combination scored the trees differently went to an adversarial attribution agent whose
default verdict was NOISE (12 agents; five single-combination deltas were skipped and are
listed as noise). Route hits were counted from the probes' tool calls, not their
self-reports: all 14 new-tree probes opened their phase files. The bank was split into
families first, because the old tree cannot be graded on content it never had: 18
**AB** questions (same facts on both trees, inline vs `references/phase-N-*.md`), 5
**MIXED** (the old tree has the core rule, graded on that part only) and 13 **NEW**
(2026-09 content; the old tree is scored for honesty only).

| combo | AB old → new (/18) | MIXED old → new (/5) | NEW new (/13) |
|---|---|---|---|
| opus-5 low | 17.5 → 18 | 5 → 5 | 10 |
| opus-5 medium | 17.5 → 18 | 4 → 5 | 12.5 |
| sonnet-5 low | 13.5 → 16.5 | 4 → 4 | 10 |
| sonnet-5 medium | 14.5 → 17 | 4 → 5 | 12 |
| haiku-4.5 medium | 12.5 → 15.5 | 3.5 → 3 | 12.5 |
| opus-4.6 medium | 14.5 → 16 | 4 → 4 | 12 |
| sonnet-4.6 medium | 14.5 → 16 | 4 → 4.5 | 12.5 |
| **seven combos** | **104.5 → 117 / 126** | **28.5 → 30.5 / 35** | **81.5 / 91** |

No combination scored the PR head below `main` on the shared questions, and the gap
widens as the model weakens. The noise floor matters for reading the table: the same
new tree, same questions and same combinations re-run two days after the 09-03 final
wave moved individual 18-question sheets by −3 to +4, so no single row above is
significant on its own; what carries the result is the sign (seven of seven, both sets)
and the attribution. Six of the twelve attributed deltas were textual and in the PR's
favour: the flight-pricing ladder (B2) lost its last rung on `main` for six of seven
combinations because the old text splits the ladder between Phase 3 and §When things
fail; the rental-leg record (B5), the city-agent prompt (B7) and the sell-out rule (B10)
moved facts that `main` kept in prose next to an enumeration into the enumeration
itself; the intake rules (A1) and the stock-mode limit (A3) are numbered and restated in
the gate on the PR head and buried in a long sentence on `main`. One delta went the other
way and was the question's fault, not the skill's: B15 asks "which two scripts must exit
0" and the PR head has three gates, so three combinations chose the two bold ones
(`plan_lint --strict`, `qc.py`) and dropped `route_tools check` — the bank was corrected,
the wording was not. Everything else (B3, B6, B9, B14, B16, A5 and the five skipped
rows) is identical text on both trees and reads as sampling noise. On the NEW family the
old tree's probes were asked, in effect, about rules that do not exist: six combinations
fabricated nothing across 13 × 6 answers (they cited the adjacent older text and said
the rest was not in the documents); haiku invented three.

The end-to-end control ran the same Haiku São Paulo → Kenya order on `main`, in a
worktree without `themes/.auth_header`. It came out PARTIAL (21 PASS / 13 FAIL / 8 N/A
against `main`'s own contract) and it changed one reading of the 09-03 run: on `main`
the same model wrote six `brief` cards, so "no `brief` at all" on the PR head looked like
the heavier Phase 1 specification pushing a weak model past the point where it drops
the whole section rather than a model failure. That reading did not survive its own
control. The 09-03 run had been made in the working checkout, where `.auth_header`
exists, so it was not the stock-mode run it was graded as; re-run on the PR head in a
clean worktree, Haiku wrote all nine cards in canonical order, put the yellow-fever +
ICVP row on the checklist (the audit hit, from the departure country), the travel-clinic
row second, three of the four ladder rows and a four-VEVENT gates `.ics`, and ran
`plan_lint --strict` itself, recording its six FAILs honestly (two `TBD` placeholders, a
`meta.self_check` still reading "pending", no T-1 row, no self-check `decisions[]` row).
The verdict on that reading: not reproduced. The missing `brief` was sampling variance,
and the fix already on this branch — `plan_lint` fails per card with "brief.X missing
(required)" — turns that kind of omission into a deterministic red (on the `main` plan it
reports 12 FAILs, on the re-run 6). What the re-run did show is the next defect class:
the gates exist and were run, and they do not block. `plan_lint --strict` had exited 6
and `route_tools check` had exited 2 (a real Wilson → Seronera flight with no `mode:
fly`) at delivery time; both renderers ran anyway, `qc.py` stayed green on a Chinese
plan whose 43 timeline rows and nine brief cards were all in English, `trip.kml` was
never written, and the tester reported "all phases complete". Against `main` the same
model did better on everything the PR added (nine cards with advisory / emergency /
health, the yellow-fever row, the ladder, the `.ics`, dated hotel labels, no "待计算"
in the page) and worse on the day plans (`sun` 9/9 → 5/9, `rain_alt` 4 → 1, meal rows
17 → 6, language 0/62 → 43/43 English rows) — the pattern of a weak model given more
to do, not of worse text: the seven-tier probe above finds the same rules more
reliably on the PR head, and the two end-to-end runs are one sample each. Six
actionable gaps came out of the pair and are logged as PLN-10 to PLN-12: renderers
that enforce the gates (with an escape hatch that watermarks the page), lint coverage
for language, source stamps, empty-stop days and the KML, the Phase 4 gate's mode
wording that contradicts `check`'s own hint, the `fast-flights` install line under
PEP 668, an origin → hub table (both trees put São Paulo at GIG), and the cover-title
fallback. Cost of the comparison: three workflows, 58 agents, about 6.5 M tokens.
