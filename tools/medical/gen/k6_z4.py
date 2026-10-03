"""XYF-Z4 walker with a separate wheeled saddle unit (photo: the two pieces side by side; drawn that way).
Walker x 0-680: four legs with S-bent flared feet, side rails, X brace across the front (z = depth), open back,
horseshoe forearm rest closed at the front. Saddle unit to its right (+x): L-shaped padded saddle + back pad."""
from k6lib import *

W, DEP, H = 1180, 800, 1300
d = D("xyf-z4", [W, DEP, H], {"tube": "metal#58719e", "pad": "leather#8aa0d0", "spad": "leather#5868a8", "black": "plastic#1d1f22",
                              "chrome": "chrome", "cap": "plastic#e9ece9", "rubber": "rubber#3a3d42"})
WW = 680
D0, D1 = 140, 660           # leg z (straight part)
FLARE = 75
YT = 1170                   # top side rails
PT = H                      # pad top


def leg(id, x, z, out, ytop, ybend=360):
    d.tube(id, [[x, ytop, z], [x, ybend, z], [x, ybend - 160, z + out * FLARE], [x, 100, z + out * FLARE]], 25, "tube",
           bend=70)


for x in (45, WW - 45):
    s = "l" if x < 300 else "r"
    leg(f"leg-b{s}", x, D0, -1, YT)
    leg(f"leg-f{s}", x, D1, 1, YT)
    # top side rail (photo): a flat grey steel channel standing on edge, reaching past both legs
    d.bar(f"side-top{s}", [x, YT, D0 - 70], [x, YT, D1 + 70], [24, 46], "metal#9aa3ad", r=3)
    star_knob(d, f"top-knob-b{s}", [x + (-14 if s == "l" else 14), YT - 30, D0], "x", -1 if s == "l" else 1, "black")
    star_knob(d, f"top-knob-f{s}", [x + (-14 if s == "l" else 14), YT - 30, D1], "x", -1 if s == "l" else 1, "black")
    d.cyl(f"side-mid{s}", [x, 430, D0 - 110], [x, 430, D1 + 110], 25, "tube")
    d.cyl(f"side-mid-cap{s}", [x, 430, D0 - 125], [x, 430, D0 - 108], 27, "cap")
    d.cyl(f"side-low{s}", [x, 160, D0 - FLARE], [x, 160, D1 + FLARE], 22, "tube")
    for z in (D0 - FLARE, D1 + FLARE):
        caster(d, f"cas{s}{z}", [x, 0, z], 75, "rubber")
    # thin chrome telescopic rods beside the legs
    for z in (D0 + 30, D1 - 30):
        xo = x + (14 if s == "l" else -14)
        d.tube(f"rod{s}{z}", [[xo, 450, z], [xo, YT - 50, z], [x, YT - 30, z]], 8, "chrome", bend=15)
# X brace across the front between the feet
d.cyl("x1", [45, 170, D1 + 40], [WW - 45, 430, D1 + 40], 22, "tube")
d.cyl("x2", [45, 430, D1 + 40], [WW - 45, 170, D1 + 40], 22, "tube")
# horseshoe forearm rest closed at the front, open toward the user at the back
AW = 125
Z0, Z1 = 90, 730
out = (f"M 0 {Z0 + 30} Q 0 {Z0} 30 {Z0} L {AW - 20} {Z0} Q {AW} {Z0} {AW} {Z0 + 30} L {AW} {Z1 - 230} "
       f"Q {AW} {Z1 - AW} {AW + 110} {Z1 - AW} L {WW - AW - 110} {Z1 - AW} Q {WW - AW} {Z1 - AW} {WW - AW} {Z1 - 230} "
       f"L {WW - AW} {Z0 + 30} Q {WW - AW} {Z0} {WW - AW + 20} {Z0} L {WW - 30} {Z0} Q {WW} {Z0} {WW} {Z0 + 30} "
       f"L {WW} {Z1 - 120} Q {WW} {Z1} {WW - 120} {Z1} L 120 {Z1} Q 0 {Z1} 0 {Z1 - 120} Z")
