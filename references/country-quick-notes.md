# Country quick notes

High-churn facts are marked ⚡ — re-verify at plan time. Everything here is a starting
point, not a source: it saves searches by telling you what to search for.

**Two directions live in this file.** Most sections are **outbound** — a Chinese
passport leaving China (visa lines say "Chinese passports need…"). The **China
(inbound)** section is the reverse: a foreign passport entering mainland China. When
the traveller is not Chinese, read the visa line of every outbound section as "check
your own passport", and use the destination-has-no-section rule below for the rest.

**Destination has no section here?** Don't improvise — work the **"Destination not
listed?" checklist** immediately below, then write what you found into a new section
here so the next run doesn't pay for it again.

## Destination not listed? — the checklist (as of 2026-08, after the Mexico / Morocco / Turkey / Vietnam tests)

Four consecutive test trips landed on countries with no section here — the whole of
Latin America, Africa, the Middle East / West Asia, and Vietnam. Every line below is
something that silently produced a *wrong plan* in at least one of those runs. Phase 1
reserves its 2-3 extra searches for the lines marked **hard**.

- [ ] **hard — Visa / entry, two official sources, dated.** Check the traveller's actual
  passport against the destination's MFA or immigration site *and* their own foreign
  ministry; write "as of <month>, verify before booking". Rules flip: Turkey went
  visa-free for Chinese ordinary passports on 2026-01-02 and the old "e-Visa" answer is
  still all over the web. **The assembler owns this line — city subagents must not
  decide visa questions** (on the Turkey test both of them returned the stale answer and
  put it first on the checklist, which is the expensive kind of wrong). The same audit
  carries the **yellow-fever certificate column** — every entry country and every
  transit airport (data-sources.md §Visa / entry).
- [ ] **Currency: closed or convertible, and does the FX source carry it?**
  `frankfurter.dev` carries exactly **30 currencies** (checked 2026-08: no MAD, no VND)
  and **silently drops** a symbol it doesn't have — HTTP 200, key just missing, so an
  unchecked run prices the trip in the wrong money. Count the keys you asked for.
  Fallback `open.er-api.com` (keyless), reason noted in `meta.fx`. Closed currencies
  (MAD, TND, DZD…) can't be bought before or carried out after — say so in the brief.
- [ ] **hard — Holidays: can the source see religious ones?** `date.nager.at` returns
  fixed-date **secular** holidays only. Muslim countries: Ramadan, Eid al-Fitr, Eid
  al-Adha, Islamic New Year and Mawlid all move on the Hijri calendar — one separate
  search. Same for lunar/Buddhist calendars (Tết, Songkran, Vesak). And the reverse trap:
  Día de Muertos is *not* a statutory holiday, yet flights, buses and hotels price like
  one. "The API says no holiday" is not "no crowds".
- [ ] **Regional and school holidays.** nager's `counties` field carries state-level days;
  school breaks appear in no API at all, and they are what move hotel prices.
- [ ] **hard — Time zone and DST, before any prose.** Run `route_tools sun --write`
  *first*, then write every sunrise/sunset/golden-hour line against its values — Morocco
  moved to permanent UTC+0 on 2026-09-20 and ten days of hand-written times were an hour
  out, invisible to `qc`, `check` and the renderers. Check intra-country splits too.
- [ ] **Transit card and passes, with the break-even.** Name the card (Istanbulkart,
  Suica, Opal, T-money, Rejsekort…) and say on which ride or day it pays back; price
  museum passes against the actual anchor list, not the brochure.
- [ ] **Weekly rhythms of worship and markets.** Friday midday prayer shuts mosques and
  madrasas to visitors ~12:00-14:30 across Muslim countries; Istanbul's covered bazaars
  close Sundays; museums close Monday or Tuesday; Sunday morning belongs to Mass. Fix the
  weekly pattern *before* pinning anchors — it reshuffles the whole route.
- [ ] **Local ride app, payment, SIM.** Which app actually works (Grab, BiTaksi, Bolt,
  DiDi, Uber-on-licensed-taxis), how cash-first the country really is, and whether a
  local SIM is a trap — Turkey IMEI-blocks an unregistered foreign handset after ~120
  days, so eSIM or roaming.
- [ ] **Driving licence and insurance: the 1968 Vienna Convention test.** An IDP is only
  recognised where both countries are parties. **China is not a party and issues no IDP**
  — self-driving or riding anything over 50 cc is unlicensed driving, and the insurer
  refuses the claim outright. Answer with pillion seats, drivers and bicycles, never
  "just rent a scooter". (US: party to 1949 Geneva but China to neither convention,
  so no recognition either way — see §USA Driving for the counter reality.)
- [ ] **Intercity ticket release windows, each with its own date on the checklist.**
  Vietnam rail 60 days, China 12306 15 days, Japan JR 1 month, Trenitalia/Italo 90-120
  days, Norway Vy ~90 — plus night-bus operators and seasonal ferry timetables.
- [ ] **Highest sleeping altitude and the ladder to it.** Not the highest point
  visited — the highest **bed**, and the steps up to it. See §Altitude below: this
  line reshapes the route order, so it is answered at skeleton time, not at packing
  time.
- [ ] **Travel advisory, and what the insurance must cover.** Read the traveller's own
  foreign ministry (Auswärtiges Amt, travel.gc.ca, 中国领事服务网), then check the policy
  does not exclude the thing the trip is built on — ballooning, diving, motorbike
  pillion, altitude — and that it carries repatriation where hospitals want cash up front.
- [ ] **hard — Health: vaccines, vectors, water, rabies — one CDC / TravelHealthPro
  page, dated** (→ `brief.health` five lines + the travel-clinic consult row;
  phase-1-brief.md §Health line). The plan never doses.
- [ ] **hard — Hazard season: does the window hit one?** §Hazard seasons below, then the
  live feeds (data-sources.md §Hazard feeds) → `brief.season` card + hazard gate +
  insurance deadline NOW (phase-1-brief.md §Hazard line).
- [ ] **hard — Street safety, six named lines** (the `brief.safety` template,
  output-template.md §Brief templates): ① 2-3 current scams by name — the advisory
  page's "Safety and security" section plus one `{city} scam tourists {year}` search;
  ② pickpocket hotspots by line / station / square; ③ the taxi rule (which app, the
  official airport rank, never the arrivals-hall tout); ④ the after-dark avoid list per
  base; ⑤ what to do when it happens (police report first — the report number is the
  claim key, data-sources.md §Travel insurance); ⑥ legal & customs red lines (drones ·
  vapes · biosecurity declarations · alcohol / dress / blasphemy · photographing
  military sites · same-sex relations law) from the advisory page's "Local laws".
