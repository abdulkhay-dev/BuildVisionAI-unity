"""sensory-soft-ball-pool: soft foam wall blocks in dark red and green around a pool of multicolour balls."""
import random
from s2lib import *

W, Dp, H, T = 1700, 1500, 600, 180
d = D("sensory-soft-ball-pool", [W, Dp, H], {"red": "leather#8c211d", "green": "leather#4b8a2f", "fill": "plastic#3a3f60"})
def block(id, x0, z0, x1, z1, mat):
    d.box(id, [x0, 0, z0, x1, H, z1], mat, r=18, puff=4)
# front wall (photo 1): red | green | red. Photo 1 also shows the back wall's top red | green | red and the side
# walls two blocks each: left = green at the front, red at the back; right = red at the front, green at the back
# (photo 2, the front-right corner: front green, front red | corner | right red, right green).
for i, (a, b, m) in enumerate([(0, 610, "red"), (610, 1110, "green"), (1110, W, "red")]):
    block(f"front{i}", a, Dp - T, b, Dp, m)
for i, (a, b, m) in enumerate([(0, 600, "red"), (600, 1100, "green"), (1100, W, "red")]):
    block(f"back{i}", a, 0, b, T, m)
for i, (a, b, m) in enumerate([(T, Dp / 2, "red"), (Dp / 2, Dp - T, "green")]):
    block(f"left{i}", 0, a, T, b, m)
for i, (a, b, m) in enumerate([(T, Dp / 2, "green"), (Dp / 2, Dp - T, "red")]):
    block(f"right{i}", W - T, a, W, b, m)
# balls: a loose hex layer near the top over a hidden filler
d.box("fill", [T, 0, T, W - T, 470, Dp - T], "fill")
cols = ["gloss#e02a2a", "gloss#f5d21e", "gloss#f58a1e", "gloss#3cb43c", "gloss#2a8ae0", "gloss#1f3fa8"]
rnd = random.Random(11)
pos = {c: [] for c in range(len(cols))}
bd = 100
j = 0
z = T + bd / 2
while z <= Dp - T - bd / 2 + 1:
    x = T + bd / 2 + (bd / 2 if j % 2 else 0)
    while x <= W - T - bd / 2 + 1:
        pos[rnd.randrange(len(cols))].append([x, 495 + rnd.uniform(-18, 14), z + rnd.uniform(-5, 5)])
        x += bd
    z += bd * 0.866; j += 1
for c, ps in pos.items():
    p0 = ps[0]
    d.sphere(f"balls{c}", p0, bd, cols[c], soft=True, copies=[[p[0] - p0[0], p[1] - p0[1], p[2] - p0[2]] for p in ps[1:]])
d.save()
