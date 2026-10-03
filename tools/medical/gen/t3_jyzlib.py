"""Shared parts of the JYZ traction tables (table-3 batch): the cervical traction pole with its top arm, pulleys,
rope, spring scale, spreader and head sling; the console cabinet; harness belts; louvred doors."""
from lib import *

def pole(d, xp, zp, ybase, H, dirx, arm, style="rods", slingmat="fabric#c9bfe0", edgemat=None, ys=None, k=1.0,
         spreadmat="chrome", lattice=False):
    """Stainless pole at (xp, zp) from ybase to H; the top arm reaches `arm` mm along dirx (+1 / -1)."""
    xf = xp + dirx * arm                       # far pulley
    d.cyl("pole", [xp, ybase, zp], [xp, H - 60, zp], 40, "chrome")
    d.cyl("pole-collar", [xp, ybase, zp], [xp, ybase + 45, zp], 70, "white")
    d.box("pole-clamp", [xp - 32, H - 170, zp - 30, xp + 32, H - 40, zp + 30], "white", r=8)
    for i, y in enumerate((H - 150, H - 240) if style == "rods" else (H - 230,)):
        d.cyl(f"pole-knob-stem{i}", [xp - dirx * 30, y, zp], [xp - dirx * 60, y, zp], 12, "black")
        d.lathe(f"pole-knob{i}", [xp - dirx * 60, y, zp], [[0, 0], [22, 0], [24, 8], [16, 22], [0, 22]], "black",
                axis="x", rot=rot("y", 180, [xp - dirx * 60, y, zp]) if dirx > 0 else None)
    if style == "rods":
        d.cyl("arm-rod", [xp - dirx * 20, H - 35, zp], [xf + dirx * 25, H - 35, zp], 22, "chrome")
        d.box("arm-plate", [min(xp, xf) - 10, H - 75, zp - 22, max(xp, xf) + 10, H - 50, zp + 22], "white", r=6)
        tri = (f"M {xp} {H - 75} L {xf - dirx * 40} {H - 75} L {xp + dirx * 60} {H - 230} L {xp} {H - 230} Z")
    else:
        d.box("arm-bar", [min(xp, xf) - 10, H - 80, zp - 22, max(xp, xf) + 10, H - 30, zp + 22], "white", r=8)
        tri = (f"M {xp} {H - 80} L {xf - dirx * 60} {H - 80} L {xp + dirx * 40} {H - 250} L {xp} {H - 250} Z")
    if lattice and style == "rods":   # JYZ-IIIA photo: an open lattice truss (three triangular windows)
        def tw(p):
            return "M " + " L ".join(f"{xp + dirx * a:.1f} {H - b:.1f}" for a, b in p) + " Z "
        L_ = abs(xf - xp)
        tri += " " + tw([(25, 95), (L_ * 0.40, 95), (25, 205)]) + tw([(L_ * 0.46, 95), (L_ * 0.74, 95), (L_ * 0.30, 160)]) \
               + tw([(38, 214), (L_ * 0.40, 112), (L_ * 0.22, 175)])
    d.slab("arm-truss", "front", tri, [zp - 8, zp + 8], "white", r=3)
    if style != "rods":
        d.cyl("truss-hole", [xp + dirx * 120, H - 125, zp - 9], [xp + dirx * 120, H - 125, zp + 9], 50, "plastic#d9dde2")
    d.add("pulley-far", "wheel", "black", at=[xf, H - 62, zp], d=70, d2=20, axis="z")
    d.add("pulley-near", "wheel", "black", at=[xp + dirx * 70, H - 62, zp], d=60, d2=20, axis="z")
    for i, x in enumerate((xp + dirx * 80, xf - dirx * 50) if style == "rods" else (xf - dirx * 70,)):
        d.cyl(f"arm-knob-stem{i}", [x, H - 30, zp], [x, H - 5, zp], 12, "black")
        d.lathe(f"arm-knob{i}", [x, H - 22, zp], [[0, 0], [26, 0], [26, 8], [12, 22], [0, 22]], "black")
    # rope, spring scale, spreader, sling
    xr = xf + dirx * 34
    ys = ys if ys is not None else H - 800       # spreader height
    d.cyl("rope", [xr, H - 62, zp], [xr, ys + 260, zp], 4, "metal#d0d3d6", soft=True)
    d.cyl("scale", [xr, ys + 260, zp], [xr, ys + 90, zp], 26, "chrome")
    d.cyl("scale-hook", [xr, ys + 90, zp], [xr, ys + 20, zp], 8, "chrome", soft=True)
    sw = 175 * k
    # spreader (photos): a bar rising a little to the hook in the middle, its ends bent up into hooks
    d.tube("spreader", [[xr - sw, ys + 40 * k, zp], [xr - sw + 8, ys, zp], [xr, ys + 18, zp], [xr + sw - 8, ys, zp],
                        [xr + sw, ys + 40 * k, zp]], 11, spreadmat, bend=12)
    # head sling (photos): from each spreader end an outer and an inner strap hang down to the two ends of a wide padded
    # cup (one in front, one behind); the two inner straps cross in the middle, so the sling reads as a crossed X;
    # cups = a grey/lilac band over a slightly wider coloured band (the piping along both edges)
    def P(px, py, pz): return [xr + px * k, ys + py * k, zp + pz * k]
    hl, hr = P(-162, -18, 0), P(162, -18, 0)
    cups = {"a": [(-215, -215, 0), (-218, -330, 30), (-150, -420, 55), (-50, -445, 60), (40, -380, 45), (60, -240, 0)],
            "b": [(215, -195, 0), (218, -310, -30), (150, -400, -55), (50, -425, -60), (-40, -360, -45), (-60, -225, 0)]}
    for nm, pts in cups.items():
        path = [P(*q) for q in pts]
        d.strap("sling-cup-" + nm, path, [70 * k, 7], slingmat, bend=45 * k, soft=True, roll=0)
        if edgemat:
            d.strap("sling-pipe-" + nm, path, [86 * k, 4], edgemat, bend=45 * k, soft=True, roll=0)
    for nm, (top, e) in {"lo": (hl, cups["a"][0]), "li": (hl, cups["a"][-1]), "ro": (hr, cups["b"][0]),
                         "ri": (hr, cups["b"][-1])}.items():
        d.strap("sling-" + nm, [top, P(*e)], [44 * k, 4], slingmat, soft=True, roll=0 if nm[1] == "o" else 90)
    return xr


