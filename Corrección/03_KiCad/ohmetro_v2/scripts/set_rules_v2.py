# Reglas de diseño v2 (JLCPCB 4 capas): holgura 0,15 mm, pista 0,15 mm, vía 0,40/0,20 mm, agujero-agujero 0,25 mm,
# cobre-borde 0,3 mm, agujero-cobre 0,15 mm (la huella USB4105 trae 0,194 mm pad-NPTH), texto mín. 0,8 mm.
import json, sys
p = sys.argv[1]; d = json.load(open(p, encoding="utf-8"))
for c in d["net_settings"]["classes"]:
    if c["name"] == "Default":
        c.update({"clearance": 0.15, "track_width": 0.15, "via_diameter": 0.45, "via_drill": 0.2})
d["board"]["design_settings"]["rules"].update({"min_clearance": 0.15, "min_copper_edge_clearance": 0.3, "min_track_width": 0.15,
    "min_via_diameter": 0.4, "min_through_hole_diameter": 0.2, "min_via_annular_width": 0.1, "min_hole_to_hole": 0.25,
    "min_hole_clearance": 0.15, "min_text_height": 0.8})
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
