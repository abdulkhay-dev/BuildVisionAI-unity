#!/usr/bin/env python3
"""Art and patterned door glass of the DveriMebel / el'PORTA / BRAVO catalogue (2020), redrawn as vector artwork.

    python3 tools/doors/textures/art_glass.py                  # every glass: textures + entries + Glass/art.json
    python3 tools/doors/textures/art_glass.py sprig wc         # only these (entries / Glass/art.json keep all)
    python3 tools/doors/textures/art_glass.py --compare        # + tools/doors/.cache/glass_art.png (needs the photos)
    python3 tools/doors/textures/art_glass.py --no-write --compare
    then: python3 tools/doors/textures/merge_entries.py tools/doors/textures/entries/art-glass.json

Needs numpy and Pillow only. Writes per glass (M = material id "doorglass_<id>"):

    Assets/House4696/External/Materials/M/M_albedo.png   see-through glass: sRGB RGBA, alpha = opacity (satin 0.90 as
                                                          the app's Magic Fog, paint 1, clear lines 0.14)
    Assets/House4696/External/Materials/M/M_albedo.jpg   mirrors: opaque sRGB
    Assets/House4696/External/Materials/M/M_mask.png     R metallic, G occlusion 255, B 0, A smoothness
    Assets/House4696/External/Materials/M/M_normal.png   only Silver Art (engraved lines), OpenGL
    tools/doors/textures/entries/art-glass.json          the external.json entries (category "doorglass")
    Assets/House4696/Resources/Doors/Glass/art.json      the catalogue glass (id, name, role, material, fit)

Two kinds of glass:
  * fit - a picture over one pane: u across the visible glass (0 on the lock side, as the catalogue photo shows the
    leaf), v up. The engine stretches it over every pane of the door, so a picture is drawn for the pane of the design
    that sells the glass (art "pane", leaf mm). metersPerTile [1, 1]: the UVs already run 0..1.
    The motifs were traced from the catalogue renders into vector files (tools/doors/textures/art/<art>.json; how:
    tools/doors/textures/art/trace/README) and are rendered here at any resolution;
  * tile - a pattern in metres (metersPerTile = the tile): White Crystal's rhombus lattice and Silver Art's
    engraved scribbles are generated here (seamless).
A picture is a stack of layers over a base glass: each layer is a coverage (vector items rendered with 4x4
supersampling: crisp, anti-aliased edges) with its own colour, opacity, metallic and smoothness.

Vector files: millimetres, origin at the bottom-left of the pane / tile, x to the right, y up. Items:
{"stroke": [[x, y, w], ...]} a centre line with its width (round joins and ends); {"poly": [ring, hole, ...]} rings
of [x, y] (the first is the outline, the others holes). Layer: {"role", "color", optional "alpha" / "metallic" /
"smooth", "items", optional "tone": a grey PNG over the pane that shades the colour (sprig's buds)}.
"""
import argparse
import io
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXT = ROOT / "Assets" / "House4696" / "External"
GLASS_JSON = ROOT / "Assets" / "House4696" / "Resources" / "Doors" / "Glass" / "art.json"
ENTRIES = HERE / "entries" / "art-glass.json"
ART = HERE / "art"
CACHE = ROOT / "tools" / "doors" / ".cache"
SOURCE = "procedural:tools/doors/textures/art_glass.py"
SS = 4                                   # supersampling of the vector renderer

# ------------------------------------------------------------------------------------------------ materials
# sRGB colour, opacity (see-through glass only), metallic, smoothness
SATIN = dict(color="#f2ece3", alpha=0.90, metallic=0.0, smooth=0.40)        # = M_DoorGlassSatin (Magic Fog)
CLEAR = dict(color="#f4f6f6", alpha=0.14, metallic=0.0, smooth=0.95)        # polished (not etched) glass
MIRROR = dict(color="#ebebeb", alpha=1.0, metallic=1.0, smooth=0.98)        # silver mirror (= M_IntMirror)
BLACK_MIRROR = dict(color="#47474a", alpha=1.0, metallic=1.0, smooth=0.98)  # black (graphite) mirror, ~6 % reflection
FROSTED = dict(color="#e9e7e3", alpha=1.0, metallic=0.0, smooth=0.32)       # sandblasted mirror: diffuse white
BASES = dict(satin=SATIN, mirror=MIRROR, black_mirror=BLACK_MIRROR, frosted=FROSTED,
             frosted_white=dict(FROSTED, color="#f1eee9"))                # Silver Art's matt field (p033: #f3eee9)
