#!/usr/bin/env python3
"""Lift textures, family `walls`: decorated cabin walls of the GLZ / NBSL catalogue (p.11-14).

    python tools/lifts/textures/walls.py [--no-merge] [ids]          # ids like sl-1134_back

liftwall_<cabin>_back / _side: one fitted picture across the whole wall (all its panels), metersPerTile [1, 1],
u = left -> right as seen from inside the car, v = floor -> ceiling (car height 2.385 m). Drawn for a 1.34 m back
wall (576 x 1024) and a 2.0 m side wall (864 x 1024); every division is a fraction of the width, so other car sizes
stretch it. Both side walls use the same picture (the engine mirrors nothing), so side designs are symmetric.
Colours are baked (not tinted): stainless #d9d9d9, rose gold #d6a476, titanium gold #d2b262, black titanium #3b3633,
smoky grey #7a6650 (metals.md), wood-look 8054 (dark sapele) #64361c, 8055 (beech) #b8915a.

Plain-finish walls get no picture (the engine uses lift_brushed / lift_mirror with the finish tint): SL-1136 side
(smoky-grey hairline) is one of them.
"""
import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lift_kit as K                # noqa: E402

FAMILY = "walls"
SOURCE = "procedural:tools/lifts/textures/walls.py"
H_M = 2.385
SIZES = {"back": (1.34, 576), "side": (2.0, 864)}
PH = 1024
STAINLESS, ROSE, TIGOLD, BLACKTI, SMOKY = "#d9d9d9", "#d6a476", "#d2b262", "#3b3633", "#7a6650"
WOOD_8054, WOOD_8055 = "#64361c", "#b8915a"


class Wall:
    """Per-pixel layers of one wall: colour (linear), metallic, smoothness, hairline, etch, wood, seams."""

    def __init__(self, kind, seed):
        self.W, self.w = SIZES[kind]
        self.h = PH
        self.rng = np.random.default_rng(seed)
        self.col = np.zeros((self.h, self.w, 3))
        self.sm = np.zeros((self.h, self.w))
        self.hair = np.zeros((self.h, self.w))
        self.etch = np.zeros((self.h, self.w))
        self.wood = np.zeros((self.h, self.w))
        self.wood_col = np.zeros((self.h, self.w, 3))
        self.wood_h = np.zeros((self.h, self.w))
        self.seams = []
        self.mmx, self.mmy = self.W * 1000 / self.w, H_M * 1000 / self.h

    def canvas(self):
        return K.MCanvas(self.W, H_M, self.w, self.h, 4)

    def band(self, f0, f1):
        """Coverage of the vertical band between width fractions f0..f1."""
        c = self.canvas()
        c.rect(f0 * self.W, 0, f1 * self.W, H_M)
        return c.mask()

    def metal(self, m, colour, smooth, hairline=False):
        a = m[..., None]
        self.col = self.col * (1 - a) + K.lin(colour) * a
        self.sm = self.sm * (1 - m) + smooth * m
        self.hair = self.hair * (1 - m) + (1.0 if hairline else 0.0) * m

    def woodpanel(self, m, light, dark, mean, contrast=0.9):
        a, tone = K.woodgrain(self.rng, self.h, self.w, self.mmx, self.mmy, light, dark, contrast=contrast)
        a = K.fit_mean(a, mean)
        al = m[..., None]
        self.wood_col = self.wood_col * (1 - al) + a * al
        self.wood_h = self.wood_h * (1 - m) + tone * m
        self.wood = np.maximum(self.wood, m)

    def panels(self, spec):
        """spec: list of (fraction width, kind, args) left to right; seams between them."""
        f = 0.0
        for width, kind, args in spec:
            m = self.band(f, f + width)
            if kind == "wood":
                self.woodpanel(m, *args)
            else:
                self.metal(m, *args)
            f += width
            if f < 0.999:
                self.seams.append(f)

    def render(self):
        alb, nrm, msk = K.etched_metal(self.rng, self.w, self.h, self.mmx, self.mmy, self.col, self.etch,
                                       bg_smooth=self.sm, hairline=self.hair, seam_u=None, etch_light=1.22)
        # wood-look film over steel: dielectric, satin
        wd = self.wood
        if wd.max() > 0:
            a8 = K.to8(self.wood_col)
            alb = np.round(alb * (1 - wd[..., None]) + a8 * wd[..., None]).astype(np.uint8)
            wn = K.normal_from_height(self.wood_h, k=0.12, periodic=False)
            nrm = np.round(nrm * (1 - wd[..., None]) + wn * wd[..., None]).astype(np.uint8)
            msk = msk.astype(np.float64)
            msk[..., 0] *= (1 - wd)
            msk[..., 3] = msk[..., 3] * (1 - wd) + 0.5 * 255 * wd
            msk = np.round(msk).astype(np.uint8)
        # panel joints: dark hairline reveals
        if self.seams:
            xs = np.arange(self.w)[None, :] + 0.5
            sl = np.zeros((1, self.w))
            for u in self.seams:
                sl = np.maximum(sl, np.clip(1.3 - np.abs(xs - u * self.w), 0, 1))
            sl = sl * np.ones((self.h, 1))
            alb = np.round(alb * (1 - 0.75 * sl[..., None])).astype(np.uint8)
            msk = msk.copy()
            msk[..., 1] = np.round(msk[..., 1] * (1 - 0.6 * sl)).astype(np.uint8)
        return alb, nrm, msk


