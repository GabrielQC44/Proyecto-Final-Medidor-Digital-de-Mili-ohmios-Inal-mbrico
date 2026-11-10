# -*- coding: utf-8 -*-
"""Vuelca pads, pistas, vías y contorno de un .kicad_pcb a JSON (ejecutar con el Python de KiCad).
uso: python.exe dump_board.py placa.kicad_pcb salida.json"""
import sys, json
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
mm = pcbnew.ToMM
out = {"pads": [], "tracks": [], "vias": [], "edge": None, "fps": [], "zones": []}
bb = b.GetBoardEdgesBoundingBox()
out["edge"] = [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())]
for fp in b.GetFootprints():
    cbb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox() if fp.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else fp.GetBoundingBox(False)
    out["fps"].append({"ref": fp.GetReference(), "x": mm(fp.GetPosition().x), "y": mm(fp.GetPosition().y),
                       "rot": fp.GetOrientationDegrees(), "side": "B" if fp.IsFlipped() else "F",
                       "bbox": [mm(cbb.GetLeft()), mm(cbb.GetTop()), mm(cbb.GetRight()), mm(cbb.GetBottom())]})
    for p in fp.Pads():
        pb = p.GetBoundingBox()
        layers = []
        if p.IsOnLayer(pcbnew.F_Cu): layers.append("F")
        if p.IsOnLayer(pcbnew.B_Cu): layers.append("B")
        for i, L in ((pcbnew.In1_Cu, "I1"), (pcbnew.In2_Cu, "I2")):
            if p.IsOnLayer(i): layers.append(L)
        shp = p.GetShape(pcbnew.F_Cu) if p.IsOnLayer(pcbnew.F_Cu) else p.GetShape(pcbnew.B_Cu)
        out["pads"].append({"ref": fp.GetReference(), "num": p.GetNumber(), "net": p.GetNetname(),
                            "x": mm(p.GetPosition().x), "y": mm(p.GetPosition().y),
                            "bbox": [mm(pb.GetLeft()), mm(pb.GetTop()), mm(pb.GetRight()), mm(pb.GetBottom())],
                            "round": shp == pcbnew.PAD_SHAPE_CIRCLE, "layers": layers,
                            "drill": mm(p.GetDrillSize().x) if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else 0})
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        out["vias"].append({"x": mm(t.GetPosition().x), "y": mm(t.GetPosition().y), "d": mm(t.GetWidth(pcbnew.F_Cu)),
                            "drill": mm(t.GetDrillValue()), "net": t.GetNetname()})
    else:
        out["tracks"].append({"a": [mm(t.GetStart().x), mm(t.GetStart().y)], "b": [mm(t.GetEnd().x), mm(t.GetEnd().y)],
                              "w": mm(t.GetWidth()), "layer": b.GetLayerName(t.GetLayer()), "net": t.GetNetname()})
out["keepouts"] = []
for fp in b.GetFootprints():
    for z in fp.Zones():
        if z.GetIsRuleArea():
            o = z.Outline(); bb = o.BBox()
            out["keepouts"].append({"ref": fp.GetReference(), "bbox": [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())]})
for z in b.Zones():
    o = z.Outline()
    pts = [[mm(o.CVertex(i).x), mm(o.CVertex(i).y)] for i in range(o.TotalVertices())]
    out["zones"].append({"net": z.GetNetname(), "layers": [b.GetLayerName(l) for l in z.GetLayerSet().Seq()], "pts": pts})
json.dump(out, open(sys.argv[2], "w"), indent=0)
print("pads", len(out["pads"]), "tracks", len(out["tracks"]), "vias", len(out["vias"]))
