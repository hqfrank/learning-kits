/* story.js — the shared runtime for learning-kit story pages. Vanilla JS, no build, no CDN.
   Exposes window.Story = {go, set, bind, predict, poisson, reduced}.

   Markup it understands (see ~/.kiro/agents/learn/context/story.md for the full vocabulary):
   figure.st-scene#id[data-dwell=ms]   a scene player. Steps = number of <li> in its ol.st-cap.
     [data-s="2"]          part appears at step 2 and stays.   [data-s="0"] = always drawn.
     [data-s="2 4"]        appears at 2, and gets .is-lit on steps 2 and 4.
     .st-at[data-s="2 3"]  shown ONLY on the listed steps (a token in a slot, a busy ring).
     .st-tok               a token on an offset-path; it runs once each time its step is lit.
     .st-vals > [data-s]   one text per step at one spot (a changing number); behaves like .st-at.
   section.scene[data-title]   a scroll scene: fades in once, gets a rail dot.
   .st-predict                 predict-then-reveal: buttons [data-choice], one [data-right]; [data-why] per button;
                               reveals every .st-gated[data-gate=<predict id>] after any answer.
   button.st-card              a flip card.
   [data-ref=x]                linked highlighting: hover/focus one, all x light, the rest dim.
   .st-loop                    an ambient, data-carrying animation: paused off-screen, under reduced motion, or by the user.
   [data-view-switch]          buttons with data-view="kitchen|eng" toggle body.view-eng (metaphor labels vs real terms).
   URL ?shot=1 → no transitions (deterministic screenshots); ?scene=<id>&s=<n> opens a scene at a step. */
