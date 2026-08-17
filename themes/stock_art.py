#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stock_art.py — the PICTURE side of art.json, drawn from the built-in stock kit.

For a session with no image generation and no OpenRouter key (SKILL.md Phase 0's
capability check → `prefs.pictures = "stock"`) the deliverable is still a themed
page, so the pictures come from `themes/assets/stock/` — region cover paintings
plus world-landmark and generic-scene cut-outs in the illustrated gouache style —
topped up with the same-country pictures the shared library already ships
(`index.json` → `library`) and the generic plane / train / bus / balloon.

    python3 themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
    python3 themes/render_theme2.py plan.geo.json --art plan.art.json \
            --assets themes/assets/stock -o trip-illustrated.html

**`--assets themes/assets/stock` is not optional at render time.** `data_uri()`
searches `themes/assets/` but not its sub-folders, so without the flag every
stock stem resolves to `""` and the page renders imageless without one error —
the render command this script prints when it is done already carries the flag.

What it fills, what stays yours
    fills   the cover painting, one cut-out per day, the endcap picture, the
            stock notice (`end.fine` + `cover.credit`), and for clay the terrain
            zones + day figurines.
    yours   every WORD: `cover.kick`/`kick_en`, the cover title (`zh`/`en`/`sub`),
            each day's 4-character `theme`, `end.line`. They are written as ""
            and listed in `_stock_todo` — shipping the empties is a defect.
    says so The notice must stay visible: the page fine print carries the full
            string, `cover.credit` a short form (the one slot all eight themes
            print), and the chat reply must say the same line once.

How a picture is chosen
    cover   `library[cc].cover` when the destination country has a hand-drawn
            one, else `stock-cover-<country_archetype[cc]>`; multi-country trips
            take the country with the most days. Countries come from the plan's
            own words (`trip`, `meta.route`, `legs`, `days[].city`,
            `days[].stops[].name`) matched against `index.json.country_names`
            (Latin on word boundaries, CJK as substrings, longest name wins),
            minus the origin — and a country named in a single stop is ignored,
            or Istanbul's Egyptian Bazaar would move the trip to Egypt. Nothing
            recognised → a WARN listing the fields that were read, the neutral
            cover, and `--country ISO2` as the fix.
    days    keyword score per cut-out over the day's city / label / stop names /
            block text; a landmark whose `countries` include a destination
            outranks a generic scene, ties prefer the shared library's
            same-country pictures, a stem never repeats on consecutive days and
            repeats are spread. A day that starts at an airport gets the plane
            and one that starts on a train the train — unless the day is really
            about a place ("the regional train to Füssen, then Neuschwanstein"),
            which keeps its own picture. A day that matched nothing rotates
            through the neutral pool.

Usage: python3 themes/stock_art.py <plan.geo.json> [--theme illustrated|clay]
       [--lang zh|en] [--country ISO2] [--index PATH] [-o OUT] [--force]
