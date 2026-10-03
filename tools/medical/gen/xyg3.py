from pfx_lib import *
d = D("xyg-3", [3500, 900, 1300], {
  "deck": "plastic#cfcee6", "trim": "metal#d2d4da", "post": "plastic#eeeef5", "rail": "metal#c6c7da",
  "foot": "plastic#bdbcd8", "grey": "metal#a7a9b4", "dark": "plastic#2a2c30", "box": "metal#cdcedc",
  "logo": "gloss#2f5fc0", "cord": "plastic#8e9098"})
T = 55    # platform top
RY = 1000  # rail centre (middle of the 850-1300 electric range)
# --- platform: two halves, bevelled ramp ends (right ramp longer), aluminium edge trim with rivets
# the platform is shorter than the rails: measured on the photo (rail vanishing point) the rails overhang its left
# end by ~650 (the leaning posts' tops are beyond it) and its right ramp end by ~80; the seam is in its middle
P0, P1 = 650, 3420
PM = (P0 + P1) / 2
d.slab("deck-l", "front", f"M {P0} 0 L {PM - 1} 0 L {PM - 1} {T} L {P0 + 95} {T} Q {P0 + 80} {T} {P0 + 70} {T - 6} L {P0} 5 Z", [0, 900], "deck", r=3)
d.slab("deck-r", "front", f"M {PM + 1} 0 L {P1} 0 L {P1} 5 L {P1 - 190} {T - 8} Q {P1 - 200} {T} {P1 - 220} {T} L {PM + 1} {T} Z",
       [0, 900], "deck", r=3)
d.box("seam", [PM - 2, T - 1, 4, PM + 2, T + 0.6, 896], "plastic#a9a8c4", soft=True)
d.box("trim", [P0 + 70, 0, 896, P1 - 200, T + 2, 903], "trim", r=2, copies=[[0, 0, -899]])
d.decal("rivet", [P0 + 110, T - 12, 903.5], [7, 7], "front", "metal#7d8089", soft=True, repeat=rep(26, [100, 0, 0]))
d.decal("rivet-b", [P0 + 110, T - 12, -3.5], [7, 7], "back", "metal#7d8089", soft=True, repeat=rep(26, [100, 0, 0]))
XL0, XL1 = 985, 570       # left posts: bottom x, top x (lean ~25 deg toward the left end, measured on the photo)
XR = 2930                 # right columns
for side, z in (("n", 750), ("b", 150)):
    # rail with black end caps
    d.cyl(f"rail-{side}", [20, RY, z], [3460, RY, z], 48, "rail")
    d.cyl(f"rail-cap-{side}", [3460, RY, z], [3480, RY, z], 46, "dark", copies=[[-3460, 0, 0]])
    # left leaning post on a trapezoid foot plate
    d.bar(f"post-l-{side}", [XL0, T + 20, z], [XL1, RY - 45, z], [80, 60], "post", r=5)
    d.slab(f"foot-l-{side}", "front", f"M {XL0 - 110} {T} L {XL0 + 90} {T} L {XL0 + 60} {T + 28} L {XL0 - 80} {T + 28} Z",
           [z - 65, z + 65], "foot", r=3)
    # right upright lifting column on a grey base bracket
    d.box(f"col-r-{side}", [XR - 42, T + 30, z - 34, XR + 42, RY - 55, z + 34], "post", r=6)
    d.box(f"base-r-{side}", [XR - 85, T, z - 70, XR + 85, T + 32, z + 70], "grey", r=6)
    # grey forked saddle clamps around the rail, small lever
    for nm, x in (("l", XL1), ("r", XR)):
        d.box(f"clamp-{nm}-{side}", [x - 40, RY - 62, z - 36, x + 40, RY - 24, z + 36], "grey", r=8)
        d.box(f"fork-{nm}-{side}", [x - 32, RY - 30, z - 33, x + 32, RY + 18, z - 26], "grey", r=4, copies=[[0, 0, 59]])
        d.cyl(f"lever-{nm}-{side}", [x + 40, RY - 45, z], [x + 85, RY - 70, z], 12, "grey")
# long clamp lever sticking out to the left from the near-left saddle, black grip at its end
d.cyl("end-lever", [XL1 - 40, RY - 40, 760], [XL1 - 300, RY - 70, 775], 18, "grey")
d.cyl("end-lever-grip", [XL1 - 300, RY - 70, 775], [XL1 - 400, RY - 82, 780], 28, "dark")
# --- control box at the foot of the near right column, blue logo, black socket
d.box("ctl-box", [2430, T, 770, 2830, T + 150, 892], "box", r=10)
d.decal("logo-icon", [2480, T + 112, 892.5], [26, 26], "front", "logo", soft=True)
d.decal("logo-text", [2550, T + 112, 892.5], [90, 16], "front", "logo", soft=True)
d.decal("logo-sub", [2550, T + 92, 892.5], [90, 5], "front", "plastic#7d8ab0", soft=True)
d.cyl("socket", [2770, T + 55, 891], [2770, T + 55, 897], 26, "dark")
# --- hand pendant in a holder on the near right column, coiled grey cable down to the box
d.box("pendant-holder", [XR - 60, 820, 730, XR - 42, 950, 770], "dark", r=4)
d.box("pendant", [XR - 115, 720, 728, XR - 60, 960, 778], "dark", r=14)
d.cyl("pendant-grip", [XR - 88, 960, 753], [XR - 88, 1010, 753], 40, "plastic#5a5d64")
d.decal("pendant-keys", [XR - 88, 860, 778.5], [30, 70], "front", "plastic#4f535b", soft=True)
d.coil("pendant-cord", [XR - 88, 715, 760], [XR - 80, 330, 790], 34, 8, 26, "cord", soft=True)
d.tube("pendant-cable", [[XR - 80, 330, 790], [XR - 90, 200, 830], [XR - 120, T + 75, 860], [2830, T + 75, 850]],
       10, "cord", bend=60, soft=True)
d.box("plug", [2830, T + 60, 835, 2860, T + 90, 865], "plastic#f2f2f2", r=4)
d.save()
