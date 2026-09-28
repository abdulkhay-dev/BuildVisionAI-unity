"""Tracing helpers: catalogue photo -> ink map in pane millimetres -> binary super-resolution -> vector contours.

Pane coordinates: millimetres, origin at the bottom-left corner of the visible glass, x right, y up (as the photo
shows it). A hi-res grid of `res` px/mm covers the pane: row 0 at the top (y = H).
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
import cv2

DOORS = __import__('pathlib').Path(__file__).resolve().parents[4]
sys.path.insert(0, str(DOORS))
import measure  # noqa: E402

PHOTOS = str(DOORS / '.cache' / 'photos') + '/'
_leaf_cache = {}


def leaf_of(fname, bounds=None, bottom=None):
    key = (fname, bounds, bottom)
    if key not in _leaf_cache:
        rgb, grey = measure.load_photo(PHOTOS + fname)
        _leaf_cache[key] = measure.find_leaf(grey, bounds=bounds, bottom=bottom)
    return _leaf_cache[key]


def load_rgb(fname):
    return np.asarray(Image.open(PHOTOS + fname).convert('RGB')).astype(np.float64)


class View:
    """One photo of the pane. pane = (x0, y0, x1, y1) of the visible glass in leaf mm (y up from the leaf bottom).
    ink: 2D array over the whole photo (0 = background glass, 1 = full ink); weight: same shape."""

    def __init__(self, fname, pane, ink, weight=None, leaf=None, psf=0.5, name=None):
        self.fname = fname
        self.name = name or fname
        self.leaf = leaf or leaf_of(fname)
        self.pane = pane
        self.ink = ink
        self.weight = np.ones_like(ink) if weight is None else weight
        self.psf = psf               # Gaussian sigma of (pixel footprint + render/JPEG blur), photo px
        L = self.leaf
        self.sx, self.sy = L['sx'], L['sy']   # px per mm

    def px_of(self, xm, ym):
        """Pane mm -> photo px (continuous)."""
        L = self.leaf
        X = L['x0'] + (self.pane[0] + xm) * self.sx
        Y = L['y1'] - (self.pane[1] + ym) * self.sy
        return X, Y

    def mm_of(self, X, Y):
        L = self.leaf
        return (X - L['x0']) / self.sx - self.pane[0], (L['y1'] - Y) / self.sy - self.pane[1]

    def samples(self, W, H, margin=0.0):
        """Photo pixels whose centres fall inside the pane (shrunk by margin mm): their pane-mm centres, ink, weight."""
        X0, Y1 = self.px_of(margin, margin)
        X1, Y0 = self.px_of(W - margin, H - margin)
        c0, c1 = int(np.ceil(X0 - 0.5)), int(np.floor(X1 - 0.5))
        r0, r1 = int(np.ceil(Y0 - 0.5)), int(np.floor(Y1 - 0.5))
        r0, c0 = max(r0, 0), max(c0, 0)
        r1, c1 = min(r1, self.ink.shape[0] - 1), min(c1, self.ink.shape[1] - 1)
        rr, cc = np.mgrid[r0:r1 + 1, c0:c1 + 1]
        xm, ym = self.mm_of(cc + 0.5, rr + 0.5)
        return xm, ym, self.ink[r0:r1 + 1, c0:c1 + 1], self.weight[r0:r1 + 1, c0:c1 + 1], (r0, c0)


class Grid:
    def __init__(self, W, H, res):
        self.W, self.H, self.res = W, H, res
        self.nx, self.ny = int(round(W * res)), int(round(H * res))

    def rc(self, xm, ym):
        """mm -> continuous (row, col) index (pixel centres at integers)."""
        return (self.H - ym) * self.res - 0.5, xm * self.res - 0.5


def _bilinear_setup(grid, xm, ym):
    r, c = grid.rc(xm, ym)
    r = np.clip(r, 0, grid.ny - 1.001)
    c = np.clip(c, 0, grid.nx - 1.001)
    r0 = np.floor(r).astype(np.int64); c0 = np.floor(c).astype(np.int64)
    fr = r - r0; fc = c - c0
    idx = [(r0, c0, (1 - fr) * (1 - fc)), (r0 + 1, c0, fr * (1 - fc)), (r0, c0 + 1, (1 - fr) * fc),
           (r0 + 1, c0 + 1, fr * fc)]
    return idx


class Op:
    """Forward operator of one view: hi-res coverage -> predicted ink at the view's photo pixels."""

    def __init__(self, grid, view, margin=0.0):
        self.grid, self.view = grid, view
        xm, ym, ink, w, self.origin = view.samples(grid.W, grid.H, margin)
        self.shape = ink.shape
        self.m = ink.ravel()
        self.w = w.ravel()
        self.idx = _bilinear_setup(grid, xm.ravel(), ym.ravel())
        # blur on the hi-res grid = the photo pixel footprint + psf, in hi-res px
        self.sig = (view.psf / view.sy * grid.res, view.psf / view.sx * grid.res)

    def fwd(self, c):
        b = ndimage.gaussian_filter(c, self.sig, mode='nearest')
        out = np.zeros(self.m.shape)
        for r, cc, wt in self.idx:
            out += wt * b[r, cc]
        return out

    def adj(self, v):
        acc = np.zeros((self.grid.ny, self.grid.nx))
        for r, cc, wt in self.idx:
            np.add.at(acc, (r, cc), wt * v)
        return ndimage.gaussian_filter(acc, self.sig, mode='nearest')


