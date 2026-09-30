#!/usr/bin/env python3
"""Casegoods texture family `prints`: printed / ornamental fronts (wave 6).

    python tools/casegoods/textures/prints.py                 # every material + entries/prints.json + sheets/prints.png
    python tools/casegoods/textures/prints.py british [motif …]   # only the Бритиш Бум prints (or some motifs)
    python tools/casegoods/textures/prints.py eliza | martina | ken | sheet
    python3 tools/doors/textures/merge_entries.py tools/casegoods/textures/entries/prints.json

Materials (Assets/House4696/External/Materials/<id>/):
* cgprint_british_bum_<motif> (26) — the «Бритиш Бум» photo-printed fronts, cleaned from the rectified crops of
  tools/casegoods/gen/prints/british-bum/<motif>.png into flat prints: a `print` is fitted to the whole +z face of its
  front (CaseBuilder.Print: u = (x − x0) / w across, v = (y − y0) / h up), so each albedo has the front's aspect
  (w × h mm at 1–2 px/mm, ≤ 2048 px where that keeps ≥ 1 px/mm) and metersPerTile [1, 1] (the UV already spans 0…1).
  Cleaning: the photo's shading is divided out (a robust local ground estimate), the handle is cut out and in-painted
  across its short axis (lines that cross it continue), the ink is unmixed into the motif's 1–3 ink colours and
  re-thresholded into crisp line art on the «Крем» ground #e0d6cd (the fronts' swatch, p. 131).
* cgprint_eliza_rozy — the gilded rose spray of «Элиза», a `print` decal for the ellipse parts `*-orn` (role
  `ornament`): gold line-art roses on the «Белая Ваниль» ground, metallic gold in the mask, a raised-line normal map.
* cg_martina_listya — the carved leaf relief of «Мартина» («Молоко с серебром»): a tiling role material (role
  `carve`), milk-white raised leaves on a silver-patinated recessed ground, strong normal map and AO; leaves along U.
* cgprint_ken_elochka_<w>x<h> — the «ёлочка» UV print of «Кен» as transparent decals (dark-brown 2.5 mm chevron lines,
  alpha elsewhere 0) laid over the oak front, one per front size, the lines exactly where the designs' V-grooves are.

Needs numpy + Pillow only.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXT = ROOT / "Assets" / "House4696" / "External"
DESIGNS = ROOT / "Assets" / "House4696" / "Resources" / "Casegoods" / "Designs"
CROPS = ROOT / "tools" / "casegoods" / "gen" / "prints" / "british-bum"
ENTRIES = HERE / "entries" / "prints.json"
SHEET = HERE / "sheets" / "prints.png"
SOURCE = "procedural:tools/casegoods/textures/prints.py"

sys.path.insert(0, str(ROOT / "tools" / "doors" / "textures"))
from make_finishes import srgb_to_linear, linear_to_srgb, linear_to_lab, blur, gauss_noise  # noqa: E402

CREAM = "#e0d6cd"          # «Крем», p. 131 swatch «Фасад» (flat ±0.5)
VANILLA = "#e8e6e4"        # «Белая Ваниль», p. 108 swatch
FILM_SMOOTH = 0.35         # the fronts' matt film


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0


def rgb_hex(c):
    c = np.clip(np.round(np.asarray(c) * 255), 0, 255).astype(int)
    return "#%02x%02x%02x" % tuple(c)


def lab(c_srgb):
    return linear_to_lab(srgb_to_linear(np.asarray(c_srgb, float)))


def de76(a, b):
    return float(np.linalg.norm(lab(a) - lab(b)))


def wblur(a, sy, sx):
    """Gaussian blur of a periodic tile (wrapped edges: no seam)."""
    r = int(3 * max(sy, sx) + 2)
    return blur(np.pad(a, [(r, r), (r, r)], mode="wrap"), sy, sx)[r:-r, r:-r]


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def to_img(a):
    return Image.fromarray(np.clip(np.round(a * 255), 0, 255).astype(np.uint8))


def folder(mid):
    f = EXT / "Materials" / mid
    f.mkdir(parents=True, exist_ok=True)
    return f


def flat_normal(n=64):
    a = np.zeros((n, n, 3), np.uint8)
    a[..., 0] = a[..., 1] = 128
    a[..., 2] = 255
    return Image.fromarray(a)


def const_mask(metal=0, ao=255, smooth=FILM_SMOOTH, n=64):
    a = np.zeros((n, n, 4), np.uint8)
    a[..., 0] = metal
    a[..., 1] = ao
    a[..., 3] = int(round(smooth * 255))
    return Image.fromarray(a, "RGBA")


def height_to_normal(hgt, strength):
    """Height (px units × strength = slope) → OpenGL normal map (+Y green = up = −row), periodic differences."""
    gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) * 0.5 * strength
    gr = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) * 0.5 * strength
    n = np.stack([-gx, gr, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return Image.fromarray(np.round((n * 0.5 + 0.5) * 255).astype(np.uint8))


def entry(mid, name, tile, albedo_ext="jpg", transparent=False, max_size=2048, extra=None):
    e = {"id": mid, "name": name, "category": "casegoods", "source": SOURCE, "neutral": False,
         "metersPerTile": list(tile), "maxSize": max_size, "folder": f"Materials/{mid}",
         "textures": {"albedo": f"{mid}_albedo.{albedo_ext}", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}
    if transparent:
        e["transparent"] = True
    if extra:
        e.update(extra)
    return e


# =============================================================================================== Бритиш Бум
MOTIF_NAMES = {
    "flag_england_door": "флаг и «England»", "lantern_london_door": "фонарь и «London»",
    "stpauls_door_l": "Собор Св. Павла, левая", "stpauls_door_r": "Собор Св. Павла, правая",
    "bigben_door_l": "воздушные шары и Вестминстер, левая", "bigben_door_r": "Биг-Бен, правая",
    "gherkin_door": "флаг и улица Лондона", "shield_door": "щит и меч «England»", "football_door": "«England» и мяч",
    "stamp_drawer": "почтовый штемпель", "balloons_drawer_2": "воздушный шар", "balloons_drawer_3": "воздушные шары",
    "england_drawer_4": "«England»", "skyline_drawer_2": "панорама Лондона, верх", "skyline_drawer_3": "панорама Лондона, низ",
    "england_drawer_s": "«England», малый ящик", "bus_drawer_s": "автобус", "towerbridge_door_l": "«Wow» и Тауэрский мост, левая",
    "towerbridge_door_r": "Тауэрский мост, правая", "umbrella_door": "зонт", "lamp_door": "зонт, фонарь и мяч",
    "bigben_column_door": "Биг-Бен «Big Ben»", "guard_door": "королевский гвардеец", "london_rail": "«London», царга кровати",
    "bus_stamp_drawer": "автобус и штемпель", "eye_england_drawer": "Лондонский глаз и «England»",
}

# per-motif tuning (all optional):
#   trim  [left, bottom, right, top] mm forced to ground at the edges (gap shadows, the neighbour's edge)
#   lo/hi the ink-coverage thresholds of the crisp line art; inks = number of ink colours
#   holes extra rectangles [x0, y0, x1, y1] mm (front coordinates, y up) to cut out and in-paint
#   nohandle  ignore the design's handle (the crop has none there)
CAT = dict(sharp=2.5, lo=0.3, hi=0.55, boost=1.15, sig=2.0, pre=1.0, trim=(8, 8, 8, 8), inks=3)          # the 100-dpi catalogue crops: blurred, faint
CATA = dict(CAT, sharp=2.0, lo=0.42, hi=0.68, adapt=True, floor=0.3)  # … with thin faint strokes: adaptive threshold
def _bus_lower_deck():
    """The lower deck of the 2.16 bus under the handle (the visible ends of its lines on both sides, the perspective
    of the upper deck's windows): the band under the upper deck, the lower windows, the door."""
    lines = [([(84, 110.7), (247, 114.8)], 1.3), ([(84, 105.2), (247, 112.3)], 1.3),
             ([(166.5, 91.5), (166.5, 108.5)], 1.3), ([(170.5, 91.5), (170.5, 108.5)], 1.3)]
    for xa, xb in ((86, 104), (108, 135), (139, 164), (173, 183), (187, 201), (205, 228)):
        ta, tb = 99 + (xa - 40) * 0.057, 99 + (xb - 40) * 0.057
        ba, bb = 85 + (xa - 40) * 0.03, 85 + (xb - 40) * 0.03
        r = 1.8
        lines.append(([(xa + r, ta), (xb - r, tb), (xb, tb - r), (xb, bb + r), (xb - r, bb), (xa + r, ba), (xa, ba + r),
                       (xa, ta - r), (xa + r, ta)], 1.3))
    return lines


BUS_LOWER_DECK = _bus_lower_deck()
FLAG = dict(donor="gherkin_door", src=[40, 1395, 415, 1815])            # the site photo's flag + «England»
TUNE = {
    "flag_england_door": dict(CAT, transplant=[dict(FLAG, scale=0.95, at=[218, 1780], clear=[30, 1560, 434, 2050])]),
    "stpauls_door_l": dict(CAT, transplant=[dict(FLAG, scale=0.95, at=[213, 1360], clear=[30, 1170, 434, 1640])]),
    "shield_door": dict(CAT, transplant=[dict(donor="football_door", src=[40, 160, 330, 262], drop=[[250, 122, 72]],
                                              rot=-10, scale=1.05, at=[205, 180], clear=[60, 110, 400, 250])], trim=(8, 8, 8, 16)),
    "lantern_london_door": dict(CAT, boost=1.0, lo=0.18, hi=0.4, trim=(8, 8, 8, 14)),
    "lamp_door": dict(ground=[[0, 880, 48, 1150]]),
    "england_drawer_s": dict(trim=(3, 3, 3, 7)),
    "bus_drawer_s": dict(nohandle=True, ground=[[84, 86, 292, 116.5]], draw=BUS_LOWER_DECK), "stpauls_door_r": CAT,
    "bigben_door_l": CAT, "bigben_door_r": CAT,
    "towerbridge_door_l": CAT, "towerbridge_door_r": dict(CAT, trim=(8, 8, 8, 14)), "umbrella_door": dict(CAT, boost=1.0, sharp=0.5, lo=0.2, hi=0.4, thr=0.12, pure=0.6, inks=3, pre=1.6, trim=(20, 12, 20, 20)),
    "bigben_column_door": CAT, "guard_door": CAT, "london_rail": CAT, "bus_stamp_drawer": CAT,
    "eye_england_drawer": dict(CAT, trim=(8, 12, 20, 8)),
}


def fronts():
    """motif → the fronts that print it (design, part id, w, h, handles in front mm)."""
    out = {}
    for f in sorted(DESIGNS.glob("british-bum-*.json")):
        parts = json.loads(f.read_text())["parts"]
        for p in parts:
            pr = p.get("print")
            if not pr:
                continue
            b = p["box"]
            x0, x1 = sorted((b[0], b[3]))
            y0, y1 = sorted((b[1], b[4]))
            hs = []
            for h in parts:
                if h.get("kind") == "handle" and x0 <= h["at"][0] <= x1 and y0 <= h["at"][1] <= y1:
                    hs.append(dict(x=h["at"][0] - x0, y=h["at"][1] - y0, dir=h.get("dir", "right"),
                                   d=h.get("d", 128), band=h.get("band", 12)))
            out.setdefault(pr.replace("cgprint_", "").replace("british_bum_", ""), []).append(
                dict(design=f.stem, part=p["id"], w=x1 - x0, h=y1 - y0, handles=hs))
    return out


def rank_bg(img, k, rank_frac):
    """Per-channel rank filter (odd size k, rank fraction) of a uint8 RGB image."""
    k = k | 1
    return img.filter(ImageFilter.RankFilter(k, int(k * k * rank_frac)))


def handle_cand(S, bg):
    """Pixels that look like the metal handle: grey (less chroma than the ground) and off the ground's brightness,
    or brighter than the ground (highlights)."""
    lum = S @ [0.3, 0.59, 0.11]
    lb = bg @ [0.3, 0.59, 0.11]
    chroma = S.max(-1) - S.min(-1)
    cb = bg.max(-1) - bg.min(-1)
    dev = lum - lb
    return ((np.abs(dev) > 0.06) & (chroma < cb + 0.012)) | (dev > 0.045)


def detect_handle(cand, h, ppm, H):
    """Refine a design handle rectangle on the image: the long grey / bright blob near it. Returns a px rect."""
    horiz = h["dir"] in ("right", "left")
    L, B = h["d"] / 2, h["band"] / 2
    cx, cy = h["x"] * ppm, H - h["y"] * ppm
    ax, ay = ((L + 40) * ppm, (B + 60) * ppm) if horiz else ((B + 60) * ppm, (L + 40) * ppm)
    r0, r1 = int(max(0, cy - ay)), int(min(cand.shape[0], cy + ay))
    c0, c1 = int(max(0, cx - ax)), int(min(cand.shape[1], cx + ax))
    c = cand[r0:r1, c0:c1]
    along = c.sum(1 if horiz else 0)
    idx = np.nonzero(along > 0.3 * (h["d"] * ppm))[0]
    if len(idx) == 0:
        return None
    runs, start = [], idx[0]
    for a, b in zip(idx, np.append(idx[1:], -10)):
        if b != a + 1:
            runs.append((start, a))
            start = b
    run = max(runs, key=lambda r: along[r[0]:r[1] + 1].sum())
    run = (max(0, run[0] - int(6 * ppm)), min(len(along) - 1, run[1] + int(6 * ppm)))   # the bow of a curved handle
    sel = c[run[0]:run[1] + 1, :] if horiz else c[:, run[0]:run[1] + 1]
    prof = sel.sum(0 if horiz else 1)
    idx2 = np.nonzero(prof > 0)[0]
    # the handle's extent along: the longest dense stretch
    dense = np.convolve(prof > 0, np.ones(int(4 * ppm) | 1), "same") > 0
    idx2 = np.nonzero(dense)[0]
    if len(idx2) == 0:
        return None
    a0, a1 = idx2[0], idx2[-1]
    if horiz:
        return [c0 + a0, r0 + run[0], c0 + a1 + 1, r0 + run[1] + 1]
    return [c0 + run[0], r0 + a0, c0 + run[1] + 1, r0 + a1 + 1]


def span_fill(mask, vertical):
    """Fill each column (vertical) or row between its first and last set pixel: the handle's body between its
    outline and highlights."""
    M = mask if vertical else mask.T
    out = np.zeros_like(M)
    cols = np.nonzero(M.any(0))[0]
    for c in cols:
        idx = np.nonzero(M[:, c])[0]
        out[idx[0]:idx[-1] + 1, c] = True
    return out if vertical else out.T


def grow(mask, px):
    k = max(3, int(round(px)) * 2 + 1)
    return np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(k))) > 0


