"""kinesio-1 helpers (on top of lib.py)."""
import math
from lib import *


def ushell(cx, cz, r, t, open_to="-z"):
    """Half-ring outline in a plane (a, b) = (cx, cz) opening to -b (or +b): a C-shaped cradle / calf shell."""
    s = 1 if open_to == "-z" else -1
    o = r * s
    i = (r - t) * s
    return (f"M {cx - r} {cz} Q {cx - r} {cz + o} {cx} {cz + o} Q {cx + r} {cz + o} {cx + r} {cz} "
            f"L {cx + r - t} {cz} Q {cx + r - t} {cz + i} {cx} {cz + i} Q {cx - r + t} {cz + i} {cx - r + t} {cz} Z")


def ring_disc(d, id, at, r_out, r_in, ring_mat, face_mat, axis="x", t=3.0, out=1, **kw):
    """A flat disc of face_mat with a thin coloured ring round it (pink/grey drum faces): two stacked lathes."""
    d.lathe(id + "-ring", at, [[0, 0], [r_out, 0], [r_out, t], [0, t]], ring_mat, axis=axis, **kw)
    a2 = list(at)
    k = {"x": 0, "y": 1, "z": 2}[axis]
    a2[k] += 0.6 * out
    d.lathe(id + "-face", a2, [[0, 0], [r_in, 0], [r_in, t], [0, t]], face_mat, axis=axis, **kw)


def controller(d, id, x0, z0, plug, lie=True, shell="plastic#f1f2f0", face="gloss#1f5d9c"):
    """CPM hand controller (white, dark-blue face, 3 buttons) lying on the table at (x0, z0) along x,
    a black coiled cable to the plug point [x, y, z]."""
    L, W, T = 150, 80, 26
    d.box(id, [x0, 0, z0, x0 + L, T, z0 + W], shell, r=10)
    d.box(id + "-face", [x0 + 8, T - 2, z0 + 8, x0 + L - 8, T + 1, z0 + W - 8], face, r=6, soft=True)
    d.cyl(id + "-btn", [x0 + 60, T, z0 + 40], [x0 + 60, T + 5, z0 + 40], 16, "gloss#f4f4f2", soft=True,
          copies=[[45, 0, 0]])
    d.cyl(id + "-btn-red", [x0 + 82, T, z0 + 22], [x0 + 82, T + 5, z0 + 22], 14, "gloss#d2262a", soft=True)
    # cable: coil from the controller end toward the plug, then a plain cord up to it
    a = [x0 - 5, 12, z0 + W / 2]
    mid = [(a[0] + plug[0]) / 2, 14, (a[2] + plug[2]) / 2]
    d.coil(id + "-coil", a, mid, 26, 6, 16, "rubber#18191b", soft=True)
    d.tube(id + "-cord", [mid, [mid[0], 12, mid[2]], [plug[0], 20, plug[2]], plug], 7, "rubber#18191b",
           bend=40, soft=True)


def ellipse(cx, cz, rx, rz):
    k = 0.5523
    return (f"M {cx + rx} {cz} C {cx + rx} {cz + rz * k} {cx + rx * k} {cz + rz} {cx} {cz + rz} "
            f"C {cx - rx * k} {cz + rz} {cx - rx} {cz + rz * k} {cx - rx} {cz} "
            f"C {cx - rx} {cz - rz * k} {cx - rx * k} {cz - rz} {cx} {cz - rz} "
            f"C {cx + rx * k} {cz - rz} {cx + rx} {cz - rz * k} {cx + rx} {cz} Z")


# lettering (review 2026-10-02): p1lib.text() draws real letters; p1lib patches D's helpers with other
# argument orders, so keep this batch's D methods as they were
_keep = {k: D.__dict__[k] for k in ("bar", "lathe", "sphere", "decal", "screen", "slab", "loft", "caster") if k in D.__dict__}
from p1lib import text, text_len  # noqa: E402
for _k in ("bar", "lathe", "sphere", "decal", "screen", "slab", "loft", "caster"):
    if _k in _keep:
        setattr(D, _k, _keep[_k])
    elif _k in D.__dict__:
        delattr(D, _k)


def text_right(d, id, s, origin, h, mat, along=(1, 0), **kw):
    """Lettering on a +x ("right") face, reading correctly when seen from +x: p1lib.text() lays glyphs in the
    (z, y) plane, which reads mirrored from +x — so draw them reading along +z from origin, then mirror the new
    strokes in z about the line's middle (origin = the bottom-left of the first letter as SEEN, i.e. its max z)."""
    n0 = len(d.d["parts"])
    L = text_len(s, h) * abs(along[0]) if along[1] == 0 else 0.0
    z_hi = origin[2]
    o = [origin[0], origin[1], z_hi - L] if along == (1, 0) else list(origin)
    n = text(d, id, s, o, h, mat, along=along, face="right", **kw)
    if along == (1, 0):
        zc = o[2] + L / 2
    else:  # a slanted line: mirror about the origin's z
        zc = origin[2]
    for p in d.d["parts"][n0:]:
        p["at"][2] = round(2 * zc - p["at"][2], 1)
        if "rot" in p:
            p["rot"]["deg"] = -p["rot"]["deg"]
            p["rot"]["about"] = list(p["at"])
    return n
