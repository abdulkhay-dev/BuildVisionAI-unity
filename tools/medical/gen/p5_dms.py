"""Deep muscle stimulators XY-DMS-103A (graphite hammer, blue head) and XY-DMS-102B (black percussion gun),
both standing on their grips. Writes only xy-dms-103a.json and xy-dms-102b.json."""
from p5lib import *

def octagon(z0, y0, z1, y1, c):
    return poly([(z0 + c, y0), (z1 - c, y0), (z1, y0 + c), (z1, y1 - c), (z1 - c, y1), (z0 + c, y1), (z0, y1 - c), (z0, y0 + c)])

# ---------------- XY-DMS-103A ----------------
# Review 2026-10-02, measured on the photo (grip 48 mm = 3.1 px/mm): box ~192 + 21 mm dark end plate, 63 mm tall,
# grip + neck ~289 mm, overall 250 x 372 (estimate 230 x 400; the author's 345 had a too-short grip and a too-tall box).
d = D("xy-dms-103a", [250, 80, 372], {"alu": "metal#6e727a", "dark": "metal#3a3d43", "blue": "metal#2f6fd8",
                                      "grip": "rubber#18191b", "cap": "metal#8a8e95", "white": "gloss#f2f2f2"})
X0, X1, Y0, Y1, ZC, YC, GX = 58, 250, 289, 352, 40, 320, 154
d.slab("box", "side", octagon(0, Y0, 80, Y1, 10), [X0 + 4, X1], "alu", r=2)
d.slab("end-l", "side", octagon(1, Y0 + 1, 79, Y1 - 1, 9.5), [X0 - 16, X0 + 6], "dark", r=2)
d.cyl("screw", [X0 - 16.5, Y0 + 10, 12], [X0 - 15, Y0 + 10, 12], 6, "plastic#1a1b1d",
      copies=[[0, 43, 0], [0, 0, 56], [0, 43, 56]])
d.slab("seam", "side", octagon(-0.6, Y0 - 0.6, 80.6, Y1 + 0.6, 10.3), [X1 - 37, X1 - 35.5], "dark", r=0.4, soft=True)
d.cyl("cap", [GX, Y1 - 2, ZC], [GX, Y1 + 10, ZC], 74, "dark")
d.cyl("cap-top", [GX, Y1 + 10, ZC], [GX, Y1 + 11, ZC], 62, "metal#2c2e33", soft=True)
# blue anodised head: dark collar, neck, cap
d.cyl("collar", [X0 - 22, YC, ZC], [X0 - 15, YC, ZC], 32, "dark")
d.cyl("neck", [22, YC, ZC], [X0 - 21, YC, ZC], 24, "blue")
d.lathe("head", [0, YC, ZC], [[0, 0], [18, 0], [19, 3], [19, 21], [18, 23], [0, 23]], "blue", axis="x")
# front: logo disc + text, a slightly darker strip with the ECG line
d.cyl("logo", [112, Y1 - 18, 80], [112, Y1 - 18, 80.8], 12, "white", soft=True)
d.decal("logo-t", [134, Y1 - 17, 80.9], [26, 4.5], "front", "white", soft=True)
d.decal("ecg", [176, Y1 - 31, 80.9], [62, 1.3], "front", "plastic#d6d8dc", soft=True)
yb = Y1 - 31
d.tube("ecg-peak", [[118, yb, 81], [124, yb, 81], [127, yb + 6, 81], [130, yb - 8, 81], [133, yb + 9, 81],
                    [136, yb - 3, 81], [139, yb, 81], [142, yb + 4, 81], [145, yb, 81], [128, yb, 81]][:9], 1.3,
       "plastic#d6d8dc", soft=True)
d.decal("ecg-end", [206, Y1 - 31, 80.9], [10, 2.4], "front", "plastic#d6d8dc", soft=True)
# back: black touch panel with the LED window and -/o/+ keys
d.add("touch", "screen", "plastic#121315", box=[160, Y0 + 6, -1.5, 210, Y1 - 6, 3], r=3, face="back", bezel=1,
      print="med_xy-dms-103a_screen")