# ------------------------------------------------------------------------------------------------ ornaments
def arch(c, cx, half, cap_y, scale=1.0):
    """Etched classical arch on fluted Ionic columns (as door SL-7037), columns at cx +- half."""
    s = scale
    for sx in (-1, 1):
        x = cx + sx * half
        c.rect(x - 0.075 * s, 0.03, x + 0.075 * s, 0.07)
        c.rect(x - 0.065 * s, 0.07, x + 0.065 * s, 0.09)
        n, hw = 5, 0.058 * s
        sw = 2 * hw / n
        for i in range(n):
            a = x - hw + i * sw
            c.rect(a + 0.003, 0.09, a + sw - 0.003, cap_y)
        cy1 = cap_y + 0.085 * s
        c.rect(x - 0.085 * s, cy1 - 0.016 * s, x + 0.085 * s, cy1)
        c.poly([(x - 0.07 * s, cap_y), (x + 0.07 * s, cap_y), (x + 0.08 * s, cy1 - 0.016 * s), (x - 0.08 * s, cy1 - 0.016 * s)])
        for vx in (-1, 1):
            vcx, vcy = x + vx * 0.068 * s, cap_y + 0.022 * s
            c.circle(vcx, vcy, 0.024 * s)
            pts = []
            for t in np.linspace(0, 1, 50):
                a = math.pi / 2 + vx * 1.5 * 2 * math.pi * t
                r = 0.018 * s * 0.55 ** (3 * t)
                pts.append((vcx + r * math.cos(a), vcy + r * math.sin(a)))
            c.line(pts, 0.004, v=0)
    ay = cap_y + 0.085 * s
    r_out, r_in = half + 0.06 * s, half - 0.045 * s
    c.poly(c.arc_pts(cx, ay, r_out, 0, math.pi) + c.arc_pts(cx, ay, r_in, math.pi, 0))
    c.line(c.arc_pts(cx, ay, r_out - 0.008, 0, math.pi), 0.003, v=0)
    c.line(c.arc_pts(cx, ay, r_in + 0.008, 0, math.pi), 0.003, v=0)
    rm = (r_out + r_in) / 2
    nb = max(9, int(math.pi * rm / 0.045))
    for a in np.linspace(0.05, math.pi - 0.05, nb):
        c.circle(cx + rm * math.cos(a), ay + rm * math.sin(a), 0.0085 * s, v=0)
    c.poly([(cx - 0.045 * s, ay + r_in - 0.01), (cx + 0.045 * s, ay + r_in - 0.01), (cx + 0.06 * s, ay + r_out + 0.035 * s),
            (cx - 0.06 * s, ay + r_out + 0.035 * s)])
    c.rect(cx - 0.025 * s, ay + r_in + 0.02, cx + 0.025 * s, ay + r_out + 0.01)
    ri = half - 0.095 * s
    c.line([(cx - ri, 0.12)] + c.arc_pts(cx, ay - 0.04, ri, math.pi, 0) + [(cx + ri, 0.12), (cx - ri, 0.12)], 0.004)
    return ay + r_out + 0.035 * s


