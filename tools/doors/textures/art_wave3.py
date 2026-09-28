#!/usr/bin/env python3
"""Door glass pictures, glass patterns and painted ornaments (decals) of wave 3 of the DveriMebel / el'PORTA / BRAVO
catalogue (2020): the art is drawn here as vectors (and noise fields for textured glass) and rendered at any size.

    python3 tools/doors/textures/art_wave3.py                    # every picture: textures + entries/art-wave3.json
    python3 tools/doors/textures/art_wave3.py status_15 bc       # only these (a material id or its tail)
    python3 tools/doors/textures/art_wave3.py --check            # + tools/doors/.cache/art_wave3.png (needs the photos)
    python3 tools/doors/textures/art_wave3.py --check --no-write --out x.png lotos   # check sheet of a few, no files
    python3 tools/doors/textures/art_wave3.py --merge            # + merge the entries into External/external.json

Needs numpy and Pillow only (and art_glass.py next to it: its vector renderer). Writes per picture (M = material id):

    Assets/House4696/External/Materials/M/M_albedo.png   sRGB RGBA; alpha = opacity (satin 0.90, painted lines 1,
                                                          empty decal 0)
    Assets/House4696/External/Materials/M/M_mask.png     R metallic, G occlusion 255, B 0, A smoothness
    tools/doors/textures/entries/art-wave3.json          the external.json entries (category "doorglass" / "doorart",
                                                          "transparent": true)

Three kinds of picture (`kind`):
  * fit   - a glass picture stretched over its pane's bounds (`box`, leaf mm of the 800 x 2000 leaf; the design's
            glass part has role "art:M", or a shared glass with "fit": true): metersPerTile [1, 1];
  * tile  - a glass pattern repeating in metres (`box` = one tile, [0, 0, w, h] mm): metersPerTile = its size;
  * decal - a painted ornament laid on a face and stretched over its shape's bounds (`box`): transparent (alpha 0)
            everywhere except the ornament.
Drawing: a picture function gets an `Art` whose coordinates are the leaf millimetres of the catalogue render (origin
bottom-left of the leaf, x = 0 on the lock side, y up; for tiles the tile's own mm). It adds layers (a colour, an
opacity, metallic, smoothness) and draws into them: strokes with a width profile, fills, splines, spirals, leaves,
dots; `with a.mirror_x(cx)` draws everything mirrored as well; `with a.at(x, y, rot, s)` places a motif drawn in
local coordinates. A picture may also paint its base glass (a noise field for textured glass) through `base`.
Every picture names the catalogue photos it was drawn from; --check puts the photo crop next to the picture shown at
the photo's scale (composited over the glass / panel under it, inside the design's shape) and at 1:1-ish.
Picture families live in art_wave3_*.py next to this file (they register with the same decorator).
"""
import argparse
import contextlib
import fcntl
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import art_glass as AG  # noqa: E402  (wave 2: the supersampled vector renderer)

ROOT = HERE.parents[2]
EXT = ROOT / "Assets" / "House4696" / "External"
DESIGNS = ROOT / "Assets" / "House4696" / "Resources" / "Doors" / "Designs"
CACHE = ROOT / "tools" / "doors" / ".cache"
PHOTOS = CACHE / "photos"
ENTRIES = HERE / "entries" / "art-wave3.json"
MANIFEST = EXT / "external.json"
LOCK = ROOT / ".cache" / "external.json.lock"          # the lock of merge_entries.py
SOURCE = "procedural:tools/doors/textures/art_wave3.py"
FAMILIES = ("art_wave3_skinny", "art_wave3_laminated", "art_wave3_fineline")

# ------------------------------------------------------------------------------------------------ base materials
# sRGB colour, opacity, metallic, smoothness. SATIN = the app's M_DoorGlassSatin (Magic Fog).
SATIN = dict(color="#f2ece3", alpha=0.90, metallic=0.0, smooth=0.40)
BRONZE = dict(color="#be9682", alpha=0.90, metallic=0.0, smooth=0.40)     # bronze satin (WOOD CLASSIC renders)
NONE = dict(color="#8c8783", alpha=0.0, metallic=0.0, smooth=0.45)        # empty decal
PAINT_GREY = "#8b8782"                                                    # wave 2's line paint on satin


def hex_rgb(h):
    return AG.hex_rgb(h)


