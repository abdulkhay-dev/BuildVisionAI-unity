"""Shared helpers of the classic collections Сати, Шанталь, Мартина, Сорбонна, Элиза (wave 3, part A).

Millimetres; x left → right, y up from the floor, z from the back (the wall) to the front, as in Docs/casegoods-designs.md.
Everything here returns plain part dicts; `common.dump` writes the design one part per line.

    frame_front(...)   a classic frame-and-panel front: the milled frame (one board with holes = the cut-list part),
                       the sunk panels in its holes (grooves / plain / carved), a bead round each panel and a patina line
    cornice(...)       an overhanging crown moulding round the front and both sides (plane "top", path at its outer edge)
    rect_ring(...)     a front-plane moulding frame (closed) — applied frames, patina lines
    bow(...)           a classic bow (arched) handle of rods; bar(...), knob(...)
    drawer_box(...)    the drawer box behind a front: sides, back, a ХДФ bottom in grooves
    leg_round(...)     a turned / tapered round leg (rod with its bounding box, so the checker counts it)
    metal_base(...)    a bed's metal frame with slats and the mattress
"""
import math

from common import dump  # noqa: F401  (re-exported for the generators)


def r5(v):
    return round(v * 2) / 2


def fmt(v):
    v = r5(v)
    return int(v) if v == int(v) else v


def box(*b):
    return [fmt(v) for v in b]


def part(pid, b, n=None, **kw):
    p = {}
    if n is not None:
        p["n"] = str(n)
    if pid is not None and pid != (str(n) if n is not None else None):
        p["id"] = pid
    if "kind" in kw:
        p["kind"] = kw.pop("kind")
    p["box"] = box(*b)
    p.update(kw)
    return p


def back(pid, b, n=None, **kw):
    return part(pid, b, n, kind="back", **kw)


def rect_path(x0, y0, x1, y1):
    return f"M {fmt(x0)} {fmt(y0)} L {fmt(x1)} {fmt(y0)} L {fmt(x1)} {fmt(y1)} L {fmt(x0)} {fmt(y1)} Z"


def outline_with_holes(x0, y0, x1, y1, holes, bottom=None):
    """One polygon: the board's outline with its openings joined to the edge by zero-width slits (a keyhole path), so
    the engine (even-odd) and check.py (which reads one polygon) both see the holes. Each hole is joined to the top
    edge when nothing lies above it, else to the bottom edge. `bottom` replaces the straight bottom edge (commands from
    (x0, y0) to (x1, y0), e.g. an arch) — then every hole must reach the top."""
    top, bot = [], []
    for h in holes:
        sx = (h[0] + h[2]) / 2
        above = any(g is not h and g[0] < sx < g[2] and g[1] >= h[3] for g in holes)
        (bot if above and bottom is None else top).append((sx, h))
    f = fmt
    s = f"M {f(x0)} {f(y0)}"
    if bottom:
        s += " " + bottom
    else:
        for sx, (a0, b0, a1, b1) in sorted(bot):
            s += (f" L {f(sx)} {f(y0)} L {f(sx)} {f(b0)} L {f(a0)} {f(b0)} L {f(a0)} {f(b1)} L {f(a1)} {f(b1)}"
                  f" L {f(a1)} {f(b0)} L {f(sx)} {f(b0)} L {f(sx)} {f(y0)}")
        s += f" L {f(x1)} {f(y0)}"
    s += f" L {f(x1)} {f(y1)}"
    for sx, (a0, b0, a1, b1) in sorted(top, reverse=True):
        s += (f" L {f(sx)} {f(y1)} L {f(sx)} {f(b1)} L {f(a1)} {f(b1)} L {f(a1)} {f(b0)} L {f(a0)} {f(b0)}"
              f" L {f(a0)} {f(b1)} L {f(sx)} {f(b1)} L {f(sx)} {f(y1)}")
    s += f" L {f(x0)} {f(y1)} Z"
    return s


