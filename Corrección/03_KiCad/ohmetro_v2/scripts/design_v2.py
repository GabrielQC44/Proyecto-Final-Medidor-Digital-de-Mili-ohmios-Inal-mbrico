# -*- coding: utf-8 -*-
"""
Diseño v2 del miliohmímetro: fuente única de verdad (netlist, valores, huellas, MPN).
Base: v1 migrada (v2/kicad/v1_migrado). Cambios justificados en v2/calculos/fase2_calculos.md.
Formato: ref -> (lib_id, valor, huella, {pin: red}, MPN, unidad)
"""
R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
Y = lambda v: f"RC0402FR-07{v}L"      # Yageo RC 0402 1 % 100 ppm/°C (película gruesa)

def R(a, b, val, mpn, fp=R0402):
    return ("Device:R", val, fp, {"1": a, "2": b}, mpn, 1)
def C(a, b, val, mpn, fp=C0402):
    return ("Device:C", val, fp, {"1": a, "2": b}, mpn, 1)

P = {}
# ============================================================ Bloque 1: USB-C, cargador, batería
P["J1"] = ("Connector:USB_C_Receptacle_USB2.0_16P", "USB-C", "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
           {"A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS",
            "A5": "CC1", "B5": "CC2", "A6": "USB_DP", "B6": "USB_DP", "A7": "USB_DN", "B7": "USB_DN",
            "A8": None, "B8": None, "SH": "GND"}, "USB4105-GF-A", 1)
P["R1"] = R("CC1", "GND", "5.1k", Y("5K1"))
P["R2"] = R("CC2", "GND", "5.1k", Y("5K1"))
P["D1"] = ("Power_Protection:USBLC6-2SC6", "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6",
           {"1": "USB_DN", "6": "USB_DN", "3": "USB_DP", "4": "USB_DP", "5": "VBUS", "2": "GND"}, "USBLC6-2SC6", 1)
P["U2"] = ("Battery_Management:BQ24074RGT", "BQ24074RGTR", "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias",
           {"1": "TS", "2": "VBAT", "3": "VBAT", "4": "GND", "5": "VSYS", "6": "GND", "7": "USB_PG", "8": "GND",
            "9": "CHG_N", "10": "VSYS", "11": "VSYS", "12": "ILIM", "13": "VBUS", "14": "TMR", "15": "ITERM",
            "16": "ISET", "17": "GND"}, "BQ24074RGTR", 1)
P["C1"] = C("VBUS", "GND", "1u", "CL05A105KA5NQNC")                       # entrada IN (datasheet: 1 µF)
P["C2"] = C("VSYS", "GND", "4.7u", "CL10A475KO8NNNC", C0603)              # OUT
P["C3"] = C("VBAT", "GND", "4.7u", "CL10A475KO8NNNC", C0603)              # BAT
P["R3"] = R("ISET", "GND", "2.37k", Y("2K37"))                            # I_CHG = 376 mA (≤ 0,5 C)
P["R4"] = R("ILIM", "GND", "3.48k", Y("3K48"))                            # I_IN = 438 mA
P["R5"] = R("ITERM", "GND", "3.16k", Y("3K16"))                           # I_TERM = 40 mA
P["R6"] = R("TMR", "GND", "46.4k", Y("46K4"))                             # t_MAX ≈ 6,2 h
P["R7"] = R("TS", "GND", "10k", Y("10K"))                                 # sin NTC (datasheet)
P["R8"] = R("USB_PG", "3V3", "100k", Y("100K"))
P["R9"] = R("CHG_N", "3V3", "100k", Y("100K"))
P["R10"] = R("3V3", "LED_A", "1k", Y("1K"))
P["D2"] = ("Device:LED", "CHG (rojo)", "LED_SMD:LED_0603_1608Metric", {"1": "CHG_N", "2": "LED_A"}, "LTST-C191KRKT", 1)
P["J2"] = ("Connector_Generic:Conn_01x02", "BAT 1S (JST PH)", "Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
           {"1": "VBAT", "2": "PGND", "MP": "PGND"}, "S2B-PH-SM4-TB(LF)(SN)", 1)
