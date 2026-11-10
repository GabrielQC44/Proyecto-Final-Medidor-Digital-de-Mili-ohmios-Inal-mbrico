# -*- coding: utf-8 -*-
"""BOM v2 (Fase 2). Precios: DigiKey (distribuidor autorizado), cantidad 1, consultados el 2026-11-09.
Genera v2/bom/BOM_v2_fase2.csv y BOM_v2_fase2.md."""
import os, sys, csv
from collections import OrderedDict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import design_v2 as D
OUTD = os.path.abspath(os.path.join(HERE, "..", "..", "..", "bom")); os.makedirs(OUTD, exist_ok=True)
FECHA = "2026-11-09"
DK = lambda mpn: "https://www.digikey.com/en/products/result?keywords=" + mpn.replace("(", "%28").replace(")", "%29").replace("=", "%3D").replace(" ", "%20")
YAGEO_DS = "https://yageogroup.com/content/datasheet/asset/file/PYU-RC_GROUP_51_ROHS_L"
SAMSUNG_DS = "https://product.samsungsem.com/mlcc/"   # ficha por MPN en el sitio del fabricante
# MPN -> (fabricante, descripción/tecnología, tolerancia, TCR/dieléctrico, potencia/tensión, precio USD, datasheet, nota de precio, justificación)
INFO = {
 "ESP32-C3-MINI-1-N4X": ("Espressif", "Módulo Wi-Fi/BLE5 RISC-V, antena PCB, 13,2×16,6 mm, certificado", "—", "—", "3,0–3,6 V", 3.26,
     "https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf", "", "Reemplaza la placa SuperMini; módulo certificado (FCC/CE) con flash de 4 MB; mismo SoC, así que el firmware es compatible"),
 "ADS1220IRVAR": ("Texas Instruments", "ADC ΔΣ de 24 bits, VQFN-16 3,5×3,5 mm", "—", "Ref. int. 2,048 V, 5 ppm/°C típ.", "3,3 V", 9.26,
     "https://www.ti.com/lit/ds/symlink/ads1220.pdf", "", "Mismo ADC de la v1, ahora como chip (el módulo CJMCU no cabe en 4×4 cm); referencia interna"),
 "OPA376AIDCKR": ("Texas Instruments", "Op-amp de precisión RRIO, SC70-5", "Vos 25 µV máx.", "1 µV/°C", "3,3 V", 2.03,
     "https://www.ti.com/lit/ds/symlink/opa376.pdf", "", "Mismo op-amp de la v1, en encapsulado SC70 en vez de SOT-23"),
 "SN74LVC1G125DCKR": ("Texas Instruments", "Buffer tri-state, SC70-5", "—", "—", "3,3 V", 0.13,
     "https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf", "", "Mismo buffer de la v1 (pulso en GPIO10), en SC70"),
 "IRLHM620TRPBF": ("Infineon", "N-MOSFET 20 V, VGS(th) 0,5–1,1 V, PQFN 3,3×3,3 mm", "—", "—", "20 V / Rth_JA 46 °C/W", 2.01,
     "https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlhm620-datasheet-en.pdf", "Stock no publicado; estado Active",
     "Reemplaza el D2PAK (16 veces más área). VGS(th) bajo: más de 1 V de margen de compuerta. SOA DC a 4 V ≈ 5 A; modelo SPICE disponible"),
 "NTZD3154NT1G": ("onsemi", "Doble N-MOSFET 20 V, SOT-563 1,6×1,6 mm", "—", "RDS(on) ≤ 0,7 Ω @2,5 V", "20 V", 0.39,
     "https://www.onsemi.com/pdf/datasheet/ntzd3154n-d.pdf", "", "Conmuta RA/RB en VSET (mejora 2). Su RDS(on) solo afecta a VSET, no al lazo ni al Kelvin"),
 "BQ24074RGTR": ("Texas Instruments", "Cargador Li-Ion 1S con power-path, 1,5 A, VQFN-16 3×3 mm", "I_CHG ±10 %", "—", "OVP 10,5 V (28 V máx.)", 2.43,
     "https://www.ti.com/lit/ds/symlink/bq24074.pdf", "", "Reemplaza al módulo TP4056 (mejora 4): power-path, OVP, temporizador, PGOOD/CHG"),
 "TPS63802DLAR": ("Texas Instruments", "Buck-boost 2 A, VSON-HR-10 2×3 mm", "VFB ±1 %", "—", "1,3–5,5 V", 3.40,
     "https://www.ti.com/lit/ds/symlink/tps63802.pdf", "", "El mismo regulador de la v1, integrado en la placa en vez de módulo"),
 "DFE201612E-R47M=P2": ("Murata", "Bobina de potencia 0,47 µH, 2016 (2,0×1,6×1,2 mm)", "±20 %", "—", "Isat 5,5 A, 26 mΩ", 0.27,
     "https://www.murata.com/en-us/products/productdetail?partno=DFE201612E-R47M%3DP2", "", "Bobina recomendada en el datasheet del TPS63802 (Tabla 10-2)"),
 "USBLC6-2SC6": ("STMicroelectronics", "Protección ESD para USB, SOT-23-6", "—", "—", "VBUS 5 V", 0.54,
     "https://www.st.com/resource/en/datasheet/usblc6-2.pdf", "", "ESD en D+/D− del USB del ESP32 (producto comercial)"),
 "USB4105-GF-A": ("GCT", "Receptáculo USB-C 2.0 de 16 pines, SMD", "—", "—", "5 A", 0.80,
     "https://gct.co/files/drawings/usb4105.pdf", "", "Un solo USB-C para cargar y programar"),
 "S4B-PH-K-S(LF)(SN)": ("JST", "Conector PH de 4 polos, 2,0 mm, ángulo recto THT, con traba", "—", "—", "2 A/contacto", 0.18,
     "https://www.jst-mfg.com/product/pdf/eng/ePH.pdf", "", "Mejora 1: un solo conector Kelvin polarizado; no se puede invertir"),
 "S2B-PH-SM4-TB(LF)(SN)": ("JST", "Conector PH de 2 polos, SMD, ángulo recto", "—", "—", "2 A", 0.49,
     "https://www.jst-mfg.com/product/pdf/eng/ePH.pdf", "", "Batería con conector polarizado"),
 "Y44870R10000B9R": ("VPG Foil Resistors", "Shunt CSM2512S de lámina metálica (Bulk Metal Foil) con 4 terminales, 2512", "±0,1 %", "±15 ppm/°C", "1 W", 6.04,
     "https://vpgfoilresistors.com/products/current-sense-resistors/csm2512s/datasheet",
     "DigiKey: sin precio unitario; el precio corresponde al tramo de 500 uds. ($6,0368). No se mantiene en stock (28 semanas). Alternativa en stock: Y14870R10000B9R (2 terminales), $13,05",
     "Patrón único: reemplaza 3 R_REF (1 % y TCR alto). 4 terminales: el sensado Kelvin queda en la propia resistencia"),
 "LP603048JK+PCM+2 WIRES 70MM": ("Jauch Quartz", "Li-Po 1S de 820 mAh con PCM, 51×31×7 mm (incluye PCM)", "—", "Descarga máx. 2 C, carga máx. 0,5 C", "3,7 V", 11.67,
     "https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5883/LP603048JK_1s1p.pdf", "",
     "Batería plana que soporta el pulso de 1 A (1,2 C) dentro de su especificación"),
 "FCR7350R": ("Cliff Electronic Components", "Borne banana 4 mm de seguridad para panel, rojo (C1 = F+, P1 = S+)", "—", "—", "CAT, 4 mm", 7.66,
     "https://www.cliffuk.co.uk/products/testleads/sockets/S16NPC.pdf", "", "Mejora 1: bornes estándar como los miliohmímetros comerciales; aceptan pinzas Kelvin comerciales (banana simple o doble a 19 mm)"),
 "FCR7350B": ("Cliff Electronic Components", "Borne banana 4 mm de seguridad para panel, negro (P2 = S−, C2 = F−)", "—", "—", "CAT, 4 mm", 7.66,
     "https://www.cliffuk.co.uk/products/testleads/sockets/S16NPC.pdf", "", "Ídem; rojo y negro agrupados por pinza (C1-P1 / P2-C2) y rotulados en la tapa"),
 "73096-2": ("Pomona Electronics", "Borne banana de seguridad 4 mm para PCB (vertical), rojo (C1 = F+, P1 = S+)", "—", "—", "24 A, CAT III 1000 V", 13.17,
     "https://assets.edgenet.com/44f40043-51c7-4f8b-b242-62acf84469a2", "", "Mejora 1 (variante B): bornes soldados directamente en la PCB, sin arnés; aceptan pinzas Kelvin comerciales con banana de 4 mm"),
 "73096-0": ("Pomona Electronics", "Borne banana de seguridad 4 mm para PCB (vertical), negro (P2 = S−, C2 = F−)", "—", "—", "24 A, CAT III 1000 V", 13.17,
     "https://assets.edgenet.com/44f40043-51c7-4f8b-b242-62acf84469a2", "", "Ídem; columna negra (P2/C2) y columna roja (P1/C1), una columna por pinza"),
 "PHR-2": ("JST", "Carcasa PH de 2 polos (batería)", "—", "—", "—", 0.10, "https://www.jst-mfg.com/product/pdf/eng/ePH.pdf", "", "Para crimpar los cables de la batería"),
 "SPH-002T-P0.5S": ("JST", "Contacto crimp PH, 24–30 AWG", "—", "—", "2 A", 0.0204, "https://www.jst-mfg.com/product/pdf/eng/ePH.pdf", "", "2 contactos (batería)"),
 "LTST-C191KRKT": ("Lite-On", "LED rojo 0603", "—", "—", "2 V", 0.15,
     "https://optoelectronics.liteon.com/upload/download/DS22-2000-223/LTST-C191KRKT.PDF", "", "Indicador de carga (CHG)"),
 "PTS815SJM250SMTRLFS": ("C&K", "Pulsador táctil SMD de 4,2×3,2 mm", "—", "—", "12 V/50 mA", 0.26,
     "https://www.littelfuse.com/assetdocs/littelfuse-c-k-tactile-pts815-series-datasheet?assetguid=1c4ee7c5-01fd-4370-a5cc-03ec62685e73", "", "BOOT y RESET (los traía la SuperMini)"),
 "ERA-2AEB102X": ("Panasonic", "Resistencia de película delgada 1 kΩ, 0402", "±0,1 %", "±25 ppm/°C", "1/16 W", 0.11,
     "https://industrial.panasonic.com/cdbs/www-data/pdf/RDM0000/AOA0000C307.pdf", "",
     "Filtro RC de entrada del ADC. Lámina delgada: bajo ruido de exceso y apareamiento; con 1 kΩ y 10 nF C0G mantiene fc = 8 kHz como en la v1"),
 "GRM1885C1H103JA01D": ("Murata", "MLCC 10 nF, 0603", "±5 %", "C0G/NP0", "50 V", 0.13,
     "https://www.murata.com/en-us/products/productdetail?partno=GRM1885C1H103JA01D", "",
     "C0G: sin efecto piezoeléctrico, sin coeficiente de tensión y sin absorción dieléctrica (filtro del ADC y C_ST)"),
 "GRM1555C1H102JA01D": ("Murata", "MLCC 1 nF, 0402", "±5 %", "C0G/NP0", "50 V", 0.11,
     "https://www.murata.com/en-us/products/productdetail?partno=GRM1555C1H102JA01D", "", "C_F del lazo: C0G para que la compensación no cambie con temperatura ni tensión"),
 "CL05B104KO5NNNC": ("Samsung EM", "MLCC 100 nF, 0402", "±10 %", "X7R", "16 V", 0.10, "https://product.samsungsem.com/mlcc/CL05B104KO5NNNC.do", "Sin stock a la fecha (sustituibles)", "Desacople: X7R es suficiente"),
 "CL05A105KA5NQNC": ("Samsung EM", "MLCC 1 µF, 0402", "±10 %", "X5R", "25 V", 0.19, "https://product.samsungsem.com/mlcc/CL05A105KA5NQNC.do", "", "Desacople / RC de EN"),
 "CL10A475KO8NNNC": ("Samsung EM", "MLCC 4,7 µF, 0603", "±10 %", "X5R", "16 V", 0.14, "https://product.samsungsem.com/mlcc/CL10A475KO8NNNC.do", "Sin stock a la fecha", "OUT/BAT del BQ24074 (según datasheet)"),
 "CL10A106KP8NNNC": ("Samsung EM", "MLCC 10 µF, 0603", "±10 %", "X5R", "10 V", 0.20, "https://product.samsungsem.com/mlcc/CL10A106KP8NNNC.do", "Sin stock a la fecha", "Entrada del TPS63802 / 3V3 del ESP32"),
 "GRM21BR61A226ME44L": ("Murata", "MLCC 22 µF, 0805", "±20 %", "X5R", "10 V", 0.32,
     "https://www.murata.com/en-us/products/productdetail?partno=GRM21BR61A226ME44L", "Sin stock a la fecha", "Salida del TPS63802 (datasheet: 22 µF)"),
 "CL21A476MQYNNNE": ("Samsung EM", "MLCC 47 µF, 0805", "±20 %", "X5R", "6,3 V", 0.34, "https://product.samsungsem.com/mlcc/CL21A476MQYNNNE.do", "",
     "2 en paralelo en el drenador: reemplazan CF3 de 470 µF (0603 era imposible); ESR baja junto a Q1"),
}
YAGEO = ("YAGEO", "Resistencia de película gruesa, 0402", "±1 %", "±100 ppm/°C", "1/16 W", 0.10, YAGEO_DS,
         "Precio verificado en RC0402FR-0710KL (misma serie y precio)", None)