def lightest(px):
    """The lightest pixel of a strip (a soft shadow at the hole's edge is not continued; a crossing line is dark in
    every pixel of the strip, so it is)."""
    return px[np.argmax(px @ [0.3, 0.59, 0.11])]


def inpaint_mask(R, mask, vertical, band=12):
    """Fill the masked pixels by linear interpolation between the nearest known pixels of their column (vertical)
    or row: lines crossing the gap continue."""
    A = R if vertical else R.transpose(1, 0, 2)
    M = mask if vertical else mask.T
    n = A.shape[0]
    for c in np.nonzero(M.any(0))[0]:
        col = M[:, c]
        i = 0
        while i < n:
            if not col[i]:
                i += 1
                continue
            j = i
            while j < n and col[j]:
                j += 1
            top = lightest(A[max(0, i - band):i, c]) if i > 0 else None
            bot = lightest(A[j:min(n, j + band), c]) if j < n else None
            top = bot if top is None else top
            bot = top if bot is None else bot
            if top is not None:
                t = ((np.arange(j - i) + 0.5) / (j - i))[:, None]
                A[i:j, c] = top[None] * (1 - t) + bot[None] * t
            i = j


def kmeans(X, k, iters=25, seed=1):
    rng = np.random.default_rng(seed)
    # init: spread by darkness
    order = np.argsort(X.sum(1))
    C = X[order[np.linspace(0, len(X) - 1, k + 2)[1:-1].astype(int)]].copy()
    for _ in range(iters):
        d = ((X[:, None, :] - C[None]) ** 2).sum(-1)
        lab_ = d.argmin(1)
        for j in range(k):
            if (lab_ == j).any():
                C[j] = X[lab_ == j].mean(0)
    return C, lab_