# ------------------------------------------------------------------------------------------------ SVG paths
_TOK = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _bez3(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n + 1)[1:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def _bez2(p0, p1, p2, n):
    t = np.linspace(0, 1, n + 1)[1:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def _nseg(*pts, step=1.5):
    L = sum(float(np.hypot(*(b - a))) for a, b in zip(pts[:-1], pts[1:]))
    return int(np.clip(L / step, 4, 400))


def _arc(p0, rx, ry, phi, large, sweep, p1, step=1.5):
    """SVG elliptical arc (endpoint parametrisation) -> points after p0."""
    if rx == 0 or ry == 0 or np.allclose(p0, p1):
        return np.array([p1])
    rx, ry = abs(rx), abs(ry)
    c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (p0 - p1) / 2
    x1, y1 = c * dx + s * dy, -s * dx + c * dy
    lam = x1 * x1 / (rx * rx) + y1 * y1 / (ry * ry)
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    k = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1)
    cx1, cy1 = k * rx * y1 / ry, -k * ry * x1 / rx
    cx = c * cx1 - s * cy1 + (p0[0] + p1[0]) / 2
    cy = s * cx1 + c * cy1 + (p0[1] + p1[1]) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    t1 = ang(1, 0, (x1 - cx1) / rx, (y1 - cy1) / ry)
    dt = ang((x1 - cx1) / rx, (y1 - cy1) / ry, (-x1 - cx1) / rx, (-y1 - cy1) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    n = int(np.clip(abs(dt) * max(rx, ry) / step, 4, 720))
    t = t1 + dt * np.linspace(0, 1, n + 1)[1:]
    X = cx + c * rx * np.cos(t) - s * ry * np.sin(t)
    Y = cy + s * rx * np.cos(t) + c * ry * np.sin(t)
    out = np.stack([X, Y], 1)
    out[-1] = p1
    return out


def parse_path(d, step=1.5):
    """SVG path data (absolute and relative M L H V C S Q T A Z) -> [(points Nx2, closed), ...] with curves
    flattened to ~step mm."""
    toks = _TOK.findall(d)
    i, cmd = 0, None
    subs, cur = [], []
    pos = np.zeros(2)
    start = np.zeros(2)
    last_c = None     # last control point (for S / T)
    last_cmd = ""

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    def flush(closed):
        nonlocal cur
        if len(cur) > 1:
            subs.append((np.array(cur, np.float64), closed))
        cur = []

    while i < len(toks):
        t = toks[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t
            i += 1
            if cmd in "Zz":
                if cur:
                    flush(True)
                pos = start.copy()
                last_cmd = cmd
                continue
        rel = cmd.islower()
        C = cmd.upper()
        base = pos if rel else np.zeros(2)
        if C == "M":
            flush(False)
            pos = base + np.array([num(), num()])
            start = pos.copy()
            cur = [pos.copy()]
            cmd = "l" if rel else "L"
            last_c = None
        elif C == "L":
            pos = base + np.array([num(), num()])
            cur.append(pos.copy())
            last_c = None
        elif C == "H":
            pos = np.array([(pos[0] if rel else 0) + num(), pos[1]])
            cur.append(pos.copy())
            last_c = None
        elif C == "V":
            pos = np.array([pos[0], (pos[1] if rel else 0) + num()])
            cur.append(pos.copy())
            last_c = None
        elif C in "CS":
            if C == "C":
                p1 = base + np.array([num(), num()])
            else:
                p1 = 2 * pos - last_c if last_c is not None and last_cmd.upper() in "CS" else pos.copy()
            p2 = base + np.array([num(), num()])
            p3 = base + np.array([num(), num()])
            if not cur:
                cur = [pos.copy()]
            cur.extend(_bez3(pos, p1, p2, p3, _nseg(pos, p1, p2, p3, step=step)))
            last_c, pos = p2, p3
        elif C in "QT":
            if C == "Q":
                p1 = base + np.array([num(), num()])
            else:
                p1 = 2 * pos - last_c if last_c is not None and last_cmd.upper() in "QT" else pos.copy()
            p2 = base + np.array([num(), num()])
            if not cur:
                cur = [pos.copy()]
            cur.extend(_bez2(pos, p1, p2, _nseg(pos, p1, p2, step=step)))
            last_c, pos = p1, p2
        elif C == "A":
            rx, ry, phi, large, sweep = num(), num(), num(), num(), num()
            p1 = base + np.array([num(), num()])
            if not cur:
                cur = [pos.copy()]
            cur.extend(_arc(pos, rx, ry, phi, int(large), int(sweep), p1, step))
            pos = p1
            last_c = None
        else:
            raise ValueError(f"path command {cmd}")
        last_cmd = cmd
    flush(False)
    return subs


# ------------------------------------------------------------------------------------------------ design shapes
def shape_rings(shape):
    """A design part's shape ({"rect"}, {"ellipse"}, {"path"}) -> list of closed rings (leaf mm)."""
    if "rect" in shape:
        x0, y0, x1, y1 = shape["rect"]
        return [np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], np.float64)]
    if "ellipse" in shape:
        cx, cy, rx, ry = shape["ellipse"]
        t = np.linspace(0, 2 * np.pi, 361)[:-1]
        return [np.stack([cx + rx * np.cos(t), cy + ry * np.sin(t)], 1)]
    if "path" in shape:
        return [p for p, _ in parse_path(shape["path"])]
    raise ValueError(f"shape {shape}")


def design_rings(design, ref=None):
    """Rings of the parts of a design that show material `ref` (role "art:ref" or decal image ref); ref None: the
    glass parts of the door's own glass (no role / role glass)."""
    d = json.loads((DESIGNS / f"{design}.json").read_text(encoding="utf-8"))
    rings = []
    for p in d.get("parts", []):
        if ref is None:
            ok = p["type"] == "glass" and p.get("role") in (None, "glass", "true")
        else:
            ok = p.get("role") == f"art:{ref}" or p.get("image") == ref
        if ok:
            rings += shape_rings(p["shape"])
    return rings


def rings_bounds(rings):
    a = np.vstack(rings)
    return (float(a[:, 0].min()), float(a[:, 1].min()), float(a[:, 0].max()), float(a[:, 1].max()))


# ------------------------------------------------------------------------------------------------ curve helpers
def spline(pts, n=None, closed=False, step=1.0):
    """Centripetal Catmull-Rom spline through the points -> dense points (Nx2 or Nx3 when the points carry a width:
    the width is interpolated too)."""
    P = np.asarray(pts, np.float64)
    if len(P) < 3:
        return _resample(P, step)
    if closed:
        P = np.vstack([P[-1], P, P[0], P[1]])
    else:
        P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = [P[1]]
    for k in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[k - 1], P[k], P[k + 1], P[k + 2]

        def tj(ti, a, b):
            return ti + max(np.hypot(*(b[:2] - a[:2])), 1e-6) ** 0.5
        t0 = 0.0
        t1 = tj(t0, p0, p1)
        t2 = tj(t1, p1, p2)
        t3 = tj(t2, p2, p3)
        m = n or max(3, int(np.hypot(*(p2[:2] - p1[:2])) / step))
        t = np.linspace(t1, t2, m + 1)[1:, None]
        A1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
        A2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
        A3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
        B1 = (t2 - t) / (t2 - t0) * A1 + (t - t0) / (t2 - t0) * A2
        B2 = (t3 - t) / (t3 - t1) * A2 + (t - t1) / (t3 - t1) * A3
        out.extend((t2 - t) / (t2 - t1) * B1 + (t - t1) / (t2 - t1) * B2)
    return np.array(out)


def _resample(P, step):
    P = np.asarray(P, np.float64)
    if len(P) < 2:
        return P
    seg = np.hypot(*(P[1:, :2] - P[:-1, :2]).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    if s[-1] <= 0:
        return P
    n = max(2, int(s[-1] / step) + 1)
    u = np.linspace(0, s[-1], n)
    return np.stack([np.interp(u, s, P[:, j]) for j in range(P.shape[1])], 1)


def arclen(P):
    seg = np.hypot(*(P[1:, :2] - P[:-1, :2]).T)
    return np.concatenate([[0], np.cumsum(seg)])


def spiral(cx, cy, r0, r1, a0, a1, step=1.0):
    """Spiral from angle a0 (deg, radius r0) to a1 (radius r1), radius varying linearly with the angle."""
    n = max(8, int(abs(math.radians(a1 - a0)) * max(r0, r1) / step))
    a = np.radians(np.linspace(a0, a1, n))
    r = np.linspace(r0, r1, n)
    return np.stack([cx + r * np.cos(a), cy + r * np.sin(a)], 1)


def widths(P, w, taper=None, profile=None):
    """Widths along a polyline: w scalar or (w0, w1); taper (a, b) = lengths (mm) over which the stroke thins to a
    point at the start / end (sine ease); profile: f(u 0..1) multiplier."""
    s = arclen(P)
    L = max(s[-1], 1e-6)
    u = s / L
    if isinstance(w, (tuple, list)):
        W = np.interp(u, np.linspace(0, 1, len(w)), w)
    else:
        W = np.full(len(P), float(w))
    if taper:
        a, b = taper
        if a:
            W *= np.sin(np.clip(s / a, 0, 1) * np.pi / 2) ** 0.8 * 0.85 + 0.15 * (s / a >= 0)
        if b:
            W *= np.sin(np.clip((L - s) / b, 0, 1) * np.pi / 2) ** 0.8 * 0.85 + 0.15 * ((L - s) / b >= 0)
    if profile is not None:
        W *= profile(u)
    return W


# ------------------------------------------------------------------------------------------------ the drawing
def leaf_ring(base, tip, width, bend=0.0, shape=0.5):
    """Outline of a pointed leaf from base to tip (see Layer.leaf)."""
    b, t = np.asarray(base, np.float64), np.asarray(tip, np.float64)
    d = t - b
    L = float(np.hypot(*d))
    if L < 1e-6:
        return None
    u = d / L
    nrm = np.array([-u[1], u[0]])
    s = np.linspace(0, 1, 60)
    mid = b + np.outer(s, d) + np.outer(np.sin(np.pi * s) * bend * L, nrm)
    k = np.where(s < shape, np.sin(np.pi / 2 * s / max(shape, 1e-3)),
                 np.cos(np.pi / 2 * (s - shape) / max(1 - shape, 1e-3)))
    hw = width / 2 * np.clip(k, 0, 1) ** 0.9
    return np.vstack([mid + nrm * hw[:, None], (mid - nrm * hw[:, None])[::-1]])


class Layer:
    def __init__(self, art, props):
        self.art = art
        self.props = props
        self.items = []

    # every public drawing call goes through _add (transforms + symmetry)
    def _add(self, kind, rings_or_pts):
        for tf in self.art._copies():
            if kind == "stroke":
                P = rings_or_pts.copy()
                P[:, :2] = tf(P[:, :2])
                P[:, 2] *= self.art._scale()
                self.items.append({"stroke": P})
            else:
                self.items.append({"poly": [tf(np.asarray(r, np.float64)) for r in rings_or_pts]})

    def stroke(self, pts, w=2.0, taper=None, profile=None, step=0.8):
        """Polyline stroked with round joins: points Nx2 (width w: scalar or (w0, ..., wn) along it) or Nx3 (own
        widths); taper (a, b) mm thins it to a point at the start / end; profile f(u) multiplies the width."""
        P = _resample(np.asarray(pts, np.float64), step)
        if P.shape[1] == 3:
            P[:, 2] *= widths(P[:, :2], 1.0, taper, profile)
        else:
            P = np.column_stack([P, widths(P, w, taper, profile)])
        self._add("stroke", P)
        return P

    def curve(self, pts, w=2.0, taper=None, profile=None, closed=False):
        """Smooth curve (Catmull-Rom) through the points."""
        P = spline(pts, closed=closed)
        if closed:
            P = np.vstack([P, P[:1]])
        return self.stroke(P, w, taper, profile)

    def path(self, d, w=2.0, taper=None, profile=None):
        """SVG path data stroked (each subpath)."""
        out = []
        for P, closed in parse_path(d):
            if closed:
                P = np.vstack([P, P[:1]])
            out.append(self.stroke(P, w, taper, profile))
        return out

    def fill(self, shape):
        """Filled polygon: SVG path data (subpaths after the first are holes), a list of rings or one ring."""
        if isinstance(shape, str):
            rings = [p for p, _ in parse_path(shape)]
        else:
            first = np.asarray(shape[0], np.float64)
            rings = [np.asarray(r, np.float64) for r in shape] if first.ndim == 2 else [np.asarray(shape, np.float64)]
        self._add("poly", rings)

    def fill_curve(self, pts):
        """Closed smooth outline through the points, filled."""
        self._add("poly", [spline(pts, closed=True)])

    def spiral(self, cx, cy, r0, r1, a0, a1, w=2.0, taper=None, profile=None):
        return self.stroke(spiral(cx, cy, r0, r1, a0, a1), w, taper, profile)

    def dot(self, x, y, r):
        t = np.linspace(0, 2 * np.pi, max(12, int(r * 6)), endpoint=False)
        self._add("poly", [np.stack([x + r * np.cos(t), y + r * np.sin(t)], 1)])

    def ellipse(self, cx, cy, rx, ry, w=None, rot=0.0):
        t = np.linspace(0, 2 * np.pi, max(24, int((rx + ry) * 2)), endpoint=True)
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        X, Y = rx * np.cos(t), ry * np.sin(t)
        P = np.stack([cx + c * X - s * Y, cy + s * X + c * Y], 1)
        if w is None:
            self._add("poly", [P[:-1]])
        else:
            self.stroke(P, w)

    def diamond(self, x, y, w, h, rot=0.0):
        P = np.array([[0, -h / 2], [w / 2, 0], [0, h / 2], [-w / 2, 0]], np.float64)
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        P = P @ np.array([[c, s], [-s, c]])
        self._add("poly", [P + [x, y]])

    def rect(self, x0, y0, x1, y1, w=None):
        P = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], np.float64)
        if w is None:
            self._add("poly", [P])
        else:
            self.stroke(np.vstack([P, P[:1]]), w)

    def leaf(self, base, tip, width, bend=0.0, shape=0.5, vein=None):
        """A pointed leaf / petal from base to tip: width = its greatest width, bend = sideways bow of its midrib
        (fraction of the length, + = to the left of base->tip), shape = where along it is widest (0..1).
        vein: width of a midrib cut out of it (0 = none)."""
        b, t = np.asarray(base, np.float64), np.asarray(tip, np.float64)
        d = t - b
        L = float(np.hypot(*d))
        if L < 1e-6:
            return
        u = d / L
        nrm = np.array([-u[1], u[0]])
        s = np.linspace(0, 1, 60)
        mid = b + np.outer(s, d) + np.outer(np.sin(np.pi * s) * bend * L, nrm)
        # half width: rises to the max at `shape`, pointed at both ends
        k = np.where(s < shape, np.sin(np.pi / 2 * s / max(shape, 1e-3)),
                     np.cos(np.pi / 2 * (s - shape) / max(1 - shape, 1e-3)))
        hw = width / 2 * np.clip(k, 0, 1) ** 0.9
        left = mid + nrm * hw[:, None]
        right = mid - nrm * hw[:, None]
        ring = np.vstack([left, right[::-1]])
        if vein:
            self._add("poly", [ring])
        else:
            self._add("poly", [ring])

    def teardrop(self, base, tip, width, bend=0.0):
        """A drop: round at the base, pointed at the tip."""
        self.leaf(base, tip, width, bend, shape=0.25)

    def leaf_line(self, base, tip, width, w=2.0, bend=0.0, shape=0.5):
        """The outline of a leaf (see leaf) drawn as a line of width w."""
        ring = leaf_ring(base, tip, width, bend, shape)
        if ring is not None:
            self.stroke(np.vstack([ring, ring[:1]]), w)


