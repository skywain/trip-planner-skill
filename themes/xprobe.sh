#!/bin/bash
# xprobe.sh — headless regression probe for the PNG export engine.
#
#   ./xprobe.sh <page.html> module '#d5' out.png
#   ./xprobe.sh <page.html> page   ''    out.png
#
# Clicks the real export button in headless Chrome, reports the canvas the
# engine produced ("OK <w>x<h> blob=<bytes> errs=<n>") and rasterises the
# exported PNG itself to <out.png> so it can be eyeballed. A green title is
# necessary but NOT sufficient — always look at the picture: cropped
# decorations, dropped effects and BLANK ICONS (sprite <use> refs, 2026-08-15)
# only show up visually.
#
# Chrome 151 headless hangs at exit on this Mac (work done, process never
# quits — 0% CPU forever), so each Chrome runs in the background with its own
# throwaway profile; we poll for its output, then kill just that Chrome
# (matched by its unique --user-data-dir).
#
# ANCHOR=bottom ./xprobe.sh …  shows the LAST 2600px of the export instead of
# the first — the only way to see whether a whole-page grab lost its tail.
#
# `page ''` on a MODULE-ONLY theme (no whole-page button: 夜航 noir, 玻璃
# glass, and any renderer built with page_root="") prints
# "NO-BTN" — but <out.png> is still written: it is then a plain screenshot of
# the LIVE page's first 2600px (1200px-wide window), i.e. the cover, and is
# fine to use as the cover eyeball check. NO-BTN is not a failure of the page.
# 闪屏 splash is the other trap: its whole-page export DELIBERATELY collapses
# the 100svh hero to zero height (see render_splash extra_css), so the export
# — and this probe's `page ''` picture — starts at DAY 01. To eyeball the
# splash cover use the live page instead:
#     ./xprobe.sh <page.html> live '' cover.png
# (a MODE other than page/module finds no button → NO-BTN → the same
# first-2600px live screenshot as above; the title line is expected).
#
# Viewport floor: macOS headless Chrome will not shrink innerWidth below ≈500
# whatever --window-size says (--window-size=390,844 renders a 500px-wide
# layout and screenshots its left 390px, which looks exactly like an overflow
# bug). For the 390px acceptance check, inject an in-page measurement instead
# of narrowing the window: e.g. wrap the page in a 390px-wide container /
# iframe, or read `document.documentElement.scrollWidth` vs `innerWidth` in
# the page and print it into the title — do not trust a narrow --window-size.
#
# Exit noise: this script kills its own background Chrome (pkill -9); the
# shell's "Killed: 9" job report is swallowed by the { … ; } 2>/dev/null +
# wait pattern below, so a clean run prints only the title/png lines. If you
# still see "Killed: 9" (older copies of this script), it is normal, not a
# failure.
set -u
# Scratch files (instrumented copy + throwaway Chrome profiles) go to
# $XPROBE_TMP, else $TMPDIR/xprobe, else /tmp/xprobe; only <out.png> lands
# where you asked.
SRC="$1"; MODE="$2"; SEL="${3:-}"; OUT="$4"; ANCHOR="${ANCHOR:-top}"
D="${XPROBE_TMP:-${TMPDIR:-/tmp}/xprobe}"; mkdir -p "$D"
TMP="$D/probe-$(basename "$OUT" .png).html"
python3 - "$SRC" "$MODE" "$SEL" "$TMP" "$ANCHOR" <<'PY'
import sys, pathlib, json
src, mode, sel, tmp, anchor = sys.argv[1:6]
img = ("<div style='position:relative;height:2600px;overflow:hidden'>"
       "<img style='position:absolute;bottom:0;left:0;width:100%;display:block' src=\"+JSON.stringify(u)+\"></div>"
       if anchor == 'bottom' else
       "<img style='width:100%;display:block' src=\"+JSON.stringify(u)+\">")
s = pathlib.Path(src).read_text(encoding='utf-8')
pick = ('document.querySelector("[data-x-page]")' if mode == 'page'
        else 'document.querySelector(%s)' % json.dumps('[data-x-for="%s"]' % sel))
wait = 16000 if mode == 'page' else 6000
inject = ('<script>window.__errs=[];window.onerror=function(m){window.__errs.push(String(m));};'
  'var _tb=HTMLCanvasElement.prototype.toBlob;'
  'HTMLCanvasElement.prototype.toBlob=function(cb,t){window.__c=this;'
  'return _tb.call(this,function(b){window.__blob=b?b.size:0;cb(b);},t);};'
  'window.addEventListener("load",function(){setTimeout(function(){'
  'var b=' + pick + ';'
  'if(!b){document.title="NO-BTN";return;}b.click();'
  'setTimeout(function(){'
  'if(!window.__c){document.title="NO-CANVAS errs="+window.__errs.join("~");return;}'
  'document.title="OK "+window.__c.width+"x"+window.__c.height+" blob="+(window.__blob||0)+" errs="+window.__errs.length;'
  'try{var u=window.__c.toDataURL("image/png");'
  'document.body.innerHTML="' + img + '";'
  'document.body.style.cssText="margin:0;background:#999";}catch(e){}'
  '},' + str(wait) + ');},900);});</script>')
pathlib.Path(tmp).write_text(s.replace('</body>', inject + '</body>', 1), encoding='utf-8')
PY
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# pass 1: title (dump-dom) — poll for </html>, then kill
UDD=$(mktemp -d "$D/udd.XXXXXX"); DOM="$UDD/dom.txt"
{ "$CH" --headless=new --disable-gpu --no-first-run --user-data-dir="$UDD" --window-size=1200,900 \
  --virtual-time-budget=45000 --dump-dom "file://$TMP" > "$DOM" 2>/dev/null & } 2>/dev/null
for i in $(seq 1 240); do grep -q '</html>' "$DOM" 2>/dev/null && break; sleep 1; done
TITLE=$(grep -o '<title>[^<]*</title>' "$DOM" | head -1)
echo "$(basename "$SRC") [$MODE ${SEL:-page}] → ${TITLE:-TIMEOUT(no dom in 240s)}"
{ pkill -9 -f -- "--user-data-dir=$UDD"; wait; } 2>/dev/null; sleep 1; rm -rf "$UDD"

# pass 2: screenshot of the exported PNG — poll for a PNG whose size stops growing
UDD=$(mktemp -d "$D/udd.XXXXXX"); rm -f "$OUT"
{ "$CH" --headless=new --disable-gpu --no-first-run --user-data-dir="$UDD" --hide-scrollbars \
  --window-size=1200,2600 --virtual-time-budget=45000 --screenshot="$OUT" "file://$TMP" 2>/dev/null & } 2>/dev/null
last=-1
for i in $(seq 1 240); do
  if [ -s "$OUT" ]; then sz=$(stat -f%z "$OUT"); [ "$sz" = "$last" ] && break; last=$sz; fi
  sleep 1
done
{ pkill -9 -f -- "--user-data-dir=$UDD"; wait; } 2>/dev/null; sleep 1; rm -rf "$UDD"
[ -s "$OUT" ] && echo "  png → $OUT ($(stat -f%z "$OUT") bytes)" || echo "  png → MISSING"
