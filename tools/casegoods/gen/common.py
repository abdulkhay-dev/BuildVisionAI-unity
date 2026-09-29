"""Helpers for writing designs by script (optional): one part per line, like the hand-written files."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DESIGNS = os.path.join(ROOT, "Assets/House4696/Resources/Casegoods/Designs")


def dump(did, size, parts, moves):
    lines = ["{", f'  "id": "{did}",', f'  "size": {json.dumps(size)},', '  "parts": [']
    lines.append(",\n".join("    " + json.dumps(p, ensure_ascii=False) for p in parts))
    lines.append("  ],")
    lines.append('  "moves": [')
    lines.append(",\n".join("    " + json.dumps(m, ensure_ascii=False) for m in moves))
    lines.append("  ]")
    lines.append("}")
    path = os.path.join(DESIGNS, did + ".json")
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def ring(pid, at, d, z, dia=112, band=12, t=5, standoff=10):
    return {"id": pid, "kind": "handle", "model": "ring-half", "at": at, "dir": d, "d": dia, "band": band, "t": t,
            "standoff": standoff, "z": z, "covers": ["k1"]}


def drawer_box(tag, x0, x1, y0, h, z0, z1, bottom_t=3.5, n=("6.2", "6.3", "6.4", "6.5")):
    """Box between x0..x1 (outer), y0..y0+h, from z0 (back) to z1 (the front's back face): sides, back, bottom in grooves."""
    s, b = [], []
    s.append({"n": n[0], "id": f"{n[0]}-{tag}", "box": [x0, y0, z0, x0 + 16, y0 + h, z1]})
    s.append({"n": n[1], "id": f"{n[1]}-{tag}", "box": [x1 - 16, y0, z0, x1, y0 + h, z1]})
    s.append({"n": n[2], "id": f"{n[2]}-{tag}", "box": [x0 + 16, y0, z0, x1 - 16, y0 + h, z0 + 16]})
    s.append({"n": n[3], "id": f"{n[3]}-{tag}", "kind": "back", "box": [x0 + 11, y0 + 10, z0 + 4, x1 - 11, y0 + 10 + bottom_t, z1 - 2]})
    return s


def feet(xs, zs, h=4, d=20, n="g"):
    out = []
    k = 0
    for x in xs:
        for z in zs:
            k += 1
            out.append({"id": f"{n}-{k}", "kind": "tube", "mat": "black", "box": [x - d / 2, 0, z - d / 2, x + d / 2, h, z + d / 2], "covers": [n]})
    return out
