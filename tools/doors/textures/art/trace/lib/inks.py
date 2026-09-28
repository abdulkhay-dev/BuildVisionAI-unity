import numpy as np
from scipy import ndimage
import tr

LUMA = np.array([0.299, 0.587, 0.114])


def satin_ink(fname, level=150.0, pct=85, win=61, cols=None):
    """Dark motif on satin: ink = (bg - grey) / (bg - level); white highlight = (grey - bg) / (255 - bg).
    bg = a high percentile along each column (long vertical window) - the satin with its shading."""
    rgb = tr.load_rgb(fname)
    g = rgb @ LUMA
    bg = ndimage.percentile_filter(g, pct, size=(win, 1), mode='nearest')
    bg = ndimage.gaussian_filter(bg, (win / 8, 0.5))
    dark = (bg - g) / np.maximum(bg - level, 10)
    white = (g - bg) / np.maximum(255 - bg, 8)
    return rgb, g, bg, dark, white


def mirror_ink(fname, level=195.0, size=9):
    """Light motif on a dark mirror: bg = grey opening (removes the thin motif)."""
    rgb = tr.load_rgb(fname)
    g = rgb @ LUMA
    bg = ndimage.uniform_filter(ndimage.grey_opening(g, size=(size, size)), size)
    ink = (g - bg) / np.maximum(level - bg, 20)
    return rgb, g, bg, ink


def box_weight(view_shape, view, boxes_mm):
    """Weight 1 except inside pane-mm boxes (x0, y0, x1, y1)."""
    w = np.ones(view_shape)
    H, W = view_shape
    rr, cc = np.mgrid[0:H, 0:W]
    xm, ym = view.mm_of(cc + 0.5, rr + 0.5)
    for x0, y0, x1, y1 in boxes_mm:
        w[(xm >= x0) & (xm <= x1) & (ym >= y0) & (ym <= y1)] = 0
    return w