Default output is `<plan stem>.art.json` beside the plan — the sidecar the
renderers pick up on their own; an existing file is never overwritten without
`--force`. The day → stem table goes to stderr, the output path to stdout.
"""
import argparse
import datetime
import json
import pathlib
import re
import sys
import unicodedata

from theme_common import load_plan

HERE = pathlib.Path(__file__).parent
ASSETS = HERE / "assets"
STOCK = ASSETS / "stock"
DEFAULT_INDEX = STOCK / "index.json"

THEMES = ("illustrated", "clay")

# The full notice lives in index.json (one canonical wording, SPEC). `credit` is
# a thin one-line slot in every theme, so it takes the first clause only.
NOTICE_SHORT = {
    "en": "Pictures: built-in stock kit (no image generator was available).",
    "zh": "图片来自内置素材库(本次未接入生图能力)。",
}

# A day that matched nothing rotates through these, so a text-only trip still
# gets a plausible picture instead of the same one eight times.
NEUTRAL_POOL = ("stock-old-town-square", "stock-city-park", "stock-cafe",
                "stock-viewpoint", "stock-market", "stock-harbour")

# archetype → clay terrain kind (render_clay2.TERRAIN's neutral, geography-free
# kinds only — the four place-bound US kinds never travel to another trip).
CLAY_ZONE = {
    "tropical-beach": "coast", "mediterranean-coast": "coast",
    "nordic-fjord": "coast", "desert-medina": "desert",
    "rainforest": "forest", "alpine-lake": "lake", "savanna": "plain",
}
CLAY_ZONE_DEFAULT = "ridge"
CLAY_FLY, CLAY_TOUR, CLAY_LAST = "clay-plane", "clay-bus-solo", "clay-luggage"
CLAY_ALTERNATE = ("clay-balloon", "clay-signpost")

# The shared library's stems (index.json → library) carry no keywords of their
# own, so they are matched on the words their name already says, plus these
# aliases for the ones a plan writes differently (and never in English).
LIB_ALIASES = {
    "japan-gate": ["kaminarimon", "sensoji", "sensō-ji", "浅草", "雷门", "浅草寺"],
    "japan-torii": ["torii", "fushimi", "inari", "鸟居", "伏见", "稻荷"],
    "japan-pagoda": ["pagoda", "五重塔", "塔"],
    "japan-maple": ["maple", "autumn leaves", "koyo", "红叶", "枫叶", "紅葉"],
    "japan-bamboo": ["bamboo", "arashiyama", "竹林", "岚山", "嵐山"],
    "japan-onsen": ["onsen", "hot spring", "ryokan", "温泉", "泡汤", "旅馆"],
    "japan-stage": ["kiyomizu", "清水寺", "舞台"],
    "japan-stall": ["yatai", "street food", "nakamise", "小吃", "屋台", "商店街"],
    "japan-teahouse": ["teahouse", "tea ceremony", "machiya", "茶屋", "茶室"],
    "japan-lantern": ["lantern", "chochin", "灯笼", "提灯"],
    "japan-ropeway": ["ropeway", "cable car", "hakone", "索道", "缆车", "箱根"],
    "japan-train": ["shinkansen", "bullet train", "新干线", "新幹線", "列车"],
    "turkey-hagia": ["hagia sophia", "ayasofya", "圣索菲亚", "聖索菲亞"],
    "turkey-bazaar": ["bazaar", "grand bazaar", "spice market", "巴扎", "大巴扎", "香料市场"],
    "turkey-chimney": ["fairy chimney", "goreme", "göreme", "cappadocia",
                       "精灵烟囱", "仙人烟囱", "格雷梅", "卡帕多奇亚"],
    "turkey-pamukkale": ["pamukkale", "hierapolis", "travertine", "棉花堡", "希拉波利斯"],
    "turkey-ferry": ["bosphorus", "ferry", "博斯普鲁斯", "渡轮", "海峡"],
    "turkey-underground": ["underground city", "derinkuyu", "kaymakli", "地下城"],
    "turkey-balloon": ["hot air balloon", "balloon", "热气球", "熱氣球", "气球"],
    "liberty": ["statue of liberty", "liberty island", "自由女神"],
    "golden-gate": ["golden gate", "金门大桥", "金門大橋"],
    "diamond-head": ["diamond head", "waikiki", "钻石头山", "威基基"],
    "kilauea": ["kilauea", "volcanoes national park", "lava", "基拉韦厄", "火山口"],
    "prismatic": ["grand prismatic", "yellowstone", "geyser", "大棱镜", "黄石", "间歇泉"],
    "teton": ["teton", "jackson hole", "提顿"],
    "yosemite": ["yosemite", "half dome", "el capitan", "优胜美地", "优诗美地"],
    "stadium": ["stadium", "ballpark", "game", "球场", "球赛", "体育场"],
    "tiananmen": ["tiananmen", "forbidden city", "天安门", "故宫", "紫禁城"],
    "bus": ["coach", "tour bus", "day tour", "包车", "大巴", "一日游"],
}

# Travel-day signals, read from the FIRST TWO blocks of a day only: that is the
# difference between "the day starts at an airport" (a travel day) and "there is
# a flight somewhere in the notes" (not one). 起飞 is deliberately absent — a
# Cappadocia balloon launch field (起飞场) is not a flight.
FLY_RE = re.compile(r"airport|flight|✈|机场|機場|航班|飞机|飛機|登机|登機|值机|值機", re.I)
RAIL_RE = re.compile(r"\btrain\b|railway|shinkansen|bullet train|"
                     r"高铁|高鐵|火车|火車|列车|列車|新干线|新幹線|动车|動車", re.I)
TOUR_RE = re.compile(r"guided tour|day tour|day trip|excursion|small-group|"
                     r"跟团|一日游|包车|包車|团队游|导游", re.I)

# Phrases that carry a country name but are not that country. Word boundaries
# already save us from japanese / Indiana / Chinatown; CJK has no boundaries to
# work with, and these two Istanbul names are in every itinerary of the city:
# 埃及香料市场 = the Egyptian (Spice) Bazaar, 苏丹艾哈迈德 = Sultanahmet. `Island`
# is the German/Icelandic name of Iceland and reads Museum Island as a country.
FALSE_FRIENDS = ("new mexico", "new england", "little india", "india pale ale",
                 "museum island", "long island", "coney island", "rhode island",
                 "easter island", "island hopping",
                 "埃及香料", "埃及市场", "埃及市集", "苏丹艾哈迈德", "蘇丹艾哈邁德")

# CJK ideographs + kana: a keyword in these scripts has no word boundary to hang
# a \b on and is matched as a plain substring. _LETTER is what a Latin keyword
# may not be glued to (so "oman" misses "Romania"), _JOIN what a space inside a
# keyword may become (so "mont saint michel" catches "Mont Saint-Michel").

_CJK_RE = re.compile(r"[⺀-鿿豈-﫿ｦ-ﾟ]")
_LETTER = r"0-9a-zÀ-ɏ"
_JOIN = r"[\s\-‐-―_/,.'’·・]*"

# scoring weights per source of text
W_PLACE, W_STOP, W_BLOCK, W_NOTE = 3, 2, 2, 1
W_ANCHOR = 3                     # an anchor block is what the day is FOR
LANDMARK_MIN = 2                 # a landmark needs more than a passing note
MIN_DAYS = 2                     # days a country needs to count without strong evidence
DECAY = 0.55                     # score × DECAY per previous use, to spread repeats
TRAVEL_KEEP = 9.0                # above this a travel day keeps its own picture
BONUS_LIBRARY = 0.6              # tie-break: the hand-drawn same-country picture
BONUS_UNUSED = 0.3               # tie-break: something we have not used yet
FEATURE_MAX = 3                  # illustrated: how many wide "feature" cards


def warn(msg):
    sys.stderr.write("WARN %s\n" % msg)


# --------------------------------------------------------------- matching --
def _is_cjk(s):
    return bool(_CJK_RE.search(s))


def fold(text):
    """Lower-case and strip diacritics — the one normalisation both sides get.

    Plans write the places as the places are spelled: `Teotihuacán`, `México`,
    `Göreme`, `Café`. Keyword lists cannot carry every accented spelling, so both
    sides are folded to bare letters before matching (a keyword list that DOES
    carry the accents still works — it folds to the same bytes). CJK is not
    affected: NFKD only normalises compatibility ideographs and full-width forms,
    which is what we want anyway.
    """
    if not text:
        return ""
    d = unicodedata.normalize("NFKD", text)
    return "".join(c for c in d if not unicodedata.combining(c)).lower()


def _pattern(phrase):
    """Compiled matcher for a Latin phrase, or None for a CJK one (substring).

    Latin keywords must match on WORD BOUNDARIES: plain `in` finds "oman" inside
    "Romania", "iran" inside "Tirana" and "fuji" inside "Fujian". Spaces in a
    keyword match any run of separators, so "mont saint michel" also catches
    "Mont Saint-Michel", and a trailing plural is allowed — the keyword lists are
    singular but plans write "the petrified waterfalls" and "two markets".
    """
    if _is_cjk(phrase):
        return None
    toks = [re.escape(t) for t in re.split(r"[\s\-_/]+", phrase) if t]
    if not toks:
        return None
    return re.compile("(?<![%s])%s(?:e?s)?(?![%s])"
                      % (_LETTER, _JOIN.join(toks), _LETTER))


def _count(text, phrase, pat, cap=2):
    """How often `phrase` occurs in the already-lowercased `text` (capped)."""
    if not text:
        return 0
    if pat is None:
        n, i = 0, text.find(phrase)
        while i >= 0 and n < cap:
            n += 1
            i = text.find(phrase, i + len(phrase))
        return n
    return min(cap, sum(1 for _ in pat.finditer(text)))


def _spans(text, phrase, pat):
    if pat is None:
        out, i = [], text.find(phrase)
        while i >= 0:
            out.append((i, i + len(phrase)))
            i = text.find(phrase, i + len(phrase))
        return out
    return [m.span() for m in pat.finditer(text)]


class CountryIndex:
    """`country_names` turned into a longest-match-wins name → ISO2 lookup."""

    def __init__(self, country_names):
        rows = []
        for cc, names in (country_names or {}).items():
            for n in names or []:
                n = fold((n or "").strip())
                if len(n) >= 2:
                    rows.append((n, cc.upper(), _pattern(n)))
        # longest first: 刚果民主共和国 must claim its span before 刚果 sees it
        rows.sort(key=lambda r: -len(r[0]))
        self.rows = rows

    def hits(self, text):
        """{ISO2: matches} in `text`; overlapping shorter names are dropped."""
        if not text:
            return {}
        low = fold(text)
        for bad in FALSE_FRIENDS:
            if bad in low:
                low = low.replace(bad, " " * len(bad))
        claimed, out = [], {}
        for name, cc, pat in self.rows:
            for a, b in _spans(low, name, pat):
                if any(a < d and c < b for c, d in claimed):
                    continue
                claimed.append((a, b))
                out[cc] = out.get(cc, 0) + 1
        return out


class Candidate:
    """One pickable picture: a stock cut-out, a library stem or a generic prop."""

    def __init__(self, stem, kind, countries, keywords, source):
        self.stem = stem
        self.kind = kind               # "landmark" | "scene"
        self.countries = [c.upper() for c in (countries or [])]
        self.source = source           # "stock" | "library" | "generic"
        seen, self.keys = set(), []
        for k in keywords:
            k = fold(k)
            if k and k not in seen:
                seen.add(k)
                self.keys.append((k, _pattern(k)))
        self.used = 0

    def score(self, buckets):
        """(score, [matched keywords]) over {weight: lowercased text}."""
        total, seen = 0.0, []
        for kw, pat in self.keys:
            hit = 0
            for w, text in buckets.items():
                n = _count(text, kw, pat)
                if n:
                    hit += n * w
            if hit:
                total += hit
                seen.append(kw)
        return total, seen


# ------------------------------------------------------------ plan reading --
def _s(v):
    return v if isinstance(v, str) else ""


def _blocks(day):
    """The day's timeline rows — `timeline` in our plans, `blocks` elsewhere."""
    for key in ("timeline", "blocks"):
        v = day.get(key)
        if isinstance(v, list):
            return [b for b in v if isinstance(b, dict)]
    return []