ROLES = {                                # layer materials (colour / alpha / metallic / smooth may be overridden)
    "paint": dict(color="#8c8783", alpha=1.0, metallic=0.0, smooth=0.50),   # enamel / UV print on satin
    "clear": CLEAR,
    "frosted": dict(FROSTED, color="#b5b3af"),                             # frosted motif on a mirror (grey)
    "mirror": MIRROR,
    "print": dict(color="#cfcfcd", alpha=1.0, metallic=0.0, smooth=0.36),   # light print on the black mirror
}

# ------------------------------------------------------------------------------------------------ the glass
# id / name (as the catalogue writes it) / role (fallback when the material is missing) / fit or tile / art (vector
# file) or gen (generator) / base glass / layer role overrides / albedo size (px) / refs: catalogue photos for the
# check sheet (photo, pane in leaf mm) - the first is shown.
GLASS = [
    dict(id="sprig", name="Стекло Глейс SPRIG", role="satin", fit=True, art="sprig", base="satin", size=(512, 4096),
         refs=[("p014_gleys-1-sprig__3d-cappuccino.jpg",), ("p014_gleys-1-sprig__3d-wenge.jpg",)]),
    dict(id="twig", name="Стекло Глейс TWIG", role="satin", fit=True, art="twig", base="satin", size=(512, 4096),
         refs=[("p014_gleys-1-twig__3d-cappuccino.jpg",), ("p014_gleys-1-twig__3d-wenge.jpg",)]),
    # Глейс-2 TWIG: the same glass on a wider pane with its own composition - a design art role, not a catalogue glass
    dict(id="twig-2", material="doorglass_twig_2", catalog=False, name="Стекло Глейс TWIG (Глейс-2)", role="satin",
         fit=True, art="twig-2", base="satin", size=(1024, 4096),
         refs=[("p014_gleys-2-twig__3d-cappuccino.jpg",), ("p014_gleys-2-twig__3d-wenge.jpg",)]),
    dict(id="vitrazh", name="Белое сатинато «Витраж»", role="satin", fit=True, art="vitrazh", base="satin",
         size=(512, 4096), refs=[("p012_trend-14__3d-cappuccino.jpg",), ("p012_trend-14__3d-wenge.jpg",)]),
    dict(id="print", name="Зеркало черное худ. «Print»", role="black", fit=True, art="print", base="black_mirror",
         size=(1024, 4096), refs=[("p065_s-13-print__wenge-veralinga.jpg",)]),
    dict(id="stamp", name="Зеркало черное худ. «Stamp»", role="black", fit=True, art="stamp", base="black_mirror",
         size=(1024, 4096), refs=[("p065_s-13-stamp__wenge-veralinga.jpg",)]),
    dict(id="sa", name="Зеркало белое худож-е «Silver Art» (SA)", role="mirror", fit=False, gen="silver_art",
         base="frosted_white", size=(2048, 2048),
         refs=[("p033_porta-51-sa__cappuccino-crosscut.jpg", (157.0, 0.0, 299.0, 2000.0)),
               ("p049_vm4-sa__cappuccino-veralinga.jpg", (133.0, 250.0, 672.5, 1800.0))]),
    dict(id="wc", name="Белое худож-е сатинато White Crystal (WC)", role="satin", fit=False, gen="white_crystal",
         base="satin", size=(512, 1024),
         refs=[("p105_klasiko-13-wc__bez-otdelki.jpg", (158.0, 827.0, 642.0, 1858.5)),
               ("p045_klassiko-33-wc__organic-oak.jpg", (158.0, 827.0, 642.0, 1858.5))]),
    dict(id="mystic", name="Белое худож-е «Mystic»", role="satin", fit=True, art="mystic", base="satin",
         size=(1024, 2048), refs=[("p061_simpl-15-2-m__cappuccino-veralinga.jpg",),
                                  ("p061_simpl-15-2-m__wenge-veralinga.jpg",)]),
    # the small pane of Симпл-15.2 M: a design art role ("art:doorglass_mystic_small")
    dict(id="mystic-small", material="doorglass_mystic_small", catalog=False, name="Белое худож-е «Mystic» (узкое)",
         role="satin", fit=True, art="mystic-small", base="satin", size=(1024, 256),
         refs=[("p061_simpl-15-2-m__cappuccino-veralinga.jpg",)]),
    # no door photo shows it: the swatch of the 3D-Graf glass list is the Глейс TWIG blades frosted on a mirror
    dict(id="mirror-art", name="Зеркало белое худож-е", role="mirror", fit=True, art="twig", base="mirror",
         layer_roles={"paint": "frosted"}, size=(512, 4096), swatch="pdf/cat-6_3.jpg", refs=[]),
]