# ------------------------------------------------------------------------------------------------------------ fronts
def frame_front(pid, n, x0, y0, x1, y1, z0, t, holes, *, sink=4.0, pt=8.0, face=None, panel_mat=None, bead=None,
                patina=None, patina_prof=None, mat=None, extra=None, outline=None, bottom=None, kind="front"):
    """A frame-and-panel front: `holes` [(hx0, hy0, hx1, hy1), …] are the panel openings of the milled frame.

    The frame is the cut-list part (n, full box, `shape: path` = the board with its openings); each opening holds a panel
    `pt` thick whose face lies `sink` mm below the frame's face (face = grooves / flat), with the bead profile `bead`
    round it (a front-plane moulding lying on the panel against the frame's edge) and a patina line `patina` (a thin
    moulding of the role "patina") where the bead meets the frame. Returns the list of parts; ids start with pid."""
    zf = z0 + t
    fr = {"id": pid} if n is None else {"n": str(n), "id": pid}
    fr.update({"kind": kind, "box": box(x0, y0, z0, x1, y1, zf), "shape": "path",
               "outline": outline or outline_with_holes(x0, y0, x1, y1, holes, bottom)})
    if mat:
        fr["mat"] = mat
    if extra:
        fr.update(extra)
    out = [fr]
    for k, (a0, b0, a1, b1) in enumerate(holes):
        pz1 = zf - sink
        pz0 = max(z0, pz1 - pt)
        pn = {"id": f"{pid}-p{k + 1}", "kind": kind, "box": box(a0, b0, pz0, a1, b1, pz1)}
        if face:
            f = dict(face)
            if f.get("type") == "grooves" and callable(f.get("lines")):
                f["lines"] = f["lines"](a0, b0, a1, b1)
            pn["face"] = f
        if panel_mat or mat:
            pn["mat"] = panel_mat or mat
        out.append(pn)
        if bead:
            out.append({"id": f"{pid}-b{k + 1}", "kind": "moulding", "profile": bead, "closed": True, "z": fmt(pz1),
                        "path": [[fmt(a0), fmt(b0)], [fmt(a1), fmt(b0)], [fmt(a1), fmt(b1)], [fmt(a0), fmt(b1)]],
                        **({"mat": mat} if mat else {})})
        if patina:
            out.append({"id": f"{pid}-pt{k + 1}", "kind": "moulding", "profile": patina_prof or patina, "closed": True,
                        "z": fmt(pz1), "mat": "patina",
                        "path": [[fmt(a0), fmt(b0)], [fmt(a1), fmt(b0)], [fmt(a1), fmt(b1)], [fmt(a0), fmt(b1)]]})
    return out


def vlines(pitch, margin=0):
    """Grooves face lines: vertical lines every `pitch` across a panel (boards of a wainscot panel)."""
    def f(a0, b0, a1, b1):
        w = a1 - a0
        k = max(1, round(w / pitch))
        return [[fmt(a0 + w * i / k), fmt(b0 + margin), fmt(a0 + w * i / k), fmt(b1 - margin)] for i in range(1, k)]
    return f


def hlines(pitch, margin=0):
    def f(a0, b0, a1, b1):
        h = b1 - b0
        k = max(1, round(h / pitch))
        return [[fmt(a0 + margin), fmt(b0 + h * i / k), fmt(a1 - margin), fmt(b0 + h * i / k)] for i in range(1, k)]
    return f


def ring(pid, x0, y0, x1, y1, z, profile, mat=None, covers=None):
    p = {"id": pid, "kind": "moulding", "profile": profile, "closed": True, "z": fmt(z),
         "path": [[fmt(x0), fmt(y0)], [fmt(x1), fmt(y0)], [fmt(x1), fmt(y1)], [fmt(x0), fmt(y1)]]}
    if mat:
        p["mat"] = mat
    if covers:
        p["covers"] = covers
    return p


def cornice(pid, x0, x1, z0, z1, y, profile, mat=None, covers=None, back_ends=True):
    """A crown moulding round the front and both sides: plane "top", the path at its OUTER edge (so the checker's
    extent sees it), the profile lying inwards (side 1 on this path: back-right → front-right → front-left → back-left);
    y = the level its section stands on (v up from there)."""
    p = {"id": pid, "kind": "moulding", "profile": profile, "plane": "top", "z": fmt(y), "side": 1,
         "path": [[fmt(x1), fmt(z0)], [fmt(x1), fmt(z1)], [fmt(x0), fmt(z1)], [fmt(x0), fmt(z0)]]}
    if mat:
        p["mat"] = mat
    if covers:
        p["covers"] = covers
    return p


def front_band(pid, x0, x1, y, z, profile, side=1, mat=None, covers=None):
    """An open front-plane moulding along x at height y (a belt, a frieze bead); side 1 = the profile lies above."""
    p = {"id": pid, "kind": "moulding", "profile": profile, "z": fmt(z), "side": side,
         "path": [[fmt(x0), fmt(y)], [fmt(x1), fmt(y)]]}
    if mat:
        p["mat"] = mat
    if covers:
        p["covers"] = covers
    return p