d.cyl("pin", [76, Y0 - 6, 52], [76, Y0 + 2, 52], 5, "metal#c7a24a")
# handle: flared grey neck with a ring, black rubber grip with grooves, grey metal end cap
d.lathe("neck-h", [GX, 244, ZC], [[0, 0], [24, 0], [25, 18], [26, 22], [28, 26], [30, 40], [31, 46], [0, 46]], "dark")
d.lathe("neck-ring", [GX, 262, ZC], [[0, 0], [27, 0], [27, 5], [0, 5]], "metal#8f949b")
d.loft("grip", [sec(14, 46, 42, 17, GX, ZC), sec(120, 48, 44, 19, GX, ZC), sec(246, 46, 42, 18, GX, ZC)], "grip")
d.loft("groove", [sec(170, 48.6, 44.6, 19, GX, ZC), sec(172, 48.6, 44.6, 19, GX, ZC)], "plastic#2a2b2e", copies=[[0, -130, 0]])
d.loft("end-cap", [sec(0, 52, 46, 20, GX, ZC), sec(9, 50, 45, 19, GX, ZC), sec(16, 46, 42, 17, GX, ZC)], "cap")
d.save()

# ---------------- XY-DMS-102B ----------------
# Review 2026-10-02: the in-use photo shows the round logo cap and the display on the SAME face, the face opposite the
# grip, so standing on the grip they are on the TOP: the cap is the top end of the grip axis (Ø80 head at the left end
# of the box, cap raised ~10 mm), the display on the box top, the shaft socket out of the head's left side.
AX = 74                              # grip axis; proportions from the product photo (grip 48 = 2.1 px/mm) and the
BY0, BY1, TOP = 190, 247, 266       # in-use photo (cap Ø ~52, box face 75 wide, ~107 from the axis to the end)
d = D("xy-dms-102b", [184, 80, TOP], {"black": "plastic#1b1c1e", "panel": "gloss#2e3034", "grip": "rubber#151617",
                                      "white": "gloss#f4f4f4", "ring": "plastic#3a3c40"})
ZC = 40
d.cyl("head", [AX, BY0, ZC], [AX, BY1 + 4, ZC], 60, "black", sides=40)
d.box("box", [AX, BY0, 2.5, AX + 110, BY1, 77.5], "black", r=10)
d.cyl("cap", [AX, BY1 + 3, ZC], [AX, TOP - 1, ZC], 54, "black", sides=40)
d.cyl("cap-rim", [AX, TOP - 1.5, ZC], [AX, TOP - 0.8, ZC], 54, "ring", sides=40, soft=True)
d.cyl("logo-w", [AX, TOP - 1, ZC], [AX, TOP - 0.2, ZC], 40, "white", soft=True, sides=40)
d.box("cross-h", [AX - 14, TOP - 0.4, ZC - 4.5, AX + 14, TOP, ZC + 4.5], "black", soft=True)
d.box("cross-v", [AX - 4.5, TOP - 0.4, ZC - 14, AX + 4.5, TOP, ZC + 14], "black", soft=True)
d.cyl("socket", [0, 218, ZC], [AX - 26, 218, ZC], 34, "black")
d.cyl("socket-ring", [0, 218, ZC], [7, 218, ZC], 30, "ring")
d.cyl("socket-hole", [-0.5, 218, ZC], [1, 218, ZC], 14, "plastic#0a0a0b", soft=True)
# top: display panel with the LED window and -/o/+ keys
d.box("panel", [AX + 38, BY1 - 1, 12, AX + 98, BY1 + 2.2, 68], "panel", r=3)
d.decal("lcd", [AX + 52, BY1 + 2.4, ZC], [10, 30], "top", "plastic#6c7076", soft=True)
d.decal("k-minus", [AX + 80, BY1 + 2.4, ZC - 17], [2, 6], "top", "white", soft=True)
d.cyl("k-o", [AX + 80, BY1 + 2.2, ZC], [AX + 80, BY1 + 2.8, ZC], 6, "white", soft=True)
d.cyl("k-o-in", [AX + 80, BY1 + 2.8, ZC], [AX + 80, BY1 + 3.0, ZC], 3.6, "panel", soft=True)
d.decal("k-plus", [AX + 80, BY1 + 2.4, ZC + 17], [6, 2], "top", "white", soft=True)
d.decal("k-plus2", [AX + 80, BY1 + 2.4, ZC + 17], [2, 6], "top", "white", soft=True)
d.cyl("hole", [AX + 109, 214, ZC], [AX + 111, 214, ZC], 6, "plastic#050506", soft=True)
# grip under the head: slight flare at the foot, a shoulder ring under the box
d.lathe("grip", [AX, 0, ZC], [[0, 0], [26, 0], [25, 8], [24, 22], [24, 150], [25, 172], [0, 172]], "grip")
d.lathe("shoulder", [AX, 166, ZC], [[0, 0], [26, 0], [29, 6], [30, 24], [0, 24]], "black")
d.save()
