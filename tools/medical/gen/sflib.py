"""Shared parts of the XY-K-SF treatment tables (Treatment Table.pdf) — used by sf.py.
Frame: the table's length runs along x, its width along z (front = z = D), y up. Millimetres."""
import math
from lib import D, rot

PAD = "leather#9ec5e8"
MATS = {
    "pad": PAD,
    "frame": "plastic#f1f2f4",      # white powder-coated steel
    "grey": "plastic#c3c8cf",       # light-grey panels / covers
    "fillet": "plastic#666b73",     # dark-grey covers on the convex face of the swan arms
    "cap": "rubber#1f2124",         # black end caps / plugs / feet
    "bolt": "plastic#2b2e33",       # black bolt heads, pivots
    "steel": "metal#b9bdc3",        # stainless foot bars, gas springs
    "act": "plastic#a9aeb5",        # grey Linak actuators
    "letter": "plastic#9aa0a8",     # grey "XIANG YU / MEDICAL" lettering
}


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def poly_path(pts, close=True):
    s = "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in pts)
    return s + (" Z" if close else "")


def rrect_pts(x0, z0, x1, z1, r, n=6):
    """Rounded rectangle as a point list (counter-clockwise in a, b)."""
    r = min(r, (x1 - x0) / 2 - 0.1, (z1 - z0) / 2 - 0.1)
    pts = []
    for cx, cz, a0 in ((x1 - r, z0 + r, -90), (x1 - r, z1 - r, 0), (x0 + r, z1 - r, 90), (x0 + r, z0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def chamfer_pts(x0, z0, x1, z1, cx, cz, r, n=5):
    """Long hexagon/octagon (ends tapered: corners cut by cx along x and cz across), corners rounded r."""
    raw = [(x0 + cx, z0), (x1 - cx, z0), (x1, z0 + cz), (x1, z1 - cz), (x1 - cx, z1), (x0 + cx, z1), (x0, z1 - cz), (x0, z0 + cz)]
    return round_poly(raw, r, n)


def round_poly(raw, r, n=5):
    pts = []
    m = len(raw)
    for i in range(m):
        a, c, b = raw[i - 1], raw[i], raw[(i + 1) % m]
        da = norm((a[0] - c[0], a[1] - c[1])); db = norm((b[0] - c[0], b[1] - c[1]))
        la = math.dist(a, c); lb = math.dist(b, c)
        ang = math.acos(max(-1, min(1, da[0] * db[0] + da[1] * db[1])))
        t = min(r / math.tan(ang / 2) if ang > 1e-3 else 0, la * 0.45, lb * 0.45)
        p0 = (c[0] + da[0] * t, c[1] + da[1] * t); p1 = (c[0] + db[0] * t, c[1] + db[1] * t)
        for k in range(n + 1):
            s = k / n
            pts.append(((1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * c[0] + s * s * p1[0],
                        (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * c[1] + s * s * p1[1]))
    return pts


def norm(v):
    l = math.hypot(*v) or 1
    return (v[0] / l, v[1] / l)


def stadium_pts(cx, cz, lx, lz, n=10):
    """Stadium (slot) centred at cx, cz: length lx along x, width lz."""
    r = lz / 2
    pts = []
    for k in range(n + 1):
        a = math.radians(-90 + 180 * k / n)
        pts.append((cx + lx / 2 - r + r * math.cos(a), cz + r * math.sin(a)))
    for k in range(n + 1):
        a = math.radians(90 + 180 * k / n)
        pts.append((cx - lx / 2 + r + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def ellipse_pts(cx, cz, rx, rz, n=24):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cz + rz * math.sin(2 * math.pi * k / n)) for k in range(n)]


def quad(p0, c, p1, n=10):
    return [((1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * c[0] + s * s * p1[0],
             (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * c[1] + s * s * p1[1]) for s in (k / n for k in range(n + 1))]


class T(D):
    """A treatment table design with the SF helpers."""

    def __init__(s, id, size, extra=None):
        m = dict(MATS)
        if extra: m.update(extra)
        super().__init__(id, size, m)

    # ---------------------------------------------------------------- upholstery
    def pad(s, id, x0, x1, z0, z1, y0, t=75, cr=55, er=28, r=None, hole=None, outline=None, mat="pad", board=12, plug=True):
        """An upholstered section on a thin white board. hole = (cx, cz, lx, lz) stadium breathing slot."""
        pts = outline or rrect_pts(x0, z0, x1, z1, cr)
        path = poly_path(pts)
        if hole and isinstance(hole, list):           # arbitrary hole outline (point list)
            path += " " + poly_path(hole)
            hole = None
        elif hole:
            path += " " + poly_path(stadium_pts(*hole))
        s.add(id, "slab", mat, plane="top", outline=path, w=[y0, y0 + t], r=er, rot=r)
        if hole and plug:
            cx, cz, lx, lz = hole
            s.add(id + "-plug", "slab", mat, plane="top", outline=poly_path(stadium_pts(cx, cz, lx - 14, lz - 14)),
                  w=[y0 + 8, y0 + t - 9], r=10, rot=r)
        if board:
            bpts = outline and inset(outline, 10) or rrect_pts(x0 + 10, z0 + 10, x1 - 10, z1 - 10, max(cr - 10, 8))
            s.add(id + "-board", "slab", "frame", plane="top", outline=poly_path(bpts), w=[y0 - board, y0 + 1], r=3, rot=r)

    # ---------------------------------------------------------------- frames
    def leg(s, id, x, z, y1, w=60, cap=True, foot=False, copies=None):
        s.box(id, [x - w / 2, 0 if not foot else 18, z - w / 2, x + w / 2, y1, z + w / 2], "frame", r=4, copies=copies)
        if cap:
            s.box(id + "-cap", [x - w / 2 - 1, y1, z - w / 2 - 1, x + w / 2 + 1, y1 + 10, z + w / 2 + 1], "cap", r=3, copies=copies)
        if foot:
            s.box(id + "-foot", [x - w / 2 + 2, 0, z - w / 2 + 2, x + w / 2 - 2, 20, z + w / 2 - 2], "cap", r=3, copies=copies)

    def bolt(s, id, at, face="front", d=18, copies=None):
        x, y, z = at
        a, b = {"front": ([x, y, z], [x, y, z + 6]), "back": ([x, y, z], [x, y, z - 6]),
                "left": ([x, y, z], [x - 6, y, z]), "right": ([x, y, z], [x + 6, y, z])}[face]
        s.cyl(id, a, b, d, "bolt", soft=True, copies=copies)


def inset(pts, d):
    """Crude inset of a convex-ish outline towards its centroid (for boards under shaped pads)."""
    cx = sum(p[0] for p in pts) / len(pts); cz = sum(p[1] for p in pts) / len(pts)
    out = []
    for x, z in pts:
        v = norm((cx - x, cz - z))
        out.append((x + v[0] * d, z + v[1] * d))
    return out


# ------------------------------------------------------------------ mirroring a finished design along x
import re

def _fx(W, x): return round(W - x, 1)

def _flip_path_str(W, sv):
    toks = re.findall(r"[A-Za-z]|-?\d+(?:\.\d+)?", sv)
    out, i, cmd, idx = [], 0, None, 0
    for t in toks:
        if re.match(r"[A-Za-z]", t):
            cmd = t.upper(); idx = 0; out.append(t); continue
        v = float(t)
        if cmd in ("M", "L", "Q", "C"):
            if idx % 2 == 0: v = W - v
        elif cmd == "H":
            v = W - v
        elif cmd == "A":
            k = idx % 7
            if k == 4: v = 1 - v          # sweep flag
            if k == 5: v = W - v
        idx += 1
        out.append(f(v))
    return " ".join(out)

def flip_design(d):
    """Mirror every part of d (a D instance) about the middle of the width (x -> W - x)."""
    W = d.d["size"][0]
    for p in d.d["parts"]:
        k = p["kind"]
        if "box" in p:
            b = p["box"]; p["box"] = [_fx(W, b[3]), b[1], b[2], _fx(W, b[0]), b[4], b[5]]
        for key in ("from", "to", "at"):
            if key in p and isinstance(p[key], list) and not (k == "loft"):
                if k == "lathe" and p.get("axis") == "x": raise Exception("lathe along x not flippable")
                p[key] = [_fx(W, p[key][0])] + p[key][1:]
        if "path" in p:
            p["path"] = [[_fx(W, q[0])] + q[1:] for q in p["path"]]
        if k == "slab":
            pl = p.get("plane", "front")
            if "outline" in p and pl in ("top", "front"):
                p["outline"] = _flip_path_str(W, p["outline"])
            if pl == "side" and "w" in p:
                p["w"] = [_fx(W, p["w"][1]), _fx(W, p["w"][0])]
        if k == "loft":
            ax = p.get("axis", "y")
            for sct in p["sections"]:
                if ax == "x": sct["at"] = _fx(W, sct["at"])
                elif "cx" in sct: sct["cx"] = _fx(W, sct["cx"])
        if "face" in p:
            p["face"] = {"left": "right", "right": "left"}.get(p["face"], p["face"])
        if "rot" in p:
            r_ = p["rot"]
            r_["about"] = [_fx(W, r_["about"][0])] + r_["about"][1:]
            if r_["axis"] in ("y", "z"): r_["deg"] = -r_["deg"]
        if "copies" in p:
            p["copies"] = [[-c[0]] + c[1:] for c in p["copies"]]
        if "repeat" in p:
            p["repeat"]["step"] = [-p["repeat"]["step"][0]] + p["repeat"]["step"][1:]
