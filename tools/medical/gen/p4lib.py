"""Outline helpers for the physio-4 generators (plane coordinates in mm, y up)."""
import math

def poly(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"

def arc(cx, cy, r, a0, a1, n=16):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]

def rrect_pts(x0, y0, x1, y1, r, n=6):
    return (arc(x1 - r, y0 + r, r, -90, 0, n) + arc(x1 - r, y1 - r, r, 0, 90, n) +
            arc(x0 + r, y1 - r, r, 90, 180, n) + arc(x0 + r, y0 + r, r, 180, 270, n))

def rrect(x0, y0, x1, y1, r, n=6):
    return poly(rrect_pts(x0, y0, x1, y1, r, n))

def ring(x0, y0, x1, y1, r, t, ri=None):
    """Rounded rectangular frame of width t."""
    return rrect(x0, y0, x1, y1, r) + " " + rrect(x0 + t, y0 + t, x1 - t, y1 - t, ri if ri is not None else max(r - t, 2))

def arch_pts(x0, x1, y0, ys, n=20):
    """Tombstone: straight sides from y0 to ys, a half circle on top."""
    cx, r = (x0 + x1) / 2, (x1 - x0) / 2
    return [(x0, y0), (x1, y0)] + arc(cx, ys, r, 0, 180, n)

def qpts(p0, c, p1, n=12):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]) for t in (k / n for k in range(n + 1))]

def band(pts, half):
    L, R = [], []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l * half, dx / l * half
        L.append((p[0] + nx, p[1] + ny)); R.append((p[0] - nx, p[1] - ny))
    return poly(L + R[::-1])