# ----------------------------------------------------------------------------------------------------------- handles
def knob(pid, x, y, z, d=30, t=14, standoff=16, mat=None):
    p = {"id": pid, "kind": "handle", "model": "knob", "at": [fmt(x), fmt(y)], "d": d, "t": t, "standoff": standoff,
         "z": fmt(z)}
    if mat:
        p["mat"] = mat
    return p


def bar(pid, x, y, z, d=160, vertical=False, band=10, t=8, standoff=22, post=12, section=None, mat=None):
    p = {"id": pid, "kind": "handle", "model": "bar", "at": [fmt(x), fmt(y)], "dir": "up" if vertical else "right",
         "d": d, "band": band, "t": t, "standoff": standoff, "post": post, "z": fmt(z)}
    if section:
        p["section"] = section
    if mat:
        p["mat"] = mat
    return p


def bow(pid, x, y, z, cc=128, rise=10, off=24, d=9, vertical=False, segs=6, mat="metal", foot=12):
    """A classic bow handle: two posts (rods from the face) and an arc of rod segments between them, bulging `rise`
    away from the post line in the front plane (up, or to the right when vertical) — the Sati / Шанталь cast pulls.
    Returns rod parts (no box: they stay out of the extent like handles)."""
    parts = []
    ax, ay = (0, 1) if vertical else (1, 0)          # along the handle
    bx, by = (1, 0) if vertical else (0, 1)          # the bulge
    hl = cc / 2
    ends = [(-hl, 0), (hl, 0)]
    for k, (s, _) in enumerate(ends):
        px, py = x + ax * s, y + ay * s
        parts.append({"id": f"{pid}-post{k + 1}", "kind": "rod", "mat": mat, "from": [fmt(px), fmt(py), fmt(z)],
                      "to": [fmt(px), fmt(py), fmt(z + off)], "d": foot, "d2": d})
    pts = []
    for i in range(segs + 1):
        s = -hl + cc * i / segs
        b = rise * (1 - (s / hl) ** 2)
        pts.append((x + ax * s + bx * b, y + ay * s + by * b, z + off))
    for i in range(segs):
        a, c = pts[i], pts[i + 1]
        parts.append({"id": f"{pid}-arc{i + 1}", "kind": "rod", "mat": mat, "from": [fmt(v) for v in a],
                      "to": [fmt(v) for v in c], "d": d})
    return parts


def ids(parts):
    return [p.get("id") or p.get("n") for p in parts]


# ---------------------------------------------------------------------------------------------------------- drawers
def drawer_box(tag, x0, x1, y0, h, z0, z1, t=16, bottom=3.5, ns=(None, None, None, None), bottom_size=None):
    """Box outer x0..x1, y0..y0+h, from z0 (its back) to z1 (the back of the front): sides, back between them, ХДФ
    bottom in 10-mm-high grooves (8 mm into the sides and the back). ns = cut-list numbers (side l, side r, back,
    bottom); bottom_size = (width, depth) of the listed bottom."""
    n1, n2, n3, n4 = ns
    out = [part(f"{tag}-sl", [x0, y0, z0, x0 + t, y0 + h, z1], n1),
           part(f"{tag}-sr", [x1 - t, y0, z0, x1, y0 + h, z1], n2),
           part(f"{tag}-bk", [x0 + t, y0, z0, x1 - t, y0 + h, z0 + t], n3)]
    if bottom_size:
        bw, bd = bottom_size
        cx = (x0 + x1) / 2
        bz1 = z1 - 2
        out.append(back(f"{tag}-bt", [cx - bw / 2, y0 + 10, bz1 - bd, cx + bw / 2, y0 + 10 + bottom, bz1], n4))
    else:
        out.append(back(f"{tag}-bt", [x0 + t - 8, y0 + 10, z0 + 8, x1 - t + 8, y0 + 10 + bottom, z1 - 2], n4))
    return out


