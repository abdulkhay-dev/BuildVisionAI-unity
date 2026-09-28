#!/usr/bin/env python3
"""2D elevation of a window design (Docs/window-designs.md), seen from outside — a check without Unity.

    python3 tools/windows/preview2d.py Assets/House4696/Resources/Windows/Designs/w01.json [--size 1.4x1.4]
        [--finish "#f1f0eb"] [--photo tools/windows/reference/w01.jpg] [--out out.png] [--pxmm 0.4]

Draws the frame outline, mullions, sashes, glazing bars, frosted bands, the surround and the sills at the requested size
(the design's fixX / fixY zones keep their size, the rest stretches — the same rule as the engine), and optionally puts
the catalogue picture beside it. Needs only numpy and Pillow. It mirrors WindowBuilder.cs closely enough for layout
work; the 3D look (depth, shading, reflections) is checked in Unity.
"""
import argparse
import json
import math
import sys

from PIL import Image, ImageDraw, ImageFilter


# ---------------------------------------------------------------- resizing (ResizeMap.cs)
class ResizeMap:
    def __init__(self, ref, length, fixed):
        self.ref, self.len = float(ref), float(length)
        iv = sorted([(max(0.0, a), min(self.ref, b)) for a, b in (fixed or []) if b > a])
        merged = []
        for a, b in iv:
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b))
            else:
                merged.append((a, b))
        self.fixed = merged
        fixed_len = sum(b - a for a, b in merged)
        free = self.ref - fixed_len
        self.k = (self.len - fixed_len) / free if free > 1e-6 and self.len > fixed_len else None

    def map(self, v):
        if self.k is None:
            return v * self.len / self.ref
        out, pos = 0.0, 0.0
        for a, b in self.fixed:
            if v <= a:
                return out + (v - pos) * self.k
            out += (a - pos) * self.k
            if v <= b:
                return out + (v - a)
            out += b - a
            pos = b
        return out + (v - pos) * self.k


# ---------------------------------------------------------------- shapes (Shape2D.cs subset, y up, mm)
def arc_points(x1, y1, rx, ry, phi, large, sweep, x2, y2, n=48):
    """SVG elliptical arc → points (endpoint parametrisation, y up: sweep 1 = counter-clockwise)."""
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    cp, sp = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    rx, ry = abs(rx), abs(ry)
    lam = (x1p ** 2) / rx ** 2 + (y1p ** 2) / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den > 0 else 0.0
    if large == sweep:
        co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx, cy = cp * cxp - sp * cyp + (x1 + x2) / 2, sp * cxp + cp * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    pts = []
    for i in range(1, n + 1):
        t = t1 + dt * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cp * x - sp * y + cx, sp * x + cp * y + cy))
    return pts


def parse_path(d):
    import re
    toks = re.findall(r"[MmLlHhVvCcQqAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d)
    polys, cur, i, cmd = [], [], 0, None
    x = y = 0.0
    sx = sy = 0.0

    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v
    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]):
            cmd = toks[i]; i += 1
            if cmd in "Zz":
                if cur:
                    polys.append(cur); cur = []
                x, y = sx, sy
                continue
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            nx, ny = num(), num()
            if rel: nx += x; ny += y
            if cur: polys.append(cur)
            cur = [(nx, ny)]; x, y = nx, ny; sx, sy = x, y
            cmd = "l" if rel else "L"
        elif c == "L":
            nx, ny = num(), num()
            if rel: nx += x; ny += y
            cur.append((nx, ny)); x, y = nx, ny
        elif c == "H":
            nx = num()
            if rel: nx += x
            cur.append((nx, y)); x = nx
        elif c == "V":
            ny = num()
            if rel: ny += y
            cur.append((x, ny)); y = ny
        elif c == "C":
            p = [num() for _ in range(6)]
            if rel: p = [p[k] + (x if k % 2 == 0 else y) for k in range(6)]
            for k in range(1, 17):
                t = k / 16
                a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; cc = 3 * (1 - t) * t * t; dd = t ** 3
                cur.append((a * x + b * p[0] + cc * p[2] + dd * p[4], a * y + b * p[1] + cc * p[3] + dd * p[5]))
            x, y = p[4], p[5]
        elif c == "Q":
            p = [num() for _ in range(4)]
            if rel: p = [p[k] + (x if k % 2 == 0 else y) for k in range(4)]
            for k in range(1, 13):
                t = k / 12
                cur.append(((1 - t) ** 2 * x + 2 * (1 - t) * t * p[0] + t * t * p[2], (1 - t) ** 2 * y + 2 * (1 - t) * t * p[1] + t * t * p[3]))
            x, y = p[2], p[3]
        elif c == "A":
            rx, ry, phi, la, sw, nx, ny = [num() for _ in range(7)]
            if rel: nx += x; ny += y
            cur.extend(arc_points(x, y, rx, ry, phi, int(la), int(sw), nx, ny))
            x, y = nx, ny
        else:
            raise ValueError("unsupported path command " + cmd)
    if cur:
        polys.append(cur)
    return polys