(() => {
"use strict";
const D = document, B = D.body, $$ = (s, r = D) => Array.from(r.querySelectorAll(s));
const Q = new URLSearchParams(location.search);
const reduced = !!(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
D.documentElement.classList.remove("no-js"); D.documentElement.classList.add("js");
if (Q.get("shot")) { B.classList.add("st-shot", "st-still"); D.documentElement.style.scrollBehavior = "auto"; }
if (reduced) B.classList.add("st-still");

/* ---------- wide figures: wrap so phones scroll sideways ---------- */
$$("svg[data-wide]").forEach(sv => { const w = D.createElement("div"); w.className = "st-wide"; sv.parentNode.insertBefore(w, sv); w.appendChild(sv); });

/* ---------- scene players ---------- */
const scenes = {};
const parseS = el => (el.getAttribute("data-s") || "").trim().split(/\s+/).map(Number).filter(n => !isNaN(n));
function makeScene(fig) {
  const caps = $$("ol.st-cap > li", fig), n = Math.max(caps.length, 1);
  const parts = $$("[data-s]", fig).map(el => ({el, s: parseS(el), at: el.classList.contains("st-at") || !!el.closest(".st-vals")}));
  const bar = D.createElement("div"); bar.className = "st-player";
  bar.innerHTML = `<button class="btn" data-go="-1" aria-label="Previous step">&#9664;</button>
    <button class="btn" data-play aria-label="Play the scene from step 1">&#9654; Play</button>
    <input type="range" min="1" max="${n}" step="1" value="1" aria-label="Step">
    <button class="btn" data-go="1" aria-label="Next step">&#9654;</button><span class="st-count" aria-hidden="true"></span>`;
  const capList = fig.querySelector("ol.st-cap");
  (capList || fig).insertAdjacentElement(capList ? "beforebegin" : "beforeend", bar);
  if (capList) capList.setAttribute("aria-live", "polite");
  const rng = bar.querySelector("input"), cnt = bar.querySelector(".st-count"), playB = bar.querySelector("[data-play]");
  let cur = 0, timer = null;
  const dwell = +fig.dataset.dwell || 3000;
  function set(k, user) {
    k = Math.max(1, Math.min(n, k)); const changed = k !== cur; cur = k;
    if (user) stop();
    rng.value = k; cnt.textContent = `${k} / ${n}`;
    caps.forEach((li, i) => li.classList.toggle("is-on", i === k - 1));
    for (const p of parts) {
      const first = Math.min(...p.s), on = p.at ? p.s.includes(k) : (p.s.includes(0) || k >= first);
      const lit = p.s.includes(k);
      p.el.classList.toggle("is-on", on);
      p.el.classList.toggle("is-lit", lit);
      if (p.el.classList.contains("st-tok")) {
        p.el.classList.remove("is-run");
        if (lit && changed && !B.classList.contains("st-still")) { void p.el.getBoundingClientRect(); p.el.classList.add("is-run"); }
      }
    }
    fig.dispatchEvent(new CustomEvent("st-step", {detail: {step: k, n}}));
  }
  function stop() { clearInterval(timer); timer = null; playB.innerHTML = "&#9654; Play"; }
  function play() {
    if (timer) return stop();
    set(1); playB.innerHTML = "&#10074;&#10074; Pause";
    timer = setInterval(() => { if (cur >= n) return stop(); set(cur + 1); }, reduced ? dwell * 1.5 : dwell);
  }
  bar.addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    if (b.hasAttribute("data-play")) play(); else set(cur + (+b.dataset.go), true);
  });
  rng.addEventListener("input", () => set(+rng.value, true));
  fig.tabIndex = fig.tabIndex >= 0 ? fig.tabIndex : 0;
  fig.addEventListener("keydown", e => {
    if (e.target.tagName === "INPUT") return;
    if (e.key === "ArrowRight") { set(cur + 1, true); e.preventDefault(); }
    if (e.key === "ArrowLeft") { set(cur - 1, true); e.preventDefault(); }
  });
  set(1);
  return scenes[fig.id] = {set: k => set(k, true), get step() { return cur; }, n, fig};
}
$$("figure.st-scene").forEach(makeScene);

/* ---------- scroll scenes: reveal once, rail dots, progress ---------- */
const secs = $$("section.scene");
if (!Q.get("shot") && "IntersectionObserver" in window) {
  secs.forEach(s => s.classList.add("st-pending"));
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.remove("st-pending"); io.unobserve(e.target); } }), {rootMargin: "0px 0px -12% 0px"});
  secs.forEach(s => io.observe(s));
}
if (secs.length) {
  const nav = D.createElement("nav"); nav.className = "st-dots"; nav.setAttribute("aria-label", "Scenes");
  secs.forEach(s => { if (!s.id) return; const a = D.createElement("a"); a.href = "#" + s.id; a.innerHTML = `<span>${s.dataset.title || s.id}</span>`; a.setAttribute("aria-label", s.dataset.title || s.id); nav.appendChild(a); });
  B.appendChild(nav);
  const bar = D.createElement("div"); bar.className = "st-progress"; B.appendChild(bar);
  const dots = $$("a", nav);
  const onScroll = () => {
    const h = D.documentElement; bar.style.width = (100 * h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight)) + "%";
    let k = -1; secs.forEach((s, i) => { if (s.getBoundingClientRect().top < innerHeight * .45) k = i; });
    dots.forEach((d, i) => d.classList.toggle("is-on", i === k));
  };
  addEventListener("scroll", onScroll, {passive: true}); onScroll();
}

/* ---------- ambient loops: pause off-screen; a global motion switch ---------- */
const loops = $$(".st-loop");
if (loops.length) {
  if ("IntersectionObserver" in window) {
    const lo = new IntersectionObserver(es => es.forEach(e => e.target.classList.toggle("is-paused", !e.isIntersecting)));
    loops.forEach(l => lo.observe(l));
  }
  const mb = D.createElement("button"); mb.className = "btn st-motion";
  const label = () => { const still = B.classList.contains("st-still"); mb.textContent = still ? "\u25B6 Motion on" : "\u275A\u275A Motion off"; mb.setAttribute("aria-pressed", String(still)); };
  mb.addEventListener("click", () => { B.classList.toggle("st-still"); label(); B.dispatchEvent(new CustomEvent("st-motion")); });
  label(); B.appendChild(mb);
}

