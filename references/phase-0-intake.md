# Phase 0 — Intake (the procedure)

Read this at the start of Phase 0, before you decide whether to ask the user anything.
SKILL.md Phase 0 is the contract — inputs, outputs, and the gates that decide pass/fail;
this file is the whole procedure it points at: what counts as a core fact, how origin
is inferred, the intake message format and its rules, what goes into `prefs`, the
picture-capability check, the style line and the plan language.

Inputs: the user's request (and anything said earlier in the conversation). Outputs:
the plan's top-level `prefs` block and `lang`, the picture mode (`prefs.pictures`), the
assumptions block for checkpoint (a) — and at most one intake message.

## Read the request first — one message, or none

**Read the request before deciding whether to ask anything.** Most requests already carry
what matters — "帮我安排今年 10.1 到 10.7 的德国之旅" has the destination and the dates,
and gets **zero questions**: infer the rest, list the assumptions in one block at the top
of checkpoint (a), and move. Ask only when a *core* fact is missing **and** cannot be
inferred — and then ask for everything in ONE message in the **intake format** below,
under four rules: (1) core first, optional after; (2) **only the items the user has not
already answered** — anything stated in the request (destination, dates, party, "自驾",
a style name, a budget) is settled and must not reappear as a question; (3) **each
optional line carries its default**; (4) **one "all defaults" escape hatch** (the 💡 line).

## Core and optional facts

**Core** — must be known or defensibly assumed:
- **Origin** (city/airport). Missing → infer from the conversation language, the user's
  locale/timezone or anything said earlier, pick that city's own international airport
  (language or locale alone names a country, not a city: take that country's largest
  international gateway — Brazil → São Paulo GRU, Mexico → MEX, Japan → Tokyo HND / NRT,
  mainland China → Shanghai PVG — unless a city was mentioned, and say so) and state it
  as an assumption; it costs one line to fix at checkpoint (a) and a whole round trip to
  ask. Genuinely unguessable → it is the one core question.
  A city named anywhere in the request ("我住在圣保罗", "from Toronto") overrides the
  language inference: a Chinese-language request from someone living in São Paulo
  departs GRU, never PVG. When a city is known, the hub is *that city's* main
  international airport, not the country's biggest — the ones that recur:
  São Paulo GRU (GIG is Rio) · Buenos Aires EZE · Mexico City MEX ·
  Shanghai PVG · Beijing PEK / PKX · Guangzhou CAN · Shenzhen SZX · Hong Kong HKG ·
  Taipei TPE · Singapore SIN · Seoul ICN · Tokyo HND / NRT · Sydney SYD · Melbourne MEL ·
  Toronto YYZ · New York JFK / EWR · London LHR · Paris CDG · Frankfurt FRA · Dubai DXB.
  A city not on this line: look its airport up; never guess it from the country.
- **Destination** (country, city or a shortlist). Missing → ask; nothing to plan without it.
- **When / how long** (dates, or a duration + rough month + flexibility). Missing → ask.
- **Page style** — one of the eight themes (Phase 6). Default: **illustrated 插画版**.
  Before you mention styles at all, run the **picture-capability check** below — its
  result decides what you say about pictures.

**Optional** — ask them in the same message only when you are already asking; never
send a message just for these. Unanswered → default, and the assumptions block says so:
- travel style: self-drive · group tour · public transport + walking (default: public
  transport, or self-drive where the destination is car-first — Phase 3 §Driving legs)
- lodging habit: hotel · hostel · B&B / guesthouse · apartment · ryokan/onsen-style
  stays, and the band (default: mid-range hotel, refundable)
- scenery taste: scenery/nature · city · beach · forest · lake · mountain (default: read
  from the destination + interests)
- party size & mobility (default: 2 adults, no kids) · budget style or number (mid) ·
  interests ranked (food/history/nature/anime/hiking/shopping/photography/nightlife) ·
  pace 2/3/4 anchors per day (3) · ±day flexibility (±2) · passport nationality
  (visa! infer from origin, state it) · locked must-sees.

