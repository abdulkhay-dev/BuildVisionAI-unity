"""Older Xiangyu carts with a framed drawer front: XY-K-LC-5 (pneumatic compression) and XY-K-CZR-II
(magnetic vibration heat). Writes only xy-k-lc-5.json and xy-k-czr-ii.json."""
from lib import *
from p4lib import *

def plinth(d, x0, x1, z0, z1, y0, y1, mat, front=60, side=45, back=40):
    xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
    o = (f"M {x0} {z0 + 45} Q {x0} {z0} {x0 + 45} {z0} Q {xm} {z0 + 2 * back} {x1 - 45} {z0} Q {x1} {z0} {x1} {z0 + 45} "
         f"Q {x1 - 2 * side} {zm} {x1} {z1 - 45} Q {x1} {z1} {x1 - 45} {z1} Q {xm} {z1 - 2 * front} {x0 + 45} {z1} "
         f"Q {x0} {z1} {x0} {z1 - 45} Q {x0 + 2 * side} {zm} {x0} {z0 + 45} Z")
    d.slab("plinth", "top", o, [y0, y1], mat, r=16)

def front_frame(d, x0, x1, y0, y1, z, rb, rows, gap="plastic#c4c8cd", frame="frame"):
    """Raised frame (arched bottom corners rb) around stacked panels; rows = [(name, ya, yb), ...] top to bottom."""
    t = 12
    d.slab("frame", "front", poly(frame_pts(x0, y0, x1, y1, 22, rb)) + " " + poly(frame_pts(x0 + t, y0 + t, x1 - t, y1 - t, 12, rb - t)),
           [z - 4, z + 7], frame, r=3)
    d.slab("gap", "front", poly(frame_pts(x0 + t, y0 + t, x1 - t, y1 - t, 12, rb - t)), [z - 4, z + 1], gap, r=1)
    for nm, ya, yb in rows:
        rr = rb - t - 4 if ya <= y0 + t + 2 else 4
        d.slab(nm, "front", poly(frame_pts(x0 + t + 3, ya, x1 - t - 3, yb, 4, rr)), [z - 4, z + 4], "panel", r=2)

def frame_pts(x0, y0, x1, y1, rt, rb, n=8):
    return (arc(x1 - rb, y0 + rb, rb, -90, 0, n) + arc(x1 - rt, y1 - rt, rt, 0, 90, n) +
            arc(x0 + rt, y1 - rt, rt, 90, 180, n) + arc(x0 + rb, y0 + rb, rb, 180, 270, n))

def u_handle(d, xb, so, y, za, zb, dia, mat, mount):
    """U bar standing off both sides of a body whose left face is at x = xb (mirrored)."""
    xo = xb - so
    d.tube("handle", [[xb, y, zb], [xo, y, zb], [xo, y, za], [xb, y, za]], dia, mat, bend=dia * 0.9, mirror="x")
    d.cyl("handle-mount", [xb + 2, y, za], [xb - 16, y, za], dia + 16, mount, mirror="x", copies=[[0, 0, zb - za]])

def side_slots(d, x, y0, z0, n, len_, pitch, mat, groups):
    d.box("side-slots", [x - 2, y0, z0, x + 1, y0 + 4, z0 + len_], mat, repeat=rep(n, [0, pitch, 0]), mirror="x",
          copies=[[0, 0, g] for g in groups])

def vent_dots(d, x, y0, z0, mat, grids):
    offs = [[0, -9 * r, g] for g in grids for r in range(4)][1:]
    d.box("vent-dots", [x - 1, y0, z0, x + 1, y0 + 4, z0 + 4], mat, soft=True, repeat=rep(7, [0, 0, 9]), copies=offs)

