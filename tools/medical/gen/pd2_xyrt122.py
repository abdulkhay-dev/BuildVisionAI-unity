# XYRT-122 medical treadmill (children) with parallel bars: low deck (console end at z=0, the child walks toward it
# from the tail at z max), grey 4-post cage with a rectangular top frame and hook ends at the tail, chrome S tubes up to
# a tilted grey console, a striped weight-support sling across the middle, two white obstacle boards on the belt.
from pd2_lib import *

W, D, H = 800, 1800, 1350
C = W / 2
d = Design("xyrt-122", [W, D, H], {
    "frame": "metal#8f959c", "belt": "rubber#1f2022", "black": "plastic#1d1e20", "hood": "plastic#3b3e43",
    "post": "metal#a3a8ae", "chrome": "chrome", "console": "plastic#9a9fa5", "face": "plastic#cfd8de",
    "white": "plastic#f5f5f3", "green": "fabric#8fe36a", "pink": "fabric#c8346a", "wstrip": "fabric#f2f2f2"})
# --- deck
d.box("side-l", [128, 40, 240, 200, 190, 1720], "frame", r=10)
d.box("side-r", [600, 40, 240, 672, 190, 1720], "frame", r=10)
d.box("deck", [200, 120, 250, 600, 165, 1710], "black", r=4)
d.box("belt", [204, 160, 245, 596, 182, 1712], "belt", r=9)
d.box("hood", [128, 40, 40, 672, 245, 275], "hood", r=45)
d.box("hood-top", [150, 238, 70, 650, 252, 250], "black", r=8)
for nm, x in (("l", 120), ("r", 590)):
    d.box(f"tail-cap-{nm}", [x, 30, 1690, x + 90, 180, 1792], "black", r=40)
d.box("tail-roller", [205, 118, 1705, 595, 168, 1780], "black", r=20)
d.decal("tail-label", [635, 180.5, 1745], [50, 30], "top", "gloss#f2c21a", soft=True)
for x in (165, 635):
    for z in (320, 1640):
        d.cyl(f"foot-{x}-{z}", [x, 0, z], [x, 14, z], 62, "post")
        d.cyl(f"foot-stem-{x}-{z}", [x, 14, z], [x, 44, z], 18, "chrome")
# --- cage: 4 round posts with black bases, clamp blocks and knobs
XL, XR, ZF, ZT = 92, W - 92, 300, 1590
YT = 1000
for nm, x, z in (("lf", XL, ZF), ("rf", XR, ZF), ("lt", XL, ZT), ("rt", XR, ZT)):
    s = -1 if x < C else 1
    d.cyl(f"post-{nm}", [x, 20, z], [x, YT, z], 50, "post")
    d.box(f"post-base-{nm}", [x - 34, 0, z - 34, x + 34, 140, z + 34], "black", r=8)
    d.box(f"clamp-{nm}", [x - 40, YT - 40, z - 42, x + 40, YT + 22, z + 42], "black", r=8)
    # knobs on the inner side of the posts (toward the walkway), as in the photo
    d.lathe(f"knob-{nm}", [x - s * 25, 860, z], [[0, 0], [8, 0], [8, 12], [20, 14], [20, 34], [0, 36]], "black",
            axis="x", rot=rot("y", 180, [x - s * 25, 860, z]) if s > 0 else None)
# side handrails over the posts, running past the tail posts and bending down (hooks)
for nm, x in (("l", XL), ("r", XR)):
    d.tube(f"rail-{nm}", spline([[x, YT + 30, ZF - 60], [x, YT + 30, ZT], [x, YT + 22, ZT + 110], [x, YT - 40, ZT + 175],
                                 [x, YT - 150, ZT + 190]], 5), 42, "post", bend=6)
    d.add(f"rail-end-{nm}", "lathe", "black", at=[x, YT - 152, ZT + 190], profile=[[0, 0], [22, 0], [22, 6], [0, 8]],
          rot=rot("x", 180, [x, YT - 152, ZT + 190]))