def clean_british(motif, info, tune):
    w, h = info["w"], info["h"]
    ppm = 2.0 if max(w, h) * 2 <= 2048 else max(1.0, 2048 / max(w, h))
    W, H = int(round(w * ppm)), int(round(h * ppm))
    src_img = Image.open(CROPS / f"{motif}.png").convert("RGB")
    S = np.asarray(src_img.resize((W, H), Image.BICUBIC), float) / 255.0

    # 1. a first ground estimate (for the handle detection)
    f = max(1, int(round(4 * ppm)))                       # 4 mm per px
    small = src_img.resize((max(8, W // f), max(8, H // f)), Image.BOX)
    k = int(tune.get("bgk", 100) / 4)
    bg0 = np.asarray(rank_bg(small, k, 0.85).filter(ImageFilter.GaussianBlur(1.5)).resize((W, H), Image.BICUBIC), float) / 255

    # 2. holes: the handles (the design position, refined on the image) + extra rectangles
    cand = handle_cand(S, bg0)
    _l, _lb = S @ [0.3, 0.59, 0.11], bg0 @ [0.3, 0.59, 0.11]
    shade = (_l < _lb - 0.025) & ((S.max(-1) - S.min(-1)) < (bg0.max(-1) - bg0.min(-1)) + 0.01)
    hmask = np.zeros((H, W), bool)
    vert_fill = np.zeros((H, W), bool)          # pixels filled along columns (horizontal handles)
    nholes = 0
    if not tune.get("nohandle"):
        for hd in info["handles"]:
            horiz = hd["dir"] in ("right", "left")
            r = None if tune.get("design_handle") else detect_handle(cand, hd, ppm, H)
            if r is None:
                L, B = hd["d"] / 2, hd["band"] / 2
                cx, cy = hd["x"] * ppm, H - hd["y"] * ppm
                r = [cx - L * ppm, cy - B * ppm, cx + L * ppm, cy + B * ppm] if horiz else \
                    [cx - B * ppm, cy - L * ppm, cx + B * ppm, cy + L * ppm]
                box = np.zeros((H, W), bool)
                box[max(0, int(r[1])):int(r[3]), max(0, int(r[0])):int(r[2])] = True
                m = box
            else:
                box = np.zeros((H, W), bool)
                box[max(0, int(r[1])):int(r[3]), max(0, int(r[0])):int(r[2])] = True
                m = span_fill(box & cand, vertical=horiz)
            m = grow(m, tune.get("hgrow", 4.0) * ppm) & grow(box, 6 * ppm)
            # the handle's shadow: grey pixels darker than the ground, connected to it (≤ 15 mm)
            lim = grow(box, tune.get("shadow_mm", 15) * ppm)
            for _ in range(int(15 * ppm)):
                m2 = m | (grow(m, 1) & shade & lim)
                if m2.sum() == m.sum():
                    break
                m = m2
            m = grow(m, 1.5 * ppm)
            # the soft shadow cast downwards (the photos are lit from above): the mask pushed 8 mm lower too
            sh = int(tune.get("shadow_below", 8) * ppm)
            m[sh:] |= m[:-sh]
            hmask |= m
            if horiz:
                vert_fill |= m
            nholes += 1
    extra = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in tune.get("holes", []):
        sl = (slice(max(0, int(round(H - y1 * ppm))), int(round(H - y0 * ppm))), slice(max(0, int(round(x0 * ppm))), int(round(x1 * ppm))))
        extra[sl] = True
        if x1 - x0 >= y1 - y0:
            vert_fill[sl] = True                  # a wide hole is filled across its height
        nholes += 1
    hmask |= extra

    # 3. the ground (photo shading) without the handles
    S_fill = S.copy()
    S_fill[hmask] = np.median(S[~hmask], axis=0)
    small = to_img(S_fill).resize((max(8, W // f), max(8, H // f)), Image.BOX)
    bg = np.asarray(rank_bg(small, k, tune.get("rank", 0.85)).filter(ImageFilter.GaussianBlur(1.5))
                    .resize((W, H), Image.BICUBIC), float) / 255
    R = np.clip(S / np.maximum(bg, 0.05), 0, 1.15)
    inpaint_mask(R, vert_fill, True, int(6 * ppm))
    inpaint_mask(R, hmask & ~vert_fill, False, int(6 * ppm))
    for x0, y0, x1, y1 in tune.get("ground", []):            # areas known to be plain ground
        R[max(0, int(round(H - y1 * ppm))):int(round(H - y0 * ppm)), max(0, int(round(x0 * ppm))):int(round(x1 * ppm))] = 1
    if tune.get("draw"):
        # lines of the drawing hidden under the handle, redrawn where the visible parts on both sides put them
        lumR0 = R @ [0.3, 0.59, 0.11]
        ref = R[lumR0 <= np.percentile(lumR0, 0.4)].mean(0)
        ss = 4
        im = Image.new("L", (W * ss, H * ss), 0)
        dr = ImageDraw.Draw(im)
        for pts, wmm in tune["draw"]:
            dr.line([(x * ppm * ss, (h - y) * ppm * ss) for x, y in pts], fill=255, width=int(round(wmm * ppm * ss)), joint="curve")
        a = (np.asarray(im.resize((W, H), Image.LANCZOS), float) / 255)[..., None]
        R = R * (1 - a) + ref * a

    # 4. edges: gap shadows / neighbours forced to ground
    tl, tb, tr, tt = [int(round(v * ppm)) for v in tune.get("trim", (3, 3, 3, 3))]
    if tl: R[:, :tl] = 1
    if tr: R[:, W - tr:] = 1
    if tt: R[:tt] = 1
    if tb: R[H - tb:] = 1

    # straight lines along the edges (the gap to the neighbour front / the carcass): rows / columns near an edge whose
    # darkening runs along most of it
    lumR = 1 - (R @ [0.3, 0.59, 0.11])
    e = int(round(tune.get("edge_band", 12) * ppm))
    for axis in (0, 1):
        prof = (lumR > 0.12).mean(1 - axis)
        n = len(prof)
        for i in list(range(min(e, n))) + list(range(max(0, n - e), n)):
            if prof[i] > 0.6:
                if axis == 0:
                    R[max(0, i - 1):i + 2] = 1
                else:
                    R[:, max(0, i - 1):i + 2] = 1
    D = np.clip(1 - R, 0, 1)
    Db = np.stack([blur(D[..., c], 0.8 * ppm / 2, 0.8 * ppm / 2) for c in range(3)], -1)

    # 5. ink colours
    lumD = Db @ [0.3, 0.59, 0.11]
    thr = tune.get("thr") or max(0.22, np.percentile(lumD[H // 10:H - H // 10, W // 10:W - W // 10], 99.3) * 0.7)
    inner = np.zeros((H, W), bool)                      # the palette: away from the edges and the holes
    e15 = int(15 * ppm)
    inner[e15:H - e15, e15:W - e15] = True
    inner &= ~grow(hmask, 6 * ppm)
    strong = (lumD > thr) & inner
    X = R[strong].reshape(-1, 3)
    if len(X) < 50:
        X = R[(lumD >= np.percentile(lumD[inner], 99.5)) & inner].reshape(-1, 3)
    n_ink = tune.get("inks", 2)
    # cluster on the darkening's hue (its direction) as much as on its depth: terracotta fills vs brown lines
    Dx = 1 - X
    nx = np.linalg.norm(Dx, axis=1, keepdims=True) + 1e-6
    C, lab_ = kmeans(np.hstack([Dx / nx * 3.0, nx * 0.7]), n_ink)
    inks = []
    cream = hex_rgb(CREAM)
    for j in range(n_ink):
        Xj = X[lab_ == j]
        if len(Xj) == 0:
            continue
        dark = Xj[np.argsort(Xj.sum(1))[:max(1, int(len(Xj) * tune.get("pure", 0.33)))]].mean(0)   # the pure ink (thin lines are mixed)
        # faint sources (the 100-dpi catalogue photos): even the darkest pixels are mixed with the ground
        dark = 1 - np.clip((1 - dark) * tune.get("boost", 1.0), 0, 0.92)
        c = np.clip(cream * dark, 0, 1)
        # a little more saturated and deeper, like the print on the film
        m = c.mean()
        c = np.clip(m + (c - m) * tune.get("sat", 1.2), 0, 1) * tune.get("deep", 0.95)
        # not blacker than the print's deepest brown (L* 26): the dark clusters of the catalogue photos are crushed
        for _ in range(20):
            if lab(c)[0] >= tune.get("min_L", 26):
                break
            c = np.clip(c * 1.06 + 0.004, 0, 1)
        inks.append((1 - dark, c))
    # 6. unmix: per pixel the ink whose direction explains the darkening best, coverage along it
    best_a = np.zeros((H, W))
    best_r = np.full((H, W), 1e9)
    best_k = np.zeros((H, W), int)
    for j, (d, _) in enumerate(inks):
        a = (Db @ d) / max(1e-6, d @ d)
        res = np.linalg.norm(Db - a[..., None] * d, axis=-1)
        better = res < best_r
        best_r[better], best_a[better], best_k[better] = res[better], a[better], j
    # coverage of the chosen ink, sharpened and thresholded into crisp line art
    cov = np.zeros((H, W))
    for j, (d, _) in enumerate(inks):
        a = (D @ d) / max(1e-6, d @ d)
        cov[best_k == j] = a[best_k == j]
    if tune.get("pre"):
        # the catalogue photos resolve ~3 mm: smooth their JPEG blocks away before the threshold (continuous lines)
        ps = tune["pre"] * ppm
        cov = blur(cov, ps, ps)
    sig = tune.get("sig", 1.2) * ppm / 2
    cov = cov + tune.get("sharp", 1.0) * (cov - blur(cov, sig, sig))
    if tune.get("adapt"):
        # adaptive: coverage relative to the strongest line nearby (faint and strong strokes alike become crisp)
        n = int(tune.get("adapt_mm", 14) * ppm) | 1
        lm = np.asarray(Image.fromarray(np.clip(cov * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(n)), float) / 255
        lm = blur(lm, n / 3, n / 3)
        cov = cov / np.maximum(lm, tune.get("floor", 0.22))
    lo, hi = tune.get("lo", 0.2), tune.get("hi", 0.45)
    # in and around the in-painted holes only strong (crossing) lines survive: soft smudges of the handle's ends
    # and shadow go
    zone = blur(grow(hmask, 4 * ppm).astype(float), 2 * ppm, 2 * ppm) * tune.get("zone_k", 0.25)
    A = smoothstep(lo + zone, hi + zone, cov)
    A = np.asarray(Image.fromarray(np.round(A * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3)), float) / 255
    inkc = np.zeros((H, W, 3))
    for j, (_, c) in enumerate(inks):
        inkc[best_k == j] = c
    # ink colour edges: spread the choice from the core outwards (avoid per-pixel flicker)
    out = cream * (1 - A[..., None]) + inkc * A[..., None]
    # transplants: a clean copy of the same artwork from a sharper source (site photo) over an unreadable one
    for tp in tune.get("transplant", []):
        out, A = transplant(out, A, ppm, h, tp)
    stats = dict(ppm=ppm, size=(W, H), inks=[rgb_hex(c) for _, c in inks], holes=nholes,
                 cover=float(A.mean()), _A=A)
    return out, stats, S


_CACHE = {}


def cleaned(motif):
    if motif not in _CACHE:
        _CACHE[motif] = clean_british(motif, fronts()[motif][0], TUNE.get(motif, {}))
    return _CACHE[motif]


def transplant(out, A, ppm, h, tp):
    """tp: donor motif, src [x0, y0, x1, y1] mm on the donor (y up), optional `drop` circles [[x, y, r], …] mm on
    the donor, `rot` degrees (counter-clockwise), `scale`, `at` [x, y] mm = where the src centre lands, `clear`
    [x0, y0, x1, y1] mm on the target (set to ground first)."""
    d_out, d_st, _ = cleaned(tp["donor"])
    dp, dh = d_st["ppm"], fronts()[tp["donor"]][0]["h"]
    x0, y0, x1, y1 = tp["src"]
    Ad = d_st["_A"].copy()
    yy, xx = np.mgrid[0:Ad.shape[0], 0:Ad.shape[1]]
    for cx, cy, r in tp.get("drop", []):
        Ad[(xx / dp - cx) ** 2 + ((dh - yy / dp) - cy) ** 2 < r * r] = 0
    box = (int(x0 * dp), int((dh - y1) * dp), int(x1 * dp), int((dh - y0) * dp))
    col = Image.fromarray(np.round(d_out * 255).astype(np.uint8)).crop(box)
    alp = Image.fromarray(np.round(Ad * 255).astype(np.uint8)).crop(box)
    k = tp.get("scale", 1.0) * ppm / dp
    size = (max(1, int(round(col.size[0] * k))), max(1, int(round(col.size[1] * k))))
    col, alp = col.resize(size, Image.LANCZOS), alp.resize(size, Image.LANCZOS)
    if tp.get("rot"):
        col = col.rotate(tp["rot"], Image.BICUBIC, expand=True, fillcolor=tuple(int(v * 255) for v in hex_rgb(CREAM)))
        alp = alp.rotate(tp["rot"], Image.BICUBIC, expand=True, fillcolor=0)
    out, A = out.copy(), A.copy()
    H, W = A.shape
    cream = hex_rgb(CREAM)
    if tp.get("clear"):
        c0, c1_, c2, c3 = tp["clear"]
        sl = (slice(max(0, int((h - c3) * ppm)), int((h - c1_) * ppm)), slice(max(0, int(c0 * ppm)), int(c2 * ppm)))
        out[sl] = cream
        A[sl] = 0
    cx, cy = tp["at"]
    px, py = int(round(cx * ppm - col.size[0] / 2)), int(round((h - cy) * ppm - col.size[1] / 2))
    c = np.asarray(col, float) / 255
    a = (np.asarray(alp, float) / 255)[..., None]
    ys, xs = slice(max(0, py), min(H, py + c.shape[0])), slice(max(0, px), min(W, px + c.shape[1]))
    cy_, cx_ = slice(ys.start - py, ys.stop - py), slice(xs.start - px, xs.stop - px)
    out[ys, xs] = out[ys, xs] * (1 - a[cy_, cx_]) + c[cy_, cx_] * a[cy_, cx_]
    A[ys, xs] = np.maximum(A[ys, xs], a[cy_, cx_, 0])
    return out, A


def build_british(only=None):
    fr = fronts()
    results = {}
    for motif in sorted(p.stem for p in CROPS.glob("*.png")):
        if only and motif not in only:
            continue
        info = fr[motif][0]
        out, st, S = clean_british(motif, info, TUNE.get(motif, {}))
        mid = f"cgprint_british_bum_{motif}"
        fo = folder(mid)
        to_img(out).save(fo / f"{mid}_albedo.jpg", quality=93, subsampling=0, optimize=True)
        flat_normal().save(fo / f"{mid}_normal.jpg", quality=95)
        const_mask().save(fo / f"{mid}_mask.png", optimize=True)
        st["fronts"] = [f"{e['design']} {e['part']} {e['w']:g}×{e['h']:g}" for e in fr[motif]]
        st["w"], st["h"] = info["w"], info["h"]
        results[motif] = st
        st.pop('_A', None)
        print(f"{mid}: {st['size'][0]}×{st['size'][1]} px ({st['ppm']:.2f} px/mm), inks {st['inks']}, "
              f"holes {st['holes']}, cover {st['cover']:.3f}")
    return results


def british_entries():
    es = []
    for motif in sorted(p.stem for p in CROPS.glob("*.png")):
        mid = f"cgprint_british_bum_{motif}"
        es.append(entry(mid, f"Бритиш Бум — фотопечать «{MOTIF_NAMES.get(motif, motif)}»", (1.0, 1.0)))
    return es


# =============================================================================================== Элиза «розы»
ELIZA_MM = (264.0, 60.0)          # the median ornament ellipse (220×44 … 320×60, aspect 3.7–5.3: the decal is fitted)
ELIZA_PX = (1536, 352)
GOLD = "#c9a45c"                  # the collection's gilding (finish role `patina`)
GOLD_LIGHT = "#dcc08a"            # the raised petals catch light: a paler gold fill
GOLD_DARK = "#9a7a3f"             # the incised outlines


def _ellipse_pts(cx, cy, rx, ry, rot=0.0, n=48):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x, y = rx * np.cos(t), ry * np.sin(t)
    c, s_ = math.cos(rot), math.sin(rot)
    return [(cx + c * a - s_ * b, cy + s_ * a + c * b) for a, b in zip(x, y)]


def _leaf_pts(cx, cy, length, width, rot, bend=0.12, n=40):
    """A pointed leaf (two arcs) along its axis `rot`, base at (cx, cy)."""
    t = np.linspace(0, 1, n)
    half = width / 2 * np.sin(np.pi * t) ** 0.8
    ax = t * length
    mid = bend * length * np.sin(np.pi * t)
    top = [(a, m + h) for a, m, h in zip(ax, mid, half)]
    bot = [(a, m - h) for a, m, h in zip(ax[::-1], mid[::-1], half[::-1])]
    c, s_ = math.cos(rot), math.sin(rot)
    return [(cx + c * a - s_ * b, cy + s_ * a + c * b) for a, b in top + bot]


def _rose(draw_fill, draw_line, cx, cy, r, squash=1.0, turn=0.0):
    """A stylised rose: two rings of round petals and a spiral heart (drawn back to front)."""
    for k in range(6):                                            # outer petals
        a = turn + k * math.pi / 3
        pts = _ellipse_pts(cx + 0.55 * r * math.cos(a), cy + 0.55 * r * math.sin(a) * squash, 0.5 * r, 0.42 * r * squash,
                           a)
        draw_fill(pts)
        draw_line(pts)
    for k in range(5):                                            # inner petals
        a = turn + 0.3 + k * 2 * math.pi / 5
        pts = _ellipse_pts(cx + 0.28 * r * math.cos(a), cy + 0.28 * r * math.sin(a) * squash, 0.33 * r, 0.26 * r * squash, a)
        draw_fill(pts)
        draw_line(pts)
    sp = []                                                       # the heart: a spiral
    for i in range(60):
        t = i / 59
        a = turn + t * 3.2 * math.pi
        rr = 0.26 * r * (1 - t) + 0.03 * r
        sp.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * squash))
    draw_line(sp, closed=False)


def build_eliza():
    W, H = ELIZA_PX
    ss = 4
    k = W * ss / ELIZA_MM[0]                                     # supersampled px per mm
    Wm, Hm = ELIZA_MM
    hgt = Image.new("L", (W * ss, H * ss), 0)                    # relief: 0 ground, 255 top of the gilding
    fillm = Image.new("L", (W * ss, H * ss), 0)                  # where the pale gold fill is
    linem = Image.new("L", (W * ss, H * ss), 0)                  # the dark incised lines
    dh, df, dl = ImageDraw.Draw(hgt), ImageDraw.Draw(fillm), ImageDraw.Draw(linem)
    lw = max(2, int(round(0.9 * k)))                             # 0.9 mm lines

    def P(pts):
        # the part is an ellipse inscribed in the box: the spray is kept inside it (ends drawn in towards the middle)
        out = []
        for x, y in pts:
            ux = (x - Wm / 2) / (Wm / 2) * 0.9
            x2 = Wm / 2 + ux * Wm / 2
            y2 = Hm / 2 + (y - Hm / 2) * (1 - 0.35 * ux * ux)
            out.append((x2 * k, (Hm - y2) * k))
        return out

    def fill(pts):
        q = P(pts)
        df.polygon(q, fill=255)
        dh.polygon(q, fill=200)
        dl.polygon(q, fill=0)                                     # a petal in front hides the lines behind it

    def line(pts, closed=True):
        q = P(pts)
        if closed:
            q = q + q[:1]
        dl.line(q, fill=255, width=lw, joint="curve")
        dh.line(q, fill=120, width=lw, joint="curve")

    cx, cy = Wm / 2, Hm / 2
    # p. 108: three rose heads side by side (the middle one larger), small leaves round them, a bud and a curl at
    # each end, a short stem hanging from the middle
    for sgn in (-1, 1):                                          # the spray is mirror-symmetric
        st = [(cx + sgn * (6 + 70 * t), cy - 4 + 6 * math.sin(t * math.pi * 1.4) - 3 * t) for t in np.linspace(0, 1, 50)]
        dl.line(P(st), fill=255, width=lw, joint="curve")
        dh.line(P(st), fill=160, width=int(lw * 1.3), joint="curve")
        tw = [(cx + sgn * (74 + 12 * t + 2 * math.sin(t * 8)), cy + 2 + 8 * t * math.cos(t * 5)) for t in np.linspace(0, 1, 40)]
        dl.line(P(tw), fill=255, width=max(2, lw * 3 // 4), joint="curve")
        dh.line(P(tw), fill=140, width=lw, joint="curve")
        for bx, by, L, Wd, ang in ((14, -14, 14, 6.5, -0.9), (16, 12, 13, 6, 0.8), (46, -11, 15, 6.5, -0.45),
                                   (47, 9, 14, 6, 0.5), (62, -6, 14, 6, -0.2), (64, 5, 12, 5.5, 0.55)):
            a = ang if sgn > 0 else math.pi - ang
            pts = _leaf_pts(cx + sgn * bx, cy + by, L, Wd, a, bend=0.1 * sgn)
            fill(pts)
            line(pts)
            rib = [(cx + sgn * bx + math.cos(a) * L * t, cy + by + math.sin(a) * L * t + 0.1 * sgn * L * math.sin(math.pi * t))
                   for t in np.linspace(0.05, 0.85, 12)]
            line(rib, closed=False)
        _rose(fill, line, cx + sgn * 31, cy + 1, 13.0, squash=0.85, turn=0.4 * sgn)
        bud = _leaf_pts(cx + sgn * 80, cy - 1, 8, 6.5, math.pi / 2 + sgn * 0.6, bend=0.0)
        fill(bud)
        line(bud)
    hang = [(cx + 2 * math.sin(t * 3), cy - 10 - 9 * t) for t in np.linspace(0, 1, 20)]
    dl.line(P(hang), fill=255, width=lw, joint="curve")
    dh.line(P(hang), fill=160, width=int(lw * 1.3), joint="curve")
    hb = _leaf_pts(cx, cy - 17, 7, 5.5, -math.pi / 2, bend=0.0)
    fill(hb)
    line(hb)
    _rose(fill, line, cx, cy + 2, 17.0, squash=1.0, turn=0.15)

    down = lambda im: np.asarray(im.resize((W, H), Image.LANCZOS), float) / 255
    F, L_, Hh = down(fillm), down(linem), down(hgt)
    ground = hex_rgb(VANILLA)
    gold, gl, gd = hex_rgb(GOLD), hex_rgb(GOLD_LIGHT), hex_rgb(GOLD_DARK)
    alb = ground * (1 - F[..., None]) + gl * F[..., None]
    lineA = np.clip(L_ * 1.2, 0, 1)[..., None]
    alb = alb * (1 - lineA) + gd * lineA
    # a gilded edge round every fill (the relief's rim catches the gilding)
    rim = np.clip(np.abs(F - blur(F, 1.2, 1.2)) * 4, 0, 1)[..., None]
    alb = alb * (1 - rim * 0.6) + gold * rim * 0.6
    fo = folder("cgprint_eliza_rozy")
    to_img(alb).save(fo / "cgprint_eliza_rozy_albedo.jpg", quality=93, subsampling=0, optimize=True)
    height_to_normal(blur(Hh, 1.2, 1.2), 2.2).save(fo / "cgprint_eliza_rozy_normal.jpg", quality=93, subsampling=0)
    goldness = np.clip(F + L_, 0, 1)
    m = np.zeros((H, W, 4), np.uint8)
    m[..., 0] = np.round(goldness * 230)                         # gilding: metallic
    m[..., 1] = np.round(255 - 40 * np.clip(L_, 0, 1))           # a little AO in the incised lines
    m[..., 3] = np.round((0.30 + goldness * 0.32) * 255)         # matt vanilla film / satin gold
    Image.fromarray(m, "RGBA").save(fo / "cgprint_eliza_rozy_mask.png", optimize=True)
    print(f"cgprint_eliza_rozy: {W}×{H}, gold cover {goldness.mean():.3f}, mean {rgb_hex(alb.reshape(-1, 3).mean(0))}")
    return alb


# =============================================================================================== Мартина «листья»
MARTINA_TILE = (0.5, 0.25)        # m: U along the grain (the leaves' axis) × V
MARTINA_PX = (2048, 1024)         # 4.1 px/mm
MILK = "#eeeeea"                  # the carved leaves: milk-white paint (lighter than the flat body swatch #e3e3e0)
SWATCH_CARVE = "#c8c9c8"          # target mean: the p. 48 swatch carved panel reads #c1c1c0 printed; the renders need it light
RECESS_RANGE = ("#a9abad", "#b8babc")   # light silver-grey patina paint in the recesses


def build_martina(ground_hex=None):
    W, H = MARTINA_PX
    ppm = W / (MARTINA_TILE[0] * 1000)
    rng = np.random.default_rng(573)
    ss = 2
    hgt = Image.new("L", (W * ss, H * ss), 0)
    edge = Image.new("L", (W * ss, H * ss), 0)                   # incised outlines / midribs (patina lines)
    dh, de = ImageDraw.Draw(hgt), ImageDraw.Draw(edge)
    k = ppm * ss
    # sinuous stems along U (3 across the 250 mm of V) with broad leaves branching alternately off them, leaning ±35°
    # (the p. 45–48 doors: leaves ~100 × 35 mm, heavy overlap, a stem network between them)
    items = []
    n_st, per = 3, 8
    for si in range(n_st):
        v0 = (si + 0.5) * 250 / n_st
        amp, ph = rng.uniform(6, 10), rng.uniform(0, 2 * np.pi)
        stem = lambda u, v0=v0, amp=amp, ph=ph: v0 + amp * math.sin(2 * math.pi * u / 250 + ph)
        items.append(("stem", [(u, stem(u)) for u in np.linspace(-20, 520, 110)]))
        for j in range(per):
            u = (j + rng.uniform(0.1, 0.4) + 0.5 * (si % 2)) * 500 / per
            side = 1 if (j + si) % 2 else -1
            lean = math.radians(side * rng.uniform(22, 50))
            slope = math.atan2(stem(u + 1) - stem(u - 1), 2)
            L, Wd = rng.uniform(90, 115), rng.uniform(33, 44)
            items.append(("leaf", (u, stem(u), L, Wd, slope + lean, rng.uniform(-0.1, 0.1) * side)))
    for _ in range(3):                                           # loose leaves filling the gaps (the carving is dense)
        ang = math.radians(rng.choice((-1, 1)) * rng.uniform(20, 45))
        items.append(("leaf", (rng.uniform(0, 500), rng.uniform(0, 250), rng.uniform(80, 105), rng.uniform(30, 40), ang,
                               rng.uniform(-0.1, 0.1))))
    stems = [it for it in items if it[0] == "stem"]
    leaves = [it for it in items if it[0] == "leaf"]
    rng.shuffle(leaves)
    for kind, data in stems + leaves:
        for ou in (-500, 0, 500):                                 # periodic: draw the wrapped copies
            for ov in (-250, 0, 250):
                if kind == "stem":
                    q = [((x + ou) * k, (y + ov) * k) for x, y in data]
                    dh.line(q, fill=255, width=int(7 * k), joint="curve")
                    de.line(q, fill=0, width=int(7 * k), joint="curve")
                    continue
                u, v, L, Wd, ang, bend = data
                pts = _leaf_pts(u, v, L, Wd, ang, bend=bend, n=40)
                rib = [(u + math.cos(ang) * L * t - math.sin(ang) * bend * L * math.sin(math.pi * t),
                        v + math.sin(ang) * L * t + math.cos(ang) * bend * L * math.sin(math.pi * t))
                       for t in np.linspace(0.05, 0.88, 16)]
                q = [((x + ou) * k, (y + ov) * k) for x, y in pts]
                r = [((x + ou) * k, (y + ov) * k) for x, y in rib]
                dh.polygon(q, fill=255)
                de.polygon(q, fill=0)                             # a leaf on top hides the lines under it
                de.line(q + q[:1], fill=255, width=max(2, int(2.0 * k)), joint="curve")
                de.line(r, fill=170, width=max(2, int(1.4 * k)), joint="curve")
    box2 = lambda im: (np.asarray(im, float) / 255).reshape(H, ss, W, ss).mean((1, 3))   # exact: stays periodic
    Hh = box2(hgt)                                                         # 1 = leaf face, 0 = recessed ground
    E = box2(edge)
    # relief: leaves 2.5 mm proud with rounded (milled) edges, V-cut outlines and midribs
    rel = wblur(Hh, 0.9 * ppm, 0.9 * ppm) * 2.5 - E * 0.9                  # mm
    rel = rel + 0.08 * gauss_noise(rng, (H, W), 3 * ppm, 3 * ppm)         # hand-finish unevenness
    # colours: milk-white leaves, silver-grey patina in the recess and in the cut lines, a soft transition
    cover = float(Hh.mean())
    milk = srgb_to_linear(hex_rgb(MILK))
    target = srgb_to_linear(hex_rgb(SWATCH_CARVE))
    lines_w = float((E * Hh).mean())
    if ground_hex is None:                                       # solve the silver ground so the mean hits the swatch
        grey = (target - milk * (cover - 0.55 * lines_w)) / max(1e-3, 1 - cover + 0.55 * lines_w)
        lo_, hi_ = (srgb_to_linear(hex_rgb(c)) for c in RECESS_RANGE)
        grey = np.clip(grey, lo_, hi_)
    else:
        grey = srgb_to_linear(hex_rgb(ground_hex))
    t = np.clip(wblur(Hh, 0.6 * ppm, 0.6 * ppm), 0, 1)[..., None]
    tone = 1 + 0.05 * gauss_noise(rng, (H, W), 25 * ppm, 25 * ppm)[..., None]   # patina clouds
    # the patina also lies softly on the leaves' milled flanks (p. 48: white relief, grey-silver shading towards the
    # recesses): a band along each leaf edge, its strength solved so the mean lands on the target (leaf centres stay milk)
    band = np.clip(1 - (wblur(Hh, 4.5 * ppm, 4.5 * ppm) - 0.45) / 0.5, 0, 1)[..., None] * t
    base = grey * tone * (1 - t) + milk * t
    base = base * (1 - 0.55 * (E * Hh)[..., None]) + grey * tone * 0.55 * (E * Hh)[..., None]
    tl = linear_to_lab(target)[0]
    lo_k, hi_k = 0.0, 1.0
    for _ in range(30):
        kk = (lo_k + hi_k) / 2
        lin = base * (1 - kk * band) + grey * tone * kk * band
        if linear_to_lab(lin.reshape(-1, 3).mean(0))[0] > tl:
            lo_k = kk
        else:
            hi_k = kk
    alb = linear_to_srgb(np.clip(lin, 0, 1))
    fo = folder("cg_martina_listya")
    to_img(alb).save(fo / "cg_martina_listya_albedo.jpg", quality=92, subsampling=0, optimize=True)
    nrm_rel = rel.reshape(H // 2, 2, W // 2, 2).mean((1, 3))           # an exact 2× box: stays periodic
    height_to_normal(nrm_rel * (512 / (MARTINA_TILE[1] * 1000)), 1.0).save(
        fo / "cg_martina_listya_normal.jpg", quality=93, subsampling=0)
    # mask: silver patina (metallic, satin) in the recesses and cut lines; matt paint on the leaves; AO from depth
    # the patina is paint: not metallic (a faint 0.15 only in the deepest cut lines), satin; AO moderate (≥ 0.7)
    silver = np.clip((1 - t[..., 0]) + 0.6 * E * Hh, 0, 1)
    ao = np.clip(1 - 0.2 * (1 - wblur(Hh, 2.5 * ppm, 2.5 * ppm)) - 0.12 * E, 0.7, 1)
    m = np.zeros((H, W, 4), np.float64)
    m[..., 0] = 0.15 * np.clip(E * Hh * 1.5 - 0.5, 0, 1)
    m[..., 1] = ao
    m[..., 3] = 0.24 + silver * 0.1
    mimg = Image.fromarray(np.round(m.reshape(H // 2, 2, W // 2, 2, 4).mean((1, 3)) * 255).astype(np.uint8), "RGBA")
    mimg.save(fo / "cg_martina_listya_mask.png", optimize=True)
    mean = alb.reshape(-1, 3).mean(0)
    mean_lin = linear_to_srgb(lin.reshape(-1, 3).mean(0))
    print(f"cg_martina_listya: {W}×{H}, leaves cover {cover:.2f}, ground {rgb_hex(linear_to_srgb(grey))}, "
          f"mean {rgb_hex(mean_lin)} (ΔE76 {de76(mean_lin, hex_rgb(SWATCH_CARVE)):.2f} to {SWATCH_CARVE})")
    return alb, dict(ground=rgb_hex(linear_to_srgb(grey)), mean=rgb_hex(mean_lin), cover=cover,
                     de=de76(mean_lin, hex_rgb(SWATCH_CARVE)))


# =============================================================================================== Кен «ёлочка»
KEN_INK = "#3b2e27"               # the UV print's lines (p. 70, the darkest line cores)
KEN_PPM = 2.0


def ken_fronts():
    """Unique front sizes / line sets of the ёлочка fronts: id suffix → (w, h, lines local mm, users)."""
    out = {}
    for f in sorted(DESIGNS.glob("ken-*.json")):
        for p in json.loads(f.read_text())["parts"]:
            fc = p.get("face") or {}
            if fc.get("type") != "grooves":
                continue
            b = p["box"]
            x0, y0 = min(b[0], b[3]), min(b[1], b[4])
            w, h = abs(b[3] - b[0]), abs(b[4] - b[1])
            lines = tuple(sorted(tuple(round(v, 2) for v in (l[0] - x0, l[1] - y0, l[2] - x0, l[3] - y0)) for l in fc["lines"]))
            key = None
            for kk, e in out.items():
                if e["lines"] == lines and e["w"] == w and e["h"] == h:
                    key = kk
            if key is None:
                key = f"{int(round(w))}x{int(round(h))}"
                if key in out:
                    key += "_" + p["id"].replace("f-", "").replace("-", "_")
                    first = out.pop(f"{int(round(w))}x{int(round(h))}")
                    out[f"{int(round(w))}x{int(round(h))}_" + first["users"][0].split()[1].replace("f-", "").replace("-", "_")] = first
                out[key] = dict(w=w, h=h, lines=lines, users=[], width=fc.get("w", 2.5))
            out[key]["users"].append(f"{f.stem} {p['id']}")
    return out


def build_ken():
    res = {}
    ink = hex_rgb(KEN_INK)
    for key, e in ken_fronts().items():
        W, H = int(round(e["w"] * KEN_PPM)), int(round(e["h"] * KEN_PPM))
        ss = 4
        im = Image.new("L", (W * ss, H * ss), 0)
        d = ImageDraw.Draw(im)
        k = KEN_PPM * ss
        for x0, y0, x1, y1 in e["lines"]:
            d.line([(x0 * k, (e["h"] - y0) * k), (x1 * k, (e["h"] - y1) * k)], fill=255, width=int(round(e["width"] * k)))
        a = np.asarray(im.resize((W, H), Image.LANCZOS), float) / 255
        rgba = np.zeros((H, W, 4), np.uint8)
        rgba[..., :3] = np.round(ink * 255)
        rgba[..., 3] = np.round(a * 255)
        mid = f"cgprint_ken_elochka_{key}"
        fo = folder(mid)
        Image.fromarray(rgba, "RGBA").save(fo / f"{mid}_albedo.png", optimize=True)
        flat_normal().save(fo / f"{mid}_normal.jpg", quality=95)
        const_mask(smooth=0.0).save(fo / f"{mid}_mask.png", optimize=True)
        res[key] = dict(e, px=(W, H), cover=float(a.mean()))
        print(f"{mid}: {W}×{H}, lines {len(e['lines'])}, for {', '.join(e['users'])}")
    return res


# =============================================================================================== entries, sheet
def all_entries():
    es = british_entries()
    es.append(entry("cgprint_eliza_rozy", "Элиза — золотой орнамент «розы» (печать)", (1.0, 1.0)))
    es.append(entry("cg_martina_listya", "Мартина — резьба «листья» под серебряной патиной («Молоко с серебром»)",
                    MARTINA_TILE))
    for key, e in ken_fronts().items():
        es.append(entry(f"cgprint_ken_elochka_{key}", f"Кен — УФ печать «ёлочка», фасад {e['w']:g}×{e['h']:g}",
                        (1.0, 1.0), albedo_ext="png", transparent=True))
    ENTRIES.parent.mkdir(parents=True, exist_ok=True)
    ENTRIES.write_text(json.dumps(es, ensure_ascii=False, indent=1))
    print(f"{ENTRIES.relative_to(ROOT)}: {len(es)} entries")
    return es


def _catpage(page, crop, dpi=300):
    import pymupdf                                                # only the sheet needs the catalogue
    doc = pymupdf.open(ROOT / "tools" / "casegoods" / "reference" / "catalog_km2.pdf")
    pg = doc[page - 1]
    r = pg.rect
    x0, y0, x1, y1 = crop
    clip = pymupdf.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height, r.x0 + x1 * r.width, r.y0 + y1 * r.height)
    pix = pg.get_pixmap(dpi=dpi, clip=clip)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def _fit_h(im, h):
    return im.resize((max(1, int(round(im.size[0] * h / im.size[1]))), h), Image.LANCZOS)


def _fit_w(im, w):
    return im.resize((w, max(1, int(round(im.size[1] * w / im.size[0])))), Image.LANCZOS)


def _shade(mid, tile_px=None, light=(-0.5, 0.6, 0.62), amb=0.35, key=0.8):
    """Albedo lit by the normal map (Lambert + ambient) × AO: a quick relief preview."""
    fo = EXT / "Materials" / mid
    alb = np.asarray(Image.open(fo / f"{mid}_albedo.jpg").convert("RGB"), float) / 255
    H, W = alb.shape[:2]
    n = np.asarray(Image.open(fo / f"{mid}_normal.jpg").convert("RGB").resize((W, H), Image.BICUBIC), float) / 127.5 - 1
    m = np.asarray(Image.open(fo / f"{mid}_mask.png").convert("RGBA").resize((W, H), Image.BICUBIC), float) / 255
    l = np.array(light) / np.linalg.norm(light)
    lam = np.clip(n @ l, 0, 1)
    return to_img(np.clip(alb * (amb + key * lam[..., None]) * m[..., 1:2], 0, 1))


def sheet():
    from PIL import ImageFont
    font = ImageFont.load_default()
    blocks = []

    def label(im, text):
        c = Image.new("RGB", (im.size[0], im.size[1] + 16), "white")
        c.paste(im, (0, 16))
        ImageDraw.Draw(c).text((2, 2), text, fill=(20, 20, 160), font=font)
        return c

    def row(ims, gap=10, bg="white"):
        h = max(i.size[1] for i in ims)
        r = Image.new("RGB", (sum(i.size[0] for i in ims) + gap * (len(ims) - 1), h), bg)
        x = 0
        for i in ims:
            r.paste(i, (x, 0))
            x += i.size[0] + gap
        return r

    fr = fronts()
    motifs = sorted(p.stem for p in CROPS.glob("*.png"))
    tall = [m for m in motifs if fr[m][0]["h"] >= 1000]
    small = [m for m in motifs if fr[m][0]["h"] < 1000 and fr[m][0]["h"] > fr[m][0]["w"] * 0.6]
    wide = [m for m in motifs if m not in tall and m not in small]

    def pair(m, h=None, w=None):
        mid = f"cgprint_british_bum_{m}"
        res = Image.open(EXT / "Materials" / mid / f"{mid}_albedo.jpg").convert("RGB")
        src = Image.open(CROPS / f"{m}.png").convert("RGB").resize(res.size, Image.BICUBIC)
        if h:
            src, res = _fit_h(src, h), _fit_h(res, h)
            return label(row([src, res], gap=3, bg="red"), m[:24])
        src, res = _fit_w(src, w), _fit_w(res, w)
        c = Image.new("RGB", (w, src.size[1] * 2 + 3), "red")
        c.paste(src, (0, 0))
        c.paste(res, (0, src.size[1] + 3))
        return label(c, f"{m}  {fr[m][0]['w']:g} x {fr[m][0]['h']:g} mm")

    blocks.append(label(row([pair(m, h=760) for m in tall]), "British Bum - tall doors: source crop | cgprint_british_bum_* (fitted to the whole front, up = +y)"))
    blocks.append(label(row([pair(m, h=420) for m in small]), "British Bum - small doors"))
    ws = [pair(m, w=780) for m in wide]
    for i in range(0, len(ws), 4):
        blocks.append(row(ws[i:i + 4]))

    # Элиза
    cat = [_fit_h(_catpage(108, c, 400), 150) for c in ((0.07, 0.53, 0.13, 0.57), (0.205, 0.42, 0.245, 0.47),
                                                        (0.05, 0.225, 0.1, 0.26))]
    tex = Image.open(EXT / "Materials" / "cgprint_eliza_rozy" / "cgprint_eliza_rozy_albedo.jpg").convert("RGB")
    fits = []
    for w, h in ((220, 44), (250, 68), (320, 60)):
        im = tex.resize((w * 2, h * 2), Image.LANCZOS)
        mk = Image.new("L", im.size, 0)
        ImageDraw.Draw(mk).ellipse([0, 0, im.size[0] - 1, im.size[1] - 1], fill=255)
        bg = Image.new("RGB", (im.size[0] + 12, im.size[1] + 12), hex_rgb_to_tuple(VANILLA))
        ring = Image.new("RGB", im.size, hex_rgb_to_tuple(GOLD))
        bg.paste(ring, (6, 6), mk)
        inner = mk.resize((im.size[0] - 2, im.size[1] - 2))
        bg.paste(im.resize(inner.size), (7, 7), inner)
        fits.append(label(bg, f"on the {w} x {h} ellipse"))
    blocks.append(label(row(cat + [_fit_h(_shade("cgprint_eliza_rozy"), 180)] + fits),
                        "Eliza roses: p. 108 (chest, door medallion, crest) | cgprint_eliza_rozy lit | fitted to the -orn ellipses (gold rim = role ornament)"))
    # Мартина
    sw = _fit_h(_catpage(48, (0.70, 0.855, 0.78, 0.905)), 300)
    door = _fit_h(_catpage(48, (0.36, 0.45, 0.43, 0.58)), 300)
    alb = Image.open(EXT / "Materials" / "cg_martina_listya" / "cg_martina_listya_albedo.jpg").convert("RGB")
    lit = _shade("cg_martina_listya", amb=0.62, key=0.5)                  # a light studio: soft key + ambient
    # a door panel 310 × 442 mm (U = the panel's long side = y): the tile rotated, 1:1 m at 0.7 px/mm
    pnl = Image.new("RGB", (int(310 * 0.7), int(442 * 0.7)))
    tile = lit.rotate(90, expand=True).resize((int(250 * 0.7), int(500 * 0.7)), Image.LANCZOS)
    for x in range(0, pnl.size[0], tile.size[0]):
        for y in range(0, pnl.size[1], tile.size[1]):
            pnl.paste(tile, (x, y))
    blocks.append(label(row([sw, door, _fit_h(alb, 300), _fit_h(lit, 300), _fit_h(pnl, 300)]),
                        "Martina leaves: p. 48 swatch Moloko s serebrom | p. 48 interior door | cg_martina_listya albedo (0.5 x 0.25 m) | simulated lit (normal x AO, studio) | a lit 310 x 442 mm door panel, 1:1 (leaves along U = y)"))
    # Кен
    kc = _fit_h(_catpage(70, (0.215, 0.44, 0.32, 0.6)), 300)
    kens = []
    for key, e in ken_fronts().items():
        mid = f"cgprint_ken_elochka_{key}"
        dec = Image.open(EXT / "Materials" / mid / f"{mid}_albedo.png").convert("RGBA")
        base = Image.new("RGBA", dec.size, hex_rgb_to_tuple("#a8937c") + (255,))
        kens.append(label(_fit_h(Image.alpha_composite(base, dec).convert("RGB"), 300), key))
    blocks.append(label(row([kc] + kens), "Ken elochka: p. 70 | transparent decals over the oak (provisional #a8937c), the lines where the designs' V-grooves are"))

    Wd = max(b.size[0] for b in blocks)
    out = Image.new("RGB", (Wd + 20, sum(b.size[1] + 14 for b in blocks) + 10), "white")
    y = 10
    for b in blocks:
        out.paste(b, (10, y))
        y += b.size[1] + 14
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    out.save(SHEET, optimize=True)
    print(f"{SHEET.relative_to(ROOT)}: {out.size[0]}×{out.size[1]}")


def hex_rgb_to_tuple(h):
    return tuple(int(round(v * 255)) for v in hex_rgb(h))


# =============================================================================================== main
def main(argv):
    what = argv[0] if argv else "all"
    if what in ("british", "all"):
        build_british(set(argv[1:]) or None)
    if what in ("eliza", "all"):
        build_eliza()
    if what in ("martina", "all"):
        build_martina()
    if what in ("ken", "all"):
        build_ken()
    if what in ("all", "entries"):
        all_entries()
    if what in ("all", "sheet"):
        sheet()


if __name__ == "__main__":
    main(sys.argv[1:])