d.slab("rest", "top", out, [PT - 72, PT], "pad", r=22)
d.slab("rest-base", "top", out, [PT - 82, PT - 70], "metal#55647a", r=2)
for x in (45, WW - 45):
    d.cyl(f"rest-post{x}", [x, YT, D0], [x, PT - 80, D0], 22, "chrome", copies=[[0, 0, D1 - D0]])
d.box("brake", [WW - 140, PT - 120, D1 + 30, WW - 60, PT - 85, D1 + 80], "metal#b7bcc2", r=6)
# --- saddle unit
SX0, SX1 = 820, 1160
SZ0, SZ1 = 200, 600
YS = 860                    # saddle top
for x in (SX0 + 20, SX1 - 20):
    s = "l" if x < 1000 else "r"
    d.tube(f"s-leg-b{s}", [[x, 470, SZ0], [x, 330, SZ0], [x, 200, SZ0 - 60], [x, 100, SZ0 - 60]], 22, "tube", bend=60)
    d.tube(f"s-leg-f{s}", [[x, 470, SZ1], [x, 330, SZ1], [x, 200, SZ1 + 60], [x, 100, SZ1 + 60]], 22, "tube", bend=60)
    d.cyl(f"s-low{s}", [x, 150, SZ0 - 60], [x, 150, SZ1 + 60], 20, "tube")
    for z in (SZ0 - 60, SZ1 + 60):
        caster(d, f"s-cas{s}{z}", [x, 0, z], 70, "rubber")
    for z in (SZ0 + 40, SZ1 - 40):
        d.cyl(f"s-post{s}{z}", [x, 450, z], [x, YS - 110, z], 25, "tube")
        d.cyl(f"s-rod{s}{z}", [x + (14 if s == "l" else -14), 380, z], [x + (14 if s == "l" else -14), YS - 120, z], 9,
              "chrome")
        star_knob(d, f"s-knob{s}{z}", [x, YS - 120, z + 16], "z", 1, "black", dd=34)
# loop rail at mid height with hooks at the front (they hang the unit on the walker)
d.tube("s-loop", [[SX0 + 20, 470, SZ1 + 20], [SX0 + 20, 470, SZ0 - 40], [SX1 - 20, 470, SZ0 - 40],
                  [SX1 - 20, 470, SZ1 + 20]], 22, "tube", bend=60)
d.cyl("s-cross", [SX0 + 20, 470, SZ1 + 20], [SX1 - 20, 470, SZ1 + 20], 22, "tube")
d.tube("hook", [[SX0 + 60, 470, SZ1 + 20], [SX0 + 60, 470, SZ1 + 90], [SX0 + 60, 510, SZ1 + 100]], 14, "cap", bend=20,
       copies=[[SX1 - SX0 - 120, 0, 0]])
d.box("s-seatplate", [SX0 + 10, YS - 140, SZ0, SX1 - 10, YS - 125, SZ1], "black", r=3)
# L-shaped padded saddle: seat part toward the front, back pad rising at the back (the walker's open side)
L = (f"M {SZ0 - 40} {YS - 130} L {SZ1 + 40} {YS - 130} Q {SZ1 + 60} {YS - 130} {SZ1 + 60} {YS - 110} L {SZ1 + 60} {YS - 15} "
     f"Q {SZ1 + 60} {YS} {SZ1 + 40} {YS} L {SZ0 + 110} {YS} Q {SZ0 + 70} {YS} {SZ0 + 70} {YS + 40} L {SZ0 + 70} {H - 140} "
     f"Q {SZ0 + 70} {H - 120} {SZ0 + 50} {H - 120} L {SZ0 - 20} {H - 120} Q {SZ0 - 40} {H - 120} {SZ0 - 40} {H - 140} Z")
d.slab("saddle", "side", L, [SX0 + 35, SX1 - 35], "spad", r=24)
d.box("s-backplate", [SX0 + 120, YS, SZ0 - 52, SX1 - 120, H - 125, SZ0 - 40], "metal#9aa3ad", r=4)
d.save()
