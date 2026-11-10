# -*- coding: utf-8 -*-
"""Genera las tareas de ruteo de la PCB v2 (por red, árbol mínimo entre pads) y las zonas.
uso: route_plan_v2.py board_dump.json tasks.json zones.json"""
import json, sys, math
d = json.load(open(sys.argv[1]))
X0, Y0, X1, Y1 = d["edge"]

def nn(n): return n.lstrip("/")
pads = {}
for p in d["pads"]:
    if p["net"] and not p["net"].startswith("unconnected"):
        pads.setdefault(nn(p["net"]), []).append(p)

# ancho (mm), capas y orden por red
POWER = {"PGND": 1.0, "F_PLUS": 1.0, "F_MINUS": 1.0, "VSYS": 0.8, "VBAT": 0.8, "VBUS": 0.5, "3V3": 0.4, "SW1": 0.6, "SW2": 0.6}
KELVIN = ["RX_P", "RX_N", "RREF_P", "RREF_N"]
ANALOG = ["AIN0", "AIN1", "AIN2", "AIN3", "VSET", "INN", "OPA_OUT", "GATE", "BUF_Y", "SWA", "SWB", "AVDD", "FB"]
order = ["PGND", "F_PLUS", "F_MINUS", "VSYS", "VBAT", "VBUS", "SW1", "SW2"] + KELVIN + ANALOG + ["3V3", "USB_DP", "USB_DN", "CC1", "CC2"]
rest = sorted(n for n in pads if n not in order and n != "GND")
order += rest

def small(p):
    x1, y1, x2, y2 = p["bbox"]
    return min(x2 - x1, y2 - y1) < 0.55

def mst(pl):
    pts = pl[:]
    used = [pts[0]]; rem = pts[1:]; edges = []
    while rem:
        best = min(((math.hypot(a["x"] - b["x"], a["y"] - b["y"]), a, b) for a in used for b in rem), key=lambda t: t[0])
        edges.append((best[1], best[2])); used.append(best[2]); rem.remove(best[2])
    return edges

def lay(p):
    return ["F.Cu", "In2.Cu", "B.Cu"] if p.get("drill") else ["F.Cu"]

# conexiones cortas dibujadas a mano en routes_v2.json (no se rutean automáticamente)
SKIP = [("3V3", (127.65, 107.6), (127.75, 105.6)), ("SWA", (116.89, 122.8), (117.49, 121.1))]
def skipped(n, a, b):
    for sn, p, q in SKIP:
        if sn == n and ({(round(a["x"], 2), round(a["y"], 2)), (round(b["x"], 2), round(b["y"], 2))} == {p, q}): return True
    return False
tasks = []
for n in order:
    if n not in pads or len(pads[n]) < 2 or n in ("SW1", "SW2"): continue   # SW1/SW2: ruteo manual (routes_v2.json)
    for a, b in mst(pads[n]):
        if skipped(n, a, b): continue
        if n in POWER:
            w = POWER[n]          # ancho completo; si el pin fino no lo permite, el ruteador baja a w_min
            L = ["F.Cu", "In2.Cu"]
        elif n in KELVIN:
            w = 0.2; L = ["F.Cu", "In2.Cu"]
        else:
            w = 0.2 if n in ANALOG else 0.15; L = ["F.Cu", "In2.Cu", "B.Cu"]
        # pads del mismo componente muy cercanos: unirlos en F.Cu
        t = {"net": pads[n][0]["net"], "a": [a["x"], a["y"]], "b": [b["x"], b["y"]],
             "w": w, "layers": L, "a_layers": [l for l in lay(a) if l in L], "b_layers": [l for l in lay(b) if l in L],
             "end_free": 0.05}
        if n in POWER and w >= 0.8:
            t.update({"via_d": 0.6, "via_drill": 0.3})
        else:
            t.update({"via_d": 0.45, "via_drill": 0.2})
        if n in POWER:
            t["w_min"] = 0.25 if (small(a) or small(b)) else min(t["w"], 0.4)
        else:
            t["w_min"] = t["w"]
        tasks.append(t)

