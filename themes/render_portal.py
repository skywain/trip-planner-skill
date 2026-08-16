#!/usr/bin/env python3
"""Portal (穿越版) — scroll-scrubbed video fly-through, scroll-world style.

One continuous camera flight through N floating worlds (one per dive
clip): dive INTO a world, fly back out through the clouds, arrive at the
next, dive again.
Scroll position is mapped to video time (blob-loaded for instant seeking,
two stacked <video> slots, hard cuts at frame-chained seams). Day content
fades in while the camera is inside that day's world.

FOOTAGE (US regression chain, 19 clips = 10 dives + 9 frame-chained links;
any N ≥ 1 works — N dives + N-1 links, or dives only):
  portal/sNN-dive.mp4      s01..s10, 124f / 5.17s each
  portal/sNN-sMM-link.mp4  9 seams, 90f / 3.75s each
  1344x768 @ 24fps, ~35 MB total. Videos stay sidecar files (embedding
  them as data URIs would triple-bloat the page), so this page travels
  together with its video dir (themes/assets/portal/ for the US trip) —
  file:// double-click included.

Usage: python3 render_portal.py <plan.geo.json> [--art <file>|none] [--assets DIR] -o out.html

ART CONTRACT (schema: ART-SCHEMA.md → themes.portal):
  cover.kick                 <title> "{kick} {year} · 穿越版" (en page: cover.kick_en
                             wins when set, year not repeated — theme_common.
                             title_head); h1 "穿越{kick}"                    → "穿越"
  cover.zh (theme=portal)    h1 override (e.g. 「穿越美国行」)               → kick form
  themes.portal.tag          intro eyebrow                                    → "PORTAL · <N> WORLDS · ONE TAKE"
                             where N = number of "dive" clips, spelled out
                             ONE..TWELVE (digits beyond; "ONE WORLD" singular;
                             no dives → "PORTAL · ONE TAKE")
  themes.portal.intro        intro paragraph (the N-world route sentence)     → generic
  themes.portal.outro        {"tag": "DIAMOND HEAD · SUNRISE", "zh": "落在日出里", "text": "…"} → TOUCHDOWN / 落地 / generic
  (day overlay card: plan day.label ≤64 chars and up to four anchor rows' `what`
   ≤52 chars are shown; longer copy is cut at a word/punctuation boundary with an
   ellipsis — soft_cut() — so keep labels short or accept the "…")
                             (no world count in the outro defaults — nothing
                             to keep in sync there)
  themes.portal.video_dir    directory holding the clips, relative to the ART
                             file (or absolute); the page links them RELATIVE
                             to the output HTML so file:// double-click works  → "portal"
                             e.g. art trips/x/x.art.json + video_dir "portal"
                             + -o trips/x/out/X-穿越版.html → page links
                             "../portal/s01-dive.mp4"
  themes.portal.clips        [{"file","dur","off","kind":"dive"|"link","day":N}]
                             in reel order; "day" = 1-based plan day whose
                             overlay fades in during that dive (links carry
                             no day → no overlay)                            → no footage,
                             page renders intro/outro only
                             dur = clip length in seconds as ffprobe reports it
                                   (3 decimals is plenty: 124f@24fps → 5.167);
                                   too large → the tail of the scroll span
                                   freezes on the last frame, too small →
                                   the last frames are never reached, and the
                                   seam cut lands on a non-matching frame
                             off = seconds skipped at the HEAD of the clip
                                   (0 normally; >0 only to hide a bad first
                                   frame). Scroll maps p∈[0,1] onto
                                   t = off + p·(dur − off − 0.03) — the 0.03
                                   keeps the seek inside the last real frame
                             1 clip → single-slot playback (no seam pre-seek);
                             ≥2 clips → two-slot frame-chained seams
  days[d].theme              4-char day title on the overlay                  → city
  cover.en / outro.en        used instead of .zh when the page language is en
                             (plan.lang / --lang en; the other key is the
                             fallback, then the theme's own English default)

Language: plan.lang / meta.lang / --lang (theme_common.init_lang). Shared UI
words go through T(); this theme's own voice (loading line, scroll cue,
no-JS note, intro/outro defaults) lives in L below. zh output is byte-stable.
"""
import argparse
import json
import os
import pathlib
import re
import sys

