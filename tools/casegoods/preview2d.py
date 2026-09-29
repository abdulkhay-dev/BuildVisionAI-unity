#!/usr/bin/env python3
"""Checks and 2D drawings of a case furniture design (Docs/casegoods-designs.md) — no Unity needed.

    python3 tools/casegoods/preview2d.py Assets/House4696/Resources/Casegoods/Designs/flora-0-01.json
        [--ref tools/casegoods/reference/flora/front/flora-0-01.png] [--out tools/casegoods/pilot/flora-0-01.png]
        [--finish flora-samshit] [--pxmm 0.35] [--open]

Checks (printed; exit code 1 on errors):
  * every row of the assembly instruction's cut list (the model's "is" PDF, read by cutlist.py) is built — by parts with
    that "n" or by "covers" — as many times as the list says, and every part's box has the listed sizes (±1 mm);
  * the parts' extent equals the catalogue size [L, B, H] (±1 mm);
  * solid parts that are not in one moving group do not overlap (more than 0.6 mm in every axis).
Drawing: front, left side and top views (orthographic, near parts over far ones) and, with --ref, the reference front
view (a crop of the instruction's drawing or a photo, tight round the piece incl. legs) scaled to the same extent with
our edges in red over it.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CATALOG = os.path.join(ROOT, "Assets/House4696/Resources/Casegoods/catalog.json")
sys.path.insert(0, HERE)
import cutlist  # noqa: E402

SOLID = {"panel", "back", "front", "glass", "mirror", "tube"}


def hex_rgb(h, default=(200, 200, 200)):
    if not h:
        return default
    h = h.split("#")[-1]
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return default


def load(path):
    with open(path) as fh:
        d = json.load(fh)
    with open(CATALOG) as fh:
        cat = json.load(fh)
    did = d.get("id") or os.path.splitext(os.path.basename(path))[0]
    model = next((m for m in cat["models"] if (m.get("design") or m["id"]) == did), None)
    return d, cat, model


def pid(p):
    return p.get("id") or p.get("n")


def box_of(p):
    b = p.get("box")
    if b:
        return [min(b[0], b[3]), min(b[1], b[4]), min(b[2], b[5]), max(b[0], b[3]), max(b[1], b[4]), max(b[2], b[5])]
    if p.get("kind") == "handle" and p.get("at"):
        r = p.get("d", 80) / 2
        x, y, z = p["at"][0], p["at"][1], p.get("z", 0)
        dx, dy = {"up": (0, 1), "down": (0, -1), "left": (-1, 0), "right": (1, 0)}.get(p.get("dir", "up"), (0, 1))
        x0, x1 = (x - r, x + r) if dx == 0 else sorted([x, x + dx * r])
        y0, y1 = (y - r, y + r) if dy == 0 else sorted([y, y + dy * r])
        return [x0, y0, z, x1, y1, z + p.get("standoff", 8) + p.get("t", 6)]
    if p.get("kind") == "moulding":
        prof_w = 41
        pts = p.get("path") or []
        if not pts:
            return None
        plane = p.get("plane", "front")
        a0, a1 = min(q[0] for q in pts), max(q[0] for q in pts)
        b0, b1 = min(q[1] for q in pts), max(q[1] for q in pts)
        z = p.get("z", 0)
        if plane == "front":
            return [a0, b0, z, a1, b1, z + 16]
        if plane == "top":
            return [a0, z, b0, a1, z + 16, b1]
    return None


# ---------------------------------------------------------------------------------------------------------- checks
def check(d, cat, model, is_pdf):
    errors, warns = [], []
    parts = d.get("parts", [])
    size = d.get("size") or (model or {}).get("size")
    # extent
    boxes = [box_of(p) for p in parts]
    boxes = [b for b in boxes if b]
    if boxes and size:
        ext = [max(b[3] for b in boxes) - min(b[0] for b in boxes), max(b[5] for b in boxes) - min(b[2] for b in boxes),
               max(b[4] for b in boxes) - min(b[1] for b in boxes)]
        for name, got, want in zip(("L", "B", "H"), ext, size):
            if abs(got - want) > 1.0:
                errors.append(f"габарит {name}: детали дают {got:g}, каталог {want:g}")
    # ids
    ids = {}
    for p in parts:
        i = pid(p)
        if i is None:
            continue
        if i in ids:
            errors.append(f"id '{i}' повторяется — дайте деталям свои id")
        ids[i] = p
    for mv in d.get("moves", []):
        for i in mv.get("parts", []):
            if i not in ids:
                errors.append(f"движение '{mv.get('name')}': нет детали '{i}'")
    # cut list
    if is_pdf and os.path.exists(is_pdf):
        rows = cutlist.parse(is_pdf)
        if not rows:
            warns.append("таблица деталей не прочитана из PDF — сверьте по картинке страницы")
        listed = {r["n"] for r in rows}
        for r in rows:
            have = [p for p in parts if str(p.get("n")) == r["n"]]
            cov = sum(1 for p in parts for c in (p.get("covers") or []) if str(c) == r["n"])
            label = r.get("name") or r.get("code") or ""
            sizes = " × ".join(f"{s:g}" for s in r["size"]) if r.get("size") else "размеры на чертеже"
            if len(have) + cov != r["count"]:
                errors.append(f'деталь {r["n"]} ({label}, {sizes}): в спецификации {r["count"]} шт, в чертеже {len(have)} + covers {cov}')
            if not r.get("size"):
                continue
            want = sorted(r["size"])
            for p in have:
                b = box_of(p)
                if not b:
                    continue
                got = sorted([b[3] - b[0], b[4] - b[1], b[5] - b[2]])
                # two sizes (the thickness not listed): compare the two biggest
                if len(want) == 2:
                    got = got[1:]
                if any(abs(g - w) > 1.0 for g, w in zip(got, want)):
                    errors.append(f'деталь {pid(p)}: размеры {" × ".join(f"{g:g}" for g in got)}, '
                                  f'по спецификации {" × ".join(f"{w:g}" for w in want)}')
        for p in parts:
            n = p.get("n")
            if n is not None and str(n) not in listed and rows:
                warns.append(f"деталь {pid(p)}: номера {n} нет в спецификации (не прочитан? сверьте по картинке)")
        known = [r["n"] for r in rows]
        print(f"спецификация: {len(rows)} строк ({', '.join(known)})")
    elif is_pdf:
        warns.append(f"нет файла инструкции {is_pdf}")
    # overlaps of solid parts (static ones, and parts of different moving groups)
    group = {}
    for mv in d.get("moves", []):
        for i in mv.get("parts", []):
            group[i] = mv.get("name")
    solid = [p for p in parts if p.get("kind", "panel") in SOLID and p.get("box")]
    for i in range(len(solid)):
        for j in range(i + 1, len(solid)):
            a, b = solid[i], solid[j]
            ga, gb = group.get(pid(a)), group.get(pid(b))
            if ga is not None and ga == gb:
                continue
            A, B = box_of(a), box_of(b)
            ov = [min(A[k + 3], B[k + 3]) - max(A[k], B[k]) for k in range(3)]
            # a back (hardboard) or a drawer bottom sits in grooves of the panels round it: up to 10 mm deep is right
            if (a.get("kind") == "back" or b.get("kind") == "back") and min(ov) <= 10.0:
                continue
            if all(o > 0.6 for o in ov):
                warns.append(f"детали {pid(a)} и {pid(b)} пересекаются на {ov[0]:.1f} × {ov[1]:.1f} × {ov[2]:.1f} мм")
    return errors, warns


# ---------------------------------------------------------------------------------------------------------- drawing
def moulding_polys(p, cat):
    """Front-plane polygons of a moulding: bands between the profile's steps (u positions) — each a ring or strip."""
    prof = cat.get("profiles", {}).get(p.get("profile"), {}).get("pts", [[0, 0], [0, 16], [41, 16], [41, 0]])
    width = max(q[0] for q in prof)
    steps = sorted({round(q[0], 1) for q in prof if 0 < q[0] < width})
    path = [tuple(q) for q in p["path"]]
    closed = p.get("closed", False)
    if closed and area(path) < 0:
        path = path[::-1]
    rings = [offset(path, u, closed) for u in [0] + steps + [width]]
    return rings, closed