def tv_grad(c, eps=0.05):
    gx = np.zeros_like(c); gy = np.zeros_like(c)
    gx[:, :-1] = c[:, 1:] - c[:, :-1]
    gy[:-1, :] = c[1:, :] - c[:-1, :]
    n = np.sqrt(gx * gx + gy * gy + eps * eps)
    px, py = gx / n, gy / n
    div = px.copy(); div[:, 1:] -= px[:, :-1]
    div += py; div[1:, :] -= py[:-1, :]
    return -div


def solve(grid, ops, init, lam=0.15, mu=3.0, iters=300, lr=0.05, fixed=None, verbose=False):
    """Coverage c on the grid minimising sum_views w (A c - m)^2 + lam * perimeter + mu * c(1-c).
    Perimeter and area terms are expressed per photo px (scaled by the hi-res px size of the first view)."""
    c = np.clip(init.copy(), 0, 1)
    v0 = ops[0].view
    f = grid.res / v0.sx          # hi-res px per photo px
    mt = np.zeros_like(c); vt = np.zeros_like(c)
    b1, b2 = 0.9, 0.999
    for it in range(iters):
        m_it = mu * min(1.0, it / (0.6 * iters))
        g = np.zeros_like(c)
        err = 0.0
        for op in ops:
            r = op.fwd(c) - op.m
            err += float((op.w * r * r).sum())
            g += 2 * op.adj(op.w * r)
        g += lam / f * tv_grad(c)
        g += m_it / (f * f) * (1 - 2 * c)
        mt = b1 * mt + (1 - b1) * g
        vt = b2 * vt + (1 - b2) * g * g
        mh = mt / (1 - b1 ** (it + 1)); vh = vt / (1 - b2 ** (it + 1))
        c = np.clip(c - lr * mh / (np.sqrt(vh) + 1e-12), 0, 1)
        if fixed is not None:
            c[fixed[0]] = fixed[1][fixed[0]]
        if verbose and (it % 50 == 0 or it == iters - 1):
            print('  it %d err %.4f binar %.4f' % (it, err, float((c * (1 - c)).mean())))
    return c


def init_from_views(grid, views, gamma=1.0):
    """Initial coverage: the views' ink resampled to the grid (bilinear), averaged."""
    ys = grid.H - (np.arange(grid.ny) + 0.5) / grid.res
    xs = (np.arange(grid.nx) + 0.5) / grid.res
    X, Y = np.meshgrid(xs, ys)
    acc = np.zeros((grid.ny, grid.nx)); wsum = np.zeros_like(acc)
    for v in views:
        px, py = v.px_of(X, Y)
        val = ndimage.map_coordinates(v.ink, [py - 0.5, px - 0.5], order=3, mode='nearest')
        wt = ndimage.map_coordinates(v.weight, [py - 0.5, px - 0.5], order=1, mode='nearest')
        acc += val * wt; wsum += wt
    return np.clip(acc / np.maximum(wsum, 1e-6), 0, 1) ** gamma


