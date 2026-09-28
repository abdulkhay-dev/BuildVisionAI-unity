"""Row-wise tracking of thin, mostly vertical lines in an ink map on a mm grid (pane mm, y up)."""
import numpy as np
from scipy import ndimage, interpolate


def row_peaks(row, thr, min_sep=2):
    """Sub-pixel positions and heights of local maxima above thr."""
    r = row
    k = np.nonzero((r[1:-1] > thr) & (r[1:-1] >= r[:-2]) & (r[1:-1] > r[2:]))[0] + 1
    out = []
    for i in k:
        a, b, c = r[i - 1], r[i], r[i + 1]
        den = a - 2 * b + c
        off = 0.5 * (a - c) / den if abs(den) > 1e-9 else 0.0
        out.append((i + float(np.clip(off, -0.5, 0.5)), b))
    # enforce min separation (keep higher)
    out.sort()
    res = []
    for p in out:
        if res and p[0] - res[-1][0] < min_sep:
            if p[1] > res[-1][1]:
                res[-1] = p
        else:
            res.append(p)
    return res


def track(M, res, H, thr=0.25, step_mm=0.5, max_jump_mm=1.2, max_gap_mm=6.0, min_len_mm=10.0, smooth_mm=1.0):
    """Tracks of ridge peaks row by row (top to bottom). M on a grid of `res` px/mm, row 0 at y = H.
    Returns list of arrays (n, 3): x_mm, y_mm, peak."""
    Ms = ndimage.gaussian_filter1d(M, smooth_mm * res, axis=1)
    Ms = ndimage.gaussian_filter1d(Ms, smooth_mm * res, axis=0)
    rstep = max(1, int(round(step_mm * res)))
    active, done = [], []
    for r in range(0, M.shape[0], rstep):
        y = H - (r + 0.5) / res
        pk = [((c + 0.5) / res, h) for c, h in row_peaks(Ms[r], thr)]
        # predictions
        preds = []
        for t in active:
            pts = t['pts']
            if len(pts) >= 3:
                (x1, y1, _), (x2, y2, _) = pts[-3], pts[-1]
                slope = (x2 - x1) / (y2 - y1) if abs(y2 - y1) > 1e-9 else 0.0
                preds.append(x2 + slope * (y - y2))
            else:
                preds.append(pts[-1][0])
        # greedy matching by distance
        pairs = sorted(((abs(p[0] - preds[i]), i, j) for i in range(len(active)) for j, p in enumerate(pk)))
        ut, up = set(), set()
        for d, i, j in pairs:
            gap = active[i]['pts'][-1][1] - y
            if d > max_jump_mm * max(1.0, gap / step_mm) ** 0.5:
                continue
            if i in ut or j in up:
                continue
            ut.add(i); up.add(j)
            active[i]['pts'].append((pk[j][0], y, pk[j][1]))
        keep = []
        for i, t in enumerate(active):
            if i in ut or t['pts'][-1][1] - y <= max_gap_mm:
                keep.append(t)
            else:
                done.append(t)
        active = keep
        for j, p in enumerate(pk):
            if j not in up:
                active.append({'pts': [(p[0], y, p[1])]})
    done += active
    out = []
    for t in done:
        a = np.array(t['pts'])
        if a[0, 1] - a[-1, 1] >= min_len_mm:
            out.append(a)
    return out


def fit_track(a, s_mm=0.3, step=1.0):
    """Smoothing spline x(y) through a track -> resampled (n, 2) points x, y (top to bottom)."""
    y = a[:, 1][::-1]; x = a[:, 0][::-1]
    keep = np.r_[True, np.diff(y) > 1e-6]
    y, x = y[keep], x[keep]
    spl = interpolate.UnivariateSpline(y, x, k=3, s=len(y) * s_mm ** 2)
    yy = np.arange(y[0], y[-1], step)
    if len(yy) < 2:
        yy = np.array([y[0], y[-1]])
    return np.stack([spl(yy), yy], 1)[::-1]


def link(tracks, max_dy=60.0, max_dev=6.0, min_len=0):
    """Joins tracks across gaps (crossings): the bottom end of one continues into the top of another when the
    straight-line prediction from its last 20 mm lands within max_dev mm. Returns chains (lists of track indices)."""
    ends = []
    for i, a in enumerate(tracks):
        tail = a[-min(len(a), 20):]
        dy = tail[0, 1] - tail[-1, 1]
        slope = (tail[-1, 0] - tail[0, 0]) / -dy if dy > 1e-6 else 0.0   # dx per mm downwards
        ends.append((a[-1, 0], a[-1, 1], slope))
    starts = []
    for a in tracks:
        head = a[:min(len(a), 20)]
        dy = head[0, 1] - head[-1, 1]
        slope = (head[-1, 0] - head[0, 0]) / dy if dy > 1e-6 else 0.0
        starts.append((a[0, 0], a[0, 1], slope))
    cand = []
    for i, (xe, ye, se) in enumerate(ends):
        for j, (xs, ys, ss) in enumerate(starts):
            if i == j:
                continue
            gap = ye - ys
            if gap < -8 or gap > max_dy:
                continue
            pred = xe + se * max(gap, 0)
            dev = abs(pred - xs) + 0.5 * abs(se - ss) * max(gap, 5)
            if dev <= max_dev:
                cand.append((dev + 0.02 * gap, i, j))
    cand.sort()
    nxt, prv = {}, {}
    for c, i, j in cand:
        if i in nxt or j in prv:
            continue
        # no cycles
        k = j
        while k in nxt:
            k = nxt[k]
        if k == i:
            continue
        nxt[i] = j; prv[j] = i
    chains = []
    for i in range(len(tracks)):
        if i in prv:
            continue
        ch = [i]
        while ch[-1] in nxt:
            ch.append(nxt[ch[-1]])
        chains.append(ch)
    return chains