def material_id(g):
    return g.get("material") or "doorglass_" + g["id"].replace("-", "_")


def see_through(g):
    return BASES[g["base"]]["alpha"] < 1.0


# ------------------------------------------------------------------------------------------------ colour
def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float64) / 255.0


def srgb_to_linear(s):
    s = np.asarray(s, dtype=np.float64)
    return np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(v):
    v = np.clip(np.asarray(v, dtype=np.float64), 0.0, 1.0)
    return np.where(v <= 0.0031308, 12.92 * v, 1.055 * v ** (1 / 2.4) - 0.055)


def luma(rgb):
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


# ------------------------------------------------------------------------------------------------ vector renderer
class Canvas:
    """Coverage raster of a W x H mm area at (nx, ny) px (supersampled SS x SS); rows top-down (y = H at row 0).
    wrap: a tile - items are drawn again shifted by the tile size, so the result tiles."""

    def __init__(self, size_mm, size_px, wrap=False):
        self.W, self.H = size_mm
        self.nx, self.ny = size_px
        self.kx = self.nx * SS / self.W
        self.ky = self.ny * SS / self.H
        self.img = Image.new("L", (self.nx * SS, self.ny * SS), 0)
        self.draw = ImageDraw.Draw(self.img)
        self.wrap = wrap

    def _xy(self, pts, dx=0.0, dy=0.0):
        pts = np.asarray(pts, np.float64)
        return list(zip(((pts[:, 0] + dx) * self.kx).tolist(), ((self.H - pts[:, 1] - dy) * self.ky).tolist()))

    def _offsets(self, bbox):
        if not self.wrap:
            return [(0.0, 0.0)]
        x0, y0, x1, y1 = bbox
        return [(i * self.W, j * self.H) for i in (-1, 0, 1) for j in (-1, 0, 1)
                if x1 + i * self.W >= 0 and x0 + i * self.W <= self.W and y1 + j * self.H >= 0 and y0 + j * self.H <= self.H]

    def poly(self, rings, value=255):
        pts = np.asarray(rings[0], np.float64)
        bbox = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max())
        for dx, dy in self._offsets(bbox):
            self.draw.polygon(self._xy(rings[0], dx, dy), fill=value)
            for hole in rings[1:]:
                self.draw.polygon(self._xy(hole, dx, dy), fill=0)

    def stroke(self, pts, value=255):
        """Variable-width centre line [[x, y, w], ...], round joins and ends."""
        p = np.asarray(pts, np.float64)
        if len(p) == 1:
            p = np.vstack([p, p])
        r = p[:, 2].max()
        bbox = (p[:, 0].min() - r, p[:, 1].min() - r, p[:, 0].max() + r, p[:, 1].max() + r)
        for dx, dy in self._offsets(bbox):
            X = (p[:, 0] + dx) * self.kx
            Y = (self.H - p[:, 1] - dy) * self.ky
            R = p[:, 2] / 2
            for k in range(len(p) - 1):
                ax, ay, bx, by = X[k], Y[k], X[k + 1], Y[k + 1]
                if math.hypot(bx - ax, by - ay) < 1e-9:
                    continue
                nxm, nym = -(by - ay) / self.ky, (bx - ax) / self.kx      # normal in mm space
                nl = math.hypot(nxm, nym)
                nxm, nym = nxm / nl, nym / nl
                ra, rb = R[k], R[k + 1]
                self.draw.polygon([(ax + nxm * ra * self.kx, ay + nym * ra * self.ky),
                                   (bx + nxm * rb * self.kx, by + nym * rb * self.ky),
                                   (bx - nxm * rb * self.kx, by - nym * rb * self.ky),
                                   (ax - nxm * ra * self.kx, ay - nym * ra * self.ky)], fill=value)
            for k in range(len(p)):
                rx, ry = R[k] * self.kx, R[k] * self.ky
                if rx >= 0.25 or ry >= 0.25:
                    self.draw.ellipse([X[k] - rx, Y[k] - ry, X[k] + rx, Y[k] + ry], fill=value)

    def coverage(self):
        a = np.asarray(self.img)
        s = a.reshape(self.ny, SS, self.nx, SS).sum((1, 3), dtype=np.uint32)
        return s.astype(np.float32) / (255.0 * SS * SS)


