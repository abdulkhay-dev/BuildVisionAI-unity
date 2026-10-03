# XYRT-121 manual treadmill (children): red belt on a yellow chassis with green deck strips, black wheels,
# two wavy red foam handrails from the tail to the front posts, red U top bar with an orange counter (front = tail, z max)
from pd2_lib import *

W, D, H = 630, 820, 980
C = W / 2
d = Design("xyrt-121", [W, D, H], {"yel": YEL, "red": RED, "blk": BLK, "belt": "rubber#d42020",
                                    "green": "plastic#5cc24a", "orange": "gloss#f08a1e", "white": "plastic#f4f4f2"})
XL, XR = 92, W - 92            # chassis side tubes, posts and rails
ZF, ZT = 120, 790              # front posts (console end, z=0 side) and tail
# chassis: two yellow side tubes, front and rear cross tubes, green deck board, red belt over rounded ends
d.cyl("side-l", [XL, 88, 40], [XL, 88, 805], 42, "yel")
d.cyl("side-r", [XR, 88, 40], [XR, 88, 805], 42, "yel")
d.cyl("cross-f", [XL, 88, 50], [XR, 88, 50], 38, "yel")
d.cyl("cross-t", [XL, 88, 795], [XR, 88, 795], 38, "yel")
d.box("deck", [XL + 14, 96, 55, XR - 14, 116, 790], "green", r=4)
d.box("belt", [XL + 26, 112, 45, XR - 26, 128, 800], "belt", r=8)
# three pairs of white shoe prints (sole + heel) pointing to the posts
for i, z in enumerate((190, 410, 640)):
    for j, dx in enumerate((-48, 48)):
        x = C + dx
        d.slab(f"print-sole{i}{j}", "top", svg_poly(ellipse_pts(x, z, 21, 36, n=24)), [128, 129.5], "white", r=0.5, soft=True)
        d.slab(f"print-heel{i}{j}", "top", svg_poly(ellipse_pts(x, z + 58, 15, 18, n=20)), [128, 129.5], "white", r=0.5, soft=True)
# black wheels at the corners (front ones under the posts on short yellow brackets)
for nm, x, z in (("lf", XL - 42, 60), ("rf", XR + 42, 60), ("lt", XL - 42, 770), ("rt", XR + 42, 770)):
    d.add(f"wheel-{nm}", "wheel", "blk", at=[x, 36, z], d=72, d2=44, axis="x")
    d.cyl(f"axle-{nm}", [x, 36, z], [XL if x < C else XR, 70, z], 22, "yel")
# front posts: yellow bottom, red foam, up into the top U bar
for nm, x in (("l", XL), ("r", XR)):
    d.cyl(f"post-{nm}", [x, 80, ZF], [x, 950, ZF], 32, "yel")
    d.cyl(f"post-foam-{nm}", [x, 165, ZF], [x, 930, ZF], 44, "red")
    d.cyl(f"post-collar-{nm}", [x, 724, ZF], [x, 760, ZF], 50, "yel")
d.lathe("knob", [XL - 22, 650, ZF], [[0, 0], [6, 0], [6, 14], [14, 16], [14, 30], [0, 32]], "blk", axis="x",
        rot=rot("y", 180, [XL - 22, 650, ZF]))  # on the x=0 side (the side the photo shows)
# top U bar: arms over the posts pointing back, round end at the front, black caps
YU = 952
u = [[XL, YU, 262]] + arc_xz(C, 120 + 0, YU, C - XL, 180, 360, n=16, rz=105) + [[XR, YU, 262]]
d.tube("top-u", u, 44, "red", bend=40)
for nm, x in (("l", XL), ("r", XR)):
    d.cyl(f"top-cap-{nm}", [x, YU, 248], [x, YU, 272], 46, "blk")
# orange counter on the front of the U, facing the user
d.lathe("counter", [C, YU + 6, 26], [[0, 0], [24, 0], [24, 22], [0, 22]], "orange", axis="y")
d.sphere("counter-ball", [C, YU + 28, 28], 0, "orange", radii=[30, 22, 18])
d.decal("counter-face", [C, YU + 28, 47], [26, 20], "front", "plastic#f6f2e6", soft=True)
# wavy handrails from the tail corners to the front posts
wave = [[0, 120, ZT], [0, 400, ZT - 2], [0, 556, 748], [0, 628, 672], [0, 642, 595], [0, 606, 505], [0, 618, 428],
        [0, 686, 335], [0, 740, 245], [0, 750, 180], [0, 742, ZF]]
for nm, x in (("l", XL), ("r", XR)):
    pts = spline([[x, p[1], p[2]] for p in wave], 5)
    d.tube(f"rail-{nm}", pts, 44, "red", bend=8)
    d.cyl(f"rail-foot-{nm}", [x, 75, ZT], [x, 150, ZT], 34, "yel")
d.save()
