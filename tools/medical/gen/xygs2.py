from pfx_lib import *
import math
d = D("xygs-2", [1060, 1050, 1160], {
  "pad": "leather#8fb8e0", "frame": "plastic#f3f3f4", "steel": "metal#c9ccd1", "black": "rubber#1e1f22",
  "foam": "leather#1d1e21", "knob": "plastic#1c1d20", "rim": "plastic#f5f6f7", "peg": "plastic#f4f4f4",
  "sand": "plastic#3aa9bd", "bag": "acrylic#eef6ff48"})
def circle(cz, cy, r):
    return f"M {cz - r} {cy} A {r} {r} 0 1 0 {cz + r} {cy} A {r} {r} 0 1 0 {cz - r} {cy} Z"
# --- floor frame: side rails full depth, front cross bar, black caps; floor bars under the chair legs
d.box("rail", [200, 0, 30, 240, 40, 1040], "frame", r=4, mirror="x")
d.box("rail-cap", [196, 0, 0, 244, 44, 34], "black", r=4, mirror="x")
d.box("front-bar", [160, 0, 1000, 900, 40, 1040], "frame", r=4)
d.box("front-cap", [130, 0, 996, 162, 44, 1044], "black", r=4, mirror="x")
d.box("floor-cross", [240, 0, 700, 820, 40, 740], "frame", r=4, copies=[[0, 0, -500]])
# --- chair: legs, seat frame, mid side bars
d.box("leg", [270, 40, 700, 310, 480, 740], "frame", r=4, mirror="x", copies=[[0, 0, -500]])
d.box("seat-side", [270, 440, 200, 310, 480, 760], "frame", r=4, mirror="x")
d.box("apron", [270, 425, 740, 790, 480, 770], "frame", r=4)
d.box("seat-back-bar", [310, 440, 200, 750, 480, 240], "frame", r=4)
d.box("mid-side", [270, 230, 240, 310, 270, 700], "frame", r=4, mirror="x")
d.box("mid-cross", [310, 230, 700, 750, 270, 740], "frame", r=4)
d.decal("label", [500, 452, 770.5], [230, 32], "front", "gloss#2a4fae", soft=True)
d.decal("label-txt", [490, 458, 771], [190, 9], "front", "plastic#f4f6fb", soft=True)
d.decal("label-txt2", [580, 444, 771], [60, 5], "front", "plastic#dfe6f5", soft=True)
# seat (blue PU on a white pan) and the tall backrest in a white rim
d.box("seat-pan", [285, 480, 220, 775, 495, 765], "rim", r=6)
d.box("seat", [292, 492, 225, 768, 555, 760], "pad", r=26, puff=8)
br = rot("x", -10, [530, 520, 230])
d.box("back-shell", [285, 510, 190, 775, 1150, 232], "rim", r=40, rot=br)
d.box("back-pad", [300, 528, 222, 760, 1134, 262], "pad", r=34, puff=7, rot=br)
d.bar("back-strut", [530, 440, 215], [530, 640, 185], [120, 30], "frame", r=4)
# armrests: black padded U loops with white front brackets
d.tube("arm", [[282, 520, 690], [282, 800, 712], [282, 800, 320], [282, 530, 310]], 34, "black", bend=70, mirror="x")
d.box("arm-bracket", [266, 470, 676, 298, 530, 706], "frame", r=4, mirror="x")
# --- knee-lever assemblies (left: x small; right: mirrored geometry but rollers at different heights)
PY, PZ = 510, 815
def lz(y):  # lever centre-line z at height y (lever leans forward to the bottom)
    return PZ + (PY - y) / (PY - 110) * 70