def day_buckets(day):
    """{weight: text} for one plan day — what the day is about, by loudness.

    The keys ARE the weights, so sources that weigh the same share one bucket
    (an anchor block is as loud as the city name, a stop name as loud as an
    ordinary block) and one keyword scan covers all of them.
    """
    parts = {W_PLACE: [], W_STOP: [], W_BLOCK: [], W_NOTE: []}
    for key in ("city", "label", "title", "theme"):
        parts[W_PLACE].append(_s(day.get(key)))
    for st in day.get("stops") or []:
        if isinstance(st, dict):
            parts[W_STOP].append(_s(st.get("name")))
    for b in _blocks(day):
        what = _s(b.get("what")) or _s(b.get("title"))
        parts[W_ANCHOR if b.get("kind") == "anchor" else W_BLOCK].append(what)
        parts[W_NOTE].append(_s(b.get("note")) or _s(b.get("notes")))
    parts[W_NOTE].append(_s(day.get("ribbon")))
    return dict((w, fold(" · ".join(x for x in v if x))) for w, v in parts.items())


def day_country_text(day):
    """Only the place-naming fields — a note about the flight home must not put
    the origin country back into the day's country."""
    bits = [_s(day.get("city")), _s(day.get("label")), _s(day.get("title"))]
    for st in day.get("stops") or []:
        if isinstance(st, dict):
            bits += [_s(st.get("name")), _s(st.get("query"))]
    return " · ".join(b for b in bits if b)