# ------------------------------------------------------------------ XY-K-LC-5
def lc5():
    d = D("xy-k-lc-5", [560, 480, 1150], {"shell": "gloss#f3f4f5", "frame": "plastic#d5d8dc", "panel": "gloss#f6f7f8",
                                           "head": "plastic#dfe1e4", "glass": "gloss#121316", "dark": "plastic#3d4146"})
    plinth(d, 10, 550, 0, 480, 95, 185, "shell", front=55)
    d.add("castor", "caster", "rubber#3b3e43", at=[55, 0, 50], d=110, copies=[[450, 0, 0], [0, 0, 385], [450, 0, 385]])
    d.box("body", [55, 45, 40, 505, 926, 440], "shell", r=30)
    front_frame(d, 100, 460, 50, 866, 440, 70,
                [("logo-panel", 714, 852), ("drawer-1", 578, 710), ("drawer-2", 428, 574), ("door", 64, 424)])
    d.box("pull", [245, 696, 443, 315, 707, 446], "black#141517", r=3, copies=[[0, -136, 0]])
    d.cyl("logo-mark", [238, 790, 443], [238, 790, 446], 40, "gloss#2f86c8", soft=True)
    d.decal("logo-text", [318, 796, 444.5], [92, 18], "front", "plastic#2f86c8", soft=True)
    d.decal("logo-sub", [318, 777, 444.5], [92, 6], "front", "plastic#5f9fd0", soft=True)
    side_slots(d, 55, 255, 300, 7, 45, 11, "plastic#9da3aa", [0, 65])
    # ledge with 2 hose connectors, dark strip with 2 windows
    d.box("ledge", [68, 924, 60, 492, 960, 448], "head", r=8)
    d.box("conn", [150, 932, 444, 205, 952, 453], "plastic#7d93b0", r=4, copies=[[205, 0, 0]])
    d.box("conn-slot", [156, 937, 450, 199, 947, 455], "plastic#2c3440", r=2, copies=[[205, 0, 0]])
    d.box("strip", [150, 878, 436, 410, 906, 447], "dark", r=12)
    d.box("strip-win", [232, 883, 445, 274, 901, 449], "black#0d0e10", r=2, copies=[[52, 0, 0]])
    d.decal("strip-text", [280, 903, 447.5], [120, 3], "front", "plastic#9aa0a6", soft=True)
    # head: light grey box, black glass front with logo text (left) and the touch screen (right)
    d.box("head", [50, 958, 90, 510, 1150, 450], "head", r=30)
    d.box("head-glass", [72, 974, 444, 488, 1136, 453], "glass", r=12)
    # touch screen (no screen crop): light UI with the blue leg-chamber drawing and a column of icons at the right
    d.box("screen", [300, 988, 450, 474, 1122, 455.5], "gloss#eef2f6", r=4)
    d.decal("ui-leg", [372, 1078, 455.8], [110, 12], "front", "plastic#5b8fd0", soft=True)
    d.decal("ui-leg2", [372, 1052, 455.8], [110, 10], "front", "plastic#8db3e0", soft=True)
    d.decal("ui-icon", [455, 1100, 455.8], [10, 8], "front", "plastic#9db4cf", soft=True, repeat=rep(6, [0, -17, 0]))
    d.decal("ui-text", [350, 1015, 455.8], [70, 4], "front", "plastic#9aa3ad", soft=True, copies=[[0, -12, 0]])
    d.cyl("head-mark", [112, 1100, 452], [112, 1100, 455], 26, "gloss#2f86c8", soft=True)
    d.decal("head-name", [175, 1100, 453.5], [80, 12], "front", "plastic#e8eaec", soft=True)
    d.decal("head-text", [185, 1072, 453.5], [160, 5], "front", "plastic#8d939a", soft=True, copies=[[0, -14, 0], [0, -40, 0], [0, -52, 0]])
    d.slab("hose-holder", "side", "M 230 975 L 380 975 Q 420 1010 400 1060 L 340 1060 Q 330 1010 230 975 Z", [506, 548], "plastic#b6b2e4", r=8)
    d.box("power", [44, 1000, 330, 52, 1040, 400], "black#141517", r=6)
    d.decal("power-sw", [43, 1020, 300], [22, 26], "left", "gloss#2e9a4a", soft=True)
    vent_dots(d, 50, 1110, 120, "plastic#8f959c", [0, 75])
    # side bars along the depth: front mount near the front corner, the bar running back past the cabinet's middle
    u_handle(d, 55, 50, 830, 60, 420, 36, "wood#c8a46a", "plastic#3a3d42")
    d.save()