def fret_frame(c, x0, y0, x1, y1, lw=0.005, k=0.06):
    """Thin etched line frame with Chinese key-fret corners (SL-1109 / SL-8048): each corner steps in twice."""
    pts = [
        (x0 + k, y0), (x1 - k, y0), (x1 - k, y0 + k * 0.5), (x1 - k * 0.5, y0 + k * 0.5), (x1 - k * 0.5, y0 + k),
        (x1, y0 + k), (x1, y1 - k), (x1 - k * 0.5, y1 - k), (x1 - k * 0.5, y1 - k * 0.5), (x1 - k, y1 - k * 0.5),
        (x1 - k, y1), (x0 + k, y1), (x0 + k, y1 - k * 0.5), (x0 + k * 0.5, y1 - k * 0.5), (x0 + k * 0.5, y1 - k),
        (x0, y1 - k), (x0, y0 + k), (x0 + k * 0.5, y0 + k), (x0 + k * 0.5, y0 + k * 0.5), (x0 + k, y0 + k * 0.5),
        (x0 + k, y0)]
    c.line(pts, lw)
    # small square key motifs inside the corners
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)):
        q = k * 0.45
        ax, ay = cx + sx * k * 1.05, cy + sy * k * 1.05
        c.line([(ax, ay), (ax + sx * q, ay), (ax + sx * q, ay + sy * q), (ax, ay + sy * q), (ax, ay)], lw * 0.8)


def ribbons(c, rng, W, n_bundles=5, lw=(0.003, 0.006)):
    """Long sweeping etched strands in bundles (SL-8147): cubic curves rising from low on one side and arching over."""
    for b in range(n_bundles):
        x0 = rng.uniform(0.05, 0.6) * W
        span = rng.uniform(0.4, 0.9) * W * (1 if rng.random() < 0.6 else -1)
        p0 = (x0, rng.uniform(-0.2, 0.6))
        p1 = (x0 + span * 0.1, rng.uniform(1.2, 1.8))
        p2 = (x0 + span * 0.6, rng.uniform(2.2, 2.7))
        p3 = (x0 + span, rng.uniform(1.6, 2.6))
        k = rng.integers(4, 9)
        for i in range(k):
            off = (i - k / 2) * rng.uniform(0.008, 0.016)
            q = [(p[0] + off * (1 + 0.6 * j), p[1] + off * 0.3 * j) for j, p in enumerate((p0, p1, p2, p3))]
            pts = []
            for t in np.linspace(0, 1, 160):
                u = 1 - t
                pts.append((u ** 3 * q[0][0] + 3 * u * u * t * q[1][0] + 3 * u * t * t * q[2][0] + t ** 3 * q[3][0],
                            u ** 3 * q[0][1] + 3 * u * u * t * q[1][1] + 3 * u * t * t * q[2][1] + t ** 3 * q[3][1]))
            # strands fade in and out: draw a sub-range
            a = int(rng.uniform(0, 0.25) * len(pts))
            e = int(rng.uniform(0.7, 1.0) * len(pts))
            c.line(pts[a:e], rng.uniform(*lw))