def area(pts):
    return 0.5 * sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))


def offset(path, d, closed):
    n = len(path)
    out = []
    for i in range(n):
        prev = path[(i - 1) % n] if closed else path[max(0, i - 1)]
        nxt = path[(i + 1) % n] if closed else path[min(n - 1, i + 1)]
        t0 = (path[i][0] - prev[0], path[i][1] - prev[1])
        t1 = (nxt[0] - path[i][0], nxt[1] - path[i][1])
        if t0 == (0, 0):
            t0 = t1
        if t1 == (0, 0):
            t1 = t0
        l0, l1 = math.hypot(*t0), math.hypot(*t1)
        n0 = (-t0[1] / l0, t0[0] / l0)
        n1 = (-t1[1] / l1, t1[0] / l1)
        m = (n0[0] + n1[0], n0[1] + n1[1])
        lm = math.hypot(*m)
        if lm < 1e-6:
            m = n1
        else:
            m = (m[0] / lm, m[1] / lm)
            c = max(m[0] * n1[0] + m[1] * n1[1], 0.25)
            m = (m[0] / c, m[1] / c)
        out.append((path[i][0] + m[0] * d, path[i][1] + m[1] * d))
    return out


def colours(cat, finish_id, model):
    fin = next((f for f in cat["finishes"] if f["id"] == finish_id), None)
    if fin is None and model:
        col = next((c for c in cat["collections"] if c["id"] == model.get("collection")), {})
        fins = model.get("finishes") or col.get("finishes") or []
        fin = next((f for f in cat["finishes"] if fins and f["id"] == fins[0]), None)
    body = hex_rgb((fin or {}).get("body"), (215, 210, 200))
    front = hex_rgb((fin or {}).get("front") or (fin or {}).get("body"), body)
    col = next((c for c in cat["collections"] if model and c["id"] == model.get("collection")), {})
    metal = hex_rgb(col.get("metal"), (200, 200, 205))
    return {"body": body, "front": front, "back": body, "metal": metal, "gold": metal, "chrome": (205, 208, 212),
            "glass": (190, 215, 220), "mirror": (215, 225, 230), "led": (255, 250, 220), "bedding": (240, 238, 232),
            "white": (241, 240, 236), "black": (30, 30, 30)}


