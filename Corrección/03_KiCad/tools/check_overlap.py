# Lista solapes de courtyard (bbox) entre huellas y huellas fuera del contorno. uso: check_overlap.py board.json
import json, sys
d = json.load(open(sys.argv[1])); e = d["edge"]; f = d["fps"]
bad = 0
for i in range(len(f)):
    a = f[i]["bbox"]
    if a[0] < e[0] - 0.01 or a[1] < e[1] - 0.01 or a[2] > e[2] + 0.01 or a[3] > e[3] + 0.01:
        print("FUERA", f[i]["ref"], [round(v, 2) for v in a]); bad += 1
    for j in range(i + 1, len(f)):
        b = f[j]["bbox"]
        ox = min(a[2], b[2]) - max(a[0], b[0]); oy = min(a[3], b[3]) - max(a[1], b[1])
        if ox > 0.01 and oy > 0.01:
            print("SOLAPE", f[i]["ref"], f[j]["ref"], round(ox, 2), round(oy, 2)); bad += 1
print("problemas:", bad)
