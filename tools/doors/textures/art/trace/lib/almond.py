"""Pointed leaf / bud shapes ("almonds") and fitting them to a mask."""
import numpy as np
import cv2
from scipy import optimize


def almond(B, T, wmax, skew=1.0, p=1.0, bend=0.0, asym=0.0, n=80):
    """Closed outline (n*2, 2) from base B to tip T. Half width wmax*sin(pi*t^skew)^p; centre line bent by `bend`
    (mm, towards the left normal); asym shifts width between the sides (-1..1)."""
    B = np.asarray(B, float); T = np.asarray(T, float)
    ax = T - B
    L = np.hypot(*ax)
    u = ax / max(L, 1e-9)
    nrm = np.array([-u[1], u[0]])
    t = np.linspace(0, 1, n)
    c = B[None, :] + t[:, None] * ax[None, :] + (bend * np.sin(np.pi * t))[:, None] * nrm[None, :]
    h = wmax * np.sin(np.pi * np.clip(t, 0, 1) ** skew) ** p
    left = c + (h * (1 + asym))[:, None] * nrm[None, :]
    right = c - (h * (1 - asym))[:, None] * nrm[None, :]
    return np.vstack([left, right[::-1][1:-1]])


def raster(poly, shape, res, H, x0=0.0):
    img = np.zeros(shape, np.uint8)
    pts = np.stack([(poly[:, 0] - x0) * res * 16, (H - poly[:, 1]) * res * 16], 1)
    cv2.fillPoly(img, [np.round(pts).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=4)
    return img.astype(bool)


def fit(mask, res, H, x0, guess, fixed=()):
    """Fits almond params to a boolean mask (grid rows top = H, cols from x0 mm). guess: dict of params
    (Bx, By, Tx, Ty, wmax, skew, p, bend, asym)."""
    keys = ['Bx', 'By', 'Tx', 'Ty', 'wmax', 'skew', 'p', 'bend', 'asym']
    free = [k for k in keys if k not in fixed]
    m = mask.astype(bool)
    s0 = np.array([guess[k] for k in free], float)

    def params(s):
        g = dict(guess); g.update(dict(zip(free, s)))
        return g

    def loss(s):
        g = params(s)
        if g['wmax'] <= 0.2 or g['skew'] <= 0.2 or g['p'] <= 0.2:
            return 2.0
        poly = almond((g['Bx'], g['By']), (g['Tx'], g['Ty']), g['wmax'], g['skew'], g['p'], g['bend'], g['asym'])
        r = raster(poly, m.shape, res, H, x0)
        inter = (r & m).sum(); uni = (r | m).sum()
        return 1 - inter / max(uni, 1)

    best = None
    for _ in range(3):
        res_ = optimize.minimize(loss, s0, method='Nelder-Mead',
                                 options=dict(maxiter=1500, xatol=0.02, fatol=1e-5, adaptive=True))
        s0 = res_.x
        if best is None or res_.fun < best[0]:
            best = (res_.fun, res_.x)
    return params(best[1]), best[0]
