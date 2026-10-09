# Phase 3 — Flights & intercity legs (the procedure)

Read this at the start of Phase 3, before the first flight scan. SKILL.md Phase 3 is the
contract — inputs, outputs, and the gates that decide pass/fail; this file is the whole
procedure it points at: the plan shape, international flights (price sources, airports,
separate tickets, LCC arithmetic), intercity rail vs fly, driving legs, and what every
leg row records.

Inputs: the chosen route skeleton (Phase 2), `prefs.travel_style`, the Phase 1 visa /
entry facts (transit countries included) and, for a car-first segment,
`prefs.languages` and `brief.driving`. Outputs: `legs[]` rows — one pick + one backup
per leg — the checklist rows for flights, date-locked rail and rentals, the budget rows
they imply, and the baggage walkthrough for multi-leg trips.

## Write to the plan shape

From here on you are writing `plan.geo.json`. **`assets/plan.example.json` is the single
source of truth for the plan's top-level shape** — `legs`, `checklist`, `budget`,
`hotels`, `brief`, `days[]`… — so open it (or output-template.md §Top-level plan
skeleton, copied from it) before writing a field. `budget` is a list of
`{cat, per_person, total, note}` rows, not `{note, rows}`; `legs` rows use
`from/to/dep/arr`. A wrong shape does not fail loudly: the renderers WARN and print an
empty section (they used to crash — the Vietnam test lost both themed pages to it).

## International

**International:**
- Run `scripts/flight_scan.py` (Google Flights data, keyless; `--help` for usage) to
  grid-scan the date window and both open-jaw directions. Fails twice → browser on
  Google Flights (URL recipes in data-sources.md); that blocked too → the second
  price source (Skyscanner / Kayak; on CN networks Trip.com/携程 is the primary and
  Google the backup); "price unverified" only when every source fails — §When
  things fail. **Every international pick and backup
  is priced in ≥ 2 sources** (Google + Skyscanner / Kayak / Trip.com / the carrier's
  site — data-sources.md §Flights → Second price source); `legs.note` names them
  with the as-of date, a > 10 % disagreement prints as a band. No browser pane →
  Google alone, and `legs.note` says "single source — no browser".
- Multi-airport cities: compare fare + ground transfer cost + time (HND vs NRT,
  LHR vs LGW/STN…). A ¥400-cheaper fare into a far airport often loses.
- Departing CN: also spot-check one LCC directly in the browser (Spring 春秋, Peach,
  Scoot…) — aggregators miss or misprice some LCC inventory.
- **Separate tickets across an international connection are a visa trap, not just
  a baggage nuisance** — audit whenever two PNRs meet at a foreign hub, including
  tickets the user bought before coming to you. Separate-journey policies tag bags
  only to the first ticket's endpoint, and carousels sit landside — so claiming +
  re-checking can REQUIRE entering the transit country. Before writing "no visa
  needed", check: the first carrier's separate-PNR interline stance (assume no
  through-check), the passport's transit-country visa need, and airside overnight
  options if the layover crosses a night. A needed transit visa goes on the
  checklist with its deadline counted back from the departure date.
- LCC arithmetic: add the checked-bag fee before comparing — a "cheap" fare + ¥280 bag
  usually isn't.

## Intercity within the destination

**Intercity within the destination:**
- Mode rule: rail wins under ~5 h station-to-station (city-center to city-center, no
  airport buffers); fly beyond that or across water; overnight options only for
  shoestring budgets.
- Price on the **operator's** site — resellers add fees. Country-quick-notes.md lists
  the operators and their booking-window rules (high-speed fares rise as buckets sell).

## Driving legs

**Driving legs (parks and car-first destinations):**
- A national park without a car is a bus-tour compromise — decide that explicitly with
  the user, never by default. The user sees it at checkpoint (a) as a pair priced
  all-in for the same days: **self-drive** (base + taxes + collision waiver /
  liability + fuel + one-way fee + park entry) against **the tour** (fare + nights the
  traveller books themselves + surcharges + tips — data-sources.md §Group tours, Price
  anatomy). Each side shows what it actually reaches (viewpoint tiers,
  phase-4-days.md step 2); the tour side shows its commentary language against
  `prefs.languages` (data-sources.md §Group tours, Structure quirks to check); the
  self-drive side shows the two licence columns from
  `brief.driving` (phase-1-brief.md §Driving card), legality first. The own-language
  consensus line (phase-1-brief.md §Where the facts come from) sits beside the pair.
  A rental is its own leg, its `type` saying so ("car rental" / 租车 — a self-drive
  trigger, phase-1-brief.md §Driving card): pick-up/drop-off at airports, one-way drop
  fees noted, and the airport↔park drive budgeted honestly (Las Vegas→Grand Canyon
  South Rim ≈ 4.5 h, Salt Lake City→Moab ≈ 3.5-4 h — the map's "nearby airport" is
  half a day of driving).
