"""Helpers for the hydro-3 / hydro-4 generators (steam beds, capsules, fumigation units, paraffin wax devices).
Each h3_*.py writes only its own devices' design files."""
import math, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from h1lib import *          # D, P, ring, rr, ell, offset, arc, sec, rot, rep
# p1lib re-binds D.decal/bar/lathe/... with physio-1's argument order: keep lib's methods (review 2026-10-03:
# before this every decal of these generators got mat='front', face=<material> and rendered wrong)
_LIB = {k: getattr(D, k) for k in ('bar', 'lathe', 'sphere', 'decal', 'slab', 'loft')}
from p1lib import text, text_len, _FONT
for _k, _f in _LIB.items(): setattr(D, _k, _f)

# extra glyphs for the brand name 翔宇医疗 (cap box 0..1)
_FONT.setdefault("医", (0.9, [[(0.9, 0.95), (0.05, 0.95), (0.05, 0.0), (0.9, 0.0)], [(0.32, 0.86), (0.24, 0.66)],
                             [(0.26, 0.72), (0.76, 0.72)], [(0.16, 0.46), (0.82, 0.46)],
                             [(0.49, 0.72), (0.49, 0.46), (0.24, 0.13)], [(0.52, 0.4), (0.78, 0.12)]]))
_FONT.setdefault("疗", (0.95, [[(0.55, 1.0), (0.55, 0.9)], [(0.18, 0.9), (0.95, 0.9)], [(0.18, 0.9), (0.18, 0.4), (0.02, 0.04)],
                             [(0.0, 0.74), (0.09, 0.64)], [(0.0, 0.52), (0.09, 0.42)],
                             [(0.38, 0.72), (0.88, 0.72), (0.63, 0.52)], [(0.63, 0.52), (0.63, 0.0), (0.52, 0.05)]]))
_FONT.setdefault("1", (0.3, [[(0.0, 0.8), (0.25, 1.0), (0.25, 0.0)]]))
_FONT.setdefault("b", (0.48, [[(0, 1), (0, 0)], [(0, 0.45), (0.15, 0.6), (0.35, 0.62), (0.48, 0.5), (0.48, 0.12),
                                                (0.35, 0), (0.15, 0), (0, 0.12)]]))
_FONT.setdefault("x", (0.48, [[(0, 0.62), (0.48, 0)], [(0, 0), (0.48, 0.62)]]))
_FONT.setdefault("/", (0.45, [[(0.0, 0.0), (0.45, 1.0)]]))


def text3(d, id, s, origin, h, mat, u=(1, 0, 0), v=(0, 1, 0), face="front", stroke=None, gap=0.28, soft=True, surf=None):
    """Text with an explicit reading direction u and up direction v (3D unit vectors in the face plane).
    origin = the bottom-left of the first letter. Returns the number of strokes."""
    st = stroke or max(1.5, h * 0.14)
    n = 0; pen = 0.0
    for c in s:
        if c not in _FONT:
            pen += 0.45; continue
        wch, polys = _FONT[c]
        for poly in polys:
            for a, b in zip(poly, poly[1:]):
                mu, mv = (pen + (a[0] + b[0]) / 2) * h, (a[1] + b[1]) / 2 * h
                du, dv = (b[0] - a[0]) * h, (b[1] - a[1]) * h
                ln = math.hypot(du, dv)
                at = [origin[k] + mu * u[k] + mv * v[k] for k in range(3)]
                if surf: at = surf(at)
                w = [du * u[k] + dv * v[k] for k in range(3)]
                if face in ("front", "back"):
                    ax, ang = "z", math.degrees(math.atan2(w[1], w[0]))
                elif face in ("left", "right"):
                    ax, ang = "x", -math.degrees(math.atan2(w[1], w[2]))
                else:
                    ax, ang = "y", math.degrees(math.atan2(-w[2], w[0]))
                d.add(f"{id}-{n}", "decal", mat, at=at, size=[ln + st, st], face=face, soft=soft,
                      rot={"axis": ax, "deg": round(ang, 1), "about": at})
                n += 1
        pen += wch + gap
    return n

ROOT = "/Users/abdulxay/Documents/works/ansormed/unity"
# compare.py finds a Python with Pillow by itself (~/.cache/house-med-venv)
PY = sys.executable

BLUE = "gloss#2b78d0"        # Xiangyu logo blue


def go(d, timeout=150):
    """Save, wait for the watcher's render (.txt newer than the json), build the compare sheet."""
    d.save()
    i = d.d["id"]
    j = f"{ROOT}/Assets/House4696/Resources/Medical/Designs/{i}.json"
    t = f"{ROOT}/tools/medical/renders/{i}.txt"
    t0 = time.time()
    while time.time() - t0 < timeout:
        if os.path.exists(t) and os.path.getmtime(t) > os.path.getmtime(j):
            break
        time.sleep(2)
    else:
        print(i, "TIMEOUT"); return
    print(i, open(t).read().strip())
    subprocess.run([PY, f"{ROOT}/tools/medical/compare.py", i])