- [ ] **Money lines, the universal five** (data-sources.md §FX → Money safety): refuse
  DCC · card FX fee → buffer · ATM fee and cap · cash number · which cards and wallets
  work — plus the **mainland-China origin trio** when the traveller departs from
  there: UnionPay vs Visa/MC acceptance, Alipay+ / WeChat coverage ⚡, foreign cash
  pre-ordered 1-2 days ahead.

## Altitude

- **Design the sleep ladder, not just the route.** What the body prices is the
  altitude it *sleeps* at: a high day trip from a low bed is forgiving, while raising
  the sleeping altitude by big jumps above ~2,500 m is what loses a day to headache
  and bad sleep. Order the bases so the beds climb gradually and the highest bed
  comes late — this is a route-order decision, which is why the checklist asks it at
  skeleton time.
- **Cap the first day at altitude.** Arriving high (CDMX 2,240 m, Lijiang 2,400 m,
  Cusco 3,400 m): one light anchor, no stair-heavy sight, no same-day push higher.
  The energy-curve rule (scheduling.md rule 6) tightens at altitude; it never relaxes.
- **Diamox lead time is a doctor's question.** The plan writes "the traveller asks
  their doctor about acetazolamide, N days before the climb" and puts the consult
  date on the checklist — it never doses or prescribes.
- **Insurance reads altitude sickness as illness, not accident** — and many policies
  also cap covered altitude at 3,000-4,000 m. Check the policy's altitude ceiling
  against the trip's highest point, and that illness cover (not just accident cover)
  is real, before buying — see data-sources.md §Travel insurance.

## Travel clinic

The Diamox rule, generalised to every vaccine and prophylaxis: **the plan writes the
consult date and the agenda; it never doses or prescribes.** Consult = departure − 4 to
6 weeks (rabies pre-exposure needs two doses in 7 days, Japanese encephalitis two in
28, hepatitis A ≥ 2 weeks, malaria prophylaxis starts 1-2 days to 1-2 weeks before
depending on the drug — all reasons the row sits early in the urgency sort). Agenda =
the health page's "recommended for most / some travellers" rows + the route's activity
tags (rural nights, hiking, animal contact, altitude, diving). The yellow-fever
certificate has its own lead time: 10 days after the jab (phase-1-brief.md §Health
line). Typhoid / hepatitis A "recommended for most travellers" and ORS in the kit are
agenda items, not plan prescriptions.

## Hazard seasons

Window ∩ season ≠ ∅ → `brief.season` card + hazard gate + insurance deadline NOW +
exposed bookings refundable + one buffer day at the peak (phase-1-brief.md §Hazard
line). Months are the usual season, all ⚡ — the official source column is what the
gate re-reads.

| region | hazard | months | official source | plan action |
|---|---|---|---|---|
| Japan · Taiwan · Philippines · Vietnam · Hong Kong · S China | typhoon | Jul-Oct, peak Aug-Sep | JMA · CWA · PAGASA · HKO · NCHMF | ferries, islands and Shinkansen days refundable; +1 buffer day |
| US Gulf + SE coasts · Caribbean · Mexico Caribbean | Atlantic hurricane | 1 Jun-30 Nov, peak Aug-Oct | NOAA NHC | same; cruise / island days keep a backup date |
| Mexico Pacific · Central America Pacific | East Pacific hurricane | May-Nov | NOAA NHC · SMN | same |
| India · Bangladesh · Sri Lanka SW · Thailand · Myanmar | monsoon floods | Jun-Oct | IMD · TMD | rail / road days with a fly-over fallback; rule 10 rain |
| Central Vietnam (Huế-Hội An-Đà Nẵng) | floods | Oct-Dec | NCHMF | the evacuation plan in the city section (§Vietnam) |
| Northern Australia | cyclone + stinger season | Nov-Apr | BoM | reef days weather-backed; stinger suits |
| US West · Canada West · SE Australia · Mediterranean (GR/ES/PT/IT/FR) · Chile | wildfire + smoke | Jul-Oct N · Dec-Mar S · Jul-Sep Med | national fire service; AirNow / air-quality index | park days droppable; smoke = indoor rain_alt |
| Middle East · Mediterranean · South Asia | heat ≥ 38 °C | Jul-Aug · Apr-Jun | national met office | scheduling.md rule 10 heat, every day |
| Iceland · Italy (Etna, Stromboli) · Indonesia · Hawaii · Japan · Guatemala · Philippines | volcano | year-round | USGS HVO · INGV · PVMBG · JMA | base-rate rule (phase-4-days.md); gate on the observatory's alert level |
| Japan · Taiwan · Turkey · Indonesia · Chile · Peru · Mexico · Italy · NZ · Nepal | earthquake / tsunami | year-round | USGS feed · JMA | one `brief.season` line: coastal bases know the high ground |
| Alps · Nordic · Hokkaido · Rockies · Andes passes | avalanche + winter road closures | Nov-Apr | road authority (Vegvesen, NEXCO …) | mountain legs with a rail or fly alternative |
| > 66°N | polar night · midnight sun | late Nov-mid Jan · Jun-Jul | — | a plan shaper, not a hazard: daylight in every day header, rule 10 cold |
| Southern hemisphere | seasons reversed | Dec-Feb = summer | — | check the season card against the month, not the name |

## Japan
- Hazards: typhoon season Jul-Oct, peak Aug-Sep (JMA) — island, ferry and Shinkansen
  days refundable with one buffer day; earthquakes year-round (JMA / USGS feed) —
  §Hazard seasons.
- Entry: most treaty passports get 90-day visa-free stamps ⚡; **Chinese passports
  need a visa** — the JAPAN eVISA (single-entry tourism, 15/30-day stays) covers
  mainland residents ⚡, and there is no transit-without-visa landing for PRC
  passports: airside-only connections are fine, but stepping landside (e.g. to
  re-check bags on separate tickets) needs the visa.
- Transit: Suica/ICOCA in Apple Wallet works for visitors ⚡; Google Maps transit is
  reliable countrywide.
- JR Pass: since the Oct-2023 price hike the nationwide pass usually LOSES on the
  Tokyo–Kyoto–Osaka golden route — do the arithmetic vs Smart-EX singles ⚡. Regional
  passes (JR West/Kansai etc.) still often win.
- Shinkansen: Smart-EX app/site or Klook; reserved seats fine 1-3 days out except peaks.
- Sell-outs to check early: Ghibli Museum (sales open the 10th of the prior month,
  JST), Ghibli Park, teamLab, Shibuya Sky sunset slots, Pokémon Café, Nintendo Museum ⚡.