P["RDIV1"] = R("VBAT", "VBAT_SENSE", "220k", Y("220K"))                   # = v1
P["RDIV2"] = R("VBAT_SENSE", "GND", "220k", Y("220K"))                    # = v1
P["CDIV"] = C("VBAT_SENSE", "GND", "100n", "CL05B104KO5NNNC")             # C_M2 del informe v1
P["NT1"] = ("Device:NetTie_2", "Estrella GND/PGND", "NetTie:NetTie-2_SMD_Pad0.5mm", {"1": "GND", "2": "PGND"}, "", 1)

# ============================================================ Bloque 1b: regulador 3,3 V (TPS63802 integrado)
P["U3"] = ("ohmetro:TPS63802DLA", "TPS63802DLAR", "ohmetro:TI_DLA_VSON-HR-10_2x3mm",
           {"1": "VSYS", "2": "VSYS", "3": "GND", "4": "FB", "5": None, "6": "3V3", "7": "SW2", "8": "GND", "9": "SW1", "10": "VSYS"},
           "TPS63802DLAR", 1)
P["L1"] = ("Device:L", "0.47u", "Inductor_SMD:L_Murata_DFE201610P", {"1": "SW1", "2": "SW2"}, "DFE201612E-R47M=P2", 1)
P["C4"] = C("VSYS", "GND", "10u", "CL10A106KP8NNNC", C0603)
P["C5"] = C("3V3", "GND", "22u", "GRM21BR61A226ME44L", C0805)
P["R11"] = R("3V3", "FB", "560k", Y("560K"))
P["R12"] = R("FB", "GND", "100k", Y("100K"))

# ============================================================ Bloque 2: fuente de corriente (base v1)
P["U5"] = ("74xGxx:SN74LVC1G125DCK", "SN74LVC1G125DCKR", "Package_TO_SOT_SMD:SOT-353_SC-70-5",
           {"1": "GND", "2": "PULSE", "3": "GND", "4": "BUF_Y", "5": "3V3"}, "SN74LVC1G125DCKR", 1)
P["C6"] = C("3V3", "GND", "100n", "CL05B104KO5NNNC")
P["RM10"] = R("PULSE", "GND", "100k", Y("100K"))                           # pull-down de GPIO10 (informe v1)
P["RDV1"] = R("BUF_Y", "VSET", "33k", Y("33K"))                            # = v1
P["RST1"] = R("VSET", "GND", "1k", Y("1K"))                                # = v1
P["CST1"] = C("VSET", "GND", "10n", "GRM1885C1H103JA01D", C0603)          # = v1 (C0G)
P["RA"] = R("VSET", "SWA", "976", Y("976R"))                               # rango 0,5 A
P["RB"] = R("VSET", "SWB", "105", Y("105R"))                               # rango 0,1 A
P["Q3"] = ("Transistor_FET:Q_Dual_NMOS_S1G1D2S2G2D1", "NTZD3154N", "Package_TO_SOT_SMD:SOT-563",
           {"1": "GND", "2": "RANGE_B", "6": "SWB"}, "NTZD3154NT1G", 1)
P["Q3B"] = ("Transistor_FET:Q_Dual_NMOS_S1G1D2S2G2D1", "NTZD3154N", "Package_TO_SOT_SMD:SOT-563",
            {"4": "GND", "5": "RANGE_A", "3": "SWA"}, "NTZD3154NT1G", 2)
P["R13"] = R("RANGE_A", "GND", "100k", Y("100K"))
P["R14"] = R("RANGE_B", "3V3", "10k", Y("10K"))                            # GPIO8 strapping = 1
P["U4"] = ("Amplifier_Operational:OPA376xxDCK", "OPA376AIDCKR", "Package_TO_SOT_SMD:SOT-353_SC-70-5",
           {"1": "VSET", "2": "GND", "3": "INN", "4": "OPA_OUT", "5": "3V3"}, "OPA376AIDCKR", 1)  # DCK: 1 +IN, 2 V-, 3 -IN, 4 OUT, 5 V+
