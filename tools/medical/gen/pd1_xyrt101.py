from pd1_lib import *
W, D_, H = 550, 500, 1000
d = K("xyrt-101", [W, D_, H], {"w": "wood#e8cc9c", "wb": "plastic#f6f6f3", "green": "gloss#2fa04a", "red": "gloss#e02a2a",
                                "yel": "gloss#f4cf1e", "blue": "gloss#5cb8e8", "ink": "plastic#2a2a2a"})
# A-frame: front legs splayed at the floor, leaning back to the hinge; rear legs down to the back
FT, FB = [130, 660, 372], [52, 0, 470]
RT, RB = [130, 645, 340], [95, 0, 50]
d.bar("fleg", FB, FT, [34, 22], "w", r=3, mirror="x")
d.bar("rleg", RT, RB, [32, 20], "w", r=3, mirror="x")
d.sphere("hknob", [112, 664, 372], 34, "red", mirror="x")
# side rungs between front and rear legs, green end knobs
def on(a, b, y): t = y / b[1] if b[1] else 0; return [a[0] + (b[0] - a[0]) * y / b[1], y, a[2] + (b[2] - a[2]) * y / b[1]]
f3, r3 = on(FB, FT, 330), on(RB, RT, 330)
d.cyl("rung", [f3[0] - 18, 330, f3[2]], [r3[0] - 18, 330, r3[2]], 20, "w", mirror="x")
d.sphere("rk", [f3[0] - 24, 330, f3[2] + 6], 30, "green", mirror="x")
f5 = on(FB, FT, 480)
d.sphere("fk", [f5[0] - 20, 480, f5[2]], 30, "green", mirror="x")
d.sphere("rk2", [r3[0] - 24, 330, r3[2]], 30, "green", mirror="x")
# whiteboard, tilted back 12° about its pivot on the legs, colour frame green / yellow / blue / red
TL = rot("x", -12, [W / 2, 640, 392])
z0, z1 = 384, 404
d.box("bf-l", [50, 410, z0, 86, 1000, z1], "green", r=4, rot=TL)
d.box("bf-r", [W - 86, 410, z0, W - 50, 1000, z1], "blue", r=4, rot=TL)
d.box("bf-t", [86, 964, z0, W - 86, 1000, z1], "yel", r=4, rot=TL)
d.box("bf-b", [86, 410, z0, W - 86, 448, z1], "red", r=4, rot=TL)
d.box("wb", [86, 448, z0 + 2, W - 86, 964, z1 - 4], "wb", rot=TL)
d.sphere("pk", [70, 640, 380], 30, "green", mirror="x")
# line drawing of the cartoon baby (traced on a crop of the photo: board inner quad in crop pixels → board mm)
zf = z1 - 4 + 0.6
tilt = {"axis": "x", "deg": -12, "about": [W / 2, 640, 392]}
Q = [(80, 95), (605, 80), (835, 935), (290, 1005)]          # inner corners TL, TR, BR, BL (crop of the photo, 3x)


def uv(px, py):
    u, v = 0.5, 0.5
    for _ in range(30):
        x = (1 - u) * (1 - v) * Q[0][0] + u * (1 - v) * Q[1][0] + u * v * Q[2][0] + (1 - u) * v * Q[3][0]
        y = (1 - u) * (1 - v) * Q[0][1] + u * (1 - v) * Q[1][1] + u * v * Q[2][1] + (1 - u) * v * Q[3][1]
        xu = -(1 - v) * Q[0][0] + (1 - v) * Q[1][0] + v * Q[2][0] - v * Q[3][0]
        xv = -(1 - u) * Q[0][0] - u * Q[1][0] + u * Q[2][0] + (1 - u) * Q[3][0]
        yu = -(1 - v) * Q[0][1] + (1 - v) * Q[1][1] + v * Q[2][1] - v * Q[3][1]
        yv = -(1 - u) * Q[0][1] - u * Q[1][1] + u * Q[2][1] + (1 - u) * Q[3][1]
        det = xu * yv - xv * yu
        du = ((px - x) * yv - (py - y) * xv) / det
        dv = ((py - y) * xu - (px - x) * yu) / det
        u, v = u + du, v + dv
    return (86 + u * 378, 964 - v * 516)


