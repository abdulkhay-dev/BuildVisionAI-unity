"""kinesio-5: xy-51 (upper-limb hanging frame: two telescopic columns on a U base, spring scales, spreaders,
khaki arm slings) and xy-kgj-1 (hip rotation platform with a tilted red/blue disc and a chrome U handrail)."""
from k5lib import *

# ---------------- xy-51 ----------------
# Base 800 x 800 at x 0..800; both hanging pairs point to +x (as photographed), so the right pair overhangs the
# base: size W covers the whole model (the size is the placement footprint), the base stays at x 0..800.
BW, DD, H = 800, 800, 2050
ARM, SPR = 235, 450          # scale offset from the column, spreader length (photo: 4.2 mm/px at the columns)
SW = 140                     # sling width
W = int(BW - 80 + SPR + SW / 2 + 15)
d = D("xy-51", [W, DD, H], {"frame": "plastic#efede6", "inner": "black#2b2b2e", "cap": "rubber#141416",
                             "chrome": "chrome", "sling": "fabric#8f7b3a", "slingIn": "fabric#6a5a28",
                             "knob": "plastic#151517", "bar": "metal#ddd8c4"})
# U base: back cross tube along x, two feet along z with black front caps
d.bar("base-back", [0, 22, 55], [BW, 22, 55], [44, 44], "frame", r=4)
for x in (25, BW - 25):
    d.bar(f"foot{x}", [x, 22, 10], [x, 22, DD - 14], [48, 44], "frame", r=4)
    d.box(f"foot-cap{x}", [x - 24, 0, DD - 16, x + 24, 44, DD], "cap", r=3)
CZ = 60
HZ = CZ + 42                 # the hanging hardware hangs just in front of the column (the near sling covers it)
for s, x, yk in (("l", 80, 1150), ("r", BW - 80, 880)):
    # outer white tube up to the clamp collar (photo: the right collar ~880, the left one hidden behind the sling)
    d.box(f"col-shoe-{s}", [x - 30, 40, CZ - 30, x + 30, 70, CZ + 30], "frame", r=4)
    d.cyl(f"col-{s}", [x, 40, CZ], [x, yk + 20, CZ], 40, "frame")
    d.cyl(f"col-collar-{s}", [x, yk - 10, CZ], [x, yk + 30, CZ], 46, "frame")
    knob(d, f"col-knob-{s}", [x, yk, CZ + 22], axis="z", dd=30)
    # dark inner tube with a tight J bend at the top, then a light arm carrying the spring scale
    TX = x + ARM
    d.tube(f"inner-{s}", [[x, yk + 10, CZ], [x, 1985, CZ], [x + 8, 2030, CZ + 10], [x + 70, 2036, HZ]], 28,
           "inner", bend=45)
    d.cyl(f"arm-{s}", [x + 66, 2036, HZ], [TX + 22, 2036, HZ], 24, "frame")
    d.lathe(f"arm-cap-{s}", [TX + 22, 2036, HZ], [[0, 0], [12, 0], [12, 8], [0, 10]], "frame", axis="x")
    # spring scale (flat chrome tube, hook at both ends) hanging from the arm
    d.tube(f"scale-hook-{s}", [[TX, 2024, HZ], [TX, 1992, HZ]], 5, "chrome", soft=True)
    d.box(f"scale-{s}", [TX - 15, 1760, HZ - 11, TX + 15, 1995, HZ + 11], "chrome", r=8)
    d.box(f"scale-win-{s}", [TX - 6, 1785, HZ + 10, TX + 6, 1965, HZ + 12], "metal#e9eef2", soft=True)
    d.tube(f"scale-rod-{s}", [[TX, 1760, HZ], [TX, 1662, HZ]], 5, "chrome", soft=True)
    # spreader bar along x, centred under the scale, from the column to +SPR
    X0, X1 = x + 5, x + SPR
    d.cyl(f"spreader-{s}", [X0 - 10, 1655, HZ], [X1 + 10, 1655, HZ], 16, "bar")
    for k, xs in enumerate((X0 + 12, X1 - 12)):
        # S-hook and a chrome triangle buckle at the sling top
        d.tube(f"hook-{s}{k}", [[xs, 1662, HZ], [xs + 8, 1645, HZ], [xs, 1628, HZ], [xs, 1590, HZ]], 5, "chrome",
               bend=6, soft=True)
        d.tube(f"tri-{s}{k}", [[xs, 1590, HZ], [xs - 34, 1528, HZ], [xs + 34, 1528, HZ], [xs, 1590, HZ]], 5,
               "chrome", bend=4, soft=True)
        # sling: a wide khaki band hanging in a loop from the buckle bar (flat from the front, a narrow U from the
        # side), slightly creased and turned on its hook like soft cloth
        tw = 6 if k == 0 else -8
        rz = (13 if k == 0 else -9) + (4 if s == "r" else 0)
        lp = [[xs, 1528, HZ + 4], [xs, 1440, HZ + 12], [xs, 1330, HZ + 20], [xs, 1210, HZ + 26], [xs, 1105, HZ + 24],
              [xs, 1062, HZ + 4], [xs, 1068, HZ - 18], [xs, 1150, HZ - 24], [xs, 1300, HZ - 16], [xs, 1440, HZ - 8],
              [xs, 1528, HZ - 3]]
        rr = rot("y", tw, [xs, 0, HZ])
        d.strap(f"sling-{s}{k}", lp, [SW, 4], "sling", bend=30, rot=rr, rots=[rot("z", rz * 0.25, [xs, 1528, HZ])])
        # stitched hem bands at the top (darker), and a crease line down the face
        d.strap(f"sling-hem-{s}{k}", [[xs, 1526, HZ + 7], [xs, 1490, HZ + 11]], [SW + 2, 5], "slingIn", rot=rr,
                rots=[rot("z", rz * 0.25, [xs, 1528, HZ])], soft=True)
        d.strap(f"sling-crease-{s}{k}", [[xs + 18, 1470, HZ + 16], [xs + 22, 1300, HZ + 23], [xs + 15, 1130, HZ + 28]],
                [10, 5], "slingIn", rot=rr, rots=[rot("z", rz * 0.25, [xs, 1528, HZ])], soft=True)