def render_items(items, size_mm, size_px, wrap=False):
    cv = Canvas(size_mm, size_px, wrap)
    for it in items:
        if "poly" in it:
            cv.poly(it["poly"])
        elif "stroke" in it:
            cv.stroke(it["stroke"])
    cov = cv.coverage()
    cv.img.close()
    return cov


# ------------------------------------------------------------------------------------------------ pictures
class Picture:
    """Albedo (sRGB 0..1), opacity, metallic, smoothness and height (for the normal map) at the albedo resolution."""

    def __init__(self, size_px, base):
        w, h = size_px
        self.size = size_px
        self.rgb = np.ones((h, w, 3), np.float32) * hex_rgb(base["color"]).astype(np.float32)
        self.alpha = np.full((h, w), base["alpha"], np.float32)
        self.metallic = np.full((h, w), base["metallic"], np.float32)
        self.smooth = np.full((h, w), base["smooth"], np.float32)
        self.height = None

    def layer(self, cov, props, color=None):
        cov = cov.astype(np.float32)
        k = cov[..., None]
        c = hex_rgb(props["color"]) if color is None else color
        self.rgb = self.rgb * (1 - k) + c * k
        for name in ("alpha", "metallic", "smooth"):
            setattr(self, name, getattr(self, name) * (1 - cov) + props[name] * cov)


def layer_props(layer, overrides=None):
    role = (overrides or {}).get(layer["role"], layer["role"])
    props = dict(ROLES[role])
    if role == layer["role"]:                   # an overridden role keeps its own look
        for key in ("color", "alpha", "metallic", "smooth"):
            if key in layer:
                props[key] = layer[key]
    return props


def draw_art(pic, art, wrap=False, overrides=None):
    for layer in art["layers"]:
        props = layer_props(layer, overrides)
        cov = render_items(layer["items"], art["size"], pic.size, wrap)
        color = None
        if "tone" in layer and props["color"] == layer.get("color", props["color"]):
            base = hex_rgb(props["color"])
            im = Image.open(ART / layer["tone"]).convert("L").resize(pic.size, Image.BICUBIC)
            t = np.asarray(im, np.float64) / 255.0
            color = np.clip(base[None, None, :] * (t / max(luma(base), 1e-3))[..., None], 0, 1)
        pic.layer(cov, props, color)


