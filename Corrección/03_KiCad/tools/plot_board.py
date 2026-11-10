# -*- coding: utf-8 -*-
"""Dibuja el JSON de dump_board.py (inspección rápida). uso: plot_board.py board.json out.png [x1 y1 x2 y2]"""
import sys, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
d = json.load(open(sys.argv[1]))
fig, ax = plt.subplots(figsize=(14, 14))
COL = {"F.Cu": "red", "B.Cu": "blue", "In1.Cu": "green", "In2.Cu": "orange"}
for t in d["tracks"]:
    ax.plot([t["a"][0], t["b"][0]], [t["a"][1], t["b"][1]], color=COL.get(t["layer"], "k"),
            lw=t["w"] * 72 / 25.4 * 14 / ((d["edge"][2] - d["edge"][0]) / 25.4 * 1.0) / 1.0, alpha=.6, solid_capstyle="round")
for p in d["pads"]:
    x1, y1, x2, y2 = p["bbox"]
    c = "purple" if len(p["layers"]) > 1 else ("red" if "F" in p["layers"] else "blue")
    if p["round"]:
        ax.add_patch(Circle((p["x"], p["y"]), (x2 - x1) / 2, color=c, alpha=.5))
    else:
        ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, color=c, alpha=.5))
    ax.text(p["x"], p["y"], f"{p['num']}", fontsize=5, ha="center", va="center", clip_on=True)
for v in d["vias"]:
    ax.add_patch(Circle((v["x"], v["y"]), v["d"] / 2, color="k", alpha=.7))
for f in d["fps"]:
    x1, y1, x2, y2 = f["bbox"]
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, ec="gray", lw=.5, ls="--"))
    ax.text(x1, y1, f["ref"], fontsize=7, color="darkgreen", clip_on=True)
e = d["edge"]
ax.add_patch(Rectangle((e[0], e[1]), e[2] - e[0], e[3] - e[1], fill=False, ec="m"))
if len(sys.argv) > 3:
    x1, y1, x2, y2 = map(float, sys.argv[3:7]); ax.set_xlim(x1, x2); ax.set_ylim(y2, y1)
else:
    ax.set_xlim(e[0] - 2, e[2] + 2); ax.set_ylim(e[3] + 2, e[1] - 2)
ax.set_aspect("equal"); ax.grid(True, lw=.3)
plt.savefig(sys.argv[2], dpi=100, bbox_inches="tight")
