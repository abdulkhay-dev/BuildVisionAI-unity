"""Draw a door design (Docs/door-designs.md) in 2D - the reference interpretation of the design format.

    python3 tools/doors/preview2d.py <design> --out <png> [--size 700x2000] [--scale 0.8] [--glass black]
    python3 tools/doors/preview2d.py <design> --photo <file> [--photo <file> ...] --out <png>
                                    [--check] [--zoom X0,Y0,X1,Y1] [--bounds X0,Y0,X1,Y1] [--bottom Y1]
    python3 tools/doors/preview2d.py porta-22 --photos-of ПОРТА-22 --pages 9-11,19-27 --check --out <png>
    python3 tools/doors/preview2d.py <design> [<design> ...] --sheet [--widths 600,800,900] --out <png>

<design> is a path or a design id (Assets/House4696/Resources/Doors/Designs/<id>.json); <file> a path or a file
name inside tools/doors/.cache/photos. --photos-of adds every photo of the catalogue index (.cache/index.json, see
catalog_index.py) whose caption is that model (any glass/finish suffix; 'ПОРТА-2' does not match 'ПОРТА-22'),
optionally only from the catalogue pages --pages; the biggest photo comes first (it is the one drawn).
Needs numpy + Pillow (and measure.py next to this file for photos).

Layout semantics implemented here (the generator must match them):
  * Coordinates are ref mm (origin bottom-left of the leaf as the photo shows it, x = 0 the lock edge, y up).
  * Resizing: along each axis a coordinate maps through fixX / fixY - fixed intervals keep their length (and move),
    the rest of the axis stretches proportionally (piecewise-linear map M).
  * A split node cuts its rectangle at the absolute positions "at", mapped through M (and fitted linearly onto the
    node's actual extent when that differs from M of its ref extent, which only happens under the thin rule).
    Cells with a ref size < 60 mm along the split axis keep that size: a run of consecutive thin cells keeps its
    total size and is centred on M(ref centre of the run); a thin run touching the node's start or end stays
    anchored to it. The cuts next to a thin run move with it.
  * Separators are centred on their cut, never scale, and are painted over the two neighbouring cells
    (joint = hairline, none = no seam, glass:W / black:W / mirror:W / clear:W = strip of glass, metal:W[:P] =
    aluminium strip, groove:W:D = milled groove).
  * level / grain / radius / material / glass are inherited down the tree; a leaf node of the tree is a piece (a
    glass pane when its "glass" is true or a glass role).
  * Parts: shapes map through M; a part (bounding box) thinner than 60 mm along an axis keeps its size along it
    (its centre moves). The drawing shows rect / ellipse / arch parts as their boxes (paths are not drawn yet).
  * Handle: keeps its height above the bottom and its distance from the lock edge. Hinges keep their distance to
    the nearer end of the leaf.

Drawing (to compare with the catalogue renders, which are lit from the upper left; neutral wood tone so that every
level and joint stays readable): pieces tinted by grain and level (-3 darker), grain as faint streaks, a joint as a
dark hairline on its upper/left side and a lit one on its lower/right side, a level step as a dark edge + cast shadow
where the higher piece is above/left of the lower one and a lit edge where it is below/right, glass white (satin) /
black / mirror / clear, metal grey, a groove as a shaded channel.

--photo: finds the leaf in the photo (measure.find_leaf), resamples it to the drawing scale and writes
photo | design | overlay (design lines dashed over the photo: green = cuts/joints/steps, magenta = glass edges,
blue = metal, orange = grooves; the leaf bounds green, handle axis and hinge centres magenta).
--check measures every design line on every --photo and prints the offset of the photo's line from the design's
(mm, and px of that photo; + = the photo's line is right of / above the design's). The line of a cut is split into
segments by the pieces on both sides; the rule of a segment follows what the render shows there:
    joint       same level: midpoint of the dark hairline (upper/left piece) and the lit one right after it,
                or the dark hairline + 1 mm when the lit one is lost in a light finish
    step-dark   the higher piece above/left (also wood above/left of glass): where the dark band (its rounded edge
                + the cast shadow) starts on the higher piece's side, + 1 mm
    step-lit    the higher piece below/right: midpoint of the dark line just before its lit edge and the lit edge,
                or the lit edge's leading half-level crossing
    glass-edge  wood below glass: half-level crossing between wood and glass
    glass-edge-r  wood right of glass: its lit edge is as bright as the glass - reported, not counted
    strip-start / strip-end   edges of a glass/metal strip: half-level crossings
    groove-lit / groove-dark  edges of a groove: the lit / dark rounded board edge
Segments shorter than 15 mm are not measured. The last column is the offset averaged over the photos (weights
(px/mm)^2, mismatches > 3 px left out). Then, per cut, the pooled offset and the suggested ref position (big photos
only when there is one: the blur of the small ones biases the rules by 0.5-1 px), and for strips the measured width.
--zoom X0,Y0,X1,Y1 (mm) also writes <out>-zoom.png: that region of the first photo enlarged (nearest neighbour,
--zoom-scale px/mm, levels stretched) with the design lines.
--sheet renders every design at each of --widths (height --height, default 2000), --per-row designs a row.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DESIGNS = ROOT / "Assets/House4696/Resources/Doors/Designs"
THIN = 60.0
EPS = 1e-6

GLASS_RGB = {"satin": (243, 238, 232), "black": (22, 22, 24), "mirror": (200, 210, 216), "clear": (214, 234, 240)}
METAL_RGB = (165, 168, 172)
CHROME_RGB = (212, 216, 220)
BASE_RGB = (192, 163, 132)   # neutral mid wood: every level / joint stays readable


# ------------------------------------------------------------------------------------------------------ design files

def load_design(arg):
    p = Path(arg)
    if not p.exists():
        p = DESIGNS / (arg if arg.endswith(".json") else arg + ".json")
    if not p.exists():
        raise SystemExit(f"design not found: {arg} (a path or an id in {DESIGNS})")
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"^\s*//.*$", "", text, flags=re.M)  # tolerate // comment lines
    d = json.loads(text)
    d.setdefault("ref", [800, 2000])
    return d


# ------------------------------------------------------------------------------------------------------ resizing maps

class AxisMap:
    """Piecewise-linear map of one axis: fixed intervals keep their length, the rest stretches proportionally."""

    def __init__(self, fixed, ref_len, new_len):
        iv = sorted([max(0.0, float(a)), min(float(ref_len), float(b))] for a, b in (fixed or []) if b > a)
        merged = []
        for a, b in iv:
            if merged and a <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        fixed_len = sum(b - a for a, b in merged)
        free = ref_len - fixed_len
        if free <= EPS:
            if abs(new_len - ref_len) > EPS:
                raise ValueError("the whole axis is fixed: it cannot be resized")
            k = 1.0
        else:
            k = (new_len - fixed_len) / free
            if k <= 0:
                raise ValueError(f"size {new_len:g} is not larger than the fixed parts ({fixed_len:g})")
        self.k = k
        pts = [(0.0, 0.0)]
        x = y = 0.0
        for a, b in merged:
            y += (a - x) * k
            pts.append((a, y))
            y += b - a
            pts.append((b, y))
            x = b
        y += (ref_len - x) * k
        pts.append((float(ref_len), y))
        self.pts = pts

    def __call__(self, v):
        pts = self.pts
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if v <= x1:
                return y0 + (v - x0) * ((y1 - y0) / (x1 - x0) if x1 > x0 else 1.0)
        return pts[-1][1] + (v - pts[-1][0])


# ------------------------------------------------------------------------------------------------------------ layout

INHERITED = ("level", "grain", "radius", "material", "glass")
DEFAULTS = dict(level=0, grain="v", radius=1.5, material="finish", glass=False)


def parse_sep(s):
    """'joint' | 'none' | 'glass:10' | 'metal:4:1' | 'groove:6:3' -> dict(kind, width, extra, spec)."""
    parts = str("joint" if s is None else s).split(":")
    return dict(kind=parts[0], width=float(parts[1]) if len(parts) > 1 else 0.0,
                extra=float(parts[2]) if len(parts) > 2 else 0.0, spec=":".join(parts))


class Layout:
    """A design laid out at a leaf size: pieces, separators, parts (all in mm of that size)."""

    def __init__(self, design, width=None, height=None):
        self.d = design
        rw, rh = design["ref"]
        self.W = float(width or rw)
        self.H = float(height or rh)
        self.mx = AxisMap(design.get("fixX"), rw, self.W)
        self.my = AxisMap(design.get("fixY"), rh, self.H)
        self.pieces = []  # dict(rect=(x0, y0, x1, y1), props, path)
        self.seps = []    # dict(axis, pos, rect, span, sep, path)   axis 'x' = vertical cut line at x = pos
        self._node(design.get("layout") or {}, (0.0, 0.0, float(rw), float(rh)), (0.0, 0.0, self.W, self.H),
                   dict(DEFAULTS), "layout")
        self.parts = [self._part(p) for p in design.get("parts", [])]

    def _node(self, node, ref, new, inh, path):
        props = dict(inh)
        for k in INHERITED:
            if k in node:
                props[k] = node[k]
        if "split" not in node:
            self.pieces.append(dict(rect=new, props=props, path=path))
            return
        axis = node["split"]
        cuts = [float(c) for c in node["at"]]
        n = len(cuts)
        cells = node.get("cells") or [{} for _ in range(n + 1)]
        seps = node.get("sep", "joint")
        seps = seps if isinstance(seps, list) else [seps] * n
        if len(cells) != n + 1 or len(seps) != n:
            raise ValueError(f"{path}: {n} cuts need {n + 1} cells and {n} separators")
        i0 = 0 if axis == "x" else 1
        lo_r, hi_r, lo_n, hi_n = ref[i0], ref[i0 + 2], new[i0], new[i0 + 2]
        if cuts != sorted(cuts) or any(not (lo_r < c < hi_r) for c in cuts):
            raise ValueError(f"{path}: cuts {cuts} must ascend strictly inside {lo_r:g}..{hi_r:g}")
        m = self.mx if axis == "x" else self.my
        a, b = m(lo_r), m(hi_r)
        if abs(a - lo_n) < EPS and abs(b - hi_n) < EPS:
            f = m
        else:  # the node itself moved/kept its size (thin rule above): fit M onto its actual extent
            f = lambda v: lo_n + (m(v) - a) * (hi_n - lo_n) / (b - a)
        br = [lo_r] + cuts + [hi_r]
        bn = [lo_n] + [f(c) for c in cuts] + [hi_n]
        thin = [br[i + 1] - br[i] < THIN for i in range(n + 1)]
        i = 0
        while i <= n:
            if not thin[i]:
                i += 1
                continue
            j = i
            while j < n and thin[j + 1]:
                j += 1
            if not (i == 0 and j == n):
                size = br[j + 1] - br[i]
                start = bn[0] if i == 0 else bn[n + 1] - size if j == n else f((br[i] + br[j + 1]) / 2) - size / 2
                for k in range(max(1, i), min(n, j + 1) + 1):
                    bn[k] = start + (br[k] - br[i])
            i = j + 1
        if any(bn[k + 1] < bn[k] - EPS for k in range(n + 1)):
            raise ValueError(f"{path}: the leaf is too small for this layout (cells overlap)")
        for k, cell in enumerate(cells):
            r, nn = list(ref), list(new)
            r[i0], r[i0 + 2] = br[k], br[k + 1]
            nn[i0], nn[i0 + 2] = bn[k], bn[k + 1]
            self._node(cell or {}, tuple(r), tuple(nn), props, f"{path}.cells[{k}]")
        for k in range(n):
            sp = parse_sep(seps[k])
            pos, w2 = bn[k + 1], sp["width"] / 2
            if axis == "x":
                rect, span = (pos - w2, new[1], pos + w2, new[3]), (new[1], new[3])
            else:
                rect, span = (new[0], pos - w2, new[2], pos + w2), (new[0], new[2])
            self.seps.append(dict(axis=axis, pos=pos, ref_pos=cuts[k], rect=rect, span=span, sep=sp,
                                  path=f"{path}.at[{k}]"))

    def _part(self, part):
        shape = part.get("shape") or {}
        out = dict(part)
        if "rect" in shape:
            out["box"] = self.map_box(*shape["rect"])
        elif "ellipse" in shape:
            cx, cy, rx, ry = shape["ellipse"]
            out["box"] = self.map_box(cx - rx, cy - ry, cx + rx, cy + ry)
        elif "arch" in shape:
            x0, y0, x1, y1 = shape["arch"]
            out["box"] = self.map_box(x0, y0, x1, y1 + shape.get("rise", 0))
        return out

    def map_box(self, x0, y0, x1, y1):
        def one(m, a, b):
            if b - a < THIN:
                c = m((a + b) / 2)
                return c - (b - a) / 2, c + (b - a) / 2
            return m(a), m(b)
        a, b = one(self.mx, x0, x1)
        c, d = one(self.my, y0, y1)
        return (a, c, b, d)

    def segments(self, s):
        """Pieces on both sides of separator s along its span.
        -> [(a, b, piece_before, piece_after)]; before = the lower/left side."""
        i0 = 0 if s["axis"] == "x" else 1   # coordinate across the line
        j0 = 1 - i0                          # coordinate along the line
        pos = s["pos"]
        a, b = s["span"]
        before = [p for p in self.pieces if abs(p["rect"][i0 + 2] - pos) < 1e-4
                  and p["rect"][j0] < b - EPS and p["rect"][j0 + 2] > a + EPS]
        after = [p for p in self.pieces if abs(p["rect"][i0] - pos) < 1e-4
                 and p["rect"][j0] < b - EPS and p["rect"][j0 + 2] > a + EPS]
        brk = sorted({a, b} | {min(max(p["rect"][j0 + e], a), b) for p in before + after for e in (0, 2)})
        out = []
        for u, v in zip(brk, brk[1:]):
            if v - u < EPS:
                continue
            mid = (u + v) / 2
            pb = next((p for p in before if p["rect"][j0] <= mid <= p["rect"][j0 + 2]), None)
            pa = next((p for p in after if p["rect"][j0] <= mid <= p["rect"][j0 + 2]), None)
            if out and out[-1][2] is pb and out[-1][3] is pa:
                out[-1] = (out[-1][0], v, pb, pa)
            else:
                out.append((u, v, pb, pa))
        return out

    def handle(self):
        h = self.d.get("handle")
        return (float(h.get("x", 60)), float(h.get("y", 1000))) if h else None

    def hinges(self):
        rh = self.d["ref"][1]
        return [y if y < rh / 2 else self.H - (rh - y) for y in self.d.get("hinges", [250, rh - 250])]


def _level(p):
    return None if p is None else float(p["props"].get("level", 0))


def _is_glass(p):
    return p is not None and bool(p["props"].get("glass"))


def seg_rule(s, pb, pa):
    """Rule of a line segment between piece pb (lower/left) and pa (upper/right) at separator s (width 0).

    Glass counts as the lowest level: wood above/left of glass shows its shadowed edge (step-dark); wood below
    glass shows as a plain half-level edge (glass-edge); wood right of glass has a lit edge as bright as the
    glass, so that edge cannot be located well (glass-edge-r, reported but not counted in the worst offset)."""
    gb, ga = _is_glass(pb), _is_glass(pa)
    if gb and ga:
        return None
    if gb or ga:
        wood_first = ga        # the wood is the lower/left piece
        if s["axis"] == "y":
            return "glass-edge" if wood_first else "step-dark"
        return "step-dark" if wood_first else "glass-edge-r"
    lb, la = _level(pb), _level(pa)
    if lb is None or la is None or lb == la:
        return "joint" if s["sep"]["kind"] != "none" else None
    if s["axis"] == "y":   # pb below, pa above
        return "step-lit" if lb > la else "step-dark"
    return "step-dark" if lb > la else "step-lit"   # pb left, pa right


def design_lines(lay):
    """Every line of the design the photo should show: dict(axis, pos, span, kind, rule, label, glass_side)."""
    lines = []
    for s in lay.seps:
        sp = s["sep"]
        if sp["width"] > 0:
            for edge, pos in (("start", s["pos"] - sp["width"] / 2), ("end", s["pos"] + sp["width"] / 2)):
                rule = "strip-" + edge
                if sp["kind"] == "groove":
                    # the boards' rounded edges: lower board's top edge lit, upper board's bottom edge dark;
                    # left board's right edge dark, right board's left edge lit
                    lit = (edge == "start") == (s["axis"] == "y")
                    rule = "groove-lit" if lit else "groove-dark"
                lines.append(dict(axis=s["axis"], pos=pos, span=s["span"], kind=sp["kind"], rule=rule,
                                  label=f"{s['path']} {sp['spec']} {edge}", ref=s["ref_pos"], cut=s["path"],
                                  width=sp["width"]))
            continue
        for a, b, pb, pa in lay.segments(s):
            rule = seg_rule(s, pb, pa)
            if rule is None:
                continue
            lines.append(dict(axis=s["axis"], pos=s["pos"], span=(a, b), kind=sp["kind"], rule=rule,
                              glass_side=-1 if _is_glass(pb) else 1, ref=s["ref_pos"], cut=s["path"],
                              label=f"{s['path']} {sp['spec']} [{a:.0f}..{b:.0f}]"))
    return lines


# ------------------------------------------------------------------------------------------------------------ drawing

def _font(size):
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def glass_rgb(role, door_glass):
    if role is True or role in ("glass", None):
        role = door_glass
    if isinstance(role, str) and role.startswith("lacobel:"):
        h = role.split(":")[1].lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return GLASS_RGB.get(role, GLASS_RGB["satin"])


def render(lay, scale, base_rgb=BASE_RGB, door_glass="satin", finish2_rgb=(110, 90, 75)):
    """RGB image of the leaf at `scale` px per mm (image up = design up)."""
    W, H = lay.W, lay.H
    wpx, hpx = int(round(W * scale)), int(round(H * scale))
    img = np.zeros((hpx, wpx, 3), float)
    level = np.full((hpx, wpx), -99.0)
    rng = np.random.default_rng(7)

    def px(x0, y0, x1, y1):
        c0, c1 = int(round(x0 * scale)), int(round(x1 * scale))
        r0, r1 = int(round((H - y1) * scale)), int(round((H - y0) * scale))
        return max(0, r0), min(hpx, r1), max(0, c0), min(wpx, c1)

    base = np.array(base_rgb, float)
    mats = {"finish": base, "finish2": np.array(finish2_rgb, float), "metal": np.array(METAL_RGB, float),
            "chrome": np.array(CHROME_RGB, float), "black": np.array((25, 25, 27), float)}
    for p in lay.pieces:
        pr = p["props"]
        r0, r1, c0, c1 = px(*p["rect"])
        if r1 <= r0 or c1 <= c0:
            continue
        if pr.get("glass"):
            img[r0:r1, c0:c1] = glass_rgb(pr["glass"], door_glass)
            continue
        mat = pr.get("material", "finish")
        col = mats.get(mat, base)
        lv = float(pr.get("level", 0))
        tint = (1.0 + 0.06 * lv) * (0.95 if pr.get("grain") == "h" else 1.0)
        block = np.ones((r1 - r0, c1 - c0, 1)) * col * tint
        if mat in ("finish", "finish2"):
            amp = 0.05 * max(40.0, float(col.mean()))
            if pr.get("grain") == "h":
                streak = rng.normal(0, amp, (r1 - r0, 1)) + rng.normal(0, amp / 3, (r1 - r0, c1 - c0))
            else:
                streak = rng.normal(0, amp, (1, c1 - c0)) + rng.normal(0, amp / 3, (r1 - r0, c1 - c0))
            block = block + streak[..., None]
        img[r0:r1, c0:c1] = block
        level[r0:r1, c0:c1] = lv

    # level steps (light from the upper left): the lower piece gets a cast shadow under / right of a higher one;
    # the higher piece's rounded edge is dark where it faces down/right and lit where it faces up/left
    def shifted(dy, dx):
        out = np.full_like(level, -99.0)
        ys = slice(max(dy, 0), hpx + min(dy, 0))
        yd = slice(max(-dy, 0), hpx + min(-dy, 0))
        xs = slice(max(dx, 0), wpx + min(dx, 0))
        xd = slice(max(-dx, 0), wpx + min(-dx, 0))
        out[ys, xs] = level[yd, xd]
        return out

    valid = level > -99
    shade = np.zeros((hpx, wpx))
    sh = max(1, int(round(3 * scale)))
    for d in range(1, sh + 1):
        wgt = 0.5 * (1 - (d - 1) / sh)
        higher = (shifted(d, 0) > level) | (shifted(0, d) > level)   # the piece d px above / left is higher
        shade = np.maximum(shade, (higher & valid) * wgt)
    img *= (1 - shade)[..., None]
    rim = max(1, int(round(1.5 * scale)))
    for d in range(1, rim + 1):
        below, right = shifted(-d, 0), shifted(0, -d)                 # level d px below / right
        above, left = shifted(d, 0), shifted(0, d)
        dark = valid & (((below < level) & (below > -99)) | ((right < level) & (right > -99)))
        lit = valid & (((above < level) & (above > -99)) | ((left < level) & (left > -99)))
        img[dark] *= 0.6
        img[lit] = np.minimum(255, img[lit] * 1.25 + 20)

    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    X = lambda x: x * scale
    Y = lambda y: (H - y) * scale
    hair = max(1, int(round(1.2 * scale)))
    dark_c, lite_c = tuple(int(c * 0.5) for c in base), tuple(min(255, int(c * 1.25 + 20)) for c in base)
    for s in lay.seps:
        sp = s["sep"]
        kind = sp["kind"]
        x0, y0, x1, y1 = s["rect"]
        if kind == "joint":
            for a, b, pb, pa in lay.segments(s):
                if seg_rule(s, pb, pa) != "joint":
                    continue
                if s["axis"] == "y":
                    y = Y(s["pos"])
                    d.rectangle([X(a), y - hair, X(b) - 1, y - 1], fill=dark_c)
                    d.rectangle([X(a), y, X(b) - 1, y + hair - 1], fill=lite_c)
                else:
                    x = X(s["pos"])
                    d.rectangle([x - hair, Y(b), x - 1, Y(a) - 1], fill=dark_c)
                    d.rectangle([x, Y(b), x + hair - 1, Y(a) - 1], fill=lite_c)
        elif kind in ("glass", "black", "mirror", "clear") or kind.startswith("lacobel"):
            role = True if kind == "glass" else (sp["spec"].split(":")[0] if kind != "lacobel" else sp["spec"])
            d.rectangle([X(x0), Y(y1), X(x1) - 1, Y(y0) - 1], fill=glass_rgb(role, door_glass))
        elif kind == "metal":
            d.rectangle([X(x0), Y(y1), X(x1) - 1, Y(y0) - 1], fill=METAL_RGB)
        elif kind == "groove":
            # a channel between the pieces: its floor in shade, the edge above/left dark, below/right lit
            d.rectangle([X(x0), Y(y1), X(x1) - 1, Y(y0) - 1], fill=tuple(int(c * 0.72) for c in base))
            if s["axis"] == "y":
                d.rectangle([X(x0), Y(y1), X(x1) - 1, Y(y1) + hair - 1], fill=dark_c)
                d.rectangle([X(x0), Y(y0) - hair, X(x1) - 1, Y(y0) - 1], fill=lite_c)
            else:
                d.rectangle([X(x0), Y(y1), X(x0) + hair - 1, Y(y0) - 1], fill=dark_c)
                d.rectangle([X(x1) - hair, Y(y1), X(x1) - 1, Y(y0) - 1], fill=lite_c)
    for p in lay.parts:
        if "box" not in p:
            continue
        x0, y0, x1, y1 = p["box"]
        fill = {"glass": glass_rgb(p.get("role", True), door_glass), "inlay": METAL_RGB}.get(p.get("type"))
        d.rectangle([X(x0), Y(y1), X(x1) - 1, Y(y0) - 1], fill=fill, outline=(90, 90, 90))
    edge = lay.d.get("edge") or {}
    if edge.get("material") == "metal":
        d.rectangle([0, 0, out.width - 1, out.height - 1], outline=METAL_RGB, width=max(1, int(round(2 * scale))))
    h = lay.handle()
    if h:
        hx, hy = h
        d.rectangle([X(hx - 26), Y(hy + 26), X(hx + 26), Y(hy - 26)], fill=CHROME_RGB, outline=(110, 110, 110))
        d.rectangle([X(hx), Y(hy + 8), X(hx + 135), Y(hy - 8)], fill=CHROME_RGB, outline=(110, 110, 110))
    for y in lay.hinges():
        d.rectangle([X(lay.W - 4), Y(y + 39), X(lay.W) - 1, Y(y - 39)], fill=CHROME_RGB, outline=(110, 110, 110))
    return out


# ------------------------------------------------------------------------------------------------------ photo compare

CUT_RGB, GLASS_LINE_RGB = (0, 255, 60), (255, 0, 255)
LINE_RGB = {"glass": GLASS_LINE_RGB, "black": GLASS_LINE_RGB, "mirror": GLASS_LINE_RGB, "clear": GLASS_LINE_RGB,
            "metal": (0, 140, 255), "groove": (255, 150, 0)}


def line_rgb(ln):
    return GLASS_LINE_RGB if ln["rule"].startswith("glass-edge") else LINE_RGB.get(ln["kind"], CUT_RGB)


def load_measure():
    sys.path.insert(0, str(HERE))
    import measure
    return measure


def open_photo(M, photo, bounds=None, bottom=None):
    rgb, grey = M.load_photo(photo)
    return dict(name=Path(str(photo)).name, rgb=rgb, grey=grey, leaf=M.find_leaf(grey, bounds, bottom))


def photo_leaf_image(ph, lay, scale):
    """The photo's leaf resampled onto the drawing (the design's W x H at `scale`)."""
    leaf = ph["leaf"]
    size = (int(round(lay.W * scale)), int(round(lay.H * scale)))
    im = Image.fromarray(ph["rgb"].astype(np.uint8))
    return im.transform(size, Image.EXTENT, (leaf["x0"], leaf["y0"], leaf["x1"], leaf["y1"]), Image.BICUBIC)


def finish_rgb(ph):
    """Median colour of the lock stile (a flat board of the finish) - to tint the drawing like the photo."""
    leaf, rgb = ph["leaf"], ph["rgb"]
    x0, x1 = int(leaf["x0"] + 0.03 * leaf["w"]), int(leaf["x0"] + 0.11 * leaf["w"])
    y0, y1 = int(leaf["y0"] + 0.1 * leaf["h"]), int(leaf["y0"] + 0.4 * leaf["h"])
    return tuple(int(v) for v in np.median(rgb[y0:y1, x0:x1].reshape(-1, 3), axis=0))


def _dashed(d, x0, y0, x1, y1, fill, dash=5, gap=4, width=1):
    """Dashed straight line (horizontal or vertical) - the photo's line stays visible between the dashes."""
    if abs(y1 - y0) < 1e-9:
        a, b = sorted((x0, x1))
        while a < b:
            d.line([a, y0, min(a + dash, b), y0], fill=fill, width=width)
            a += dash + gap
    else:
        a, b = sorted((y0, y1))
        while a < b:
            d.line([x0, a, x0, min(a + dash, b)], fill=fill, width=width)
            a += dash + gap