def part_colour(p, cols):
    kind = p.get("kind", "panel")
    role = p.get("mat") or {"panel": "body", "front": "front", "back": "back", "moulding": "front", "glass": "glass",
                            "mirror": "mirror", "tube": "metal", "handle": "metal", "light": "led",
                            "mattress": "bedding"}.get(kind, "body")
    if role in cols:
        return cols[role]
    if "#" in role:
        return hex_rgb(role)
    return cols["body"]


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def view(d, cat, cols, axis, pxmm, pad=20):
    """Orthographic view. axis: front (x, y; near = large z), left (z, y; near = small x), top (x, z; near = large y)."""
    parts = d.get("parts", [])
    boxes = [box_of(p) for p in parts]
    allb = [b for b in boxes if b]
    X0, Y0, Z0 = min(b[0] for b in allb), min(b[1] for b in allb), min(b[2] for b in allb)
    X1, Y1, Z1 = max(b[3] for b in allb), max(b[4] for b in allb), max(b[5] for b in allb)
    if axis == "front":
        ext = (X0, Y0, X1, Y1)
        def proj(x, y, z): return x, y
        def depth(b): return b[5]
    elif axis == "left":
        ext = (Z0, Y0, Z1, Y1)
        def proj(x, y, z): return z, y
        def depth(b): return -b[0]
    else:
        ext = (X0, Z0, X1, Z1)
        def proj(x, y, z): return x, z
        def depth(b): return b[4]
    W = int((ext[2] - ext[0]) * pxmm) + 2 * pad
    H = int((ext[3] - ext[1]) * pxmm) + 2 * pad
    im = Image.new("RGB", (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(im, "RGBA")

    def P(a, b):
        return (pad + (a - ext[0]) * pxmm, H - pad - (b - ext[1]) * pxmm)

    order = sorted(range(len(parts)), key=lambda i: depth(boxes[i]) if boxes[i] else 0)
    edges = []
    for i in order:
        p, b = parts[i], boxes[i]
        kind = p.get("kind", "panel")
        c = part_colour(p, cols)
        if kind == "moulding":
            if axis != "front" or p.get("plane", "front") != "front":
                if b:
                    a0, b0 = proj(b[0], b[1], b[2]); a1, b1 = proj(b[3], b[4], b[5])
                    r = [P(a0, b0), P(a1, b1)]
                    dr.rectangle([min(r[0][0], r[1][0]), min(r[0][1], r[1][1]), max(r[0][0], r[1][0]), max(r[0][1], r[1][1])], fill=shade(c, 1.02), outline=(40, 40, 40))
                continue
            rings, closed = moulding_polys(p, cat)
            outer, inner = rings[0], rings[-1]
            if closed:
                mask = Image.new("L", im.size, 0)
                md = ImageDraw.Draw(mask)
                md.polygon([P(*q) for q in outer], fill=255)
                md.polygon([P(*q) for q in inner], fill=0)
                im.paste(shade(c, 1.04), (0, 0), mask)
            for k, ring in enumerate(rings):
                pts = [P(*q) for q in ring] + ([P(*ring[0])] if closed else [])
                edges.append((pts, (40, 40, 40) if k in (0, len(rings) - 1) else (90, 90, 90)))
            if closed:  # mitres
                for q in range(len(outer)):
                    edges.append(([P(*outer[q]), P(*inner[q])], (90, 90, 90)))
            continue
        if kind == "handle" and axis == "front":
            x, y = p["at"]
            r = p.get("d", 80) / 2
            band = p.get("band", 10)
            dx, dy = {"up": (0, 1), "down": (0, -1), "left": (-1, 0), "right": (1, 0)}.get(p.get("dir", "up"), (0, 1))
            a0 = math.atan2(dy, dx) - math.pi / 2
            if p.get("model", "ring-half") == "ring-half":
                outer = [(x + r * math.cos(a0 + math.pi * t / 24), y + r * math.sin(a0 + math.pi * t / 24)) for t in range(25)]
                inner = [(x + (r - band) * math.cos(a0 + math.pi * t / 24), y + (r - band) * math.sin(a0 + math.pi * t / 24)) for t in range(25)]
                poly = [P(*q) for q in outer + inner[::-1]]
                dr.polygon(poly, fill=c, outline=(40, 40, 40))
            else:
                dr.ellipse([P(x - r, y + r), P(x + r, y - r)], fill=c, outline=(40, 40, 40))
            continue
        if not b:
            continue
        a0, b0 = proj(b[0], b[1], b[2])
        a1, b1 = proj(b[3], b[4], b[5])
        q0, q1 = P(a0, b0), P(a1, b1)
        rect = [min(q0[0], q1[0]), min(q0[1], q1[1]), max(q0[0], q1[0]), max(q0[1], q1[1])]
        shape = p.get("shape", "rect")
        thin_front = (b[5] - b[2]) <= min(b[3] - b[0], b[4] - b[1])
        round_here = (shape in ("circle", "ring") and ((axis == "front" and thin_front) or (axis == "top" and not thin_front))) or \
                     (kind == "tube" and ((axis == "top" and (b[4] - b[1]) >= max(b[3] - b[0], b[5] - b[2])) or
                                          (axis == "front" and (b[5] - b[2]) >= max(b[3] - b[0], b[4] - b[1]))))
        fill = c + (110,) if kind == "glass" else c
        if round_here:
            dr.ellipse(rect, fill=fill, outline=(40, 40, 40))
            if shape == "ring" and p.get("inner"):
                cx, cy = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
                ri = p["inner"] / 2 * pxmm
                dr.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], outline=(40, 40, 40))
        else:
            dr.rectangle(rect, fill=fill, outline=(40, 40, 40))
        g = p.get("glass")
        if g and kind == "front" and axis == "front":
            o = (g.get("frame", 50) + g.get("rebate", 10)) * pxmm
            dr.rectangle([rect[0] + o, rect[1] + o, rect[2] - o, rect[3] - o], fill=(200, 222, 228), outline=(40, 40, 40))
    for pts, col in edges:
        dr.line(pts, fill=col, width=1)
    return im, ext


