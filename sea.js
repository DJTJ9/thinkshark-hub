// Lebendiges Meer: Boids-Schwarm, ein Hai, Blasen und Meeresschnee auf einem fixen Canvas.
// Der obere Teil ist reine Simulation ohne DOM (in tests/test_sea.py per node getestet).
(function () {
  "use strict";

  const CFG = {
    maxSpeed: 1.7, minSpeed: 0.6,
    viewRadius: 70, sepRadius: 24,
    wSep: 0.05, wAli: 0.04, wCoh: 0.0006,
    sharkRadius: 180, pointerRadius: 140, wFlee: 0.9,
    sharkSpeed: 1.2, sharkTurn: 0.02, margin: 40,
  };

  function makeBoid(rand, w, h) {
    const a = rand() * Math.PI * 2;
    return { x: rand() * w, y: rand() * h, vx: Math.cos(a), vy: Math.sin(a) };
  }

  function flee(b, t, weight) {
    const dx = b.x - t.x, dy = b.y - t.y;
    const d2 = dx * dx + dy * dy;
    if (d2 === 0 || d2 >= t.radius * t.radius) return;
    const d = Math.sqrt(d2);
    const push = (1 - d / t.radius) * weight;
    b.vx += (dx / d) * push;
    b.vy += (dy / d) * push;
  }

  function clampSpeed(b, min, max) {
    const sp = Math.hypot(b.vx, b.vy) || 1e-6;
    const cl = Math.min(max, Math.max(min, sp));
    b.vx = (b.vx / sp) * cl;
    b.vy = (b.vy / sp) * cl;
  }

  function wrap(b, w, h) {
    const m = CFG.margin;
    if (b.x < -m) b.x = w + m; else if (b.x > w + m) b.x = -m;
    if (b.y < -m) b.y = h + m; else if (b.y > h + m) b.y = -m;
  }

  // Separation, Alignment, Cohesion + Flucht vor allen threats ({x, y, radius}).
  function stepBoids(boids, threats, w, h, dt) {
    const view2 = CFG.viewRadius * CFG.viewRadius, sep2 = CFG.sepRadius * CFG.sepRadius;
    for (const b of boids) {
      let sx = 0, sy = 0, ax = 0, ay = 0, cx = 0, cy = 0, n = 0;
      for (const o of boids) {
        if (o === b) continue;
        const dx = o.x - b.x, dy = o.y - b.y, d2 = dx * dx + dy * dy;
        if (d2 > view2) continue;
        n++; ax += o.vx; ay += o.vy; cx += o.x; cy += o.y;
        if (d2 < sep2) { sx -= dx; sy -= dy; }
      }
      if (n) {
        b.vx += sx * CFG.wSep + (ax / n - b.vx) * CFG.wAli + (cx / n - b.x) * CFG.wCoh;
        b.vy += sy * CFG.wSep + (ay / n - b.vy) * CFG.wAli + (cy / n - b.y) * CFG.wCoh;
      }
      for (const t of threats) flee(b, t, CFG.wFlee);
      clampSpeed(b, CFG.minSpeed, CFG.maxSpeed);
    }
    for (const b of boids) { b.x += b.vx * dt; b.y += b.vy * dt; wrap(b, w, h); }
  }

  // Der Hai patrouilliert zwischen zufälligen Wegpunkten und weicht nur dem Pointer aus.
  function stepShark(s, pointer, w, h, dt, rand) {
    const dx = s.tx - s.x, dy = s.ty - s.y;
    if (dx * dx + dy * dy < 3600) { s.tx = rand() * w; s.ty = rand() * h; }
    const d = Math.hypot(dx, dy) || 1e-6;
    s.vx += (dx / d) * CFG.sharkTurn * dt;
    s.vy += (dy / d) * CFG.sharkTurn * dt;
    if (pointer) flee(s, pointer, CFG.wFlee);
    clampSpeed(s, CFG.sharkSpeed * 0.6, CFG.sharkSpeed);
    s.x += s.vx * dt; s.y += s.vy * dt;
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { CFG, makeBoid, stepBoids, stepShark };
    return;
  }

  const FISH_ALPHA = 0.35;
  const STILL_FISH = 8;
  const root = document.documentElement;
  const detail = document.body.classList.contains("detail");
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const canvas = document.createElement("canvas");
  canvas.className = "sea";
  canvas.setAttribute("aria-hidden", "true");
  document.body.prepend(canvas);
  const ctx = canvas.getContext("2d");

  let w = 0, h = 0, pointer = null, raf = 0, last = 0;
  const clamp01 = (v) => Math.min(1, Math.max(0, v));
  const depth = () => parseFloat(root.style.getPropertyValue("--depth")) || 0;

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    w = window.innerWidth; h = window.innerHeight;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();

  const fishCount = detail ? 0 : still ? STILL_FISH : (window.innerWidth < 900 ? 14 : 36);
  const boids = Array.from({ length: fishCount }, () => makeBoid(Math.random, w, h));
  boids.forEach((b) => { b.size = 5 + Math.random() * 4; });
  const shark = detail || still ? null
    : { x: -80, y: h * 0.6, vx: 1, vy: 0, tx: w * 0.7, ty: h * 0.4 };
  const small = window.innerWidth < 900;
  const bubbles = Array.from({ length: small ? 8 : 18 }, () => ({
    x: Math.random() * w, y: Math.random() * h, r: 1 + Math.random() * 2.5, v: 0.3 + Math.random() * 0.5,
  }));
  const snow = Array.from({ length: small ? 16 : 40 }, (_, i) => ({
    x: Math.random() * w, y: Math.random() * h, r: 0.6 + Math.random() * 1.2,
    v: 0.08 + Math.random() * 0.18, amber: i % 7 === 0,
  }));

  function update(dt) {
    const threats = [];
    if (pointer) threats.push(pointer);
    if (shark) {
      stepShark(shark, pointer, w, h, dt, Math.random);
      threats.push({ x: shark.x, y: shark.y, radius: CFG.sharkRadius });
    }
    stepBoids(boids, threats, w, h, dt);
    for (const p of bubbles) { p.y -= p.v * dt; if (p.y < -10) { p.y = h + 10; p.x = Math.random() * w; } }
    for (const p of snow) { p.y += p.v * dt; if (p.y > h + 10) { p.y = -10; p.x = Math.random() * w; } }
  }

  function drawFish(b, alpha) {
    const s = b.size;
    ctx.save();
    ctx.translate(b.x, b.y); ctx.rotate(Math.atan2(b.vy, b.vx));
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.ellipse(0, 0, s, s * 0.42, 0, 0, Math.PI * 2);
    ctx.moveTo(-s * 0.8, 0); ctx.lineTo(-s * 1.7, -s * 0.6); ctx.lineTo(-s * 1.7, s * 0.6);
    ctx.closePath(); ctx.fill();
    ctx.restore();
  }

  function drawShark(s, alpha) {
    const a = Math.atan2(s.vy, s.vx), L = 46;
    ctx.save();
    ctx.translate(s.x, s.y); ctx.rotate(a);
    if (Math.abs(a) > Math.PI / 2) ctx.scale(1, -1); // Rückenflosse bleibt oben
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.moveTo(L, 0);
    ctx.quadraticCurveTo(L * 0.3, -L * 0.32, -L * 0.7, -L * 0.06);
    ctx.lineTo(-L * 1.25, -L * 0.42); ctx.lineTo(-L * 1.05, 0); ctx.lineTo(-L * 1.25, L * 0.3);
    ctx.lineTo(-L * 0.7, L * 0.06);
    ctx.quadraticCurveTo(L * 0.3, L * 0.26, L, 0);
    ctx.moveTo(L * 0.05, -L * 0.2); ctx.lineTo(-L * 0.25, -L * 0.62); ctx.lineTo(-L * 0.4, -L * 0.16);
    ctx.fill();
    ctx.restore();
  }

  function draw() {
    const d = depth();
    ctx.clearRect(0, 0, w, h);
    // Schwarm am dichtesten um 60 m (d = 0.3)
    const school = clamp01(1 - Math.abs(d - 0.3) * 1.1);
    ctx.fillStyle = "#E8EEF2";
    for (const b of boids) drawFish(b, FISH_ALPHA * Math.max(0.4, school));
    if (shark) drawShark(shark, 0.28);
    const bubbleAlpha = 0.25 * clamp01(1 - d * 4);
    if (bubbleAlpha > 0) {
      ctx.globalAlpha = bubbleAlpha; ctx.strokeStyle = "#E8EEF2"; ctx.lineWidth = 1;
      for (const p of bubbles) { ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.stroke(); }
    }
    const snowAlpha = clamp01((d - 0.5) * 4);
    if (snowAlpha > 0) {
      for (const p of snow) {
        ctx.globalAlpha = (p.amber ? 0.55 : 0.3) * snowAlpha;
        ctx.fillStyle = p.amber ? "#FFB454" : "#E8EEF2";
        ctx.beginPath(); ctx.arc(p.x, p.y, p.amber ? p.r * 1.6 : p.r, 0, Math.PI * 2); ctx.fill();
      }
    }
    ctx.globalAlpha = 1;
  }

  if (still) {
    draw();
    window.addEventListener("resize", () => { resize(); draw(); });
    return;
  }

  function frame(t) {
    const dt = Math.min((t - last) / 16.67, 3) || 1;
    last = t;
    update(dt); draw();
    raf = requestAnimationFrame(frame);
  }
  function start() { if (!raf) { last = performance.now(); raf = requestAnimationFrame(frame); } }
  function stop() { cancelAnimationFrame(raf); raf = 0; }

  window.addEventListener("resize", resize);
  window.addEventListener("pointermove", (e) => {
    pointer = { x: e.clientX, y: e.clientY, radius: CFG.pointerRadius };
  }, { passive: true });
  document.addEventListener("pointerleave", () => { pointer = null; });
  window.addEventListener("pointerup", (e) => { if (e.pointerType !== "mouse") pointer = null; });
  document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); else start(); });
  start();
})();