def plan_country_text(plan):
    """[(label, text)] — where the trip says which country it is about.

    `meta.party` is deliberately absent: it names the travellers' PASSPORTS
    ("2 名中国护照持有者"), which is the one country the trip is not going to.
    `brief` is absent for the same reason (visa prose names the passport country
    and every neighbour); it is read only by the last-resort pass in
    detect_countries() when nothing else named a country at all.
    """
    meta = plan.get("meta") if isinstance(plan.get("meta"), dict) else {}
    out = []
    for label, v in (("trip", plan.get("trip")), ("meta.route", meta.get("route")),
                     ("meta.country", meta.get("country")),
                     ("meta.countries", meta.get("countries"))):
        if isinstance(v, str) and v:
            out.append((label, v))
        elif isinstance(v, list):
            out.append((label, " · ".join(str(x) for x in v)))
    for i, lg in enumerate(plan.get("legs") or []):
        if isinstance(lg, dict):
            out.append(("legs[%d]" % i, " · ".join(
                _s(lg.get(k)) for k in ("from", "to", "type"))))
    return out


def brief_country_text(plan):
    brief = plan.get("brief") if isinstance(plan.get("brief"), dict) else {}
    return " · ".join(str(v) for v in brief.values() if isinstance(v, str))


def origin_text(plan):
    """Where the trip STARTS — excluded from the destination set."""
    meta = plan.get("meta") if isinstance(plan.get("meta"), dict) else {}
    prefs = plan.get("prefs") if isinstance(plan.get("prefs"), dict) else {}
    bits = [_s(prefs.get("notes"))]
    legs = [lg for lg in (plan.get("legs") or []) if isinstance(lg, dict)]
    if legs:
        bits += [_s(legs[0].get("from")), _s(legs[-1].get("to"))]
    route = _s(meta.get("route"))
    if route:
        bits.append(re.split(r"→|->|—>|➜|>", route)[0])
    return " · ".join(b for b in bits if b)


def is_fly_day(day):
    if any(isinstance(s, dict) and _s(s.get("mode")).lower() == "fly"
           for s in day.get("stops") or []):
        return True
    head = " · ".join(_s(b.get("what")) or _s(b.get("title"))
                      for b in _blocks(day)[:2])
    return bool(FLY_RE.search(head))


def is_rail_day(day):
    head = " · ".join(_s(b.get("what")) or _s(b.get("title"))
                      for b in _blocks(day)[:2])
    return bool(RAIL_RE.search(head))


def is_tour_day(day, travel_style):
    text = " · ".join(day_buckets(day).values())
    if TOUR_RE.search(text):
        return True
    return (travel_style == "group-tour"
            and any(isinstance(s, dict) and _s(s.get("mode")).lower() in ("bus", "drive")
                    for s in day.get("stops") or []))


# ------------------------------------------------------------------ assets --
def asset_exists(stem):
    """Does any webp variant of `stem` exist where the renderers will look?"""
    if not stem:
        return False
    for d in (STOCK, ASSETS):
        if (d / (stem + ".webp")).exists() or (d / (stem + ".cut.webp")).exists():
            return True
        if any(d.glob(stem + ".*.webp")):
            return True
    return False


