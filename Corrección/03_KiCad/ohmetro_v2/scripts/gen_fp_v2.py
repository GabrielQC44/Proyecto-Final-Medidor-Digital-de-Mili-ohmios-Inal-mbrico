# -*- coding: utf-8 -*-
"""Huellas propias v2 (dimensiones de las hojas de datos oficiales):
 - TI_DLA_VSON-HR-10_2x3mm: TPS63802 DLA0010A 'Example board layout' (SLVSEU9D, p. 36).
 - Infineon_PQFN-8_3.3x3.3mm: PowerPAK 1212-8 de KiCad (mismo estándar PQFN 3,3x3,3 P0,65 del IRLHM620) renumerado G=1, D=2, S=3.
 - R_Shunt_VPG_CSM2512S_4T: CSM2512S land pattern (VPG doc. 63145 rev. 4-Mar-15, Fig. 2): l=4.06 b=3.68 e=1.39 a=1.65 c=1.14 d=0.53.
 - ESP32-C3-MINI-1: copiada sin cambios de la biblioteca oficial github.com/espressif/kicad-libraries (incluye zona de exclusión de antena)."""
import os, re, uuid
OUT = os.path.join(os.path.dirname(__file__), "..", "ohmetro.pretty")
U = lambda: str(uuid.uuid4())
def pad(n, x, y, w, h, shape="roundrect", extra=""):
    rr = " (roundrect_rratio 0.2)" if shape == "roundrect" else ""
    return f'(pad "{n}" smd {shape} (at {x:.4f} {y:.4f}) (size {w:.4f} {h:.4f}) (layers "F.Cu" "F.Paste" "F.Mask"){rr}{extra} (uuid "{U()}"))'
def fp(name, descr, pads, body, extra=[]):
    x1, y1, x2, y2 = body
    t = [f'(property "Reference" "REF**" (at 0 {y1-1:.2f} 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))',
         f'(property "Value" "{name}" (at 0 {y2+1:.2f} 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))',
         f'(fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab") (uuid "{U()}"))',
         f'(fp_rect (start {x1-0.25} {y1-0.25}) (end {x2+0.25} {y2+0.25}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "{U()}"))'] + extra + pads
    open(os.path.join(OUT, name + ".kicad_mod"), "w", encoding="utf-8").write(
        f'(footprint "{name}" (version 20240108) (generator "ohmetro_scripts") (layer "F.Cu")\n (descr "{descr}")\n (attr smd)\n ' + "\n ".join(t) + "\n)\n")

# --- TPS63802 DLA0010A (origen = centro del encapsulado; Y de KiCad hacia abajo)
p = []
for i, n in enumerate(["1", "2", "3", "4", "5"]):
    p.append(pad(n, -0.9, -1.0 + 0.5 * i, 0.6, 0.25))
for n, y in [("10", -1.0), ("9", -0.5), ("7", 0.5), ("6", 1.0)]:
    p.append(pad(n, 0.75, y, 0.9, 0.25))
p.append(pad("8", 0.55, 0.0, 1.3, 0.25))
dot = f'(fp_circle (center -1.45 -1.35) (end -1.35 -1.35) (stroke (width 0.1) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))'
fp("TI_DLA_VSON-HR-10_2x3mm", "TI DLA0010A VSON-HR 10 pines 2x3 mm (TPS63802), land pattern del datasheet", p, (-1.0, -1.5, 1.0, 1.5), [dot])

# --- PQFN 3.3x3.3 (IRLHM620): copia renumerada de Vishay_PowerPAK_1212-8_Single
src = open("C:/Program Files/KiCad/10.0/share/kicad/footprints/Package_SO.pretty/Vishay_PowerPAK_1212-8_Single.kicad_mod", encoding="utf-8").read()
ren = {"1": "3", "2": "3", "3": "3", "4": "1", "5": "2", "6": "2", "7": "2", "8": "2", "9": "2"}
src = re.sub(r'\(pad "(\d)"', lambda m: f'(pad "{ren.get(m.group(1), m.group(1))}"', src)
src = src.replace('(footprint "Vishay_PowerPAK_1212-8_Single"', '(footprint "Infineon_PQFN-8_3.3x3.3mm"', 1)
src = re.sub(r'\(descr "[^"]*"\)', '(descr "PQFN 3,3x3,3 mm P0,65 (IRLHM620): land pattern estándar PowerPAK 1212-8; pads G=1, D=2 (5-8 + EP), S=3 (1-3)")', src, 1)
open(os.path.join(OUT, "Infineon_PQFN-8_3.3x3.3mm.kicad_mod"), "w", encoding="utf-8").write(src)

# --- CSM2512S 4 terminales: 1=I1, 2=E1, 3=E2, 4=I2 (símbolo Device:R_Shunt: 1/4 corriente, 2/3 sensado)
l, b, e, a, c, d = 4.06, 3.68, 1.39, 1.65, 1.14, 0.53
wI = b - c - d                       # ancho del pad de corriente = 2,01
yI = -b / 2 + wI / 2; yE = b / 2 - c / 2
p = [pad("1", -(l / 2 + a / 2), yI, a, wI), pad("2", -(l / 2 + e / 2), yE, e, c),
     pad("3", (l / 2 + e / 2), yE, e, c), pad("4", (l / 2 + a / 2), yI, a, wI)]
fp("R_Shunt_VPG_CSM2512S_4T", "VPG CSM2512S 4 terminales (I1/I2 corriente, E1/E2 sensado), land pattern doc. 63145", p, (-3.175, -1.5875, 3.175, 1.5875),
   ['(model "${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_2512_6332Metric.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))'])
print("ok", sorted(os.listdir(OUT)))
