"""Pulse magnetic therapy desk unit (no model code). Writes only pulse-magnetic-therapy-device.json."""
from p5lib import *

W, DP, H = 400, 340, 120
CX, CZ = W / 2, DP / 2
d = D("pulse-magnetic-therapy-device", [W, DP, H],
      {"blue": "plastic#8fb4ef", "shell": "gloss#f6f7f8", "glass": "plastic#060607", "key": "gloss#ffffff",
       "line": "gloss#3a6fd0", "led": "plastic#8d8f93", "txt": "plastic#9a9ea4"})
# Review 2026-10-02: the photo's blue tub is ~70 % of the height and the white part a low lid sloping up from a thin
# projecting lip to a plateau at the back that carries the glass (was a 50/50 tub + puffy white block).
d.loft("tub", [sec(0, 340, 280, 88, CX, CZ), sec(16, 372, 312, 100, CX, CZ), sec(48, 396, 336, 108, CX, CZ),
               sec(72, 396, 336, 108, CX, CZ), sec(82, 390, 330, 105, CX, CZ)], "blue")
# vent grooves at the back of the right side
d.box("vent", [W - 7, 30, 150, W + 0.5, 32.5, 236], "plastic#6f8fc4", r=1.2, repeat=rep(5, [0, 8, 0]))
# white lip ring and the low lid, rising towards a plateau shifted to the back
d.loft("lip", [sec(80, 400, 340, 110, CX, CZ), sec(87, 400, 340, 110, CX, CZ)], "shell")
LID = [(85, 394, 334, 104, 170), (96, 390, 330, 103, 168), (105, 378, 316, 98, 163), (111, 360, 298, 90, 155),
       (115.5, 340, 276, 82, 147), (118.5, 318, 252, 74, 140)]
d.loft("shell", [sec(y, w, dd, r, CX, cz) for y, w, dd, r, cz in LID], "shell")

def surf(z):
    """height of the lid top along the middle at depth z (front slope)"""
    pts = [(cz + dd / 2, y) for y, w, dd, r, cz in LID]
    for (z1, y1), (z2, y2) in zip(pts, pts[1:]):
        if z2 <= z <= z1:
            return y1 + (y2 - y1) * (z1 - z) / (z1 - z2)
    return LID[-1][0] if z < pts[-1][0] else LID[0][0]
# big black glossy squircle window on the rear 60 %
d.slab("glass", "top", rrect(50, 28, W - 50, 200, 72), [115, 119.3], "glass", r=1.5)
y = 119.5
d.decal("logo", [92, y, 50], [22, 16], "top", "line", soft=True)
d.decal("logo-t", [122, y, 50], [34, 7], "top", "line", soft=True)
d.decal("title", [278, y, 54], [72, 9], "top", "plastic#e8eaee", soft=True)
d.decal("title2", [278, y, 66], [80, 4], "top", "txt", soft=True)
for gx in (88, 214):            # two channels: a thin blue frame around 3 grey LED windows
    d.decal(f"fr-h{gx}", [gx + 49, y, 98], [104, 1.6], "top", "line", soft=True, copies=[[0, 0, 44]])
    d.decal(f"fr-v{gx}", [gx - 3, y, 120], [1.6, 44], "top", "line", soft=True, copies=[[104, 0, 0]])
    d.decal(f"led{gx}", [gx + 20, y, 115], [34, 28], "top", "led", soft=True, copies=[[60, 0, 0]])
    d.decal(f"ledm{gx}", [gx + 51, y, 115], [20, 28], "top", "led", soft=True)
    d.decal(f"cap{gx}", [gx + 14, y, 136], [20, 3], "top", "txt", soft=True, copies=[[30, 0, 0], [70, 0, 0]])
d.decal("dot", [120, y, 168], [4, 4], "top", "led", soft=True, copies=[[160, 0, 18]])
d.decal("co", [130, y, 196], [120, 6], "top", "plastic#d8dbe0", soft=True)
# front white area on the slope: keys (pills along z, round keys), each sitting on the lid surface
import math
def tilt_at(x, z):                   # keys follow the lid slope (turned about x)
    ang = math.degrees(math.atan((surf(z - 5) - surf(z + 5)) / 10))
    return rot("x", ang, [x, surf(z), z])
def pill(id_, x, z, w, l, ang=0):
    y = surf(z)
    t = tilt_at(x, z)
    if ang:
        t = [rot("y", ang, [x, y, z]), t]
    d.slab(id_, "top", rrect(x - w / 2, z - l / 2, x + w / 2, z + l / 2, w / 2 - 0.5), [y - 1.5, y + 2.6], "key", r=1.6,
           rot=t if not ang else t[1])
    if ang:
        d.d["parts"][-1]["rot"] = t[1]
        d.d["parts"][-1]["outline"] = rrect_rot(x, z, w, l, ang)
def rrect_rot(x, z, w, l, ang):
    pts = rrect_pts(x - w / 2, z - l / 2, x + w / 2, z + l / 2, w / 2 - 0.5)
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return poly([(x + (px - x) * c + (pz - z) * s_, z - (px - x) * s_ + (pz - z) * c) for px, pz in pts])
def rkey(id_, x, z, dd):
    y = surf(z)
    d.cyl(id_, [x, y - 1.5, z], [x, y + 2.6, z], dd, "key", rot=tilt_at(x, z))
pill("time-l", 62, 250, 28, 58)
pill("freq-l", 118, 268, 24, 52, -25)
rkey("rk-l1", 168, 236, 30)
rkey("rk-l2", 152, 284, 30)
rkey("rk-c", 204, 296, 38)
rkey("rk-r1", 244, 248, 30)
pill("freq-r", 292, 276, 24, 52, 25)
pill("time-r", 346, 266, 28, 58)
d.decal("ksym", [62, surf(250) + 2.8, 250], [10, 2], "top", "txt", soft=True, rot=tilt_at(62, 250))
d.decal("ksym2", [346, surf(266) + 2.8, 266], [10, 2], "top", "txt", soft=True, rot=tilt_at(346, 266))
d.decal("ftxt", [292, surf(222) + 0.3, 222], [70, 3], "top", "txt", soft=True, copies=[[0, 0, 9]])
d.save()
