"""Binary super-resolution of a low-res 'ink' map: find a hi-res coverage field c in [0,1] (nearly binary, smooth
contours) whose box-downsampled + blurred version matches the ink map."""
import numpy as np
from scipy import ndimage


def down(c, f):
    h, w = c.shape
    return c.reshape(h // f, f, w // f, f).mean((1, 3))


def up(r, f):
    return np.repeat(np.repeat(r, f, 0), f, 1) / (f * f)


def blur(a, s):
    return ndimage.gaussian_filter(a, s, mode='nearest') if s > 0 else a


def upsample_smooth(m, f, order=3):
    """Cubic spline upsampling, pixel-centre aligned."""
    h, w = m.shape
    yy = (np.arange(h * f) + 0.5) / f - 0.5
    xx = (np.arange(w * f) + 0.5) / f - 0.5
    Y, X = np.meshgrid(yy, xx, indexing='ij')
    return ndimage.map_coordinates(m, [Y, X], order=order, mode='nearest')


def tv_grad(c, eps=0.05):
    gx = np.diff(c, axis=1, append=c[:, -1:])
    gy = np.diff(c, axis=0, append=c[-1:, :])
    n = np.sqrt(gx * gx + gy * gy + eps * eps)
    px, py = gx / n, gy / n
    div = (px - np.roll(px, 1, 1)) + (py - np.roll(py, 1, 0))
    div[:, 0] = px[:, 0]
    div[0, :] += py[0, :] - (py - np.roll(py, 1, 0))[0, :]
    return -div


def solve(m, f=8, psf=0.4, lam=0.15, mu_max=2.0, iters=300, lr=0.05, weight=None, init=None, verbose=False):
    """m: ink map (low res, ~0..1). Returns hi-res coverage (h*f, w*f)."""
    m = np.asarray(m, np.float64)
    if weight is None:
        weight = np.ones_like(m)
    c = np.clip(upsample_smooth(m, f), 0, 1) if init is None else init.copy()
    mt = np.zeros_like(c); vt = np.zeros_like(c)
    b1, b2 = 0.9, 0.999
    for it in range(iters):
        mu = mu_max * min(1.0, it / (0.6 * iters))
        pred = blur(down(c, f), psf)
        r = weight * (pred - m)
        g = 2 * up(blur(r, psf), f)
        g += lam / f * tv_grad(c)
        g += mu / (f * f) * (1 - 2 * c)
        mt = b1 * mt + (1 - b1) * g
        vt = b2 * vt + (1 - b2) * g * g
        mh = mt / (1 - b1 ** (it + 1)); vh = vt / (1 - b2 ** (it + 1))
        c = np.clip(c - lr * mh / (np.sqrt(vh) + 1e-12), 0, 1)
        if verbose and it % 50 == 0:
            print(it, float((r ** 2).mean()), float((c * (1 - c)).mean()))
    return c