- Peaks to avoid or book months ahead: Golden Week (Apr 29–May 5), Obon (~Aug 11-16),
  New Year (Dec 29–Jan 3), cherry-blossom Kyoto weekends.
- Closures: many museums close Mondays; when Monday is a national holiday they close
  Tuesday instead.
- Cash still matters at small restaurants and shrines; 7-Eleven ATMs take foreign cards.
- Luggage on move days: takkyubin (ヤマト等) hotel→hotel is usually **next-day** — book
  it the evening before and keep an overnight kit; station coin lockers, especially the
  large ones at Kyoto/Tokyo/Shinjuku, are gone by mid-morning in peak season.
- **IC cards** (added 2026-08 after the London→Japan test): Suica / PASMO / ICOCA are
  interchangeable nationwide for metro, JR local, buses and konbini — one card, any
  region. Visitors: Apple Wallet Suica/PASMO (top up with a foreign card ⚡, no
  physical card needed) or a Welcome Suica at the airport ⚡ (physical-card sales were
  rationed 2023-24 and still come and go — check). An IC card does **not** cover
  Shinkansen reserved seats or limited-express surcharges: those are separate tickets.
- **Shinkansen booking window**: JR reservations (Smart-EX / EX app, JR West/East
  sites, station counters) open **1 month before the travel date at 10:00 JST** ⚡ —
  earlier for nothing. Ordinary days: 1-3 days out is fine; koyo weekends, Golden
  Week, Obon and the New-Year run sell the good trains on day one. Suitcases over
  **160 cm** (L+W+H) on the Tokaido/Sanyo/Kyushu Shinkansen need the free
  "oversized baggage" seat reservation ⚡ or you pay a fee on board — say so on
  every Shinkansen move day.
- **Autumn (紅葉) season**: Kyoto colour peaks roughly mid-to-late November ⚡ (the
  koyo forecast pages move it by a week each year — verify in September). Temple
  night illuminations (Kiyomizu, Eikan-dō, Kōdai-ji…) run fixed date windows and
  ticket separately ⚡. **Labour Thanksgiving Day, 23 November** is a national
  holiday — when it lands on a Monday, Monday-closed museums close **Tuesday**
  instead (rule above), and the three-day weekend is a domestic-crowd peak.
- **Geocoding Japanese places is unreliable** — Nominatim is weak on Japanese names,
  and *wrong* is worse than *missing*: on the 2026 test `Gōra Station` resolved
  ~600 m off and `Sannenzaka` landed on a guesthouse named after the street, both
  silently. Hand-fill `lat/lon` for anything you already know (temples, stations,
  markets), read every resolved `display_name` against the query, and re-query
  with the Japanese name (`強羅駅`, `産寧坂`) before trusting a hit — see
  navigation.md "Geocoding discipline".
- Street safety: crime is low; the real risks are bicycles on pavements, the last
  train's drunk crowd, and left-side traffic when crossing — these are lines ② and ④
  of the six-line `brief.safety` template; the other four lines are still written,
  mostly "none of note", never imported warnings.

## Korea
- Google Maps directions are crippled — plan with Naver Map (EN ok) or Kakao Map.
- T-money card everywhere; KTX via Korail site/app ⚡.
- DMZ tours book out ~1 week and require the passport on the day.
- Street safety: low crime; the risks are late-night drinking districts and taxis
  refusing short rides (Kakao T solves the second) — lines ② ④ of the six-line
  `brief.safety` template; the other four are written short ("none of note").

## Thailand / SE Asia
- Grab is the city-transport default; 12go.asia for intercity bus/train/ferry.
- Temples: shoulders/knees covered; temples take the opener slot — scheduling.md rule
  10 (heat) triggers most days of the year here.
- Onward-ticket rules enforced unevenly ⚡ — check before booking one-ways.
- **Vietnam has its own section below** — the visa, licence and FX traps there are not
  generic to the region.

## Vietnam (as of 2026-08, after the Shenzhen→Vietnam test)
- **e-Visa from the government portal only — `evisa.gov.vn`**: US$25 single / US$50
  multiple, up to **90 days**, **3-5 working days** (7-10 in peak) ⚡, all nationalities
  including Chinese passports. The first screen of search results is agencies charging
  US$20-60 on top, so name the official site. The approval is a **PDF you must print** —
  the counter wants paper. Submit ~3 weeks out. Never fill the form for the user.