def load_art(art_id):
    return json.loads((ART / f"{art_id}.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------------ generators
def white_crystal(size_px):
    """Белое худож-е сатинато White Crystal: satin with a lattice of clear lines forming rhombi 106.5 mm wide and
    157.9 mm tall (lines 34.0° from the vertical, 88.3 mm apart; measured on the Классико-13 / -33 renders, p105 and
    p045), 3 mm wide. One rhombus period per tile; a crossing sits on x = 400 mm of the 800 mm leaf (the pane's
    centre line of Классико-13 / -33) and at y = 62 mm mod 79 as on Классико-13."""
    W, H, LW = 106.5, 157.9, 3.0
    xc, yc = 400.0 % (W / 2), 62.2 % (H / 2)
    art = {"size": [W, H], "layers": [{"role": "clear", "items": []}]}
    items = art["layers"][0]["items"]
    for s in (1, -1):                              # x / W - s y / H = c + k through the crossing
        c = xc / W - s * yc / H
        for k in range(-3, 4):
            # the line x = W (c + k + s y / H) from y = -H .. 2H
            ys = np.array([-H, 2 * H])
            xs = W * (c + k + s * ys / H)
            items.append({"stroke": [[xs[0], ys[0], LW], [xs[1], ys[1], LW]]})
    return art, (W / 1000.0, H / 1000.0)


def silver_art(size_px, tile=(600.0, 600.0), seed=5105):
    """Зеркало белое худож-е «Silver Art»: a frosted (matt white) mirror with hand-scratched engraved lines (some with
    a hooked end), small zig-zag marks and polished mirror crescents (PORTA-51 SA, VETRO VM4 SA; swatch of p30).
    Scattered on a seamless tile with the statistics of the p033 render: ~0.035 mm of line per mm² (a vertical scan
    meets 0.028 lines per mm, a horizontal one 0.016: mostly within ±50° of the horizontal), lines 25..190 mm,
    ~30 crescents and ~35 marks per m²."""
    rng = np.random.default_rng(seed)
    W, H = tile
    lines, marks, crescents = [], [], []
    total, target = 0.0, 0.035 * W * H
    while total < target:
        r = rng.random()
        if r < 0.45:
            ang = rng.uniform(15, 55)                  # lower left -> upper right, the swatch's long strokes
        elif r < 0.8:
            ang = rng.normal(0, 14)                    # near horizontal
        else:
            ang = rng.uniform(-90, 90)
        L = float(np.clip(rng.lognormal(math.log(70), 0.5), 25, 190))
        t = math.radians(ang)
        u = np.array([math.cos(t), math.sin(t)])
        n = np.array([-u[1], u[0]])
        p0 = np.array([rng.uniform(0, W), rng.uniform(0, H)])
        bend = rng.normal(0, 0.06) * L
        s = np.linspace(0, 1, max(8, int(L / 3)))
        pts = p0 + np.outer(s * L, u) + np.outer(4 * s * (1 - s) * bend, n)
        if rng.random() < 0.3:                         # a hooked end: a short stroke turned back at 30..70°
            hl = rng.uniform(6, 16)
            ht = t + math.radians(rng.choice([-1, 1]) * rng.uniform(110, 150))
            hs = np.linspace(0, 1, 6)[1:]
            pts = np.vstack([pts, pts[-1] + np.outer(hs * hl, [math.cos(ht), math.sin(ht)])])
            s = np.linspace(0, 1, len(pts))
        w = rng.uniform(0.9, 1.3) * np.clip(np.minimum(s, 1 - s) / 0.1, 0.3, 1.0)
        lines.append(np.c_[pts, w])
        total += L
    for _ in range(int(35e-6 * W * H)):                # zig-zag marks, 2..3 strokes 8..14 mm
        c = np.array([rng.uniform(0, W), rng.uniform(0, H)])
        t = math.radians(rng.normal(-10, 25))
        u = np.array([math.cos(t), math.sin(t)])
        n = np.array([-u[1], u[0]])
        for j in range(rng.integers(2, 4)):
            L = rng.uniform(8, 14)
            s = np.linspace(0, 1, 16)
            pts = c + n * j * 2.4 + np.outer(s * L, u) + np.outer(1.3 * np.sin(s * math.pi * 3), n)
            marks.append(np.c_[pts, np.full(len(s), 0.8)])
    for _ in range(int(30e-6 * W * H)):                # polished crescents: circle arcs 35..80 mm, 3..5 mm thick
        R = rng.uniform(30, 70)
        a0 = rng.uniform(0, 2 * math.pi)
        span = math.radians(rng.uniform(50, 80))
        c = np.array([rng.uniform(0, W), rng.uniform(0, H)])
        a = np.linspace(a0, a0 + span, 40)
        pts = c + R * np.stack([np.cos(a), np.sin(a)], 1)
        s = np.linspace(0, 1, 40)
        w = rng.uniform(3.0, 5.0) * np.sin(math.pi * s ** 1.3) ** 0.8 + 0.2
        crescents.append(np.c_[pts, w])
    items_l = [{"stroke": np.round(l, 3).tolist()} for l in lines + marks]
    # engraved line: a grey groove with a white lit edge above it
    hi = [{"stroke": np.round(np.c_[l[:, :2] + np.array([-0.4, 0.5]), l[:, 2] * 0.55], 3).tolist()}
          for l in lines + marks]
    art = {"size": [W, H], "layers": [
        {"role": "frosted", "color": "#fdfcfa", "items": hi},
        {"role": "frosted", "color": "#aba9a5", "items": items_l},
        {"role": "mirror", "items": [{"stroke": np.round(c, 3).tolist()} for c in crescents]}]}
    return art, (W / 1000.0, H / 1000.0)


GENERATORS = dict(white_crystal=white_crystal, silver_art=silver_art)


def build(g):
    """-> (Picture, art, metersPerTile)."""
    base = BASES[g["base"]]
    pic = Picture(g["size"], base)
    if "art" in g:
        art = load_art(g["art"])
        draw_art(pic, art, False, g.get("layer_roles"))
        tile = (1.0, 1.0)
    else:
        art, tile = GENERATORS[g["gen"]](g["size"])
        draw_art(pic, art, True)
        if g["gen"] == "silver_art":               # engraved grooves for the normal map
            cov = render_items(art["layers"][1]["items"], art["size"], pic.size, True)
            pic.height = -cov
    return pic, art, tile


# ------------------------------------------------------------------------------------------------ output
def normal_png(height, px_mm, depth_mm=0.25):
    """OpenGL normal map of a periodic height field (0..1 = depth_mm)."""
    h = height * depth_mm
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) / 2 * px_mm[0]
    gr = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) / 2 * px_mm[1]
    n = np.stack([-gx, gr, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.round((n * 0.5 + 0.5) * 255).astype(np.uint8)


def write_glass(g, pic, tile):
    mid = material_id(g)
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    rgb = np.round(np.clip(pic.rgb, 0, 1) * 255).astype(np.uint8)
    tex = {}
    if see_through(g):
        a = np.round(np.clip(pic.alpha, 0, 1) * 255).astype(np.uint8)
        Image.fromarray(np.dstack([rgb, a]), "RGBA").save(folder / f"{mid}_albedo.png", optimize=True)
        tex["albedo"] = f"{mid}_albedo.png"
    else:
        Image.fromarray(rgb).save(folder / f"{mid}_albedo.jpg", quality=95, subsampling=0, optimize=True)
        tex["albedo"] = f"{mid}_albedo.jpg"
    if pic.height is not None:
        W, H = (tile[0] * 1000, tile[1] * 1000) if not g.get("fit") else (1, 1)
        px_mm = (pic.size[0] / W, pic.size[1] / H)
        Image.fromarray(normal_png(pic.height, px_mm)).save(folder / f"{mid}_normal.png", optimize=True)
        tex["normal"] = f"{mid}_normal.png"
    m = np.zeros(pic.alpha.shape + (4,), np.uint8)
    m[..., 0] = np.round(np.clip(pic.metallic, 0, 1) * 255)
    m[..., 1] = 255
    m[..., 3] = np.round(np.clip(pic.smooth, 0, 1) * 255)
    Image.fromarray(m, "RGBA").save(folder / f"{mid}_mask.png", optimize=True)
    tex["mask"] = f"{mid}_mask.png"
    for old in folder.glob(f"{mid}_*"):             # a format switch (png <-> jpg) leaves no stale file
        if old.name not in tex.values() and old.suffix != ".meta":
            old.unlink()
    return tex


def entry(g, tex, tile):
    e = {"id": material_id(g), "name": g["name"], "category": "doorglass", "source": SOURCE, "neutral": False,
         "metersPerTile": [round(tile[0], 4), round(tile[1], 4)], "maxSize": max(g["size"]),
         "folder": f"Materials/{material_id(g)}", "textures": tex}
    if see_through(g):
        e["transparent"] = True
    return e


def glass_def(g):
    d = {"id": g["id"], "name": g["name"], "role": g["role"], "material": material_id(g)}
    if g.get("fit"):
        d["fit"] = True
    return d


def write_catalog(entries):
    ENTRIES.parent.mkdir(parents=True, exist_ok=True)
    ENTRIES.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    defs = [glass_def(g) for g in GLASS if g.get("catalog", True)]
    GLASS_JSON.parent.mkdir(parents=True, exist_ok=True)
    GLASS_JSON.write_text("[\n" + ",\n".join("  " + json.dumps(d, ensure_ascii=False) for d in defs) + "\n]\n",
                          encoding="utf-8")


# ------------------------------------------------------------------------------------------------ check sheet
PHOTO_MM = 2080.0


def leaf_of(fname):
    """Leaf bounds of a catalogue photo (tools/doors/measure.py)."""
    sys.path.insert(0, str(ROOT / "tools" / "doors"))
    import measure
    _, grey = measure.load_photo(CACHE / "photos" / fname)
    return measure.find_leaf(grey)


def shade(pic_rgb, alpha, metallic, env=0.30, bg=1.0):
    """How the catalogue renders show it: see-through glass over a white studio, metal reflecting a dim room."""
    lin = srgb_to_linear(pic_rgb)
    m = metallic[..., None]
    lin = lin * (1 - m) + lin * env * m
    rgb = linear_to_srgb(lin)
    a = alpha[..., None]
    return rgb * a + bg * (1 - a)


def shaded(pic):
    img = shade(pic.rgb, pic.alpha, pic.metallic)
    return Image.fromarray(np.round(np.clip(img, 0, 1) * 255).astype(np.uint8))


def view_of(g, im, pane, box, ppm):
    """The shaded picture im over leaf box (x0, y0, x1, y1 mm) at ppm px/mm; fit: pane = the picture's leaf rect."""
    x0, y0, x1, y1 = box
    size = (max(1, int(round((x1 - x0) * ppm))), max(1, int(round((y1 - y0) * ppm))))
    if g.get("fit"):
        px, py, qx, qy = pane
        sx, sy = im.width / (qx - px), im.height / (qy - py)
        pad = 256                                      # boxes may reach past the pane
        big = Image.new("RGB", (im.width + 2 * pad, im.height + 2 * pad), (200, 200, 200))
        big.paste(im, (pad, pad))
        return big.resize(size, Image.LANCZOS, box=((x0 - px) * sx + pad, (qy - y1) * sy + pad, (x1 - px) * sx + pad,
                                                     (qy - y0) * sy + pad))
    tw, th = g["tile"][0] * 1000.0, g["tile"][1] * 1000.0
    k0, k1 = int(math.floor(x0 / tw)), int(math.floor(x1 / tw))
    j0, j1 = int(math.floor(y0 / th)), int(math.floor(y1 / th))
    a = np.asarray(im)
    big = np.tile(a, (j1 - j0 + 1, k1 - k0 + 1, 1))
    bi = Image.fromarray(big)
    sx, sy = im.width / tw, im.height / th
    top = (j1 + 1) * th
    return bi.resize(size, Image.LANCZOS, box=((x0 - k0 * tw) * sx, (top - y1) * sy, (x1 - k0 * tw) * sx,
                                               (top - y0) * sy))


def photo_view(fname, box, ppm, leaf):
    im = Image.open(CACHE / "photos" / fname).convert("RGB")
    x0, y0, x1, y1 = box
    X0, X1 = leaf["x0"] + x0 * leaf["sx"], leaf["x0"] + x1 * leaf["sx"]
    Y0, Y1 = leaf["y1"] - y1 * leaf["sy"], leaf["y1"] - y0 * leaf["sy"]
    size = (max(1, int(round((x1 - x0) * ppm))), max(1, int(round((y1 - y0) * ppm))))
    pad = 64                                           # boxes may run past the photo (cropped above the floor)
    big = Image.new("RGB", (im.width + 2 * pad, im.height + 2 * pad), "white")
    big.paste(im, (pad, pad))
    return big.resize(size, Image.LANCZOS, box=(X0 + pad, Y0 + pad, X1 + pad, Y1 + pad))


def compare(glasses, pics, out_path):
    """Per glass: the catalogue photo's pane | the picture at the same scale (enlarged alike) | a detail of each."""
    blocks = []
    PH = 900                                           # height of the whole-pane views, px
    for g in glasses:
        pic, art = pics[g["id"]]
        pane = art.get("pane") if g.get("fit") else None
        cols = []
        label = "%s  %s  (%s)" % (g["id"], material_id(g), "fit" if g.get("fit") else
                                   "tile %.0f x %.0f mm" % (g["tile"][0] * 1000, g["tile"][1] * 1000))
        ref = g["refs"][0] if g["refs"] else None
        if ref:
            fname = ref[0]
            box = tuple(ref[1]) if len(ref) > 1 else tuple(pane)
            leaf = leaf_of(fname)
            ppm = PH / (box[3] - box[1])
            ppm = min(ppm, 520 / (box[2] - box[0]))
            cols += [photo_view(fname, box, ppm, leaf), view_of(g, pic, pane, box, ppm)]
            # detail: a 300 px tall window around the middle of the pane at 4x the photo scale
            ph_ppm = leaf["sy"]
            z = 4 * ph_ppm if ph_ppm > 0.3 else 8 * ph_ppm
            wmm, hmm = min(box[2] - box[0], 360 / z), min(box[3] - box[1], 320 / z)
            cx = (box[0] + box[2]) / 2
            cy = min(max(box[1] + (box[3] - box[1]) * g.get("detail", 0.62), box[1] + hmm / 2), box[3] - hmm / 2)
            dbox = (cx - wmm / 2, cy - hmm / 2, cx + wmm / 2, cy + hmm / 2)
            cols += [photo_view(fname, dbox, z, leaf), view_of(g, pic, pane, dbox, z)]
            note = "photo %s (%.2f px/mm)   |  picture same scale  |  detail x%.0f: photo | picture" % (
                fname.split("__")[0], ph_ppm, z / ph_ppm)
        else:
            sw = Image.open(CACHE / g["swatch"]).convert("RGB")
            cols.append(sw.resize((sw.width * 6, sw.height * 6), Image.LANCZOS))
            ppm = PH / (pane[3] - pane[1])
            cols.append(view_of(g, pic, pane, tuple(pane), ppm))
            cols.append(view_of(g, pic, pane, (pane[0], pane[1] + 1400, pane[2], pane[1] + 1900), 1.6))
            note = "no door photo: the catalogue swatch x6 | picture on the Глейс-1 pane | detail"
        w = sum(c.width for c in cols) + 12 * (len(cols) - 1)
        blk = Image.new("RGB", (max(w, 420), max(c.height for c in cols) + 40), "white")
        d = ImageDraw.Draw(blk)
        d.text((2, 2), label, fill="black")
        d.text((2, 18), note, fill=(70, 70, 70))
        x = 0
        for c in cols:
            blk.paste(c, (x, 40))
            x += c.width + 12
        blocks.append(blk)
    # rows of blocks, 2600 px wide
    rows, row, rw = [], [], 0
    for b in blocks:
        if row and rw + b.width > 2600:
            rows.append(row)
            row, rw = [], 0
        row.append(b)
        rw += b.width + 30
    rows.append(row)
    W = max(sum(b.width + 30 for b in r) for r in rows)
    H = sum(max(b.height for b in r) + 30 for r in rows) + 30
    sheet = Image.new("RGB", (W, H), (236, 236, 236))
    ImageDraw.Draw(sheet).text((6, 6), "Door art glass vs the catalogue (tools/doors/textures/art_glass.py): see-through "
                                       "glass shown over white, mirrors reflecting a dim room", fill="black")
    y = 30
    for r in rows:
        x = 0
        for b in r:
            sheet.paste(b, (x, y))
            x += b.width + 30
        y += max(b.height for b in r) + 30
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    print("check sheet", out_path)


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("glass", nargs="*", help="glass ids (default: all)")
    ap.add_argument("--compare", action="store_true", help="write tools/doors/.cache/glass_art.png")
    ap.add_argument("--no-write", action="store_true", help="do not write textures / entries / Glass/art.json")
    ap.add_argument("--sheet", default=str(CACHE / "glass_art.png"))
    args = ap.parse_args()
    todo = [g for g in GLASS if not args.glass or g["id"] in args.glass]
    if args.glass and len(todo) != len(args.glass):
        sys.exit("unknown glass: " + ", ".join(set(args.glass) - {g["id"] for g in GLASS}))
    pics, entries = {}, {}
    if ENTRIES.exists():
        entries = {e["id"]: e for e in json.loads(ENTRIES.read_text(encoding="utf-8"))}
    for g in todo:
        pic, art, tile = build(g)
        g["tile"] = tile
        if args.compare:
            pics[g["id"]] = (shaded(pic), art)
        if not args.no_write:
            tex = write_glass(g, pic, tile)
            entries[material_id(g)] = entry(g, tex, tile)
            print("glass", g["id"], "->", material_id(g), "x".join(map(str, g["size"])))
        del pic
    if not args.no_write:
        order = [material_id(g) for g in GLASS]
        write_catalog([entries[m] for m in order if m in entries])
        print("entries", ENTRIES, "| glass", GLASS_JSON)
    if args.compare:
        compare(todo, pics, Path(args.sheet))


if __name__ == "__main__":
    main()