def draw_lines(img, lay, lines, scale):
    d = ImageDraw.Draw(img)
    H = lay.H
    for ln in lines:
        a, b = ln["span"]
        if ln["axis"] == "y":
            y = round((H - ln["pos"]) * scale - 0.5)
            _dashed(d, a * scale, y, b * scale, y, line_rgb(ln))
        else:
            x = round(ln["pos"] * scale - 0.5)
            _dashed(d, x, (H - b) * scale, x, (H - a) * scale, line_rgb(ln))
    d.rectangle([0, 0, img.width - 1, img.height - 1], outline=(0, 200, 0))
    h = lay.handle()
    if h:
        x, y = h[0] * scale, (H - h[1]) * scale
        d.line([x - 14, y, x + 14, y], fill=(255, 0, 255))
        d.line([x, y - 14, x, y + 14], fill=(255, 0, 255))
    for hy in lay.hinges():
        y = (H - hy) * scale
        d.line([img.width - 16, y, img.width - 1, y], fill=(255, 0, 255))
    return img


def autocontrast(im):
    """Stretch the levels of a (dark) photo crop so its lines are visible."""
    a = np.asarray(im).astype(float)
    lo, hi = np.percentile(a, 1), np.percentile(a, 99)
    return Image.fromarray(np.clip((a - lo) * 255.0 / max(hi - lo, 1), 0, 255).astype(np.uint8))


