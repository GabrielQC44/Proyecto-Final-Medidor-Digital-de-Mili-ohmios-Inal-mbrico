# -*- coding: utf-8 -*-
"""Ruteo iterativo ("fallidas primero"): repite el ruteo poniendo al frente las conexiones que fallaron
en la pasada anterior y guarda la mejor solución. uso: route_iter.py board.json tasks.json out.json [iter]"""
import sys, json, subprocess, os, tempfile
board, tasks_f, out_f = sys.argv[1:4]
N = int(sys.argv[4]) if len(sys.argv) > 4 else 6
here = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(tasks_f))
tasks = cfg["tasks"]
key = lambda t: (t["net"], tuple(t["a"]), tuple(t["b"]), bool(t.get("fanout")))
best = None
for it in range(N):
    tmp_t = tempfile.mktemp(suffix=".json"); tmp_o = tempfile.mktemp(suffix=".json")
    json.dump(dict(cfg, tasks=tasks), open(tmp_t, "w"))
    subprocess.run([sys.executable, "-I", os.path.join(here, "router.py"), board, tmp_t, tmp_o], capture_output=True, text=True)
    res = json.load(open(tmp_o))
    fails = [r["task"] for r in res if r["type"] == "fail"]
    sig = [f for f in fails if not f.get("fanout")]
    score = len(sig) * 10 + (len(fails) - len(sig))
    print(f"pasada {it+1}: fallas de señal {len(sig)}, fanouts GND sin vía {len(fails) - len(sig)}")
    if best is None or score < best[0]:
        best = (score, res, fails)
    if not sig:
        break
    fk = {key(f) for f in fails}
    tasks = [t for t in tasks if key(t) in fk and not t.get("fanout")] + [t for t in tasks if not (key(t) in fk and not t.get("fanout"))]
json.dump(best[1], open(out_f, "w"), indent=1)
print("mejor: fallas", [(f["net"], f["a"]) for f in best[2]])
