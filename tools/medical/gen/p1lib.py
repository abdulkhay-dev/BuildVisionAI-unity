"""Helpers of batch physio-1 on top of lib.py (shared by the physio-1 generators only)."""
import math
from lib import *


def rr_path(cx, cz, w, d, r, y, n=5):
    """Closed rounded-rectangle polyline in the x-z plane at height y (first point repeated at the end)."""
    hw, hd = w / 2.0, d / 2.0
    r = min(r, hw, hd)
    pts = []
    corners = [(hw - r, hd - r, 0), (-hw + r, hd - r, 90), (-hw + r, -hd + r, 180), (hw - r, -hd + r, 270)]
    for (ux, uz, a0) in corners:
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append([cx + ux + r * math.cos(a), y, cz + uz + r * math.sin(a)])
    pts.append(list(pts[0]))
    return pts


def arc(cx, cz, rx, rz, a0, a1, y, n=12):
    """Elliptic arc in the x-z plane at height y, angles in degrees (0 = +x, 90 = +z)."""
    out = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        out.append([cx + rx * math.cos(a), y, cz + rz * math.sin(a)])
    return out


def rotx(p, deg, about):
    """Point p rotated about the x axis through `about` (+deg turns y towards +z), as the engine does."""
    a = math.radians(deg)
    y, z = p[1] - about[1], p[2] - about[2]
    return [p[0], about[1] + y * math.cos(a) - z * math.sin(a), about[2] + y * math.sin(a) + z * math.cos(a)]


def _bar(s, id, a, b, section, mat, **kw): return s.add(id, "bar", mat, **{"from": a, "to": b}, section=section, **kw)
def _lathe(s, id, at, profile, mat, **kw): return s.add(id, "lathe", mat, at=at, profile=profile, **kw)
def _sphere(s, id, at, dd, mat, **kw): return s.add(id, "sphere", mat, at=at, d=dd, **kw)
def _decal(s, id, at, size, mat, face="front", **kw): return s.add(id, "decal", mat, at=at, size=size, face=face, **kw)
def _screen(s, id, box, mat, **kw): return s.add(id, "screen", mat, box=box, **kw)
def _slab(s, id, plane, outline, w, mat, **kw): return s.add(id, "slab", mat, plane=plane, outline=outline, w=w, **kw)
def _loft(s, id, sections, mat, **kw): return s.add(id, "loft", mat, sections=sections, **kw)
def _caster(s, id, at, dd, mat="rubber", **kw): return s.add(id, "caster", mat, at=at, d=dd, **kw)
D.bar, D.lathe, D.sphere, D.decal, D.screen, D.slab, D.loft, D.caster = _bar, _lathe, _sphere, _decal, _screen, _slab, _loft, _caster


def sec(at, w, dd, r, cx, cz):
    return {"at": at, "w": w, "d": dd, "r": r, "cx": cx, "cz": cz}


