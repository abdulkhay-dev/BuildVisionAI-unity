"""Helpers shared by the generators of Челси Бум, Луна, Линель and Соната Бум (gen/chelsi-bum.py, luna.py, linel.py,
sonata-bum.py): parts, drawer boxes, handles, cut lists and catalogue fragments.

Coordinates as in Docs/casegoods-designs.md: mm, x left → right, y up from the floor, z from the wall to the front.
"""
import json
import math
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))


def r1(v):
    return round(v * 10) / 10


def box(x0, y0, z0, x1, y1, z1):
    return [r1(x0), r1(y0), r1(z0), r1(x1), r1(y1), r1(z1)]


def P(n, b, pid=None, **kw):
    """A cut-list part: n = its number, b = the box."""
    p = {"n": str(n)} if n is not None else {}
    if pid:
        p["id"] = pid
    p["box"] = box(*b)
    p.update(kw)
    return p


def H(pid, b, letter, **kw):
    """Hardware that shows (legs, glides, castors, rails): covers its letter."""
    p = {"id": pid, "box": box(*b), "covers": [letter]}
    p.update(kw)
    return p


def back(n, b, pid=None, **kw):
    return P(n, b, pid, kind="back", **kw)


def front(n, b, pid=None, **kw):
    return P(n, b, pid, kind="front", **kw)


def rounded_rect_path(a0, b0, a1, b1, corners):
    """SVG outline of a rectangle in its plane (a right, b up) with rounded corners: corners = {"tl": r, "tr": r,
    "bl": r, "br": r} (the quarter circles are written as cubic curves)."""
    k = 0.5523
    tl, tr, bl, br = (corners.get(c, 0) for c in ("tl", "tr", "bl", "br"))
    s = [f"M {r1(a0 + bl)} {r1(b0)}", f"L {r1(a1 - br)} {r1(b0)}"]
    if br:
        s.append(f"C {r1(a1 - br + k * br)} {r1(b0)} {r1(a1)} {r1(b0 + br - k * br)} {r1(a1)} {r1(b0 + br)}")
    s.append(f"L {r1(a1)} {r1(b1 - tr)}")
    if tr:
        s.append(f"C {r1(a1)} {r1(b1 - tr + k * tr)} {r1(a1 - tr + k * tr)} {r1(b1)} {r1(a1 - tr)} {r1(b1)}")
    s.append(f"L {r1(a0 + tl)} {r1(b1)}")
    if tl:
        s.append(f"C {r1(a0 + tl - k * tl)} {r1(b1)} {r1(a0)} {r1(b1 - tl + k * tl)} {r1(a0)} {r1(b1 - tl)}")
    s.append(f"L {r1(a0)} {r1(b0 + bl)}")
    if bl:
        s.append(f"C {r1(a0)} {r1(b0 + bl - k * bl)} {r1(a0 + bl - k * bl)} {r1(b0)} {r1(a0 + bl)} {r1(b0)}")
    return " ".join(s) + " Z"


def drawer_box(tag, ns, x0, x1, y0, hs, zb, zf, hb=None, t=16.0, bottom=None, under=False, back_t=None, mat=None,
               groove=10.0):
    """A drawer box between x0..x1 (outer), sides hs high from y0, from zb (back) to zf (the front's back face).
    ns = (left side, right side, back, bottom) cut-list numbers. The back (hb high, default hs − 14, back_t thick
    = t) stands on the bottom between the sides. bottom = (width, length, thickness) as listed: centred on the box,
    from zb, in grooves `groove` mm up — or nailed under the box (under=True)."""
    hb = hb if hb is not None else hs - 14
    back_t = back_t or t
    bw, bl, bt = bottom if bottom else (x1 - x0 - 2 * t + 11, zf - zb + 5, 3.0)
    cx = (x0 + x1) / 2
    kw = {"mat": mat} if mat else {}
    out = [P(ns[0], (x0, y0, zb, x0 + t, y0 + hs, zf), f"{ns[0]}-{tag}", **kw),
           P(ns[1], (x1 - t, y0, zb, x1, y0 + hs, zf), f"{ns[1]}-{tag}", **kw)]
    if under:
        out.append(P(ns[2], (x0 + t, y0, zb, x1 - t, y0 + hb, zb + back_t), f"{ns[2]}-{tag}", **kw))
        out.append(back(ns[3], (cx - bw / 2, y0 - bt, zb, cx + bw / 2, y0, zb + bl), f"{ns[3]}-{tag}"))
    else:
        out.append(P(ns[2], (x0 + t, y0 + hs - hb, zb, x1 - t, y0 + hs, zb + back_t), f"{ns[2]}-{tag}", **kw))
        out.append(back(ns[3], (cx - bw / 2, y0 + groove, zb, cx + bw / 2, y0 + groove + bt, zb + bl), f"{ns[3]}-{tag}"))
    return out


