"""Measure a catalogue door photo: leaf bounds and the edges of its pieces, in leaf millimetres.

    python3 tools/doors/measure.py <photo> [--out overlay.png] [--xband A:B ...] [--yband A:B ...]
                                   [--bounds X0,Y0,X1,Y1] [--bottom Y1] [--min 5] [--json out.json]

<photo> is a file path or a file name inside tools/doors/.cache/photos (see catalog_index.py).

The photos are the manufacturer's orthographic 3D renders: the leaf seen from the front (lock edge on the left, hinges
on the right) inside a border that is the door frame/casing; the photo bottom is the floor. Needs numpy + Pillow.

Leaf bounds (pixels, continuous coordinates: pixel i spans [i, i+1)):
    x0, x1  centres of the dark gaps between the casing and the leaf (median column profile of the middle rows)
    y0      centre of the dark gap under the head casing
    y1      the photo bottom (floor). Cross-check: the two hinges (bright runs in the right gap) sit symmetrically
            on the leaf, so hinge_top + hinge_bottom - y0 is the leaf bottom as well. When the photo is cropped above
            the floor (some catalogue photos are), that estimate is used and a note is printed. --bottom / --bounds
            override the detection.
    The leaf is mapped to 800 x 2000 mm independently along x and y (the catalogue photos are not all scaled
    uniformly; the aspect is reported against 800x2000 = 0.400).

Leaf millimetres (the design coordinates of Docs/door-designs.md): origin at the bottom-left corner of the leaf as
the photo shows it, x to the right (x = 0 is the lock edge), y up.

Features: for every band the tool averages the photo across the band (median of the band's columns for a row profile,
of its rows for a column profile) and reports, along the profile:
    dark    a dark line (joint hairline, shadow under a step, frame gap): position = centre of the dip
    bright  a bright line/strip (glass strip, lit rounded edge): centre, width (half-maximum), and "glass" when the
            strip is near-white
    glass   a run of white, grain-free rows/columns clearly brighter than the wood next to it (a glass pane or
            strip of any width): its half-level edges. Not reliable on white finishes (Bianco, Snow), where the
            wood is as white as the satin glass - measure glass on the mid/dark finishes.
    step    a brightness step between two flat areas (edge of a panel): position of the steepest gradient
with "str" = the contrast in grey levels (sign: + brighter, - darker than the surroundings; for steps the sign of
the change along +mm) and the pixel position. Default bands: --xband 280:520 (rows profile across the middle of the
leaf) and --yband 300:1700 (columns profile). Several bands can be given; each is printed separately.

--out writes the photo enlarged 3x with the leaf bounds (green), the hinges (magenta) and the detected features of
every band drawn over their band (dark = red, bright = cyan, glass = blue, step = yellow, labelled in mm).

It also prints the handle (rosette centre, from the difference to a vertical running median of the wood) and the
finish colour (mean of the stiles without outliers - the "color" of catalog.json finishes).

Library use (preview2d.py imports it): load_photo(), find_leaf(), find_hinges(), find_handle(), finish_colour(),
px_to_mm()/mm_to_px(), row_profile(), col_profile(), features(), measure_band().
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PHOTOS = HERE / ".cache" / "photos"
REF_W, REF_H = 800.0, 2000.0


# ----------------------------------------------------------------------------------------------------------- loading

def resolve_photo(name):
    p = Path(name).expanduser()
    if p.exists():
        return p
    q = PHOTOS / name
    if q.exists():
        return q
    raise SystemExit(f"photo not found: {name}")


def load_photo(path):
    """-> (rgb float HxWx3, grey float HxW) of the photo."""
    rgb = np.asarray(Image.open(resolve_photo(path)).convert("RGB")).astype(float)
    grey = rgb @ np.array([0.299, 0.587, 0.114])
    return rgb, grey


# -------------------------------------------------------------------------------------------------------- leaf bounds

def _valley(prof, lo, hi):
    """Sub-pixel position (continuous coordinates) and depth of the darkest point of prof[lo:hi]."""
    lo, hi = max(1, lo), min(len(prof) - 1, hi)
    i = lo + int(np.argmin(prof[lo:hi]))
    a, b, c = prof[i - 1], prof[i], prof[i + 1]
    den = a - 2 * b + c
    off = 0.5 * (a - c) / den if den > 0 else 0.0
    return i + 0.5 + float(np.clip(off, -0.5, 0.5)), float(b)


def _runs(mask):
    out, start = [], None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(mask)))
    return out


def find_hinges(grey, x1, y0, y1):
    """Hinges = bright runs inside the dark gap on the hinge side (the chrome knuckles cover the gap).
    A hinge is 2.5-6 % of the leaf height long; the upper one is centred 4-16 % below the leaf top, the lower one
    in the last 20 % of the photo. -> [(top, bottom) px] (continuous), upper first; [] if not found."""
    H, W = grey.shape
    xi = int(np.floor(x1))
    lo, hi = int(max(0, y0 + 2)), int(min(H, y1))
    h = y1 - y0
    best = []
    for cols in ([xi - 1, xi], [xi, xi + 1], [xi + 1, xi + 2]):
        cols = [c for c in cols if 0 <= c < W]
        seg = grey[lo:hi, cols].max(axis=1)
        base = float(np.median(seg))
        top = float(np.percentile(seg, 99.5))
        if top - base < 25:
            continue
        thr = base + 0.4 * (top - base)
        runs = []
        for a, b in _runs(seg > thr):
            if runs and a + lo - runs[-1][1] <= 2:  # bridge 1-2 px interruptions (dark lines across the chrome)
                runs[-1] = (runs[-1][0], b + lo)
            else:
                runs.append((a + lo, b + lo))
        runs = [r for r in runs if 0.025 * h <= r[1] - r[0] <= 0.06 * h]
        up = [r for r in runs if y0 + 0.04 * h <= (r[0] + r[1]) / 2 <= y0 + 0.16 * h]
        dn = [r for r in runs if (r[0] + r[1]) / 2 >= y0 + 0.80 * h]
        if not up or not dn:
            continue
        ra = max(up, key=lambda r: r[1] - r[0])
        rb = max(dn, key=lambda r: r[1] - r[0])
        la, lb = ra[1] - ra[0], rb[1] - rb[0]
        if abs(la - lb) > max(3, 0.25 * max(la, lb)):
            continue
        if not best or la + lb > sum(b - a for a, b in best):
            best = [(float(ra[0]), float(ra[1])), (float(rb[0]), float(rb[1]))]
    return best


def find_leaf(grey, bounds=None, bottom=None):
    """Leaf bounds in the photo. -> dict(x0, y0, x1, y1, W, H, hinges, notes, ...), continuous pixel coordinates."""
    H, W = grey.shape
    notes = []
    if bounds:
        x0, y0, x1, y1 = bounds
        notes.append("bounds given")
    else:
        rows = grey[int(H * 0.2):int(H * 0.8)]
        col = np.median(rows, axis=0)
        x0, _ = _valley(col, 2, int(W * 0.15))
        x1, _ = _valley(col, int(W * 0.85), W - 1)
        c0, c1 = int(x0 + (x1 - x0) * 0.3), int(x0 + (x1 - x0) * 0.7)
        row = np.median(grey[:, c0:c1], axis=1)
        y0, _ = _valley(row, 1, int(H * 0.08))
        y1 = float(H)
    hinges = find_hinges(grey, x1, y0, y1)
    y1_sym = None
    if len(hinges) == 2:
        c_top = sum(hinges[0]) / 2
        c_bot = sum(hinges[1]) / 2
        y1_sym = c_top + c_bot - y0
    if bottom is not None:
        y1 = float(bottom)
        notes.append("bottom given")
    elif not bounds and y1_sym is not None:
        tol = max(1.5, 0.003 * (y1 - y0))
        if y1_sym > y1 + tol:
            notes.append(f"photo cropped above the floor: leaf bottom from the hinges at {y1_sym:.1f}px "
                         f"(photo bottom {y1:.0f}px)")
            y1 = y1_sym
        elif y1_sym < y1 - tol:
            notes.append(f"hinges are not symmetric about the photo height: they put the leaf bottom at "
                         f"{y1_sym:.1f}px, the photo bottom is {y1:.0f}px (kept)")
    elif not bounds:
        notes.append("hinges not found: leaf bottom = photo bottom (unchecked)")
    w, h = x1 - x0, y1 - y0
    return dict(x0=x0, y0=y0, x1=x1, y1=y1, W=W, H=H, w=w, h=h, aspect=w / h, sx=w / REF_W, sy=h / REF_H,
                hinges=hinges, y1_hinges=y1_sym, notes=notes)


def _vmedian(a, win):
    """Running median of every column of a 2D array along the rows (window win, edges clamped)."""
    h = win // 2
    pad = np.pad(a, ((h, h), (0, 0)), mode="edge")
    stack = np.lib.stride_tricks.sliding_window_view(pad, win, axis=0)
    return np.median(stack, axis=-1)


def _components(mask):
    """4-connected components of a boolean 2D mask -> list of (count, (r0, c0, r1, c1), pixel list)."""
    seen = np.zeros_like(mask, bool)
    out = []
    H, W = mask.shape
    for r in range(H):
        for c in range(W):
            if not mask[r, c] or seen[r, c]:
                continue
            stack, pix = [(r, c)], []
            seen[r, c] = True
            while stack:
                y, x = stack.pop()
                pix.append((y, x))
                for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
            ys = [q[0] for q in pix]
            xs = [q[1] for q in pix]
            out.append((len(pix), (min(ys), min(xs), max(ys) + 1, max(xs) + 1), pix))
    return sorted(out, key=lambda t: -t[0])


def find_handle(grey, leaf, area=(0.0, 330.0, 700.0, 1300.0)):
    """The lever handle on its square rosette, near the lock edge. The wood around it has a vertical grain, so a
    tall vertical running median of every column is the background; the handle is what differs from it.
    -> dict(x, y (rosette centre, leaf mm), box (rosette px box r0, c0, r1, c1), lever (px box)) or None."""
    xa, xb, ya, yb = area
    c0, c1 = int(mm_to_px(leaf, x=xa)), int(np.ceil(mm_to_px(leaf, x=xb)))
    r0, r1 = int(mm_to_px(leaf, y=yb)), int(np.ceil(mm_to_px(leaf, y=ya)))
    c0 = max(c0, int(np.ceil(leaf["x0"])) + 1)
    sub = grey[r0:r1, c0:c1]
    win = max(9, int(round(0.03 * leaf["h"])) | 1)       # ~60 mm: taller than the rosette
    diff = np.abs(sub - _vmedian(sub, win))
    noise = float(np.median(diff)) + 1.0
    mask = diff > max(18.0, 5.0 * noise)
    comps = _components(mask)
    if not comps or comps[0][0] < 12:
        return None
    count, (b0, a0, b1, a1), pix = comps[0]
    # rows of the blob = the rosette's rows (the lever lies inside them). The rosette's columns: count the mask per
    # column over the rows the lever does not cross (the lever reaches far right of the rosette), with a low
    # threshold so that the dim bevel of the plate counts too.
    side = b1 - b0
    far = a0 + 1.5 * side * leaf["sx"] / leaf["sy"]
    lever_rows = {y for y, x in pix if x > far}
    cols = np.zeros(a1 - a0)
    for y, x in pix:
        if y not in lever_rows:
            cols[x - a0] += 1
    if cols.max() == 0:
        cols = np.bincount([x - a0 for _, x in pix], minlength=a1 - a0).astype(float)
    tall = np.where(cols >= 0.3 * cols.max())[0]
    ra0, ra1 = a0 + tall.min(), a0 + tall.max() + 1
    rb0, rb1 = b0, b1
    cx = c0 + (ra0 + ra1) / 2.0
    cy = r0 + (rb0 + rb1) / 2.0
    return dict(x=float(px_to_mm(leaf, x=cx)), y=float(px_to_mm(leaf, y=cy)),
                box=tuple(int(v) for v in (r0 + rb0, c0 + ra0, r0 + rb1, c0 + ra1)),
                lever=tuple(int(v) for v in (r0 + b0, c0 + a0, r0 + b1, c0 + a1)),
                size_mm=(float((ra1 - ra0) / leaf["sx"]), float((rb1 - rb0) / leaf["sy"])))


def px_to_mm(leaf, x=None, y=None):
    if x is not None:
        return (x - leaf["x0"]) / leaf["w"] * REF_W
    return (leaf["y1"] - y) / leaf["h"] * REF_H


def mm_to_px(leaf, x=None, y=None):
    if x is not None:
        return leaf["x0"] + x / REF_W * leaf["w"]
    return leaf["y1"] - y / REF_H * leaf["h"]


# ------------------------------------------------------------------------------------------------------------- colour

FLAT_AREAS = ((20, 105, 250, 850), (20, 105, 1150, 1750), (700, 780, 300, 1700))  # x0, x1, y0, y1 mm: the stiles


def finish_colour(rgb, leaf, areas=FLAT_AREAS):
    """Mean colour of flat finish areas (the stiles, clear of the handle, hinges and edges); pixels further than 2.5
    sigma from the median (grain streaks, joints, highlights) are left out. -> ((r, g, b) floats, pixel count)."""
    px = []
    for x0, x1, y0, y1 in areas:
        c0, c1 = int(np.ceil(mm_to_px(leaf, x=x0))), int(np.floor(mm_to_px(leaf, x=x1)))
        r0, r1 = int(np.ceil(mm_to_px(leaf, y=y1))), int(np.floor(mm_to_px(leaf, y=y0)))
        if c1 > c0 and r1 > r0:
            px.append(rgb[r0:r1, c0:c1].reshape(-1, 3))
    px = np.concatenate(px)
    grey = px.mean(axis=1)
    med, sd = np.median(grey), grey.std() or 1.0
    keep = np.abs(grey - med) <= 2.5 * sd
    return tuple(float(v) for v in px[keep].mean(axis=0)), int(keep.sum())


def hex_colour(c):
    return "#" + "".join(f"{int(round(min(255, max(0, v)))):02x}" for v in c)


# ----------------------------------------------------------------------------------------------------------- profiles

def row_profile(img, leaf, xa, xb):
    """Median over the columns of the x band [xa, xb] mm, for every photo row. -> 1D array (length H)."""
    c0 = int(round(mm_to_px(leaf, x=xa)))
    c1 = max(c0 + 1, int(round(mm_to_px(leaf, x=xb))))
    return np.median(img[:, c0:c1], axis=1)


def col_profile(img, leaf, ya, yb):
    """Median over the rows of the y band [ya, yb] mm (ya < yb), for every photo column."""
    r0 = int(round(mm_to_px(leaf, y=yb)))
    r1 = max(r0 + 1, int(round(mm_to_px(leaf, y=ya))))
    return np.median(img[r0:r1], axis=0)


def _running_median(p, win):
    n = len(p)
    h = win // 2
    pad = np.pad(p, h, mode="edge")
    return np.array([np.median(pad[i:i + win]) for i in range(n)])


def features(prof, lo, hi, white=None, min_contrast=5.0):
    """Line and step features of a profile inside [lo, hi) (pixel indices).

    white: optional 1D "whiteness" of the same profile (0..1: bright and unsaturated) used to tag glass.
    -> list of dict(kind, pos (continuous px), width (px), str, glass)."""
    lo, hi = max(2, int(lo)), min(len(prof) - 2, int(hi))
    p = np.asarray(prof, float)
    base = _running_median(p, 11)
    r = p - base
    seg = r[lo:hi]
    mad = float(np.median(np.abs(seg - np.median(seg)))) or 1.0
    thr = max(min_contrast, 4.0 * 1.4826 * mad)
    out = []
    i = lo
    while i < hi:
        if abs(r[i]) < thr:
            i += 1
            continue
        sgn = 1 if r[i] > 0 else -1
        j = i
        while j < hi and sgn * r[j] > thr * 0.5:
            j += 1
        # extend back to the half-threshold start
        s = i
        while s > lo and sgn * r[s - 1] > thr * 0.5:
            s -= 1
        k = s + int(np.argmax(sgn * r[s:j]))
        peak = sgn * r[k]
        # position: centroid of the part above half the peak
        idx = np.arange(s, j)
        wts = np.clip(sgn * r[s:j] - peak * 0.5, 0, None)
        pos = float((idx * wts).sum() / wts.sum()) + 0.5 if wts.sum() > 0 else k + 0.5
        # width at half maximum, sub-pixel
        half = peak * 0.5
        a = k
        while a > lo and sgn * r[a - 1] > half:
            a -= 1
        b = k
        while b < hi - 1 and sgn * r[b + 1] > half:
            b += 1
        left = a - 1 + (half - sgn * r[a - 1]) / (sgn * r[a] - sgn * r[a - 1]) if a > lo else a
        right = b + (sgn * r[b] - half) / (sgn * r[b] - sgn * r[b + 1]) if b < hi - 1 else b + 1
        width = float(right - left)
        f = dict(kind="bright" if sgn > 0 else "dark", pos=pos, width=width, str=float(sgn * peak),
                 edges=(float(left) + 0.5, float(right) + 0.5))
        if sgn > 0 and white is not None:
            f["glass"] = bool(white[k] > 0.55 and width >= 1.5)
        out.append(f)
        i = max(j, i + 1)
    # steps: strong gradients that are not the flank of a reported line
    d = np.diff(p)
    dmad = float(np.median(np.abs(d[lo:hi] - np.median(d[lo:hi])))) or 1.0
    dthr = max(min_contrast * 1.5, 5.0 * 1.4826 * dmad)
    for i in range(lo, hi - 1):
        if abs(d[i]) < dthr or abs(d[i]) < abs(d[i - 1]) or abs(d[i]) < abs(d[i + 1]):
            continue
        pos = i + 1.0  # boundary between pixel i and i+1
        if any(abs(pos - f["pos"]) <= f["width"] / 2 + 2 for f in out):
            continue
        # flat on both sides?
        a0, a1 = p[max(lo, i - 5):i - 1], p[i + 2:min(hi, i + 7)]
        if len(a0) < 2 or len(a1) < 2:
            continue
        if abs(a1.mean() - a0.mean()) < dthr:
            continue
        out.append(dict(kind="step", pos=pos, width=0.0, str=float(a1.mean() - a0.mean())))
    out.sort(key=lambda f: f["pos"])
    return out


def glass_runs(grey, white, leaf, axis, a, b, lo, hi):
    """Glass across a band: rows (axis 'y') or columns ('x') whose pixels are white (whiteness > 0.5) and without
    grain (the spread across the band well below that of the wood). Edges at the half-level crossings between the
    glass and the wood next to it. -> features dict(kind='glass', pos, width, str, edges, glass=True)."""
    if axis == "y":
        c0, c1 = int(round(mm_to_px(leaf, x=a))), int(round(mm_to_px(leaf, x=b)))
        g, w = grey[:, c0:c1], white[:, c0:c1]
        spread, wprof, prof = g.std(axis=1), np.median(w, axis=1), np.median(g, axis=1)
    else:
        r0, r1 = int(round(mm_to_px(leaf, y=b))), int(round(mm_to_px(leaf, y=a)))
        g, w = grey[r0:r1], white[r0:r1]
        spread, wprof, prof = g.std(axis=0), np.median(w, axis=0), np.median(g, axis=0)
    lo, hi = int(np.ceil(lo)), int(hi)
    wood_spread = float(np.median(spread[lo:hi])) or 1.0
    noise = float(np.median(np.abs(np.diff(prof[lo:hi])))) + 1.0
    mask = np.zeros(len(prof), bool)
    mask[lo:hi] = (wprof[lo:hi] > 0.5) & (spread[lo:hi] < max(3.0, 0.6 * wood_spread))
    out = []
    for s0, s1 in _runs(mask):
        if s1 - s0 < 2:
            continue
        inside = float(np.median(prof[s0:s1]))
        left = float(np.median(prof[max(0, s0 - 6):max(1, s0 - 2)]))
        right = float(np.median(prof[min(len(prof) - 1, s1 + 2):min(len(prof), s1 + 6)]))
        edges = []
        for j, outside, step in ((s0, left, -1), (s1 - 1, right, 1)):
            half = (inside + outside) / 2
            k = j
            while 0 < k + step < len(prof) - 1 and prof[k + step] > half and abs(k - j) < 6:
                k += step
            v1, v2 = prof[k], prof[k + step]
            t = (v1 - half) / (v1 - v2) if v1 != v2 else 0.5
            edges.append(k + 0.5 + step * t)
        e0, e1 = sorted(edges)
        contrast = inside - max(left, right)
        if contrast < max(15.0, 3.0 * noise):   # white finishes: wood as white as the glass - not a glass run
            continue
        out.append(dict(kind="glass", pos=(e0 + e1) / 2, width=e1 - e0, str=inside - (left + right) / 2,
                        edges=(e0, e1), glass=True))
    return out


def whiteness(rgb):
    """0..1 per pixel: bright and unsaturated (satin glass is ~0.8-1, light finishes lower because of saturation)."""
    mx = rgb.max(axis=-1)
    mn = rgb.min(axis=-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    return np.clip((mn - 150) / 90.0, 0, 1) * np.clip(1 - sat * 4, 0, 1)


# -------------------------------------------------------------------------------------------------------------- bands

def measure_band(rgb, grey, leaf, axis, a, b, min_contrast=5.0):
    """axis 'y': horizontal features in the x band [a, b] mm; axis 'x': vertical features in the y band [a, b] mm.
    -> list of features with 'mm' (and 'mm_edges' for lines) added, in mm order."""
    white = whiteness(rgb)
    if axis == "y":
        prof = row_profile(grey, leaf, a, b)
        wprof = row_profile(white, leaf, a, b)
        lo, hi = leaf["y0"] + 1, leaf["y1"] - 1
        conv = lambda v: px_to_mm(leaf, y=v)
    else:
        prof = col_profile(grey, leaf, a, b)
        wprof = col_profile(white, leaf, a, b)
        lo, hi = leaf["x0"] + 1, leaf["x1"] - 1
        conv = lambda v: px_to_mm(leaf, x=v)
    feats = features(prof, lo, hi, wprof, min_contrast)
    runs = glass_runs(grey, white, leaf, axis, a, b, lo, hi)
    # a bright line inside a glass run is the run itself
    feats = [f for f in feats if not any(r["edges"][0] - 1 <= f["pos"] <= r["edges"][1] + 1 for r in runs)] + runs
    for f in feats:
        if axis == "y" and f["kind"] == "step":
            f["str"] = -f["str"]          # sign of the change along +mm (up)
        f["mm"] = conv(f["pos"])
        if "edges" in f:
            e = sorted(conv(v) for v in f["edges"])
            f["mm_edges"] = e
            f["mm_width"] = e[1] - e[0]
    feats.sort(key=lambda f: f["mm"])
    return feats


def parse_band(s):
    a, b = (float(v) for v in s.split(":"))
    return (min(a, b), max(a, b))


# ------------------------------------------------------------------------------------------------------------ overlay

def _font(size):
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def write_overlay(path, rgb, leaf, bands, scale=3):
    H, W = rgb.shape[:2]
    img = Image.fromarray(rgb.astype(np.uint8)).resize((W * scale, H * scale), Image.NEAREST)
    margin = 90
    canvas = Image.new("RGB", (W * scale + 2 * margin, H * scale), (255, 255, 255))
    canvas.paste(img, (margin, 0))
    d = ImageDraw.Draw(canvas)
    font = _font(11)
    X = lambda x: margin + x * scale
    Y = lambda y: y * scale
    d.rectangle([X(leaf["x0"]), Y(leaf["y0"]), X(leaf["x1"]), Y(leaf["y1"]) - 1], outline=(0, 200, 0))
    for a, b in leaf["hinges"]:
        d.line([X(leaf["x1"]) + 4, Y(a), X(leaf["x1"]) + 4, Y(b)], fill=(255, 0, 255), width=2)
    hd = leaf.get("handle")
    if hd:
        r0, c0, r1, c1 = hd["box"]
        d.rectangle([X(c0), Y(r0), X(c1), Y(r1)], outline=(255, 0, 255))
        cx, cy = X(mm_to_px(leaf, x=hd["x"])), Y(mm_to_px(leaf, y=hd["y"]))
        d.line([cx - 6, cy, cx + 6, cy], fill=(255, 0, 255))
        d.line([cx, cy - 6, cx, cy + 6], fill=(255, 0, 255))
    colours = {"dark": (255, 40, 40), "bright": (0, 220, 255), "step": (255, 220, 0), "glass": (0, 120, 255)}
    for axis, a, b, feats in bands:
        for f in feats:
            c = colours[f["kind"]]
            if f.get("glass"):
                c = (0, 120, 255)
            if axis == "y":
                y = Y(f["pos"])
                x_a, x_b = X(mm_to_px(leaf, x=a)), X(mm_to_px(leaf, x=b))
                d.line([x_a, y, x_b, y], fill=c, width=1)
                side = X(leaf["x1"]) + 8 if a > REF_W / 2 else 2
                d.text((side, y - 6), f"{f['mm']:.0f}", fill=c, font=font)
            else:
                x = X(f["pos"])
                y_a, y_b = Y(mm_to_px(leaf, y=b)), Y(mm_to_px(leaf, y=a))
                d.line([x, y_a, x, y_b], fill=c, width=1)
                d.text((x - 8, y_b + 2), f"{f['mm']:.0f}", fill=c, font=font)
    canvas.save(path)


# --------------------------------------------------------------------------------------------------------------- main

def fmt_feature(f):
    s = f"{f['mm']:8.1f} mm  {f['kind']:6s} str {f['str']:+6.0f}  px {f['pos']:7.1f}"
    if f["kind"] != "step":
        s += f"  width {f['mm_width']:5.1f} mm ({f['width']:.1f}px)  [{f['mm_edges'][0]:.1f} .. {f['mm_edges'][1]:.1f}]"
    if f.get("glass"):
        s += "  glass"
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("photo")
    ap.add_argument("--out", help="overlay PNG")
    ap.add_argument("--xband", action="append", help="A:B mm: band of columns for the horizontal features")
    ap.add_argument("--yband", action="append", help="A:B mm: band of rows for the vertical features")
    ap.add_argument("--bounds", help="X0,Y0,X1,Y1 leaf bounds in photo pixels (skip the detection)")
    ap.add_argument("--bottom", type=float, help="leaf bottom in photo pixels (photo cropped above the floor)")
    ap.add_argument("--min", type=float, default=5.0, help="minimum contrast in grey levels (default 5)")
    ap.add_argument("--json", help="write the leaf bounds and features as JSON")
    a = ap.parse_args(argv)

    rgb, grey = load_photo(a.photo)
    bounds = [float(v) for v in a.bounds.split(",")] if a.bounds else None
    leaf = find_leaf(grey, bounds, a.bottom)
    print(f"{resolve_photo(a.photo).name}: {leaf['W']}x{leaf['H']} px")
    print(f"leaf x {leaf['x0']:.1f} .. {leaf['x1']:.1f}  y {leaf['y0']:.1f} .. {leaf['y1']:.1f}   "
          f"{leaf['w']:.1f} x {leaf['h']:.1f} px   {leaf['sx']:.4f} x {leaf['sy']:.4f} px/mm   "
          f"aspect w/h {leaf['aspect']:.4f} (800x2000: 0.4000, x/y scale ratio {leaf['sx'] / leaf['sy']:.4f})")
    if leaf["hinges"]:
        hs = ", ".join(f"{px_to_mm(leaf, y=(a_ + b_) / 2):.0f} (len {(b_ - a_) / leaf['sy']:.0f})"
                       for a_, b_ in leaf["hinges"])
        print(f"hinges (centre mm above the leaf bottom): {hs}")
    col, npx = finish_colour(rgb, leaf)
    print(f"finish colour (mean of the stiles, {npx} px): {hex_colour(col)}")
    hd = find_handle(grey, leaf)
    if hd:
        print(f"handle: rosette centre x {hd['x']:.1f} mm from the lock edge, y {hd['y']:.1f} mm above the bottom "
              f"(rosette {hd['size_mm'][0]:.0f} x {hd['size_mm'][1]:.0f} mm)")
    leaf["handle"] = hd
    for n in leaf["notes"]:
        print("note:", n)

    xbands = [parse_band(s) for s in (a.xband or ["280:520"])]
    ybands = [parse_band(s) for s in (a.yband or ["300:1700"])]
    out = []
    for xa, xb in xbands:
        feats = measure_band(rgb, grey, leaf, "y", xa, xb, a.min)
        print(f"\nhorizontal features (y mm, from the bottom) in x band {xa:.0f}..{xb:.0f} mm:")
        for f in feats:
            print("  " + fmt_feature(f))
        out.append(("y", xa, xb, feats))
    for ya, yb in ybands:
        feats = measure_band(rgb, grey, leaf, "x", ya, yb, a.min)
        print(f"\nvertical features (x mm, from the lock edge) in y band {ya:.0f}..{yb:.0f} mm:")
        for f in feats:
            print("  " + fmt_feature(f))
        out.append(("x", ya, yb, feats))
    if a.out:
        write_overlay(a.out, rgb, leaf, out)
        print("\noverlay ->", a.out)
    if a.json:
        Path(a.json).write_text(json.dumps(dict(leaf=leaf, bands=[dict(axis=ax, band=[p, q], features=fs)
                                                                   for ax, p, q, fs in out]), indent=1))


if __name__ == "__main__":
    main()
