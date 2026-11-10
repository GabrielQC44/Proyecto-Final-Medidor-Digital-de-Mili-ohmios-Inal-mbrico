# -*- coding: utf-8 -*-
"""Grafica las formas de onda REALES del Monte Carlo leídas de los .raw ASCII de LTspice
(todas las corridas superpuestas en colores, como la ventana de LTspice). Datos sin modificar."""
import os, re, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
MODES = {1: "0,1 A (RX = 1 Ω)", 2: "0,5 A (RX = 100 mΩ)", 3: "1 A (RX = 10 mΩ)"}
WANT = ["time", "I(RXX)", "V(vset)", "V(gate)"]

def read_raw_stream(path):
    runs, cur = [], {k: [] for k in WANT}
    with open(path, "r", encoding="latin-1", errors="ignore") as f:
        names = []
        for line in f:
            if line.startswith("No. Variables:"): nv = int(line.split(":")[1])
            if line.startswith("Variables:"):
                for _ in range(nv): names.append(next(f).split()[1])
            if line.startswith("Values:"): break
        idx = {n: i for i, n in enumerate(names)}
        vals, last_t = [], None
        for line in f:
            parts = line.split()
            if not parts: continue
            vals.append(float(parts[-1]))
            if len(vals) == nv:
                t = abs(vals[0])
                if last_t is not None and t < last_t:
                    runs.append({k: np.array(v) for k, v in cur.items()}); cur = {k: [] for k in WANT}
                for k in WANT: cur[k].append(vals[idx[k]] if k != "time" else t)
                last_t = t; vals = []
        runs.append({k: np.array(v) for k, v in cur.items()})
    return runs

fig, axs = plt.subplots(3, 3, figsize=(16, 11))
for r, (m, name) in enumerate(MODES.items()):
    runs = read_raw_stream(os.path.join(HERE, "ondas_m3" if m == 3 else "", f"mc_v2_modo{m}.raw"))
    cmap = plt.get_cmap("turbo", len(runs))
    # CSV con las curvas re-muestreadas (interpolación lineal) a una rejilla común de 641 puntos
    tg = np.linspace(0, 3.2e-3, 641)
    M = np.column_stack([tg] + [np.interp(tg, run["time"], run["I(RXX)"]) for run in runs])
    np.savetxt(os.path.join(HERE, f"mc_curvas_I_modo{m}.csv"), M, delimiter=",", fmt="%.7g",
               header="t_s," + ",".join(f"I_run{k+1}_A" for k in range(len(runs))), comments="")
    order = np.random.default_rng(1).permutation(len(runs))  # solo el orden de dibujo
    for i in order:
        run = runs[i]
        t = run["time"] * 1e3; c = cmap(i)
        axs[r, 0].plot(t, run["I(RXX)"] * 1e3, color=c, lw=0.4, alpha=0.6)
        pl = (t > 1.0) & (t < 3.0)
        axs[r, 1].plot(t[pl], run["I(RXX)"][pl] * 1e3, color=c, lw=0.5, alpha=0.7)
        sel = (t > 0.45) & (t < 0.75)
        axs[r, 2].plot(t[sel], run["I(RXX)"][sel] * 1e3, color=c, lw=0.4, alpha=0.6)
    axs[r, 0].set_title(f"Corriente I(RX), {name}: {len(runs)} corridas"); axs[r, 0].set_ylabel("I [mA]")
    axs[r, 1].set_title(f"Zoom de la meseta (dispersión), {name}"); axs[r, 1].set_ylabel("I [mA]")
    axs[r, 2].set_title(f"Detalle del flanco de subida, {name}"); axs[r, 2].set_ylabel("I [mA]")
    for c in range(3):
        axs[r, c].set_xlabel("t [ms]"); axs[r, c].grid(alpha=.3)
fig.suptitle("Monte Carlo LTspice (curvas reales de los .raw): fuente de corriente v2", fontsize=13)
plt.tight_layout(); plt.savefig(os.path.join(HERE, "mc_formas_de_onda.png"), dpi=120)
print("ok")
