"""Hand-authored curves: Catmull-Rom splines (open / closed), offsets, tapered strokes."""
import numpy as np


def catmull(pts, closed=False, n_per=12, alpha=0.5):
    """Centripetal Catmull-Rom through points -> dense polyline."""
    P = np.asarray(pts, float)
    if closed:
        P = np.vstack([P[-1:], P, P[:2]])
    else:
        P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t0 = 0.0
        t1 = t0 + max(np.hypot(*(p1 - p0)) ** alpha, 1e-6)
        t2 = t1 + max(np.hypot(*(p2 - p1)) ** alpha, 1e-6)
        t3 = t2 + max(np.hypot(*(p3 - p2)) ** alpha, 1e-6)
        ts = np.linspace(t1, t2, n_per, endpoint=False)[:, None]
        A1 = (t1 - ts) / (t1 - t0) * p0 + (ts - t0) / (t1 - t0) * p1
        A2 = (t2 - ts) / (t2 - t1) * p1 + (ts - t1) / (t2 - t1) * p2
        A3 = (t3 - ts) / (t3 - t2) * p2 + (ts - t2) / (t3 - t2) * p3
        B1 = (t2 - ts) / (t2 - t0) * A1 + (ts - t0) / (t2 - t0) * A2
        B2 = (t3 - ts) / (t3 - t1) * A2 + (ts - t1) / (t3 - t1) * A3
        out.append((t2 - ts) / (t2 - t1) * B1 + (ts - t1) / (t2 - t1) * B2)
    if not closed:
        out.append(P[-2:-1])
    return np.vstack(out)


def ring_offset(ring, d):
    """Offsets a closed ring outward by d (positive = outward for a counter-clockwise ring)."""
    r = np.asarray(ring, float)
    area = 0.5 * np.sum(r[:, 0] * np.roll(r[:, 1], -1) - np.roll(r[:, 0], -1) * r[:, 1])
    t = np.roll(r, -1, 0) - np.roll(r, 1, 0)
    t /= np.maximum(np.hypot(t[:, 0], t[:, 1])[:, None], 1e-9)
    n = np.stack([t[:, 1], -t[:, 0]], 1)          # right normal: outward for CCW
    if area < 0:
        n = -n
    return r + n * d


def taper(n, w0, w1=None, wmid=None, ends=(0.2, 0.2), lo=0.15):
    """Width profile: w0 at start .. w1 at end (linear), multiplied by soft tapers over the given fractions."""
    w1 = w0 if w1 is None else w1
    t = np.linspace(0, 1, n)
    w = w0 + (w1 - w0) * t
    if wmid is not None:
        w = w + (wmid - (w0 + w1) / 2) * np.sin(np.pi * t)
    a, b = ends
    f = np.ones(n)
    if a > 0:
        f = np.minimum(f, lo + (1 - lo) * np.clip(t / a, 0, 1) ** 0.7)
    if b > 0:
        f = np.minimum(f, lo + (1 - lo) * np.clip((1 - t) / b, 0, 1) ** 0.7)
    return w * f


def stroke(pts, widths):
    p = np.asarray(pts, float)
    return {'stroke': np.round(np.c_[p, widths], 3).tolist()}


def poly(*rings):
    return {'poly': [np.round(np.asarray(r, float), 3).tolist() for r in rings]}
