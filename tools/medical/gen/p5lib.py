"""Helpers for the physio-5 generators (outlines in plane mm, y up)."""
import math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

def poly(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"

def arc(cx, cy, r, a0, a1, n=16, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]

def rrect_pts(x0, y0, x1, y1, r, n=6):
    if isinstance(r, (int, float)): r = [r] * 4      # corners: (x1,y0) (x1,y1) (x0,y1) (x0,y0)
    a, b, c, d = r
    return (arc(x1 - a, y0 + a, a, -90, 0, n) + arc(x1 - b, y1 - b, b, 0, 90, n) +
            arc(x0 + c, y1 - c, c, 90, 180, n) + arc(x0 + d, y0 + d, d, 180, 270, n))

def rrect(x0, y0, x1, y1, r, n=6):
    return poly(rrect_pts(x0, y0, x1, y1, r, n))

def arch_pts(x0, x1, y0, h, r, n=10):
    """Half-stadium: flat bottom at y0, straight top at y0+h, shoulders of radius r (r <= h)."""
    return [(x0, y0), (x1, y0)] + arc(x1 - r, y0 + h - r, r, 0, 90, n) + arc(x0 + r, y0 + h - r, r, 90, 180, n)

def star_outline(cx, cz, n, r_tip, w_root, w_tip, a0=90, hub=None):
    """n tapering spokes (rounded tips) around (cx, cz) in the top plane; a0 = angle of the first spoke (deg, 90 = +z)."""
    pts = []
    for k in range(n):
        a = math.radians(a0 + 360 * k / n)
        ux, uz = math.cos(a), math.sin(a); vx, vz = -uz, ux
        # root corners sit on a small circle where neighbouring spokes meet
        rr = w_root / (2 * math.tan(math.pi / n))
        p_r1 = (cx + ux * rr - vx * w_root / 2, cz + uz * rr - vz * w_root / 2)
        tip = r_tip - w_tip / 2
        p_t1 = (cx + ux * tip - vx * w_tip / 2, cz + uz * tip - vz * w_tip / 2)
        pts.append(p_r1); pts.append(p_t1)
        # rounded tip: half circle from -v to +v through +u
        for j in range(1, 8):
            t = math.pi * j / 8
            pts.append((cx + ux * tip + (-vx * math.cos(t) + ux * math.sin(t)) * w_tip / 2,
                        cz + uz * tip + (-vz * math.cos(t) + uz * math.sin(t)) * w_tip / 2))
        pts.append((cx + ux * tip + vx * w_tip / 2, cz + uz * tip + vz * w_tip / 2))
        pts.append((cx + ux * rr + vx * w_root / 2, cz + uz * rr + vz * w_root / 2))
    return poly(pts)

def spoke_tips(cx, cz, n, r, a0=90):
    return [(cx + r * math.cos(math.radians(a0 + 360 * k / n)), cz + r * math.sin(math.radians(a0 + 360 * k / n))) for k in range(n)]