- **Driving licence — the trap that voids the insurance.** Vietnam recognises only IDPs
  issued under the **1968 Vienna Convention**; **China is not a party and issues no IDP**,
  so riding anything over 50 cc is unlicensed driving — fines to ₫5 M and, far worse,
  **the travel/medical policy refuses the claim in full**. The obvious answer ("rent a
  scooter") is wrong: pillion tours with a licensed driver, or a bicycle — say why in
  `decisions` and `brief.safety`.
- **VND is not in frankfurter.dev and the API drops it silently** — `symbols=VND,USD`
  returns HTTP 200 with only USD, so an unchecked run quietly prices the trip in dollars.
  Use `open.er-api.com` and count the keys. Mental rate ₫10,000 ≈ ¥2.6 (2026-08 ⚡).
- **Night trains: `dsvn.vn`**, the official railway site — cheaper than agents, foreign
  passports can book, passport at the counter. **Sales open 60 days ahead** ⚡: that date
  goes on the checklist. Hanoi→Đà Nẵng **SE** (SE19 dep ~19:50, arr ~12:35 next day,
  15.5-17 h ⚡, soft sleeper US$45-55 pp) kills a hotel night, a flight and a travel day —
  but only on that leg; Đà Nẵng→Saigon is a 1 h 20 flight against 15 h of rail.
- **Hạ Long: 2D1N boat vs day trip is arithmetic, not taste.** The day trip spends ~6 h on
  the road for ~4 h of water; the overnight buys sunset, stars and the morning bay and
  replaces a Hanoi hotel night, at US$105-160 pp + US$20-40 transfer ⚡ (~13% of a
  mid-budget trip). Lan Hạ Bay: same class, US$20-50 less, fewer boats. Confirm transfers
  included, big bags on board (they are), kayak included.
- **December is three climates in one trip**: Hanoi/Hạ Long 19-24 °C, one rain day in ten;
  **Hội An / Đà Nẵng 24-26 °C with rain on all ten days, ~137 mm** — the tail of the
  central wet season, so both Hội An days need a rain plan *and* a "Thu Bồn floods the old
  town → move the block north to Đà Nẵng" escape; Saigon 28-31 °C dry with afternoon
  showers. Sunset ~17:15-17:35 mid-December — nothing outdoors after 17:00.
- Holidays: four statutory days (1 Jan, 30 Apr, 1 May, 2 Sep) plus **Tết** on the lunar
  calendar, so most windows are clear — but Christmas, *not* a holiday, packs the church
  districts on 24-25 Dec, and December opens the western high season (boats and Hội An
  homestays +15-30% over November ⚡). Hội An's lantern night is the 14th of the **lunar**
  month — check the lunar date, not the guidebook photo.
- Money and apps: cash society (street food, basket boats, markets, xe ôm); ATM fees
  ₫50-165k or 2-5% with ₫2-5 M local-bank caps → fewer, larger withdrawals. **No tipping
  culture**, but ₫50-100k lands well with boat crew and drivers. **Grab** is the ride/food
  default. ₫20,000 and ₫500,000 are both blue polymer notes: count the zeros.
- Streets: the motorbike flow does not stop — cross at a steady, straight, unhurried pace
  and let it part around you; stopping mid-road is the dangerous move. Phone-snatching
  from bikes is the real Saigon risk. Low-cost domestic carriers sell **bare fares with no
  checked bag** — buy the 20 kg at ticketing, it doubles at the airport.

## Italy / Spain / France
- Rail: book Trenitalia/Italo, Renfe, SNCF directly 2-4 months out — high-speed fares
  rise as buckets sell. Omio/Trainline acceptable when foreign cards fail; small markup.
- Sell-outs: Uffizi & Accademia, Colosseum underground, Vatican early entry, Alhambra
  (often 2-4 weeks!), Sagrada Família, Louvre timed entry, Eiffel summit.
- State museums close Mon or Tue (varies); free first Sundays = the worst crowds
  (Vatican Museums: last Sunday). Churches shut to tourists during Mass and commonly
  12:00-15:00; shops and small venues keep siesta hours ~13:30-17:00 in Spain and
  small-town Italy.
- City tourist tax is collected at the hotel, sometimes cash-only — put it in the budget.
- August: locals on holiday — Paris/Madrid partially shut, coasts jammed ⚡.
- Street safety (`brief.safety` lines ① ②, all ⚡ — re-check against the advisory
  page): Rome — Termini and metro lines A / B, buses 64 and 40, the "friendship
  bracelet" and petition-clipboard scams; Barcelona — La Rambla and metro L3, the
  "bird-dropping" distraction; Paris — metro line 1, RER B from CDG, the "gold ring"
  and petition scams; everywhere, taxis only from the official rank or the app.

## Italy — Rome / Florence / Venice specifics (as of 2026-08, after the Singapore→Italy test)
- Entry: **Singapore (and most treaty) passports are Schengen visa-free, 90 days in
  any 180**; Chinese passports need a Schengen visa from the country of main stay
  (see Nordic). Two schedule-shaping rules on top of the visa question: **EES**
  (biometric entry/exit registration, live since 2026-04-10 ⚡ — first-time entry
  takes face + four fingerprints, budget +60 min at the border) and **ETIAS**
  (official line: launches Q4 2026, mandatory from 2027-01-01 ⚡) — a trip in that
  window gets a "re-check the official ETIAS page 1 month before departure" checklist
  item, not a guess either way.
- **Closure days differ by museum, not by city**: Uffizi, Accademia, Galleria
  Borghese, Capitoline Museums, Doge's Palace side rooms → **Monday**; **Peggy
  Guggenheim (Venice) → Tuesday**; Vatican Museums → Sunday (except the free last
  Sunday); Colosseum/Forum open daily. The Italy test's worst self-check catch was a
  Tuesday rain alternative pointing at the Peggy Guggenheim — run every rain/swap
  target through the same day-of-week check as the anchors, and put the Monday
  closure day to work as the transfer day.
- **Rail release windows**: Trenitalia (Frecciarossa/Frecciargento) opens sales
  roughly **90-120 days out** and Italo about the same ⚡ — Super Economy buckets on
  Rome–Florence–Venice can be a third of the walk-up fare and are gone weeks ahead
  in October; book the exact train (seat reservation is compulsory on the Frecce),
  and expect foreign cards to fail sometimes → Omio/Trainline as fallback with markup.
- **Venice access fee** (Contributo di Accesso): day-visitors pay on a published
  calendar of peak dates (spring–summer weekends and holidays; €5 booked ahead,
  higher if paid late ⚡ — the calendar changes every year), overnight guests are
  exempt but must hold the exemption/hotel registration. Look up the year's date list
  on the Comune's official page and say for each Venice day whether it is a fee day.
  Also: no vaporetto in the small hours — an early VCE departure needs a **pre-booked
  water taxi** (~€100-150 ⚡) written into the plan the night before.
- **Holy days and dress**: churches keep to the Mass schedule (Sunday morning is for
  worshippers; feast days such as 1 Nov, 8 Dec and Easter week close museums or shift
  hours ⚡), and enforce the dress code at the door — St Peter's, the Duomo of
  Florence and San Marco turn away shoulders/knees/hats. Every worship-site block
  carries the one-line dress note (scheduling.md Traps).

## USA (as of 2026-08)
- Hazards: Atlantic hurricanes Jun-Nov on the Gulf and SE coasts (NOAA NHC), wildfire
  smoke Jul-Oct in the West (AirNow), winter road closures in the Rockies / Sierra —
  §Hazard seasons; the volcano gate on a Hawaii trip is the worked example of a
  hazard gate.
- Entry: VWP/ESTA covers treaty passports only — **Chinese passports need a B1/B2
  visa** (Beijing interview waits run weeks-months ⚡) **plus current EVUS enrollment**
  on 10-year visas ⚡. On any US trip, visa status is the first intake question.
- Driving: state law and the rental counter are **two different gates** ⚡.
  UT/ID/MT-style statutes accept any home-country license for visitors, but Hertz's
  published policy requires an IDP for **non-Latin-alphabet** licenses (with a
  separate PRC-license certification-form path ⚡) and Enterprise strongly
  recommends one — and mainland China cannot issue a genuine IDP (party to neither
  road-traffic convention), so a Chinese-license renter can be refused at the
  counter even where state law is fine. Translations work often in practice but are
  not policy: get written confirmation from the specific pickup branch before
  building a self-drive plan, and treat counter refusal — plus the insurer
  re-examining license validity after an accident — as the headline risk, ahead of
  road skills. Car essential outside NYC/SF/Boston/Chicago/DC; city parking
  $40-70/night.
- Parks: entrance fees are per **vehicle** (~$35); 3+ parks → an annual pass wins,
  but the $80 America the Beautiful is **residents-only since 2026** ⚡ —
  non-residents see the surcharge bullet below for the $250 pass that replaces it. Timed-entry policy
  changes per park per year ⚡ (Yosemite dropped its system for 2026; Yellowstone
  has never had one — check each park). In-park lodges and gateway towns sell out
  and close seasonally ⚡.
- **Non-resident park surcharge (2026-01-01 ⚡)**: non-US residents 16+ pay
  **$100/person at 11 flagship parks** (Acadia, Bryce, Everglades, Glacier, Grand
  Canyon, Grand Teton, Rocky Mountain, Sequoia/Kings Canyon, Yellowstone,
  Yosemite, Zion — no park outside these 11 charges it); the $250 non-resident
  annual pass waives it, admitting the whole private vehicle at per-vehicle parks
  or the holder + 3 adults at per-person parks, so it wins from the 2nd park even
  solo ($135×2 > $250). Tour smallprint now reads "park fees included **for US
  residents**" — that wording excludes the surcharge; ask who collects it.
- Bags ⚡: domestic carriers don't weigh carry-ons (size 22×14×9 in only) but
  charge ~$35-45 **per checked bag per one-way** (connections included; separate
  tickets and directions are what multiply) — so one case beats two across a
  multi-leg itinerary; CN/JP carriers on the international bookends DO weigh cabin
  bags (5-10 kg), so "carry-on only" dies at international check-in, not domestic.
  UA Basic Economy is personal-item-only on domestic/short-haul Latin America
  routes (long-haul international keeps the carry-on).
- Hotels ⚡: resort strips (Waikiki, Las Vegas) carry resort/urban fees of
  $30-56/night plus ~19% taxes — sometimes inside the list price, sometimes at the
  property; quote the checkout all-in (data-sources.md §Hotels), and expect NYC
  boutiques to do the same with "urban" fees.
- Lookalike names bite bookings: **JAC** (Jackson Hole, WY) vs **JAX**
  (Jacksonville, FL) is one airport-code letter; Columbus OH vs GA, Jackson
  WY/MS/TN; SFO searches on aggregators mix in OAK/SJC departures. Booking links
  in the plan carry the state (see output-template.md §Booking-artifact conventions).
- Booking forms: **KTN = a US trusted-traveler number** (TSA PreCheck / Global
  Entry) — leave it blank; never the passport number. (A mismatched KTN is
  silently ignored, so the mistake is harmless — but it buys nothing, and the
  passport goes only in the travel-documents section at check-in.)
- Sports tickets: team site first, then SeatGeek/StubHub resale — marquee fixtures
  (Messi, playoffs) run 3-10× ⚡; kickoff times can shift for TV after on-sale ⚡.
- Distances are the trap — one region per 10-15 days.

## Mexico — CDMX / Oaxaca, Día de Muertos (as of 2026-08, after the Berlin→Mexico test)
- Entry: German and most EU/UK/US/CA/AU/JP passports are **visa-free for tourism up to
  180 days**; passport valid ≥6 months, a national ID card is not accepted. Chinese
  passports need a Mexican visa *or* qualify on a valid US/Schengen/UK/CA/JP visa ⚡ —
  verify, this is one of the routes that changes.
- **There is no paper FMM by air any more.** Entry is the digital **FMMd**: biometric
  passports use the **E-Gate at AICM**, and what you leave with is a printed slip and/or a
  stamp carrying the entry date and days granted — photograph it, and pull the FMMd PDF
  from the INM site if you need to prove status for a car rental or hotel ⚡. Sites selling
  an "FMM tourist card" for a flight are selling the land-border form.
- **Día de Muertos (1-2 Nov) is NOT a statutory holiday** — nager.at returns zero federal
  holidays across the window (nearest: Revolution Day, 16 Nov) — yet domestic flights, ADO
  buses and Oaxaca hotels fill and price like one. "No holiday" is not "no crowds".
- **The two cities peak on different nights**, which is what makes a combined route work:
  CDMX takes the Saturday Reforma parade, the Coyoacán ofrendas and the marigold canyon at
  the **Mercado de Jamaica** in the last week of October; Oaxaca takes 1 Nov (Angelitos,
  Comparsa de Catrinas, first vigils) and 2 Nov (panteones fill from the afternoon,
  comparsas after dark). ⚡ **The CDMX parade date is published only ~6 weeks out**
  (cultura.cdmx.gob.mx — unpublished on 2026-08-15; historically a Saturday in the window)
  → build the day so it works either way, with a swap tag and a rain_alt, not a guess.
- **Oaxaca 1-5 Nov is the hardest booking on the trip**: the trade line is "book by May",
  by August the centro is largely gone and rates run 2-3× ⚡. Take Jalatlaco or the Santo
  Domingo fringe rather than holding out for the Zócalo.
- CDMX↔Oaxaca: **fly (1 h 05) rather than ADO (6.5-7 h)** on festival days — ADO GL/Platino
  stays as the comfortable budget backup, booked at ado.com.mx, never a reseller. 1 Nov is
  one of the busiest domestic flying days of the Mexican year ⚡.
- **INAH raised admissions on 1 January 2026** and adjusts every January: foreign-visitor
  rate at flagship sites ~MX$210 ⚡, with separate local pricing. Museo Frida Kahlo (Casa
  Azul) is **online timed tickets only — no door sales**, closed Mondays.
- Closure days are per museum: Monday for Antropología, Bellas Artes and Casa Azul;
  **Tuesday** for the Museo Vivo del Muralismo at the SEP. Run rain alternatives through
  the same day-of-week check as the anchors.
- **Uber and DiDi have been barred from AICM pickups since March 2026** ⚡ — authorised
  sitio taxis at the airport, app cars everywhere else, never a street taxi at arrivals.
- Cash for markets, cemeteries, colectivos, comparsa stalls, church donations and every
  tip; bank ATMs (Santander/Banorte/BBVA), and decline the machine's own currency
  conversion. Tipping 10-15% — check whether *propina* is already on the bill.
- Altitude and cold nights: CDMX sits at 2,240 m, so the first day feels thin and the
  nights want a jacket; Monte Albán at midday has no shade. Late Oct – early Nov is the
  dry sweet spot (~24/10 °C, near-zero rain, ~11 h of daylight).
- Manners at the cemeteries: a family occasion, not a show — ask before photographing, buy
  candles and marigolds at the gate stalls, don't step over a grave. Comparsa routes and
  cemetery hours are set locally days ahead ⚡: ask the hotel, don't promise a time.
  Travel-medical insurance **with repatriation** is not the line to skip — private
  hospitals expect cash on the spot and consular help is billed back.

## Australia (as of 2026-08)
- Entry: the ETA (subclass 601) and eVisitor (651) are for listed passports only —
  **Chinese passports need Visitor visa subclass 600** (tourist stream, online via
  ImmiAccount, immi.homeaffairs.gov.au; fee ~AUD 200 ⚡ — the site 403s scrapers, read
  it in the browser pane). Processing: 90% of applications in **~33 days** ⚡ (official
  processing-time page) — for a trip 6-8 weeks out this is the tightest deadline in
  the whole plan and goes to the top of the checklist. Passport valid for the stay;
  no onward-ticket rule, but be ready to show one.
- **Daylight saving splits the country**: NSW/VIC/ACT/SA/TAS switch on the **first
  Sunday of October** (02:00 → 03:00; ends first Sunday of April); **QLD, NT and WA
  do not**. From that Sunday, Sydney/Melbourne run 1 h ahead of Brisbane/Cairns —
  re-check every SYD↔QLD flight, tour pickup and phone-call time across the switch,
  and fetch sun times on both sides of it (scheduling.md rule 7).
- Public holidays are **state-level** — nager.at returns them with a `counties`
  field, read it: the **first Monday of October** is Labour Day in NSW/ACT/SA *and*
  King's Birthday in QLD (a double long weekend; long-weekend hotel/tour surge in
  both states). Melbourne Cup Day (first Tuesday of November) is VIC-only.
