# -*- coding: utf-8 -*-
"""Lector de archivos .raw ASCII de LTspice (incluye .step). Devuelve lista de corridas: dict var->lista."""
import re
def read_raw(path):
    txt = open(path, "rb").read()
    try:
        s = txt.decode("utf-16-le")
        if "Title" not in s[:200]: raise ValueError
    except Exception:
        s = txt.decode("latin-1")
    head, data = s.split("Values:", 1)
    nvars = int(re.search(r"No\. Variables:\s*(\d+)", head).group(1))
    flags = re.search(r"Flags:(.*)", head).group(1)
    cplx = "complex" in flags
    vs = re.search(r"Variables:\s*\n(.*)", head, re.S).group(1).strip().splitlines()
    names = [l.split()[1] for l in vs[:nvars]]
    toks = data.split()
    pts = []
    i = 0
    while i < len(toks):
        i += 1  # índice del punto
        vals = []
        for k in range(nvars):
            t = toks[i]; i += 1
            if cplx:
                re_, im = t.split(","); vals.append(complex(float(re_), float(im)))
            else:
                vals.append(float(t))
        pts.append(vals)
    # separar corridas de .step (el eje x reinicia)
    runs, cur = [], []
    for p in pts:
        x = abs(p[0])
        if cur and x < abs(cur[-1][0]) and x <= abs(cur[0][0]) * 1.0000001:
            runs.append(cur); cur = []
        cur.append(p)
    if cur: runs.append(cur)
    return [{n: [p[j] for p in r] for j, n in enumerate(names)} for r in runs]