- Record per driving leg: pick-up/drop point + counter hours, one-way drop fee,
  airport↔park drive time (budgeted honestly), car class (and whether it has CarPlay /
  Android Auto — navigation.md §Self-drive days), price +
  as-of date, insurance note, fuel estimate, park entrance fee (per **vehicle** in the
  US; 3+ parks → an annual pass wins — the $80 America the Beautiful is
  residents-only since 2026, non-residents take the $250 pass from the 2nd park,
  country notes §USA), and the licence's legal status and the desk's terms from
  `brief.driving`. **Rental tactics** go in the same record: price the class on the
  brand's site for the traveller's home market too ⚡ (country sites often bundle the
  waiver and liability for less than the destination rate plus counter add-ons); pay
  at the counter, not prepaid, while the drive decision is open; book the return a
  little late — the slack is free where early returns cost nothing (read the terms);
  skip prepaid fuel, toll packs where the route has no toll roads, and accident cover
  the traveller's insurance already gives; take the class locals actually rent on that
  terrain instead of assuming a compact. Price surfaces and what an inclusive rate
  must contain: data-sources.md §Car rental.
- **Every self-drive day carries a no-car fallback, worked out before anything is
  cancelled**: the bus or park shuttle, taxi and walking chain that still reaches the
  day's main anchor, with timetable (weekday grid included) and price — for a refused
  licence at the counter, a missing car, or a driver unfit to drive. When the drive
  goes ahead, a free-cancellation booking held against it (data-sources.md §Group
  tours, Reserve-now-pay-later) does not wait for its cutoff if no new information
  will arrive before it (the counter's answer comes only at pick-up): release it at a
  calm moment once the fallback is walked on the map, not at the last one.
- Gateway towns run out of cars and rooms in season — the rental and the first night
  go on the booking checklist, not the "later" pile.

## Record for every leg

**Record for every leg**: carrier, date, dep/arr local times, price + currency + as-of
date, **checked-bag fee** (US domestic: $35-45 per bag per one-way on every major
since Southwest ended free bags in 2025 — 4 legs is a real budget line; UA Basic
Economy is personal-item-only on domestic and short-haul Latin America routes,
while long-haul international Basic Economy does include the carry-on ⚡),
refund/change class, deep link. A non-refundable fare sets `"refundable": false` on
its legs row (shape: output-template.md §Top-level plan skeleton; it triggers the
independent review — phase-6-assemble.md §Independent review). Once booked,
`legs.note` says which reference does what: the carrier's **record locator** (usually
6 characters, on the e-ticket receipt) is what the carrier's app and check-in want —
an OTA's order number is not — and the 13-digit e-ticket number finds the receipt
after the trip; the codes themselves stay out of the rendered page. Multi-leg trips
get a
**baggage walkthrough**: where the big bag physically is on every tour/venue day
(day tours = bag stays at hotel; stadiums ban bags; 2-day tours are often
overnight-bag-only). Output 1 pick + 1 backup per leg. **A backup counts only if it
still reaches the leg's pinned dependency** (tour pickup, event, onward flight); when
none does, the leg is **must-catch** — `legs.note` says "no usable backup" and the plan
buys margin instead (arrive the day before, or take the earliest departure). The ground
run to a dawn must-catch goes by pre-booked car, with rail as the backup: early weekend
trains are the thinnest (live case: a Sunday-dawn commuter train cancelled outright, on
a non-refundable ticket).

## Exit criteria — tick every line before Phase 4

- [ ] `legs`, `budget`, `checklist` follow `assets/plan.example.json` shapes (budget is
      a list of rows; legs use from / to / dep / arr).
- [ ] Every international pick and backup is priced in ≥ 2 sources, `legs.note` names
      them with the as-of date (or says "single source — no browser"), a > 10 %
      disagreement prints as a band.
- [ ] The separate-tickets audit ran for every foreign hub where two PNRs meet — before
      "no visa needed" was written anywhere; a needed transit visa is on the checklist
      with its deadline.
- [ ] Every leg row: carrier · date · dep / arr local · price + currency + as-of ·
      checked-bag fee · refund / change class · deep link; a non-refundable fare
      carries `"refundable": false`; one pick + one backup that
      still reaches the pinned dependency (or "no usable backup" on a must-catch leg).
- [ ] A car-first segment went to the user as the all-in pair (self-drive vs tour,
      what each reaches, commentary language, licence legality) — decided with the
      user, never by default; headless, the days run on the legal option and the
      assumptions block shows both columns (phase-1-brief.md §Driving card step 4).
- [ ] Self-drive: the rental is its own leg with pick-up / drop-off, counter hours, car
      class, price + as-of, one-way drop fee, airport↔park drive time, insurance note,
      fuel, park fees, licence status from `brief.driving`; every self-drive day has
      its no-car fallback (timetable + price); the
      rental and the first gateway night are on the checklist.
- [ ] Multi-leg trips carry the baggage walkthrough (where the big bag is on every tour
      / venue day).