def clean(c, grid, smooth_px=1.5, min_area_mm2=1.0, min_hole_mm2=1.0):
    """Binary from the coverage: smoothed, specks and pinholes removed."""
    b = ndimage.gaussian_filter(c, smooth_px) > 0.5
    px_area = 1.0 / grid.res ** 2
    lab, n = ndimage.label(b)
    if n:
        areas = ndimage.sum(np.ones_like(b, float), lab, index=np.arange(1, n + 1)) * px_area
        keep = np.concatenate([[False], areas >= min_area_mm2])
        b = keep[lab]
    lab, n = ndimage.label(~b)
    if n:
        areas = ndimage.sum(np.ones_like(b, float), lab, index=np.arange(1, n + 1)) * px_area
        fill = np.concatenate([[False], areas < min_hole_mm2])
        b = b | fill[lab]
    return b


def contours(b, grid, smooth=1.2, tol=0.02, up=2):
    """Vector contours of a binary on the grid, in pane mm: list of (points (n,2) [x, y], is_hole).
    The binary is upsampled x`up` (nearest) and its pixel contours smoothed (Gaussian along the contour, `smooth`
    grid px), then simplified (Douglas-Peucker, tol mm)."""
    bb = np.repeat(np.repeat(b.astype(np.uint8), up, 0), up, 1)
    cs, hier = cv2.findContours(bb, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    if hier is None:
        return out
    hier = hier[0]
    for k, cnt in enumerate(cs):
        p = cnt[:, 0, :].astype(np.float64)       # (x=col, y=row) in up-px, pixel corner based
        if len(p) < 8:
            continue
        # pixel centres -> the boundary lies half a px outside; cv2 contours run through boundary pixel centres
        s = smooth * up
        if s > 0:
            n = len(p)
            k1 = int(3 * s) + 1
            t = np.arange(-k1, k1 + 1)
            ker = np.exp(-0.5 * (t / s) ** 2); ker /= ker.sum()
            pp = np.concatenate([p[-k1:], p, p[:k1]])
            p = np.stack([np.convolve(pp[:, 0], ker, 'valid'), np.convolve(pp[:, 1], ker, 'valid')], 1)
        xm = (p[:, 0] + 0.5) / (grid.res * up)
        ym = grid.H - (p[:, 1] + 0.5) / (grid.res * up)
        pts = np.stack([xm, ym], 1)
        pts = cv2.approxPolyDP(pts.astype(np.float32).reshape(-1, 1, 2), tol, True)[:, 0, :].astype(np.float64)
        is_hole = hier[k][3] >= 0
        out.append((pts, is_hole))
    return out


def field_from_views(grid, views, arrays, order=3):
    """Average of per-view arrays (same shape as each view's photo) resampled onto the grid, weighted."""
    ys = grid.H - (np.arange(grid.ny) + 0.5) / grid.res
    xs = (np.arange(grid.nx) + 0.5) / grid.res
    X, Y = np.meshgrid(xs, ys)
    acc = None; wsum = np.zeros((grid.ny, grid.nx))
    for v, a in zip(views, arrays):
        px, py = v.px_of(X, Y)
        wt = ndimage.map_coordinates(v.weight, [py - 0.5, px - 0.5], order=1, mode='nearest')
        if a.ndim == 3:
            val = np.stack([ndimage.map_coordinates(a[..., k], [py - 0.5, px - 0.5], order=order, mode='nearest')
                            for k in range(a.shape[2])], -1)
            acc = val * wt[..., None] if acc is None else acc + val * wt[..., None]
        else:
            val = ndimage.map_coordinates(a, [py - 0.5, px - 0.5], order=order, mode='nearest')
            acc = val * wt if acc is None else acc + val * wt
        wsum += wt
    if acc.ndim == 3:
        return acc / np.maximum(wsum, 1e-6)[..., None]
    return acc / np.maximum(wsum, 1e-6)


def sampler(grid, F):
    """(x_mm, y_mm) -> bilinear sample of a grid field."""
    def f(X, Y):
        r, c = grid.rc(np.asarray(X), np.asarray(Y))
        return ndimage.map_coordinates(F, [r, c], order=1, mode='nearest')
    return f