- **School holidays** move prices and reef-boat availability more than public
  holidays: NSW spring break runs the last week of September into the first ~2 weeks
  of October (2026: 28 Sep–9 Oct ⚡, education.nsw.gov.au); QLD's is a week earlier
  (⚡ qed.qld.gov.au). Not visible in any holiday API — one search per state.
- Sydney transit: **Opal card or just tap a contactless card/phone** on trains, ferries,
  light rail, buses (transportnsw.info); daily/weekly caps apply automatically. Blue
  Mountains by train from Central (~2 h, Opal) — no car needed for Sydney + Blue
  Mountains. Cairns: day tours include hotel pickup; no useful transit.
- **Seasonal shutdowns are real and per-venue** — Skyrail Rainforest Cableway runs
  reduced loops / full closure days for maintenance in some spring windows ⚡
  (skyrail.com.au notices page); Kuranda Scenic Railway likewise. Check the official
  page for the exact dates before pinning any Kuranda day.
- Great Barrier Reef boats (Cairns/Port Douglas): outer-reef pontoon days are
  **date-sensitive** — capacity, weather cancellations, and stinger season from ~Nov
  ⚡; book the specific date and keep the next day free as weather backup. Prices on
  operator sites (sunlover.com.au, quicksilver-cruises.com…) beat aggregators.