# ------------------------------------------------------------------ XY-K-CZR-II
def czr2():
    d = D("xy-k-czr-ii", [520, 480, 1100], {"shell": "plastic#e3e5e8", "frame": "plastic#d8dbdf", "panel": "gloss#eaedf0",
                                             "label": "plastic#a9a7a7", "dark": "plastic#4f545a"})
    plinth(d, 0, 520, 0, 480, 100, 160, "shell", front=70, side=60, back=45)
    d.add("castor", "caster", "rubber#1b1c1e", at=[50, 0, 50], d=75, copies=[[420, 0, 0], [0, 0, 385], [420, 0, 385]])
    d.box("body", [60, 60, 40, 460, 905, 440], "shell", r=26)
    front_frame(d, 95, 425, 72, 835, 440, 75,
                [("logo-panel", 695, 822), ("drawer-1", 540, 691), ("drawer-2", 392, 536), ("door", 85, 388)])
    d.box("pull", [238, 660, 441, 322, 686, 447], "plastic#b3b8be", r=4, copies=[[0, -152, 0]])
    d.box("pull-in", [244, 664, 444, 316, 676, 448], "plastic#6d7379", r=3, copies=[[0, -152, 0]])
    d.cyl("logo-mark", [222, 755, 443], [222, 755, 446], 42, "gloss#2f7fd0", soft=True)
    d.decal("logo-text", [305, 762, 444.5], [100, 20], "front", "plastic#2f7fd0", soft=True)
    d.decal("logo-sub", [305, 742, 444.5], [100, 8], "front", "plastic#2f7fd0", soft=True)
    d.decal("door-text", [185, 255, 444.5], [10, 230], "front", "plastic#8f959c", soft=True)
    side_slots(d, 60, 175, 90, 6, 55, 14, "plastic#a8adb3", [0, 70])
    # dark pill strip with 2 round sockets
    d.box("strip", [120, 855, 436, 400, 886, 446], "dark", r=14)
    d.cyl("socket", [205, 870, 445], [205, 870, 450], 18, "metal#c9ccd0", copies=[[130, 0, 0]])
    d.cyl("socket-in", [205, 870, 449], [205, 870, 451], 8, "black#141517", copies=[[130, 0, 0]])
    d.decal("strip-text", [180, 870, 446.5], [22, 5], "front", "plastic#c9ccd0", soft=True, copies=[[130, 0, 0]])
    # head: white box, sloped grey label panel at the front
    d.slab("head", "side", "M 40 905 L 462 905 L 462 935 L 420 1100 L 40 1100 Z", [45, 475], "shell", r=22)
    t = rot("x", -14.3, [260, 935, 462])
    d.box("label", [68, 940, 458, 452, 1088, 465], "label", r=4, rot=t)
    z = 465.5
    d.decal("title", [260, 1078, z], [160, 6], "front", "plastic#55595f", soft=True, rot=t)
    d.decal("led-win", [150, 1040, z], [40, 22], "front", "plastic#2a2c30", soft=True, rot=t, copies=[[200, 0, 0]])
    d.decal("led", [150, 1040, z + 0.4], [24, 12], "front", "plastic#b8443c", soft=True, rot=t, copies=[[200, 0, 0]])
    d.decal("bar", [205, 1035, z], [5, 26], "front", "gloss#2f7fd0", soft=True, rot=t, copies=[[200, 0, 0]])
    d.decal("lamps", [150, 1005, z], [55, 5], "front", "plastic#8a9097", soft=True, rot=t, copies=[[200, 0, 0]])
    d.decal("key", [100, 968, z], [18, 9], "front", "plastic#4d6f9a", soft=True, rot=t,
            copies=[[24 * k, 0, 0] for k in range(1, 6)] + [[200 + 24 * k, 0, 0] for k in range(0, 6)])
    d.decal("key-row2", [195, 990, z], [18, 9], "front", "plastic#ffffff", soft=True, rot=t, copies=[[0, 18, 0], [200, 0, 0], [200, 18, 0]])
    d.box("power", [40, 925, 220, 47, 990, 330], "black#141517", r=6)
    d.decal("power-sw", [39, 960, 245], [22, 30], "left", "gloss#2e9a4a", soft=True)
    d.decal("power-sock", [39, 960, 295], [30, 30], "left", "plastic#2a2c30", soft=True)
    vent_dots(d, 45, 1075, 80, "plastic#9aa0a6", [0, 80, 160])
    u_handle(d, 60, 55, 772, 110, 400, 32, "gloss#f0a040", "plastic#c4c8cd")
    d.save()

lc5(); czr2()