def bar(pid, x, y, z, length, dirn="up", band=12, t=10, standoff=24, post=None, letter="k", section=None, mat="metal"):
    """A bar handle on a face at z: centre [x, y], along dirn."""
    p = {"id": pid, "kind": "handle", "model": "bar", "mat": mat, "at": [r1(x), r1(y)], "dir": dirn, "d": length,
         "band": band, "t": t, "standoff": standoff, "z": r1(z), "covers": [letter]}
    if post:
        p["post"] = post
    if section:
        p["section"] = section
    return p


def knob(pid, x, y, z, d=30, standoff=22, letter="k", mat="metal"):
    return {"id": pid, "kind": "handle", "model": "knob", "mat": mat, "at": [r1(x), r1(y)], "d": d, "t": 10,
            "standoff": standoff, "z": r1(z), "covers": [letter]}


def dmove(name, parts, travel=300):
    return {"type": "drawer", "name": name, "parts": [p if isinstance(p, str) else p["id"] if "id" in p else p["n"] for p in parts],
            "travel": travel}


def door(name, parts, hinge="left", angle=100, axis=None):
    m = {"type": "door", "name": name, "parts": [p if isinstance(p, str) else p.get("id") or p["n"] for p in parts],
         "hinge": hinge, "angle": angle}
    if axis:
        m["axis"] = [r1(axis[0]), r1(axis[1])]
    return m


def ids(parts):
    return [p.get("id") or p["n"] for p in parts]


def glides(xs, zs, h, d=24, letter="s", mat="black", tag="g"):
    out, k = [], 0
    for x in xs:
        for z in zs:
            k += 1
            out.append(H(f"{tag}-{k}", (x - d / 2, 0, z - d / 2, x + d / 2, h, z + d / 2), letter, kind="tube", mat=mat))
    return out


def feet(xs, zs, h, w=60, dz=40, letter="k1", mat="black", tag="f"):
    """Square plastic feet (Челси)."""
    out, k = [], 0
    for x in xs:
        for z in zs:
            k += 1
            out.append(H(f"{tag}-{k}", (x - w / 2, 0, z - dz / 2, x + w / 2, h, z + dz / 2), letter, mat=mat, edge=2))
    return out


def write_cutlist(did, code, rows, source, note=None):
    """gen/cutlists/<did>.json: rows = [(n, a, b, t or None, count, name)]."""
    out = {"code": code, "source": source}
    if note:
        out["note"] = note
    rr = []
    for n, a, b, t, c, name in rows:
        size = [a, b] if t is None else [a, b, t]
        rr.append({"n": str(n), "name": name, "size": size, "count": c})
    out["rows"] = rr
    path = os.path.join(HERE, "cutlists", did + ".json")
    with open(path, "w") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return path