# ------------------------------------------------------------- the picking --
def detect_countries(plan, ci, forced):
    """(dest, per_day, order, notes) — the ISO2 codes the plan is about.

    A country counts as a destination on TWO kinds of evidence, because one
    mention inside one stop name is noise, not a destination: Istanbul's
    苏丹艾哈迈德 (Sultanahmet) reads as Sudan and its 埃及香料市场 (Egyptian
    Bazaar) as Egypt, and a Mexico City day walks down calle Argentina past the
    Jamaica flower market.

      strong   the trip title, `meta.route`, `meta.country`/`countries`, the
               flight legs — a country named there is a destination outright
      days     a country named in ≥ MIN_DAYS days' city / label / stop names

    The origin (first leg's `from`, last leg's `to`, the head of `meta.route`,
    `prefs.notes`) is then subtracted, unless that would empty the set. If
    nothing at all was found, one last pass reads `brief` too; still nothing →
    the caller warns and falls back to a neutral cover, and `--country ISO2` is
    the fix.

    `per_day` is the country each day sits in — carried forward over days that
    name none, so "day 6: 格雷梅" keeps the day in Turkey.
    """
    notes = []
    days = [d for d in (plan.get("days") or []) if isinstance(d, dict)]
    if forced:
        dest = list(forced)
        notes.append("--country %s (given)" % ",".join(dest))
        return dest, [dest[0] for _ in days], dest, dest, notes

    order, strong = [], []
    for label, text in plan_country_text(plan):
        for cc in ci.hits(text):
            if cc not in order:
                order.append(cc)
            if cc not in strong:
                strong.append(cc)
                notes.append("%s → %s" % (label, cc))

    day_hits = []
    for d in days:
        day_hits.append(set(ci.hits(day_country_text(d))))
    tally = {}
    for hs in day_hits:
        for cc in hs:
            tally[cc] = tally.get(cc, 0) + 1
            if cc not in order:
                order.append(cc)
    repeated = [cc for cc in order if cc not in strong and tally.get(cc, 0) >= MIN_DAYS]
    for cc in repeated:
        notes.append("days×%d → %s" % (tally[cc], cc))
    thin = [cc for cc in order if cc not in strong and cc not in repeated]
    if thin:
        notes.append("ignored %s (named once)" % ",".join(thin))

    found = [cc for cc in order if cc in strong or cc in repeated]
    origin = set(ci.hits(origin_text(plan)))
    dest = [cc for cc in found if cc not in origin] or list(found)
    if origin & set(found):
        notes.append("origin %s dropped" % ",".join(sorted(origin & set(found))))
    if not dest:
        # nothing named a country: allow the visa/brief prose to speak after all
        for cc in ci.hits(brief_country_text(plan)):
            if cc not in origin:
                dest.append(cc)
                order.append(cc)
                notes.append("brief → %s" % cc)

    per_day, last = [], None
    for hs in day_hits:
        here = [cc for cc in hs if cc in dest]
        if here:
            last = sorted(here, key=lambda c: dest.index(c))[0]
        per_day.append(last)
    # days before the first named country belong to the first country named after
    first = next((cc for cc in per_day if cc), dest[0] if dest else None)
    return dest, [cc or first for cc in per_day], order, strong, notes


def cover_country(dest, per_day, order, strong):
    """The country the cover paints: most days wins, but only among the ones
    the trip actually claims (title / route / legs) when it claims any — a
    stop called 埃及香料市场 must not repaint an Istanbul trip as Egypt."""
    if not dest:
        return None
    pool = [cc for cc in dest if cc in (strong or [])] or list(dest)
    if len(pool) == 1:
        return pool[0]
    tally = {}
    for cc in per_day:
        if cc in pool:
            tally[cc] = tally.get(cc, 0) + 1
    if not tally:
        return pool[0]
    best = max(tally.values())
    return sorted([c for c in tally if tally[c] == best],
                  key=lambda c: order.index(c) if c in order else 99)[0]


def neutral_cover(idx, plan):
    """No country: the modern skyline only when the trip reads urban.

    Scored over the WHOLE plan (the title, the route and every day's own words) —
    a trip whose title says nothing still says "rooftop bar, observation deck,
    CBD" in its days, and that is the only evidence there is.
    """
    text = fold(" ".join([_s(plan.get("trip"))]
                         + [t for _, t in plan_country_text(plan)]
                         + [" ".join(day_buckets(d).values())
                            for d in (plan.get("days") or []) if isinstance(d, dict)]))
    city = nature = 0
    for cov in idx.get("covers") or []:
        arch = cov.get("archetype")
        if arch not in ("modern-skyline", "alpine-lake", "nordic-fjord",
                        "rainforest", "savanna", "tropical-beach"):
            continue
        n = 0
        for kw in cov.get("keywords") or []:
            kw = fold(kw)
            n += _count(text, kw, _pattern(kw))
        if arch == "modern-skyline":
            city += n
        else:
            nature += n
    return "stock-cover-modern-skyline" if city > nature else "stock-cover-alpine-lake"