def ref_overlay(ref_path, ours, ext, pxmm, box=None, pad=20):
    ref = Image.open(ref_path).convert("L")
    if box:
        crop = ref.crop(tuple(box))
    else:
        a = np.asarray(ref) < 140
        ys, xs = np.where(a)
        if len(xs) == 0:
            return None
        crop = ref.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    w = int((ext[2] - ext[0]) * pxmm)
    h = int((ext[3] - ext[1]) * pxmm)
    crop = crop.resize((max(1, w), max(1, h)), Image.LANCZOS)
    base = Image.new("RGB", ours.size, (255, 255, 255))
    base.paste(crop.convert("RGB"), (pad, ours.size[1] - pad - h))
    # our edges in red
    o = np.asarray(ours.convert("L")) < 80
    arr = np.asarray(base).copy()
    arr[o] = (0.35 * arr[o] + 0.65 * np.array([230, 30, 30])).astype(np.uint8)
    return Image.fromarray(arr), base


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("design")
    ap.add_argument("--ref", help="reference front view (a crop of the instruction's front view or a photo)")
    ap.add_argument("--ref-box", help="x0,y0,x1,y1: the piece's outline in the reference (px, incl. legs); default: all dark pixels")
    ap.add_argument("--out")
    ap.add_argument("--finish")
    ap.add_argument("--is", dest="is_pdf", help="assembly instruction PDF (default: the model's)")
    ap.add_argument("--pxmm", type=float, default=0.35)
    a = ap.parse_args()
    d, cat, model = load(a.design)
    is_pdf = a.is_pdf
    if not is_pdf and model and model.get("is"):
        is_pdf = os.path.join(ROOT, "tools/casegoods/reference", model.get("collection", ""), "is", model["is"])
    errors, warns = check(d, cat, model, is_pdf)
    for e in errors:
        print("ОШИБКА  " + e)
    for w in warns:
        print("внимание " + w)
    if not errors and not warns:
        print("ok: спецификация, габарит и пересечения сходятся")
    if a.out:
        cols = colours(cat, a.finish, model)
        front, ext = view(d, cat, cols, "front", a.pxmm)
        left, _ = view(d, cat, cols, "left", a.pxmm)
        top, _ = view(d, cat, cols, "top", a.pxmm)
        panels = []
        if a.ref:
            box = [float(v) for v in a.ref_box.split(",")] if a.ref_box else None
            r = ref_overlay(a.ref, front, ext, a.pxmm, box)
            if r:
                panels += [r[1], r[0]]
        panels += [front, left, top]
        W = sum(p.size[0] for p in panels) + 10 * (len(panels) - 1)
        H = max(p.size[1] for p in panels)
        sheet = Image.new("RGB", (W, H), (255, 255, 255))
        x = 0
        for p in panels:
            sheet.paste(p, (x, H - p.size[1]))
            x += p.size[0] + 10
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        sheet.save(a.out)
        print("→ " + a.out)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
