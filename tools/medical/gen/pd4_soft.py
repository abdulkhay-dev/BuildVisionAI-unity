"""Soft play of batch pediatric-5: XYRT-87 'Kid's heaven' (foam blocks: cube stack with the XYRT-88 drill tunnel,
stairs, slide, ramp, half-moon, round steps). Front = +z, x from the left seen from the front."""
from pd4lib import *

FOAM = {"blue": "leather#1f4fbf", "teal": "leather#1f9c80", "red": "leather#e11f22", "yel": "leather#f4c81c",
        "green": "leather#1e9a4a", "white": "leather#f2f2f2", "dark": "leather#3b4046", "black": "leather#16181b",
        "lblue": "leather#5a76c8"}


def ring(d, id, x0, x1, y, z, ro, ri, mat):
    """A tunnel band (axis x) from x0 to x1, outer / inner radius."""
    L = x1 - x0
    d.lathe(id, [x0, y, z], [[ri, 0], [ro, 0], [ro, L], [ri, L], [ri, 0]], mat, axis="x", caps=False, sides=40)


def xyrt87():
    W, DD, H = 2600, 2300, 900
    d = D("xyrt-87", [W, DD, H], dict(FOAM))
    cx0, cx1, cz0, cz1 = 1250, 1850, 500, 1100
    # cube stack: lower block, upper cube (left face teal), seam
    d.box("block-low", [cx0, 0, cz0, cx1, 450, cz1], "blue", r=25, puff=8)
    d.box("cube-up", [cx0, 452, cz0, cx1, H, cz1], "blue", r=25, puff=8)
    d.box("cube-up-left", [cx0 - 6, 470, cz0 + 15, cx0 + 2, H - 18, cz1 - 15], "teal", r=6)
    # drill tunnel through the upper cube along x: banded ends sticking out both sides
    ty, tz, ro, ri = 672, 800, 215, 150
    ring(d, "tun-core", cx0 - 10, cx1 + 10, ty, tz, ro - 10, ri, "blue")
    bands = [("teal", 45), ("white", 8), ("blue", 55), ("white", 8), ("yel", 55), ("white", 8), ("red", 50)]
    x = cx0 - 225
    for i, (m, w) in enumerate(bands):
        ring(d, f"tun-l{i}", x, x + w, ty, tz, ro if m != "white" else ro - 4, ri, m)
        x += w
    x = cx1 + 225
    for i, (m, w) in enumerate(bands):
        ring(d, f"tun-r{i}", x - w, x, ty, tz, ro if m != "white" else ro - 4, ri, m)
        x -= w
    d.lathe("tun-lip", [cx0 - 225, ty, tz], [[ri - 5, 0], [ri + 30, 0], [ri + 30, 4], [ri - 5, 4], [ri - 5, 0]], "lblue",
            axis="x", caps=False, sides=40)
    # red stairs (photo): two stair modules side by side in front of the cube's right half, 5 steps down to the
    # front; the left module (dark grey sides) reaches further forward, the right module (black sides) is set back
    # two steps, so its black stepped left side shows above the left module's treads
    run, rise = 220, 90
    def stairs(id, x0, x1, zt, side_l, side_r):
        for k in range(5):
            top = 450 - rise * k
            z0 = cz0 + 80 if k == 0 else zt + run * k
            d.box(f"{id}-step{k}", [x0, 0, z0, x1, top, zt + run * (k + 1)], "red", r=12, puff=3)
        side = [(cz0 + 80, 0), (cz0 + 80, 450)]
        for k in range(5):
            side += [(zt + run * (k + 1), 450 - rise * k), (zt + run * (k + 1), 450 - rise * (k + 1))]
        d.slab(f"{id}-side-l", "side", P(side), [x0 - 8, x0 + 2], side_l, r=2)
        d.slab(f"{id}-side-r", "side", P(side), [x1 - 2, x1 + 8], side_r, r=2)
    sx0, sxm, sx1 = 1560, 1930, 2300
    stairs("stl", sx0, sxm, cz1, "dark", "dark")
    stairs("str", sxm + 10, sx1, cz1 - 2 * run, "black", "black")
    # round steps in front of the cube's left half: blue, red, yellow half discs (cut by the stairs)
    rx, rz = 1420, cz1
    for nm, r_, y0, y1, m in (("disc-b", 520, 0, 110, "blue"), ("disc-r", 400, 110, 230, "red"),
                              ("disc-y", 270, 230, 350, "yel")):
        pts = [polar(rx, rz, r_, a) for a in range(0, 181, 6)]
        pts = [(min(px, sx0 - 10), pz) for px, pz in pts]
        d.slab(nm, "top", P(pts), [y0, y1], m, r=14)
    d.box("green-block", [cx0 - 20, 350, cz1, cx0 + 260, 480, cz1 + 140], "green", r=14, puff=4)
    # slide: red wedge with rainbow stripes from the cube's left face down to the front left
    sr = rot("y", 38, [cx0, 0, 860])
    zs0, zs1 = 680, 1060
    d.slab("slide", "front", P([(cx0 - 900, 0), (cx0, 0), (cx0, 470), (cx0 - 40, 470)]), [zs0, zs1], "red", r=14,
           rot=sr)
    slope = math.degrees(math.atan2(470, 860))
    cols = ["yel", "lblue", "red", "white", "yel", "lblue", "red", "white", "yel", "lblue"]
    wst = (zs1 - zs0 - 40) / len(cols)
    for i, m in enumerate(cols):
        z = zs0 + 20 + i * wst
        d.box(f"stripe{i}", [cx0 - 900, 0, z, cx0 - 900 + 985, 5, z + wst - 3], m, soft=True,
              rot={"axis": "z", "deg": round(slope, 2), "about": [cx0 - 900, 0, 0]},
              rots=[{"axis": "y", "deg": 38, "about": [cx0, 0, 860]}])
    # green ramp at the far left with a flat mat in front, blue half-moon cradle on it
    d.slab("ramp", "side", P([(250, 0), (1300, 0), (1300, 60), (250, 330)]), [0, 560], "green", r=14)
    d.box("mat", [0, 0, 1300, 560, 60, 1850], "green", r=14, puff=3)
    hm = [(80, 280), (520, 280), (520, 560), (470, 560)] + \
         [(300 + 170 * math.cos(math.radians(t)), 560 - 170 * math.sin(math.radians(t))) for t in range(0, 181, 10)] + \
         [(130, 560), (80, 560)]
    d.slab("half-moon", "front", P(hm), [260, 500], "blue", r=18)
    return d


if __name__ == "__main__":
    main({"xyrt-87": xyrt87})