class Art:
    """A picture's drawing: layers in leaf mm (or tile mm). box = (x0, y0, x1, y1)."""

    def __init__(self, box, wrap=False):
        self.box = tuple(float(v) for v in box)
        self.wrap = wrap
        self.layers = []
        self._tf = [np.eye(3)]
        self._sym = [[np.eye(3)]]
        self.base = None          # optional f(pic, X, Y) painting the base glass (X, Y: mm grids, rows top-down)

    @property
    def W(self):
        return self.box[2] - self.box[0]

    @property
    def H(self):
        return self.box[3] - self.box[1]

    def layer(self, color=PAINT_GREY, alpha=1.0, smooth=0.45, metallic=0.0, grad=None):
        """A layer of paint. grad: [(y mm, colour), ...] - the colour varies with the height (leaf mm)."""
        L = Layer(self, dict(color=color, alpha=alpha, smooth=smooth, metallic=metallic, grad=grad))
        self.layers.append(L)
        return L

    # -- transforms: the current local->leaf transform and the symmetry copies (in leaf coordinates)
    def _scale(self):
        m = self._tf[-1]
        return math.sqrt(abs(np.linalg.det(m[:2, :2])))

    def _copies(self):
        m = self._tf[-1]
        out = []
        for g in self._sym[-1]:
            M = g @ m
            out.append(lambda P, M=M: P @ M[:2, :2].T + M[:2, 2])
        return out

    @contextlib.contextmanager
    def at(self, x=0.0, y=0.0, rot=0.0, s=1.0, sx=None, sy=None):
        """Draw in local coordinates placed at (x, y), rotated rot deg, scaled."""
        c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        S = np.diag([sx if sx is not None else s, sy if sy is not None else s, 1.0])
        T = np.array([[c, -sn, x], [sn, c, y], [0, 0, 1]], np.float64) @ S
        self._tf.append(self._tf[-1] @ T)
        try:
            yield
        finally:
            self._tf.pop()

    @contextlib.contextmanager
    def mirror_x(self, cx):
        """Everything drawn inside is drawn mirrored about the vertical x = cx too (leaf coordinates)."""
        g = np.array([[-1, 0, 2 * cx], [0, 1, 0], [0, 0, 1]], np.float64)
        self._sym.append(self._sym[-1] + [g @ h for h in self._sym[-1]])
        try:
            yield
        finally:
            self._sym.pop()

    @contextlib.contextmanager
    def mirror_y(self, cy):
        g = np.array([[1, 0, 0], [0, -1, 2 * cy], [0, 0, 1]], np.float64)
        self._sym.append(self._sym[-1] + [g @ h for h in self._sym[-1]])
        try:
            yield
        finally:
            self._sym.pop()

    @contextlib.contextmanager
    def rotations(self, cx, cy, n):
        """n-fold rotational symmetry about (cx, cy)."""
        gs = []
        for k in range(n):
            a = 2 * math.pi * k / n
            c, s = math.cos(a), math.sin(a)
            gs.append(np.array([[c, -s, cx - c * cx + s * cy], [s, c, cy - s * cx - c * cy], [0, 0, 1]]))
        self._sym.append([g @ h for g in gs for h in self._sym[-1]])
        try:
            yield
        finally:
            self._sym.pop()


# ------------------------------------------------------------------------------------------------ rendering
class Spec:
    def __init__(self, mid, fn, kind, name, box, base, photos, shape, under, long, source, ppm, check_box,
                 check_design, normal=False):
        self.id, self.fn, self.kind, self.name = mid, fn, kind, name
        self.box = tuple(float(v) for v in box)
        self.base = base
        self.photos = list(photos)
        self.shape = shape                 # (design id, ref) or list of rings (leaf mm) or None
        self.under = under                 # preview colour under a decal / behind the glass
        self.long = long
        self.source = source
        self.ppm = ppm
        self.check_box = check_box         # tiles: leaf mm box of the photo to compare (shape = its glass)
        self.check_design = check_design
        self.normal = normal               # the picture sets a.height (mm): a normal map is written

    @property
    def size_mm(self):
        return self.box[2] - self.box[0], self.box[3] - self.box[1]

    def size_px(self):
        w, h = self.size_mm
        k = min(self.long / max(w, h), self.ppm or 1e9)
        nx, ny = max(4, int(round(w * k / 4)) * 4), max(4, int(round(h * k / 4)) * 4)
        return nx, ny

    def rings(self):
        if self.shape is None:
            return None
        if isinstance(self.shape, tuple) and isinstance(self.shape[0], str):
            return design_rings(*self.shape)
        return self.shape


REG = {}


def art(mid, kind, name, box, base=None, photos=(), shape=None, under=None, long=2048, source="", ppm=None,
        check_box=None, check_design=None, normal=False):
    """Registers a picture function f(a: Art) under material id `mid`."""
    def deco(fn):
        b = base if base is not None else (NONE if kind == "decal" else SATIN)
        REG[mid] = Spec(mid, fn, kind, name, box, b, photos, shape, under, long, source, ppm, check_box,
                        check_design, normal)
        return fn
    return deco


def render(spec, size_px=None):
    """-> AG.Picture of the spec at size_px (default its own size)."""
    size_px = size_px or spec.size_px()
    a = Art(spec.box, wrap=spec.kind == "tile")
    spec.fn(a)
    pic = AG.Picture(size_px, spec.base)
    nx, ny = size_px
    x0, y0, x1, y1 = spec.box
    pic.height = None
    if a.base is not None:
        # a.base(pic, X, Y): paints the base glass (pic.rgb / alpha / smooth ...) and may set pic.height (mm)
        X = x0 + (np.arange(nx) + 0.5) / nx * (x1 - x0)
        Y = y1 - (np.arange(ny) + 0.5) / ny * (y1 - y0)
        a.base(pic, *np.meshgrid(X, Y))
    off = np.array([x0, y0])
    for L in a.layers:
        if not L.items:
            continue
        items = []
        for it in L.items:
            if "stroke" in it:
                P = it["stroke"].copy()
                P[:, :2] -= off
                items.append({"stroke": P})
            else:
                items.append({"poly": [r - off for r in it["poly"]]})
        cov = AG.render_items(items, (x1 - x0, y1 - y0), size_px, wrap=a.wrap)
        props = dict(L.props)
        grad = props.pop("grad", None)
        color = None
        if grad:
            yy = y1 - (np.arange(ny) + 0.5) / ny * (y1 - y0)
            gy = [g[0] for g in grad]
            order = np.argsort(gy)
            cols = np.array([hex_rgb(grad[i][1]) for i in order])
            gy = np.array(gy)[order]
            col = np.stack([np.interp(yy, gy, cols[:, j]) for j in range(3)], 1)
            color = np.broadcast_to(col[:, None, :], (ny, nx, 3))
        pic.layer(cov, props, color)
    return pic


def bleed(rgb, alpha, iters=24):
    """Colour of (nearly) transparent pixels taken from the painted ones around them, so filtering never pulls a
    dark / white fringe into a decal's edges."""
    w = (alpha > 0.02).astype(np.float64)
    if w.all() or not w.any():
        return rgb
    acc = rgb * w[..., None]
    out = rgb.copy()
    known = w.copy()
    a, k = acc.copy(), w.copy()
    for _ in range(iters):
        a = (a + np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)) / 5
        k = (k + np.roll(k, 1, 0) + np.roll(k, -1, 0) + np.roll(k, 1, 1) + np.roll(k, -1, 1)) / 5
        # coarsen quickly: every few steps the blur widens by doubling the shift
    fill = a / np.maximum(k, 1e-6)[..., None]
    mean = acc.sum((0, 1)) / max(w.sum(), 1)
    fill = np.where((k > 1e-4)[..., None], fill, mean)
    out = np.where(known[..., None] > 0, rgb, fill)
    return out


