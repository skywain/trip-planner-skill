# Phase 4 — City day-plans (the procedure)

Read this at the start of Phase 4, before any city is planned or any city agent is
launched. SKILL.md Phase 4 is the contract — inputs, outputs, and the gates that decide
pass/fail; this file is the whole procedure it points at. When Phase 4 fans out, the
city-agent prompt is built from §City-agent contract below: paste those lines into the
prompt (or give the agent this file's absolute path — a subagent's working directory
is not the skill root), because the agent never sees SKILL.md.

Inputs: the chosen route skeleton (Phase 2), the legs table (Phase 3), the Phase 1
brief facts (visa / entry, holidays, health, advisory — the assembler's, never a city
agent's) and `prefs` (interests, pace, language). Outputs: per city, plan-JSON day
objects insertable verbatim into `days[]` (output-template.md §city-block) with
`stops`, the hour-level `timeline`, `hop_links`, `sun`, `rain_alt`, `ribbon`, plus the
city's `checklist_items`.


## City-agent contract — fan out or go sequential

When ≥3 cities and subagents are available, fan out one agent per city (otherwise do
the cities sequentially with the same structure); each prompt must include: the
dates, the user's interests + pace, **search budget ≤8**, an
explicit **"do not run geocoding"** line (parallel agents would break Nominatim's
1 req/s policy — the assembler geocodes once, centrally), **the plan language**
(`plan.lang`, with one line telling the agent every reader-facing string in its
returned block — `label`, `what`, `note`, `why`, hotel blurbs, checklist rows,
`unverified[]` — is written in that language; its sources will mostly be
English, and English notes pasted verbatim are how a zh plan goes half-English.
Machine fields keep the schema's form regardless: `stops[].query` stays
geocoder-friendly romanized/destination-local, and `kind`/`tag`/`verify` keep
the English enum words the renderers switch on),
and the exact return
format from references/output-template.md §city-block — **plan-JSON day objects,
insertable verbatim**, not a summary — and, as the prompt's own last line, the hard
rule: **city agents do not
make visa/entry judgements** — no visa rows in their `checklist_items`, no "you need
a visa" in notes. Visa/entry facts are the assembler's Phase 1 job and override
anything a city block says (Turkey test: both city agents put an outdated "visa
required" as checklist item #1; entry had been visa-free since 2026-01-02). The same
holds for health, advisory, hazard and insurance lines — Phase 1 facts, assembler-only.
When the user prefers group tours, the city agent's first job is
finding real in-sale products with departure schedules (data-sources.md §Group
tours) — the tour's schedule then dictates the surrounding legs, and a fly-in day
tour must clear BOTH weekday grids (operator departure days AND feeder-flight
schedules — same section) before its day is fixed in the skeleton.

## Per city — the six steps

Per city:
1. Anchors per interest-fit, ≤ pace + 1 optional per day. Cluster by geography per day;
   order clusters so the route never criss-crosses town.
2. **Verify every anchor**: open days + hours, last-entry time, price, and sell-out
   pressure (official site beats blogs; treat blog data >12 months old as stale).
   **Any anchor that sells out goes on the booking checklist with its lead time**
   (Ghibli, teamLab, Uffizi, Alhambra,
   Sagrada Família… see country-quick-notes.md). For dates more than ~3 months out
   nobody publishes that day's hours yet, so verify the **seasonal pattern + closure
   rule**, stamp it "pattern as of {date}", and let the **T-14 row of the pre-departure
   re-check ladder** (output-template.md §Pre-departure re-check ladder) carry the
   re-confirmation. Claiming date-specific verification you cannot have is
   worse than admitting the horizon — and prices move on their own schedule
   (admission fees jump at fiscal-year boundaries), so re-check the fee, not just
   the hours. National parks and other big nature anchors: also read the park's
   official Alerts/Current Conditions page — storm, fire and eruption closures
   outlast news cycles, and a partially-open park may hold 2-3 hours of content
   where the brochure promises a day (resize the day; design it droppable while
   the region is in disaster recovery). When the draw is a natural phenomenon
   (lava fountains, aurora), plan the day to work WITHOUT it: base rate ≈ event
   duration ÷ recurrence interval, the official forecast horizon (days, not
   weeks) sets a decision gate on the checklist — keep every related booking
   cancellable until that gate, and pay no premium for a lottery ticket.
3. Transit: day-pass vs pay-per-ride arithmetic — sum the day's expected rides and
   recommend the pass only when it actually wins. Note the local IC card / transit app.
4. Each day gets one rain alternative and a food **area** (market/street/neighborhood)
   near the evening cluster — named restaurants only on request; they churn too fast.
5. Timing realism: transit between clusters from Google Maps (browser) or mark the
   estimate unverified; hard stop = last entry, and nothing scheduled after it.
6. **Timeline assembly — hour-level is the default deliverable.** Read
   references/scheduling.md (dwell times, tiered ticket margins, buffer policy,
   arrival/moving/departure day structures, worship + siesta + crowd-calendar traps,
   degradation tags) and references/navigation.md (hop links, canonical hop-row
   format, exit numbers, verify-vs-estimate rules), then run scripts/route_tools.py
   in this order: **geocode → per-day tz sweep → sun --write → links --write →
   check → kml**, so every hop carries a distance-sane duration and a tappable map
   link written into the plan for you. **`check` must exit 0 before rendering** —
   a BROKEN hop is a stop with no lat/lon (geocode it, or hand-fill: navigation.md
   §2), a SUSPICIOUS hop is an undeclared hop over 12 km, or a declared walk / transit
   hop over 60 km. It has two fixes and no third. A vehicle really runs the hop (fly /
   drive / boat / train / bus) → declare that `mode` on the arriving stop and give it
   its `legs[]` row (add the row if the leg has none) — an undeclared real flight is a
   defect too (a tester shipped exit 2 on Wilson → Seronera rather than write
   `mode: fly`). Nothing runs it (a 250 km hop inside one city is a mis-geocoded stop)
   → fix the stop (read `geocache.json`'s `display_name`, re-query or hand-fill), never
   the `mode` (a tester silenced a hotel geocoded to Kisumu with `mode: transit`). And
   never explain the flag away in prose (a tester shipped exit-2 output rationalised as
   "expected for a multi-city trip" — every flagged hop was a real defect).
   `sun --write` runs once the stops carry coordinates: it fills every day's
   `sun` (civil dawn · sunrise / sunset) in one canonical string and refuses data
   that fails a solar sanity check — never hand-copy sunrise numbers, and **run it
   before writing any sunrise / golden-hour / dark-start prose**: tz changes live in
   tzdata, not in your head (Morocco moves to UTC+0 on 2026-09-20 — the tester's
   hand-written times were an hour off on all ten days, and neither `check` nor
   `qc.py` compares prose against `sun`). A moving day defaults to the last stop;
   when the day's sunrise anchor is at the *first* stop, set the day's `sun_stop`
   (scheduling.md rule 7). **A plan that crosses timezones stamps every day's `tz`
   (IANA name) before `sun --write`** — sun refuses any day whose zone it would
   have to guess from longitude (the guess puts Hawaii at UTC-11), and it refuses
   per-day, so one sweep over `days[].tz` beats fifteen retries.
   **`sun`: non-zero exit = at least one day was skipped or rejected** — the written
   days are fine, re-run `--only DATE` for the ones it names before writing prose
   for them. The one exception: a day `sun` REJECTS as "polar day/night" (Tromsø in
   December, Nordkapp in June) is never re-run into green — remove that day's `sun`
   key (absent — not `null`, not `""`: the schema's own shape for a day without sun;
   renderer copies older than 2026-09-05 crash on `null`), put the polar note in the
   day's `note`, and carry it to Phase 6 as the one
   tolerated `plan_lint --strict` FAIL (output-template.md §`sun`; KNOWN-ISSUES
   PLN-11). Mark ridden
   hops with a `mode` on the arriving stop (`transit`/`train`/`bus`/`drive`/`boat`/
   `fly`; long signature walks `walk`), or the walking total and the links will
   both be wrong — `check` says (guessed) next to anything you left it to infer.
   Transit durations come back as ranges — keep them ranges unless you
   browser-verified the hop. Deliver day-level granularity only if the user asks for
   a rough cut. Each finished day also gets its `ribbon` one-liner (Stop1 →walk 12′→
   Stop2 →metro 9′→ …, output-template.md §5) — no script writes it; seven blank
   ribbons is the usual way to find out you forgot.

## Exit criteria — tick every line before Phase 5

- [ ] Every city block came back as plan-JSON day objects in `plan.lang`, with machine
      fields in schema form; no visa / entry / health / advisory / hazard / insurance
      rows in any
      `checklist_items` or note (assembler-only facts).
- [ ] Anchors per interest-fit, ≤ pace + 1 optional per day, clustered so the route
      never criss-crosses;
      every anchor verified (hours, last entry, price, sell-out — sell-out anchors on the
      booking checklist with lead time) or stamped "pattern as
      of {date}" with the T-14 ladder row carrying the re-confirmation.
- [ ] Each day has its rain alternative (closure-checked), its food area, its `ribbon`.
- [ ] `route_tools.py` ran geocode → tz sweep → sun --write → links --write → check →
      kml; `check` exited 0 (no BROKEN / SUSPICIOUS hop survived; every `mode`
      written to clear a flag names a vehicle that really runs the hop — fly / drive /
      boat / train / bus — and that leg has its `legs[]` row; none added to silence a
      flag); `sun` exited 0 or every named day was re-run with `--only DATE` — except
      a polar day it REJECTED, whose `sun` key stays absent (never `null`, never `""`)
      and is named in the summary (PLN-11).
- [ ] No sunrise / sunset / dark-start prose was written before `sun --write`; every
      ridden hop carries its `mode` on the arriving stop; unverified transit durations
      stay ranges.
