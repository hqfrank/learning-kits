#!/usr/bin/env python3
"""shoot.py — verify a story page the way a learner sees it.

Usage:  ~/.local/share/learn-kit/venv/bin/python learning/stories/tools/shoot.py <page.html> [out_dir]

For a desktop (1280 px) and a phone (390 px) viewport it:
  * loads the page with ?shot=1 (no transitions, loops still) and records console errors and failed asserts;
  * saves the first viewport (the "answer" screen) and the full page;
  * steps every figure.st-scene through every step and saves each step as its own PNG;
  * flags horizontal overflow (anything wider than the viewport);
  * writes contact.png: every step of every scene on one sheet, for a one-glance review.
Exit code 1 if there are console errors, failed asserts, or overflow.
"""
import base64, json, pathlib, sys
from playwright.sync_api import sync_playwright

page_path = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else f"/tmp/story-shots/{page_path.stem}")
out.mkdir(parents=True, exist_ok=True)
url = page_path.as_uri() + "?shot=1"
problems, shots = [], []

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vw, vh in (("desk", 1280, 820), ("phone", 390, 844)):
        pg = b.new_page(viewport={"width": vw, "height": vh}, device_scale_factor=1)
        logs = []
        pg.on("console", lambda m, logs=logs: logs.append((m.type, m.text)))
        pg.on("pageerror", lambda e, logs=logs: logs.append(("pageerror", str(e))))
        pg.goto(url); pg.wait_for_timeout(400)
        pg.screenshot(path=str(out / f"{name}-first-screen.png"))
        pg.screenshot(path=str(out / f"{name}-full.png"), full_page=True)
        over = pg.evaluate("""() => { const W = document.documentElement.clientWidth; const bad = [];
            const clipped = el => { for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) { const o = getComputedStyle(a).overflowX; if (o === 'auto' || o === 'scroll' || o === 'hidden') return true; } return false; };
            for (const el of document.querySelectorAll('body *')) { const r = el.getBoundingClientRect(); if (clipped(el)) continue;
              if (r.width && r.right > W + 2 && getComputedStyle(el).position !== 'fixed' && !el.closest('.st-card .back')) bad.push(el.tagName + (el.id ? '#' + el.id : '') + '.' + (el.className.baseVal ?? el.className)); }
            return bad.slice(0, 8); }""")
        if over: problems.append(f"{name}: horizontal overflow: {over}")
        scenes = pg.evaluate("() => Object.entries(Story.scenes).map(([k, v]) => [k, v.n])")
        for sid, n in scenes:
            for k in range(1, n + 1):
                pg.evaluate(f"Story.go('{sid}', {k})"); pg.wait_for_timeout(60)
                f = out / f"{name}-{sid}-{k}.png"
                pg.locator(f"#{sid}").screenshot(path=str(f))
                if name == "desk": shots.append((sid, k, n, f))
        for t, msg in logs:
            if t in ("error", "pageerror", "assert") or "Assertion failed" in msg:
                problems.append(f"{name}: console {t}: {msg}")
        pg.close()
    if shots:
        cells = "".join(f'<figure><img src="data:image/png;base64,{base64.b64encode(f.read_bytes()).decode()}"><figcaption>{sid} {k}/{n}</figcaption></figure>' for sid, k, n, f in shots)
        sheet = b.new_page(viewport={"width": 1600, "height": 900})
        sheet.set_content(f"<style>body{{margin:10px;font:13px sans-serif;display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}img{{width:100%;border:1px solid #ccc}}figure{{margin:0}}</style>{cells}")
        sheet.screenshot(path=str(out / "contact.png"), full_page=True)
    b.close()

print(json.dumps({"out": str(out), "scenes_steps": len(shots), "problems": problems}, indent=1))
sys.exit(1 if problems else 0)
