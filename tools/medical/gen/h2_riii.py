from h2lib import *
# XY-SL-RIII children gait pool (photo front-left): white acrylic deck with rounded edges over a green vertically ribbed
# skirt; big glass gait windows in the front and back walls (lower right corner chamfered, white frame); inside two
# stainless handrails at two heights along both long walls, a moulded step at the left end, a rail at the right end;
# on the back rim a grey speaker grille and a fold-up LCD screen between two chrome posts; a keypad at the front left.
W, DP, H = 3000, 1800, 1260
RY, RT = 930, 150               # deck 930..1080 (printed height 1080; the raised screen reaches ~1260)
T = RY + RT
d = D("xy-sl-riii", [W, DP, H], {
    "shell": "gloss#f7f8f9", "inner": "gloss#eef1f4", "green": "gloss#4fb848", "rib": "gloss#46a841",
    "steel": "metal#c8ccd0", "grey": "plastic#8d949c", "dark": "black#2b2f35", "blue": "gloss#2f6fd0"})
WB = 540
SK = 18                                           # skirt inset under the deck
# windows (review: front one read again with perspective; the back one sits further LEFT in the photo, behind the
# lane, and is shorter): x range, bottom, top, chamfer (dx, dy) at the lower right
WIN = {"front": (1130, 2470, 540, RY - 30, 230, 150), "back": (620, 1700, 540, RY - 30, 200, 140)}


def win(nm, g=0):
    x0, x1, b, t, cx, cy = WIN[nm]
    return f"M {x0 - g} {t + g} L {x0 - g} {b - g} L {x1 - cx + g * 0.4} {b - g} L {x1 + g} {b + cy - g * 0.4} L {x1 + g} {t + g} Z"


# skirt: front / back walls with the window holes, end walls
for nm, z0, z1 in (("front", DP - SK - 40, DP - SK), ("back", SK, SK + 40)):
    d.slab(f"skirt-{nm}", "front", f"M {SK} 0 L {W - SK} 0 L {W - SK} {RY + 2} L {SK} {RY + 2} Z " + win(nm), [z0, z1], "green", r=4)
    d.slab(f"frame-{nm}", "front", win(nm, 45) + " " + win(nm), [z1 - 2, z1 + 8] if nm == "front" else [z0 - 8, z0 + 2], "shell", r=6)
    d.slab(f"glass-{nm}", "front", win(nm, 10), [(z0 + z1) / 2 - 4, (z0 + z1) / 2 + 4], "glass", r=2)
d.box("skirt-l", [SK, 0, SK + 60, SK + 40, RY + 2, DP - SK - 60], "green", r=4)
d.box("skirt-r", [W - SK - 40, 0, SK + 60, W - SK, RY + 2, DP - SK - 60], "green", r=4)
for i, (x, z) in enumerate(((SK + 60, SK + 60), (W - SK - 60, SK + 60), (SK + 60, DP - SK - 60), (W - SK - 60, DP - SK - 60))):
    d.cyl(f"corner{i}", [x, 0, z], [x, RY + 2, z], 120, "green", sides=24)
# vertical ribs every 100 mm, short under the windows
for nm, zr in (("f", [DP - SK - 2, DP - SK + 7]), ("b", [SK - 7, SK + 2])):
    x0, x1, b, t, cx, cy = WIN["front" if nm == "f" else "back"]
    k = 0
    x = 110
    while x < W - 100:
        top = RY if (x < x0 - 60 or x > x1 + 60) else b - 50
        if top:
            d.box(f"rib-{nm}{k}", [x - 10, 0, zr[0], x + 10, top, zr[1]], "rib", r=4); k += 1
        x += 100
d.box("rib-l", [SK - 7, 0, 160, SK + 2, RY, 180], "rib", r=4, repeat=rep(15, [0, 0, 100]))
d.box("rib-r", [W - SK - 2, 0, 160, W - SK + 7, RY, 180], "rib", r=4, repeat=rep(15, [0, 0, 100]))
# basin + deck
hole = rr(200, 190, 2820, 1610, 50)
d.slab("floor", "top", P(rr(SK + 40, SK + 40, W - SK - 40, DP - SK - 40, 20)), [WB - 60, WB - 30], "inner", r=4)
# inner walls in pieces, open in front of the two windows
I0, I1 = SK + 40, DP - SK - 40

