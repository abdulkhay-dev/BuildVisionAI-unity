"""Dual-channel transcranial magnetic stimulator XY-K-JLC-J: white cart with a grey spine, host / cooling unit /
drawer on shelves, top tray with monitor, two chrome coil arms (figure-8 coil left, round coil right).
Writes only xy-k-jlc-j.json."""
from p5lib import *

W, DP, H = 700, 600, 1800
CX = W / 2
d = D("xy-k-jlc-j", [W, DP, H],
      {"base": "plastic#e6e8eb", "white": "gloss#f4f5f6", "grey": "plastic#9aa0a7", "top": "plastic#8c9097",
       "dark": "plastic#3a3d42", "black": "gloss#111214", "chrome": "chrome", "coil": "gloss#f2f3f4",
       "hose": "plastic#9a9fa6", "knob": "plastic#1d1e21", "wheel": "rubber#3a3d42", "hub": "plastic#e9eaec",
       "green": "gloss#3ad13a", "red": "gloss#d42a22"})
# ---- base plate on 4 castors
for i, (x, z) in enumerate([(80, 80), (W - 80, 80), (80, DP - 80), (W - 80, DP - 80)]):
    d.add(f"castor{i}", "caster", "wheel", at=[x, 0, z], d=100)
    d.cyl(f"wcap{i}", [x - 17, 50, z], [x + 17, 50, z], 66, "hub", soft=True)
d.slab("base", "top", rrect(10, 10, W - 10, DP - 10, 70), [118, 166], "base", r=16)
# ---- grey spine at the right rear with vertical text; dark post at the left rear
d.box("spine", [552, 160, 498, 630, 1000, 590], "grey", r=10)
d.decal("spine-txt", [591, 520, 590.4], [12, 300], "front", "plastic#d3d6da", soft=True)
d.box("spine-rail", [584, 560, 589, 598, 980, 593], "plastic#e4e6e9", r=3)
d.box("post", [92, 160, 150, 132, 990, 190], "dark", r=6)
# ---- shelves and boxes
ZB0, ZB1 = 196, 588
d.box("shelf1", [78, 350, 180, 600, 362, ZB1 + 10], "white", r=4)
d.box("shelf2", [78, 668, 180, 600, 680, ZB1 + 10], "white", r=4)
# drawer: slot handle at the top edge, slot vents low on the front
d.box("drawer", [110, 166, 220, 512, 336, ZB1 - 4], "white", r=10)
d.box("drawer-slot", [190, 312, ZB1 - 6, 426, 326, ZB1 - 2], "dark", r=5)
d.box("drawer-vent", [176, 190, ZB1 - 5, 180, 198, ZB1 - 3], "dark", soft=True, repeat=rep(30, [9, 0, 0]))
# cooling unit: grey top, LED column, gauge, dot grille at the right
d.box("cool", [92, 364, ZB0, 532, 648, ZB1], "white", r=10)
d.box("cool-top", [98, 640, ZB0 + 6, 526, 650, ZB1 - 6], "top", r=4)
d.decal("cool-logo", [150, 610, ZB1 + 0.4], [56, 8], "front", "gloss#2f7fd8", soft=True)
d.cyl("cool-led", [312, 540, ZB1], [312, 540, ZB1 + 2], 6, "green", copies=[[0, -16 * k, 0] for k in range(1, 6)])
d.decal("cool-ledt", [326, 500, ZB1 + 0.4], [12, 82], "front", "plastic#b0b4ba", soft=True)
d.box("gauge", [424, 420, ZB1 - 1, 436, 500, ZB1 + 2], "plastic#2a2c30", r=2)
d.box("gauge-in", [427, 430, ZB1 + 1.5, 433, 470, ZB1 + 2.5], "red", soft=True)
d.cyl("grille", [462, 420, ZB1], [470, 420, ZB1 + 1], 5, "dark", sides=8, soft=True, repeat=rep(5, [11, 0, 0]),
      copies=[[0, 11 * k, 0] for k in range(1, 9)])
d.decal("cool-sym", [478, 590, ZB1 + 0.4], [16, 16], "front", "plastic#8a8e94", soft=True)
# host: grey top, black 7" LCD, two silver knobs, red E-stop, two sockets
d.box("host", [92, 682, ZB0, 532, 924, ZB1], "white", r=10)
d.box("host-top", [98, 916, ZB0 + 6, 526, 926, ZB1 - 6], "top", r=4)
d.decal("host-logo", [152, 900, ZB1 + 0.4], [58, 8], "front", "gloss#2f7fd8", soft=True)
d.decal("host-title", [152, 886, ZB1 + 0.4], [58, 6], "front", "plastic#6a6e74", soft=True)
d.add("lcd", "screen", "black", box=[178, 728, ZB1 - 2, 330, 846, ZB1 + 3], r=4, face="front", bezel=6)
d.lathe("knob", [136, 846, ZB1], [[0, 0], [14, 0], [14, 14], [12, 16], [0, 16]], "metal#c4c7cc", axis="z",
        copies=[[230, 0, 0]])