def zoom_image(M, ph, lay, lines, box, k):
    x0, y0, x1, y1 = box
    leaf = ph["leaf"]
    src = Image.fromarray(ph["rgb"].astype(np.uint8))
    area = (M.mm_to_px(leaf, x=x0), M.mm_to_px(leaf, y=y1), M.mm_to_px(leaf, x=x1), M.mm_to_px(leaf, y=y0))
    zim = autocontrast(src.transform((int(round((x1 - x0) * k)), int(round((y1 - y0) * k))), Image.EXTENT, area,
                                     Image.NEAREST))
    d = ImageDraw.Draw(zim)
    for ln in lines:
        a, b = ln["span"]
        if ln["axis"] == "y" and y0 <= ln["pos"] <= y1 and b > x0 and a < x1:
            y = round((y1 - ln["pos"]) * k - 0.5)
            _dashed(d, (max(a, x0) - x0) * k, y, (min(b, x1) - x0) * k, y, line_rgb(ln), 10, 10, 2)
        elif ln["axis"] == "x" and x0 <= ln["pos"] <= x1 and b > y0 and a < y1:
            x = round((ln["pos"] - x0) * k - 0.5)
            _dashed(d, x, (y1 - min(b, y1)) * k, x, (y1 - max(a, y0)) * k, line_rgb(ln), 10, 10, 2)
    return zim