/* ---------- predict-then-reveal ---------- */
function predict(box) {
  const why = box.querySelector(".why") || box.appendChild(Object.assign(D.createElement("p"), {className: "why"}));
  why.setAttribute("aria-live", "polite");
  box.addEventListener("click", e => {
    const b = e.target.closest("[data-choice]"); if (!b) return;
    $$("[data-choice]", box).forEach(x => { x.classList.toggle("is-right", x.hasAttribute("data-right")); x.classList.toggle("is-wrong", x === b && !x.hasAttribute("data-right")); x.setAttribute("aria-pressed", String(x === b)); });
    why.innerHTML = (b.hasAttribute("data-right") ? "<b>Yes.</b> " : "<b>Not quite.</b> ") + (b.dataset.why || "");
    $$(`.st-gated[data-gate="${box.id}"]`).forEach(g => g.classList.add("is-open"));
    box.dispatchEvent(new CustomEvent("st-answer", {detail: {choice: b.dataset.choice, right: b.hasAttribute("data-right")}}));
  });
}
$$(".st-predict").forEach(predict);
if (Q.get("shot")) $$(".st-gated").forEach(g => g.classList.add("is-open"));

/* ---------- flip cards ---------- */
$$("button.st-card").forEach(c => { c.setAttribute("aria-pressed", "false");
  c.addEventListener("click", () => { const f = c.classList.toggle("is-flipped"); c.setAttribute("aria-pressed", String(f)); }); });

/* ---------- linked highlighting ---------- */
function hl(ref) { B.classList.toggle("has-hl", !!ref); $$("[data-ref]").forEach(x => x.classList.toggle("is-hl", !!ref && x.dataset.ref === ref)); }
D.addEventListener("pointerover", e => { const t = e.target.closest && e.target.closest("[data-ref]"); hl(t ? t.dataset.ref : null); });
D.addEventListener("focusin", e => { const t = e.target.closest && e.target.closest("[data-ref]"); hl(t ? t.dataset.ref : null); });

/* ---------- view switch: metaphor labels vs real terms ---------- */
$$("[data-view-switch]").forEach(sw => sw.addEventListener("click", e => {
  const b = e.target.closest("[data-view]"); if (!b) return;
  B.classList.toggle("view-eng", b.dataset.view === "eng");
  $$("[data-view-switch] [data-view]").forEach(x => x.setAttribute("aria-pressed", String(x.dataset.view === b.dataset.view)));
}));
if (Q.get("view") === "eng") B.classList.add("view-eng");

/* ---------- live figures: bind inputs to one pure model ---------- */
// bind(root, model, render): every input[data-k] inside root feeds settings[k]; model(settings) -> out; render(out, settings).
function bind(root, model, render) {
  const ins = $$("input[data-k],select[data-k]", root);
  const run = () => { const s = {}; ins.forEach(i => { s[i.dataset.k] = i.type === "checkbox" ? i.checked : +i.value; });
    const out = model(s); render(out, s); return out; };
  ins.forEach(i => i.addEventListener("input", run)); return run();
}

/* ---------- exact Poisson (Garwood) interval, used by deadline scenes ---------- */
function pcdf(k, lam) { let t = Math.exp(-lam), s = t; for (let i = 1; i <= k; i++) { t *= lam / i; s += t; } return s; }
function solve(f, lo, hi) { for (let i = 0; i < 200; i++) { const m = (lo + hi) / 2; if (f(m) > 0) lo = m; else hi = m; } return (lo + hi) / 2; }
// two-sided (1-alpha) interval on the mean count, given k observed events
function poisson(k, alpha = 0.05) {
  const up = solve(l => pcdf(k, l) - alpha / 2, 0, 50 + 10 * k);
  const lo = k === 0 ? 0 : solve(l => (1 - pcdf(k - 1, l)) - alpha / 2 < 0 ? 1 : -1, 0, 50 + 10 * k);
  return {lo, up};
}
console.assert(Math.abs(poisson(0).up - 3.689) < 0.001, "Garwood k=0 upper bound is -ln(0.025)=3.689");
console.assert(Math.abs(poisson(1).up - 5.572) < 0.001, "Garwood k=1 upper bound is 5.572");
console.assert(Math.abs(poisson(1).lo - 0.0253) < 0.001, "Garwood k=1 lower bound is 0.0253");

window.Story = {go: (id, k) => scenes[id] && scenes[id].set(k), set: (id, k) => scenes[id] && scenes[id].set(k), scenes, bind, predict, poisson, reduced};

/* deep link: ?scene=<id>&s=<n> */
if (Q.get("scene") && scenes[Q.get("scene")]) { scenes[Q.get("scene")].set(+Q.get("s") || 1); scenes[Q.get("scene")].fig.scrollIntoView(); }
})();