JUST_Y = {"5K1": "CC de USB-C (dispositivo UFP, 5,1 kΩ por especificación)", "2K37": "R_ISET: 376 mA ≤ 0,5 C", "3K48": "R_ILIM: 438 mA ≤ 500 mA USB",
          "3K16": "R_ITERM: 40 mA", "46K4": "R_TMR: 6,2 h", "10K": "Pull-ups / TS sin NTC / EN", "100K": "Pull-ups/pull-downs y R_G2 (v1)", "1K": "R_ST (v1), LED, R_FB",
          "220K": "Divisor de batería (v1)", "560K": "Divisor FB: 3,30 V", "33K": "R_DV (v1)", "976R": "R_A rango 0,5 A", "105R": "R_B rango 0,1 A",
          "470R": "R_G (v1)", "10R": "Filtro RC de AVDD"}
JUST_Y_GEN = ("Divisor de VSET y polarizaciones: la exactitud de VSET se cancela en la medición ratiométrica, así que alcanza con 1 %/100 ppm (se cuantifica en la Fase 5). "
              "La red de medición usa película delgada y lámina metálica.")

groups = OrderedDict()
for ref, (lib, val, fp, nets, mpn, unit) in D.P.items():
    if ref == "Q3B" or not mpn: continue
    groups.setdefault(mpn, {"refs": [], "val": val, "fp": fp})["refs"].append(ref)