for nm, z0, z1 in (("f", 1610, I1), ("b", I0, 190)):
    x0, x1 = WIN["front" if nm == "f" else "back"][:2]
    d.box(f"wall-{nm}1", [I0, WB - 40, z0, x0, RY, z1], "inner", r=4)
    d.box(f"wall-{nm}2", [x1, WB - 40, z0, W - I0, RY, z1], "inner", r=4)
d.box("wall-l", [I0, WB - 40, I0, 200, RY, I1], "inner", r=4)
d.box("wall-r", [2820, WB - 40, I0, W - I0, RY, I1], "inner", r=4)
# the glass windows show through: open the inner wall in front of them (two lane walls drawn as thin panels instead)
d.slab("deck", "top", ring(rr(0, 0, W, DP, 60), hole), [RY, T], "shell", r=40)
# moulded step / seat at the left end
d.box("step", [200, WB - 40, 190, 620, 760, 1610], "inner", r=40)
d.tube("step-rail", [[150, T - 5, 380], [150, T + 28, 410], [150, T + 28, 1010], [150, T - 5, 1040]], 28, "steel", bend=30)
# stainless lane handrails at two heights along the front and back inner walls
for nm, z, zw, xa, xb in (("f", 1560, 1610, 1160, 2440), ("b", 240, 190, 520, 2050)):
    for k, y in enumerate((680, 850)):
        d.tube(f"rail-{nm}{k}", [[xa, y, zw], [xa, y, z], [xb, y, z], [xb, y, zw]], 32, "steel", bend=30)
d.tube("rail-r", [[2820, 850, 500], [2770, 850, 500], [2770, 850, 1300], [2820, 850, 1300]], 32, "steel", bend=30)
# jets on the inner walls
d.lathe("jet", [700, 600, 1608], [[0, 0], [20, 0], [20, 6], [0, 8]], "chrome", axis="z",
        rot=rot("y", 180, [700, 600, 1608]), copies=[[300, 120, 0], [1950, 0, 0]])
d.lathe("jet-fl", [1500, WB - 28, 900], [[0, 0], [22, 0], [22, 5], [0, 7]], "chrome", copies=[[400, 0, 300], [700, 0, -200], [-300, 0, 350]])
d.lathe("jet-b", [2350, 760, 192], [[0, 0], [20, 0], [20, 6], [0, 8]], "chrome", axis="z", copies=[[-1900, 0, 0], [300, -100, 0]])
# back rim: speaker grille, LCD screen between two chrome posts
# speaker grille on the back inner wall near the top, facing the lane
d.lathe("speaker", [2150, RY - 90, 190], [[0, 0], [80, 0], [80, 8], [0, 8]], "grey", axis="z")
d.slab("speaker-g", "front", ring(ell(2150, RY - 90, 62, 62), ell(2150, RY - 90, 48, 48)) + " " + P(ell(2150, RY - 90, 34, 34)) + " " + P(ell(2150, RY - 90, 20, 20)),
       [197, 201], "plastic#6f767e", r=1)
for i, x in enumerate((2440, 2840)):
    d.cyl(f"post{i}", [x, T - 2, 95], [x, T + 120, 95], 50, "chrome")
d.box("screen-hinge", [2540, T - 2, 70, 2740, T + 30, 120], "grey", r=8)
d.add("screen", "screen", "plastic#9aa0a8", box=[2520, T + 20, 80, 2760, H, 110], r=10, face="front", bezel=16,
      rot=rot("x", -10, [2640, T + 20, 95]))
# keypad and buttons at the front left of the deck
d.add("keypad", "screen", "plastic#3a3f46", box=[150, T - 4, 1640, 430, T + 8, 1740], r=6, face="top", bezel=10)
d.lathe("btn-chr", [200, T - 2, 1560], [[0, 0], [18, 0], [18, 8], [0, 10]], "chrome", copies=[[400, 0, 60]])
d.lathe("btn-blue", [400, T - 2, 1560], [[0, 0], [18, 0], [18, 8], [0, 10]], "blue")
d.save()