def feature_near(prof, p0, rule, dirn, ppm, glass_side=1, max_win=None):
    """Photo position (continuous px) of the feature a design line of `rule` sits on, searched near p0 (px).

    dirn: +1 when photo px grow with mm (x), -1 when they shrink (y); glass_side: -1 = the glass is on the
    smaller-mm side of a glass-edge line. In photo px the upper/left side is always the smaller one, and the lit
    side of a joint (lower/right) the larger one."""
    win = max(3, int(round(4 * ppm / 0.4)))   # 4 px on a big photo, 2 on a small one
    if max_win is not None:                    # stay clear of the next design line
        win = max(2, min(win, int(max_win)))
    n = len(prof)
    prof = np.asarray(prof, float)
    i0, i1 = max(3, int(np.floor(p0 - win))), min(n - 4, int(np.ceil(p0 + win)) + 1)
    if i1 - i0 < 3:
        return None
    base = float(np.median(prof[max(0, i0 - 3 * win):min(n, i1 + 3 * win)]))
    noise = float(np.median(np.abs(np.diff(prof[max(0, i0 - 3 * win):min(n, i1 + 3 * win)])))) + 1.0
    thr = max(4.0, 2.0 * noise)

    def crossing(j, step, level):
        """Walk from index j in direction step while prof stays on j's side of level; sub-pixel crossing."""
        below = prof[j] < level
        k = j
        while 0 < k + step < n - 1 and (prof[k + step] < level) == below and abs(k + step - j) < 3 * win:
            k += step
        v1, v2 = prof[k], prof[k + step]
        t = (level - v1) / (v2 - v1) if v2 != v1 else 0.5
        return k + 0.5 + step * t

    if rule.startswith("strip") or rule.startswith("glass-edge"):
        # the bright side: the strip itself (strip rules) or the glass (glass-edge)
        bright_after = glass_side > 0 if rule.startswith("glass-edge") else rule == "strip-start"
        step = 1 if bright_after == (dirn > 0) else -1          # px direction towards the bright side
        j = int(round(p0 - 0.5))
        far = [int(round(p0 - 0.5 + step * t)) for t in range(1, win + 1)]
        near = [int(round(p0 - 0.5 - step * t)) for t in range(1, win + 1)]
        hi_v = max(prof[min(max(i, 0), n - 1)] for i in far)
        lo_v = float(np.median([prof[min(max(i, 0), n - 1)] for i in near]))
        if hi_v - lo_v < thr:
            return None
        half = (hi_v + lo_v) / 2
        # nearest crossing of `half` to p0 going from dark to bright in direction step
        best = None
        for jj in range(i0, i1 - 1):
            v1, v2 = prof[jj], prof[jj + 1]
            if (v1 - half) * (v2 - half) <= 0 and v1 != v2 and ((v2 > v1) == (step > 0)):
                c = jj + 0.5 + (half - v1) / (v2 - v1)
                if best is None or abs(c - p0) < abs(best - p0):
                    best = c
        return best

    def centroid_at(k, sign):
        a, b = max(0, k - 1), min(n, k + 2)
        vals = sign * (prof[a:b] - base)
        w = np.clip(vals - vals[k - a] * 0.5, 0, None)
        return float((np.arange(a, b) * w).sum() / w.sum()) + 0.5 if w.sum() > 0 else k + 0.5

    def pick(sign):
        """The extremum (sign -1 dark, +1 lit) the line sits on: local extrema of the window weighted by their
        contrast and by their closeness to p0 - grain streaks further away do not win over the real edge."""
        best, score = None, 0.0
        for k in range(i0, i1):
            v = sign * (prof[k] - base)
            if v < thr or sign * prof[k] < sign * prof[k - 1] or sign * prof[k] < sign * prof[k + 1]:
                continue
            sc = v * np.exp(-((k + 0.5 - p0) / (0.75 * win)) ** 2)
            if sc > score:
                best, score = k, sc
        return best

    if rule in ("groove-lit", "step-lit"):
        kl = pick(1)
        if kl is None:
            return None
        cl = centroid_at(kl, 1)
        if rule == "groove-lit":
            return cl
        # a dark line just before the lit edge (the lower piece's end in shadow): the step is between them
        look = range(max(1, kl - int(np.ceil(2.5 * ppm / 0.4))), kl)
        if len(look):
            kd2 = min(look, key=lambda i: prof[i])
            if base - prof[kd2] >= thr:
                return (centroid_at(kd2, -1) + cl) / 2
        half = (prof[kl] + base) / 2
        return crossing(kl, -1, half)
    kd = pick(-1)
    if kd is None:
        return None
    cd = centroid_at(kd, -1)
    if rule == "groove-dark":
        return cd
    if rule == "step-dark":
        # the higher piece is above/left (smaller px): its edge is where the dark band starts on that side
        side = prof[max(0, kd - 3 * win):max(1, kd - 1)]
        plateau = float(np.median(side)) if len(side) else base
        return crossing(kd, -1, (plateau + prof[kd]) / 2) + 1.0 * ppm
    # joint: a lit line right after the dark one (larger px) -> the contact is between them
    look = range(kd + 1, min(n - 1, kd + 1 + int(np.ceil(2.5 * ppm / 0.4))))
    if len(look):
        kl = max(look, key=lambda i: prof[i])
        if prof[kl] - base >= thr:
            return (cd + centroid_at(kl, 1)) / 2
    return cd + 1.0 * ppm