def write(spec, pic):
    folder = EXT / "Materials" / spec.id
    folder.mkdir(parents=True, exist_ok=True)
    rgb = pic.rgb
    if spec.kind == "decal":
        rgb = bleed(rgb, pic.alpha)
    rgba = np.dstack([np.clip(rgb, 0, 1), np.clip(pic.alpha, 0, 1)])
    Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), "RGBA").save(folder / f"{spec.id}_albedo.png", optimize=True)
    nx, ny = pic.size
    k = max(1, int(math.ceil(max(nx, ny) / 512)))
    mw, mh = max(4, nx // k), max(4, ny // k)
    met = np.asarray(Image.fromarray((pic.metallic * 255).astype(np.uint8)).resize((mw, mh), Image.BOX))
    smo = np.asarray(Image.fromarray((pic.smooth * 255).astype(np.uint8)).resize((mw, mh), Image.BOX))
    mask = np.dstack([met, np.full_like(met, 255), np.zeros_like(met), smo])
    Image.fromarray(mask.astype(np.uint8), "RGBA").save(folder / f"{spec.id}_mask.png", optimize=True)
    if getattr(pic, "height", None) is not None:
        normal_map(pic.height, spec).save(folder / f"{spec.id}_normal.png", optimize=True)


def normal_map(h, spec, max_side=1024):
    """Tangent-space normal map (OpenGL: +Y green = up the picture) of a height field in mm at the picture's
    resolution; tiles wrap."""
    ny, nx = h.shape
    w, hh = spec.size_mm
    kx, ky = nx / w, ny / hh                        # px per mm
    if spec.kind == "tile":
        dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) / 2 * kx
        dy = (np.roll(h, 1, 0) - np.roll(h, -1, 0)) / 2 * ky     # rows go down, +y goes up
    else:
        dy_rows, dx = np.gradient(h)
        dx, dy = dx * kx, -dy_rows * ky
    n = np.dstack([-dx, -dy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    im = Image.fromarray(((n * 0.5 + 0.5) * 255 + 0.5).astype(np.uint8), "RGB")
    k = max(1, int(math.ceil(max(nx, ny) / max_side)))
    if k > 1:
        im = im.resize((nx // k, ny // k), Image.BOX)
    return im


def entry(spec):
    w, h = spec.size_mm
    mpt = [round(w / 1000, 4), round(h / 1000, 4)] if spec.kind == "tile" else [1.0, 1.0]
    return {
        "id": spec.id, "name": spec.name, "category": "doorart" if spec.kind == "decal" else "doorglass",
        "source": SOURCE, "neutral": False, "transparent": True, "metersPerTile": mpt, "maxSize": 2048,
        "folder": f"Materials/{spec.id}",
        "textures": {"albedo": f"{spec.id}_albedo.png", "mask": f"{spec.id}_mask.png"},
    } | ({"textures": {"albedo": f"{spec.id}_albedo.png", "normal": f"{spec.id}_normal.png",
                       "mask": f"{spec.id}_mask.png"}} if spec.normal else {})


def write_entries(specs):
    """Updates this generator's entries file (locked: several runs may write it at once)."""
    ENTRIES.parent.mkdir(parents=True, exist_ok=True)
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(ROOT / ".cache" / "art-wave3-entries.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        _write_entries(specs)


def _write_entries(specs):
    old = json.loads(ENTRIES.read_text(encoding="utf-8")) if ENTRIES.exists() else []
    by = {e["id"]: e for e in old}
    for s in specs:
        by[s.id] = entry(s)
    order = [s for s in REG]
    out = [by[i] for i in order if i in by] + [e for i, e in by.items() if i not in REG]
    ENTRIES.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


def merge(path=ENTRIES):
    """merge_entries.py's merge (same lock, same rules) that also takes the "doorart_*" decals: that tool only
    accepts door_* / doorglass_* ids."""
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = json.loads(MANIFEST.read_text())
        mats = manifest["materials"]
        index = {m["id"]: i for i, m in enumerate(mats)}
        added = replaced = 0
        for e in json.loads(Path(path).read_text()):
            if not e["id"].startswith(("doorglass_", "doorart_")):
                raise SystemExit(f"{path}: {e['id']} is not a door glass / art material")
            if e["id"] in index:
                mats[index[e["id"]]] = e
                replaced += 1
            else:
                index[e["id"]] = len(mats)
                mats.append(e)
                added += 1
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
        print(f"external.json: {added} added, {replaced} replaced")


# ------------------------------------------------------------------------------------------------ check sheet
def _font(size):
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _measure():
    sys.path.insert(0, str(HERE.parent))
    import measure
    return measure


def photo_crop(photo, box, size):
    """The leaf-mm box of a catalogue photo resampled to size (bicubic) + the photo's px/mm (sx, sy). photo: a file
    name, or (file name, (x0, y0, x1, y1)) = the leaf's bounds in the photo's pixels when measure.find_leaf misses
    them (casings, cornices)."""
    M = _measure()
    bounds = None
    if isinstance(photo, (tuple, list)):
        photo, bounds = photo
    rgb, grey = M.load_photo(photo)
    try:
        if bounds:
            bx0, by0, bx1, by1 = (float(v) for v in bounds)
            leaf = dict(x0=bx0, y0=by0, x1=bx1, y1=by1, w=bx1 - bx0, h=by1 - by0)
        else:
            leaf = M.find_leaf(grey)
    except Exception:
        H, W = grey.shape
        leaf = dict(x0=0.0, y0=0.0, x1=float(W), y1=float(H), w=float(W), h=float(H))
    x0, x1 = M.mm_to_px(leaf, x=box[0]), M.mm_to_px(leaf, x=box[2])
    ya, yb = M.mm_to_px(leaf, y=box[3]), M.mm_to_px(leaf, y=box[1])
    im = Image.open(M.resolve_photo(photo)).convert("RGB")
    crop = im.transform(size, Image.EXTENT, (x0, ya, x1, yb), Image.BICUBIC)
    return crop, (leaf["w"] / 800.0, leaf["h"] / 2000.0)


def rings_mask(rings, box, size):
    """Coverage 0..1 of the rings (even-odd union of the rings drawn filled) at size over box."""
    nx, ny = size
    x0, y0, x1, y1 = box
    ss = 3
    im = Image.new("L", (nx * ss, ny * ss), 0)
    d = ImageDraw.Draw(im)
    for r in rings:
        pts = [((x - x0) / (x1 - x0) * nx * ss, (y1 - y) / (y1 - y0) * ny * ss) for x, y in r]
        d.polygon(pts, fill=255)
    return np.asarray(im.resize(size, Image.BOX), np.float64) / 255.0


def tile_sample(pic, box_tile, box_leaf, size):
    """A tile picture as it lies in metres over a leaf-mm box (UV = mm / 1000 modulo the tile) at size."""
    nx, ny = size
    tw, th = box_tile[2] - box_tile[0], box_tile[3] - box_tile[1]
    X = box_leaf[0] + (np.arange(nx) + 0.5) / nx * (box_leaf[2] - box_leaf[0])
    Y = box_leaf[3] - (np.arange(ny) + 0.5) / ny * (box_leaf[3] - box_leaf[1])
    pw, ph = pic.size
    ix = (np.mod(X, tw) / tw * pw).astype(int) % pw
    iy = ((1 - np.mod(Y, th) / th) * ph).astype(int) % ph
    rgb = pic.rgb[iy][:, ix]
    al = pic.alpha[iy][:, ix]
    return rgb, al


BEHIND = "#9a9a9a"                    # what the check sheet shows behind transparent glass
UNDER = {"behind": hex_rgb(BEHIND),
         "satin": hex_rgb(SATIN["color"]) * SATIN["alpha"] + hex_rgb(BEHIND) * (1 - SATIN["alpha"]),
         "bronze": hex_rgb(BRONZE["color"]) * BRONZE["alpha"] + hex_rgb(BEHIND) * (1 - BRONZE["alpha"])}


def composite(spec, pic, size, box, under=None):
    """Display colour (0..1 sRGB) of the picture over `under` (default spec.under) at size over the leaf box."""
    if spec.kind == "tile":
        # supersample the tile over the box, then box-filter
        ss = 3
        rgb, al = tile_sample(pic, spec.box, box, (size[0] * ss, size[1] * ss))
        img = rgb * al[..., None] + hex_rgb(BEHIND) * (1 - al[..., None])
        im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize(size, Image.BOX)
        return np.asarray(im, np.float64) / 255.0
    rgb, al = pic.rgb, pic.alpha
    u = under or spec.under
    if isinstance(u, (list, tuple)):
        u = u[0]
    under = UNDER.get(u or ("satin" if spec.kind == "decal" else "behind"))
    if under is None:
        under = hex_rgb(u)
    img = rgb * al[..., None] + under * (1 - al[..., None])
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.resize(size, Image.LANCZOS), np.float64) / 255.0


def check_cell(spec, pic, height=560):
    """[photo crop | picture at the photo's scale | picture at the display scale] for each photo of the spec."""
    box = spec.check_box or spec.box
    bw, bh = box[2] - box[0], box[3] - box[1]
    k = height / bh
    size = (max(8, int(round(bw * k))), height)
    rings = spec.rings()
    if spec.check_design:
        rings = design_rings(*spec.check_design)
    mask = rings_mask(rings, box, size) if rings else np.ones(size[::-1])
    cells = []
    mine_hi = composite(spec, pic, size, box)
    unders = spec.under if isinstance(spec.under, (list, tuple)) else [spec.under] * 2
    for j, ph in enumerate(spec.photos[:2] or [None]):
        if ph is None or not (PHOTOS / (ph[0] if isinstance(ph, (tuple, list)) else ph)).exists():
            crop = Image.new("RGB", size, (60, 60, 60))
            sx = sy = 0.17
        else:
            crop, (sx, sy) = photo_crop(ph, box, size)
        c = np.asarray(crop, np.float64) / 255.0
        # the picture at the photo's pixel density, then enlarged like the crop
        small = (max(2, int(round(bw * sx))), max(2, int(round(bh * sy))))
        lo = composite(spec, pic, small, box, unders[min(j, len(unders) - 1)])
        lo = np.asarray(Image.fromarray((lo * 255).astype(np.uint8)).resize(size, Image.BICUBIC), np.float64) / 255
        m = mask[..., None]
        cells.append(c)
        cells.append(lo * m + c * (1 - m))
    cells.append(mine_hi * mask[..., None] + (np.asarray(cells[0]) if cells else 0) * (1 - mask[..., None]))
    gap = 6
    W = sum(c.shape[1] for c in cells) + gap * (len(cells) - 1)
    out = Image.new("RGB", (W, height + 22), (32, 32, 32))
    x = 0
    for c in cells:
        out.paste(Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)), (x, 22))
        x += c.shape[1] + gap
    d = ImageDraw.Draw(out)
    nx, ny = pic.size
    d.text((4, 3), f"{spec.id}  {spec.kind}  {bw:.0f}x{bh:.0f} mm  {nx}x{ny}px", fill=(230, 230, 230), font=_font(15))
    return out


def check_sheet(specs, pics, out_path, height=560, per_row=None):
    cells = [check_cell(s, pics[s.id], height) for s in specs]
    maxw = 2600
    rows, row, w = [], [], 0
    for c in cells:
        if row and w + c.width + 16 > maxw:
            rows.append(row)
            row, w = [], 0
        row.append(c)
        w += c.width + 16
    if row:
        rows.append(row)
    W = max(sum(c.width + 16 for c in r) for r in rows)
    H = sum(max(c.height for c in r) + 16 for r in rows)
    sheet = Image.new("RGB", (W, H), (20, 20, 20))
    y = 0
    for r in rows:
        x = 0
        for c in r:
            sheet.paste(c, (x, y))
            x += c.width + 16
        y += max(c.height for c in r) + 16
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    print(f"check sheet: {out_path} {sheet.size}")


# ------------------------------------------------------------------------------------------------ noise
def fft_noise(shape, sigma_px, seed, aniso=(1.0, 1.0)):
    """Periodic (tileable) gaussian-filtered noise, zero mean, unit std. sigma_px: feature size in px (y, x
    scaled by aniso)."""
    rng = np.random.default_rng(seed)
    h, w = shape
    n = rng.standard_normal((h, w))
    fy = np.fft.fftfreq(h)[:, None] * aniso[0]
    fx = np.fft.fftfreq(w)[None, :] * aniso[1]
    g = np.exp(-2 * (math.pi * sigma_px) ** 2 * (fx ** 2 + fy ** 2))
    f = np.real(np.fft.ifft2(np.fft.fft2(n) * g))
    f -= f.mean()
    return f / max(f.std(), 1e-9)


def load_families():
    import importlib
    for name in FAMILIES:
        if (HERE / f"{name}.py").exists():
            importlib.import_module(name)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--out", default=str(CACHE / "art_wave3.png"))
    ap.add_argument("--height", type=int, default=560)
    a = ap.parse_args(argv)
    load_families()
    specs = list(REG.values())
    if a.ids:
        specs = [s for s in specs if any(s.id == i or s.id.endswith("_" + i) or i in s.id for i in a.ids)]
        if not specs:
            raise SystemExit(f"no picture matches {a.ids}; known: {', '.join(REG)}")
    pics = {}
    for s in specs:
        pic = render(s)
        pics[s.id] = pic
        if not a.no_write:
            write(s, pic)
        print(f"{s.id:40s} {s.kind:5s} {s.size_mm[0]:6.1f} x {s.size_mm[1]:6.1f} mm -> {pic.size[0]}x{pic.size[1]}")
    if not a.no_write:
        write_entries(specs)
    if a.merge:
        merge()
    if a.check:
        check_sheet(specs, pics, Path(a.out), a.height)


# ================================================================================================ pictures
# (families: art_wave3_skinny.py, art_wave3_laminated.py)

# ------------------------------------------------------------------------------------------------ PVC (СТ-Худ.)
LINE = "#a8a098"          # sandblasted / printed thin line on white satin (PVC СТ-Худ. renders)


def knot(L, w, loops=2):
    """The PVC СТ-Худ. interlaced knot, right half, centred on (0, 0), ~84 mm to the wing tip and ~245 mm to the
    spindle tips (draw it under a mirror_x): two long pointed lenses (upper / lower), a wide lobe above and below
    the middle with `loops` - 1 nested loops inside it, and a pointed wing."""
    for pts in (
        [[0, 242], [12, 180], [22, 110], [18, 50], [0, -30]],                                   # upper lens
        [[0, 30], [-16, -30], [-24, -100], [-18, -170], [0, -245]],                              # lower lens
        [[0, 140], [30, 118], [58, 80], [60, 46], [40, 18], [10, 2], [-6, -4]],                  # upper lobe
        [[-6, 4], [10, -2], [40, -18], [60, -46], [58, -84], [30, -122], [0, -142]],             # lower lobe
        [[16, 36], [50, 20], [82, 0], [50, -20], [16, -36]],                                     # wing
    ):
        L.curve(pts, w)
    for k in range(1, loops):
        f = 1 - 0.22 * k
        L.curve([[0, 112 * f + 10], [22 * f, 96 * f + 6], [38 * f + 4, 70 * f], [34 * f + 2, 44 * f], [14, 26]], w)
        L.curve([[14, -26], [34 * f + 2, -46 * f], [38 * f + 4, -74 * f], [22 * f, -102 * f - 6],
                 [0, -116 * f - 10]], w)


@art("doorglass_status_15", "fit", "Статус-15 СТ-Худ. (узор-вензель)", (131, 919, 675, 1878),
     photos=["p077_status-15-p-23__belyy.jpg", "p077_status-15-p-35__shimo-temnyy.jpg"],
     shape=("status-15", "doorglass_status_15"))
def status_15(a):
    """Thin grey line art on white satin: a frame of thin lines (vertical lines ~65 mm inside the visible edges,
    corner curls joined by horizontal lines near the top and the bottom) and a central interlaced knot (two long
    pointed lenses, one above the other, crossed by a wide lobe on each side and a pointed wing)."""
    L = a.layer(LINE)
    cx, cy = 403.0, 1410.0
    w = 2.6
    with a.mirror_x(cx):
        L.stroke([[cx - 183, 1048], [cx - 183, 1777]], w)                       # side lines
        for yb, sgn in ((1805, 1), (1020, -1)):                                 # top / bottom bar with curls
            with a.at(cx - 170, yb, sy=sgn):
                # the bar runs in from the middle, turns into a round curl at the corner
                L.curve([[170, 0], [110, 0], [50, 0], [18, -1], [-2, -6], [-14, -2], [-18, 9], [-12, 19], [0, 21],
                         [8, 13], [4, 5], [-4, 6], [-5, 12]], w, taper=(0, 6))
                # the side line's end: a hook into the curl
                L.curve([[-13, -28], [-12, -16], [-5, -9], [4, -8]], w * 0.9)
                # an arrow-like flourish on the bar
                L.curve([[62, 0], [50, 8], [36, 12], [26, 9]], w * 0.9, taper=(0, 8))
                L.curve([[56, 0], [44, -6], [32, -6]], w * 0.8, taper=(0, 8))
        # knot, right half (mirrored)
        with a.at(cx, cy):
            knot(L, w, loops=3)





STEM = "#a3a7ac"          # thin blue-grey stems (PVC СТ-Худ. renders)
AMBER = ("#b8741a", "#dfa23a", "#f2c872")   # leaf: rim, body, highlight


def amber_leaf(a, rim, body, hi, c, ang, length, width, bend=0.08):
    """A golden-amber glass leaf (a painted 'jewel') centred at c, pointing at ang degrees."""
    u = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
    c = np.asarray(c, np.float64)
    rim.leaf(c - u * length / 2, c + u * length / 2, width, bend)
    body.leaf(c - u * length * 0.44, c + u * length * 0.44, width * 0.72, bend)
    n = np.array([-u[1], u[0]])
    hi.leaf(c - u * length * 0.3 + n * width * 0.1, c + u * length * 0.28 + n * width * 0.1, width * 0.22, bend)


@art("doorglass_pvc_skinny_33", "fit", "Скинни-33 СТ-Худ. (стебли с золотыми листьями)", (137.5, 628.6, 683.5, 1900),
     photos=[("p078_skinni-33-p-31__italoreh-st-hud.jpg", (16, 20, 146, 341)),
             ("p078_skinni-33-p-32__milanoreh-st-hud.jpg", (16, 20, 146, 341))],
     shape=("pvc-skinny-33", "doorglass_pvc_skinny_33"))
def pvc_skinny_33(a):
    """White satin; two long blue-grey stems rise from a grass tuft at the bottom and cross once, making a tall
    figure of eight (a wide bulb below, a narrow loop above), thinner grass blades inside the bulb, six
    golden-amber leaves on the stem ends."""
    S = a.layer(STEM)
    rim, body, hi = a.layer(AMBER[0]), a.layer(AMBER[1]), a.layer(AMBER[2])
    w = 3.6
    # main stems
    S.curve([[418, 805], [360, 860], [300, 950], [262, 1050], [268, 1150], [318, 1262], [392, 1352], [442, 1425],
             [474, 1505], [486, 1560]], w, taper=(0, 40))
    S.curve([[424, 805], [490, 868], [556, 958], [590, 1060], [577, 1170], [522, 1272], [452, 1360], [396, 1440],
             [344, 1540], [320, 1640], [334, 1712], [360, 1742]], w, taper=(0, 40))
    S.curve([[415, 1430], [360, 1500], [318, 1560], [292, 1600]], w * 0.8, taper=(30, 30))
    # grass blades in the bulb: curved, crossing each other like a tulip of lines
    for pts, ww in (
        ([[421, 812], [395, 860], [372, 930], [366, 1000], [378, 1060]], 2.4),
        ([[421, 812], [448, 860], [470, 930], [474, 1000], [462, 1060]], 2.4),
        ([[421, 812], [380, 850], [342, 905], [320, 960], [312, 985]], 2.6),
        ([[421, 812], [462, 850], [502, 900], [526, 960], [534, 998]], 2.6),
        ([[421, 812], [432, 900], [448, 1000], [466, 1110], [478, 1196]], 2.6),
        ([[421, 812], [405, 900], [382, 1000], [352, 1150], [330, 1300]], 2.0),
        ([[421, 812], [408, 850], [400, 900], [404, 950], [416, 985]], 1.8),
        ([[421, 812], [434, 850], [442, 900], [438, 950], [426, 985]], 1.8),
        ([[440, 1080], [470, 1110], [505, 1140], [528, 1150]], 1.8),
    ):
        S.curve(pts, ww, taper=(0, 50))
    # the tuft
    for dx, dy in ((-70, -8), (-45, -14), (-20, -18), (25, -16), (50, -12), (75, -6), (-35, 6), (40, 8)):
        S.curve([[421, 812], [421 + dx * 0.5, 812 + dy * 0.3 - 2], [421 + dx, 812 + dy]], 1.6, taper=(0, 25))
    for c, ang, ln in (((385, 1755), 22, 64), ((284, 1628), 94, 68), ((503, 1572), 98, 68), ((484, 1226), 62, 64),
                       ((298, 996), -34, 62), ((548, 1012), 14, 62)):
        amber_leaf(a, rim, body, hi, c, ang, ln, 22, bend=0.05)



@art("doorglass_lotos_st_hud", "fit", "Лотос СТ-Худ. (линии и капли)", (131, 252, 505, 1848),
     photos=["p078_lotos-p-17__italoreh-st-hud.jpg", "p078_lotos-p-18__milanoreh-st-hud.jpg"],
     shape=("lotos-st-hud", "doorglass_lotos_st_hud"))
def lotos_st_hud(a):
    """One picture over the three panes (sickle, leaf, wedge): long thin grey lines running along the sickle and
    converging into its tail, shorter ones along the leaf and the wedge, small grey drops (leaf dabs) here and
    there."""
    L = a.layer("#948e88")
    w = 4.4
    for pts, ww in (
        ([[272, 1722], [250, 1650], [226, 1520], [208, 1400], [208, 1250], [224, 1110], [252, 1000], [300, 900],
          [358, 800], [398, 690], [418, 590], [426, 505]], w),
        ([[300, 1682], [276, 1590], [258, 1500], [248, 1380], [250, 1240], [264, 1100], [292, 1000], [336, 900],
          [376, 800], [406, 670], [422, 540]], w * 0.9),
        ([[278, 1452], [270, 1300], [274, 1180], [288, 1080], [318, 990], [352, 900], [388, 770], [412, 620]],
         w * 0.85),
        ([[304, 1210], [310, 1100], [334, 1000], [366, 900], [394, 810]], w * 0.75),
        # leaf pane
        ([[238, 770], [258, 700], [288, 620], [322, 530], [350, 450], [366, 390]], w * 0.85),
        ([[228, 700], [256, 630], [296, 540], [332, 450], [352, 395]], w * 0.7),
        # wedge
        ([[168, 272], [206, 306], [250, 346], [286, 388]], w * 0.8),
        ([[160, 298], [196, 330], [236, 372]], w * 0.65),
    ):
        L.curve(pts, ww, taper=(40, 60))
    for base, tip in (((274, 1806), (256, 1770)), ((270, 1506), (254, 1470)), ((266, 1410), (252, 1374)),
                      ((260, 734), (242, 710)), ((268, 704), (250, 680)), ((282, 652), (268, 626)),
                      ((178, 312), (162, 290))):
        L.teardrop(base, tip, 15)



@art("doorglass_orbita_plyus_st_hud", "fit", "Орбита Плюс СТ-Худ. (вензель в овале)", (281.5, 228, 526.5, 1756),
     photos=["p079_orbita-plyus-p-17__italoreh-st-hud.jpg", "p079_orbita-plyus-p-18__milanoreh-st-hud.jpg"],
     shape=("orbita-plyus-st-hud", "doorglass_orbita_plyus_st_hud"))
def orbita_plyus_st_hud(a):
    """White satin ellipse: a thin vertical line through its whole height and, in the middle, an interlaced knot
    ~200 x 490 mm: a pointed lens round it all, three nested heart-shaped lobes above the middle and three below
    (crossing on the axis), and a pointed wing each side."""
    L = a.layer(LINE)
    cx, cy = 404.0, 1000.0
    L.stroke([[cx, 262], [cx, 1722]], 2.0, taper=(120, 120))
    w = 2.8
    with a.mirror_x(cx):
        with a.at(cx, cy):
            L.curve([[0, 245], [40, 190], [72, 110], [92, 10], [78, -95], [44, -178], [0, -240]], w)   # lens
            L.curve([[30, 44], [66, 20], [102, 0], [66, -20], [30, -44]], w)                          # wing
            with a.mirror_y(cy):                    # (mirror planes are in leaf coordinates)
                for f in (1.0, 0.76, 0.52):
                    L.curve([[0, 200 * f + 18], [42 * f, 172 * f + 14], [76 * f, 112 * f + 8], [80 * f, 52 * f],
                             [52 * f, 14], [16, 2], [-6, -6]], w)





def band_edges(rings, ys):
    """Left / right x of a (vertical) band shape at the heights ys: its outermost crossings."""
    left, right = [], []
    for y in ys:
        xs = []
        for r in rings:
            R = np.vstack([r, r[:1]])
            for (x0, y0), (x1, y1) in zip(R[:-1], R[1:]):
                if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
                    xs.append(x0 + (y - y0) / (y1 - y0) * (x1 - x0))
        left.append(min(xs) if xs else np.nan)
        right.append(max(xs) if xs else np.nan)
    return np.array(left), np.array(right)


JEWEL = ("#6b3a14", "#c8741e", "#f0b050")    # small amber glass jewel: rim / body / light


def jewel(a, layers, x, y, size):
    """A small amber diamond jewel with a dark centre (PVC СТ-Худ.)."""
    rim, body, lite = layers
    rim.diamond(x, y, size, size)
    body.diamond(x, y, size * 0.74, size * 0.74)
    lite.diamond(x - size * 0.1, y + size * 0.1, size * 0.3, size * 0.3)
    rim.dot(x, y, size * 0.12)


@art("doorglass_virazh_plyus_st_hud", "fit", "Вираж Плюс СТ-Худ. (штрихи и янтарные ромбики)", (256, 164, 569, 1880),
     photos=["p079_virazh-plyus-p-17__italoreh-st-hud.jpg", "p079_virazh-plyus-p-18__milanoreh-st-hud.jpg"],
     shape=("virazh-plyus-st-hud", "doorglass_virazh_plyus_st_hud"))
def virazh_plyus_st_hud(a):
    """White satin wave band: long blue-grey brush swooshes (tapered, up to ~7 mm) that follow the band and cross it
    in pairs, three small amber diamond jewels on the band's axis (top, middle, bottom)."""
    rings = design_rings("virazh-plyus-st-hud", "doorglass_virazh_plyus_st_hud")
    ys = np.linspace(175, 1870, 400)
    lx, rx = band_edges(rings, ys)
    mid, half = (lx + rx) / 2, (rx - lx) / 2

    def along(y0, y1, k0, k1, wmax):
        y = np.linspace(y0, y1, 120)
        t = (y - y0) / (y1 - y0)
        k = k0 + (k1 - k0) * (3 * t * t - 2 * t ** 3)
        x = np.interp(y, ys, mid) + k * np.interp(y, ys, half)
        S.stroke(np.stack([x, y], 1), wmax, profile=lambda u: np.sin(np.pi * np.clip(u, 0, 1)) ** 0.7)

    S = a.layer("#848d96")
    for y0, y1, k0, k1, wm in (
        (1855, 1620, -0.45, -0.05, 5.5), (1790, 1470, 0.40, -0.30, 6.5), (1540, 1290, -0.05, -0.55, 6.0),
        (1340, 900, -0.55, -0.05, 7.0), (1210, 830, 0.15, 0.50, 6.5), (1010, 650, 0.55, -0.15, 7.0),
        (720, 430, 0.15, -0.45, 6.5), (570, 250, -0.30, -0.55, 5.5), (470, 205, 0.05, 0.25, 5.0),
    ):
        along(y0, y1, k0, k1, wm * 1.75)
    J = (a.layer(JEWEL[0]), a.layer(JEWEL[1]), a.layer(JEWEL[2]))
    for y in (1845, 1082, 262):
        jewel(a, J, float(np.interp(y, ys, mid)) + (10 if y == 1845 else 0), y, 30)



# ------------------------------------------------------------------------------------------------ shared art glass
@art("doorglass_zk_uzor", "fit", "Стекло ЗК-Узор (дуги)", (269.5, 0, 530.5, 2000),
     photos=[("p096_karat-f-22__beldub-zk-uzor.jpg", (11, 10, 140, 341)),
             ("p096_karat-f-27__venge-zk-uzor.jpg", (11, 10, 140, 341))],
     shape=[np.array([[276, 0], [524, 0], [524, 2000], [276, 2000]], np.float64)])
def zk_uzor(a):
    """Карат (the glass cell x 269.5-530.5 of the whole leaf height, 276-524 visible between 13 mm aluminium
    strips; the picture spans the cell): thin tapered arcs of large circles
    crossing each other, sparse and white (frosted) at the top, grey-brown and tan in the middle, dense and
    near-black at the bottom; a few short near-horizontal strokes."""
    W = a.layer("#fbfaf8", alpha=0.97)
    G = a.layer(grad=[(1990, "#b8a89a"), (1600, "#8a766a"), (1350, "#9c8676"), (1150, "#c2aa92"),
                      (900, "#9c8a7c"), (650, "#7a716a"), (450, "#4f4b48"), (150, "#353331")])
    tw = (30, 30)
    for pts, w in (                               # white, frosted: the top
        ([[262, 1640], [330, 1700], [400, 1750], [470, 1792], [538, 1820]], 3.0),
        ([[300, 1840], [370, 1790], [440, 1735], [500, 1680], [538, 1645]], 3.0),
        ([[262, 1880], [330, 1860], [400, 1830], [470, 1790]], 2.6),
        ([[420, 1960], [450, 1880], [490, 1800], [538, 1740]], 2.4),
        ([[262, 1520], [300, 1570], [340, 1610]], 2.4),
    ):
        W.curve(pts, w * 1.5, taper=tw)
    for pts, w in (
        ([[382, 1606], [386, 1540], [398, 1480], [424, 1420], [466, 1356], [526, 1300]], 4.0),     # upper arcs
        ([[462, 1590], [492, 1560], [522, 1520], [534, 1500]], 3.4),
        ([[300, 1500], [330, 1545], [362, 1582], [392, 1604]], 2.4),
        ([[396, 1300], [402, 1200], [400, 1100], [386, 1000], [360, 910], [322, 820]], 2.8),      # long tan arc
        ([[262, 1142], [290, 1140], [318, 1140]], 2.4),                                           # short strokes
        ([[392, 1128], [440, 1124], [490, 1134], [536, 1160]], 2.4),
        ([[430, 1096], [470, 1116], [505, 1140], [536, 1158]], 2.2),
        ([[262, 1072], [310, 1056], [360, 1052], [405, 1062]], 2.4),
        ([[330, 880], [380, 846], [430, 818], [480, 792], [530, 766]], 3.6),                      # the "<"
        ([[410, 680], [450, 710], [490, 738], [530, 766]], 3.0),
        ([[262, 700], [300, 740], [345, 790], [380, 840]], 2.4),
        ([[272, 560], [340, 552], [410, 546], [480, 546], [536, 548]], 3.8),                      # dark, lower
        ([[400, 640], [352, 590], [314, 520], [292, 440], [288, 360], [306, 270], [352, 180], [402, 110]], 4.2),
        ([[358, 700], [320, 630], [296, 560], [284, 480]], 2.6),
        ([[262, 330], [330, 352], [400, 374], [470, 392], [536, 404]], 3.6),
        ([[262, 240], [300, 280], [336, 320], [372, 368], [400, 400]], 3.4),
        ([[536, 336], [492, 290], [456, 236], [434, 180], [424, 110]], 4.2),
        ([[404, 150], [450, 156], [494, 160], [536, 162]], 3.4),
        ([[262, 300], [300, 250], [342, 196], [390, 150], [436, 108]], 3.0),
        ([[262, 420], [290, 380], [322, 330], [350, 280]], 2.4),
        ([[300, 60], [340, 110], [372, 170], [390, 240]], 2.6),
        ([[470, 40], [500, 90], [520, 150], [530, 210]], 2.4),
    ):
        G.curve(pts, w * 1.35, taper=tw)



# ------------------------------------------------------------------------------------------------ patterned glass (tiles)
def _noise_mm(pic, spec_mm, sigma_mm, seed, aniso=1.0):
    """Tileable noise over the picture: sigma in mm (x), aniso = sigma_y / sigma_x."""
    nx, ny = pic.size
    w, h = spec_mm
    kx = nx / w
    # fft_noise's sigma is in px along x; stretch along y by aniso (in px units of y)
    ky = ny / h
    f = fft_noise((ny, nx), sigma_mm * kx, seed, aniso=(aniso * ky / kx, 1.0))
    return f


def _warp_x(f, dx_px):
    """Shifts every row of f by dx_px[row, col] px along x (linear interpolation, wrapping)."""
    ny, nx = f.shape
    xs = (np.arange(nx)[None, :] + dx_px) % nx
    i0 = np.floor(xs).astype(int)
    t = xs - i0
    rows = np.arange(ny)[:, None]
    return f[rows, i0 % nx] * (1 - t) + f[rows, (i0 + 1) % nx] * t


def tint(pic, base_hex, tone, dark_hex=None, light_hex=None):
    """pic.rgb = the base colour shaded by tone (-1..1: toward dark_hex / light_hex)."""
    b = hex_rgb(base_hex)
    d = hex_rgb(dark_hex) if dark_hex else b * 0.8
    l = hex_rgb(light_hex) if light_hex else np.minimum(1, b * 1.15)
    t = np.clip(tone, -1, 1)[..., None]
    pic.rgb = np.where(t < 0, b + (d - b) * (-t), b + (l - b) * t)


@art("doorglass_bronze", "tile", "Бронзовое сатинато", (0, 0, 256, 256), base=BRONZE, ppm=2.0,
     photos=["p090_vud-klassik-51__natur-oak.jpg", "p091_vud-klassik-51__golden-oak.jpg"],
     check_box=(146, 855, 648.5, 1908), check_design=("wood-klassik-51", None))
def bronze(a):
    """Plain bronze satin (Вуд Классик-51 / -53 on oak): the colour of the renders, a barely visible frost."""
    def base(pic, X, Y):
        n = _noise_mm(pic, (256, 256), 1.2, 11) * 0.5 + _noise_mm(pic, (256, 256), 12, 12) * 0.5
        tint(pic, BRONZE["color"], n * 0.035)
    a.base = base


BC_RHOMB = (97.5, 152.0)          # rhombus: width x height (mm), measured on p088 (Вуд Классик-13, 0.39 px/mm)


@art("doorglass_bc", "tile", "Бронзовое худож. сатинато (ромбы)", (0, 0, 2 * BC_RHOMB[0], 2 * BC_RHOMB[1]),
     base=BRONZE, ppm=2.5,
     photos=["p088_vud-klassik-13__natur-oak.jpg", "p088_vud-klassik-13__golden-oak.jpg"],
     check_box=(166.25, 830, 628.5, 1840.5), check_design=("wood-klassik-13", None))
def bc(a):
    """Bronze satin with a lattice of rhombi 97.5 x 152 mm (measured on the WOOD CLASSIC renders; wave 2's White
    Crystal measured 106.5 x 157.9 on the Классико ones) drawn by ~4 mm darker, partly see-through lines - the
    renders show them darker than the bronze, not white."""
    def base(pic, X, Y):
        n = _noise_mm(pic, a.box[2:], 1.2, 21) * 0.5 + _noise_mm(pic, a.box[2:], 12, 22) * 0.5
        tint(pic, BRONZE["color"], n * 0.035)
    a.base = base
    L = a.layer("#7d5b4c", alpha=0.72, smooth=0.9)
    rw, rh = BC_RHOMB
    # a crossing on the pane's centre line x = 397.25 mm (Вуд Классик-13 / -15.1) at y = 33 mm mod 76, as in p088
    xc, yc = 397.25 % rw, 33.0
    for k in range(-3, 5):
        x = xc + k * rw
        L.stroke([[x - yc * rw / rh, 0], [x + (2 * rh - yc) * rw / rh, 2 * rh]], 4.0)
        L.stroke([[x + yc * rw / rh, 0], [x - (2 * rh - yc) * rw / rh, 2 * rh]], 4.0)


@art("doorglass_bronze_wave", "tile", "Бронзовое узорчатое «волна»", (0, 0, 300, 300), base=BRONZE, ppm=2.0,
     normal=True, photos=["p090_vud-klassik-33__natur-oak.jpg", "p090_vud-klassik-33__golden-oak.jpg"],
     check_box=(112, 687, 690, 1880), check_design=("wood-klassik-33", None))
def bronze_wave(a):
    """Rolled (textured) bronze glass of Вуд Классик-33: soft vertical wavy streaks, peach-bronze, a little lighter
    than the satin; the relief goes into a normal map."""
    def base(pic, X, Y):
        nx, ny = pic.size
        size = (300, 300)
        streak = _noise_mm(pic, size, 1.6, 31, aniso=14.0)
        wav = _noise_mm(pic, size, 40, 32) * 2.5 * nx / 300        # waviness: +-2.5 mm sideways
        f = _warp_x(streak, wav)
        g = _noise_mm(pic, size, 18, 33)
        tone = 0.75 * f + 0.2 * g
        tint(pic, "#cea892", tone * 0.30, "#a47a66", "#e6cbb8")
        pic.alpha = np.full((ny, nx), 0.88)
        pic.height = 0.35 * f + 0.2 * g
    a.base = base


@art("doorglass_st_118", "tile", "Стекло художественное СТ-118", (0, 0, 250, 250), base=BRONZE, ppm=2.4,
     normal=True, photos=["p078_alfa-p-17__italoreh-st-118.jpg", "p078_alfa-p-18__milanoreh-st-118.jpg"],
     check_box=(130, 787, 680, 1852), check_design=("alfa-st-118", None))
def st_118(a):
    """СТ-118 (Альфа, Каролина): rolled bronze-pink glass with a fine vertical rain streak and soft mottling. A
    uniform texture: made tileable (see the report: better tiled than fitted)."""
    def base(pic, X, Y):
        nx, ny = pic.size
        size = (250, 250)
        streak = _noise_mm(pic, size, 1.1, 41, aniso=9.0)
        mott = _noise_mm(pic, size, 4.0, 42, aniso=2.5)
        big = _noise_mm(pic, size, 25, 43)
        tone = 0.65 * streak + 0.3 * mott + 0.2 * big
        tint(pic, "#bd9885", tone * 0.30, "#9a7564", "#d6b8a7")
        pic.height = 0.25 * streak + 0.2 * mott
    a.base = base


@art("doorglass_st_121", "tile", "Стекло художественное СТ-121", (0, 0, 400, 400), base=BRONZE, ppm=2.0,
     normal=True, photos=["p097_sonata-f-01__dub-st-121.jpg", "p097_sonata-f-11__oreh-st-121.jpg"],
     check_box=(200, 1000, 600, 1600))
def st_121(a):
    """СТ-121 (Соната, Греция, Эксклюзив, Дуэт): rolled bronze-pink glass flecked with dark brown crackle - short
    broken veins and specks - over a soft mottle. A uniform texture: made tileable."""
    def base(pic, X, Y):
        nx, ny = pic.size
        size = (400, 400)
        mott = _noise_mm(pic, size, 7.0, 51)
        vein = _noise_mm(pic, size, 5.0, 52)
        brk = _noise_mm(pic, size, 9.0, 53)
        spk = _noise_mm(pic, size, 1.5, 54)
        k = nx / 400
        wline = np.clip(1 - np.abs(vein) / 0.22, 0, 1) ** 1.5 * np.clip((brk + 0.2) / 0.6, 0, 1)
        speck = np.clip((spk - 1.5) / 0.6, 0, 1) * np.clip((brk + 0.8) / 0.6, 0, 1)
        dark = np.clip(np.maximum(wline * 0.85, speck), 0, 1)
        fine = _noise_mm(pic, size, 1.8, 55)
        tint(pic, "#b99582", 0.3 * mott + 0.12 * fine, "#94705e", "#d4b4a2")
        d = hex_rgb("#7a5646")
        pic.rgb = pic.rgb * (1 - dark[..., None] * 0.75) + d * dark[..., None] * 0.75
        pic.height = 0.25 * mott - 0.3 * dark
    a.base = base



# ------------------------------------------------------------------------------------------------ scroll helpers
def scroll_pts(lead, c, r, a0, turns, cw=True, r_end=0.3):
    """Points of a line through `lead` (list of [x, y]) that ends in a spiral around c: it enters the circle of
    radius r at angle a0 (deg) tangentially and winds `turns` times (clockwise or not) down to r * r_end."""
    a1 = a0 - 360 * turns if cw else a0 + 360 * turns
    sp = spiral(c[0], c[1], r, r * r_end, a0, a1, step=max(0.6, r / 12))
    t = math.radians(a0)
    tan = np.array([math.sin(t), -math.cos(t)]) if cw else np.array([-math.sin(t), math.cos(t)])
    approach = sp[0] - tan * r * 0.7
    pts = [np.asarray(p, np.float64) for p in lead]
    # lead points close to the spiral's start would kink the spline
    while pts and np.hypot(*(pts[-1] - sp[0])) < r * 1.0:
        pts.pop()
    pts.append(approach)
    return np.vstack([np.array(pts).reshape(-1, 2), sp])


def scroll(L, lead, c, r, a0, turns, w, cw=True, taper=(0, 0), r_end=0.22, swell=0.35):
    """A C-scroll: a smooth line through `lead` ending in a spiral (see scroll_pts). Calligraphic width: the lead
    swells by `swell` in its middle, the spiral thins from w to ~0.45 w at its eye."""
    P = scroll_pts(lead, c, r, a0, turns, cw, r_end)
    sp_n = len(spiral(c[0], c[1], r, r * r_end, a0, a0 + 360 * turns, step=max(0.6, r / 12)))
    n_lead = len(P) - sp_n
    # the lead and the spiral's first points go through one spline so the joint is smooth
    Q = spline(np.vstack([P[:n_lead], P[n_lead:n_lead + 1]])) if n_lead >= 1 else P[:1]
    S = P[n_lead + 1:]
    P = np.vstack([Q, S])
    nq = len(Q)
    wid = np.empty(len(P))
    uq = arclen(Q) / max(arclen(Q)[-1], 1e-6) if nq > 1 else np.zeros(nq)
    wid[:nq] = w * (1 + swell * np.sin(np.pi * uq))
    if len(S):
        us = arclen(np.vstack([Q[-1:], S]))[1:]
        us = us / max(us[-1], 1e-6)
        wid[nq:] = w * (1 - 0.55 * us ** 1.2)
    return L.stroke(np.column_stack([P, wid]), taper=taper)


# ------------------------------------------------------------------------------------------------ WOOD CLASSIC decals
DECAL_WC = "#6e5f55"      # the sandblasted-looking ornament over the glass: darkens bronze and white satin alike


@art("doorart_wood_klassik_51", "decal", "Вуд Классик-51: орнамент по стеклу", (146, 855, 648.5, 1908),
     photos=["p091_vud-klassik-51__golden-oak.jpg", "p091_vud-klassik-51__ivory.jpg"],
     shape=("wood-klassik-51", "doorart_wood_klassik_51"), under=["bronze", "satin"])
def wood_klassik_51(a):
    """Over the glass of Вуд Классик-51 (bronze or white satin): a garland of C-scrolls under a small crown at the
    top, a wider garland (a smile ending in down-turned curls, scrolls and a fleur above its middle) near the
    bottom, and two thin vertical lines 70 mm inside the sides joining them."""
    L = a.layer(DECAL_WC, alpha=0.55, smooth=0.3)
    cx = 397.25
    w = 4.2
    with a.mirror_x(cx):
        L.stroke([[cx - 180, 975], [cx - 180, 1788]], 2.8)                    # side lines
        # --- top: a heart of two scrolls under the crown, a garland rising to curled ends, winged tendrils
        scroll(L, [[cx, 1782], [cx + 10, 1776], [cx + 22, 1777]], (cx + 24, 1790), 11, -95, 1.3, w, cw=False)
        scroll(L, [[cx + 30, 1776], [cx + 62, 1774], [cx + 100, 1782], [cx + 140, 1798], [cx + 166, 1800]],
               (cx + 172, 1814), 14, -100, 1.4, w, cw=False)
        L.curve([[cx + 186, 1822], [cx + 180, 1840], [cx + 158, 1850], [cx + 124, 1852], [cx + 96, 1846]], w * 0.8,
                taper=(8, 30))
        L.leaf((cx + 132, 1830), (cx + 98, 1826), 10, bend=0.2)
        # the crown: a tall bud, two petals curling out, little curls beside it
        L.leaf((cx + 3, 1802), (cx + 34, 1850), 15, bend=0.25)
        scroll(L, [[cx + 40, 1838], [cx + 52, 1850], [cx + 64, 1852]], (cx + 64, 1843), 7, 90, 1.1, w * 0.7)
        # --- bottom: a lyre of two big scrolls over the middle, a long smile ending in down-turned curls
        scroll(L, [[cx, 972], [cx + 22, 968], [cx + 52, 974], [cx + 78, 992]], (cx + 57, 1002), 23, -5, 1.45, w,
               cw=False, r_end=0.28)
        scroll(L, [[cx + 4, 1036], [cx + 14, 1044], [cx + 26, 1042]], (cx + 24, 1033), 8, 80, 1.1, w * 0.8)
        L.curve([[cx + 78, 1016], [cx + 108, 1012], [cx + 138, 998], [cx + 158, 980]], w * 0.9, taper=(0, 30))
        L.curve([[cx + 70, 1030], [cx + 100, 1034], [cx + 128, 1026]], w * 0.7, taper=(0, 20))
        L.leaf((cx + 118, 1004), (cx + 146, 1020), 9, bend=-0.2)
        scroll(L, [[cx, 924], [cx + 50, 927], [cx + 110, 938], [cx + 160, 954], [cx + 186, 962]],
               (cx + 194, 948), 14, 95, 1.4, w, cw=True)
    L.stroke([[cx, 972], [cx, 1036]], w * 0.8)
    L.teardrop((cx, 1036), (cx, 1066), 12)
    L.teardrop((cx, 1796), (cx, 1872), 18)




@art("doorart_wood_klassik_53", "decal", "Вуд Классик-53: орнамент по стеклу", (146, 645, 648.5, 1892),
     photos=["p091_vud-klassik-53__golden-oak.jpg", "p091_vud-klassik-53__ivory.jpg"],
     shape=("wood-klassik-53", "doorart_wood_klassik_53"), under=["bronze", "satin"])
def wood_klassik_53(a):
    """Over the glass of Вуд Классик-53: a scroll garland along the top edge and one along the bottom edge (each
    with a small centre motif), a large fleur-de-lis on a stalk between two pairs of big spirals in the upper third
    (a butterfly-like motif ~380 x 320 mm), a small trident motif in the middle and a small fleur above the bottom
    garland. Line art only: the glass under it gives the tint."""
    L = a.layer(DECAL_WC, alpha=0.55, smooth=0.3)
    cx = 397.25
    w = 4.8
    with a.mirror_x(cx):
        # --- top garland along the hump
        scroll(L, [[cx + 6, 1842], [cx + 50, 1836], [cx + 110, 1820], [cx + 160, 1802], [cx + 190, 1798]],
               (cx + 198, 1812), 11, -100, 1.35, w, cw=False)
        L.curve([[cx + 30, 1852], [cx + 70, 1858], [cx + 120, 1846], [cx + 150, 1832]], w * 0.75, taper=(10, 30))
        scroll(L, [[cx + 2, 1858], [cx + 12, 1866], [cx + 24, 1864]], (cx + 22, 1855), 7, 80, 1.1, w * 0.8)
        # --- the big motif: a lily of four long petals, an arm to a spiral and a big spiral each side, tails
        L.curve([[cx + 4, 1418], [cx + 12, 1500], [cx + 22, 1582], [cx + 36, 1648], [cx + 50, 1682],
                 [cx + 60, 1684]], w * 0.9, taper=(10, 0))
        L.dot(cx + 60, 1676, 6.5)
        L.curve([[cx + 2, 1436], [cx + 8, 1540], [cx + 14, 1618], [cx + 22, 1650]], w * 0.8, taper=(10, 0))
        L.dot(cx + 24, 1655, 5.5)
        scroll(L, [[cx + 12, 1600], [cx + 70, 1614], [cx + 128, 1612]], (cx + 166, 1584), 20, 95, 1.6, w,
               r_end=0.3)
        scroll(L, [[cx + 48, 1592], [cx + 86, 1566], [cx + 120, 1552]], (cx + 128, 1506), 36, 45, 1.6, w * 1.1,
               r_end=0.32)
        L.curve([[cx + 46, 1558], [cx + 64, 1526], [cx + 66, 1486], [cx + 52, 1456]], w * 0.9, taper=(15, 15))
        L.curve([[cx + 116, 1470], [cx + 136, 1444], [cx + 158, 1412]], w * 0.9, taper=(0, 25))
        L.curve([[cx + 40, 1446], [cx + 30, 1418], [cx + 18, 1396]], w * 0.8, taper=(0, 20))
        # --- the small trident in the middle
        scroll(L, [[cx + 3, 1236], [cx + 16, 1262], [cx + 32, 1290], [cx + 44, 1312]], (cx + 36, 1318), 7, 0, 1.2,
               w * 0.8, cw=False)
        # --- small fleur above the bottom garland
        scroll(L, [[cx + 3, 800], [cx + 14, 812], [cx + 30, 818]], (cx + 30, 828), 7, -90, 1.1, w * 0.75,
               cw=False)
        # --- bottom garland along the lower hump
        scroll(L, [[cx + 6, 712], [cx + 60, 720], [cx + 120, 738], [cx + 168, 752], [cx + 194, 752]],
               (cx + 202, 738), 11, 100, 1.35, w, cw=True)
        L.curve([[cx + 30, 700], [cx + 74, 694], [cx + 124, 708], [cx + 160, 726]], w * 0.75, taper=(10, 30))
        L.leaf((cx + 90, 742), (cx + 128, 762), 10, bend=-0.2)
    L.teardrop((cx, 1668), (cx, 1712), 11)
    L.stroke([[cx, 1196], [cx, 1300]], w * 0.9, taper=(20, 0))
    L.teardrop((cx, 1296), (cx, 1334), 10)
    L.leaf_line((cx, 796), (cx, 872), 13, w * 0.8)
    L.teardrop((cx, 700), (cx, 740), 11)


if __name__ == "__main__":
    import art_wave3
    art_wave3.main()
