# -*- coding: utf-8 -*-
"""VARIANTE B: los 4 bornes banana Pomona 73096 se sueldan en la PCB, en lugar del J3 + arnés.
Ajusta los JSON de colocación, pistas, zonas y serigrafía de la v2 (copia) y documenta cada cambio:
  - placa de 40 x 40 a 67 x 40 mm: franja de 27 mm a la derecha con los 4 bornes en 2 x 2;
  - columna negra (x = 147): P2 = S- arriba, C2 = F- abajo; columna roja (x = 160): P1 = S+ arriba, C1 = F+ abajo;
  - se retira J3; las pistas que llegaban a sus pads se prolongan hasta los bornes:
      F+ : 1 mm en F.Cu directo desde los pines de fuente de Q1 (antes 0,25 mm en In2 hasta J3);
      F- : 1 mm en In2 desde el mismo trazo de R_SH;
      S+ / S- : par de 0,25 mm en F.Cu, paralelo, entre las filas de bornes.
Se ejecuta una vez sobre la copia (idempotente)."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: os.path.join(HERE, f)
XR = 167.0                                   # nuevo borde derecho (X0 = 100 -> W = 67)
XB, XRd, YP, YC = 147.0, 160.0, 110.5, 129.5  # columnas negra/roja, filas P (sentido) y C (corriente)

PL = json.load(open(J("placement_v2.json")))
PL.pop("J3", None)
PL.update({"J4": [XRd, YC, 0], "J5": [XRd, YP, 0], "J6": [XB, YP, 0], "J7": [XB, YC, 0]})
json.dump(PL, open(J("placement_v2.json"), "w"), indent=0)

R = json.load(open(J("routes_v2.json")))
def touches_j3(t):
    pts = [tuple(t["a"])] + ([tuple(t["b"])] if "b" in t else [])
    return any(abs(x - 133.0) < 0.01 and abs(y - 128.6) < 0.01 for x, y in pts)
# fuera: tramo de F+ en In2 hacia J3 (2 pistas) y su vía; se reemplazan por la pista de 1 mm en F.Cu
R = [t for t in R if not t.get("varB")]
R = [t for t in R if not (t["net"] == "/F_PLUS" and (touches_j3(t) or (t["type"] == "track" and t["layer"] == "In2.Cu")
                                                       or t["type"] == "via"))]
def trk(net, pts, w, layer):
    for a, b in zip(pts, pts[1:]):
        R.append({"type": "track", "a": list(a), "b": list(b), "w": w, "layer": layer, "net": net, "pre": True, "varB": True})
def via(net, p):
    R.append({"type": "via", "a": list(p), "net": net, "d": 0.45, "drill": 0.2, "pre": True, "varB": True})
trk("/F_PLUS", [(129.835, 132.33), (157.17, 132.33), (XRd, YC)], 1.0, "F.Cu")
trk("/F_MINUS", [(133.0, 122.6), (135.6, 120.0), (144.5, 120.0), (XB, 122.5), (XB, YC)], 1.0, "In2.Cu")
via("/RX_N", (133.0, 124.6)); trk("/RX_N", [(133.0, 124.6), (138.2, 119.4), (XB, 119.4), (XB, YP)], 0.25, "F.Cu")
via("/RX_P", (133.0, 126.6)); trk("/RX_P", [(133.0, 126.6), (139.0, 120.6), (XRd, 120.6), (XRd, YP)], 0.25, "F.Cu")
json.dump(R, open(J("routes_v2.json"), "w"))

for f in ["zones_v2.json", "zones_extra_v2.json"]:
    Z = json.load(open(J(f)))
    for z in Z:
        z["pts"] = [[XR + 0.05 if abs(x - 140.05) < 1e-6 else x, y] for x, y in z["pts"]]
    json.dump(Z, open(J(f), "w"))

S = [s for s in json.load(open(J("silk_v2.json"))) if s["t"] not in ("F-", "S-", "S+", "F+", "KELVIN")]
S = [s for s in S if not s.get("varB")]
for x, col in [(XB, "NEGRO"), (XRd, "ROJO")]:
    for y, lab in [(YP, "P2 S-" if x == XB else "P1 S+"), (YC, "C2 F-" if x == XB else "C1 F+")]:
        S.append({"t": lab, "x": x, "y": y - 3.2, "varB": True})
        S.append({"t": col, "x": x, "y": y + 3.2, "varB": True})
json.dump(S, open(J("silk_v2.json"), "w"))
print("variante B aplicada:", len(R), "elementos de ruteo")