- Money: cards everywhere, cash nearly unnecessary; tipping not expected. UV index
  is extreme even in spring — scheduling.md rule 10 (heat) triggers on UV ≥ 8, so
  hikes take the opener slot with shade / hat / water in the day note.

## Nordic — Norway first; Sweden / Denmark / Finland notes (as of 2026-08)
- Entry: all four are Schengen. **Chinese passports need a Schengen visa, lodged with
  the country of main stay** (most nights; ties → first entry) — Norway via
  VFS Global for the Norwegian embassy (udi.no); ~15 calendar days nominal, apply
  4-8 weeks out ⚡. Travel insurance ≥ €30k mandatory for the application.
- Rail: **Vy** (vy.no) — Oslo–Bergen line **minipris** fares open ~90 days ahead ⚡
  and sell in buckets; the Bergen Railway + Flåm Railway (Flåmsbana, visitflam.com)
  are the classic pairing. Sweden: SJ (sj.se); Denmark: DSB (dsb.dk); Finland: VR
  (vr.fi). Oslo airport → city: **Flytoget 19-20 min** (flytoget.no) or the ordinary
  Vy regional train at half the price, ~23 min — do NOT trust distance-based transit
  estimates here.
- **Fjord boats thin out fast in autumn**: Flåm–Gudvangen (Nærøyfjord) and similar
  cruises drop to reduced timetables around **1 Sep – 15 Oct** and many stop
  mid-October ⚡ (norwaysbest.com / the operator's own timetable). Verify the sailing
  for the *specific date* before pinning a Norway-in-a-nutshell day; the whole day
  hangs on one departure.
- Museums: many close **Mondays** (Oslo and Bergen both) — never put a museum in a
  Monday's rain alternative without checking. Opening hours shorten from October.
- Money: **effectively cashless** — card/phone everywhere including buses and public
  toilets; keep no NOK/SEK/DKK cash. Norway is outside the EU: **tax-free refund on
  purchases ≥ NOK 315** per shop per day (Global Blue / Planet, refund at departure).
- **Autumn school break (høstferie) is invisible to holiday APIs** — Norway has no
  public holiday in October, yet hotels and cabins price up by region: **Oslo /
  eastern fylker take week 40, Bergen / Vestland week 41** ⚡ (dates per fylke on
  the county or kommune school calendar; Sweden's höstlov is week 44, Denmark's
  efterårsferie week 42, Finland's syysloma weeks 42-43 by region). One search per
  fylke you sleep in; expect prices up and family attractions busy.
- **Aurora honesty**: at 60°N (Oslo, Bergen, Flåm) in early October, a single-night
  sighting needs Kp≥6 — roughly 5-10% per night. Say so; sell it as a bonus with a
  "look north after 22:00 if the sky is clear" note, not as an itinerary item.
  Real aurora trips go to Tromsø (69°N) from late September.
- Sun and weather: 60°N early October ≈ 07:20 sunrise / 18:50 sunset and losing ~5
  min a day; Bergen averages >200 rain days a year — every Bergen day gets an indoor
  rain alternative and the fjord day gets a weather-backup date.
- Regional notes: Stockholm — SL tap-to-ride, archipelago boats also seasonal ⚡;
  Copenhagen — Rejsekort or contactless, city very bikeable; Helsinki — HSL app,
  ferry to Tallinn is a valid day trip.
- Street safety: very low crime; the hazards are ice on pavements (Oct-Apr), the
  midnight-sun / polar-night sleep disruption, and hiking weather turning in an hour —
  lines ② and ④ of the six-line `brief.safety` template; the other four are written
  short ("none of note"), never imported warnings.

## Turkey (as of 2026-08, after the Shanghai→Turkey test)
- **Entry — this one flipped recently. Chinese ordinary passports have been visa-free
  since 2026-01-02**, tourism and transit, ≤90 days in any 180 ⚡. Two official sources
  agree (Turkish MFA visa page; Chinese embassy in Ankara notice of 2026-01-12), checked
  2026-08 — **verify again before booking**; the old "e-Visa, and only if you already hold
  a Schengen/US/UK visa" answer is dead but still everywhere online, and work/study still
  need a visa. Passport ≥6 months + a blank page; the border may spot-check a printed
  return ticket, hotel bookings, itinerary and a physical credit card. **The assembler
  decides this line, not the city subagents** — both of them returned the stale answer.
- Holidays: nothing statutory in early October — Republic Day is **29 Oct**, Ramadan 2026
  fell in March. On a Chinese Golden Week trip the pressure is all on the outbound ticket,
  not on the ground ⚡. Watch instead for event weeks that move one town's beds (Cappadocia
  Ultra-Trail, mid-October, date published late ⚡).
- **Istanbulkart**: ~165 TL card fee (non-refundable) + top-up, on metro, tram, bus, ferry
  and funicular; a ride is ~42-46 TL against ~60 TL for a single ⚡, so it pays back on the
  4th ride — at 2-4 rides a day, top up per ride rather than buying a daypass.
- Tickets run through **muze.gov.tr**. Hagia Sophia charges foreigners separately for the
  **upper-gallery visitor route** (~€25 ⚡) and the Istanbul Museum Pass does **not** cover
  it; Topkapı is one combined ticket with the Harem included (~2,750 TL ⚡), closed
  Tuesdays. Price **Museum Pass Türkiye / Cappadocia** against the real anchor list ⚡.
- **Weekly rhythm**: Friday midday prayer closes working mosques to visitors — Hagia Sophia
  before 12:00, Blue Mosque after ~14:45 — and **Kariye/Chora closes to visitors all
  Friday**. The **Grand Bazaar and Spice Bazaar close on Sundays**.
- **Balloons (Cappadocia)**: book 4-8 weeks out ($320-450 pp ⚡). The call is made at
  03:00-05:00 and flights are scrubbed for wind >10 km/h, rain, fog, snow or storms →
  **100% refund or a free move to the next morning**, so the route must hold a **second
  Cappadocia dawn as the standby window** and the operator must be told which evening you
  leave. October is the golden month and also the windy one.
- **Night buses** (obilet.com; Kamil Koç / Süha / Metro / Pamukkale Turizm) save a hotel
  night and a whole day. Pin down three things: whether you change at the Nevşehir
  *otogar*, whether the free *servis* shuttle is included, and the real arrival time.
  Station **emanet** left-luggage exists at most otogars but hours and price need
  confirming on arrival ⚡ — the whole post-night-bus day hangs on it.
- Domestic flights fill what rail doesn't: IST→Nevşehir (NAV) or Kayseri (ASR) for
  Cappadocia, Denizli (DNZ)→IST for Pamukkale. ⚠️ **AJet flies DNZ into Sabiha Gökçen
  (SAW), not IST** — with a European-side hotel that is the wrong airport.
- **Phone: eSIM or roaming, not a local SIM** — Turkey **IMEI-blocks** an unregistered
  foreign handset after ~120 days on a Turkish SIM ⚡. Google Maps works normally, so the
  skill's map deep links are fine; expect occasional throttling of social platforms, and
  venue Wi-Fi that wants a Turkish number.
- Money: the lira inflates fast — don't pre-buy cash. Cards are near-universal (UnionPay is
  not: carry Visa/Mastercard); withdraw at Ziraat / İş Bankası and **always choose to be
  charged in lira**, never the machine's own conversion. Cash for bazaar haggling, dolmuş,
  çay, toilets and tips (restaurants 5-10%).