def pick_cover(idx, plan, dest, per_day, order, strong):
    """(stem, why) for the full-bleed cover painting."""
    cc = cover_country(dest, per_day, order, strong)
    lib = (idx.get("library") or {}).get(cc or "", {})
    if cc and lib.get("cover"):
        return lib["cover"], "library %s" % cc
    arch = (idx.get("country_archetype") or {}).get(cc or "")
    if arch:
        return "stock-cover-%s" % arch, "%s → %s" % (cc, arch)
    if cc:
        warn("no archetype for country %s in index.json — using the neutral cover" % cc)
    return neutral_cover(idx, plan), "neutral (no country detected)"


def build_candidates(idx, dest):
    """Every picture this trip may pick from, by stem."""
    out = {}
    for c in idx.get("cutouts") or []:
        stem, ccs = c.get("stem"), c.get("countries") or []
        if not stem:
            continue
        if c.get("kind") == "landmark" and ccs and not (set(ccs) & set(dest)):
            continue                                  # Eiffel Tower, but in Japan
        out[stem] = Candidate(stem, c.get("kind") or "scene", ccs,
                              c.get("keywords") or [], "stock")
    lib = idx.get("library") or {}
    for cc in dest:
        for stem in (lib.get(cc, {}) or {}).get("cutouts") or []:
            if stem in out:
                continue
            words = list(LIB_ALIASES.get(stem, []))
            tail = re.sub(r"^(?:japan|turkey|china|clay|us)-", "", stem)
            words.append(tail.replace("-", " "))
            out[stem] = Candidate(stem, "scene", [cc], words, "library")
    for name, stem in (idx.get("generic") or {}).items():
        if not stem or stem in out or name in ("plane", "train"):
            continue                                  # plane/train are forced picks
        out[stem] = Candidate(stem, "scene", [], LIB_ALIASES.get(stem, [name]), "generic")
    return out


def score_day(cands, buckets, cc, prev):
    """The best candidate for one day: ((tier, score), candidate, [keywords]).

    A landmark whose country the trip visits outranks any generic scene, ties go
    to the shared library's same-country picture and then to something unused,
    and every previous use halves a stem's score so a ten-day trip does not run
    the same market picture five times. The day before's stem is off the table.
    """
    best = None
    for cand in cands.values():
        if cand.stem == prev:
            continue
        raw, seen = cand.score(buckets)
        if raw <= 0:
            continue
        tier = 1 if (cand.kind == "landmark" and raw >= LANDMARK_MIN) else 0
        bonus = 0.0
        if cand.source == "library" and cc and cc in cand.countries:
            bonus += BONUS_LIBRARY
        if not cand.used:
            bonus += BONUS_UNUSED
        key = (tier, raw * (DECAY ** cand.used) + bonus)
        if best is None or key > best[0]:
            best = (key, cand, seen)
    return best


def pick_days(idx, plan, dest, per_day):
    """[(date, stem, why, tier)] — one picture per day, in plan order."""
    cands = build_candidates(idx, dest)
    generic = idx.get("generic") or {}
    plane, train = generic.get("plane") or "plane", generic.get("train") or ""
    days = [d for d in (plan.get("days") or []) if isinstance(d, dict)]
    picks, prev, neutral_i = [], None, 0
    for i, day in enumerate(days):
        date = _s(day.get("date"))
        best = score_day(cands, day_buckets(day),
                         per_day[i] if i < len(per_day) else None, prev)
        # A travel day takes the plane / the train — but only when the day is
        # ACTUALLY just travel. "Regional train to Füssen, then Neuschwanstein"
        # starts with a train and is still the castle day; the brief's own
        # acceptance case. So a landmark, or any strong score, keeps its picture.
        strong_day = best is not None and (best[0][0] or best[0][1] >= TRAVEL_KEEP)
        if not strong_day:
            fly, rail = is_fly_day(day), (train and is_rail_day(day))
            if fly or rail:
                picks.append((date, plane if fly else train,
                              "fly day → generic.plane" if fly
                              else "rail day → generic.train", 0))
                prev = None      # a plane two days running is still the truth
                continue
        if best is None:
            stem = NEUTRAL_POOL[neutral_i % len(NEUTRAL_POOL)]
            neutral_i += 1
            if stem == prev:
                stem = NEUTRAL_POOL[neutral_i % len(NEUTRAL_POOL)]
                neutral_i += 1
            picks.append((date, stem, "nothing matched → neutral pool", 0))
            prev = stem
            continue
        (tier, sc), cand, seen = best
        cand.used += 1
        why = "%s %.1f · %s" % (cand.kind if cand.source == "stock" else cand.source,
                                sc, ", ".join(seen[:4]))
        picks.append((date, cand.stem, why, tier))
        prev = cand.stem
    return picks


