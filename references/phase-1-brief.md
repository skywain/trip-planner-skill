# Phase 1 — Country brief (the procedure)

Read this at the start of Phase 1, before any fact about the destination is written.
SKILL.md Phase 1 is the contract — inputs, outputs, and the gates that decide pass/fail;
this file is the whole procedure it points at. Every line here ends up in a `brief`
card (output-template.md §Brief templates, canonical order) or a checklist row, and
every line carries its source and as-of date.

Inputs: destination(s) and dates, the traveller's passport and origin (`prefs`,
`meta.party`), the route skeleton candidates. Outputs: the `brief` cards — visa ·
emergency · safety · health · holidays · weather · money · connectivity · insurance
(+ season when triggered — inserted after `baggage`, output-template.md §Brief templates
order) — the Phase 1 checklist rows (visa lead time, travel-clinic consult, yellow-fever
vaccine + ICVP, insurance, hazard gate, copies + registration), and
the facts every later phase inherits and no city agent may overrule.

## Where the facts come from

Read the destination's section of references/country-quick-notes.md first. **Destination
not in that file (Mexico, Morocco, Turkey and Vietnam all weren't)** → work through its
"Destination not listed? — the checklist" section instead of improvising: it is the
list of things every new country costs a first planner 6-9 searches to rediscover.

## The fact lines (visa · holidays · events · weather · money · insurance · safety)

- **Visa/entry** for that passport: official government/embassy sources only; put the
  processing lead time on the booking checklist. Rules change — never answer from memory.
  Transit countries count too: a separate-ticket connection can force ENTERING the hub
  country to re-check bags (Phase 3 §International, the separate-tickets bullet) — run
  that audit here, before writing "no visa needed" anywhere.
  **This judgement is the assembler's alone**: city subagents (Phase 4) do not make
  visa/entry calls, and anything they say about it is overwritten by this line.
- **Holidays colliding with the window**:
  `curl -s "https://date.nager.at/api/v3/PublicHolidays/{year}/{ISO2}"` (keyless ✓).
  A national holiday means closures + crowds + hotel spikes — annotate affected days.
- **What the holiday API can't see** — one budgeted search per city
  (`{city} festival OR events {month} {year}`) plus, where relevant: seasonal
  operating windows for mountain/garden/boat anchors, per-venue annual maintenance
  shutdowns of headliners, and Ramadan dates in Muslim-majority destinations (daytime
  food logistics, shifted hours, packed evenings). A local festival closes streets and
  triples hotel rates while every holiday feed says the day is ordinary.
- **User-named events get verified before anything else is planned.** A match,
  concert or festival in the request is the hardest pin in the whole trip — confirm
  team/venue/city, date, local kickoff time and ticket on-sale status FIRST, because
  the skeleton hangs off it ("Columbus vs Miami" is a home game in Ohio, and a route
  built around the wrong coast is a 13-day bug). US listings put the home side first
  in "A vs B" — but verify, never parse. Kickoff times can move for TV ⚡: re-check
  close to travel.
- **Weather for those dates**: Open-Meteo recipes in data-sources.md (first call can
  take ~10 s). One line: temps, rain odds, daylight — stamped with its mode
  (forecast / 5-yr normals + climate model) and as-of date per data-sources.md
  §Weather; the Phase 6 exit criteria check the stamp.
- **Money & connectivity — fixed lines, not a vibe.** `brief.money` carries the five
  lines of output-template.md §Brief templates (refuse DCC · card FX fee → buffer ·
  ATM rule · cash number · which cards and wallets work) plus the **origin-conditional
  block** when it applies (mainland-China origin: UnionPay vs Visa/MC acceptance,
  Alipay+/WeChat coverage, foreign-cash pre-order); `brief.connectivity` carries the
  eSIM ballpark, plug type and the digital-safety line (home-number SMS 2FA reachable
  abroad, phone-theft plan, cloud + offline copies of passport / visa / policy).
  Recipes and thresholds: data-sources.md §FX → Money safety.
- **Insurance line**: travel-medical insurance with destination-appropriate coverage
  goes on the checklist (US target: ≥$100k medical + medical evacuation — an ER visit
  is four figures before insurance). Tours never substitute for it. When the plan
  carries a monitored hazard gate, the insurance row's deadline is NOW, not "before
  departure" (the user buys — Hard rule 1); the agent's jobs are the read-side ones:
  verify the issued policy rather than the product page, and match the plan's
  activities against the exclusion list by name — data-sources.md §Travel insurance.
  The local half of the operating card (emergency numbers, the ER per base, the
  assistance line) lives in `brief.emergency` — §Emergency card below.
- **Advisory line, emergency card, health line, hazard line** — four procedures of
  their own below (§Advisory line, §Emergency card, §Health line, §Hazard line). All
  four draw only on official pages (the traveller's foreign-ministry advisory, CDC /
  TravelHealthPro, WHO, the insurer's schedule) — never from memory; a fact the fetched
  page does not carry → "n/a — see advisory" + that page's URL and as-of in the card,
  not silence — and never before the page was actually read.
- **Safety, written to the `brief.safety` template** (output-template.md §Brief
  templates — six named lines: the destination's named scams · pickpocket hotspots ·
  the taxi rule · the after-dark avoid list per base · what to do when it happens ·
  legal & customs red lines). More useful than warnings: design the plan so night
  movement is door-to-door by car — a route that never needs a dark walk beats a
  list of cautions. Sources: country-quick-notes.md (the destination's section, or
  the "Street safety" line of the not-listed checklist).

## Advisory line — level · source · date, line 0 of `brief.safety`

1. **Primary source = the traveller's passport**, always cross-checked with one second
   source (US or UK — both are keyless JSON, data-sources.md §Travel advisory): mainland
   China → 中国领事服务网 旅行风险等级 + 安全提醒 (browser pane); US → State Department
   advisories API; UK → gov.uk foreign-travel-advice API; Australia → Smartraveller;
   any other passport → its own foreign ministry in the browser pane. Two sources that
   disagree on level → the stricter one drives the plan and the disagreement goes into
   `unverified`.
2. **Level drives the plan.** "Do not travel" / US Level 4 / UK "avoid all travel" /
   CN 暂勿前往 on any base, leg or day trip → stop the pipeline and ask the user
   (Interaction contract moment 0 or a); Level 3 / "avoid all but essential" → the user
   decides with the line in front of them; a regional status ("… to parts of") → check
   every base, intercity leg and day trip against the named areas — a hit moves the
   base or asks.
3. **Write it** as line 0 of `brief.safety`: `advisory: {level} · {source} · as-of
   {date} (second source: {level})`. The T-14 and T-3 rows of the pre-departure ladder
   re-read both sources (output-template.md §Pre-departure re-check ladder).
4. The advisory page's "Safety and security", "Local laws and customs", "Health" and
   "Getting help" sections are the sources for `brief.safety` lines 1-6,
   a cross-check of `brief.health` lines 2-4, and `brief.emergency` lines 1-3 — one
   read feeds three cards.

## Emergency card — `brief.emergency`, six lines

Every number comes from the advisory page's "Getting help" / emergency section, the
mission's own site or the insurer's schedule, stamped as-of; none from memory.
1. Local emergency numbers: police · ambulance · fire — copied from the advisory page's
   "Getting help" section and stamped as-of (the familiar ones — 112 / 911 / 110 — are
   still copied and stamped from the page, never typed from memory).
2. The home consular hotline: CN 12308 / +86-10-12308 · US +1-202-501-4444 · UK +44 20
   7008 5000 · AU +61 2 6261 3305 (all four verified 2026-09-03) — printed with
   "verify at link" + the ministry page's URL; the T-14 row re-reads it.
3. The nearest mission per base: name · address · phone · office hours · link.
4. Insurer assistance line + policy-number placeholder + the first-call rule
   (approval-first clauses; hospital ER over storefront clinics; itemised bill;
   police report within the policy's window) — data-sources.md §Travel insurance.
5. Lost passport: police report first (keep the receipt) → nearest mission for an
   emergency travel document (photos + copies + the report) → the destination's
   exit-record rule before flying out ⚡.
6. Per base: one 24-hour ER with an international department (name · address · map
   link, from the browser Google Maps place card — no search budget) and the local word
   for pharmacy + one near the hotel. A base more than 2 h from an ER (desert camp,
   fjord, park lodge) gets that fact in the day note and the insurer's medical-transport
   clause checked against it.
Checklist rows this card adds: "copies ×2 (passport / visa / policy / tickets) + cloud
copies + 2 passport photos" (before departure) and the trip-registration row by
passport (中国领事 APP 出行登记 · US STEP · Smartraveller subscription — the user
registers in their own app / account; the plan lists the row and the official link,
Hard rule 1).

## Health line — `brief.health`, and the yellow-fever audit

One WebFetch per destination — not a search — of the CDC destination page (static,
sections Travel Health Notices · Vaccines and Medicines · Non-Vaccine-Preventable
Diseases · Stay Healthy and Safe · Packing List) or the TravelHealthPro country page;
zh plans also cite the 海关总署 / 国际旅行卫生保健中心 health notice as the user-facing
pointer (recipes: data-sources.md §Travel health). Five lines:
1. Vaccines and prophylaxis: the page's "recommended for most / some travellers" rows,
   copied, plus activity tags from the route (rural nights, hiking, animal contact,
   altitude) → one checklist row **"travel-clinic consult (vaccines / prophylaxis)"**,
   deadline departure − 4 to 6 weeks — or NOW when departure is already inside 6 weeks
   (the row then says "book this week; a late series may not cover the whole trip"), its
   note = that agenda; the row sorts second in the booking checklist, right after visa
   (output-template.md §Final deliverable item 3). The plan writes the consult
   date and the agenda; it never doses or prescribes (country-quick-notes.md §Travel
   clinic) — the Diamox rule generalised.
2. Vector-borne diseases present and their season (dengue, malaria, Japanese
   encephalitis, chikungunya, tick-borne …): name + months. Where the line names a
   mosquito-borne disease, dusk blocks in wetlands, paddies, forest or river boats
   carry the repellent note once per base — not on every row.
3. Water and food: tap water drinkable / bottled only · ice caution · raw and street
   food line, from "Eat and drink safely"; on bottled-water destinations the first
   street-food meal block of each base carries "hot cooked food, no raw, no ice" once.
4. Rabies and animals: the page's rabies line + "no touching dogs / monkeys / bats;
   any bite → wash 15 min → ER the same day".
5. Notice level + as-of (CDC Travel Health Notice level, or "none"), and the page URL.
**Yellow-fever certificate audit** — an entry document, run with the visa audit: for
every entry country AND every transit airport read WHO Annex 1 (data-sources.md §Travel
health): is it a risk country, and does it require the certificate from travellers
arriving from one (the transit footnotes: > 12 h / > 4 h / any duration / > 24 h in
Brazil-Bolivia-Peru-Venezuela — read the footnote per country). Any hit → checklist row
"yellow-fever vaccine + ICVP" (小黄本), deadline departure − 10 days −
clinic lead time (the certificate is valid 10 days after the jab, for life since 2016;
mainland China vaccinates only at ITHC clinics); that date already passed → stop and
ask before the skeleton is fixed — the certificate cannot be back-dated and the entry
country can refuse boarding.

## Hazard line — the season card and the hazard gate

1. **Season table first**: country-quick-notes.md §Hazard seasons — does the travel
   window intersect a typhoon / hurricane / monsoon / wildfire / heat / avalanche season,
   or sit on a volcano or earthquake exposure? Then the live feeds (data-sources.md
   §Hazard feeds: GDACS, USGS, NOAA NHC; JMA / BoM / CWA in the browser pane) — is
   anything active on the route now?
2. **A hit produces four things**: the `brief.season` card (hazard · months · official
   source URL · what the plan does about it, ≤ 5 lines); a **hazard gate** — the
   official source URL and the decision it gates (cancel / reroute / swap the island
   day) as **one named checklist row beside the ladder — not folded into T-14 / T-7 /
   T-3** (the T-7 row only re-reads the season card), deadline = the exposed booking's
   free-cancellation cutoff or the official forecast horizon, whichever is earlier, with
   its own `.ics` VEVENT every time; the insurance row's deadline set to NOW (data-sources.md
   §Travel insurance "buy before the world moves"); every exposed booking (ferry, island
   day, mountain hut, park lodge, balloon) kept refundable until the gate, and one
   buffer day when the window sits on the season's peak.
3. Volcano and aurora days keep the base-rate rule of Phase 4 (phase-4-days.md): plan
   the day to work without the phenomenon; the official forecast horizon sets the gate.
4. No hit → no card, no `unverified` line, no prose: silence is correct here; the exit
   criteria only ask that the table was consulted.

## Exit criteria — tick every line before Phase 2

- [ ] `brief` cards present in canonical order — visa · emergency · safety (line 0 =
      advisory) · health · holidays · weather (mode + as-of) · money · connectivity ·
      insurance · baggage (+ season when the window hits, after `baggage`) — every line
      with source + as-of, no
      line from memory, every absent fact written "n/a — see advisory" beside the URL +
      as-of of the page read for it (an "n/a" with no page read behind it is a fail).
- [ ] The visa audit and the yellow-fever audit covered every entry country and every
      transit airport.
- [ ] No base, leg or day trip inside a "do not travel" or regional-avoid area; a
      Level-4 hit stopped the pipeline and asked.
- [ ] Checklist rows: visa lead time · travel-clinic consult (when the health page
      recommends any vaccine or prophylaxis) · yellow-fever vaccine + ICVP (when the
      audit hits) · insurance (deadline NOW if a hazard gate exists) · hazard gate (when
      exposed) · copies + registration.
- [ ] User-named events verified: venue, date, local kickoff time, on-sale status.
- [ ] §Hazard seasons was consulted for the window, whether or not it hit.
