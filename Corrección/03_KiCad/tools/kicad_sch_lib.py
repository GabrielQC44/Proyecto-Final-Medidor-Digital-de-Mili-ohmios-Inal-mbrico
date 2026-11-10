# -*- coding: utf-8 -*-
"""Utilidades para escribir esquemáticos KiCad (.kicad_sch) a partir de una netlist.
Cada pin recibe un tramo de cable y una etiqueta local con el nombre de su red; los
pines sin conexión reciben una marca No-Connect. Es la forma más trazable de garantizar
que la netlist KiCad sea idéntica a la de origen."""
import re, uuid as _uuid

KICAD_SYM = "C:/Program Files/KiCad/10.0/share/kicad/symbols/"

def U():
    return str(_uuid.uuid4())

def _block(text, start):
    d = 0
    for j in range(start, len(text)):
        if text[j] == '(':
            d += 1
        elif text[j] == ')':
            d -= 1
            if d == 0:
                return text[start:j + 1]
    raise ValueError

def get_symbol(lib, name):
    t = open(KICAD_SYM + lib + ".kicad_sym", encoding="utf-8").read()
    m = re.search(r'\(symbol "%s"\s' % re.escape(name), t)
    return _block(t, m.start())

def flat_symbol(lib, name):
    """Devuelve el símbolo con 'extends' resuelto, renombrado a 'lib:name'."""
    s = get_symbol(lib, name)
    m = re.search(r'\(extends "([^"]+)"\)', s)
    if m:
        parent = flat_symbol(lib, m.group(1)).replace(f'"{lib}:{m.group(1)}"', '"PARENT"', 1)
        parent = parent.replace(f'(symbol "{m.group(1)}_', f'(symbol "{name}_')
        # propiedades del hijo reemplazan a las del padre
        child_props = re.findall(r'\(property "[^"]+"', s)
        for cp in child_props:
            key = cp.split('"')[1]
            i = parent.find(f'(property "{key}"')
            if i >= 0:
                blk = _block(parent, i)
                ci = s.find(f'(property "{key}"')
                parent = parent.replace(blk, _block(s, ci), 1)
        s = parent.replace('"PARENT"', f'"{name}"', 1)
    s = s.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)
    return s

