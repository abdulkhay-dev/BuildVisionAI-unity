"""Smooth closed shapes from a field on the grid: threshold -> contours -> Gaussian smoothing along the contour."""
import numpy as np
import cv2
from scipy import ndimage


def smooth_ring(p, sigma_pts):
    n = len(p)
    if sigma_pts <= 0 or n < 8:
        return p
    k1 = min(int(3 * sigma_pts) + 1, n // 2)
    t = np.arange(-k1, k1 + 1)
    ker = np.exp(-0.5 * (t / sigma_pts) ** 2); ker /= ker.sum()
    pp = np.concatenate([p[-k1:], p, p[:k1]])
    return np.stack([np.convolve(pp[:, 0], ker, 'valid'), np.convolve(pp[:, 1], ker, 'valid')], 1)


def resample_ring(p, step):
    q = np.vstack([p, p[:1]])
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(q, axis=0).T))]
    n = max(8, int(d[-1] / step))
    s = np.linspace(0, d[-1], n, endpoint=False)
    return np.stack([np.interp(s, d, q[:, 0]), np.interp(s, d, q[:, 1])], 1)


def mask_rings(mask, res, H, smooth_mm=0.6, step_mm=0.25, min_area_mm2=0.5, tol_mm=0.02):
    """Binary mask on the grid (row 0 at y = H, res px/mm) -> items [{'poly': [outer, holes...]}] in mm, ordered by
    nesting depth (outer items first). Contours at the pixel boundary, smoothed along their length."""
    up = 4
    m = cv2.resize(mask.astype(np.uint8) * 255, (mask.shape[1] * up, mask.shape[0] * up), interpolation=cv2.INTER_LINEAR)
    m = (m > 127).astype(np.uint8)
    cs, hier = cv2.findContours(m, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if hier is None:
        return []
    hier = hier[0]
    depth = []
    for i in range(len(cs)):
        d, p = 0, hier[i][3]
        while p >= 0:
            d += 1; p = hier[p][3]
        depth.append(d)
    rings = {}
    for i, c in enumerate(cs):
        p = c[:, 0, :].astype(np.float64)
        xm = (p[:, 0] + 0.5) / (res * up)
        ym = H - (p[:, 1] + 0.5) / (res * up)
        q = np.stack([xm, ym], 1)
        area = abs(cv2.contourArea(q.astype(np.float32)))
        if area < min_area_mm2:
            rings[i] = None
            continue
        q = resample_ring(q, step_mm)
        q = smooth_ring(q, smooth_mm / step_mm)
        q = cv2.approxPolyDP(q.astype(np.float32).reshape(-1, 1, 2), tol_mm, True)[:, 0, :].astype(np.float64)
        rings[i] = q
    items = []
    for i in sorted(range(len(cs)), key=lambda i: depth[i]):
        if depth[i] % 2 == 1 or rings[i] is None:
            continue
        holes = []
        ch = hier[i][2]
        while ch >= 0:
            if rings.get(ch) is not None:
                holes.append(rings[ch])
            ch = hier[ch][0]
        items.append({'poly': [np.round(rings[i], 3).tolist()] + [np.round(h, 3).tolist() for h in holes], 'depth': depth[i]})
    return items