# ---- stroke lettering (review 2026-10-02): letters drawn as rotated decal strokes on a front face ----
# glyphs in a box of cap height 1, (u along the line, v up); advance = width + gap
_FONT = {
    "X": (0.6, [[(0, 0), (0.6, 1)], [(0, 1), (0.6, 0)]]),
    "I": (0.0, [[(0, 0), (0, 1)]]),
    "A": (0.62, [[(0, 0), (0.31, 1), (0.62, 0)], [(0.13, 0.38), (0.49, 0.38)]]),
    "N": (0.6, [[(0, 0), (0, 1), (0.6, 0), (0.6, 1)]]),
    "G": (0.62, [[(0.62, 0.8), (0.45, 1), (0.15, 1), (0, 0.78), (0, 0.22), (0.15, 0), (0.47, 0), (0.62, 0.2), (0.62, 0.45), (0.36, 0.45)]]),
    "Y": (0.6, [[(0, 1), (0.3, 0.5), (0.6, 1)], [(0.3, 0.5), (0.3, 0)]]),
    "U": (0.58, [[(0, 1), (0, 0.22), (0.15, 0), (0.43, 0), (0.58, 0.22), (0.58, 1)]]),
    "M": (0.72, [[(0, 0), (0, 1), (0.36, 0.3), (0.72, 1), (0.72, 0)]]),
    "E": (0.5, [[(0.5, 1), (0, 1), (0, 0), (0.5, 0)], [(0, 0.5), (0.42, 0.5)]]),
    "D": (0.58, [[(0, 0), (0, 1), (0.3, 1), (0.58, 0.75), (0.58, 0.25), (0.3, 0), (0, 0)]]),
    "C": (0.6, [[(0.6, 0.8), (0.45, 1), (0.15, 1), (0, 0.78), (0, 0.22), (0.15, 0), (0.45, 0), (0.6, 0.2)]]),
    "L": (0.48, [[(0, 1), (0, 0), (0.48, 0)]]),
    "S": (0.58, [[(0.58, 0.82), (0.43, 1), (0.14, 1), (0, 0.8), (0.1, 0.58), (0.48, 0.42), (0.58, 0.2), (0.44, 0), (0.12, 0), (0, 0.18)]]),
    "O": (0.64, [[(0.18, 0), (0, 0.25), (0, 0.75), (0.18, 1), (0.46, 1), (0.64, 0.75), (0.64, 0.25), (0.46, 0), (0.18, 0)]]),
    "H": (0.58, [[(0, 0), (0, 1)], [(0.58, 0), (0.58, 1)], [(0, 0.5), (0.58, 0.5)]]),
    "K": (0.56, [[(0, 0), (0, 1)], [(0.56, 1), (0, 0.4)], [(0.18, 0.58), (0.56, 0)]]),
    "R": (0.56, [[(0, 0), (0, 1), (0.4, 1), (0.56, 0.86), (0.56, 0.62), (0.4, 0.48), (0, 0.48)], [(0.3, 0.48), (0.56, 0)]]),
    "T": (0.6, [[(0, 1), (0.6, 1)], [(0.3, 1), (0.3, 0)]]),
    "P": (0.54, [[(0, 0), (0, 1), (0.38, 1), (0.54, 0.86), (0.54, 0.6), (0.38, 0.46), (0, 0.46)]]),
    "V": (0.6, [[(0, 1), (0.3, 0), (0.6, 1)]]),
    "W": (0.84, [[(0, 1), (0.2, 0), (0.42, 0.7), (0.64, 0), (0.84, 1)]]),
    "B": (0.56, [[(0, 0), (0, 1), (0.4, 1), (0.54, 0.88), (0.54, 0.62), (0.4, 0.52), (0, 0.52)], [(0.4, 0.52), (0.56, 0.4), (0.56, 0.12), (0.42, 0), (0, 0)]]),
    "F": (0.5, [[(0.5, 1), (0, 1), (0, 0)], [(0, 0.52), (0.42, 0.52)]]),
    "8": (0.5, [[(0, 0), (0.5, 0), (0.5, 1), (0, 1), (0, 0)], [(0, 0.5), (0.5, 0.5)]]),
    "+": (0.6, [[(0, 0.5), (0.6, 0.5)], [(0.3, 0.2), (0.3, 0.8)]]),
    "-": (0.6, [[(0, 0.5), (0.6, 0.5)]]),
    "n": (0.48, [[(0, 0), (0, 0.62)], [(0, 0.44), (0.12, 0.6), (0.36, 0.62), (0.48, 0.5), (0.48, 0)]]),
    "u": (0.48, [[(0, 0.62), (0, 0.12), (0.12, 0), (0.36, 0.02), (0.48, 0.16)], [(0.48, 0.62), (0.48, 0)]]),
    "y": (0.52, [[(0, 0.62), (0.27, 0.04)], [(0.52, 0.62), (0.2, -0.3), (0.08, -0.34)]]),
    "o": (0.52, [[(0.26, 0), (0.05, 0.1), (0, 0.31), (0.05, 0.52), (0.26, 0.62), (0.47, 0.52), (0.52, 0.31), (0.47, 0.1), (0.26, 0)]]),
    "宇": (0.9, [[(0.45, 1), (0.45, 0.9)], [(0.04, 0.74), (0.04, 0.86), (0.86, 0.86), (0.86, 0.74)], [(0.16, 0.62), (0.74, 0.62)],
               [(0, 0.4), (0.9, 0.4)], [(0.45, 0.62), (0.45, 0), (0.34, 0.05)]]),
    "翔": (0.95, [[(0.1, 1), (0.17, 0.9)], [(0.36, 1), (0.29, 0.9)], [(0.02, 0.86), (0.42, 0.86)], [(0.05, 0.62), (0.4, 0.62)],
               [(0, 0.38), (0.44, 0.38)], [(0.22, 0.86), (0.22, 0)], [(0.52, 0.9), (0.7, 0.9), (0.7, 0.05), (0.64, 0)],
               [(0.75, 0.9), (0.95, 0.9), (0.95, 0.05), (0.89, 0)]]),
}


