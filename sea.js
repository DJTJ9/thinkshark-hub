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

  // --- Browser-Teil folgt in Task 5 ---
})();