def belt(d, nm, x0, x1, y, z0, z1, mat="fabric#b9b4c9", stripe="fabric#7d7a9c", n=5, th=34):
    """An open traction harness lying across the table: a padded band with darker stripes (photos) + buckle."""
    d.box(nm, [x0, y, z0, x1, y + th, z1], mat, r=10, puff=8)
    st = (x1 - x0 - 30) / n
    d.box(nm + "-stripe", [x0 + 15 + st * 0.3, y + th - 14, z0 - 2, x0 + 15 + st * 0.7, y + th + 3, z1 + 2], stripe, r=4,
          copies=[[st * i, 0, 0] for i in range(1, n)])
    d.box(nm + "-buckle", [x0 + 30, y + th - 2, (z0 + z1) / 2 - 40, x1 - 30, y + th + 6, (z0 + z1) / 2 + 40], "fabric#3a3d48", r=4)


def louvres(d, nm, x, y, z, n=9, cols=3, colstep=95, mat="plastic#cfd3d8", copies=None):
    cp = [[c * colstep, 0, 0] for c in range(1, cols)]
    for c in (copies or []):
        cp += [[c[0] + k * colstep, c[1], c[2]] for k in range(cols)]
    d.box(nm, [x, y, z, x + 62, y + 7, z + 3], mat, r=2, soft=True, repeat=rep(n, [0, -24, 0]), copies=cp or None)