d.save()

# ---------------- xy-kgj-1 ----------------
W, DD, H = 1220, 500, 1250
d = D("xy-kgj-1", [W, DD, H], {"rim": "metal#c9cdd2", "top": "rubber#8199d4", "chrome": "metal#e2dccb",
                                "foam": "rubber#1e2b28", "knob": "plastic#141416", "base": "plastic#dcc9a4",
                                "red": "gloss#e4645a", "blue": "gloss#4f8fd0", "holder": "plastic#1c1d20"})
d.box("platform", [0, 0, 0, W, 58, DD], "rim", r=3)
d.box("top", [16, 57, 16, W - 16, 61, DD - 16], "top", r=2)
for i in range(9):  # rivets along the front and back rim
    d.sphere(f"rivet{i}", [70 + i * 135, 30, DD + 0.5], 7, "metal#9da2a8", soft=True, copies=[[0, 0, -DD - 1]])
for i in range(3):  # and on the ends
    d.sphere(f"rivet-e{i}", [-0.5, 30, 100 + i * 150], 7, "metal#9da2a8", soft=True, copies=[[W + 1, 0, 0]])
# handrail posts stand near the FRONT edge (photo: both base plates right behind the front rim); the rail is a
# warm-tinted chrome (brassy in the photo); telescopic sleeve with the clamp knob at ~1080, a low knob at ~110,
# knobs on the +x side of each post
PZ = DD - 58
for x in (240, 980):
    d.box(f"plate{x}", [x - 40, 60, PZ - 40, x + 40, 66, PZ + 40], "chrome", r=4)
    d.cyl(f"sleeve{x}", [x, 64, PZ], [x, 1085, PZ], 34, "chrome")
    d.cyl(f"sleeve-top{x}", [x, 1068, PZ], [x, 1092, PZ], 40, "chrome")
    knob(d, f"knob-lo{x}", [x + 16, 112, PZ], axis="x", dd=40)
    knob(d, f"knob-hi{x}", [x + 18, 1080, PZ], axis="x", dd=40)
