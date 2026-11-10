# -*- coding: utf-8 -*-
"""
PCB v2, VARIANTE B (bornes banana en la PCB): 67 x 40 mm, 4 capas (F.Cu señal/potencia, In1 GND sólido, In2 señal + VSYS, B.Cu GND).
Componentes solo en la cara superior; la cara inferior queda plana para pegar la batería Li-Po.
Ejecutar con el Python de KiCad. Lee placement_v2.json, routes_v2.json (pistas) y zones del propio script.
"""
import os, sys, json, re, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pcbnew
import design_v2 as D

ROOT = os.path.abspath(os.path.join(HERE, ".."))
STD = "C:/Program Files/KiCad/10.0/share/kicad/footprints/"
X0, Y0, W, H = 100.0, 100.0, 67.0, 40.0   # VARIANTE B: +27 mm para los bornes banana
mm = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(mm(x), mm(y))

# redes desde la netlist exportada del esquemático
nt = open(os.path.join(ROOT, "ohmetro_v2.net"), encoding="utf-8").read()
PADNET = {}
for blk in re.split(r'\(net\s*\(code', nt[nt.index("(nets"):])[1:]:
    nm = re.search(r'\(name "([^"]*)"\)', blk).group(1)
    for a, b in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk):
        PADNET[(a, b)] = nm

board = pcbnew.BOARD()
ds = board.GetDesignSettings()
ds.SetCopperLayerCount(4)
ds.m_TrackMinWidth = mm(0.15); ds.m_MinClearance = mm(0.15); ds.m_CopperEdgeClearance = mm(0.3)
ds.m_HoleClearance = mm(0.15)   # USB4105: pad-NPTH de la propia huella = 0,194 mm
ds.m_ViasMinSize = mm(0.40); ds.m_MinThroughDrill = mm(0.2); ds.m_HoleToHoleMin = mm(0.25)
ds.SetBoardThickness(mm(1.6))
nets = {}
def net(name):
    if name not in nets:
        ni = pcbnew.NETINFO_ITEM(board, name); board.Add(ni); nets[name] = ni
    return nets[name]
# contorno con esquinas redondeadas (r = 1 mm)
r = 1.0
pts = [(X0 + r, Y0), (X0 + W - r, Y0), (X0 + W, Y0 + r), (X0 + W, Y0 + H - r), (X0 + W - r, Y0 + H), (X0 + r, Y0 + H), (X0, Y0 + H - r), (X0, Y0 + r)]
segs = [(0, 1), (2, 3), (4, 5), (6, 7)]
for a, b in segs:
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(V(*pts[a])); s.SetEnd(V(*pts[b])); s.SetWidth(mm(0.1)); board.Add(s)
for (cx, cy, sa) in [(X0 + W - r, Y0 + r, -90), (X0 + W - r, Y0 + H - r, 0), (X0 + r, Y0 + H - r, 90), (X0 + r, Y0 + r, 180)]:
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts)
    s.SetCenter(V(cx, cy)); s.SetStart(V(cx + r * math.cos(math.radians(sa)), cy + r * math.sin(math.radians(sa))))
    s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T)); s.SetWidth(mm(0.1)); board.Add(s)

def load_fp(fpid):
    lib, name = fpid.split(":")
    path = os.path.join(ROOT, "ohmetro.pretty") if lib == "ohmetro" else STD + lib + ".pretty"
    f = pcbnew.FootprintLoad(path, name); f.SetFPID(pcbnew.LIB_ID(lib, name)); return f

PL = json.load(open(os.path.join(HERE, "placement_v2.json")))
fps = {}
for ref, (lib, val, fpid, pinnets, mpn, unit) in D.P.items():
    if ref == "Q3B" or ref in D.OFF_BOARD: continue   # Q3B = 2.ª unidad; J4-J7 = bornes en la tapa
    f = load_fp(fpid); f.SetReference(ref); f.SetValue(val)
    f.SetField("MPN", mpn); f.GetField("MPN").SetVisible(False)
    f.Value().SetVisible(False)
    # serigrafía: solo referencias de conectores, pulsadores, LED y puntos de prueba; el resto va a F.Fab (plano de montaje)
    f.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); f.Reference().SetTextThickness(mm(0.15))
    if not re.match(r"^(J1|J2|SW|D2|TP)", ref):   # J4-J7: rótulos propios en serigrafía
        f.Reference().SetLayer(pcbnew.F_Fab)
    if re.match(r"^(TP\d|NT\d)", ref):
        f.SetAttributes(f.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM)
    board.Add(f)
    for p in f.Pads():
        n = PADNET.get((ref, p.GetNumber()))
        if n: p.SetNet(net(n))
    x, y, rot = PL[ref]
    f.SetPosition(V(x, y)); f.SetOrientationDegrees(rot)
    REFPOS = {"D2": (x + 2.4, y), "J2": (129.6, 109.7)}
    if ref in REFPOS:   # referencias reubicadas para no tapar textos/pads
        f.Reference().SetPosition(V(*REFPOS[ref])); f.Reference().SetTextAngleDegrees(0)
    fps[ref] = f

# pistas / vías / zonas generadas por el ruteo
RT = os.path.join(HERE, "routes_v2.json")
if os.path.exists(RT):
    LAY = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}
    for tr in json.load(open(RT)):
        if tr["type"] == "track":
            t = pcbnew.PCB_TRACK(board); t.SetStart(V(*tr["a"])); t.SetEnd(V(*tr["b"])); t.SetWidth(mm(tr["w"]))
            t.SetLayer(LAY[tr["layer"]])
        elif tr["type"] == "via":
            t = pcbnew.PCB_VIA(board); t.SetPosition(V(*tr["a"])); t.SetDrill(mm(tr.get("drill", 0.25))); t.SetWidth(mm(tr.get("d", 0.5)))
        else:
            continue
        t.SetNet(net(tr["net"])); board.Add(t)

ZN = os.path.join(HERE, "zones_v2.json")
ZX = os.path.join(HERE, "zones_extra_v2.json")
if os.path.exists(ZN) and os.path.exists(ZX):
    ZN = ZX                       # GND + cobre térmico VSYS de Q1
if os.path.exists(ZN):
    LAY = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}
    for z in json.load(open(ZN)):
        zone = pcbnew.ZONE(board); zone.SetLayer(LAY[z["layer"]]); zone.SetNet(net(z["net"]))
        o = zone.Outline(); o.NewOutline()
        for x, y in z["pts"]: o.Append(mm(x), mm(y))
        zone.SetAssignedPriority(z.get("prio", 0)); zone.SetLocalClearance(mm(z.get("clr", 0.2)))
        zone.SetMinThickness(mm(0.2))
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)   # sin islas de cobre aisladas
        if z.get("solid"): zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        else:
            zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); zone.SetThermalReliefGap(mm(0.25)); zone.SetThermalReliefSpokeWidth(mm(0.3))
        board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

SK = os.path.join(HERE, "silk_v2.json")
if os.path.exists(SK):
    for it in json.load(open(SK)):
        tx = pcbnew.PCB_TEXT(board); tx.SetText(it["t"]); tx.SetLayer(pcbnew.F_SilkS); tx.SetPosition(V(it["x"], it["y"]))
        tx.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); tx.SetTextThickness(mm(0.15)); board.Add(tx)

out = os.path.join(ROOT, "ohmetro_v2.kicad_pcb")
board.Save(out)
print("guardado", out, "huellas", len(fps))
