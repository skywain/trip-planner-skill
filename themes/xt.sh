#!/bin/bash
# title-only probe (no screenshot) — <html> <mode> <selector>
#   ./xt.sh ../US-2026-手账版.html page ''      → whole-page export
#   ./xt.sh ../US-2026-手账版.html module '#d5' → one module
# Prints "<file> [mode sel] <title>RES WxH blob=N errs=N</title>".
#
# Chrome 151 headless hangs at exit on this Mac (DOM dumped, process never
# quits — 0% CPU forever), so Chrome runs in the background with its own
# throwaway profile, we poll stdout for the closing </html>, then kill just
# that Chrome (matched by its unique --user-data-dir).
# Scratch files (instrumented copy + throwaway Chrome profiles) go to
# $XPROBE_TMP, else $TMPDIR/xprobe, else /tmp/xprobe.
# The shell's "Killed: 9" job report from that pkill is swallowed ({ … ; }
# 2>/dev/null + wait); if an older copy still prints it, it is normal.
# innerWidth floor ≈500 in macOS headless Chrome — see xprobe.sh header.
SRC="$1"; MODE="$2"; SEL="$3"; D="${XPROBE_TMP:-${TMPDIR:-/tmp}/xprobe}"
mkdir -p "$D"
TMP="$D/t-$(basename "$SRC" .html)-$MODE.html"
python3 - "$SRC" "$MODE" "$SEL" "$TMP" <<'PY'
import sys, pathlib, json
src, mode, sel, tmp = sys.argv[1:5]
s = pathlib.Path(src).read_text(encoding='utf-8')
pick = ('document.querySelector("[data-x-page]")' if mode == 'page'
        else 'document.querySelector(%s)' % json.dumps('[data-x-for="%s"]' % sel))
inject = ('<script>window.__e=[];window.onerror=function(m){window.__e.push(String(m));};'
  'var _t=HTMLCanvasElement.prototype.toBlob;'
  'HTMLCanvasElement.prototype.toBlob=function(cb,ty,q){var C=this;'
  'return _t.call(this,function(b){window.__last=C.width+"x"+C.height+" "+(ty?ty.replace("image/",""):"png")+" blob="+(b?b.size:"NULL");cb(b);},ty,q);};'
  'window.addEventListener("load",function(){setTimeout(function(){var b=' + pick + ';'
  'if(!b){document.title="NO-BTN";return;}b.click();'
  # 27000ms post-click: the engine decodes the capture SVG twice since the
  # ink-bottom sizing fix (probe raster + final raster); stays under the
  # 40000 virtual-time budget below
  'setTimeout(function(){document.title="RES "+(window.__last||"none")+" errs="+window.__e.length;},27000);},900);});</script>')
pathlib.Path(tmp).write_text(s.replace('</body>', inject + '</body>', 1), encoding='utf-8')
PY
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
UDD=$(mktemp -d "$D/udd.XXXXXX"); OUT="$UDD/dom.txt"
{ "$CH" --headless=new --disable-gpu --no-first-run --user-data-dir="$UDD" --window-size=1200,900 \
  --virtual-time-budget=40000 --dump-dom "file://$TMP" > "$OUT" 2>/dev/null & } 2>/dev/null
for i in $(seq 1 240); do grep -q '</html>' "$OUT" 2>/dev/null && break; sleep 1; done
grep -o '<title>[^<]*</title>' "$OUT" | head -1 | sed "s|^|$(basename "$SRC") [$MODE$SEL] |"
[ -s "$OUT" ] || echo "$(basename "$SRC") [$MODE$SEL] TIMEOUT(no dom in 240s)"
{ pkill -9 -f -- "--user-data-dir=$UDD"; wait; } 2>/dev/null; sleep 1; rm -rf "$UDD"
