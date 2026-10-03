"""Helpers of batch kinesio-5 on top of lib.py / p1lib.py (used by the k5_*.py generators only)."""
import math
from p1lib import *  # D, rot, sec, rep, text(), rpoly(), arc() ...


def circ(cx, cy, r):
    """SVG circle path (for slab outlines)."""
    return f"M {cx - r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 1 0 {cx + r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 1 0 {cx - r:.1f} {cy:.1f} Z"


def poly(pts):
    """SVG path of a closed polygon."""
    return "M " + " L ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts) + " Z"


def rocker_outline(x0, x1, ytop, sag, n=24):
    """Front-plane outline of a rocker: flat top at ytop from x0 to x1, circular arc bottom sagging by `sag`
    (lowest point at y = ytop - sag in the middle, ends meeting the top)."""
    half = (x1 - x0) / 2.0
    R = (half * half + sag * sag) / (2 * sag)
    cx, cy = (x0 + x1) / 2.0, ytop - sag + R
    pts = [(x0, ytop), (x1, ytop)]
    a0 = math.asin(half / R)
    for k in range(n + 1):
        a = a0 - 2 * a0 * k / n
        pts.append((cx + R * math.sin(a), cy - R * math.cos(a)))
    return poly(pts)


def rope(d, id, pts, mat="fabric#f2f2ee", dd=6, **kw):
    """Thin soft rope / cable polyline."""
    return d.tube(id, pts, dd, mat, soft=True, **kw)


def pulley(d, id, at, dd, w, axis, mat="black#1c1c1e", hub="chrome", **kw):
    """Grooved pulley wheel with a hub."""
    d.add(id, "wheel", mat, at=at, d=dd, d2=w, axis=axis, **kw)
    d.add(id + "-hub", "wheel", hub, at=at, d=dd * 0.35, d2=w + 6, axis=axis, **kw)


def knob(d, id, at, axis="x", flip=False, dd=44, mat="plastic#18191b", **kw):
    """Black star/ball clamp knob sticking out along +axis (or -axis when flip)."""
    r = dd / 2.0
    prof = [[0, 0], [7, 0], [7, 14], [r, 18], [r, r + 14], [r * 0.6, r + 22], [0, r + 23]]
    rr = None
    if flip:
        rr = rot({"x": "y", "z": "y", "y": "x"}[axis], 180, at)
    return d.lathe(id, at, prof, mat, axis=axis, rot=rr, **kw)


def shift(d, dx=0.0, dz=0.0):
    """Move every part by (dx, 0, dz) (review 2026-10-03: so that `size` covers the whole model). Lofts move by
    their section centres; slabs are not supported (assert)."""
    def mv(p3):
        return [p3[0] + dx, p3[1], p3[2] + dz]
    for p in d.d["parts"]:
        assert p["kind"] != "slab", p["id"]
        if "box" in p:
            b = p["box"]; p["box"] = [b[0] + dx, b[1], b[2] + dz, b[3] + dx, b[4], b[5] + dz]
        for k in ("from", "to", "at"):
            if k in p:
                p[k] = mv(p[k])
        if "path" in p:
            p["path"] = [mv(q) for q in p["path"]]
        if "sections" in p:
            ax = p.get("axis") or "y"
            for s in p["sections"]:
                if ax == "y":
                    s["cx"] += dx; s["cz"] += dz
                elif ax == "z":
                    s["cx"] += dx; s["at"] += dz
                else:  # x: cz = z, at = x
                    s["cz"] += dz; s["at"] += dx
        for r in ([p["rot"]] if "rot" in p else []) + p.get("rots", []):
            r["about"] = mv(r["about"])