## The intake message

**Intake format** (user's language; markdown; full zh/en samples in
references/output-template.md §Intake message). Keep it to one screen:

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

Rules for the block: numbering runs continuously over whatever is left; a heading with
nothing under it is dropped; the ℹ️ line appears only in stock mode (Picture-capability
check below), the 💡 line only when at least one optional item is shown; a guessed core
value is asked as a confirmation ("我猜是 X,对吗?"), not as an open question; never
more than one message, never a follow-up "just one more thing". English sample:
output-template.md. The same facts, answered or defaulted, go into `prefs` next.

## `prefs` and the assumptions block

Write what you learned or assumed into the plan's top-level `prefs` block
(`assets/plan.example.json`: `theme`, `pictures`, `travel_style`, `lodging`, `scenery`,
`pace`, `budget`, and `notes` — the inferred values in one line, e.g. "assumed origin
PVG (zh request, no origin given)"; the assumptions block at checkpoint (a) is written
from it) so Phases 2-6 read one place and a later replan does not re-ask.

## Picture-capability check

**Picture-capability check** — silent, once, before styles come up:
1. You have a **native image-generation tool** → bespoke art for this trip, nothing to
   configure (`prefs.pictures = "native"`).
2. Else `<skill>/themes/.auth_header` exists (`test -s`; never read, print or copy it) →
   `gen.py` over OpenRouter with the user's key (`"key"`).
3. Neither → **the page still ships in a theme** (Phase 6 — a plain text page is never
   the deliverable): the built-in **stock kit** (`themes/assets/stock/`) supplies the
   pictures (`"stock"`). Tell the user once — in the intake message if you are sending
   one, otherwise in the assumptions block at checkpoint (a): *"No image generator is
   available in this session, so the page will use the built-in stock illustrations —
   still a designed page, just less bespoke. If you have an OpenRouter key, put it in
   `themes/.auth_header` (one line: `Authorization: Bearer <key>`) and tell me; then I
   generate the art for this trip."* Never ask for a key in the chat, never handle one.
   `prefs.pictures` records how the pictures were **actually** produced, not what the
   check found: a session that ran `stock_art.py` sets it to `stock` before rendering,
   whatever `.auth_header` said — the chat summary's picture notice keys off it.
4. **Stock mode covers two themes only**: complete for **illustrated** (default), works
   for **clay** (built-in terrain kit); the other six themes need generated pictures —
   a user asking for one of those in stock mode is told so and offered illustrated instead.

## Style line and plan language

Style, when you do ask, is one line: the eight names with the showcase link
(https://skywain.github.io/trip-planner-skill/; offline: render
`themes/render_picker.py`), "skip = illustrated". Set the plan's top-level `"lang"` (`zh` | `en`,
output-template.md §Plan language) from the language the user asked in — the rendered
pages' UI follows it; `--lang` overrides. `lang` covers the page chrome only: **every
content string you write into the plan — day titles, notes, tips, checklist rows,
decisions, hotel blurbs — is in the user's language too.** The research sources are
mostly English and will drag your prose toward English if you let them; a zh user
receiving an English page is a shipped bug, not a style choice (self-check row, Phase 6).

## Exit criteria — tick every line before Phase 1

- [ ] At most one intake message was sent, in the intake format, and only for a core
      fact that was missing AND could not be inferred; nothing the user already stated
      was asked again; no follow-up question.
- [ ] Origin, destination, dates / duration and page style are known or defensibly
      assumed, each assumption written for the checkpoint (a) block.
- [ ] `prefs` carries theme · pictures · travel_style · lodging · scenery · pace ·
      budget · notes (the inferred values in one line); `lang` is set from the user's
      language.
- [ ] The picture-capability check ran silently before styles were mentioned;
      `prefs.pictures` ∈ native | key | stock, and in stock mode the user was told once
      with the exact notice; no key was asked for or handled in chat; a non-illustrated /
      clay theme requested in stock mode was redirected to illustrated.