def _clearance(ln, lines):
    """Distance (mm) from a line to the nearest other parallel design line (or leaf edge) that overlaps its span."""
    a, b = ln["span"]
    d = min(ln["pos"], (800.0 if ln["axis"] == "x" else 2000.0) - ln["pos"])
    for o in lines:
        if o is ln or o["axis"] != ln["axis"] or abs(o["pos"] - ln["pos"]) < 1e-6:
            continue
        if o["span"][0] < b and o["span"][1] > a:
            d = min(d, abs(o["pos"] - ln["pos"]))
    return d


def check_photo(M, lay, lines, ph):
    """-> [(line, photo mm or None)] for one photo."""
    leaf, grey = ph["leaf"], ph["grey"]
    out = []
    for ln in lines:
        a, b = ln["span"]
        if b - a < 15:     # too short to average a profile over
            out.append((ln, None))
            continue
        pad = min(20.0, (b - a) * 0.2)
        ppm = leaf["sy"] if ln["axis"] == "y" else leaf["sx"]
        max_win = 0.6 * _clearance(ln, lines) * ppm
        if ln["axis"] == "y":
            prof = M.row_profile(grey, leaf, a + pad, b - pad)
            p = feature_near(prof, M.mm_to_px(leaf, y=ln["pos"]), ln["rule"], -1, ppm,
                             ln.get("glass_side", 1), max_win)
            out.append((ln, None if p is None else M.px_to_mm(leaf, y=p)))
        else:
            prof = M.col_profile(grey, leaf, a + pad, b - pad)
            p = feature_near(prof, M.mm_to_px(leaf, x=ln["pos"]), ln["rule"], 1, ppm,
                             ln.get("glass_side", 1), max_win)
            out.append((ln, None if p is None else M.px_to_mm(leaf, x=p)))
    return out


