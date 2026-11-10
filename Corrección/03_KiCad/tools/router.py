# -*- coding: utf-8 -*-
"""
Enrutador de laberinto (A*) sobre rejilla, multicapa, con holguras reales.
Lee el JSON de dump_board.py y una lista de conexiones; escribe pistas y vías en JSON
para que el script de construcción las agregue con pcbnew. Se usa para las pocas conexiones
nuevas; KiCad DRC valida el resultado final.

uso: router.py board.json tasks.json out.json
 tasks.json: {"grid":0.1, "clearance":0.2, "edge":0.3, "via_d":0.6, "via_drill":0.3, "via_cost":25,
              "layers":["F.Cu","B.Cu"],
              "tasks":[{"net":"/VBAT","a":[x,y],"b":[x,y],"w":0.5,"layers":["F.Cu"]}, ...]}
"""
import sys, json, heapq, math
import numpy as np

def main(board_json, tasks_json, out_json):
    d = json.load(open(board_json)); T = json.load(open(tasks_json))
    g = T.get("grid", 0.1); clr = T.get("clearance", 0.2); edge = T.get("edge", 0.3)
    vd = T.get("via_d", 0.6); vdr = T.get("via_drill", 0.3); vcost = T.get("via_cost", 25)
    LAY = T.get("layers", ["F.Cu", "B.Cu"])
    LCOST = T.get("layer_cost", {})
    short = {"F": "F.Cu", "B": "B.Cu", "I1": "In1.Cu", "I2": "In2.Cu"}
    x0, y0, x1, y1 = d["edge"]
    nx, ny = int((x1 - x0) / g) + 1, int((y1 - y0) / g) + 1
    X = x0 + np.arange(nx) * g; Y = y0 + np.arange(ny) * g
    XX, YY = np.meshgrid(X, Y, indexing="xy")  # [iy, ix]

    objs = []  # (net, layers(set), kind, params)
    for p in d["pads"]:
        ls = {short[l] for l in p["layers"]}
        if p.get("drill"): ls = set(LAY)
        objs.append((p["net"], ls, "circle" if p["round"] else "rect", p["bbox"]))
    for t in d["tracks"]:
        objs.append((t["net"], {t["layer"]}, "seg", (t["a"], t["b"], t["w"])))
    for v in d["vias"]:
        objs.append((v["net"], set(LAY), "circ", (v["x"], v["y"], v["d"] / 2)))
    for k in d.get("keepouts", []):
        objs.append(("__KEEPOUT__", set(LAY), "rect", k["bbox"]))
    holes = [(p["x"], p["y"], p["drill"] / 2) for p in d["pads"] if p.get("drill")] + [(v["x"], v["y"], v["drill"] / 2) for v in d["vias"]]
    H2H = T.get("hole_to_hole", 0.25)

    def dist_map(kind, prm, win):
        ix0, iy0, ix1, iy1 = win
        xs, ys = XX[iy0:iy1, ix0:ix1], YY[iy0:iy1, ix0:ix1]
        if kind == "rect":
            bx1, by1, bx2, by2 = prm
            dx = np.maximum(np.maximum(bx1 - xs, xs - bx2), 0); dy = np.maximum(np.maximum(by1 - ys, ys - by2), 0)
            return np.hypot(dx, dy)
        if kind == "circle":
            bx1, by1, bx2, by2 = prm
            cx, cy, r = (bx1 + bx2) / 2, (by1 + by2) / 2, (bx2 - bx1) / 2
            return np.maximum(np.hypot(xs - cx, ys - cy) - r, 0)
        if kind == "circ":
            cx, cy, r = prm
            return np.maximum(np.hypot(xs - cx, ys - cy) - r, 0)
        (ax, ay), (bx, by), w = prm
        vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
        t = np.clip(((xs - ax) * vx + (ys - ay) * vy) / L2, 0, 1) if L2 > 0 else 0
        return np.maximum(np.hypot(xs - (ax + t * vx), ys - (ay + t * vy)) - w / 2, 0)

    def bbox_of(kind, prm):
        if kind in ("rect", "circle"): return prm
        if kind == "circ": cx, cy, r = prm; return [cx - r, cy - r, cx + r, cy + r]
        (ax, ay), (bx, by), w = prm
        return [min(ax, bx) - w / 2, min(ay, by) - w / 2, max(ax, bx) + w / 2, max(ay, by) + w / 2]

    def blocked(net, infl):
        """mapa booleano [capa][iy,ix] ocupado por cobre de otras redes, inflado 'infl'."""
        B = {L: np.zeros((ny, nx), bool) for L in LAY}
        for onet, ls, kind, prm in objs:
            if onet == net and net != "": continue
            bx1, by1, bx2, by2 = bbox_of(kind, prm)
            win = (max(0, int((bx1 - infl - x0) / g) - 1), max(0, int((by1 - infl - y0) / g) - 1),
                   min(nx, int((bx2 + infl - x0) / g) + 2), min(ny, int((by2 + infl - y0) / g) + 2))
            if win[0] >= win[2] or win[1] >= win[3]: continue
            m = dist_map(kind, prm, win) < infl
            for L in ls:
                if L in B: B[L][win[1]:win[3], win[0]:win[2]] |= m
        em = int(math.ceil((edge + infl - clr) / g))
        for L in LAY:
            B[L][:em, :] = True; B[L][-em:, :] = True; B[L][:, :em] = True; B[L][:, -em:] = True
        return B

    out = []
    queue = list(T["tasks"])
    while queue:
        task = queue.pop(0)
        n_before = len(out)
        net, w = task["net"], task["w"]
        tl = task.get("layers", LAY)
        vd = task.get("via_d", T.get("via_d", 0.6)); vdr = task.get("via_drill", T.get("via_drill", 0.3))
        Bt = blocked(net, clr + w / 2)
        Bv = blocked(net, clr + vd / 2)
        # separación agujero-agujero con cualquier agujero existente (también de la misma red)
        for hx, hy, hr in holes:
            rr = hr + vdr / 2 + H2H
            ix0_, ix1_ = max(0, int((hx - rr - x0) / g) - 1), min(nx, int((hx + rr - x0) / g) + 2)
            iy0_, iy1_ = max(0, int((hy - rr - y0) / g) - 1), min(ny, int((hy + rr - y0) / g) + 2)
            m = np.hypot(XX[iy0_:iy1_, ix0_:ix1_] - hx, YY[iy0_:iy1_, ix0_:ix1_] - hy) < rr
            for L in LAY: Bv[L][iy0_:iy1_, ix0_:ix1_] |= m
        def cell(p): return (int(round((p[1] - y0) / g)), int(round((p[0] - x0) / g)))
        s = cell(task["a"])
        fan = task.get("fanout", False)
        e = s if fan else cell(task["b"])
        Li = {L: i for i, L in enumerate(LAY)}
        free = {L: ~Bt[L] for L in LAY}
        # liberar alrededor de los extremos (están sobre pads de la propia red)
        # (sin liberar a la fuerza los extremos: si el ancho no cabe en el pin, se reintenta con w_min)
        start_layers = task.get("a_layers", tl); end_layers = task.get("b_layers", tl)
        nbr = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
        h = (lambda iy, ix: 0.0) if fan else (lambda iy, ix: math.hypot(iy - e[0], ix - e[1]))
        openh = []; best = {}; prev = {}
        for L in start_layers:
            st = (s[0], s[1], L); best[st] = 0; heapq.heappush(openh, (h(*s), 0, st, None))
        goal = None
        while openh:
            f, c, st, dirn = heapq.heappop(openh)
            if c > best.get(st, 1e18) + 1e-9: continue
            iy, ix, L = st
            if fan:
                px, py = x0 + ix * g, y0 + iy * g
                pb = task.get("pad_bbox")
                outside = True
                if pb:   # la vía no debe quedar dentro del pad (evita via-in-pad)
                    ddx = max(pb[0] - px, 0, px - pb[2]); ddy = max(pb[1] - py, 0, py - pb[3])
                    outside = math.hypot(ddx, ddy) >= vd / 2 + 0.05
                if L in task.get("a_layers", tl) and outside and not any(Bv[l2][iy, ix] for l2 in LAY) and math.hypot(iy - s[0], ix - s[1]) * g >= task.get("min_off", 0.0):
                    goal = st; break
            elif (iy, ix) == e and L in end_layers: goal = st; break
            for dy, dx, k in nbr:
                ny_, nx_ = iy + dy, ix + dx
                if not (0 <= ny_ < ny and 0 <= nx_ < nx) or not free[L][ny_, nx_]: continue
                turn = 0.3 if dirn and dirn != (dy, dx) else 0
                nc = c + k * task.get("layer_cost", LCOST).get(L, 1.0) + turn
                ns = (ny_, nx_, L)
                if nc < best.get(ns, 1e18):
                    best[ns] = nc; prev[ns] = st; heapq.heappush(openh, (nc + h(ny_, nx_), nc, ns, (dy, dx)))
            if not any(Bv[l][iy, ix] for l in LAY):      # vía pasante: holgura en TODAS las capas
                for L2 in tl:
                    if L2 == L: continue
                    ns = (iy, ix, L2); nc = c + vcost
                    if nc < best.get(ns, 1e18):
                        best[ns] = nc; prev[ns] = st; heapq.heappush(openh, (nc + h(iy, ix), nc, ns, None))
        if not goal:
            # reintento con pista/vía más delgada (sigue respetando las holguras)
            if task.get("w", 0) > task.get("w_min", task.get("w", 0)) + 1e-9 or (task.get("fanout") and task.get("via_d", 0.45) > 0.401):
                t2 = dict(task); t2["w"] = task.get("w_min", task["w"]); t2["via_d"] = min(task.get("via_d", 0.45), 0.4)
                t2["via_drill"] = min(task.get("via_drill", 0.2), 0.2); t2["w_min"] = t2["w"]
                print("REINTENTO:", task["net"], task["a"]); queue.insert(0, t2); continue
            print("SIN RUTA:", task); out.append({"type": "fail", "task": task}); continue
        path = [goal]
        while path[-1] in prev: path.append(prev[path[-1]])
        path.reverse()
        pts = [(x0 + ix * g, y0 + iy * g, L) for iy, ix, L in path]
        pts[0] = (task["a"][0], task["a"][1], pts[0][2])
        if not fan: pts[-1] = (task["b"][0], task["b"][1], pts[-1][2])
        # quitar puntos de rejilla pegados a los extremos exactos (evita micro-tramos colgantes)
        while len(pts) > 2 and pts[1][2] == pts[0][2] and math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]) < 1.01 * g:
            pts.pop(1)
        while len(pts) > 2 and pts[-2][2] == pts[-1][2] and math.hypot(pts[-2][0] - pts[-1][0], pts[-2][1] - pts[-1][1]) < 1.01 * g:
            pts.pop(-2)
        # comprimir en segmentos colineales y vías
        segs = []; cur = [pts[0]]
        for p in pts[1:]:
            if p[2] != cur[-1][2]:
                segs.append(cur); out.append({"type": "via", "a": [p[0], p[1]], "net": net, "d": vd, "drill": vdr})
                cur = [p]; continue
            if len(cur) >= 2:
                (ax, ay, _), (bx, by, _) = cur[-2], cur[-1]
                if abs((bx - ax) * (p[1] - by) - (by - ay) * (p[0] - bx)) < 1e-6:
                    cur[-1] = p; continue
            cur.append(p)
        segs.append(cur)
        if fan:
            out.append({"type": "via", "a": [pts[-1][0], pts[-1][1]], "net": net, "d": vd, "drill": vdr})
        for sg in segs:
            for a, b in zip(sg, sg[1:]):
                if math.hypot(a[0] - b[0], a[1] - b[1]) < 1e-6: continue
                tr = {"type": "track", "a": [a[0], a[1]], "b": [b[0], b[1]], "w": w, "layer": a[2], "net": net}
                out.append(tr); objs.append((net, {a[2]}, "seg", (tr["a"], tr["b"], w)))
        for o in out[n_before:]:
            if o["type"] == "via":
                objs.append((net, set(LAY), "circ", (o["a"][0], o["a"][1], o["d"] / 2)))
                holes.append((o["a"][0], o["a"][1], o["drill"] / 2))
        print("ok", net, task["a"], "->", task["b"], "segmentos:", sum(len(s) - 1 for s in segs))
    json.dump(out, open(out_json, "w"), indent=1)

if __name__ == "__main__":
    main(*sys.argv[1:4])
