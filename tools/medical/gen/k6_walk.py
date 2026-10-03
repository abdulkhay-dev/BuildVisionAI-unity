"""XYF-Z1 forearm-support walker, XYF-Z2 the same with brakes and a seat.
Frame: U base of cream rectangular tube, closed end at the front (z = depth), open toward the user at the back
(z = 0); two telescopic posts on the arms at mid-depth carry a cross tube and the padded forearm rest; black foam
grips stand on the rest's front edge."""
from k6lib import *


def walker(id, W, DEP, H, seat):
    d = D(id, [W, DEP, H], {"tube": "plastic#ece7d8", "inner": "metal#d9d6cc", "pad": "leather#8e9fdc" if not seat else "leather#5d7ec8",
                            "foam": "rubber#1f2023", "black": "plastic#1d1f22", "knob": "plastic#2a9fc0" if not seat else "plastic#1d1f22",
                            "chrome": "chrome", "cable": "plastic#18191b"})
    XA = 45                      # arm centre from the side
    YB = 150                     # base tube centre height
    ZP = DEP - 470               # posts
    PT = H - (125 if seat else 160)   # pad top (Z1 grips stand ~160 above the pad on the photo)
    # --- U base (rectangular tube 30 x 38), caps on the open ends
    d.sweep("base", [[XA, YB, 35], [XA, YB, DEP - 45], [W - XA, YB, DEP - 45], [W - XA, YB, 35]], [30, 38], "tube",
            shape="rect", r=5, bend=70)
    d.box("cap", [XA - 15, YB - 19, 30, XA + 15, YB + 19, 36], "black", r=3, mirror="x")
    for z in (60, DEP - 70):
        caster(d, f"cas{z}", [XA, 0, z], 100, "rubber#4a4d52", mirror="x")
        d.box(f"plate{z}", [XA - 30, YB - 25, z - 30, XA + 30, YB - 19, z + 30], "chrome", r=3, mirror="x")
    # --- telescopic posts: cream outer tube, lighter inner tube, knob at the joint, clamp at the base
    YJ = YB + (0.72 if seat else 0.84) * (PT - YB)   # joint/knob height as on the photos
    d.cyl("post", [XA, YB + 19, ZP], [XA, YJ, ZP], 34, "tube", mirror="x")
    d.cyl("post-col", [XA, YJ - 10, ZP], [XA, YJ + 18, ZP], 40, "tube", mirror="x")
    d.cyl("post-in", [XA, YJ, ZP], [XA, PT - 70, ZP], 27, "inner", mirror="x")
    d.box("post-foot", [XA - 22, YB + 15, ZP - 22, XA + 22, YB + 45, ZP + 22], "tube", r=4, mirror="x")
    star_knob(d, "post-knob", [W - XA + 17, YJ + 4, ZP], "x", 1, "knob", dd=44)
    star_knob(d, "post-knob-l", [XA - 17, YJ + 4, ZP], "x", -1, "knob", dd=44)
    # cross tube under the rest, black clamp blocks at its ends and under the grips
    d.box("cross", [XA - 25, PT - 95, ZP - 15, W - XA + 25, PT - 65, ZP + 15], "tube", r=4)
    d.box("clamp", [XA - 35, PT - 105, ZP - 22, XA + 15, PT - 60, ZP + 22], "black", r=5, mirror="x")
    # --- forearm rest: blue PU on a grey board, notch toward the user (back), grips on the front edge
    PZ0, PZ1 = ZP - 175, ZP + 175
    if not seat:
        # big rounded ends; a rounded rectangular notch ~300 wide, 55 deep at the back middle
        out = (f"M 15 {PZ0 + 110} Q 15 {PZ0} 125 {PZ0} L {W / 2 - 175} {PZ0} Q {W / 2 - 150} {PZ0} {W / 2 - 150} {PZ0 + 25} "
               f"Q {W / 2 - 150} {PZ0 + 55} {W / 2 - 115} {PZ0 + 55} L {W / 2 + 115} {PZ0 + 55} "
               f"Q {W / 2 + 150} {PZ0 + 55} {W / 2 + 150} {PZ0 + 25} Q {W / 2 + 150} {PZ0} {W / 2 + 175} {PZ0} "
               f"L {W - 125} {PZ0} Q {W - 15} {PZ0} {W - 15} {PZ0 + 110} "
               f"L {W - 15} {PZ1 - 110} Q {W - 15} {PZ1} {W - 125} {PZ1} L 125 {PZ1} Q 15 {PZ1} 15 {PZ1 - 110} Z")
    else:  # rounded lobes at the ends, deep notch
        out = (f"M 10 {PZ0 + 90} Q 10 {PZ0 - 10} 120 {PZ0} L {W / 2 - 150} {PZ0} Q {W / 2 - 120} {PZ0 + 110} {W / 2} {PZ0 + 115} "
               f"Q {W / 2 + 120} {PZ0 + 110} {W / 2 + 150} {PZ0} L {W - 120} {PZ0} Q {W - 10} {PZ0 - 10} {W - 10} {PZ0 + 90} "
               f"L {W - 10} {PZ1 - 70} Q {W - 10} {PZ1} {W - 90} {PZ1} L 90 {PZ1} Q 10 {PZ1} 10 {PZ1 - 70} Z")
    d.slab("rest-board", "top", out, [PT - 62, PT - 50], "plastic#9aa3ad", r=2)
    d.slab("rest", "top", out, [PT - 50, PT], "pad", r=20)
    GX = 215
    GZ = PZ1 - 55
    for s, x in (("l", W / 2 - GX), ("r", W / 2 + GX)):
        d.cyl(f"grip-stem-{s}", [x, PT - 70, GZ], [x, PT + 12, GZ], 22, "chrome")
        d.cyl(f"grip-{s}", [x, PT + 8, GZ], [x, H, GZ], 36, "foam")
        d.cyl(f"grip-ring-{s}", [x, PT, GZ], [x, PT + 10, GZ], 40, "chrome")
        d.box(f"grip-clamp-{s}", [x - 26, PT - 98, GZ - 26, x + 26, PT - 62, GZ + 26], "black", r=5)
        star_knob(d, f"grip-knob-{s}", [x, PT - 98, GZ], "y", -1, "black", dd=30, l=24)
        if seat:
            # bicycle brake lever in front of the grip, black cable looping down to the rear castor
            o = -1 if s == "l" else 1
            # (photo) the lever pivots in a black housing at the grip's foot and its blade rises in front of the
            # grip, curving away from it, to ~2/3 of the grip height
            d.box(f"brake-body-{s}", [x - 17, PT + 4, GZ + 14, x + 17, PT + 34, GZ + 40], "black", r=6)
            d.sweep(f"brake-{s}", [[x + o * 4, PT + 26, GZ + 34], [x + o * 8, PT + 50, GZ + 58], [x + o * 14, PT + 92, GZ + 62],
                                   [x + o * 28, PT + 112, GZ + 48]], [9, 20], "black", shape="oval", bend=25, soft=True)
            # cable: from under the housing it bows out beside the frame and comes back to the base arm at the post
            # foot (then on along the arm to the rear castor's brake)
            xc = XA if s == "l" else W - XA
            d.tube(f"cable-{s}", [[x + o * 10, PT - 20, GZ + 30], [x + o * 70, PT - 250, GZ + 110],
                                  [xc + o * 110, 560, ZP + 120], [xc + o * 60, 260, ZP + 40], [xc + o * 18, YB + 14, ZP - 40],
                                  [xc + o * 18, YB + 14, 70]], 8, "cable", bend=200, soft=True)
    if seat:
        # seat sub-frame: side bars on legs from the base arms, chrome width rods with black knobs
        YS = 540
        for z in (130, 540):
            d.cyl(f"seat-leg{z}", [XA + 50, YB + 19, z], [XA + 50, YS, z], 28, "tube", mirror="x")
            d.cyl(f"seat-leg-in{z}", [XA + 50, YB + 19, z], [XA + 30, YB, z], 22, "tube", mirror="x")
        d.box("seat-side", [XA + 35, YS - 15, 110, XA + 65, YS + 15, 560], "tube", r=4, mirror="x")
        for z in (200, 470):
            d.cyl(f"seat-rod{z}", [XA - 10, YS + 25, z], [W - XA + 10, YS + 25, z], 16, "chrome")
            star_knob(d, f"seat-rod-knob{z}", [XA + 35, YS + 5, z], "x", -1, "black", dd=36)
            star_knob(d, f"seat-rod-knob{z}r", [W - XA - 35, YS + 5, z], "x", 1, "black", dd=36)
        d.box("seat-pan", [W / 2 - 210, YS + 32, 150, W / 2 + 210, YS + 45, 520], "plastic#9aa3ad", r=4)
        d.box("seat", [W / 2 - 215, YS + 42, 145, W / 2 + 215, YS + 92, 525], "pad", r=22, puff=6)
        # backrest on a grey plate bracket at the back of the seat
        d.box("back-plate", [W / 2 - 70, YS + 40, 130, W / 2 + 70, YS + 330, 142], "plastic#9aa3ad", r=4)
        d.box("back", [W / 2 - 190, YS + 200, 85, W / 2 + 190, YS + 500, 135], "pad", r=24, puff=5,
              rot=rot("x", -6, [W / 2, YS + 180, 110]))
    d.save()


walker("xyf-z1", 840, 1050, 1450, False)
walker("xyf-z2", 860, 1050, 1550, True)