- Dress and terrain: mosques want covered knees and a headscarf for women, shoes off at the
  door; Pamukkale's travertines are **barefoot-only** (dry bag + quick towel); Uçhisar
  castle has no railings and the Red Valley sand is loose. Check the insurance does **not**
  exclude ballooning — many basic policies do, and it is the centrepiece of the trip.

## Morocco (as of 2026-08, after the Toronto→Morocco test)
- Entry: Canadian, EU, UK, US, AU/NZ and Japanese passports are **visa-free for 90 days**;
  Chinese passports too ⚡ — verify. Passport valid ≥6 months beyond departure; the only
  paperwork is the arrival card handed out on the aircraft, and the one thing to check is
  that you actually got the stamp.
- **MAD is a closed currency** — you cannot buy it before you go or change it back after
  you leave. Draw cash in the CMN arrivals hall and spend the last of it at the airport.
  **frankfurter.dev does not carry MAD** (30-currency list) → `open.er-api.com`, keyless,
  with the reason written into `meta.fx`.
- **Clocks: Morocco left permanent UTC+1 for permanent UTC+0 on 2026-09-20** (tzdata
  2026c) ⚡ — the old Ramadan-only shift is gone. On the test, sunrise/sunset written from
  general knowledge was an hour off for all ten days and nothing in `qc`/`check` caught it:
  **run `sun --write` before any golden-hour prose**, and re-check the offset nearer the
  date. Early-to-mid November: sunrise 06:37-07:00, sunset 17:18-17:39 → golden hour from
  ~16:50, dark by ~18:05. Desert nights ~12 °C; the Rif (Chefchaouen) is where the rain is.
- **date.nager.at returns only fixed-date secular holidays for Morocco** (Green March
  6 Nov, Independence Day 18 Nov) and **lists no Islamic feast at all** — Ramadan, Eid
  al-Fitr, Eid al-Adha, the Islamic New Year and Mawlid need a separate Hijri-calendar
  search ⚡. The Marrakech film festival (late Nov ⚡) doubles hotel rates while being no
  holiday at all.
- **Friday is the weekly rule**: midday prayer closes Bou Inania and similar madrasas and
  mosques to visitors and slows everything ~12:00-14:30 — pin the Fes medina day to a
  Thursday and let Friday be the moving day.
- Intercity: **ONCF** rail (oncf.ma) — Casablanca airport is on the line, so the arrival-day
  run south is a train at a fifth of a private transfer. **CTM** (ctm.ma) and **Supratours**
  are the reserved-seat coaches with a luggage hold; local buses reserve nothing.
  Chefchaouen has neither airport nor rail — the exit is a bus, or Tangier + one flight.
- **Marrakech→Fes across the High Atlas is a 3-day private-car job**, not a shared minibus:
  Tizi n'Tichka, the Dades hairpins and the Erg Chebbi sunrise are exactly the stops a
  17-seat group tour drives past. Get three things in writing: (a) it **ends in Fes**, not
  back in Marrakech; (b) a private vehicle; (c) which camp ("luxury" = ensuite tent).
  Merzouga→Fes is a real **7.5-8 h** ⚡, not the 6 h operators quote. At the camp there is
  no mains power and no signal — charge in Merzouga, carry a battery, and leave the big bag
  padlocked at the auberge with only a daypack on the camel.