def disc(d, id, at, r, face, mat, t=1.5, **kw):
    """Thin round plate on a flat face (front/back/left/right/top), centre `at` on the face."""
    ax = {"front": "z", "back": "z", "left": "x", "right": "x", "top": "y"}[face]
    x, y, z = at
    if face == "back": z -= t
    if face == "left": x -= t
    prof = [[0, 0], [r, 0], [r, t], [0, t]]
    return d.lathe(id, [x, y, z], prof, mat, axis=ax, soft=True, **kw)


def logo(d, id, at, h, face="front", blue=BLUE, white="gloss#ffffff", words=True, word_mat=None, surf=None):
    """Xiangyu logo: a round blue badge with a white T-cross, then (words) '翔宇' strokes + 'XIANGYU MEDICAL' under it.
    at = centre of the badge on the face; h = badge diameter."""
    x, y, z = at
    r = h / 2
    disc(d, id + "-badge", at, r, face, blue)
    o = 2.2
    if face == "front":
        d.decal(id + "-v", [x + r * 0.08, y - r * 0.12, z + o], [h * 0.16, h * 0.62], "front", white, soft=True)
        d.decal(id + "-h", [x - r * 0.05, y + r * 0.3, z + o], [h * 0.7, h * 0.14], "front", white, soft=True)
    elif face in ("left", "right"):
        s = -1 if face == "left" else 1
        d.decal(id + "-v", [x + s * o, y - r * 0.12, z + s * r * 0.08], [h * 0.16, h * 0.62], face, white, soft=True)
        d.decal(id + "-h", [x + s * o, y + r * 0.3, z - s * r * 0.05], [h * 0.7, h * 0.14], face, white, soft=True)
    if not words:
        return
    wm = word_mat or blue
    ch = h * 0.5
    if face == "front":
        u, n0 = (1, 0, 0), [x + r * 1.3, y - ch * 0.05, z + 1.5]
    elif face == "back":
        u, n0 = (-1, 0, 0), [x - r * 1.3, y - ch * 0.05, z - 1.5]
    elif face == "left":
        u, n0 = (0, 0, -1), [x - 1.5, y - ch * 0.05, z - r * 1.3]
    else:
        u, n0 = (0, 0, 1), [x + 1.5, y - ch * 0.05, z + r * 1.3]
    text3(d, id + "-cn", "翔宇医疗", n0, ch, wm, u=u, face=face, gap=0.2, surf=surf)
    e0 = [n0[k] + (-h * 0.42 if k == 1 else 0) for k in range(3)]
    text3(d, id + "-en", "XIANGYU MEDICAL", e0, h * 0.15, wm, u=u, face=face, gap=0.3, surf=surf)


def casters(d, id, pts, dd=75, mat=None):
    """Castors: floor points [(x, z), ...]; the castor is dd + 25 tall."""
    d.add(id, "caster", mat, at=[pts[0][0], 0, pts[0][1]], d=dd,
          copies=[[p[0] - pts[0][0], 0, p[1] - pts[0][1]] for p in pts[1:]])


def btn(d, id, at, dd, face, mat, h=8, ring_mat=None, **kw):
    """Round push button on a flat face (lathe dome)."""
    ax = {"front": "z", "top": "y", "left": "x", "right": "x"}[face]
    r = dd / 2
    prof = [[0, 0], [r, 0], [r, h * 0.6], [r * 0.7, h], [0, h]]
    if ring_mat:
        d.lathe(id + "-ring", at, [[0, 0], [r * 1.35, 0], [r * 1.35, 2], [0, 2]], ring_mat, axis=ax, soft=True,
                **{k: v for k, v in kw.items() if k in ("copies", "repeat", "mirror")})
    return d.lathe(id, at, prof, mat, axis=ax, soft=True, **kw)


def rp(pts, r):
    """SVG path of a closed polygon, corner i rounded by r[i] (or one r) with quadratic corners."""
    n = len(pts); out = []
    rs = r if isinstance(r, (list, tuple)) else [r] * n
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        def toward(a, b, dist):
            dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; k = min(dist, L / 2) / L
            return (a[0] + dx * k, a[1] + dy * k)
        if rs[i] <= 0:
            out.append(("M" if i == 0 else "L") + f" {p1[0]:.1f} {p1[1]:.1f}"); continue
        a = toward(p1, p0, rs[i]); b = toward(p1, p2, rs[i])
        out.append(("M" if i == 0 else "L") + f" {a[0]:.1f} {a[1]:.1f} Q {p1[0]:.1f} {p1[1]:.1f} {b[0]:.1f} {b[1]:.1f}")
    return " ".join(out) + " Z"


def rrp(x0, y0, x1, y1, r):
    """SVG rounded rectangle (exact arcs via rr points)."""
    return P(rr(x0, y0, x1, y1, r))


def turned(d, fn, *turns):
    """Run fn() (which adds parts) and append the turns (rot dicts) as `rots` to every part it added:
    lettering drawn flat, then tilted with a sloping panel (review 2026-10-03)."""
    n0 = len(d.d["parts"])
    fn()
    for p in d.d["parts"][n0:]:
        p["rots"] = list(p.get("rots") or []) + list(turns)
