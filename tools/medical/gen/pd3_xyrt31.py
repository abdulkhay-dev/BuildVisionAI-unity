"""xyrt-31 — crawl tunnel, blue/white striped sections alternating with dark green see-through net sections,
Ø800 × 5200. Five equal sections S/M/S/M/S (the photo's sections shrink only with the perspective). The net is
real: ring wires and lengthwise wires with open holes between them; the net sections sag into a slight waist."""
import math
from pd3_lib import *

W, Dp, H = 5200, 800, 800
d = D("xyrt-31", [W, Dp, H], {"white": "fabric#f2f3f5", "blue": "fabric#2440a8", "mesh": "rubber#1b3326"})
R = 398
c = [0, 400, 400]
L = W / 5
secs = [("s" if i % 2 == 0 else "m", i * L, (i + 1) * L) for i in range(5)]
SAG = 18
def rad(t):                      # net radius along a mesh section (t = 0..1): a gentle waist
    return R - 4 - SAG * math.sin(math.pi * t)
for i, (k, x0, x1) in enumerate(secs):
    if k != "s": continue
    # white skin, slightly puffed between the stripes
    d.lathe(f"skin{i}", [x0, 400, 400], [[R - 5, 0], [R - 1, 0], [R - 1, x1 - x0], [R - 5, x1 - x0], [R - 5, 0]], "white",
            axis="x", caps=False, sides=64)
    n = 6
    pitch = (x1 - x0 - 40) / n
    bw = pitch * 0.42
    d.lathe(f"stripe{i}", [x0 + 20 + (pitch - bw) / 2, 400, 400],
            [[R - 1, 0], [R + 2, 4], [R + 3, bw / 2], [R + 2, bw - 4], [R - 1, bw]], "blue",
            axis="x", caps=False, sides=64, repeat={"n": n, "step": [pitch, 0, 0]})
# the net (both mesh sections: section 1 drawn, section 3 as copies)
mx0, mx1 = secs[1][1], secs[1][2]
other = secs[3][1] - mx0
STEP = 34
nr = int((mx1 - mx0 - 30) // STEP)
for j in range((nr + 1) // 2):
    a = 15 + j * STEP
    t = a / (mx1 - mx0)
    r = rad(t)
    mirror_dx = (mx1 - mx0) - 2 * a
    cps = [[other, 0, 0]] + ([[mirror_dx, 0, 0], [other + mirror_dx, 0, 0]] if mirror_dx > 1 else [])
    d.lathe(f"ring{j}", [mx0 + a - 5, 400, 400], [[r - 6, 0], [r + 6, 0], [r + 6, 12], [r - 6, 12], [r - 6, 0]], "mesh",
            axis="x", caps=False, sides=64, soft=True, copies=cps)
NW = 72
pts = [[mx0 + (mx1 - mx0) * s / 8, 400 + rad(s / 8), 400] for s in range(9)]
for a in range(NW):
    d.tube(f"wire{a}", pts, 12, "mesh", soft=True, rot=rot("x", a * 360 / NW, c), copies=[[other, 0, 0]])
# blue binding rings at the section joints and the ends
for i, x in enumerate([0, L, 2 * L, 3 * L, 4 * L, W]):
    x0 = min(max(x - 22, 0), W - 44)
    d.lathe(f"bind{i}", [x0, 400, 400], [[R - 8, 0], [R + 3, 0], [R + 6, 22], [R + 3, 44], [R - 8, 44], [R - 8, 0]],
            "blue", axis="x", caps=False, sides=64)
d.save()