- Money and manners: cash for souks, petit taxis, tannery terraces, camel guides and every
  photograph. Tipping is structural and always in dirham: MAD 10-20 porter, 20-50 terrace,
  100-150 half-day guide, 300-500 for the desert driver at the end. Bargain in the souks,
  not in shops with marked prices.
- Medina friction: unofficial "guides" at the Fes gates and the tanneries, and the
  taxi-meter argument — agree the price first or insist on the meter; "la, shukran" and
  keep walking, engaging does not work. GPS drifts badly under the reed-roofed souks, so
  offline maps and the trip KML matter here more than usual.
- Connectivity and cover: eSIM on **INWI or Maroc Telecom** (they have the Atlas road and
  Merzouga; Orange is city-only), plugs C/E at 220 V. Insurance needs **medical
  evacuation** — hospitals expect immediate cash payment, and two nights of this route are
  4+ hours from a major hospital.

## China (inbound) — foreign passport entering mainland China (as of 2026-08, after the NYC→Xi'an/Beijing test)
- **Visa — check the category before anything else.** The much-advertised **240-hour
  visa-free transit** requires an onward ticket to a **third** country/region within
  240 h; a **US round trip (JFK→PEK→JFK) does NOT qualify** → an **L (tourist) visa**
  via the Chinese Visa Application Service Center of the home country (in-person
  fingerprints for most applicants, ~4 working days regular service, US passports
  usually get 10-year multi-entry ⚡). Many European, Australian, NZ, Korean and
  Japanese passports currently have a **unilateral 30-day visa-free** entry ⚡ — those
  lists change every few months, so confirm on the embassy site, not a blog. Passport
  valid ≥6 months. Hotels register foreign guests with the police — pick hotels that
  accept foreigners (nearly all chains do; some budget/local ones don't ⚡).
- **Real-name ticketing everywhere.** Rail, flagship museums, the Great Wall and the
  Forbidden City sell only against a passport number, tickets are non-transferable,
  and the passport itself is the ticket at the gate. Four different pre-sale clocks
  ⚡ run in parallel — put each on the checklist with its own date:
  1. **Rail (12306)**: sales open **15 days** ahead of departure, released in
     station-specific batches during the day (08:00-18:00 China time) — the
     Xi'an↔Beijing HSR (¥515 second class, 4.5-6 h ⚡) fills on peak weekends.
  2. **Forbidden City**: **7 days ahead at 20:00** on the palace's official channel
     (site / WeChat mini-program), passport-numbered, capped daily; **closed
     Mondays** (except national holidays). Weekend and holiday slots go in minutes.
  3. **Great Wall (Badaling / Mutianyu)**: real-name timed reservation, released ~7
     days ahead ⚡; Mutianyu is the calmer choice, Badaling has the train.
  4. **Terracotta Army / Shaanxi History Museum / National Museum**: real-name
     reservation windows of ~7 days ⚡ (Shaanxi History Museum is free and the
     hardest slot in Xi'an — reserve the minute it opens or take the paid Tang mural
     ticket). Put the flagship on a **weekday**; the China test reversed its route
     to land the Wall on a Monday and the Forbidden City on a Tuesday for this reason.
- **12306 works only in a browser for foreign users** (12306.cn/en; register with
  passport, verification once — sometimes at the station window; foreign
  Visa/Mastercard accepted since 2023 ⚡). Trip.com resells with a small fee and takes
  any card — the fallback when 12306 rejects the card. No 12306 MCP → the browser
  pane, per data-sources.md.
- **The Great Firewall shapes the plan.** Google Maps/Search/Gmail/Drive, WhatsApp,
  Instagram, X and most Western news are blocked; **every Google Maps deep link the
  skill emits is dead on the ground in China**. Three-part fix, all in the plan:
  (a) **roaming eSIM/SIM from home** (Airalo/Holafly-type or the home carrier's
  roaming) — traffic tunnels via the home network so Google works; a **local China
  SIM or hotel Wi-Fi does not**; put the eSIM at the top of the checklist;
  (b) build the map links with `route_tools.py links --provider amap` (or `apple` —
  Apple Maps works in China on Amap data) — see navigation.md "Google Maps is
  unavailable in some destinations"; (c) **the trip KML in Organic Maps** (offline,
  no network at all) is the hard fallback and goes into the footer of every China
  plan. Name 高德 (Amap, has an English mode ⚡) and 百度 as the local apps; Google
  Translate is blocked too — Apple Translate / an offline pack.
- **Payment**: Alipay and WeChat Pay accept a **foreign Visa/Mastercard/Amex** bound
  in the app (International version: single payment ≤ US$5,000, ~3% fee above ¥200
  ⚡) — set both up before departure and test with a small top-up. Foreign cards at
  POS terminals are rare outside international hotels; keep some cash (legal tender,
  taxis and small vendors must accept it) from a Bank of China / ICBC ATM. Metro:
  the Alipay/WeChat transit code or a Yikatong (Beijing) card; Didi has an English
  mode inside Alipay.
- **Winter opening hours switch in mid-November** — a real collision the holiday API
  can't see: the Forbidden City goes to winter hours on **1 Nov** (last entry
  ~15:40 ⚡); the **Terracotta Army and Mutianyu switch on 16 Nov** (closing an hour
  earlier ⚡); many parks and gardens follow. A trip straddling those dates has two
  sets of hours — put the switch date on the day cards, and sunset (17:00 in
  Beijing by mid-Nov) closes outdoor sights before the ticket does.
- **HSR practicalities**: no checked luggage — one big suitcase per person fits the
  end-of-carriage racks (first come), the overhead takes ~24"; **airport-style
  security X-ray at the station entrance plus a passport ID gate** (foreign passports
  usually go through the **manned** lane, not the e-gate ⚡) — arrive 45-60 min
  before departure, and note that stations are enormous (Beijing West, Xi'an North:
  10-15 min walk gate to platform). Boarding gates close ~5 min before departure.
- Holidays: **National Day Golden Week 1-7 Oct** and Spring Festival are the two
  weeks not to be in China as a tourist; nager.at lists them, but the shifted
  working days (weekend make-up workdays) around them are not obvious — check the
  State Council notice ⚡. Beijing/Xi'an in November: dry, cold, occasional smog days.

## General route math
- 10-15 days ≈ 8-13 usable days ≈ 2-4 bases; 2-3 bases beats 4 for almost everyone.
- Every hotel change costs ~half a day. Every intercity move costs its duration + 2 h.