# ------------------------------------------------------------------------------------------------ walls
def w1134(kind):
    """Stainless: back = hairline side panels + centre SL-8045 mirror with a fine etched dot screen; side = mirror
    centre between hairline panels."""
    w = Wall(kind, 1134 + (kind == "side"))
    if kind == "back":
        w.panels([(0.2, "metal", (STAINLESS, 0.58, True)), (0.6, "metal", (STAINLESS, 0.95)),
                  (0.2, "metal", (STAINLESS, 0.58, True))])
        c = w.canvas()
        pitch, r = 0.024, 0.0055
        for x in np.arange(0.2 * w.W + pitch, 0.8 * w.W - pitch / 2, pitch):
            for y in np.arange(0.06, H_M - 0.04, pitch):
                c.circle(x + (pitch / 2 if int(round(y / pitch)) % 2 else 0), y, r)
        w.etch = c.mask() * w.band(0.21, 0.79)
    else:
        w.panels([(0.18, "metal", (STAINLESS, 0.58, True)), (0.64, "metal", (STAINLESS, 0.95)),
                  (0.18, "metal", (STAINLESS, 0.58, True))])
    return w


def w1095(kind):
    """Titanium gold mirror with etched arches on fluted columns (SL-8008): one arch on the back wall, two on a side."""
    w = Wall(kind, 1095 + (kind == "side"))
    w.panels([(1.0, "metal", (TIGOLD, 0.93))])
    c = w.canvas()
    if kind == "back":
        arch(c, w.W / 2, w.W * 0.33, 1.52, 1.0)
    else:
        for cx in (0.25, 0.75):
            arch(c, cx * w.W, w.W * 0.18, 1.52, 0.85)
    # festoon loops under the ceiling
    n = 5 if kind == "back" else 8
    for k in range(n):
        x = (k + 0.5) / n * w.W
        c.line([(x - 0.03, H_M)] + c.arc_pts(x, H_M - 0.09, 0.03, math.pi, 2 * math.pi) + [(x + 0.03, H_M)], 0.008)
    w.etch = c.mask()
    return w


def w1109(kind):
    """Rose gold (SL-8048): mirror panels with an etched fret-cornered line frame between hairline pylons."""
    w = Wall(kind, 1109 + (kind == "side"))
    if kind == "back":
        spec = [(0.2, "metal", (ROSE, 0.6, True)), (0.6, "metal", (ROSE, 0.94)), (0.2, "metal", (ROSE, 0.6, True))]
        frames = [(0.2, 0.8)]
    else:
        spec = [(0.12, "metal", (ROSE, 0.6, True)), (0.34, "metal", (ROSE, 0.94)), (0.08, "metal", (ROSE, 0.6, True)),
                (0.34, "metal", (ROSE, 0.94)), (0.12, "metal", (ROSE, 0.6, True))]
        frames = [(0.12, 0.46), (0.54, 0.88)]
    w.panels(spec)
    c = w.canvas()
    for f0, f1 in frames:
        x0, x1 = f0 * w.W + 0.05, f1 * w.W - 0.05
        fret_frame(c, x0, 0.12, x1, H_M - 0.12, 0.005, 0.07)
    w.etch = c.mask()
    return w


def w1135(kind):
    """Dark wood-look pylons (SL-8054) alternating with stainless mirror panels."""
    w = Wall(kind, 1135 + (kind == "side"))
    wood = ("wood", ("#7c4628", "#47220f", WOOD_8054, 1.0))
    mir = ("metal", (STAINLESS, 0.96))
    if kind == "back":
        spec = [(0.27,) + wood, (0.46,) + mir, (0.27,) + wood]
    else:
        spec = [(0.12,) + mir, (0.24,) + wood, (0.28,) + mir, (0.24,) + wood, (0.12,) + mir]
    w.panels(spec)
    return w


def w1136(kind):
    """Back: beech wood-look panels (SL-8055) framed by smoky-grey hairline stainless."""
    w = Wall(kind, 1136)
    wood = ("wood", ("#cfa774", "#9c7440", WOOD_8055, 0.7))
    w.panels([(0.1, "metal", (SMOKY, 0.6, True)), (0.4,) + wood, (0.4,) + wood, (0.1, "metal", (SMOKY, 0.6, True))])
    return w


