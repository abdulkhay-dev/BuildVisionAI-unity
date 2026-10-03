"""xyrt-25 — two-castor walker for children (rear wheels). Frame: grips/open end at the back (z=0), castors at the
front (z=D) — the end the catalogue photo looks at."""
from pd3_lib import *

W, Dp, H = 430, 460, 610
G = "plastic#22a884"
d = D("xyrt-25", [W, Dp, H], {"tube": G, "grip": "rubber#1c1d1f", "tip": "rubber#2a2b2d"})
T = 25
yT, yB = 588, 140
zc = 420          # castor axis z
zp = 112          # back post
for nm, x in (("l", 17), ("r", W - 17)):
    # top rail → bend → front leg down to the castor bracket
    d.tube(f"top-{nm}", [[x, yT, 30], [x, yT, 330], [x, yB - 10, zc]], T, "tube", bend=95)
    # grip on the rail's back end (beyond the post)
    d.cyl(f"grip-{nm}", [x, yT, 10], [x, yT, 100], 34, "grip")
    d.sphere(f"gripend-{nm}", [x, yT, 10], 34, "grip", radii=[17, 17, 9])
    # back post
    d.cyl(f"post-{nm}", [x, yB, zp], [x, yT, zp], T, "tube")
    # bottom rail from the castor back, curving down to the foot under the grip end
    d.tube(f"bot-{nm}", [[x, yB, zc], [x, yB, 60], [x, 30, 28]], T, "tube", bend=70)
    d.cyl(f"tip-{nm}", [x, 0, 26], [x, 36, 27], 31, "tip")
    rigid_caster(d, f"c-{nm}", x, zc, 75, "plastic#f06a20", G, hub="rubber#1e1f22", hub_k=0.64)
    # chrome bolt heads at the joints (outer side)
    s = -1 if nm == "l" else 1
    # (photo: at the mid bar joint, the leg / bottom rail joint above the bracket, the middle low bar joint)
    d.sphere(f"bolt-{nm}", [x + s * 13, 375, 372], 9, "chrome", soft=True,
             copies=[[0, yB + 22 - 375, zc - 30 - 372], [0, yB - 375, 235 - 372]])
# cross bars
d.cyl("x-mid", [17, 375, 372], [W - 17, 375, 372], T, "tube")
d.cyl("x-low-f", [17, yB, zc - 18], [W - 17, yB, zc - 18], T, "tube")
d.cyl("x-low-m", [17, yB, 235], [W - 17, yB, 235], T, "tube")
d.box("label", [150, 363, 384, 205, 387, 386.5], "gloss#2c4ea0", r=1, soft=True)
d.box("latch", [255, 380, 376, 285, 396, 389], "chrome", r=3, soft=True)
d.save()
