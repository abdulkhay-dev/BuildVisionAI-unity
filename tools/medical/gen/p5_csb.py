"""Ultrasound therapy XY-K-CSB-I (one probe, segment LCD) and XY-K-CSB-II (two probes, colour touch screen):
one pillow-shaped desk housing. Writes only xy-k-csb-i.json and xy-k-csb-ii.json."""
from p5lib import *

W, DP, H = 380, 310, 135
CX = W / 2

def build(id_, two):
    d = D(id_, [W, DP, H], {"blue": "plastic#96bdea", "shell": "gloss#f2f3f5", "glass": "gloss#111214",
                            "pill": "gloss#9cc3ec", "metal": "metal#a9adb3", "probe": "gloss#8fb9e8",
                            "grey": "plastic#9a9ea4", "cable": "rubber#8e9297"})
    # light-blue lower tub, sides bulging out towards the top
    d.loft("tub", [sec(0, 326, 258, 64, CX, DP / 2), sec(16, 358, 290, 76, CX, DP / 2),
                   sec(45, 376, 306, 82, CX, DP / 2), sec(72, 378, 308, 84, CX, DP / 2)], "blue")
    # white upper shell with a lip all round, soft top edge
    d.loft("shell", [sec(68, 380, 310, 85, CX, DP / 2), sec(80, 378, 308, 84, CX, DP / 2),
                     sec(108, 374, 304, 83, CX, DP / 2), sec(120, 366, 296, 79, CX, DP / 2),
                     sec(127, 354, 284, 73, CX, DP / 2), sec(131, 336, 266, 64, CX, DP / 2)], "shell")
    # black glass on the rear ~55 % of the top
    zf = 176
    d.slab("glass", "top", rrect(30, 28, W - 30, zf, [58, 22, 22, 58]), [129.5, 132.4], "glass", r=1.2)
    # display (segment LCD / colour touch screen)
    # the screen picture covers the panel's printed area (logo, title, display) down to the knob's edge
    # (review: the crop's knob ring is aligned to the real knob, measured on the crops and photos)
    x0, x1, z0, z1 = (CX - 55, CX + 118, 108, 190) if not two else (CX - 38, CX + 162, 96, 205)
    d.add("lcd", "screen", "glass", box=[x0, 132.6, z1 - 3, x1, 132.6 + (z1 - z0), z1], r=2, face="front",
          bezel=1, print=f"med_{id_}_screen", rot=rot("x", -90, [CX, 132.6, z1]))
    d.decal("txt-l", [80, 132.6, 160], [60, 3], "top", "plastic#8a8e94", soft=True, copies=[[0, 0, 6]])
    # central encoder: concentric shallow rings, a white raised collar, black knob
    KZ = 205
    d.lathe("ring2", [CX, 130.6, KZ + 8], [[0, 0], [64, 0], [64, 0.6], [0, 0.6]], "plastic#f3f4f6", soft=True)
    d.lathe("collar", [CX, 130, KZ], [[0, 0], [35, 0], [34, 6], [30, 8], [0, 8]], "shell")
    d.lathe("knob", [CX, 137, KZ], [[0, 0], [22, 0], [22, 10], [20, 12], [0, 12]], "gloss#16171a")
    d.cyl("knob-dot", [CX, 148.5, KZ], [CX, 149.5, KZ], 5, "plastic#6a6e74", soft=True)
    # two light-blue pill keys
    d.box("key-l", [72, 130, 206, 118, 134.5, 224], "pill", r=8)
    d.box("key-r", [W - 120, 130, 246, W - 74, 134.5, 264], "pill", r=8)
    # probe holder(s) + probe(s): right side (and mirrored left on CSB-II)
    kw = {"mirror": "x"} if two else {}
    d.box("hook-arm", [W - 6, 66, 108, W + 48, 70, 192], "metal", r=2, **kw)
    d.box("hook-lip", [W + 44, 66, 108, W + 48, 100, 192], "metal", r=2, **kw)
    d.box("hook-plate", [W - 4, 50, 98, W + 1, 104, 202], "metal", r=3, **kw)
    px, pz = W + 26, 150
    tilt = rot("z", -22, [px, 40, pz])
    d.lathe("probe", [px, 16, pz], [[0, 0], [10, 0], [12, 40], [15, 80], [19, 112], [25, 130], [27, 145],
                                    [25, 160], [18, 172], [8, 177], [0, 178]], "probe", rot=tilt, **kw)
    d.cyl("probe-face", [px + 19, 166, pz], [px + 28, 166, pz], 34, "grey", rot=tilt, **kw)
    d.tube("sleeve", [[px - 8, 20, pz], [px - 11, 5, pz]], 17, "probe", rib=3, pitch=6, soft=True, **kw)
    d.tube("cable", [[px - 11, 6, pz], [px - 10, 4, pz - 30], [px + 4, 4, pz - 80], [px + 8, 4, 10]], 7, "cable",
           bend=30, soft=True, **kw)
    d.save()

build("xy-k-csb-i", False)
build("xy-k-csb-ii", True)