# ---------------------------------------------------------------------------------------------------------- commands

def index_photos(model, pages=None):
    """Photos of the catalogue index whose caption is `model` (with any suffix), biggest first."""
    if not model:
        return []
    idx = json.loads((HERE / ".cache" / "index.json").read_text(encoding="utf-8"))
    keep = None
    if pages:
        keep = set()
        for part in pages.split(","):
            lo, _, hi = part.partition("-")
            keep.update(range(int(lo), int(hi or lo) + 1))
    pat = re.compile(re.escape(model.upper()) + r"(?!\d)")
    hits = [e for e in idx if pat.match(e["model"].upper()) and (keep is None or e["catPage"] in keep)]
    hits.sort(key=lambda e: (-e["px"][0] * e["px"][1], e["file"]))
    return [e["file"] for e in hits]


def cmd_single(a):
    design = load_design(a.designs[0])
    W, H = (float(v) for v in a.size.lower().split("x")) if a.size else design["ref"]
    lay = Layout(design, W, H)
    scale = a.scale
    font = _font(14)
    a.photo = list(a.photo or []) + [f for f in index_photos(a.photos_of, a.pages) if f not in (a.photo or [])]
    if not a.photo:
        if a.photos_of:
            raise SystemExit(f"no photo of {a.photos_of} in the catalogue index")
        img = render(lay, scale, door_glass=a.glass)
        pad = 20
        canvas = Image.new("RGB", (img.width + 2 * pad, img.height + 2 * pad + 20), (255, 255, 255))
        canvas.paste(img, (pad, pad + 20))
        ImageDraw.Draw(canvas).text((pad, 2), f"{design.get('name', design.get('id'))}  {W:.0f}x{H:.0f}",
                                    fill=(0, 0, 0), font=font)
        canvas.save(a.out)
        print("->", a.out)
        return
    M = load_measure()
    bounds = [float(v) for v in a.bounds.split(",")] if a.bounds else None
    photos = [open_photo(M, p, bounds, a.bottom) for p in a.photo]
    ph0 = photos[0]
    lines = design_lines(lay)
    pim = photo_leaf_image(ph0, lay, scale)
    des = render(lay, scale, door_glass=a.glass)
    ov = draw_lines(pim.copy(), lay, lines, scale)
    pad = 16
    w, h = pim.width, pim.height
    canvas = Image.new("RGB", (3 * w + 4 * pad, h + 2 * pad + 22), (255, 255, 255))
    for i, im in enumerate((pim, des, ov)):
        canvas.paste(im, (pad + i * (w + pad), pad + 22))
    leaf = ph0["leaf"]
    ImageDraw.Draw(canvas).text(
        (pad, 2), f"{ph0['name']}  |  {design.get('id')} {W:.0f}x{H:.0f}  |  overlay   (photo leaf {leaf['w']:.1f}x"
                  f"{leaf['h']:.1f} px, aspect {leaf['aspect']:.4f})", fill=(0, 0, 0), font=font)
    canvas.save(a.out)
    print("->", a.out)
    for ph in photos:
        for n in ph["leaf"]["notes"]:
            print(f"note ({ph['name']}):", n)
    if a.zoom:
        zp = Path(a.out)
        zp = zp.with_name(zp.stem + "-zoom" + zp.suffix)
        zoom_image(M, ph0, lay, lines, [float(v) for v in a.zoom.split(",")], a.zoom_scale).save(zp)
        print("->", zp)
    if a.check:
        report(M, lay, lines, photos)


