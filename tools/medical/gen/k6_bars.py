"""XYG-1 parallel bars on a walkway platform with a correction board; XYG-2 parallel bars on floor plates."""
from k6lib import *

W, DEP = 3500, 1160


def xyg2():
    d = D("xyg-2", [W, DEP, 1200], {"rail": "metal#4a4e55", "cap": "gloss#1f3468", "white": "plastic#f1f1ee",
                                    "knob": "plastic#1d1f22", "inner": "metal#5e6563", "hole": "plastic#d6d8d6"})
    RY = 980          # rail centre (top 1000; adjustable 780-1200)
    XP = 420          # posts from the rail ends
    for z, out in ((260, -1), (900, 1)):
        d.cyl(f"rail{z}", [20, RY, z], [W - 20, RY, z], 40, "rail")
        d.sphere(f"cap{z}", [22, RY, z], 46, "cap", copies=[[W - 44, 0, 0]])
        for x in (XP, W - XP):
            n = f"{z}-{x}"
            d.cyl(f"post{n}", [x, 10, z], [x, 640, z], 50, "white")
            d.cyl(f"col{n}", [x, 620, z], [x, 660, z], 58, "white")
            d.cyl(f"in{n}", [x, 640, z], [x, RY - 40, z], 40, "inner")
            # ratchet holes of the inner tube
            d.cyl(f"hole{n}", [x, 690, z + out * 19], [x, 702, z + out * 19], 9, "hole", soft=True,
                  repeat=rep(9, [0, 24, 0]))
            star_knob(d, f"knob{n}", [x, 640, z + out * 29], "z", out, "knob")
            # T head: saddle under the rail, short outward arm with a blue ball (width adjustment)
            d.box(f"sad{n}", [x - 28, RY - 44, z - 26, x + 28, RY - 14, z + 26], "rail", r=5)
            d.cyl(f"arm{n}", [x, RY - 32, z + out * 26], [x, RY - 32, z + out * 95], 16, "rail")
            d.sphere(f"ball{n}", [x, RY - 32, z + out * 105], 34, "cap")
    # white floor plates across both posts of each end, 4 bolts each
    for x in (XP, W - XP):
        d.box(f"plate{x}", [x - 125, 0, 0, x + 125, 10, DEP], "white", r=3)
        d.cyl(f"bolt{x}", [x - 90, 10, 50], [x - 90, 14, 50], 14, "metal#9a9ea4", copies=[[180, 0, 0], [0, 0, DEP - 100],
                                                                                        [180, 0, DEP - 100]])
        d.cyl(f"flange{x}", [x, 10, 260], [x, 18, 260], 90, "white", copies=[[0, 0, 640]])
    d.save()


def xyg1():
    d = D("xyg-1", [W, DEP, 1200], {"rail": "plastic#a3bce2", "white": "plastic#f0eee6", "vinyl": "rubber#b5bcc5",
                                    "edge": "plastic#ddcbc0", "knob": "plastic#1d1f22", "inner": "chrome",
                                    "wood": "plastic#d9b07a", "wood2": "plastic#e2bd88"})
    T = 50
    RY = 1000
    XP = 470
    # walkway platform: grey vinyl top, beige-pink edge band, bevelled ends
    d.slab("deck", "front", f"M 0 0 L {W} 0 L {W} 8 L {W - 200} {T} L 200 {T} L 0 8 Z", [0, DEP], "edge", r=3)
    d.slab("vinyl", "front", f"M 2 8 L 200 {T} L {W - 200} {T} L {W - 2} 8 L {W - 2} 10 L {W - 200} {T + 3} "
           f"L 200 {T + 3} L 2 10 Z", [3, DEP - 3], "vinyl", r=1)
    d.decal("label", [1150, T / 2, DEP + 0.6], [130, 16], "front", "gloss#2c55a3", soft=True)
    for z, out in ((200, -1), (960, 1)):
        d.cyl(f"rail{z}", [10, RY, z], [W - 10, RY, z], 45, "rail")
        d.cyl(f"cap{z}", [0, RY, z], [12, RY, z], 43, "plastic#cfd6de", copies=[[W - 12, 0, 0]])
        for x in (XP, W - XP):
            n = f"{z}-{x}"
            d.cyl(f"fl{n}", [x, T, z], [x, T + 8, z], 110, "white")
            d.cyl(f"post{n}", [x, T, z], [x, 700, z], 60, "white")
            d.cyl(f"col{n}", [x, 680, z], [x, 720, z], 68, "white")
            d.cyl(f"in{n}", [x, 700, z], [x, RY - 50, z], 45, "inner")
            star_knob(d, f"knob{n}", [x, 700, z + out * 34], "z", out, "knob")
            # chrome T-head bracket with an outward lever and black handle
            d.box(f"sad{n}", [x - 40, RY - 52, z - 30, x + 40, RY - 18, z + 30], "inner", r=5)
            d.box(f"tee{n}", [x - 70, RY - 60, z - 12, x + 70, RY - 48, z + 12], "inner", r=3)
            d.cyl(f"lev{n}", [x, RY - 40, z + out * 30], [x, RY - 46, z + out * 110], 14, "inner")
            d.cyl(f"levh{n}", [x, RY - 46, z + out * 110], [x, RY - 50, z + out * 170], 22, "knob")
    # correction board (photo): it fills the walkway between the rails' post lines. A flat lower board, and on it a
    # wedge rising toward the front rail; the lower board shows as a step in front of the wedge. The wedge's right
    # end is bevelled.
    Z0, Z1 = 250, 905
    XL, XR = 600, 3020
    d.box("board", [XL, T, Z0, XR, T + 30, Z1], "wood", r=4)
    WZ0, WZ1 = Z0 + 15, Z1 - 60
    d.slab("board2", "side", f"M {WZ0} {T + 30} L {WZ1} {T + 30} L {WZ1} {T + 100} L {WZ0} {T + 40} Z", [XL + 10, XR - 150],
           "wood2", r=4)
    # the bevel: 4 strips across the wedge, each as high as the wedge at its back edge (the wedge's height varies
    # along z, a slab only takes one outline)
    for i in range(4):
        za, zb = WZ0 + i * (WZ1 - WZ0) / 4, WZ0 + (i + 1) * (WZ1 - WZ0) / 4
        h = 40 + 60 * (za - WZ0) / (WZ1 - WZ0) - 30
        d.slab(f"board-end{i}", "front", f"M {XR - 150} {T + 30} L {XR - 150 + 2.2 * h} {T + 30} L {XR - 150} {T + 30 + h} Z",
               [za + (0.5 if i else 0), zb], "wood2", r=2)
    d.save()


xyg2()
xyg1()