def text_len(s, h, gap=0.28):
    return sum(((_FONT[c][0] + gap) if c in _FONT else 0.45) for c in s) * h - gap * h


def text(d, id, s, origin, h, mat, along=(1, 0), stroke=None, gap=0.28, z=None, face="front", soft=True):
    """Text `s` of cap height h on a face: origin = the bottom-left of the first letter [x, y, z];
    `along` = unit reading direction in the face plane (front: (dx, dy) in x/y; side faces: (dz, dy));
    letters' up = `along` turned +90 deg. Each stroke is a decal turned in the face plane."""
    st = stroke or max(1.5, h * 0.14)
    ux, uy = along
    vx, vy = -uy, ux
    n = 0
    pen = 0.0
    for c in s:
        if c not in _FONT:
            pen += 0.45; continue
        wch, polys = _FONT[c]
        for poly in polys:
            for (a, b) in zip(poly, poly[1:]):
                pa = (pen + a[0], a[1]); pb = (pen + b[0], b[1])
                mu, mv = (pa[0] + pb[0]) / 2 * h, (pa[1] + pb[1]) / 2 * h
                du, dv = (pb[0] - pa[0]) * h, (pb[1] - pa[1]) * h
                ln = math.hypot(du, dv)
                # direction in the face plane
                wx, wy = du * ux + dv * vx, du * uy + dv * vy
                cx, cy = mu * ux + mv * vx, mu * uy + mv * vy
                ang = math.degrees(math.atan2(wy, wx))
                if face == "front":
                    at = [origin[0] + cx, origin[1] + cy, origin[2]]
                    d.add(f"{id}-{n}", "decal", mat, at=at, size=[ln + st, st], face="front", soft=soft,
                          rot={"axis": "z", "deg": round(ang, 1), "about": at})
                elif face == "top":  # plane coordinates (x, -z): letters' up points to the back
                    at = [origin[0] + cx, origin[1], origin[2] - cy]
                    d.add(f"{id}-{n}", "decal", mat, at=at, size=[ln + st, st], face="top", soft=soft,
                          rot={"axis": "y", "deg": round(ang, 1), "about": at})
                else:  # left / right: plane coordinates are (z, y)
                    at = [origin[0], origin[1] + cy, origin[2] + cx]
                    # about x: +deg turns y towards +z, so a stroke along +z turned by deg ... towards +y is -deg
                    d.add(f"{id}-{n}", "decal", mat, at=at, size=[ln + st, st], face=face, soft=soft,
                          rot={"axis": "x", "deg": round(-ang, 1), "about": at})
                n += 1
        pen += wch + gap
    return n


def rpoly(pts, r):
    """SVG path of a closed polygon with its corners rounded by r (quadratic corners)."""
    n = len(pts); out = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        def toward(a, b, dist):
            dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; k = min(dist, L / 2) / L
            return (a[0] + dx * k, a[1] + dy * k)
        a = toward(p1, p0, r); b = toward(p1, p2, r)
        out.append(("M" if i == 0 else "L") + f" {a[0]:.1f} {a[1]:.1f} Q {p1[0]:.1f} {p1[1]:.1f} {b[0]:.1f} {b[1]:.1f}")
    return " ".join(out) + " Z"