# ------------------------------------------------------------ art building --
def _rel(path):
    """The index path as the repo spells it — an art file travels with a trip and
    has no business carrying somebody's home directory."""
    try:
        return str(pathlib.Path(path).resolve().relative_to(HERE.parent))
    except ValueError:
        return str(path)


def common_block(dates, notice, notice_short, theme, index_path):
    days = dict((date, {"theme": "", "en": "", "mark": ""}) for date in dates if date)
    todo = ["cover.kick", "cover.kick_en", "themes.%s.cover.zh" % theme,
            "themes.%s.cover.en" % theme, "themes.%s.cover.sub" % theme,
            "days.*.theme", "days.*.en", "days.*.mark", "end.line"]
    art = {
        "schema": 1,
        "_note": ("Pictures picked by themes/stock_art.py from the built-in stock "
                  "kit (themes/assets/stock) — the words are still to be written: "
                  "every \"\" in _stock_todo. cover.credit and end.fine carry the "
                  "stock notice and must stay on the page (clay prints credit, not "
                  "end.fine); if you give the cover a poem and its source, keep the "
                  "notice line as well. Render with --assets themes/assets/stock or "
                  "the stock stems resolve to nothing."),
        "_stock": {
            "generated": datetime.date.today().isoformat(),
            "index": _rel(index_path),
            "theme": theme,
            "assets": "themes/assets/stock",
        },
        "_stock_todo": todo,
        "cover": {"kick": "", "kick_en": "", "credit": notice_short},
        "end": {"line": "", "fine": notice},
        "days": days,
    }
    return art


def illustrated_block(cover, picks, generic):
    days, feature = {}, []
    for date, stem, _, tier in picks:
        if not date:
            continue
        days[date] = {"hero": stem}
        if tier:
            feature.append(date)
    for date in feature[:FEATURE_MAX]:
        days[date]["feature"] = True
    return {
        "cover": {"zh": "", "en": "", "sub": "", "hero": cover},
        "end": {"hero": generic.get("plane") or "plane"},
        "days": days,
    }


def clay_block(idx, plan, per_day):
    """Terrain zones from the countries' archetypes + one figurine per day."""
    arch_of = idx.get("country_archetype") or {}
    days = [d for d in (plan.get("days") or []) if isinstance(d, dict)]
    prefs = plan.get("prefs") if isinstance(plan.get("prefs"), dict) else {}
    style = _s(prefs.get("travel_style"))

    zones, alt = [], 0
    for i, day in enumerate(days):
        cc = per_day[i] if i < len(per_day) else None
        kind = CLAY_ZONE.get(arch_of.get(cc or "", ""), CLAY_ZONE_DEFAULT)
        if not zones or zones[-1]["kind"] != kind:
            first = _s(day.get("date"))
            zones.append({"from_day": first or (i + 1), "kind": kind})
    if zones:
        zones[0]["from_day"] = 1                     # the first zone starts on day 1

    figs, rows, last_i = {}, [], len(days) - 1
    for i, day in enumerate(days):
        date = _s(day.get("date"))
        if not date:
            continue
        if is_fly_day(day):
            stem, why = CLAY_FLY, "fly day"
        elif is_tour_day(day, style):
            stem, why = CLAY_TOUR, "tour day"
        elif i == last_i:
            stem, why = CLAY_LAST, "last day"
        else:
            stem = CLAY_ALTERNATE[alt % len(CLAY_ALTERNATE)]
            why = "alternating"
            alt += 1
        figs[date] = {"figurine": stem}
        rows.append((date, stem, why))
    return ({"cover": {"zh": "", "en": "", "sub": "", "title_stem": ""},
             "zones": zones, "days": figs}, zones, rows)


# ------------------------------------------------------------------- report --
def report(theme, lang, idx, cover, cover_why, rows, notes, zones, out_path, plan_path):
    """The table the agent reads: what each day got and why (stderr)."""
    e = sys.stderr.write
    e("stock kit  v%s · %d covers · %d cut-outs · theme %s · lang %s\n"
      % (idx.get("version", "?"), len(idx.get("covers") or []),
         len(idx.get("cutouts") or []), theme, lang))
    if notes:
        e("countries  %s\n" % "; ".join(notes))
    if cover:
        e("cover      %-28s %s\n" % (cover, cover_why))
    what = "hero" if theme == "illustrated" else "figurine"
    for i, (date, stem, why) in enumerate(rows, 1):
        e("day %-2d %s %-28s %s\n" % (i, date or "?", stem, why))
    e("           (%s per day)\n" % what)
    if zones:
        e("zones      %s\n" % ", ".join("%s@%s" % (z["kind"], z["from_day"])
                                        for z in zones))
    e("notice     end.fine (full) + cover.credit (short), %s\n" % lang)
    render = "render_theme2.py" if theme == "illustrated" else "render_clay2.py"
    e("\nnext: python3 themes/%s %s --art %s \\\n"
      "        --assets themes/assets/stock -o trip-%s.html\n"
      % (render, plan_path, out_path, theme))
    e("      (--assets is required: data_uri() does not look inside "
      "themes/assets/stock on its own)\n")


