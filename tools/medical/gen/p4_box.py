"""Pneumatic compression desk units: XY-K-LC-2 (box chassis) and XY-K-WIC-1 (2 knobs).
Writes only xy-k-lc-2.json and xy-k-wic-1.json."""
import sys, math
from lib import *
from p4lib import *

def lc2():
    d = D("xy-k-lc-2", [480, 380, 290], {"shell": "gloss#f2f3f3", "blue": "gloss#2f6fd8", "panel": "plastic#e4e6e8",
                                          "dark": "plastic#2a2c30", "grey": "plastic#c9cdd2"})
    d.box("body", [8, 0, 0, 472, 286, 310], "plastic#e9ebee", r=22)
    # the bezel bows forward: its front is an arc in plan, 28 mm proud at the middle
    Z0, BOW = 352, 28
    def zf(x, off=0.0):
        return Z0 + off + BOW * (1 - ((x - 240) / 240) ** 2)
    def bowed(x0, x1, off0, off1, n=24):
        """Plan outline (top plane: a = x, b = z) of a strip of the bowed front between offsets off0 < off1."""
        xs = [x0 + (x1 - x0) * k / n for k in range(n + 1)]
        return poly([(x, zf(x, off1)) for x in xs] + [(x, zf(x, off0)) for x in xs[::-1]])
    d.slab("lip", "top", bowed(0, 480, -80, 0), [0, 30], "shell", r=10)
    d.slab("recess", "top", bowed(10, 470, -80, -30), [26, 80], "shell", r=4)
    d.slab("bezel", "top", bowed(0, 480, -80, 0), [76, 290], "shell", r=20)
    # blue U line: down the left, along the bottom of the panel, up the right (none across the top)
    d.slab("u-left", "top", bowed(58, 74, -3, 1.2), [86, 290], "blue", r=1, soft=True)
    d.slab("u-right", "top", bowed(406, 422, -3, 1.2), [86, 290], "blue", r=1, soft=True)
    d.slab("u-bottom", "top", bowed(58, 422, -3, 1.2), [86, 99], "blue", r=1, soft=True)
    # recessed light-grey label panel with white margins, the top margin wider
    d.slab("panel", "top", bowed(88, 392, -6, 0.6), [112, 250], "panel", r=2)
    def z(x): return zf(x, 0.9)
    d.decal("logo", [128, 236, z(128)], [36, 11], "front", "blue", soft=True)
    d.decal("title", [150, 218, z(150)], [84, 8], "front", "plastic#3a3f45", soft=True)
    d.decal("subtitle", [150, 205, z(150)], [92, 4], "front", "plastic#6b7077", soft=True, copies=[[0, -9, 0]])
    d.decal("led-win", [205, 214, z(205)], [44, 24], "front", "dark", soft=True, copies=[[48, 0, 0]])
    d.decal("led-win3", [290, 214, z(290)], [24, 24], "front", "dark", soft=True)
    d.decal("digit", [194, 214, z(205) + 0.3], [8, 15], "front", "plastic#d8392e", soft=True, repeat=rep(3, [11, 0, 0]), copies=[[48, 0, 0]])
    d.decal("digit3", [290, 214, z(290) + 0.3], [8, 15], "front", "plastic#d8392e", soft=True)
    d.decal("led-label", [205, 230, z(205)], [10, 3], "front", "plastic#6b7077", soft=True, copies=[[48, 0, 0], [85, 0, 0]])
    d.cyl("lamp", [190, 190, z(190) - 1], [190, 190, z(190)], 9, "plastic#9aa0a8", soft=True,
          repeat=rep(4, [8, 0, 0]), copies=[[0, -11, 0]])
    d.cyl("lamp-r", [238, 190, z(238) - 1], [238, 190, z(238)], 9, "plastic#9aa0a8", soft=True, copies=[[14, 0, 0]])
    d.decal("legs-out", [215, 160, z(215)], [80, 14], "front", "plastic#40454c", soft=True)
    d.decal("legs", [215, 160, z(215) + 0.2], [76, 10], "front", "plastic#fbfbfb", soft=True)
    d.lathe("knob", [296, 158, z(296) - 1], [[0, 0], [20, 0], [20, 14], [17, 18], [0, 18]], "metal#cfd2d6", axis="z")
    d.box("key", [348, 200.5, z(348) - 2, 368, 213.5, z(348) + 2.5], "blue", r=3, copies=[[28, 0, -1.5], [0, -20, 0], [28, -20, -1.5], [0, -40, 0]])
    d.box("key-red", [376, 160.5, z(386) - 2, 396, 173.5, z(386) + 2.5], "gloss#e0302a", r=3)
    # lower recessed strip: 2 multi-pin hose connectors (white housing, navy slot, red pins) and the name
    d.box("conn", [82, 40, 342, 158, 66, 352], "plastic#e7e9ec", r=4, copies=[[234, 0, 0]])
    d.box("conn-slot", [88, 46, 347, 152, 60, 353], "plastic#3d4a63", r=3, copies=[[234, 0, 0]])
    d.cyl("conn-pin", [100, 53, 352], [100, 53, 354], 6, "gloss#c9302a", soft=True, repeat=rep(4, [13, 0, 0]), copies=[[234, 0, 0]])
    d.decal("name", [240, 50, zf(240, -30) + 0.5], [100, 6], "front", "plastic#a9aeb4", soft=True)
    # handle recesses on both sides
    d.box("grip", [470, 200, 70, 475, 268, 170], "black#151618", r=3, mirror="x")
    d.save()

