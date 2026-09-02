# Phase 3 — Flights & intercity legs (the procedure)

Read this at the start of Phase 3, before the first flight scan. SKILL.md Phase 3 is the
contract — inputs, outputs, and the gates that decide pass/fail; this file is the whole
procedure it points at: the plan shape, international flights (price sources, airports,
separate tickets, LCC arithmetic), intercity rail vs fly, driving legs, and what every
leg row records.

Inputs: the chosen route skeleton (Phase 2), `prefs.travel_style`, the Phase 1 visa /
entry facts (transit countries included). Outputs: `legs[]` rows — one pick + one backup
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
  the user, never by default. A rental is its own leg: pick-up/drop-off at airports,
  one-way drop fees noted, and the airport↔park drive budgeted honestly (Bozeman→Old
  Faithful ≈ 2.5 h, Fresno→Yosemite Valley ≈ 2.5 h — the map's "nearby airport" is
  half a day of driving).
- Record per driving leg: pick-up/drop point + counter hours, one-way drop fee,
  airport↔park drive time (budgeted honestly), car class, price +
  as-of date, insurance note, fuel estimate, park entrance fee (per **vehicle** in the
  US; 3+ parks → an annual pass wins — the $80 America the Beautiful is
  residents-only since 2026, non-residents take the $250 pass from the 2nd park,
  country notes §USA), and the license requirement for the driver's
  passport (see country notes).
- Gateway towns run out of cars and rooms in season — the rental and the first night
  go on the booking checklist, not the "later" pile.

## Record for every leg

**Record for every leg**: carrier, date, dep/arr local times, price + currency + as-of
date, **checked-bag fee** (US domestic: $35-45 per bag per one-way on every major
since Southwest ended free bags in 2025 — 4 legs is a real budget line; UA Basic
Economy is personal-item-only on domestic and short-haul Latin America routes,
while long-haul international Basic Economy does include the carry-on ⚡),
refund/change class, deep link. Multi-leg trips get a
**baggage walkthrough**: where the big bag physically is on every tour/venue day
(day tours = bag stays at hotel; stadiums ban bags; 2-day tours are often
overnight-bag-only). Output 1 pick + 1 backup per leg.

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
      checked-bag fee · refund / change class · deep link; one pick + one backup.
- [ ] Self-drive: the rental is its own leg with pick-up / drop-off, counter hours, car
      class, price + as-of, one-way drop fee, airport↔park drive time, insurance note,
      fuel, park fees, licence requirement; the
      rental and the first gateway night are on the checklist.
- [ ] Multi-leg trips carry the baggage walkthrough (where the big bag is on every tour
      / venue day).