# --------------------------------------------------------------------- main --
def default_out(plan_path):
    p = pathlib.Path(plan_path)
    stem = p.name
    for suf in (".geo.json", ".plan.json", ".json"):
        if stem.endswith(suf):
            stem = stem[: -len(suf)]
            break
    return p.with_name(stem + ".art.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("plan", help="plan.geo.json")
    ap.add_argument("--theme", default="illustrated", choices=THEMES,
                    help="which theme block to fill (default illustrated)")
    ap.add_argument("--lang", default=None, choices=("zh", "en"),
                    help="language of the stock notice (default: the plan's "
                         "lang, else zh)")
    ap.add_argument("--country", action="append", default=[], metavar="ISO2",
                    help="destination country/countries, when the plan's words do "
                         "not name them (repeatable or comma-separated)")
    ap.add_argument("--index", default=str(DEFAULT_INDEX), metavar="PATH",
                    help="stock kit index.json (default themes/assets/stock/index.json)")
    ap.add_argument("-o", "--out", default=None, metavar="OUT",
                    help="output art file (default <plan stem>.art.json beside the plan)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing art file")
    args = ap.parse_args()

    index_path = pathlib.Path(args.index)
    if not index_path.exists():
        sys.exit("no stock index at %s — pass --index PATH" % index_path)
    idx = json.loads(index_path.read_text(encoding="utf-8"))
    plan = load_plan(args.plan)

    out = pathlib.Path(args.out) if args.out else default_out(args.plan)
    if out.exists() and not args.force:
        sys.exit("%s already exists — pass --force to overwrite it (or -o OTHER)" % out)

    meta = plan.get("meta") if isinstance(plan.get("meta"), dict) else {}
    lang = args.lang or _s(plan.get("lang")) or _s(meta.get("lang")) or "zh"
    if lang not in ("zh", "en"):
        lang = "zh"
    notice = (idx.get("notice") or {}).get(lang) or ""
    if not notice:
        warn("index.json has no notice for lang %s — the page will not say the "
             "pictures are stock; say it in the chat reply" % lang)
    short = NOTICE_SHORT.get(lang, NOTICE_SHORT["en"])

    forced = []
    for c in args.country:
        for one in re.split(r"[,\s]+", c):
            if one:
                forced.append(one.strip().upper())
    ci = CountryIndex(idx.get("country_names"))
    dest, per_day, order, strong, notes = detect_countries(plan, ci, forced)
    if not dest:
        warn("no destination country found in trip / meta.route / legs / "
             "days[].city / stops — using a neutral cover and generic scenes "
             "only (no landmarks). Pass --country ISO2 to fix it.")
    unknown = [c for c in forced if c not in (idx.get("country_archetype") or {})]
    if unknown:
        warn("--country %s is not in index.json.country_archetype — no cover, no "
             "landmarks for it" % ",".join(unknown))

    dates = [_s(d.get("date")) for d in (plan.get("days") or [])
             if isinstance(d, dict)]
    if not dates:
        warn("the plan has no days[] — only the cover and the endcap get a picture")
    elif not all(dates):
        warn("%d day(s) have no `date` — art is keyed by date, so those days get "
             "no picture at all" % sum(1 for d in dates if not d))
    art = common_block(dates, notice, short, args.theme, index_path)
    zones, cover, cover_why = [], "", ""
    if args.theme == "illustrated":
        cover, cover_why = pick_cover(idx, plan, dest, per_day, order, strong)
        picks = pick_days(idx, plan, dest, per_day)
        art["themes"] = {"illustrated": illustrated_block(
            cover, picks, idx.get("generic") or {})}
        rows = [(d, stem, why) for d, stem, why, _ in picks]
        stems = [cover, art["themes"]["illustrated"]["end"]["hero"]]
        stems += [p[1] for p in picks]
    else:
        # clay paints its own terrain and has no cover painting slot, so the
        # cut-out scoring is not run at all — the day figurines are the picture.
        block, zones, rows = clay_block(idx, plan, per_day)
        art["themes"] = {"clay": block}
        stems = [r[1] for r in rows] + [CLAY_FLY, CLAY_TOUR, CLAY_LAST]
        stems += list(CLAY_ALTERNATE)

    # index drift / a hand-edited kit: every stem this file names must resolve
    for s in sorted(set(s for s in stems if not asset_exists(s))):
        warn("no webp for stem %s in themes/assets/stock or themes/assets — that "
             "slot will render empty" % s)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(art, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    report(args.theme, lang, idx, cover, cover_why, rows, notes, zones,
           out, args.plan)
    sys.stderr.write("todo       %s\n" % ", ".join(art["_stock_todo"]))
    print(out)


if __name__ == "__main__":
    main()