def w1137(kind):
    """Rose gold hairline panels with etched sweeping strands (SL-8147) between black titanium mirror strips."""
    w = Wall(kind, 1137 + (kind == "side"))
    blk = ("metal", (BLACKTI, 0.95))
    pan = ("metal", ("#cfa27a", 0.62, True))
    if kind == "back":
        spec = [(0.1,) + blk, (0.8,) + pan, (0.1,) + blk]
        areas = [(0.1, 0.9)]
    else:
        spec = [(0.1,) + blk, (0.35,) + pan, (0.1,) + blk, (0.35,) + pan, (0.1,) + blk]
        areas = [(0.1, 0.45), (0.55, 0.9)]
    w.panels(spec)
    rng = np.random.default_rng(8147 + (kind == "side"))
    e = np.zeros((w.h, w.w))
    for f0, f1 in areas:
        c = w.canvas()
        sub = K.MCanvas((f1 - f0) * w.W, H_M, int(round((f1 - f0) * w.w)), w.h, 4)
        ribbons(sub, rng, (f1 - f0) * w.W, n_bundles=5 if kind == "back" else 3)
        m = sub.mask()
        x0 = int(round(f0 * w.w))
        e[:, x0:x0 + m.shape[1]] = np.maximum(e[:, x0:x0 + m.shape[1]], m[:, : w.w - x0])
    w.etch = e
    # etched strands: lighter, yellower gold
    w.col = w.col * (1 - e[..., None]) + K.lin("#e2c08e") * e[..., None]
    return w


WALLS = {
    "sl-1134": ("SL-1134", w1134, ("back", "side")),
    "sl-1095": ("SL-1095", w1095, ("back", "side")),
    "sl-1109": ("SL-1109", w1109, ("back", "side")),
    "sl-1135": ("SL-1135", w1135, ("back", "side")),
    "sl-1136": ("SL-1136", w1136, ("back",)),
    "sl-1137": ("SL-1137", w1137, ("back", "side")),
}
NAMES = {"back": "задняя стенка", "side": "боковая стенка"}


def mid_of(cab, kind):
    return f"liftwall_{cab.replace('-', '_')}_{kind}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-merge", action="store_true")
    args = ap.parse_args(argv)
    todo = [(c, k) for c, (_, _, kinds) in WALLS.items() for k in kinds]
    if args.ids:
        todo = [(c, k) for c, k in todo if f"{c}_{k}" in args.ids or c in args.ids]
    for cab, kind in todo:
        alb, nrm, msk = WALLS[cab][1](kind).render()
        K.write_material(mid_of(cab, kind), alb, nrm, msk)
        print(mid_of(cab, kind), K.mean_hex(alb), alb.shape)
    entries = [K.entry(mid_of(c, k), f"{WALLS[c][0]} {NAMES[k]}", SOURCE, (1, 1), 1024, mask_size=1024)
               for c, (_, _, kinds) in WALLS.items() for k in kinds]
    rows = []
    for cab, (_, _, kinds) in WALLS.items():
        ims = [K.fit_h(Image.open(K.REF / "cabins" / f"{cab}.jpg").convert("RGB"), 400)]
        for k in kinds:
            mid = mid_of(cab, k)
            alb, msk = K.read_albedo(mid), K.read_mask(mid)
            ims += [K.fit_h(Image.fromarray(alb), 400), K.fit_h(Image.fromarray(msk[..., 3]), 400),
                    K.fit_h(K.lit_preview(alb, msk), 400)]
        rows.append((f"{cab}: photo | back: albedo, smoothness, lit | side: albedo, smoothness, lit", ims))
    rows = [(a[0] + "   ||   " + (b[0] if b else ""), a[1] + (b[1] if b else [])) for a, b in zip(rows[::2], rows[1::2] + [None])]
    K.sheet(rows, K.SHEETS / f"{FAMILY}.png", "Lift cabin walls")
    K.write_entries(FAMILY, entries, merge=not args.no_merge)


if __name__ == "__main__":
    main()