d.tube("rail", [[240, 1080, PZ], [240, 1232, PZ], [980, 1232, PZ], [980, 1080, PZ]], 28, "chrome", bend=60)
d.cyl("grip", [292, 1232, PZ], [928, 1232, PZ], 40, "foam")
# rotating disc on a beige dome base, tilted ~13 deg (left side down) as in the photo, behind the post line
CX, CZ = 610, 225
d.lathe("dome", [CX, 60, CZ], [[150, 0], [140, 30], [105, 70], [70, 92], [0, 96]], "base")
d.box("pin", [CX - 3, 60, CZ + 150, CX + 3, 175, CZ + 172], "metal#d8dadd", r=2)  # flat stop blade
YD = 165
tilt = rot("z", 13, [CX, YD, CZ])
half = lambda sgn: f"M {CX - 225} {CZ} A 225 225 0 0 {1 if sgn > 0 else 0} {CX + 225} {CZ} Z"
d.slab("disc-back", "top", half(1), [YD, YD + 16], "red", r=4, rot=tilt)
d.slab("disc-front", "top", half(-1), [YD, YD + 16], "blue", r=4, rot=tilt)
d.cyl("disc-hub", [CX, YD + 16, CZ], [CX, YD + 19, CZ], 30, "metal#d8dadd", soft=True, rot=tilt)
Y0 = YD + 16
# foot holders on a line turned ~12 deg (left end toward the front): left = a binding with a high heel cup at the
# outer end and two straps; right = a slider plate on a slotted rail with a tall toe clip at the outer end
def holder(k, x0, x1, zc, outer_left, clip_h, nstraps):
    hw = 52
    d.add(f"holder{k}", "slab", "holder", plane="top", outline=rpoly([(x0, zc - hw), (x1, zc - hw), (x1, zc + hw),
          (x0, zc + hw)], 30), w=[Y0, Y0 + 12], r=4, rot=tilt)
    xo = x0 if outer_left else x1
    sg = 1 if outer_left else -1    # inward direction
    cup = [(xo, Y0), (xo, Y0 + clip_h * 0.75), (xo + sg * 18, Y0 + clip_h), (xo + sg * 52, Y0 + clip_h + 4),
           (xo + sg * 54, Y0 + clip_h - 12), (xo + sg * 26, Y0 + clip_h - 22), (xo + sg * 14, Y0 + clip_h * 0.6),
           (xo + sg * 14, Y0)]
    if not outer_left:
        cup = cup[::-1]
    d.add(f"cup{k}", "slab", "holder", plane="front", outline=rpoly(cup, 6), w=[zc - hw + 4, zc + hw - 4], r=4,
          rot=tilt)
    # side wings of the cup
    d.box(f"wing{k}", [min(xo, xo + sg * 70), Y0, zc - hw - 2, max(xo, xo + sg * 70), Y0 + clip_h * 0.45,
                       zc - hw + 6], "holder", r=4, copies=[[0, 0, 2 * hw - 4]], rot=tilt)
    for j in range(nstraps):
        xm = (x0 + x1) / 2 + (j - (nstraps - 1) / 2) * 70 - sg * 20
        d.strap(f"strap{k}{j}", [[xm, Y0 + 10, zc - hw - 3], [xm, Y0 + 52, zc - hw + 12], [xm, Y0 + 60, zc],
                                 [xm, Y0 + 52, zc + hw - 12], [xm, Y0 + 10, zc + hw + 3]], [38, 5], "holder",
                bend=16, rot=tilt)
        d.box(f"buckle{k}{j}", [xm - 14, Y0 + 58, zc - 34, xm + 14, Y0 + 66, zc - 6], "metal#d8dadd", r=3,
              rot=tilt, soft=True)
holder(0, CX - 240, CX - 45, CZ + 60, True, 92, 2)
holder(1, CX + 70, CX + 262, CZ - 42, False, 118, 1)
# the right holder slides on a slotted rail: slot plate + chrome lock screw at its inner end
d.box("rail-plate", [CX + 10, Y0, CZ - 62, CX + 75, Y0 + 7, CZ - 22], "holder", r=3, rot=tilt)
d.cyl("lock", [CX + 52, Y0 + 12, CZ - 42], [CX + 52, Y0 + 24, CZ - 42], 26, "metal#d8dadd", rot=tilt)
d.save()