def wic1():
    d = D("xy-k-wic-1", [400, 330, 200], {"shell": "plastic#ece8de", "band": "plastic#9fc0e6", "frame": "gloss#9fc0e6",
                                           "face": "plastic#e6e8ea", "dark": "plastic#4a4f57", "knob": "plastic#f4f4f2"})
    d.add("band", "slab", "band", plane="top", box=[8, 7, 8, 392, 30, 322], radii=[40], r=8)
    d.add("foot", "slab", "band", plane="top", box=[14, 0, 14, 74, 10, 74], radii=[24], r=4,
          copies=[[312, 0, 0], [0, 0, 242], [312, 0, 242]])
    # lower shell: a slightly wider skirt under the seam ridge
    d.add("skirt", "slab", "shell", plane="top", box=[-3, 26, -3, 403, 60, 333], radii=[34], r=10)
    prof = ("M 0 26 L 322 26 Q 330 26 330 34 L 330 56 Q 330 60 327 63 L 184 183 Q 180 186 175 186 "
            "L 10 186 Q 0 186 0 176 Z")
    d.slab("body", "side", prof, [0, 400], "shell", r=28)
    # raised hump over the back of the top: wide, sloping shoulders, fading out toward the front
    d.slab("hump", "front", poly([(36, 178), (364, 178), (318, 201), (82, 201)]), [8, 168], "shell", r=10)
    t = rot("x", -50, [200, 60, 330]); B = -32
    d.slab("frame", "front", poly(arch_pts(50, 350, 65, 100)) + " " + poly(arch_pts(70, 330, 70, 100)), [328, 342], "frame", r=3, rot=t)
    d.slab("face", "front", poly(arch_pts(70, 330, 68, 100)), [328, 337], "face", r=1, rot=t)
    d.slab("dark", "front", "M 70 68 L 330 68 L 330 128 Q 200 150 70 122 Z", [328, 338], "dark", r=1, rot=t)
    for nm, (x, y) in (("knob-p", (125, 125)), ("knob-t", (235, 148))):
        d.lathe(nm, [x, y, 337], [[0, 0], [30, 0], [30, 3], [29, 15], [27, 18], [0, 18]], "knob", axis="z", sides=18, rot=t)
        # grip ridge across the knob, turned to ~11 o'clock (drawn as a bar in the tilted face's world coords)
        a, th = math.radians(-50), math.radians(140)
        def tw(px, py, pz):
            return [px, 60 + (py - 60) * math.cos(a) - (pz - 330) * math.sin(a), 330 + (py - 60) * math.sin(a) + (pz - 330) * math.cos(a)]
        dx, dy = 26 * math.cos(th), 26 * math.sin(th)
        d.bar(nm + "-grip", tw(x - dx, y - dy, 359), tw(x + dx, y + dy, 359), [12, 10], "knob", r=4.5)
    d.decal("title", [200, 216, 337.5], [110, 8], "front", "plastic#3a3f45", soft=True, rot=t)
    d.decal("subtitle", [200, 205, 337.5], [90, 5], "front", "plastic#6b7077", soft=True, rot=t)
    d.slab("scale-p", "front", band(arc(125, 125, 38, -40, 120, 16), 2.2), [337, 337.6], "gloss#2f7fd8", soft=True, rot=t)
    d.decal("tick", [235, 175, 337.5], [3, 4], "front", "plastic#3a3f45", soft=True, rot=t,
            copies=[[38 * math.cos(math.radians(g)), 38 * math.sin(math.radians(g)) - 27, 0] for g in range(-30, 211, 30)])
    d.decal("logo", [200, 80, 338.5], [44, 8], "front", "plastic#8fb4e6", soft=True, rot=t)
    d.decal("labels", [125, 86, 338.5], [36, 5], "front", "plastic#d9dce0", soft=True, rot=t, copies=[[110, 0, 0]])
    d.cyl("hose-socket", [398, 60, 240], [406, 60, 240], 26, "plastic#b9bdc2")
    d.cyl("hose-hole", [404, 60, 240], [407, 60, 240], 12, "plastic#3a3f45")
    d.save()

lc2(); wic1()