# cross bars: black at the console end, grey at the tail, grey over the sling
d.bar("cross-f", [XL, YT, ZF], [XR, YT, ZF], [44, 44], "black", r=4)
d.bar("cross-t", [XL, YT, ZT], [XR, YT, ZT], [44, 44], "post", r=4)
d.bar("cross-sling", [XL, YT + 6, 1080], [XR, YT + 6, 1080], [40, 40], "post", r=4)
# chrome S tubes from the console-end rails up to the console, joined by a bar under it
d.tube("console-tube", spline([[XL, YT + 30, ZF - 40], [XL, YT + 30, 190], [XL + 5, 1130, 120], [XL + 20, 1215, 96],
                               [C, 1225, 92], [XR - 20, 1215, 96], [XR - 5, 1130, 120], [XR, YT + 30, 190],
                               [XR, YT + 30, ZF - 40]], 6), 36, "chrome", bend=6)
# console tilted toward the user: grey casing, light face, LCD, keys
T = rot("x", 32, [C, 1250, 120])
d.box("console", [C - 215, 1225, 10, C + 215, 1282, 245], "console", r=16, rot=T)
d.box("console-face", [C - 195, 1280, 28, C + 195, 1286, 228], "face", r=6, rot=T)
d.box("lcd", [C - 85, 1285, 52, C + 85, 1289, 128], "plastic#a7b096", r=3, rot=T)
d.box("lcd-frame", [C - 95, 1284, 44, C + 95, 1287, 136], "plastic#5f7d9a", r=4, rot=T)
d.box("arc", [C - 120, 1285, 150, C + 120, 1287.5, 160], "gloss#2f5f9e", r=3, rot=T, soft=True)
d.box("key-row", [C - 108, 1285, 166, C - 88, 1291, 182], "gloss#2f5f9e", r=5, rot=T, repeat={"n": 9, "step": [27, 0, 0], "local": True})
d.box("key-grey", [C - 40, 1285, 196, C - 18, 1292, 216], "plastic#e4e6e8", r=6, rot=T, repeat={"n": 3, "step": [29, 0, 0], "local": True})
for nm, x, z, col in (("r1", C - 170, 200, "gloss#d42a26"), ("b1", C - 135, 200, "gloss#3a8fd8"), ("r2", C + 160, 200, "gloss#d42a26"),
                      ("b2", C + 125, 200, "gloss#3a8fd8"), ("r3", C + 168, 60, "gloss#d42a26"), ("r4", C + 168, 100, "gloss#d42a26")):
    d.box(f"key-{nm}", [x - 13, 1285, z - 13, x + 13, 1292, z + 13], col, r=8, rot=T)
# --- weight-support sling across the middle: chrome hanger and green / white / pink stripes
ZS = 1080
d.tube("sling-frame", [[250, YT - 15, ZS], [250, 500, ZS], [550, 500, ZS], [550, YT - 15, ZS]], 24, "chrome", bend=30)
cols = ("green", "wstrip", "pink", "wstrip", "green", "wstrip", "pink", "pink", "pink")
for i, col in enumerate(cols):
    y = 930 - i * 46
    sag = max(0, i - 5) * 18
    d.strap(f"stripe-{i}", [[256, y, ZS + 4], [C, y - sag - 6, ZS + 12], [544, y, ZS + 4]], [42, 4], col, bend=120, soft=True, roll=90)
# --- obstacle boards standing on edge along the belt; the photo is taken from the tail on the x=0 side: the fruit
# pictures are on the x=0 face of the board nearer that side
for nm, x in (("n", 270), ("f", 440)):
    d.box(f"board-{nm}", [x, 182, 470, x + 30, 395, 1640], "white", r=8)
    d.box(f"board-foot-{nm}", [x - 12, 182, 1600, x + 42, 300, 1650], "post", r=6, copies=[[0, 0, -1110]])
for i, z in enumerate(range(560, 1600, 150)):
    col = ("gloss#d4262a", "gloss#f2c21a", "gloss#6cbf3a", "gloss#d4262a", "gloss#f08a1e")[i % 5]
    r = 48 if i % 2 == 0 else 36
    d.lathe(f"fruit-{i}", [268.5, 300 - (i % 3) * 18, z], [[0, 0], [r, 0], [r, 1.2], [0, 1.2]], col, axis="x", soft=True,
            rot=rot("y", 180, [268.5, 300 - (i % 3) * 18, z]))
d.save()
