# -*- coding: utf-8 -*-
"""Cruce de ganancia y margen de fase a partir de la inyección de Middlebrook.
T = -V(y)/V(x)  ->  PM = 180° + fase(T) en |T| = 1  (= fase(V(y)/V(x)) envuelta a (-180,180])."""
import sys, cmath, math
sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0])
from ltraw import read_raw
def margins(r):
    f = [abs(v) for v in r["frequency"]]
    T = [-y / x for x, y in zip(r["V(x)"], r["V(y)"])]
    mag = [abs(t) for t in T]
    for i in range(1, len(f)):
        if mag[i - 1] >= 1 > mag[i]:
            # interpolación log
            a = math.log10(mag[i - 1]); b = math.log10(mag[i])
            k = a / (a - b)
            fc = 10 ** (math.log10(f[i - 1]) + k * (math.log10(f[i]) - math.log10(f[i - 1])))
            ph = math.degrees(cmath.phase(T[i - 1])) * (1 - k) + math.degrees(cmath.phase(T[i])) * k
            pm = 180 + ph if ph < 0 else ph - 180
            # margen de ganancia: |T| donde fase = -180
            gm = None
            for j in range(i, len(f)):
                if math.degrees(cmath.phase(T[j - 1])) < 0 <= math.degrees(cmath.phase(T[j])) or \
                   math.degrees(cmath.phase(T[j - 1])) > 0 > math.degrees(cmath.phase(T[j])) and abs(math.degrees(cmath.phase(T[j]))) > 170:
                    gm = -20 * math.log10(mag[j]); break
            return fc, pm, gm, 20 * math.log10(mag[0])
    return None, None, None, 20 * math.log10(mag[0])
if __name__ == "__main__":
    runs = read_raw(sys.argv[1]); labels = sys.argv[2].split(",") if len(sys.argv) > 2 else [str(i) for i in range(len(runs))]
    for lab, r in zip(labels, runs):
        fc, pm, gm, dc = margins(r)
        print(f"{lab:>22s}  T(DC)={dc:6.1f} dB  fc={fc/1e3 if fc else float('nan'):8.1f} kHz  PM={pm if pm is not None else float('nan'):6.1f} deg  GM={gm if gm is not None else float('nan'):6.1f} dB")