def write_fragment(slug, finishes, collections, models, profiles=None):
    frag = {"finishes": finishes, "profiles": profiles or {}, "collections": collections, "models": models}
    path = os.path.join(HERE, f"{slug}_catalog.json")
    with open(path, "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=2)
    return path


def notch_top(x0, y0, x1, y1, cx, w, dep, flat=None):
    """Front outline (front plane) with a shallow notch cut down from the top edge, centred at cx, w wide at the edge,
    dep deep; its sides slope (flat = the flat bottom's width, default w − 2·dep·1.6)."""
    flat = flat if flat is not None else max(20.0, w - 3.2 * dep)
    a, b = cx - w / 2, cx + w / 2
    fa, fb = cx - flat / 2, cx + flat / 2
    return (f"M {r1(x0)} {r1(y0)} L {r1(x1)} {r1(y0)} L {r1(x1)} {r1(y1)} L {r1(b)} {r1(y1)} "
            f"C {r1(b - (b - fb) * 0.5)} {r1(y1)} {r1(fb + (b - fb) * 0.4)} {r1(y1 - dep)} {r1(fb)} {r1(y1 - dep)} "
            f"L {r1(fa)} {r1(y1 - dep)} C {r1(fa - (fa - a) * 0.4)} {r1(y1 - dep)} {r1(a + (fa - a) * 0.5)} {r1(y1)} {r1(a)} {r1(y1)} "
            f"L {r1(x0)} {r1(y1)} Z")


def notch_side(x0, y0, x1, y1, side, cy, h, dep):
    """Front outline with a lens-shaped grip cut into its vertical edge (side 'l' or 'r'), centred at cy, h long."""
    a, b = cy - h / 2, cy + h / 2
    if side == "r":
        return (f"M {r1(x0)} {r1(y0)} L {r1(x1)} {r1(y0)} L {r1(x1)} {r1(a)} "
                f"C {r1(x1 - dep * 1.33)} {r1(a + h * 0.25)} {r1(x1 - dep * 1.33)} {r1(b - h * 0.25)} {r1(x1)} {r1(b)} "
                f"L {r1(x1)} {r1(y1)} L {r1(x0)} {r1(y1)} Z")
    return (f"M {r1(x0)} {r1(y0)} L {r1(x1)} {r1(y0)} L {r1(x1)} {r1(y1)} L {r1(x0)} {r1(y1)} L {r1(x0)} {r1(b)} "
            f"C {r1(x0 + dep * 1.33)} {r1(b - h * 0.25)} {r1(x0 + dep * 1.33)} {r1(a + h * 0.25)} {r1(x0)} {r1(a)} Z")


__all__ = ["dump", "P", "H", "back", "front", "box", "r1", "rounded_rect_path", "drawer_box", "bar", "knob", "dmove",
           "door", "ids", "glides", "feet", "write_cutlist", "write_fragment", "notch_top", "notch_side", "math"]


# ---------------------------------------------------------------------------------------------------- coupe wardrobes
def coupe(W, D, Hh, sections, plinth=70, frame_mat="chrome"):
    """The carcass of a Pinskdrev «Бум» sliding-door wardrobe (Челси Бум / Соната Бум 1529 / 2027 × 650 × 2292), by
    photo: sides 16 full height and depth to the floor, the bottom 16 on a plinth (a rail recessed 20 behind the doors
    and one at the back), the top 16 between the sides, ХДФ back 3 in grooves; partitions / shelves 16 behind the door
    zone (the last 90 mm: two tracks); aluminium tracks under the top and on the bottom.
    sections = [(width, kind)] left to right: "rail" (hat shelf 1860 + rail) or "shelves" (5 shelves)."""
    T = 16
    zc = D - 90
    yb0, yb1 = plinth, plinth + T
    yt0 = Hh - T
    p = [P(None, (0, 0, 0, T, Hh, D), "side-l"), P(None, (W - T, 0, 0, W, Hh, D), "side-r"),
         P(None, (T, yt0, 0, W - T, Hh, D), "top"), P(None, (T, yb0, 0, W - T, yb1, D), "bottom"),
         P(None, (T, 0, D - 36, W - T, plinth, D - 20), "plinth"), P(None, (T, 0, 40, W - T, plinth, 56), "plinth-b"),
         back(None, (T - 6, yb0 - 6, 8, W - T + 6, yt0 + 6, 11), "back", mat="white"),
         H("track-top", (T, yt0 - 20, zc + 5, W - T, yt0, D - 5), "track", mat=frame_mat),
         H("track-bot", (T, yb1, zc + 5, W - T, yb1 + 10, D - 5), "track", mat=frame_mat)]
    x = T
    for i, (w, kind) in enumerate(sections):
        x0, x1 = x, x + w
        if i < len(sections) - 1:
            p.append(P(None, (x1, yb1, 12, x1 + T, yt0, zc), f"part-{i + 1}"))
        if kind == "rail":
            p.append(P(None, (x0 + 0.5, 1860, 12, x1 - 0.5, 1876, zc - 2), f"hat-{i + 1}"))
            cz = (12 + zc) / 2
            p.append(H(f"rail-{i + 1}", (x0, 1770, cz - 12.5, x1, 1795, cz + 12.5), "rail", kind="tube", mat="chrome"))
        else:
            n = 5
            step = (yt0 - yb1 - n * T) / (n + 1)
            for k in range(n):
                y = yb1 + (k + 1) * step + k * T
                p.append(P(None, (x0 + 0.5, y, 12, x1 - 0.5, y + T, zc - 2), f"shelf-{i + 1}-{k + 1}"))
        x = x1 + T
    return p


def coupe_doors(W, D, Hh, n, fills, plinth=70, frame_mat="chrome", overlap=25):
    """The sliding doors of coupe(): n doors on two tracks (alternate), each dw = (W − 32 + (n − 1)·25) / n wide, in an
    aluminium frame (side profiles 20 × 36, rails 30); fills[i] = [(y0, y1, role or "mirror")] panels of door i from
    the frame's bottom rail up, with a 10 mm cross profile between them. Returns (parts, moves)."""
    T = 16
    op = W - 2 * T
    dw = (op + (n - 1) * overlap) / n
    y0, y1 = plinth + T + 12, Hh - T - 22
    parts, moves = [], []
    for i in range(n):
        x0 = T + i * (dw - overlap)
        x1 = x0 + dw
        back_track = (i % 2 == 0)
        z0 = D - 80 if back_track else D - 44
        z1 = z0 + 36
        tag = f"d{i + 1}"
        ps = [P(None, (x0, y0, z0, x0 + 20, y1, z1), f"{tag}-prof-l", mat=frame_mat, edge=2),
              P(None, (x1 - 20, y0, z0, x1, y1, z1), f"{tag}-prof-r", mat=frame_mat, edge=2),
              P(None, (x0 + 20, y0, z0 + 4, x1 - 20, y0 + 30, z1 - 4), f"{tag}-rail-b", mat=frame_mat, edge=1),
              P(None, (x0 + 20, y1 - 30, z0 + 4, x1 - 20, y1, z1 - 4), f"{tag}-rail-t", mat=frame_mat, edge=1)]
        fy, top = y0 + 30, y1 - 30
        for k, (a, b, role) in enumerate(fills[i]):
            ya, yb = fy + a, min(fy + b, top)
            if role == "mirror":
                ps.append({"id": f"{tag}-fill-{k + 1}", "kind": "mirror",
                           "box": box(x0 + 20, ya, z0 + 14, x1 - 20, yb, z0 + 18)})
                ps.append(P(None, (x0 + 20, ya, z0 + 10, x1 - 20, yb, z0 + 14), f"{tag}-fill-{k + 1}-b", kind="back"))
            else:
                ps.append(P(None, (x0 + 20, ya, z0 + 13, x1 - 20, yb, z0 + 23), f"{tag}-fill-{k + 1}", kind="front",
                            mat=role))
            if k < len(fills[i]) - 1:
                ps.append(P(None, (x0 + 20, yb - 5, z0 + 10, x1 - 20, yb + 5, z0 + 26), f"{tag}-sep-{k + 1}",
                            mat=frame_mat, edge=1))
        parts += ps
        dx = (dw - overlap) if i == 0 else -(dw - overlap)
        moves.append({"type": "slide", "name": f"door_{i + 1}", "parts": [q["id"] for q in ps], "by": [r1(dx), 0, 0]})
    return parts, moves
