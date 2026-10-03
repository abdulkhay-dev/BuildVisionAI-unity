"""XY-K-SRD-I hand electrical stimulator: white rounded tray with a grey pad, display bar across the far end, five
finger cradles with black rollers, a grey fabric strap arch over the palm. Front (z = depth) = the wrist end."""
from p3lib import *

W, L = 300, 420
d = D("xy-k-srd-i", [W, L, 160], {
    "shell": "gloss#f4f5f7", "seam": "plastic#c9ccd1", "pad": "plastic#8a8f96", "cradle": "plastic#d9dbde",
    "roller": "rubber#26282b", "arrow": "gloss#3cc3d8", "black": "gloss#121315", "disp": "plastic#3a3f46",
    "logo": "gloss#2f8fd8", "strap": "fabric#7d8288", "patch": "plastic#b9bdc2", "hole": "plastic#3b3f45", "tab": "plastic#8f949a",
    "btn": "plastic#8d9298"})
outer = [(0, 0), (W, 0), (W, L), (0, L)]
RAD = [40, 40, 150, 150]
inner = [(18, 96), (W - 18, 96), (W - 18, L - 18), (18, L - 18)]
IRAD = [24, 24, 132, 132]
d.slab("tray", "top", rpoly(outer, RAD), [0, 50], "shell", r=12)
d.slab("seam", "top", rpoly([(p[0] + (-0.8 if p[0] == 0 else 0.8), p[1] + (-0.8 if p[1] == 0 else 0.8)) for p in outer], RAD), [16, 18], "seam", r=0.5)
d.slab("rim", "top", rpoly(outer, RAD) + " " + rpoly(inner, IRAD), [48, 62], "shell", r=5)
d.slab("pad", "top", rpoly(inner, IRAD), [48, 55], "pad", r=3)
# display bar across the far end: white rounded bar, black glossy top, dark window with the blue logo
# (photo: a stadium-shaped bar, its black glossy top a stadium too, nearly as big as the bar top; a large grey window)
d.slab("bar", "top", rpoly([(12, 10), (W - 12, 10), (W - 12, 88), (12, 88)], 39), [40, 92], "shell", r=10)
d.slab("bar-top", "top", rpoly([(20, 17), (W - 20, 17), (W - 20, 81), (20, 81)], 32), [90, 94], "black", r=1.5)
d.box("disp", [86, 93.5, 28, 214, 95, 70], "disp", r=3, soft=True)
d.box("disp-logo", [134, 94.6, 44, 166, 95.5, 54], "logo", soft=True)
d.box("power", [60, 60, 8, 84, 70, 12], "btn", r=4)
d.cyl("jack", [120, 65, 8], [120, 65, 12], 12, "hole")
# five finger cradles: pale grey capsules on the pad with a black roller along the inner side, cyan arrows on top
CR = [("thumb", 46, 205, -18), ("index", 106, 175, -6), ("middle", 158, 162, 0), ("ring", 208, 170, 6), ("little", 252, 225, 14)]
# (photo: flat-topped light grey capsules; a big black rubber roller runs along the lower part of one side; the thumb
# cradle is shorter, stands taller and has rollers on both sides)
for nm, cx, cz, ang in CR:
    r = rot("y", ang, [cx, 55, cz])
    th = nm == "thumb"
    hl, top = (36, 112) if th else (52, 96)
    d.box(f"{nm}", [cx - 23, 66, cz - hl, cx + 23, top, cz + hl], "cradle", r=14, rot=r)
    d.box(f"{nm}-base", [cx - 18, 55, cz - hl + 6, cx + 18, 70, cz + hl - 6], "cradle", r=8, rot=r)
    d.add(f"{nm}-roller", "sphere", "roller", at=[cx + 15, 76, cz], radii=[13, 15, hl - 6], rot=r)
    if th:
        d.add(f"{nm}-roller2", "sphere", "roller", at=[cx - 15, 76, cz], radii=[13, 15, hl - 6], rot=r)
    d.slab(f"{nm}-arrow", "top", poly([(cx - 4, cz - hl + 12), (cx + 4, cz - hl + 12), (cx, cz - hl + 6)]), [top - 0.5, top + 0.8], "arrow",
           soft=True, rot=r)
    d.slab(f"{nm}-arrow2", "top", poly([(cx - 4, cz + hl - 12), (cx + 4, cz + hl - 12), (cx, cz + hl - 6)]), [top - 0.5, top + 0.8], "arrow",
           soft=True, rot=r)
# strap arch over the palm and its logo patch
# a round arch (photo), ~120 above the pad, the logo patch on its upper side
import math as _m
arc = [[135 + 88 * _m.cos(_m.radians(a)), 58 + 0.0 + 100 * _m.sin(_m.radians(a)), 335] for a in range(180, -1, -15)]
d.add("strap", "strap", "strap", path=arc, section=[82, 5], bend=10, roll=90)
patch = [[135 + 91 * _m.cos(_m.radians(a)), 58 + 103 * _m.sin(_m.radians(a)), 335] for a in range(128, 92, -6)]
d.add("strap-patch", "strap", "patch", path=patch, section=[46, 1.5], bend=10, roll=0, soft=True)
d.box("strap-foot", [34, 55, 292, 64, 62, 378], "strap", r=4, copies=[[172, 0, 0]])
# near side: small grey upright tab and a dark oval recess
d.slab("recess", "top", rpoly(ellipse_pts(250, 300, 38, 22, 24), 0), [54.5, 56], "hole")
d.box("tab", [214, 55, 286, 232, 100, 300], "tab", r=6)
d.save()