# -------------------------------------------------------------------------------------------------------------- legs
def leg_round(pid, x, z, top, d=48, d2=30, foot=0, mat="body", splay=(0, 0)):
    """A turned tapered round leg from the underside `top` to the floor (or to a glide `foot` high), the foot moved
    by `splay` (dx, dz). Its box is the bounds, so check.py counts it in the extent (the engine ignores a rod's box)."""
    fx, fz = x + splay[0], z + splay[1]
    r = max(d, d2) / 2
    return {"id": pid, "kind": "rod", "mat": mat, "from": [fmt(x), fmt(top), fmt(z)], "to": [fmt(fx), fmt(foot), fmt(fz)],
            "d": d, "d2": d2, "box": box(min(x, fx) - r, foot, min(z, fz) - r, max(x, fx) + r, top, max(z, fz) + r)}


def glides(xs, zs, h=4, d=24, cover="g"):
    out, k = [], 0
    for x in xs:
        for z in zs:
            k += 1
            out.append({"id": f"g-{k}", "kind": "panel", "mat": "black", "shape": "circle",
                        "box": box(x - d / 2, 0, z - d / 2, x + d / 2, h, z + d / 2), "covers": [cover]})
    return out


# ---------------------------------------------------------------------------------------------------------- beds
def metal_base(x0, x1, z0, z1, y_top, leg_xs=(), leg_zs=(), slats=24, mattress=200, cover="m", slat_col="#c9a877"):
    """The bed's metal frame (металлокаркас) x0..x1 × z0..z1: two long rails 40×30, cross rails, a middle beam, slats
    (bent birch) and the mattress; legs at (leg_xs × leg_zs) down to the floor."""
    out = []
    rh = 30
    yb = y_top - rh
    out.append(part("m-rail-l", [x0, yb, z0, x0 + 40, y_top, z1], mat="black", covers=[cover]))
    out.append(part("m-rail-r", [x1 - 40, yb, z0, x1, y_top, z1], mat="black"))
    out.append(part("m-cross-h", [x0 + 40, yb, z0, x1 - 40, y_top, z0 + 30], mat="black"))
    out.append(part("m-cross-f", [x0 + 40, yb, z1 - 30, x1 - 40, y_top, z1], mat="black"))
    xm = (x0 + x1) / 2
    out.append(part("m-beam", [xm - 20, yb, z0 + 30, xm + 20, y_top, z1 - 30], mat="black"))
    k = 0
    for x in leg_xs:
        for z in leg_zs:
            k += 1
            out.append({"id": f"m-leg-{k}", "kind": "tube", "mat": "black", "box": box(x - 15, 0, z - 15, x + 15, yb, z + 15)})
    L = z1 - z0 - 60
    pitch = L / slats
    for i in range(slats):
        a = z0 + 30 + pitch * i + (pitch - 53) / 2
        out.append(part(f"m-slat-{i + 1}", [x0 + 40, y_top, a, x1 - 40, y_top + 8, a + 53], mat=slat_col))
    out.append({"id": "mattress", "kind": "mattress", "box": box(x0 + 5, y_top + 8, z0 + 5, x1 - 5, y_top + 8 + mattress, z1 - 5)})
    return out


def line_rect(pid, x0, y0, x1, y1, z, d=1.6, mat="patina"):
    """A patina (or gilded) line round a rectangle in the front plane at depth z: four thin rods (rods stay out of
    the checker's extent and overlap tests — a moulding would be counted 16 mm deep)."""
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out = []
    for k in range(4):
        a, b = pts[k], pts[(k + 1) % 4]
        out.append({"id": f"{pid}-{k + 1}", "kind": "rod", "mat": mat, "from": [fmt(a[0]), fmt(a[1]), fmt(z)],
                    "to": [fmt(b[0]), fmt(b[1]), fmt(z)], "d": d})
    return out


def line(pid, a, b, d=1.6, mat="patina"):
    return {"id": pid, "kind": "rod", "mat": mat, "from": [fmt(v) for v in a], "to": [fmt(v) for v in b], "d": d}


def leg_square(pid, x, z, top, d=50, d2=34, sx=0, sz=0, mat="body", foot=0):
    """A square tapered leg from the underside `top` to the floor, its foot moved outwards by (sx, sz) (splayed);
    box = bounds for the checker."""
    fx, fz = x + sx, z + sz
    r = d / 2
    return {"id": pid, "kind": "rod", "section": "square", "mat": mat, "from": [fmt(x), fmt(top), fmt(z)],
            "to": [fmt(fx), fmt(foot), fmt(fz)], "d": d, "d2": d2,
            "box": box(min(x - r, fx - d2 / 2), foot, min(z - r, fz - d2 / 2), max(x + r, fx + d2 / 2), top,
                       max(z + r, fz + d2 / 2))}
