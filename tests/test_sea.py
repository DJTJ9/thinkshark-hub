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