from theme_common import (T, Art, add_art_arg, esc, init_lang, lang,
                          load_art, load_plan, short_dates, theme_name, title_head)

HERE = pathlib.Path(__file__).parent

# clip chain comes from art.json (themes.portal.clips); nothing about a
# particular trip's footage lives here any more.
PX_PER_S = 340        # scroll length per clip-second — the scrub "gearing"

# theme-voice strings (shared UI words go through theme_common.T)
L = {
    "zh": {
        "portal": "穿越", "portal_h1": "穿越",
        "loading": "正在装载胶片 …",
        "loading_left_pre": "正在装载胶片 … 还差 ", "loading_left_post": " 卷",
        "ready": "胶片就绪 · 滚动起飞",
        "cue": "▼ 往下滚,穿进去",
        "nojs_h1": "穿越版需要 JS",
        "nojs_p": "这一版的本体是滚动驱动的视频飞行,关掉 JS 后请看其他七个版本。",
        "intro": "滚动就是飞行:一镜到底穿过这趟旅程的每一个世界,"
                 "天色随行程昼夜流转。松手即停,倒着滚就倒着飞。",
        "outro_tag": "TOUCHDOWN", "outro_h1": "落地",
        "outro_text": "一镜到底飞完全程。往回滚,随时倒着再飞一遍。",
    },
    "en": {
        "portal": "Through ", "portal_h1": "Portal",
        "loading": "Loading the reel …",
        "loading_left_pre": "Loading the reel … ", "loading_left_post": " to go",
        "ready": "Reel ready · scroll to take off",
        "cue": "▼ Scroll down to fly in",
        "nojs_h1": "Portal needs JavaScript",
        "nojs_p": "This edition is a scroll-driven video flight; with JS off, "
                  "open one of the other editions instead.",
        "intro": "Scrolling is flying: one continuous take through every world of "
                 "this trip, the sky turning with the itinerary. Let go and it "
                 "holds; scroll back and it flies in reverse.",
        "outro_tag": "TOUCHDOWN", "outro_h1": "Touchdown",
        "outro_text": "One take, the whole way. Scroll back up to fly it again in reverse.",
    },
}


def t(k):
    return L.get(lang(), L["zh"]).get(k, L["zh"][k])


NUM_WORDS = ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN",
             "EIGHT", "NINE", "TEN", "ELEVEN", "TWELVE"]


def portal_tag(n_worlds):
    """Default intro eyebrow: world count = number of dive clips, spelled out
    ONE..TWELVE (digits beyond that), singular for one, no count for none."""
    if n_worlds <= 0:
        return "PORTAL · ONE TAKE"
    word = NUM_WORDS[n_worlds] if n_worlds < len(NUM_WORDS) else str(n_worlds)
    return f"PORTAL · {word} {'WORLD' if n_worlds == 1 else 'WORLDS'} · ONE TAKE"


def soft_cut(s, n):
    """Overlay copy has a hard budget (the card is ~430px wide); cut over-long
    strings at a word / punctuation boundary and mark the cut with an ellipsis
    instead of slicing mid-word ("a night in a palm-g", "ScottsMiracle-" —
    Morocco/US 2026-08-16). Strings within budget are returned untouched, so
    plans that never overflowed render byte-identically."""
    s = s or ""
    if len(s) <= n:
        return s
    cut = n - 1
    for k in range(cut, int(n * 0.6), -1):
        if s[k] in " \t,;:·—–-()()、,;:" and s[k - 1] not in " \t":
            cut = k
            break
    return s[:cut].rstrip(" \t,;:·—–-(、,;:") + "…"


def day_payload(day, i, art):
    rows = []
    for r in day.get("timeline", []):
        if r.get("kind") in (None, "anchor") and len(rows) < 4:
            rows.append({"t": r.get("t", ""), "w": soft_cut(r.get("what", ""), 52)})
    return {
        "n": i, "date": day.get("date", ""),
        "theme": art.day_theme(day.get("date", ""), day.get("city", "")),
        "city": day.get("city", ""), "label": soft_cut(day.get("label", ""), 64),
        "rows": rows,
    }