def shape_polys(shape, refw, refh):
    if shape is None:
        return [[(0, 0), (refw, 0), (refw, refh), (0, refh)]]
    if "rect" in shape:
        x0, y0, x1, y1 = shape["rect"]
        return [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    if "ellipse" in shape:
        cx, cy, rx, ry = shape["ellipse"]
        return [[(cx + rx * math.cos(2 * math.pi * k / 96), cy + ry * math.sin(2 * math.pi * k / 96)) for k in range(96)]]
    if "arch" in shape:
        x0, y0, x1, y1 = shape["arch"]
        rise = shape.get("rise", (x1 - x0) / 2)
        w = x1 - x0
        r = (w * w / 4 + rise * rise) / (2 * rise)
        cx, cy = (x0 + x1) / 2, y1 - r
        a0 = math.atan2(y1 - rise - cy, x1 - cx)
        a1 = math.pi - a0
        pts = [(x0, y0), (x1, y0), (x1, y1 - rise)]
        for k in range(1, 48):
            t = a0 + (a1 - a0) * k / 48
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        pts.append((x0, y1 - rise))
        return [pts]
    if "path" in shape:
        return parse_path(shape["path"])
    raise ValueError("unknown shape " + json.dumps(shape))


def offset_poly(pts, d):
    """Polygon moved inwards by d mm (d < 0: outwards), mitred corners with a limit — like Relief.Offset."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    if area < 0:
        pts = pts[::-1]
    out = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        def nrm(a, b):
            dx, dy = b[0] - a[0], b[1] - a[1]
            l = math.hypot(dx, dy) or 1.0
            return (-dy / l, dx / l)                     # left normal = inwards on a counter-clockwise ring
        n0, n1 = nrm(p0, p1), nrm(p1, p2)
        mx_, my_ = n0[0] + n1[0], n0[1] + n1[1]
        ml = math.hypot(mx_, my_)
        if ml < 1e-6:
            mx_, my_, k = n1[0], n1[1], 1.0
        else:
            mx_, my_ = mx_ / ml, my_ / ml
            k = min(4.0, 1.0 / max(1e-3, mx_ * n1[0] + my_ * n1[1]))
        out.append((p1[0] + mx_ * d * k, p1[1] + my_ * d * k))
    return out


# ---------------------------------------------------------------- raster helpers
class Canvas:
    def __init__(self, w_mm, h_mm, pxmm, margin_mm):
        self.pxmm, self.m = pxmm, margin_mm
        self.W = int(round((w_mm + 2 * margin_mm) * pxmm))
        self.H = int(round((h_mm + 2 * margin_mm) * pxmm))
        self.h_mm = h_mm

    def px(self, x, y):
        return ((x + self.m) * self.pxmm, (self.h_mm + self.m - y) * self.pxmm)

    def mask(self):
        return Image.new("L", (self.W, self.H), 0)

    def poly(self, mask, pts, fill=255):
        ImageDraw.Draw(mask).polygon([self.px(x, y) for x, y in pts], fill=fill)
        return mask

    def rect(self, mask, x0, y0, x1, y1, fill=255):
        a, b = self.px(x0, y1), self.px(x1, y0)
        ImageDraw.Draw(mask).rectangle([a[0], a[1], b[0], b[1]], fill=fill)
        return mask

    def erode(self, mask, mm):
        k = max(1, int(round(mm * self.pxmm)))
        return mask.filter(ImageFilter.MinFilter(2 * k + 1)) if k > 0 else mask

    def dilate(self, mask, mm):
        k = max(1, int(round(mm * self.pxmm)))
        return mask.filter(ImageFilter.MaxFilter(2 * k + 1))


def land(a, b):
    from PIL import ImageChops
    return ImageChops.multiply(a, b)


def lsub(a, b):
    from PIL import ImageChops
    return ImageChops.subtract(a, b)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(rgb, k):
    return tuple(max(0, min(255, int(c * k))) for c in rgb)


# ---------------------------------------------------------------- render
def render(design, W, H, finish="#f1f0eb", pxmm=0.4):
    refw, refh = design.get("ref", [1200, 1400])
    mx = ResizeMap(refw, W, design.get("fixX"))
    my = ResizeMap(refh, H, design.get("fixY"))
    frame = {"width": 70, "depth": 70, **design.get("frame", {})}
    sash = {"width": 60, "overlap": 30, **design.get("sash", {})}
    sur = design.get("surround")
    margin = 80 + (sur.get("width", 150) + sur.get("head", 0) if sur else 0)
    cv = Canvas(W, H, pxmm, margin)
    img = Image.new("RGB", (cv.W, cv.H), (236, 233, 226))           # the facade
    col = hexrgb(finish)
    glass_c, frost_c, stone_c, metal_c = (150, 160, 168), (228, 229, 226), (208, 196, 170), (120, 124, 128)

    outline, inner = cv.mask(), cv.mask()
    polys = [[(mx.map(x), my.map(y)) for x, y in poly] for poly in shape_polys(design.get("shape"), refw, refh)]
    for poly in polys:
        cv.poly(outline, poly)
        cv.poly(inner, offset_poly(poly, frame["width"]))

    if sur:
        grown = cv.mask()
        for poly in polys:
            cv.poly(grown, offset_poly(poly, -sur.get("width", 150)))
        ring = lsub(grown, outline)
        if sur.get("bottom", True) is False:
            ring = lsub(ring, cv.rect(cv.mask(), -9999, -9999, 9999, 0))
        if sur.get("head", 0) > 0:
            head = cv.rect(cv.mask(), -sur.get("width", 150) - 15, H, W + sur.get("width", 150) + 15, H + sur.get("width", 150) + sur["head"])
            from PIL import ImageChops
            ring = ImageChops.lighter(ring, lsub(head, outline))
        scol = col if sur.get("material") == "frame" else stone_c
        img.paste(scol, mask=ring)

    img.paste((70, 72, 76), mask=outline)                            # the dark reveal behind
    img.paste(col, mask=lsub(outline, inner))                        # frame ring

    cells = []

    def walk(n, r):
        if n and n.get("split") in ("x", "y") and n.get("at") and len(n.get("cells", [])) == len(n["at"]) + 1:
            ax = n["split"] == "x"
            mp = mx if ax else my
            lo = r[0] if ax else r[1]
            mul = n.get("mullion", 80)
            for i in range(len(n["at"]) + 1):
                hi = mp.map(n["at"][i]) if i < len(n["at"]) else (r[2] if ax else r[3])
                w = (mul[i] if isinstance(mul, list) else mul) if i < len(n["at"]) else 0
                ch = hi - w / 2 if i < len(n["at"]) else hi
                cr = (lo, r[1], ch, r[3]) if ax else (r[0], lo, r[2], ch)
                walk(n["cells"][i], cr)
                if i < len(n["at"]) and w > 0.5:
                    band = cv.rect(cv.mask(), hi - w / 2, r[1] - 1, hi + w / 2, r[3] + 1) if ax else cv.rect(cv.mask(), r[0] - 1, hi - w / 2, r[2] + 1, hi + w / 2)
                    img.paste(col, mask=land(band, inner))
                lo = hi + w / 2
        else:
            cells.append((n or {}, r))
    bb = inner.getbbox()
    if not bb:
        raise SystemExit("the frame leaves no glass")
    x0 = bb[0] / pxmm - margin; x1 = bb[2] / pxmm - margin
    y1 = H + margin - bb[1] / pxmm; y0 = H + margin - bb[3] / pxmm
    walk(design.get("layout"), (x0, y0, x1, y1))

    for node, r in cells:
        kind = (node.get("sash") or ("panel" if node.get("panel") else "fixed")).lower()
        c = land(cv.rect(cv.mask(), *r), inner)
        glass = c
        if kind not in ("fixed", "panel"):
            so = c
            ov = sash["overlap"] / 2
            if kind == "slide":
                so = land(cv.rect(cv.mask(), r[0] - ov, r[1], r[2] + ov, r[3]), inner)
            elif kind == "hung":
                so = land(cv.rect(cv.mask(), r[0], r[1] - ov, r[2], r[3] + ov), inner)
            rails = node.get("rails") or {}
            si = cv.erode(so, rails.get("side", sash["width"]))
            if rails.get("top") or rails.get("bottom"):
                bb3 = so.getbbox()
                if bb3:
                    sx0 = bb3[0] / pxmm - margin; sx1 = bb3[2] / pxmm - margin
                    sy1 = H + margin - bb3[1] / pxmm; sy0 = H + margin - bb3[3] / pxmm
                    si = land(si, cv.rect(cv.mask(), sx0 - 1, sy0 + rails.get("bottom", sash["width"]), sx1 + 1, sy1 - rails.get("top", sash["width"])))
            img.paste(shade(col, 0.93), mask=lsub(so, si))
            glass = si
        if kind == "panel" and node.get("panel", "frame") != "frosted":
            img.paste(shade(col, 0.97), mask=glass)
            continue
        img.paste(glass_c if node.get("panel") != "frosted" else frost_c, mask=glass)
        if node.get("blinds"):
            bb4 = glass.getbbox()
            if bb4:
                for yy in range(bb4[1], bb4[3], max(2, int(25 * pxmm))):
                    ImageDraw.Draw(img).line([(bb4[0], yy), (bb4[2], yy)], fill=(215, 215, 212), width=1)
        fr = node.get("frosted")
        if fr:
            img.paste(frost_c, mask=land(glass, cv.rect(cv.mask(), r[0] - 20, r[1] - 20, r[2] + 20, r[1] + fr)))
        bars = node.get("bars")
        if bars:
            bb2 = glass.getbbox()
            if bb2:
                gx0 = bb2[0] / pxmm - margin; gx1 = bb2[2] / pxmm - margin
                gy1 = H + margin - bb2[1] / pxmm; gy0 = H + margin - bb2[3] / pxmm
                w = bars.get("width", 25)
                xs = [mx.map(v) for v in bars.get("x", [])] + [gx0 + (gx1 - gx0) * k / bars["cols"] for k in range(1, bars.get("cols", 0))]
                ys = [my.map(v) for v in bars.get("y", [])] + [gy0 + (gy1 - gy0) * k / bars["rows"] for k in range(1, bars.get("rows", 0))]
                for x in xs:
                    img.paste(col, mask=land(cv.rect(cv.mask(), x - w / 2, gy0 - 1, x + w / 2, gy1 + 1), glass))
                for y in ys:
                    img.paste(col, mask=land(cv.rect(cv.mask(), gx0 - 1, y - w / 2, gx1 + 1, y + w / 2), glass))

    d = ImageDraw.Draw(img)
    # members (bars, diagrid, fins, louvres) — drawn as thick polylines
    for m in design.get("members", []) or []:
        mcol = col if m.get("material", "frame") == "frame" else (184, 187, 190)
        for k in range(max(1, m.get("count", 1))):
            for poly in parse_path(m["path"]):
                pts = [cv.px(mx.map(x) + m.get("stepX", 0) * k, my.map(y) + m.get("stepY", 0) * k) for x, y in poly]
                if len(pts) > 1:
                    d.line(pts + ([pts[0]] if m["path"].strip().upper().endswith("Z") else []), fill=mcol, width=max(1, int(m.get("width", 40) * pxmm)))
    aw = design.get("awning")
    if aw:
        cols = aw.get("colors", ["#efe9dc", "#4f6b56"])
        ytop, drop, ears, stripe = H + aw.get("height", 250), aw.get("drop", 300), aw.get("ears", 150), aw.get("stripe", 150)
        x, k = -ears, 0
        while x < W + ears:
            a_, b_ = cv.px(x, ytop), cv.px(min(W + ears, x + stripe), ytop - drop - aw.get("valance", 180))
            d.rectangle([a_[0], a_[1], b_[0], b_[1]], fill=hexrgb(cols[k % len(cols)]))
            x += stripe; k += 1
    sh = design.get("shelf")
    if sh:
        a_, b_ = cv.px(-sh.get("ears", 150), sh.get("y", 0)), cv.px(W + sh.get("ears", 150), sh.get("y", 0) - sh.get("thickness", 40))
        d.rectangle([a_[0], a_[1], b_[0], b_[1]], fill=(160, 118, 70))
    if sur and sur.get("keystone"):
        k_ = sur["keystone"]; top = max(y for poly in polys for x, y in poly)
        pts = [cv.px(W / 2 - k_.get("width", 160) * 0.4, top - k_.get("height", 220) * 0.25), cv.px(W / 2 + k_.get("width", 160) * 0.4, top - k_.get("height", 220) * 0.25),
               cv.px(W / 2 + k_.get("width", 160) * 0.5, top + k_.get("height", 220) * 0.75), cv.px(W / 2 - k_.get("width", 160) * 0.5, top + k_.get("height", 220) * 0.75)]
        d.polygon(pts, fill=shade(stone_c, 0.95))
    sill = {"outside": "metal", "overhang": 40, "thickness": 50, "ears": 40, **design.get("sill", {})}
    if sill["outside"] == "stone":
        a, b = cv.px(-sill["ears"], 5), cv.px(W + sill["ears"], 5 - sill["thickness"])
        d.rectangle([a[0], a[1], b[0], b[1]], fill=stone_c)
    elif sill["outside"] == "metal":
        a, b = cv.px(0, 5), cv.px(W, -28)
        d.rectangle([a[0], a[1], b[0], b[1]], fill=metal_c)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("design")
    ap.add_argument("--size", help="WxH in metres (default: the design's ref)")
    ap.add_argument("--finish", default="#f1f0eb", help="frame colour #rrggbb")
    ap.add_argument("--photo", help="catalogue picture to put beside the elevation")
    ap.add_argument("--pxmm", type=float, default=0.4)
    ap.add_argument("--out", default="window_preview.png")
    a = ap.parse_args()
    design = json.load(open(a.design))
    refw, refh = design.get("ref", [1200, 1400])
    W, H = (float(v) * 1000 for v in a.size.lower().split("x")) if a.size else (refw, refh)
    img = render(design, W, H, a.finish, a.pxmm)
    if a.photo:
        ph = Image.open(a.photo).convert("RGB")
        h = max(img.height, 480)
        ph = ph.resize((int(ph.width * h / ph.height), h))
        img = img.resize((int(img.width * h / img.height), h))
        out = Image.new("RGB", (ph.width + img.width + 12, h), "white")
        out.paste(ph, (0, 0)); out.paste(img, (ph.width + 12, 0))
        img = out
    img.save(a.out)
    print(a.out, img.size)


if __name__ == "__main__":
    sys.exit(main())