extra = [("LP603048JK+PCM+2 WIRES 70MM", ["BT1 (externa, sobre J2)"], "820 mAh", "—"),

         ("PHR-2", ["Batería"], "", ""), ("SPH-002T-P0.5S", ["Crimp ×2"], "", "")]
rows = []
for mpn, g in groups.items():
    if mpn.startswith("RC0402FR"):
        code = mpn[len("RC0402FR-07"):-1]
        man, desc, tol, tcr, pw, price, ds, note, _ = YAGEO
        just = (JUST_Y.get(code, "") + ". " + JUST_Y_GEN).strip(". ")
    else:
        man, desc, tol, tcr, pw, price, ds, note, just = INFO[mpn]
    q = len(g["refs"])
    rows.append([", ".join(g["refs"]), q, g["val"], mpn, man, desc, tol, tcr, pw, g["fp"].split(":")[-1], f"{price:.4f}", f"{price*q:.2f}",
                 DK(mpn), ds, FECHA, note, just])
for mpn, refs, val, _ in extra:
    man, desc, tol, tcr, pw, price, ds, note, just = INFO[mpn]
    q = 2 if mpn.startswith("SPH") else 1
    rows.append([", ".join(refs), q, val, mpn, man, desc, tol, tcr, pw, "—", f"{price:.4f}", f"{price*q:.2f}", DK(mpn), ds, FECHA, note, just])