P["C7"] = C("3V3", "GND", "100n", "CL05B104KO5NNNC")
P["RFB"] = R("RREF_P", "INN", "1k", Y("1K"))                               # NUEVO: compensación
P["CF1"] = C("OPA_OUT", "INN", "1n", "GRM1555C1H102JA01D")                # 33 pF -> 1 nF C0G
P["RG1"] = R("OPA_OUT", "GATE", "470", Y("470R"))                          # = v1
P["RG2"] = R("GATE", "GND", "100k", Y("100K"))                             # = v1
P["Q1"] = ("Transistor_FET:Q_NMOS_GDS", "IRLHM620", "ohmetro:Infineon_PQFN-8_3.3x3.3mm",
           {"1": "GATE", "2": "VSYS", "3": "F_PLUS"}, "IRLHM620TRPBF", 1)
P["C8"] = C("VSYS", "PGND", "47u", "CL21A476MQYNNNE", C0805)               # sustituye CF3 470 µF
P["C9"] = C("VSYS", "PGND", "47u", "CL21A476MQYNNNE", C0805)
P["RSH"] = ("Device:R_Shunt", "0.1 0.1% 15ppm", "ohmetro:R_Shunt_VPG_CSM2512S_4T",
            {"1": "F_MINUS", "2": "RREF_P", "3": "RREF_N", "4": "PGND"}, "Y44870R10000B9R", 1)

# VARIANTE B: 4 bornes banana de seguridad de 4 mm soldados en la PCB (Pomona 73096, montaje vertical),
# sin J3 ni arnés. Columna roja: C1 = F+ y P1 = S+; columna negra: P2 = S- y C2 = F-.
for r, n, mpn, lab in [("J4", "F_PLUS", "73096-2", "C1 (F+) rojo"), ("J5", "RX_P", "73096-2", "P1 (S+) rojo"),
                       ("J6", "RX_N", "73096-0", "P2 (S-) negro"), ("J7", "F_MINUS", "73096-0", "C2 (F-) negro")]:
    P[r] = ("Connector:Conn_01x01_Socket", lab, "ohmetro:Pomona_73096_4mm_Vertical", {"1": n}, mpn, 1)
OFF_BOARD = set()

# ============================================================ Bloque 3: ADC ADS1220 (chip, ya no módulo)
P["U6"] = ("ohmetro:ADS1220_RVA", "ADS1220IRVAR", "Package_DFN_QFN:Texas_RVA_VQFN-16-1EP_3.5x3.5mm_P0.5mm_EP2.14x2.14mm",
           {"1": "GND", "2": "GND", "3": "GND", "4": "AIN3", "5": "AIN2", "6": None, "7": None, "8": "AIN1",
            "9": "AIN0", "10": "AVDD", "11": "3V3", "12": None, "13": "MISO", "14": "MOSI", "15": "SCLK",
            "16": "ADS_CS", "17": "GND"}, "ADS1220IRVAR", 1)
P["RADS1"] = R("RX_P", "AIN0", "1k", "ERA-2AEB102X")                       # película delgada 0,1 % 25 ppm
P["RADS2"] = R("RX_N", "AIN1", "1k", "ERA-2AEB102X")
P["RADS3"] = R("RREF_P", "AIN2", "1k", "ERA-2AEB102X")
P["RADS4"] = R("RREF_N", "AIN3", "1k", "ERA-2AEB102X")
P["CADS1"] = C("AIN0", "AIN1", "10n", "GRM1885C1H103JA01D", C0603)         # C0G, fc = 8 kHz (= v1)
P["CADS2"] = C("AIN2", "AIN3", "10n", "GRM1885C1H103JA01D", C0603)
P["R15"] = R("3V3", "AVDD", "10", Y("10R"))                                # filtro de AVDD
P["C10"] = C("AVDD", "GND", "1u", "CL05A105KA5NQNC")
P["C11"] = C("AVDD", "GND", "100n", "CL05B104KO5NNNC")
P["C12"] = C("3V3", "GND", "100n", "CL05B104KO5NNNC")                      # DVDD
P["R16"] = R("ADS_CS", "3V3", "10k", Y("10K"))                             # CS inactivo + strapping GPIO2