for s, sgn, xu, xl, roll_y, peg_y, bag_out, hand_y in (
        ("l", -1, 230, 170, 330, 265, False, 400),
        ("r", 1, 830, 890, 190, 150, True, 300)):
    o = 1 if sgn > 0 else -1          # +1 points outward on the right, -1 outward on the left
    d.bar(f"upright-{s}", [xu, 40, 920], [xu, PY + 20, PZ - 5], [40, 40], "steel", r=3)
    d.cyl(f"pivot-{s}", [xu + 30 * (-o), PY, PZ], [xl + 75 * o, PY, PZ], 54, "steel")
    xd = xl + 52 * o
    d.slab(f"disc-{s}", "side", circle(PZ, PY, 76) + " " + " ".join(
        circle(PZ + 55 * math.cos(a * math.pi / 6), PY + 55 * math.sin(a * math.pi / 6), 7) for a in range(12)),
        [min(xd, xd + 6 * o), max(xd, xd + 6 * o)], "steel", r=1)
    xk = xl + 75 * o
    d.lathe(f"pivot-knob-{s}", [xk, PY, PZ], [[0, 0], [20, 0], [22, 12], [14, 28], [0, 30]], "knob", axis="x",
            rot=rot("y", 0 if o > 0 else 180, [xk, PY, PZ]))
    d.bar(f"lever-{s}", [xl, PY - 30, lz(PY - 30)], [xl, 110, lz(110)], [40, 40], "steel", r=3)
    d.bar(f"sleeve-{s}", [xl, roll_y + 45, lz(roll_y + 45)], [xl, roll_y - 45, lz(roll_y - 45)], [56, 56], "steel", r=4)
    # black star knobs on the lever side and the upright front
    for i, y in enumerate((430, 385)):
        xs = xl + 20 * o
        d.lathe(f"knob-{s}{i}", [xs, y, lz(y)], [[0, 0], [8, 0], [8, 14], [24, 18], [24, 30], [0, 32]], "knob", axis="x",
                rot=rot("y", 0 if o > 0 else 180, [xs, y, lz(y)]))
    d.lathe(f"knob-u-{s}", [xu, 320, 920 - (320 - 40) / (PY - 20) * 105 + 20], [[0, 0], [8, 0], [8, 14], [24, 18], [24, 30], [0, 32]],
            "knob", axis="z")
    # black handle bar (both point to the left as in the photo)
    xh0 = xl if s == "l" else xu
    d.cyl(f"handle-{s}", [xh0 - 20, hand_y, lz(hand_y)], [xh0 - 175, hand_y, lz(hand_y)], 36, "foam")
    # shin roller pointing inward with a hanging strap loop
    xr0, xr1 = xl - 30 * o, xl - 190 * o
    zr = lz(roll_y)
    d.cyl(f"roller-{s}", [xr0, roll_y, zr], [xr1, roll_y, zr], 100, "foam")
    d.cyl(f"roller-end-{s}", [xr1, roll_y, zr], [xr1 - 6 * o, roll_y, zr], 40, "steel")
    xm = xr1 + 45 * o
    dr = min(240, roll_y - 30)   # the loop hangs down to just above the floor at most
    sp = [[xm, roll_y + 10, zr + 52], [xm - 25 * o, roll_y - dr * 0.62, zr + 70], [xm - 40 * o, roll_y - dr, zr + 40],
          [xm - 45 * o, roll_y - dr * 0.96, zr - 5], [xm - 30 * o, roll_y - dr * 0.5, zr - 30], [xm - 10 * o, roll_y - 20, zr - 52]]
    d.strap(f"strap-{s}", sp, [45, 3], "fabric#1a1a1a", bend=50, soft=True)
    d.strap(f"strap-edge-{s}", [[p[0] + 23, p[1], p[2] + (1.5 if i < 3 else -1.5)] for i, p in enumerate(sp)],
            [4, 3.6], "fabric#c2b04a", bend=50, soft=True)
    # white weight peg through the lever, teal sand in a clear bag on a small vertical rod
    zp = lz(peg_y)
    xp_out, xp_in = xl + 160 * o, xl - 150 * o
    d.cyl(f"peg-{s}", [xp_out, peg_y, zp], [xp_in, peg_y, zp], 26, "peg")
    xb = xp_out - 30 * o if bag_out else xp_in + 30 * o
    d.cyl(f"bag-rod-{s}", [xb, peg_y - 10, zp], [xb, peg_y + 110, zp], 18, "peg")
    d.sphere(f"sand-{s}", [xb, peg_y - 62, zp], None, "sand", radii=[68, 40, 68])
    d.loft(f"bag-{s}", [sec(peg_y - 104, 120, 120, 60, xb, zp), sec(peg_y - 80, 152, 152, 76, xb, zp),
                         sec(peg_y - 30, 120, 120, 60, xb, zp), sec(peg_y + 10, 34, 34, 17, xb, zp), sec(peg_y + 50, 22, 22, 11, xb, zp)],
           "bag", soft=True, dome="start")
d.save()
