from pd1_lib import *
# 6 semicircular foam arcs (section 150 × 300) alternating back / front along x: a wave of half-rings
SW, SH = 150, 300
R = (2600 - SW) / 12.0                 # centre-line radius of every arc
D_ = int(2 * (R + SW / 2) + 2)
zc = D_ / 2
cols = ["#e02020", "#f6d21a", "#14915a", "#e02020", "#1f4fb5", "#16a58a"]
d = K("circular-walking", [2600, D_, SH], {})
for k, c in enumerate(cols):
    cx = SW / 2 + R + 2 * R * k
    side = 1 if k % 2 == 0 else -1        # even arcs bulge to the back (−z), odd ones to the front
    pts = []
    n = 18
    for i in range(n + 1):
        a = math.radians(180 - 180 * i / n)
        pts.append([cx + R * math.cos(a), SH / 2, zc - side * R * math.sin(a)])
    d.add(f"arc{k}", "sweep", f"leather#{c[1:]}", path=pts, section=[SW - 4, SH], shape="rect", r=14)
    # a thin dark seam ring at the joint with the next arc
    if k < len(cols) - 1:
        x = cx + R
        d.box(f"seam{k}", [x - 1.5, 6, zc - SW / 2 + 6, x + 1.5, SH - 6, zc + SW / 2 - 6], "plastic#5a5a5a", soft=True)
d.save()