TPL = """<!doctype html>
<html lang="__HTML_LANG__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html { scroll-behavior:auto; }
  body { background:#0d0b14; color:#f3eefc;
    font-family:"PingFang SC","Hiragino Sans GB",system-ui,sans-serif; }
  :focus-visible { outline:2.5px solid #ffd98a; outline-offset:3px; }
  #track { position:relative; }
  #stage { position:fixed; inset:0; overflow:hidden; background:#0d0b14; }
  #stage video { position:absolute; inset:0; width:100%; height:100%;
    object-fit:cover; opacity:0; }
  /* soft edges so the 9:16 clip breathes on desktop */
  #stage::after { content:""; position:absolute; inset:0; pointer-events:none;
    background:radial-gradient(120% 100% at 50% 50%, transparent 62%,
      rgba(13,11,20,.55) 100%); }

  .screen { position:relative; z-index:3; height:100svh; display:flex;
    flex-direction:column; align-items:center; justify-content:center;
    gap:18px; text-align:center; padding:0 24px; }
  .screen h1 { font-size:clamp(34px,6vw,64px); font-weight:800;
    letter-spacing:.18em; text-indent:.18em; }
  .screen p { font-size:14px; line-height:2; color:#c9bfe0; max-width:34em; }
  /* intro/outro text sits over a held video frame — shadow keeps it legible */
  .screen h1, .screen p { text-shadow:0 2px 18px rgba(13,11,20,.65),
    0 1px 6px rgba(13,11,20,.5); }
  .tag { font-size:11px; letter-spacing:.4em; color:#9f8fd0; text-indent:.4em; }
  .cue { margin-top:12px; font-size:12px; letter-spacing:.3em; color:#c9bfe0;
    animation:bob 2s ease-in-out infinite; }
  @keyframes bob { 50% { transform:translateY(8px); } }
  #load { font-size:12px; letter-spacing:.2em; color:#9f8fd0;
    font-variant-numeric:tabular-nums; }

  /* day overlay card — appears while the camera is inside that world */
  .ov { position:fixed; z-index:4; left:clamp(18px,6vw,90px);
    bottom:clamp(56px,12vh,120px); max-width:min(430px, 82vw);
    opacity:0; transform:translateY(26px); pointer-events:none; }
  .ov .k { font-size:11px; letter-spacing:.34em; color:#ffd98a; }
  .ov h2 { font-size:clamp(30px,5vw,44px); font-weight:800; margin:8px 0 6px;
    letter-spacing:.1em; text-shadow:0 2px 18px rgba(0,0,0,.6); }
  .ov .lb { font-size:13px; line-height:1.9; color:#e8e0f5;
    text-shadow:0 1px 10px rgba(0,0,0,.65); }
  .ov ul { list-style:none; margin-top:12px; }
  .ov li { font-size:12.5px; line-height:2; color:#d9cfee;
    text-shadow:0 1px 8px rgba(0,0,0,.65); }
  .ov li b { font-family:ui-monospace,Menlo,monospace; font-weight:700;
    color:#ffd98a; margin-right:8px; }

  #hud { position:fixed; z-index:5; top:14px; right:16px; font-size:10px;
    letter-spacing:.18em; color:#8d7fbd; font-variant-numeric:tabular-nums;
    text-align:right; line-height:1.9; }

  .fallback { display:none; }
  .no-scrub #stage, .no-scrub .ov, .no-scrub #hud { display:none; }
  .no-scrub .fallback { display:block; position:relative; z-index:3;
    max-width:760px; margin:0 auto; padding:40px 22px 80px; }
  .fallback h2 { margin:34px 0 10px; font-size:22px; letter-spacing:.1em; }
  .fallback p { font-size:13.5px; line-height:2; color:#c9bfe0; }
  noscript .screen { height:auto; padding:60px 24px; }
  @media (prefers-reduced-motion:reduce) { .cue { animation:none; } }
  @media print {
    #stage, #hud, .ov, #scrub, #load, .cue { display:none; }
    body { background:#fff; color:#16121f; }
    .screen { height:auto; padding:48px 24px; }
    .screen h1, .screen p { text-shadow:none; }
    .screen p, .tag { color:#454050; }
  }
</style>
</head>
<body>
<div id="track">
  <section class="screen" id="intro">
    <p class="tag">__INTRO_TAG__</p>
    <h1>__H1__</h1>
    <p>__INTRO__</p>
    <p id="load">__LOADING__</p>
    <p class="cue">__CUE__</p>
  </section>
  <div id="scrub" aria-hidden="true"></div>
  <section class="screen" id="outro">
    <p class="tag">__OUTRO_TAG__</p>
    <h1>__OUTRO_H1__</h1>
    <p>__OUTRO_TEXT__</p>
  </section>
  <noscript><section class="screen"><h1>__NOJS_H1__</h1>
    <p>__NOJS_P__</p>
  </section></noscript>
</div>
<div id="stage" aria-hidden="true"><video muted playsinline preload="auto"></video><video muted playsinline preload="auto"></video></div>
__OVERLAYS__
<div id="hud" aria-hidden="true"></div>

<script>
(function () {
  var CLIPS = __CLIPS__;
  var PXS = __PXS__;
  var doc = document.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) { doc.classList.add('no-scrub'); return; }

  var stage = document.getElementById('stage');
  var slots = stage.querySelectorAll('video');
  var loadEl = document.getElementById('load');
  var hud = document.getElementById('hud');
  var scrub = document.getElementById('scrub');

  // scroll spans
  var total = 0;
  CLIPS.forEach(function (c) {
    c.play = c.dur - c.off - 0.03;          // seekable window, to the true last frame
    c.span = Math.round(c.play * PXS);
    c.start = total; total += c.span;
  });
  scrub.style.height = total + 'px';

  // Everything init()/paint() touches must be declared BEFORE the loader:
  // on file:// the done() chain is fully synchronous, so init() runs right
  // here — a declaration below the loader is still undefined then (that
  // exact bug killed every overlay/HUD on double-click while HTTP, being
  // async, hid it).
  var ovs = [].slice.call(document.querySelectorAll('.ov'));

  // Preferred: blob-load every clip (instant, reliable seeking over HTTP).
  // Double-clicked file:// pages can't fetch() at all — fall back to direct
  // <video src>, which browsers DO allow for sibling local files and which
  // seeks fine from disk. Same fallback if any fetch fails for other reasons.
  var left = CLIPS.length;
  function done(c, url) {
    c.url = url;
    left--;
    loadEl.textContent = left ? ('__LOAD_LEFT_PRE__' + left + '__LOAD_LEFT_POST__')
                              : '__READY__';
    if (!left) init();
  }
  if (location.protocol === 'file:') {
    CLIPS.forEach(function (c) { done(c, c.src); });
  } else {
    CLIPS.forEach(function (c) {
      fetch(c.src).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.blob();
      }).then(function (b) {
        done(c, URL.createObjectURL(b));
      }).catch(function () {
        done(c, c.src);       // direct-src degrade beats a dead page
      });
    });
  }

  function init() {
    slots[0].src = CLIPS[0].url; slots[0].dataset.clip = 0;
    // a single-clip reel plays in slot 0 alone: slot 1 stays empty
    // (dataset.clip unset → NaN, never matched) and slotFor() only ever
    // resolves clip 0, so no seam pre-seek is attempted.
    if (CLIPS.length > 1) { slots[1].src = CLIPS[1].url; slots[1].dataset.clip = 1; }
    // direct-src mode loads lazily: repaint once a slot learns its duration
    slots.forEach(function (s) {
      s.addEventListener('loadedmetadata', function () { paint(); });
    });
    var ticking = false;
    addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(paint); }
    }, { passive: true });
    addEventListener('resize', function () { paint(); });   // sync: works even
    // where rAF is suspended (hidden panes) — and harmless everywhere else
    paint();

    function slotFor(ci) {
      for (var s = 0; s < 2; s++)
        if (+slots[s].dataset.clip === ci) return slots[s];
      // steal the slot that is furthest from ci
      var v = slots[(ci % 2)];
      v.dataset.clip = ci; v.src = CLIPS[ci].url;
      return v;
    }

    function paint() {
      ticking = false;
      var vh = innerHeight;
      var y = scrollY - vh;              // scrub space starts after the intro
      var i, c, p;
      if (y < 0) { setActive(-1); return; }
      if (y >= total) { setActive(-2); return; }
      for (i = CLIPS.length - 1; i > 0 && y < CLIPS[i].start; i--) {}
      c = CLIPS[i];
      p = Math.min(1, Math.max(0, (y - c.start) / c.span));
      var v = slotFor(i);
      var t = c.off + p * c.play;
      if (v.readyState >= 1 && Math.abs((v.currentTime || 0) - t) > 0.033)
        v.currentTime = t;
      // frame-chained seams: the neighbour clip sits UNDERNEATH at full
      // opacity, pre-seeked to its boundary frame (pixel-identical to this
      // clip's edge frame), so crossing a seam is a hard cut between
      // identical frames. A translucent crossfade here would drag a frozen
      // ghost over moving footage and read as judder. Hysteresis (0.25/0.35)
      // keeps the spare slot from thrashing its src around mid-clip.
      var spare = slots[0] === v ? slots[1] : slots[0];
      var held = +spare.dataset.clip;
      var oc;
      if (p < 0.25) oc = i > 0 ? i - 1 : i + 1;
      else if (p > 0.35) oc = i < CLIPS.length - 1 ? i + 1 : i - 1;
      else oc = (held === i - 1 || held === i + 1) ? held
              : (i < CLIPS.length - 1 ? i + 1 : i - 1);
      var other = null;
      if (oc >= 0 && oc < CLIPS.length) {
        other = slotFor(oc);
        var ot = oc === i + 1 ? CLIPS[oc].off : CLIPS[oc].off + CLIPS[oc].play;
        if (other.readyState >= 1 && Math.abs((other.currentTime || 0) - ot) > 0.05)
          other.currentTime = ot;
      }
      slots.forEach(function (s) { s.style.opacity = 0; s.style.zIndex = 1; });
      if (other) other.style.opacity = 1;
      v.style.opacity = 1; v.style.zIndex = 2;
      // day overlays ride their dive's mid-window
      ovs.forEach(function (o) {
        var ci = +o.dataset.clip, w0 = 0.30, w1 = 0.94, oo = 0;
        if (ci === i) {
          if (p > w0 && p < w1) {
            oo = Math.min(1, (p - w0) / 0.10, (w1 - p) / 0.06);
          }
        }
        o.style.opacity = oo.toFixed(3);
        o.style.transform = 'translateY(' + (26 * (1 - oo)).toFixed(1) + 'px)';
      });
      hud.textContent = 'CLIP ' + (i + 1) + '/' + CLIPS.length + ' · ' +
        (p * 100).toFixed(0) + '%';
      stage.style.opacity = 1;
    }

    function setActive(mode) {
      slots.forEach(function (s) { s.style.opacity = 0; });
      ovs.forEach(function (o) { o.style.opacity = 0; });
      if (mode === -1) {                       // intro: hold clip 0 first frame
        var v = slotFor(0);
        if (v.readyState >= 1 && Math.abs((v.currentTime || 0) - CLIPS[0].off) > 0.05)
          v.currentTime = CLIPS[0].off;
        v.style.opacity = 1;
        var fade = Math.min(1, Math.max(0, scrollY / (innerHeight * 0.7)));
        v.style.opacity = fade.toFixed(3);
        hud.textContent = 'INTRO';
      } else {                                 // outro: hold last frame
        var w = slotFor(CLIPS.length - 1);
        var cl = CLIPS[CLIPS.length - 1];
        if (w.readyState >= 1 && Math.abs((w.currentTime || 0) - (cl.off + cl.play)) > 0.05)
          w.currentTime = cl.off + cl.play;
        w.style.opacity = 1;
        hud.textContent = 'OUTRO';
      }
    }
  }
})();
</script>
</body>
</html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("-o", "--out", required=True)
    add_art_arg(ap)
    args = ap.parse_args()
    p = load_plan(args.plan)
    init_lang(args, p)
    art = load_art(args.plan, args.art, args.assets)
    days = p.get("days", [])
    meta = p.get("meta", {})
    out = pathlib.Path(args.out)
    tp = art.theme("portal")

    # footage: files listed in art, directory relative to the art file
    # (or absolute); the page links them relative to the OUTPUT html so a
    # double-clicked file:// copy still finds them.
    clips = []
    vdir = tp.get("video_dir", "portal")
    base = (art.path.parent if art.path else pathlib.Path(args.plan).parent)
    vpath = (pathlib.Path(vdir) if pathlib.Path(vdir).is_absolute()
             else (base / vdir)).resolve()
    try:
        rel = pathlib.Path(os.path.relpath(vpath, out.resolve().parent)).as_posix()
    except ValueError:            # different drive on Windows — absolute
        rel = vpath.as_uri()
    missing = 0
    for c in tp.get("clips", []) or []:
        f = c.get("file", "")
        if not f:
            continue
        if not (vpath / f).exists():
            missing += 1
        clips.append((f"{rel}/{f}", float(c.get("dur", 0)), float(c.get("off", 0)),
                      c.get("kind", "dive"), c.get("day")))
    if missing:
        sys.stderr.write(f"WARN: {missing} clip file(s) listed in art not found under {vpath}\n")
    if len(clips) == 1:
        sys.stderr.write("NOTE: only 1 clip in themes.portal.clips — single-slot playback, "
                         "no frame-chained seams (fine for a smoke test)\n")
    elif not clips:
        sys.stderr.write("NOTE: no clips in themes.portal.clips — page renders intro/outro only\n")

    clips_js = []
    overlays = []
    for ci, (src, dur, off, kind, dayi) in enumerate(clips):
        clips_js.append({"src": src, "dur": dur, "off": off})
        if kind == "dive" and dayi and dayi <= len(days):
            d = day_payload(days[dayi - 1], dayi, art)
            rows = "".join(f'<li><b>{esc(r["t"])}</b>{esc(r["w"])}</li>'
                           for r in d["rows"])
            overlays.append(
                f'<aside class="ov" data-clip="{ci}" aria-hidden="true">'
                f'<p class="k">{T("label.day")} {d["n"]:02d} · {esc(d["date"][5:])} · {esc(d["city"])}</p>'
                f'<h2>{esc(d["theme"])}</h2>'
                f'<p class="lb">{esc(d["label"])}</p><ul>{rows}</ul></aside>')

    n_worlds = sum(1 for c in clips if c[3] == "dive")
    tag = tp.get("tag") or portal_tag(n_worlds)
    kick = art.cover("portal", "kick", "")
    year = ""
    m = re.search(r"\d{4}", meta.get("dates", "") or "")
    if m:
        year = m.group(0)
    # <title>: theme_common.title_head — kick_en on an en page, year not repeated
    title = " · ".join(x for x in (title_head(art, "portal", year), theme_name("portal")) if x)
    # cover/outro headline: the art key for the current language first, the
    # other one second (art text is trip content — showing it is fine), then
    # the theme's own fallback.
    lk, ok = (("zh", "en") if lang() == "zh" else ("en", "zh"))
    h1 = (art.cover("portal", lk) or art.cover("portal", ok)
          or (f"{t('portal')}{kick}" if kick else t("portal_h1")))
    intro = tp.get("intro") or t("intro")
    outro = tp.get("outro") or {}
    o_tag = outro.get("tag") or t("outro_tag")
    o_h1 = outro.get(lk) or outro.get(ok) or t("outro_h1")
    o_text = outro.get("text") or t("outro_text")

    html_out = (TPL
                .replace("__HTML_LANG__", T("html_lang"))
                .replace("__LOADING__", esc(t("loading")))
                .replace("__CUE__", esc(t("cue")))
                .replace("__NOJS_H1__", esc(t("nojs_h1")))
                .replace("__NOJS_P__", esc(t("nojs_p")))
                .replace("__LOAD_LEFT_PRE__", t("loading_left_pre"))
                .replace("__LOAD_LEFT_POST__", t("loading_left_post"))
                .replace("__READY__", t("ready"))
                .replace("__TITLE__", esc(title))
                .replace("__H1__", esc(h1))
                .replace("__INTRO_TAG__", esc(tag))
                .replace("__INTRO__", esc(intro))
                .replace("__OUTRO_TAG__", esc(o_tag))
                .replace("__OUTRO_H1__", esc(o_h1))
                .replace("__OUTRO_TEXT__", esc(o_text))
                .replace("__CLIPS__", json.dumps(clips_js, ensure_ascii=False))
                .replace("__PXS__", str(PX_PER_S))
                .replace("__OVERLAYS__", "".join(overlays)))
    out.write_text(html_out, encoding="utf-8")
    print(f"{out.name}: {out.stat().st_size // 1024}KB, clips={len(clips)}, "
          f"overlays={len(overlays)}")


if __name__ == "__main__":
    main()
