"""Shared helpers of the physio-3 generators (on top of lib.py)."""
import math, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

ROOT = "/Users/abdulxay/Documents/works/ansormed/unity"


def rpoly(pts, radii):
    """SVG path of a closed polygon whose corners are rounded by quadratic curves (radius = distance cut back)."""
    n = len(pts)
    if not isinstance(radii, (list, tuple)): radii = [radii] * n
    segs = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        r = radii[i]
        if r <= 0:
            segs.append(("L", p1)); continue
        def toward(a, b, d):
            l = math.hypot(b[0] - a[0], b[1] - a[1]); d = min(d, l * 0.49)
            return (a[0] + (b[0] - a[0]) * d / l, a[1] + (b[1] - a[1]) * d / l)
        a = toward(p1, p0, r); b = toward(p1, p2, r)
        segs.append(("L", a)); segs.append(("Q", p1, b))
    out = []
    first = segs[0]
    start = first[1] if first[0] == "L" else first[2]
    out.append(f"M {start[0]:.1f} {start[1]:.1f}")
    for s in segs[1:] + [segs[0]]:
        if s[0] == "L": out.append(f"L {s[1][0]:.1f} {s[1][1]:.1f}")
        else: out.append(f"Q {s[1][0]:.1f} {s[1][1]:.1f} {s[2][0]:.1f} {s[2][1]:.1f}")
    out.append("Z")
    return " ".join(out)


def ellipse_pts(cx, cy, rx, ry, n=32, a0=0.0):
    return [(cx + rx * math.cos(a0 + 2 * math.pi * i / n), cy + ry * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def poly(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def rep(n, step): return {"n": n, "step": step}


class Tilt:
    """A plane tilted about x: local horizontal coordinates (x, s = distance from the hinge edge towards the back,
    h = height above the plane) → parts drawn flat at the hinge height and turned up by the tilt."""
    def __init__(s, y, z, deg):
        s.y, s.z, s.deg = y, z, deg
        s.r = rot("x", deg, [0, y, z])
    def box(s, d, id, x0, s0, x1, s1, h0, h1, mat, r=None, **kw):
        return d.box(id, [x0, s.y + h0, s.z - s1, x1, s.y + h1, s.z - s0], mat, r=r, rot=s.r, **kw)
    def pt(s, x, sv, h=0):
        return [x, s.y + h, s.z - sv]
    def world(s, x, sv, h=0):
        a = math.radians(s.deg)
        # +deg about x turns y towards +z: y' = h cos a + sv sin a, z' = h sin a − sv cos a
        return [x, s.y + h * math.cos(a) + sv * math.sin(a), s.z + h * math.sin(a) - sv * math.cos(a)]


def render(ids, timeout=120):
    """Wait until Unity has rendered every design in ids (the .txt newer than the json); print the statuses."""
    t0 = time.time()
    pending = list(ids)
    while pending and time.time() - t0 < timeout:
        for i in list(pending):
            j = f"{ROOT}/Assets/House4696/Resources/Medical/Designs/{i}.json"
            t = f"{ROOT}/tools/medical/renders/{i}.txt"
            if os.path.exists(t) and os.path.getmtime(t) > os.path.getmtime(j):
                pending.remove(i)
                print(i, open(t).read().strip())
        time.sleep(2)
    for i in pending: print(i, "TIMEOUT")
