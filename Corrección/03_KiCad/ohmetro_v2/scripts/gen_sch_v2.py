# -*- coding: utf-8 -*-
"""Genera ohmetro_v2.kicad_sch (mejoras 1–4 y ESP32-C3-MINI-1 integrado) y la biblioteca ohmetro.kicad_sym."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from kicad_sch_lib import Sheet, flat_symbol
import design_v2 as D

OUT = os.path.join(HERE, "..")

def sym_box(name, left, right, ref="U", width=20.32, stack_names=("GND",)):
    """Símbolo rectangular; pines con nombre en stack_names se apilan (uno visible)."""
    def side(lst, x, ang):
        out, slot, stacked = [], 0, {}
        for num, nm, typ in lst:
            if nm in stack_names and nm in stacked:
                y = stacked[nm]; hide = " hide"
            else:
                y = -2.54 * slot; slot += 1; stacked[nm] = y; hide = ""
            out.append((num, nm, typ, x, y, ang, hide))
        return out, slot
    L, nl = side(left, -width / 2 - 3.81, 0)
    R, nr = side(right, width / 2 + 3.81, 180)
    n = max(nl, nr)
    top = 2.54; bot = -2.54 * n
    pins = []
    for num, nm, typ, x, y, ang, hide in L + R:
        y += 2.54 * ((n - 1) // 2)
        y = round(y / 1.27) * 1.27
        pins.append(f'(pin {typ} line (at {x:.2f} {y:.2f} {ang}) (length 3.81){hide} '
                    f'(name "{nm}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))')
    ytop = 2.54 * ((n - 1) // 2) + 2.54
    ybot = ytop - 2.54 * (n + 1)
    return f'''(symbol "ohmetro:{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "{ref}" (at 0 {ytop + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
      (property "Value" "{name}" (at 0 {ybot - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "{name}_0_1" (rectangle (start {-width/2:.2f} {ytop:.2f}) (end {width/2:.2f} {ybot:.2f})
          (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "{name}_1_1" {" ".join(pins)}))'''

sh = Sheet("ohmetro_v2", "Miliohmímetro Kelvin v2 (KiCad)", paper="A2")
for lib, name in [("Device", "R"), ("Device", "C"), ("Device", "L"), ("Device", "LED"), ("Device", "R_Shunt"),
                  ("Device", "NetTie_2"), ("Connector", "USB_C_Receptacle_USB2.0_16P"), ("Connector", "TestPoint"),
                  ("Connector_Generic", "Conn_01x02"), ("Connector_Generic", "Conn_01x04"), ("Connector", "Conn_01x01_Socket"),
                  ("Power_Protection", "USBLC6-2SC6"), ("Battery_Management", "BQ24074RGT"),
                  ("74xGxx", "SN74LVC1G125DCK"), ("Amplifier_Operational", "OPA376xxDCK"),
                  ("Transistor_FET", "Q_NMOS_GDS"), ("Transistor_FET", "Q_Dual_NMOS_S1G1D2S2G2D1"),
                  ("Switch", "SW_Push"), ("power", "PWR_FLAG")]:
    sh.add_lib(f"{lib}:{name}", flat_symbol(lib, name))
custom = {
    "ADS1220_RVA": sym_box("ADS1220_RVA", *D.ADS1220_RVA_PINS, width=22.86, stack_names=()),
    "TPS63802DLA": sym_box("TPS63802DLA", *D.TPS63802_PINS, width=15.24, stack_names=()),
    "ESP32-C3-MINI-1": sym_box("ESP32-C3-MINI-1", D.ESP_LEFT[:3] + D.ESP_LEFT[3:len(D.GNDP) + 2], D.ESP_RIGHT, width=17.78),
}
for k, v in custom.items():
    sh.add_lib(f"ohmetro:{k}", v)
open(os.path.join(OUT, "ohmetro.kicad_sym"), "w", encoding="utf-8").write(
    '(kicad_symbol_lib (version 20231120) (generator "ohmetro_scripts")\n' +
    "\n".join(v.replace(f'(symbol "ohmetro:{k}"', f'(symbol "{k}"', 1) for k, v in custom.items()) + "\n)\n")

# pines del OPA376 (DCK) por nombre
from kicad_sch_lib import pins_of
# ESP32: los NC no están en el símbolo
lib, val, fp, nets, mpn, unit = D.P["U1"]
D.P["U1"] = (lib, val, fp, {k: v for k, v in nets.items() if k not in D.NCP}, mpn, unit)

POS = {
 # Bloque 1 (A2 = 594 x 420 mm)
 "J1": (35, 70), "R1": (20, 115), "R2": (30, 115), "D1": (80, 105), "U2": (140, 75), "C1": (95, 50),
 "C2": (195, 45), "C3": (210, 45), "R3": (110, 135), "R4": (122, 135), "R5": (134, 135), "R6": (146, 135),
 "R7": (158, 135), "R8": (175, 120), "R9": (187, 120), "R10": (199, 120), "D2": (199, 140),
 "J2": (235, 70), "RDIV1": (255, 55), "RDIV2": (255, 80), "CDIV": (268, 80), "NT1": (240, 100),
 "U3": (330, 70), "L1": (330, 40), "C4": (290, 100), "C5": (380, 50), "R11": (380, 80), "R12": (380, 105),
 # Bloque 2 (flujo de señal, con cables)
 "U5": (45, 205), "C6": (30, 240), "RM10": (18, 240), "RDV1": (75, 192), "RST1": (90, 235), "CST1": (102, 235),
 "RA": (116, 235), "RB": (130, 235), "Q3": (116, 262), "Q3B": (130, 262), "R13": (100, 268), "R14": (146, 268),
 "U4": (175, 205), "C7": (163, 240), "RFB": (165, 172), "CF1": (190, 172), "RG1": (210, 200), "RG2": (222, 228),
 "Q1": (245, 200), "C8": (280, 178), "C9": (292, 178), "J4": (296, 212), "J5": (296, 224), "J6": (296, 236), "J7": (296, 248), "RSH": (255, 252),
 # Bloque 3
 "U6": (480, 215), "RADS1": (360, 190), "RADS2": (375, 190), "RADS3": (390, 190), "RADS4": (405, 190),
 "CADS1": (368, 232), "CADS2": (398, 232), "R15": (540, 175), "C10": (553, 175), "C11": (565, 175),
 "C12": (540, 255), "R16": (553, 255),
 # Bloque 4
 "U1": (130, 345), "C13": (40, 320), "C14": (52, 320), "R17": (40, 365), "C15": (52, 365), "SW1": (70, 385),
 "R18": (230, 320), "SW2": (245, 345), "TP1": (230, 380), "TP2": (245, 380), "TP3": (260, 380), "TP4": (275, 380),
}
sh.wired = set()   # redibujo con cables pendiente (unía redes); se usa la versión con etiquetas verificada
for ref, (lib_id, val, fp, nets, mpn, unit) in D.P.items():
    x, y = POS[ref]
    sh.place(lib_id, ref[:-1] if ref == "Q3B" else ref, val, fp, x, y, nets, mpn, unit=unit,
             in_bom=not (ref.startswith("TP") or ref.startswith("NT")), on_board=ref not in D.OFF_BOARD)
sh.connect_wired()
for i, (net, x, y) in enumerate([("GND", 300, 130), ("PGND", 315, 130), ("VBUS", 330, 130), ("AVDD", 345, 130)]):
    sh.place("power:PWR_FLAG", f"#FLG0{i+1}", "PWR_FLAG", "", x, y, {"1": net})

for (x1, y1, x2, y2, t) in [(8, 22, 405, 150, "Bloque 1: USB-C, cargador BQ24074 (power-path), batería Li-Po plana y regulador TPS63802 3,3 V"),
                            (8, 155, 320, 285, "Bloque 2: fuente de corriente pulsada (base v1) con selección electrónica de rango por VSET y shunt Kelvin único"),
                            (330, 155, 585, 285, "Bloque 3: ADS1220 (referencia interna 2,048 V, medición ratiométrica secuencial)"),
                            (8, 292, 585, 405, "Bloque 4: ESP32-C3-MINI-1 integrado (USB nativo, BOOT/RESET, UART en pads de prueba)")]:
    sh.rect(x1, y1, x2, y2); sh.text(t, x1 + 2, y1 + 5, 2.0)
notes = ["Mejora 1 (variante B): 4 bornes banana de seguridad de 4 mm soldados en la PCB, Pomona 73096 (J4 C1=F+ y J5 P1=S+ rojos; J6 P2=S- y J7 C2=F- negros), sin arnés. J2 batería JST PH 2P polarizado.",
         "Mejora 2: sin interruptor mecánico. RANGE_A (GPIO3) conecta RA y RANGE_B (GPIO8) conecta RB en paralelo con RST: VSET = 97 / 48,7 / 9,5 mV -> 0,97 / 0,49 / 0,095 A.",
         "            El RDS(on) de Q3 solo afecta a VSET; no está en el lazo ni en el sensado Kelvin. Shunt único RSH 0,1 ohm 0,1 % 15 ppm/°C de 4 terminales (sensado AIN2/AIN3).",
         "Mejora 3: digipot descartado (wiper 100 ohm, 2,5 mA máx., ±20 %); se mantienen los 3 rangos de la v1 (ver calculos/fase2_calculos.md).",
         "Mejora 4: TP4056 -> BQ24074 (power-path, ICHG = 376 mA <= 0,5 C de la Jauch LP603048JK 820 mAh, OVP, temporizador).",
         "Corrección v1: compensación del lazo con RFB 1k + CF 1n (margen de fase 67-84° en LTspice); ADS1220 con referencia interna (la v1 tenía VREF = 97 mV < 0,75 V mín.).",
         "Estrella GND/PGND en NT1 junto al negativo de la batería y el extremo inferior del shunt."]
for i, n in enumerate(notes):
    sh.text(n, 335, 26 + i * 6 if False else 290 + 0 * i, 1.4, bold=False) if False else None
for i, n in enumerate(notes):
    sh.text(n, 10, 410 + 0 if False else 288 + 0, 1.4, bold=False) if False else None
y0 = 300
for i, n in enumerate(notes):
    sh.text(n, 300, y0 + i * 5, 1.4, bold=False)
sh.write(os.path.join(OUT, "ohmetro_v2.kicad_sch"), "2026-11-09", "2.0 (Fase 2)", "UIS - E3T - Grupo C1B-A1A")
print("ok")