def pins_of(sym, unit=None):
    """[(number, name, x, y, angle)] de un símbolo. Con unit=n, solo pines de la unidad n (y de la 0)."""
    out = []
    if unit is not None:
        parts = []
        for m in re.finditer(r'\(symbol "[^"]*_(\d+)_(\d+)"', sym):
            u = int(m.group(1))
            if u in (0, unit):
                parts.append(_block(sym, m.start()))
        sym = "\n".join(parts)
    for m in re.finditer(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', sym):
        blk = _block(sym, m.start())
        num = re.search(r'\(number "([^"]*)"', blk).group(1)
        nam = re.search(r'\(name "([^"]*)"', blk).group(1)
        out.append((num, nam, float(m.group(1)), float(m.group(2)), float(m.group(3))))
    return out

def module_symbol(libname, name, left, right, ref="U", width=17.78, pin_len=3.81):
    """Símbolo rectangular: left/right = lista de (num, nombre, tipo) de arriba a abajo."""
    n = max(len(left), len(right))
    h = (n + 1) * 2.54
    top = h / 2
    pins = []
    for side, lst in (("L", left), ("R", right)):
        for i, (num, nm, typ) in enumerate(lst):
            y = top - 2.54 * (i + 1)
            y = round(y / 1.27) * 1.27
            if side == "L":
                x, ang = -width / 2 - pin_len, 0
            else:
                x, ang = width / 2 + pin_len, 180
            pins.append(f'''(pin {typ} line (at {x:.2f} {y:.2f} {ang}) (length {pin_len})
          (name "{nm}" (effects (font (size 1.27 1.27))))
          (number "{num}" (effects (font (size 1.27 1.27)))))''')
    body = f'''(symbol "{libname}:{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "{ref}" (at 0 {top + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
      (property "Value" "{name}" (at 0 {-top - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "{name}_0_1"
        (rectangle (start {-width/2:.2f} {top:.2f}) (end {width/2:.2f} {-top:.2f})
          (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "{name}_1_1"
        {chr(10).join(pins)})
    )'''
    return body


class Sheet:
    def __init__(self, project, title, paper="A3"):
        self.project, self.title, self.paper = project, title, paper
        self.root = U()
        self.libsyms = {}
        self.items = []
        self.wired = set()          # redes que se dibujan con cables (no con etiquetas)
        self.wpts = {}              # red -> [(x, y)] extremos de los tramos de pin

    def add_lib(self, lib_id, text):
        self.libsyms[lib_id] = text

    def text(self, s, x, y, size=2.0, bold=True):
        b = " bold" if bold else ""
        self.items.append(f'(text "{s}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) '
                          f'(effects (font (size {size} {size}){" (bold yes)" if bold else ""}) (justify left bottom)) (uuid "{U()}"))')

    def rect(self, x1, y1, x2, y2):
        self.items.append(f'(rectangle (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) '
                          f'(stroke (width 0.2) (type dash)) (fill (type none)) (uuid "{U()}"))')

    def place(self, lib_id, ref, value, fp, x, y, pinnets, mpn="", extra=None, stub=2.54, unit=1, in_bom=True, on_board=True):
        sym = self.libsyms[lib_id]
        multi = len(set(int(m) for m in re.findall(r'\(symbol "[^"]*_(\d+)_\d+"', sym)) - {0}) > 1
        pins = pins_of(sym, unit if multi else None)
        x = round(x / 1.27) * 1.27
        y = round(y / 1.27) * 1.27
        props = [("Reference", ref, 0, -2), ("Value", value, 0, 2), ("Footprint", fp, None, None),
                 ("Datasheet", "", None, None), ("MPN", mpn, None, None)]
        if extra:
            props += [(k, v, None, None) for k, v in extra.items()]
        ptxt = []
        # posición de textos: arriba / abajo del cuerpo
        ys = [p[3] for p in pins] or [0]
        xs = [p[2] for p in pins] or [0]
        for k, v, dx, dy in props:
            hide = " (hide yes)" if dx is None else ""
            if k == "Reference":
                px, py = x + max(xs) * 0 + 2.54, y - max(max(ys), 2.54) - 2.0
            elif k == "Value":
                px, py = x + 2.54, y - min(min(ys), -2.54) + (4.0 if len(pins) > 6 else 2.0)
            else:
                px, py = x, y
            ptxt.append(f'(property "{k}" "{v}" (at {px:.2f} {py:.2f} 0) '
                        f'(effects (font (size 1.27 1.27)) (justify left){hide}))')
        pin_uu = "\n".join(f'(pin "{p[0]}" (uuid "{U()}"))' for p in pins)
        self.items.append(f'''(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit {unit})
    (exclude_from_sim no) (in_bom {"yes" if in_bom else "no"}) (on_board {"yes" if on_board else "no"}) (dnp no) (uuid "{U()}")
    {chr(10).join(ptxt)}
    {pin_uu}
    (instances (project "{self.project}" (path "/{self.root}" (reference "{ref}") (unit {unit})))))''')
        # cables + etiquetas
        for num, nam, px, py, ang in pins:
            ax, ay = x + px, y - py
            net = pinnets.get(num, "__MISSING__")
            if net is None:
                self.items.append(f'(no_connect (at {ax:.2f} {ay:.2f}) (uuid "{U()}"))')
                continue
            if net == "__MISSING__":
                raise KeyError(f"{ref}.{num} sin red")
            if ang == 0:
                bx, by, la, j = ax - stub, ay, 180, "right"
            elif ang == 180:
                bx, by, la, j = ax + stub, ay, 0, "left"
            elif ang == 90:
                bx, by, la, j = ax, ay + stub, 270, "right"
            else:
                bx, by, la, j = ax, ay - stub, 90, "left"
            self.items.append(f'(wire (pts (xy {ax:.2f} {ay:.2f}) (xy {bx:.2f} {by:.2f})) '
                              f'(stroke (width 0) (type default)) (uuid "{U()}"))')
            if net in self.wired:
                self.wpts.setdefault(net, []).append((round(bx, 2), round(by, 2)))
                continue
            self.items.append(f'(label "{net}" (at {bx:.2f} {by:.2f} {la}) '
                              f'(effects (font (size 1.0 1.0)) (justify {j} bottom)) (uuid "{U()}"))')

    def connect_wired(self, hv_first=None):
        """Une con cables en L (árbol mínimo) los pines de cada red 'wired'; agrega uniones (junction)."""
        segs = []
        for net, pts in self.wpts.items():
            pts = list(dict.fromkeys(pts))
            used = [pts[0]]; rem = pts[1:]
            while rem:
                a, b = min(((a, b) for a in used for b in rem), key=lambda t: abs(t[0][0]-t[1][0]) + abs(t[0][1]-t[1][1]))
                hfirst = (hv_first or {}).get(net, True)
                c = (b[0], a[1]) if hfirst else (a[0], b[1])
                for p, q in ((a, c), (c, b)):
                    if p != q:
                        segs.append((net, p, q))
                used.append(b); rem.remove(b)
        for net, pts in self.wpts.items():   # etiqueta con el nombre de la red (conserva el nombre en netlist/PCB)
            x, y = pts[0]
            self.items.append(f'(label "{net}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.0 1.0)) (justify left bottom)) (uuid "{U()}"))')
        for net, p, q in segs:
            self.items.append(f'(wire (pts (xy {p[0]:.2f} {p[1]:.2f}) (xy {q[0]:.2f} {q[1]:.2f})) '
                              f'(stroke (width 0) (type default)) (uuid "{U()}"))')
        # uniones: punto con 3+ extremos o extremo sobre el interior de otro tramo de la misma red
        from collections import Counter
        cnt = Counter()
        for net, p, q in segs:
            cnt[(net, p)] += 1; cnt[(net, q)] += 1
        for net, pts in self.wpts.items():
            for pt in set(pts): cnt[(net, pt)] += 1
        jn = {pt for (net, pt), c in cnt.items() if c >= 3}
        for net, p, q in segs:
            for (n2, pt), c in list(cnt.items()):
                if n2 != net or pt in (p, q): continue
                if (p[0] == q[0] == pt[0] and min(p[1], q[1]) < pt[1] < max(p[1], q[1])) or                    (p[1] == q[1] == pt[1] and min(p[0], q[0]) < pt[0] < max(p[0], q[0])):
                    jn.add(pt)
        for pt in jn:
            self.items.append(f'(junction (at {pt[0]:.2f} {pt[1]:.2f}) (diameter 0) (color 0 0 0 0) (uuid "{U()}"))')

    def pwr_flag(self, net, x, y):
        self.place("power:PWR_FLAG", f"#FLG0{len([i for i in self.items if 'PWR_FLAG' in i])+1}",
                   "PWR_FLAG", "", x, y, {"1": net})

    def write(self, path, date, rev, company=""):
        libs = "\n".join(self.libsyms.values())
        txt = f'''(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")
  (uuid "{self.root}")
  (paper "{self.paper}")
  (title_block (title "{self.title}") (date "{date}") (rev "{rev}") (company "{company}"))
  (lib_symbols
{libs}
  )
{chr(10).join(self.items)}
  (sheet_instances (path "/" (page "1")))
)
'''
        open(path, "w", encoding="utf-8").write(txt)