d.box("estop-plate", [400, 760, ZB1, 450, 814, ZB1 + 4], "gloss#f2c419", r=4)
d.lathe("estop", [425, 787, ZB1 + 4], [[0, 0], [11, 0], [11, 6], [19, 8], [20, 17], [14, 21], [0, 22]], "red", axis="z")
d.box("sock", [468, 794, ZB1 - 1, 494, 820, ZB1 + 6], "plastic#202226", r=4, copies=[[0, -36, 0]])
d.decal("host-txt", [312, 700, ZB1 + 0.4], [340, 4], "front", "plastic#a0a4aa", soft=True)
# ---- top tray, monitor on a slim stand, mouse
d.slab("tray", "top", rrect(20, 120, W - 20, DP, 40), [984, 1016], "white", r=10)
d.sphere("mouse", [330, 1026, 480], None, "white", radii=[28, 12, 44])
d.box("mfoot", [370, 1016, 330, 470, 1024, 400], "metal#c4c7cc", r=3)
d.bar("mstand", [420, 1020, 360], [420, 1140, 322], [40, 10], "metal#c4c7cc", r=3)
d.box("mback", [340, 1130, 300, 500, 1300, 318], "plastic#d8dadd", r=10)
d.add("monitor", "screen", "plastic#e6e8eb", box=[210, 1072, 316, 630, 1352, 336], r=6, face="front", bezel=10,
      print="med_xy-k-jlc-j_screen")
# ---- coil arms: mount on the tray, chrome segment up to an elbow (black knob), segment to a clamp on the stem
def arm(id_, mount, elbow, clamp, stem_x, knob_dx):
    z = 250
    d.box(id_ + "-mount", [mount[0] - 20, 1012, z - 20, mount[0] + 20, 1040, z + 20], "metal#c4c7cc", r=6)
    d.cyl(id_ + "-a1", [mount[0], 1030, z], [elbow[0], elbow[1], z], 22, "chrome")
    d.sphere(id_ + "-elbow", [elbow[0], elbow[1], z], 38, "chrome")
    d.cyl(id_ + "-kshaft", [elbow[0], elbow[1], z], [elbow[0] + knob_dx, elbow[1], z], 10, "chrome")
    d.lathe(id_ + "-knob", [elbow[0] + knob_dx, elbow[1], z], [[0, 0], [22, 0], [22, 6], [8, 14], [0, 14]], "knob",
            axis="x", rot=rot("z", 180, [elbow[0] + knob_dx, elbow[1], z]) if knob_dx < 0 else None)
    d.cyl(id_ + "-a2", [elbow[0], elbow[1], z], [clamp[0], clamp[1], z], 22, "chrome")
    d.lathe(id_ + "-clamp", [stem_x, clamp[1] - 30, z], [[0, 0], [24, 0], [24, 60], [0, 60]], "chrome")
    d.cyl(id_ + "-cknob", [stem_x + (26 if knob_dx > 0 else -26), clamp[1], z],
          [stem_x + (64 if knob_dx > 0 else -64), clamp[1], z], 36, "metal#b9bdc2", sides=12)
    d.lathe(id_ + "-stem", [stem_x, clamp[1] - 110, z], [[0, 0], [20, 0], [20, 150], [26, 210], [32, 260], [0, 260]], "coil")
    return z
CY = 1580
z = arm("la", (150, 1030), (238, 1250), (40, 1395), -4, 50)
import math
def heart(cx, cy, a, r, by, n=24):
    """two circles r at (cx +- a, cy) merged at the top dip, outer tangents down to a rounded bottom at (cx, by)"""
    h = math.sqrt(r * r - a * a)
    acs = math.acos(r / math.hypot(a, cy - by))
    psi = math.atan2(h, -a)                                   # dip seen from the right centre
    tr = math.atan2(by - cy, -a) + acs                        # lower-right tangent angle
    phi = math.atan2(h, a)                                    # dip seen from the left centre
    tl = math.atan2(by - cy, a) - acs + 2 * math.pi           # lower-left tangent angle
    pts = [(cx + a + r * math.cos(psi + (tr - psi) * k / n), cy + r * math.sin(psi + (tr - psi) * k / n)) for k in range(n + 1)]
    pts += [(cx + 9, by + 5), (cx, by), (cx - 9, by + 5)]
    pts += [(cx - a + r * math.cos(tl + (phi - tl) * k / n), cy + r * math.sin(tl + (phi - tl) * k / n)) for k in range(n + 1)]
    return poly(pts)
lobes = heart(-4, CY + 30, 46, 72, CY - 92)
d.slab("coil-l", "front", lobes, [z - 12, z + 12], "coil", r=8)
d.slab("coil-l-neck", "front", poly([(-40, CY - 60), (32, CY - 60), (20, CY - 120), (-28, CY - 120)]), [z - 13, z + 13], "coil", r=10)
d.cyl("coil-l-hole", [-48, CY + 34, z + 11], [-50, CY + 16, z + 13.5], 20, "plastic#55595f", copies=[[88, 0, 0]])
d.box("coil-l-win", [-16, CY - 40, z + 11, 8, CY - 28, z + 14], "plastic#2a2c30", r=2)
z = arm("ra", (615, 1030), (672, 1262), (600, 1420), 600, -50)
d.cyl("coil-r", [600, CY + 30, z - 11], [640, CY + 30, z + 11], 186, "coil", sides=48)
d.cyl("coil-r-hole", [600, CY + 30, z + 10], [640, CY + 30, z + 12.5], 24, "plastic#55595f")
d.slab("coil-r-neck", "front", poly([(560, CY - 50), (640, CY - 50), (628, CY - 95), (572, CY - 95)]), [z - 13, z + 13], "coil", r=10)
# ---- hoses from the stems down along the sides into the host
d.tube("hose-l", [[-4, 1285, 250], [-24, 1100, 270], [10, 880, 320], [93, 800, 380]], 40, "hose", rib=3, pitch=12,
       bend=120, soft=True)
d.tube("hose-r", [[600, 1310, 250], [662, 1100, 280], [650, 860, 330], [533, 780, 380]], 40, "hose", rib=3, pitch=12,
       bend=120, soft=True)
d.save()