# ============================================================ Bloque 4: ESP32-C3-MINI-1 integrado
GNDP = ["1", "2", "11", "14"] + [str(i) for i in range(36, 54)]
NCP = ["4", "7", "9", "10", "15", "17", "24", "25", "28", "29", "32", "33", "34", "35"]
u1 = {g: "GND" for g in GNDP}
u1.update({n: None for n in NCP})
u1.update({"3": "3V3", "8": "EN", "12": "VBAT_SENSE", "13": "USB_PG", "5": "ADS_CS", "6": "RANGE_A",
           "18": "SCLK", "19": "MISO", "20": "MOSI", "21": "CHG_N", "22": "RANGE_B", "23": "BOOT",
           "16": "PULSE", "26": "USB_DN", "27": "USB_DP", "30": "U0RX", "31": "U0TX"})
P["U1"] = ("ohmetro:ESP32-C3-MINI-1", "ESP32-C3-MINI-1-N4X", "ohmetro:ESP32-C3-MINI-1", u1, "ESP32-C3-MINI-1-N4X", 1)
P["C13"] = C("3V3", "GND", "10u", "CL10A106KP8NNNC", C0603)
P["C14"] = C("3V3", "GND", "100n", "CL05B104KO5NNNC")
P["R17"] = R("3V3", "EN", "10k", Y("10K"))
P["C15"] = C("EN", "GND", "1u", "CL05A105KA5NQNC")
P["SW1"] = ("Switch:SW_Push", "RESET", "Button_Switch_SMD:SW_SPST_PTS810", {"1": "EN", "2": "GND"}, "PTS815SJM250SMTRLFS", 1)
P["R18"] = R("3V3", "BOOT", "10k", Y("10K"))
P["SW2"] = ("Switch:SW_Push", "BOOT", "Button_Switch_SMD:SW_SPST_PTS810", {"1": "BOOT", "2": "GND"}, "PTS815SJM250SMTRLFS", 1)
for i, n in enumerate(["U0RX", "U0TX", "3V3", "GND"]):
    P[f"TP{i+1}"] = ("Connector:TestPoint", n, "TestPoint:TestPoint_Pad_D1.0mm", {"1": n}, "", 1)

# --------------------------------------------------------------------- símbolos propios
ADS1220_RVA_PINS = (
    [("9", "AIN0/REFP1", "passive"), ("8", "AIN1", "passive"), ("5", "AIN2", "passive"), ("4", "AIN3/REFN1", "passive"),
     ("7", "REFP0", "passive"), ("6", "REFN0", "passive"), ("10", "AVDD", "power_in"), ("3", "AVSS", "power_in"), ("17", "EP", "passive")],
    [("16", "~{CS}", "input"), ("15", "SCLK", "input"), ("14", "DIN", "input"), ("13", "DOUT/~{DRDY}", "output"),
     ("12", "~{DRDY}", "output"), ("1", "CLK", "input"), ("11", "DVDD", "power_in"), ("2", "DGND", "power_in")])
TPS63802_PINS = ([("10", "VIN", "power_in"), ("1", "EN", "input"), ("2", "MODE", "input"), ("9", "L1", "passive"),
                  ("3", "AGND", "power_in"), ("8", "GND", "power_in")],
                 [("6", "VOUT", "power_out"), ("4", "FB", "input"), ("5", "PG", "open_collector"), ("7", "L2", "passive")])
ESP_LEFT = [("3", "3V3", "power_in"), ("8", "EN", "input")] + [(g, "GND", "power_in") for g in GNDP] + \
           [(n, "NC", "no_connect") for n in NCP]
ESP_RIGHT = [("12", "IO0", "bidirectional"), ("13", "IO1", "bidirectional"), ("5", "IO2", "bidirectional"),
             ("6", "IO3", "bidirectional"), ("18", "IO4", "bidirectional"), ("19", "IO5", "bidirectional"),
             ("20", "IO6", "bidirectional"), ("21", "IO7", "bidirectional"), ("22", "IO8", "bidirectional"),
             ("23", "IO9", "bidirectional"), ("16", "IO10", "bidirectional"), ("26", "IO18/D-", "bidirectional"),
             ("27", "IO19/D+", "bidirectional"), ("30", "RXD0", "bidirectional"), ("31", "TXD0", "bidirectional")]