def report(M, lay, lines, photos):
    results = [check_photo(M, lay, lines, ph) for ph in photos]
    print("\nphoto columns: offset of the photo's line from the design's, mm (px of that photo)")
    for i, ph in enumerate(photos):
        lf = ph["leaf"]
        print(f"  [{i}] {ph['name']}  {lf['W']}x{lf['H']}  {lf['sx']:.3f}x{lf['sy']:.3f} px/mm")
    head = f"{'line':44s} {'rule':10s} {'design':>7s} " + " ".join(f"{'[' + str(i) + ']':>12s}"
                                                               for i in range(len(photos))) + f" {'mean mm':>8s}"
    print(head)
    worst = 0.0
    for li, ln in sorted(enumerate(lines), key=lambda t: (t[1]["axis"], t[1]["pos"])):
        cols, wsum, vsum = [], 0.0, 0.0
        for ph, res in zip(photos, results):
            mm = res[li][1]
            ppm = ph["leaf"]["sy" if ln["axis"] == "y" else "sx"]
            if mm is None:
                cols.append(f"{'-':>12s}")
                continue
            off = mm - ln["pos"]
            cols.append(f"{off:+6.1f}({off * ppm:+4.1f})")
            if abs(off * ppm) <= 3:   # ignore gross mismatches (another line caught) in the mean
                wsum += ppm ** 2
                vsum += off * ppm ** 2
            if ppm > 0.3 and ln["rule"] != "glass-edge-r":
                worst = max(worst, abs(off * ppm))
        mean = vsum / wsum if wsum else float("nan")
        print(f"{ln['label'][:44]:44s} {ln['rule']:10s} {ln['pos']:7.1f} " + " ".join(cols) + f" {mean:+8.1f}")
    if any(max(ph["leaf"]["sx"], ph["leaf"]["sy"]) > 0.3 for ph in photos):
        print(f"worst offset on the big photos: {worst:.2f} px (glass-edge-r lines excluded: a lit wood edge next "
              f"to glass is as bright as the glass)")
    else:
        print("no big photo (> 0.3 px/mm): judge the small ones by the table and the overlay")
    # per cut: pooled offset of all its lines on all photos (weights (px/mm)^2, gross mismatches > 3 px and
    # glass-edge-r lines left out; the small photos only when no big one is given - their blur biases the rules
    # by ~0.5-1 px); for strips also the measured width
    print("\ncuts: pooled offset -> suggested ref position (mm); strips: measured width")
    big = any(max(ph["leaf"]["sx"], ph["leaf"]["sy"]) > 0.3 for ph in photos)
    cuts = {}
    for li, ln in enumerate(lines):
        c = cuts.setdefault(ln["cut"], dict(ref=ln["ref"], axis=ln["axis"], w=0.0, v=0.0, n=0, starts=[], ends=[]))
        for ph, res in zip(photos, results):
            mm = res[li][1]
            ppm = ph["leaf"]["sy" if ln["axis"] == "y" else "sx"]
            if big and ppm < 0.3:
                continue
            if mm is None or ln["rule"] == "glass-edge-r" or abs((mm - ln["pos"]) * ppm) > 3:
                continue
            c["w"] += ppm ** 2
            c["v"] += (mm - ln["pos"]) * ppm ** 2
            c["n"] += 1
            if ln["rule"] == "strip-start" or (ln["rule"].startswith("groove") and ln["label"].endswith("start")):
                c["starts"].append((mm - ln["pos"], ppm ** 2))
            elif ln["rule"] == "strip-end" or (ln["rule"].startswith("groove") and ln["label"].endswith("end")):
                c["ends"].append((mm - ln["pos"], ppm ** 2))
    for path, c in cuts.items():
        if not c["w"]:
            print(f"  {path:40s} ref {c['ref']:7.1f}  (not measured)")
            continue
        off = c["v"] / c["w"]
        extra = ""
        if c["starts"] and c["ends"]:
            ws = sum(w for _, w in c["starts"])
            we = sum(w for _, w in c["ends"])
            s0 = sum(o * w for o, w in c["starts"]) / ws
            e0 = sum(o * w for o, w in c["ends"]) / we
            width = next(l["width"] for l in lines if l["cut"] == path and "width" in l)
            extra = f"   strip width {width + e0 - s0:5.1f} (design {width:g})"
        print(f"  {path:40s} ref {c['ref']:7.1f}  offset {off:+5.1f} -> {c['ref'] + off:7.1f}  ({c['n']} meas.){extra}")


