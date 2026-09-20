"""Testet den reinen Boids-Kern aus sea.js in node — kein Browser, kein DOM."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node nicht installiert")

PRELUDE = """
const s = require("./sea.js");
let seed = 1;
const rand = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
"""


def _run(body):
    res = subprocess.run([NODE, "-e", PRELUDE + body], cwd=ROOT, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    return json.loads(res.stdout)


def test_a_boid_swimming_at_a_threat_turns_and_flees():
    out = _run("""
      const b = {x: 100, y: 100, vx: 1, vy: 0};
      const t = {x: 130, y: 100, radius: 140};
      for (let i = 0; i < 60; i++) s.stepBoids([b], [t], 800, 600, 1);
      console.log(JSON.stringify({dist: Math.hypot(b.x - t.x, b.y - t.y)}));
    """)
    assert out["dist"] > 100, f"Fisch flieht nicht (Abstand {out['dist']:.1f} px, Start 30 px)"


def test_speed_and_bounds_hold_over_a_long_run():
    out = _run("""
      const boids = Array.from({length: 36}, () => s.makeBoid(rand, 800, 600));
      const shark = {x: 400, y: 300, vx: 1, vy: 0, tx: 100, ty: 100};
      let ok = true;
      for (let i = 0; i < 600; i++) {
        s.stepShark(shark, null, 800, 600, 1, rand);
        s.stepBoids(boids, [{x: shark.x, y: shark.y, radius: s.CFG.sharkRadius}], 800, 600, 1);
        for (const q of boids) {
          const sp = Math.hypot(q.vx, q.vy), m = s.CFG.margin + 0.01;
          if (sp > s.CFG.maxSpeed + 1e-6 || sp < s.CFG.minSpeed - 1e-6) ok = false;
          if (q.x < -m || q.x > 800 + m || q.y < -m || q.y > 600 + m) ok = false;
        }
      }
      console.log(JSON.stringify({ok, sharkSpeed: Math.hypot(shark.vx, shark.vy)}));
    """)
    assert out["ok"], "ein Boid hat Tempo- oder Randgrenzen verlassen"
    assert out["sharkSpeed"] <= 1.2 + 1e-6


def test_neighbours_align_their_heading():
    out = _run("""
      const a = {x: 100, y: 100, vx: 1, vy: 0}, b = {x: 100, y: 140, vx: 0, vy: 1};
      for (let i = 0; i < 40; i++) s.stepBoids([a, b], [], 800, 600, 1);
      const deg = Math.abs(Math.atan2(a.vy, a.vx) - Math.atan2(b.vy, b.vx)) * 180 / Math.PI;
      console.log(JSON.stringify({deg}));
    """)
    assert out["deg"] < 45, f"Nachbarn richten sich nicht aus ({out['deg']:.1f}° statt 90° Start)"


def test_pointer_radius_matches_the_spec():
    out = _run("console.log(JSON.stringify(s.CFG));")
    assert out["pointerRadius"] == 140
    assert out["wFlee"] > out["minSpeed"], "Flucht schwächer als Mindesttempo — Fisch schwimmt in die Bedrohung"


def test_a_boid_leaving_the_camera_band_comes_back_on_the_other_side():
    out = _run("""
      const top = 1000, h = 600, m = s.CFG.margin;
      const up = {x: 123, y: top - m + 0.5, vx: 0, vy: -1};
      const down = {x: 456, y: top + h + m - 0.5, vx: 0, vy: 1};
      s.stepBoids([up], [], 800, h, 1, top);
      s.stepBoids([down], [], 800, h, 1, top);
      console.log(JSON.stringify({up, down, lo: top - m, hi: top + h + m}));
    """)
    assert out["up"]["y"] == out["hi"], f"oben raus landet nicht unten ({out['up']['y']})"
    assert out["down"]["y"] == out["lo"], f"unten raus landet nicht oben ({out['down']['y']})"
    assert out["up"]["x"] == 123 and out["down"]["x"] == 456, "x springt beim Recyceln"


def test_the_shark_picks_its_waypoints_inside_the_camera_band():
    out = _run("""
      const top = 2000, h = 600;
      const shark = {x: 400, y: top + 300, vx: 1, vy: 0, tx: 400, ty: top + 300};
      const ys = [];
      // 2000 Frames: der Hai braucht ~500 Frames bis zum ersten Wegpunkt (1.2 px/Frame).
      for (let i = 0; i < 2000; i++) { s.stepShark(shark, null, 800, h, 1, rand, top); ys.push(shark.ty); }
      console.log(JSON.stringify({lo: Math.min(...ys), hi: Math.max(...ys), n: new Set(ys).size}));
    """)
    assert out["n"] > 1, "der Hai sucht sich nie ein neues Ziel"
    assert 2000 <= out["lo"] and out["hi"] <= 2600, \
        f"Wegpunkt außerhalb des Kamera-Bandes ({out['lo']:.0f}..{out['hi']:.0f} statt 2000..2600)"


def test_top_zero_reproduces_the_viewport_only_behaviour():
    out = _run("""
      seed = 1; const a = Array.from({length: 12}, () => s.makeBoid(rand, 800, 600));
      seed = 1; const b = Array.from({length: 12}, () => s.makeBoid(rand, 800, 600));
      for (let i = 0; i < 120; i++) {
        s.stepBoids(a, [], 800, 600, 1);
        s.stepBoids(b, [], 800, 600, 1, 0);
      }
      console.log(JSON.stringify({same: JSON.stringify(a) === JSON.stringify(b)}));
    """)
    assert out["same"], "top = 0 weicht vom bisherigen Verhalten ab"
