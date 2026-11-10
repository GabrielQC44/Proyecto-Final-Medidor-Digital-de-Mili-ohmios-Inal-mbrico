# -*- coding: utf-8 -*-
"""Analiza los .log del Monte Carlo (LTspice): extrae cada .meas por corrida, guarda CSV,
calcula estadística de RX, I, VSET, VX/VREF y la sensibilidad de RX a cada parámetro
(regresión lineal sobre las desviaciones relativas). Genera resultados_mc.md y figuras PNG."""
import re, csv, os, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
MODES = {1: ("0,1 A", 1.0), 2: ("0,5 A", 0.1), 3: ("1 A", 0.01)}
NOM = {"PRSH": 0.1, "PRDV": 33e3, "PRST": 1e3, "PRA": 976, "PRB": 105, "PRFB": 1e3,
       "PRA1": 1e3, "PRA2": 1e3, "PRA3": 1e3, "PRA4": 1e3}
LABEL = {"PRSH": "R_SH (shunt 0,1 Ω, 0,1 %)", "PRDV": "R_DV 33 k (1 %)", "PRST": "R_ST 1 k (1 %)", "PRA": "R_A 976 Ω (1 %)",
         "PRB": "R_B 105 Ω (1 %)", "PRFB": "R_FB 1 k (1 %)", "PRA1": "R_ADS1 1 k (0,1 %)", "PRA2": "R_ADS2 1 k (0,1 %)",
         "PRA3": "R_ADS3 1 k (0,1 %)", "PRA4": "R_ADS4 1 k (0,1 %)", "PVOS": "Vos OPA376 (±25 µV)", "PRON": "RDS(on) Q3"}

def read_log(path):
    t = open(path, encoding="latin-1").read()
    data = {}
    for m in re.finditer(r"Measurement: (\w+)\n\s+step[^\n]*\n((?:\s+\d+\s+[-\d.eE+]+[^\n]*\n)+)", t):
        name = m.group(1).upper()
        vals = [float(l.split()[1]) for l in m.group(2).strip().splitlines()]
        data[name] = vals
    return data

md = ["# Resultados del Monte Carlo (LTspice, corridas reales)", "",
      "Netlists: `mc_v2_modo1.cir` … `mc_v2_modo3.cir` (generados por `gen_mc.py`); logs `.log`; datos `mc_v2_modoN.csv`.",
      "Modelos: OPAx376 de TI (SBOM406), IRLHM620 VDMOS de la biblioteca de LTspice. 500 corridas por rango.",
      "Tolerancias (gaussiana, 3σ): R_SH 0,1 %, R_ADS 0,1 %, R_DV/R_ST/R_A/R_B/R_FB/R_G 1 %, C 5 %, Vos OPA376 25 µV,",
      "offset ADC 4 µV, ganancia ADC 0,05 %, RDS(on) de Q3 0,55–0,70 Ω (uniforme), corriente de entrada ADC 2 nA/pin.",
      "RX medida = R_SH,nominal · (VX,on − VX,off)/(VREF,on − VREF,off) (ecuación del firmware).", ""]
summary = []
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(14, 4))
for k, (m, (name, rx)) in enumerate(MODES.items()):
    d = read_log(os.path.join(HERE, f"mc_v2_modo{m}.log"))
    n = len(d["RXMED"])
    keys = list(d.keys())
    with open(os.path.join(HERE, f"mc_v2_modo{m}.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["run"] + keys)
        for i in range(n): w.writerow([i + 1] + [d[c][i] for c in keys])
    rxm = np.array(d["RXMED"]); err = (rxm - rx) / rx * 100     # %
    I = np.array(d["IMED"]); vs = np.array(d["VSETM"]); ratio = np.array(d["RATIO"])
    # sensibilidad: regresión de err (%) sobre desviaciones relativas (%) de cada parámetro
    cols, X = [], []
    for p in ["PRSH", "PRDV", "PRST", "PRA", "PRB", "PRFB", "PRA1", "PRA2", "PRA3", "PRA4"]:
        if p in d: cols.append(p); X.append((np.array(d[p]) / NOM[p] - 1) * 100)
    for p in ["PVOS", "PRON"]:
        if p in d: cols.append(p); X.append(np.array(d[p]) * (1e6 if p == "PVOS" else 1))
    X = np.array(X).T
    A = np.c_[X, np.ones(n)]
    coef, *_ = np.linalg.lstsq(A, err, rcond=None)
    contrib = {c: abs(coef[i]) * np.std(X[:, i]) for i, c in enumerate(cols)}
    tot = math.sqrt(sum(v * v for v in contrib.values())) or 1
    summary.append((name, rx, n, rxm.mean(), rxm.std(), err.mean(), err.std(), err.min(), err.max(), I.mean(), I.std(), vs.mean(), vs.std()))
    md += [f"## Rango {name} (RX real = {rx*1e3:g} mΩ)", "",
           "| Magnitud | Media | Desv. estándar (σ) | Mín. | Máx. |", "|---|---|---|---|---|",
           f"| Corriente I | {I.mean()*1e3:.2f} mA | {I.std()*1e3:.2f} mA ({I.std()/I.mean()*100:.2f} %) | {I.min()*1e3:.2f} mA | {I.max()*1e3:.2f} mA |",
           f"| VSET | {vs.mean()*1e3:.3f} mV | {vs.std()*1e3:.3f} mV | {vs.min()*1e3:.3f} mV | {vs.max()*1e3:.3f} mV |",
           f"| VX/VREF | {ratio.mean():.6f} | {ratio.std():.2e} | {ratio.min():.6f} | {ratio.max():.6f} |",
           f"| RX medida | {rxm.mean()*1e3:.5f} mΩ | {rxm.std()*1e3:.5f} mΩ | {rxm.min()*1e3:.5f} mΩ | {rxm.max()*1e3:.5f} mΩ |",
           f"| Error de RX | {err.mean():+.4f} % | {err.std():.4f} % (3σ = {3*err.std():.3f} %) | {err.min():+.4f} % | {err.max():+.4f} % |", "",
           "Sensibilidad del error de RX (contribución a σ, regresión lineal):", "",
           "| Parámetro | Coef. (% de RX por % o µV) | Contribución a σ(RX) | % de la varianza |", "|---|---|---|---|"]
    for c in sorted(cols, key=lambda c: -contrib[c]):
        i = cols.index(c)
        md.append(f"| {LABEL[c]} | {coef[i]:+.4f} | {contrib[c]:.5f} % | {contrib[c]**2/tot**2*100:.1f} % |")
    md.append("")
    ax = axs[k]; ax.hist(err, bins=40, color="#3b6ea5"); ax.set_title(f"Rango {name}: RX = {rx*1e3:g} mΩ")
    ax.set_xlabel("Error de RX medida [%]"); ax.set_ylabel("Corridas"); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(os.path.join(HERE, "histograma_error_rx.png"), dpi=130)
md += ["## Resumen", "", "| Rango | RX real | Error medio | σ | 3σ | Peor caso | σ(I)/I |", "|---|---|---|---|---|---|---|"]
for name, rx, n, mu, sd, em, es, emin, emax, Im, Is, vm, vsd in summary:
    md.append(f"| {name} | {rx*1e3:g} mΩ | {em:+.4f} % | {es:.4f} % | {3*es:.3f} % | {max(abs(emin), abs(emax)):.3f} % | {Is/Im*100:.2f} % |")
open(os.path.join(HERE, "resultados_mc.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md[-6:]))
