# `themes/assets/portal/` — the portal theme's footage sidecar dir

Portal is the only theme that needs video. Its clips are **sidecar files** that travel next
to the rendered HTML (never inlined as data URIs), and this directory is the `video_dir` the
examples point at. **It is empty in the git tree** — no `*.mp4` is tracked here (`.gitignore`).

## The US reference chain

19 clips = 10 dives + 9 frame-chained links, 1344×768 @ 24 fps, ~35 MB. Not in the
tree; published as a GitHub Release asset. Restore it from the repo root:

```bash
curl -L https://github.com/skywain/trip-planner-skill/releases/download/demo-assets-v1/us-portal-clips.zip \
     -o us-portal-clips.zip && unzip -o us-portal-clips.zip -d themes/assets/portal/
```

## Style reference, not a footage library

The US chain is the **style reference and regression fixture** for
[`render_portal.py`](../../render_portal.py) and
[`build_portal_jobs.py`](../../build_portal_jobs.py) — the chain the design was built
against. It is **not** footage for other trips: another trip's scenery on your cover is a
logged defect. Every trip renders its own chain — art contract in the `portal` section of
[`ART-SCHEMA.md`](../../ART-SCHEMA.md), build recipe `build_portal_jobs.py --spec
worlds.json` (local ComfyUI) or `themes/genvideo.py` (cloud).

The shipped portal case is **Morocco** — `examples/morocco-2026/morocco-portal.html`,
its 9 clips in the same release as `morocco-portal-clips.zip`, live on the demo site:
<https://skywain.github.io/trip-planner-skill/examples/morocco-2026/morocco-portal.html>
That chain in motion: [`portal-motion.webp`](../../../docs/showcase/portal-motion.webp).