def P(pts): return [uv(*p) for p in pts]
def E(cx, cy, rx, ry, a0=0, a1=360, n=18): return P(ring(cx, cy, rx, ry, a0, a1, n))


head = E(382, 382, 142, 152, 0, 360, 24)
lines = [head, E(240, 485, 56, 56, -60, 250, 14), E(532, 300, 50, 52, -110, 200, 14),       # head, ears (behind the head)
         E(235, 488, 22, 18, 20, 300, 6), E(528, 300, 20, 18, 20, 300, 6),                 # ear curls
         E(345, 432, 16, 20, n=8), E(410, 418, 16, 20, n=8),                                 # eyes
         P([(325, 398), (360, 404)]), P([(398, 384), (432, 388)]),                           # brows
         P([(372, 455), (380, 462)]), E(392, 490, 12, 9, n=8),                                # nose, mouth
         P([(312, 232), (175, 190)]), P([(312, 232), (205, 262)]), P([(312, 232), (245, 160)]),   # hair tuft
         P([(312, 232), (335, 135)]), P([(312, 232), (395, 178)]), P([(312, 232), (392, 268)]),
         P([(338, 552), (330, 640), (362, 705), (382, 745), (555, 728), (562, 640), (520, 560), (498, 525)]),  # shirt
         P([(345, 565), (395, 600), (430, 610)]), P([(515, 565), (470, 600), (440, 610)]),         # arms to the hands
         P([(425, 612), (428, 572), (440, 562), (448, 612)]),                                      # hands together
         P([(382, 745), (385, 795), (470, 802), (472, 765), (560, 780), (562, 728)]),              # shorts
         P([(432, 802), (440, 885)]), P([(466, 802), (472, 885)]), P([(520, 780), (526, 870)]), P([(556, 780), (562, 870)]),
         E(458, 905, 30, 17, n=10), E(568, 893, 30, 17, n=10),                                   # shoes
         P([(650, 640), (730, 745), (712, 758), (632, 655), (650, 640)]),                         # crayon
         ]
strokes(d, "draw", lines, "ink", w=5, z=zf, extra=tilt)
# bugs and the little butterfly: dark blobs
for i, (px, py, w_, h_) in enumerate(((325, 830, 22, 26), (722, 820, 20, 24), (500, 150, 28, 12), (545, 175, 22, 10))):
    x, y = uv(px, py)
    d.decal(f"bug{i}", [x, y, zf], [w_, h_], "front", "ink", rots=[tilt])
# two columns of handwritten Chinese characters at the right of the figure
colA = [(558, 462), (574, 520), (588, 575), (600, 622), (615, 675), (628, 722), (642, 775), (656, 830), (672, 885)]
colB = [(622, 500), (638, 556), (652, 604), (700, 705), (712, 760)]
for i, (px, py) in enumerate(colA + colB):
    x, y = uv(px, py)
    d.decal(f"ch{i}", [x, y + 3, zf], [14, 4], "front", "ink", rots=[tilt])
    d.decal(f"cv{i}", [x + 1, y - 2, zf], [4, 14], "front", "ink", rots=[tilt])
# shelf tray low between the legs, a few magnetic pieces on it
d.box("shelf", [100, 196, 170, W - 100, 206, 430], "wb", r=2)
d.box("rim-f", [96, 196, 418, W - 96, 222, 432], "w", r=3)
d.box("rim-b", [96, 196, 166, W - 96, 222, 180], "w", r=3)
d.box("rim-s", [96, 196, 166, 110, 222, 432], "w", r=3, mirror="x")
d.box("pc1", [220, 206, 300, 300, 224, 350], "gloss#9a58b8", r=4)
d.box("pc2", [260, 206, 250, 300, 218, 280], "gloss#3aa84a", r=4)
d.box("pc3", [330, 206, 320, 380, 220, 350], "gloss#2c3a46", r=4)
d.save()