# GND: una vía de fanout por pad SMD de GND (los THT ya atraviesan todas las capas)
tht_gnd = [(q["ref"], q["x"], q["y"]) for q in pads.get("GND", []) if q.get("drill")]
for p in pads.get("GND", []):
    if p.get("drill"): continue
    x1, y1, x2, y2 = p["bbox"]
    if any(r == p["ref"] and x1 <= x <= x2 and y1 <= y <= y2 for r, x, y in tht_gnd): continue   # pad con vías térmicas propias
    if p["ref"] == "U1" and p["num"] == "49": continue
    if p["ref"] == "U3" and p["num"] in ("3", "8"): continue                  # GND del TPS63802: ruteo manual      # pads térmicos del módulo: vías fijas
    tasks.append({"net": p["net"], "a": [p["x"], p["y"]], "b": [p["x"], p["y"]], "w": 0.3, "layers": ["F.Cu"], "pad_bbox": p["bbox"],
                  "a_layers": ["F.Cu"], "fanout": True, "via_d": 0.45, "via_drill": 0.2, "end_free": 0.05, "min_off": 0.0})

# orden: 1) fanout GND de pines finos, 2) señales de pines finos (QFN/SON), 3) potencia, 4) Kelvin, 5) resto, 6) otros fanout GND
def fine(xy):
    for p in d["pads"]:
        if abs(p["x"] - xy[0]) < 1e-3 and abs(p["y"] - xy[1]) < 1e-3:
            x1, y1, x2, y2 = p["bbox"]; return min(x2 - x1, y2 - y1) < 0.36
    return False
def prio(t):
    f = fine(t["a"]) or (not t.get("fanout") and fine(t["b"]))
    if t.get("fanout"): return 0 if f else 5
    n = t["net"].lstrip("/")
    if f: return 1
    if n in POWER: return 2
    if n in KELVIN: return 3
    return 4
tasks.sort(key=lambda t: (prio(t), abs(t["a"][0] - t["b"][0]) + abs(t["a"][1] - t["b"][1])))
for t in tasks:
    if t["net"].lstrip("/") in POWER:
        t["layers"] = ["F.Cu", "In2.Cu", "B.Cu"]
        if t["net"].lstrip("/") in ("VSYS", "PGND", "VBAT", "F_PLUS", "F_MINUS"):
            # potencia pulsada: preferir In2 (entre planos GND) y alejarla de la capa analógica superior
            t["layer_cost"] = {"F.Cu": 2.5, "In2.Cu": 1.0, "B.Cu": 1.8}
cfg = {"grid": 0.1, "clearance": 0.2, "hole_to_hole": 0.26, "edge": 0.4, "via_cost": 12, "layers": ["F.Cu", "In2.Cu", "B.Cu"],
       "layer_cost": {"F.Cu": 1.0, "In2.Cu": 1.1, "B.Cu": 1.6}, "tasks": tasks}
json.dump(cfg, open(sys.argv[2], "w"), indent=0)

GNDNAME = pads["GND"][0]["net"]
# zonas: GND en In1 (sólido), B.Cu y F.Cu (relleno); exclusión de antena viene en la huella del ESP32
r = 0.0
outline = [[X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1]]
zones = [{"net": GNDNAME, "layer": "In1.Cu", "pts": outline, "prio": 0, "clr": 0.2, "solid": True},
         {"net": GNDNAME, "layer": "B.Cu", "pts": outline, "prio": 0, "clr": 0.2, "solid": True},
         {"net": GNDNAME, "layer": "F.Cu", "pts": outline, "prio": 0, "clr": 0.25, "solid": True}]
json.dump(zones, open(sys.argv[3], "w"), indent=0)
print("tareas", len(tasks), "redes", len([n for n in order if n in pads]))