def cmd_sheet(a):
    """Every design at each of the widths (same height), --per-row designs per row."""
    widths = [float(v) for v in a.widths.split(",")]
    H = float(a.height)
    scale = a.scale
    font = _font(15)
    groups = []
    for dp in a.designs:
        design = load_design(dp)
        imgs = []
        for w in widths:
            try:
                imgs.append((w, render(Layout(design, w, H), scale, door_glass=a.glass)))
            except ValueError as e:
                print(f"{design.get('id')} {w:.0f}: {e}")
        groups.append((design, imgs))
    gap, pad, top = 8, 28, 44
    gw = max(sum(im.width for _, im in imgs) + gap * (len(imgs) - 1) for _, imgs in groups)
    gh = int(round(H * scale)) + top
    per = max(1, a.per_row)
    rows = (len(groups) + per - 1) // per
    canvas = Image.new("RGB", (per * (gw + pad) + pad, rows * (gh + pad) + pad), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    for i, (design, imgs) in enumerate(groups):
        x = pad + (i % per) * (gw + pad)
        y = pad + (i // per) * (gh + pad)
        d.text((x, y), f"{design.get('name', design.get('id'))}  ({H:.0f} high)", fill=(0, 0, 0), font=font)
        xx = x
        for w, im in imgs:
            d.text((xx, y + 20), f"{w:.0f}", fill=(90, 90, 90), font=font)
            canvas.paste(im, (xx, y + top))
            xx += im.width + gap
    canvas.save(a.out)
    print("->", a.out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("designs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", help="WxH leaf size in mm (default: the design's ref)")
    ap.add_argument("--scale", type=float, help="px per mm (default 0.8; 0.25 for --sheet)")
    ap.add_argument("--photo", action="append", help="catalogue photo (repeat for --check on several)")
    ap.add_argument("--photos-of", help="add every catalogue photo of this model caption, e.g. ПОРТА-22")
    ap.add_argument("--pages", help="catalogue pages for --photos-of, e.g. 9-11,19-27")
    ap.add_argument("--bounds", help="X0,Y0,X1,Y1 leaf bounds in photo px (skip the detection)")
    ap.add_argument("--bottom", type=float, help="leaf bottom in photo px")
    ap.add_argument("--glass", default="satin", help="glass role for the door's glass (satin, black, mirror...)")
    ap.add_argument("--check", action="store_true", help="measure every design line on the photos")
    ap.add_argument("--zoom", help="X0,Y0,X1,Y1 mm: also write <out>-zoom.png of that region")
    ap.add_argument("--zoom-scale", type=float, default=6.0, help="px per mm of the zoom image (default 6)")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--widths", default="600,800,900")
    ap.add_argument("--height", default="2000")
    ap.add_argument("--per-row", type=int, default=4, help="designs per row of the --sheet (default 4)")
    a = ap.parse_args(argv)
    if a.scale is None:
        a.scale = 0.25 if a.sheet else 0.8
    (cmd_sheet if a.sheet else cmd_single)(a)


if __name__ == "__main__":
    main()