head = ["Referencias", "Cant", "Valor", "MPN", "Fabricante", "Descripción / tecnología", "Tolerancia", "TCR / dieléctrico",
        "Potencia / tensión", "Huella", "Precio unit. USD", "Subtotal USD", "Ficha DigiKey", "Datasheet oficial", "Fecha consulta", "Nota precio/stock", "Justificación"]
with open(os.path.join(OUTD, "BOM_v2_fase2.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(head); w.writerows(rows)
total = sum(float(r[11]) for r in rows)
md = ["# BOM v2 (Fase 2)", "", f"Precios: DigiKey (distribuidor autorizado), cantidad 1 en USD, consultados el **{FECHA}**. Datasheets: sitio oficial del fabricante.",
      "No incluye la PCB ni las pinzas Kelvin (accesorio estándar con banana de 4 mm, se compra aparte como en los equipos comerciales).", "",
      "| Refs | Cant | Valor | MPN | Fabricante | Tecnología | Tol. | TCR/Diel. | P/V | Precio | Subtotal | Enlaces |", "|" + "---|" * 12]
for r in rows:
    md.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} | ${r[10]} | ${r[11]} | [DigiKey]({r[12]}) · [datasheet]({r[13]}) |")
md += ["", f"**Total de componentes: ${total:.2f} USD** (≈ {total*3300:,.0f} COP con 1 USD ≈ 3 300 COP, la misma tasa de la Tabla 5 de la v1).", "",
       "## Justificación por componente", ""]
for r in rows:
    md.append(f"- **{r[3]}** ({r[0]}): {r[16]}" + (f" *Precio/stock: {r[15]}*" if r[15] else ""))
open(os.path.join(OUTD, "BOM_v2_fase2.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print(len(rows), "líneas, total USD", round(total, 2))
