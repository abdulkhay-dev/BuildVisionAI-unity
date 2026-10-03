from h1lib import *
# XY-SL-BII lower-limb tub: white box tub, broad front rim with valves + LCD keypad, seat with backrest at the back right
d = D("xy-sl-bii", [1000, 750, 1020], {
    "shell": "gloss#f6f7f8", "inner": "gloss#eef2f5", "dark": "black#2a2d31", "seat": "plastic#f2f2f2",
    "frame": "metal#c9ccd0", "brass": "metal#c9a04a", "line": "plastic#d9dde2"})
X0, X1, Z0, Z1 = 20, 800, 100, 730         # body
RY, RT = 600, 70                            # rim bottom, thickness
d.loft("body", [sec(30, X1 - X0 - 20, Z1 - Z0 - 20, 70, (X0 + X1) / 2, (Z0 + Z1) / 2),
                sec(60, X1 - X0, Z1 - Z0, 70, (X0 + X1) / 2, (Z0 + Z1) / 2),
                sec(RY + 10, X1 - X0, Z1 - Z0, 70, (X0 + X1) / 2, (Z0 + Z1) / 2)], "shell", caps=False)
hole = rr(100, 160, 720, 540, 90)
tub(d, "", None, hole, rr(X0 - 20, Z0 - 40, X1 + 40, Z1 + 20, 90), RY, RT, 260, rr(X0 + 15, Z0 + 15, X1 - 15, Z1 - 15, 60))
d.box("base", [X0 + 15, 10, Z0 + 15, X1 - 15, 40, Z1 - 15], "shell", r=20)
d.cyl("foot", [80, 0, 160], [80, 14, 160], 50, "dark", copies=[[660, 0, 0], [0, 0, 510], [660, 0, 510]])
# front: screwed service cover, rocker switch, brass fittings
d.box("cover", [70, 90, Z1 - 2, 560, 560, Z1 + 3], "shell", r=3)
d.box("cover-line", [64, 84, Z1 - 1, 566, 566, Z1 + 1], "line", r=2, soft=True)
d.decal("screw", [90, 110, Z1 + 3.5], [10, 10], "front", "line", repeat=rep(4, [150, 0, 0]), copies=[[0, 430, 0]], soft=True)
d.decal("screw-s", [90, 330, Z1 + 3.5], [10, 10], "front", "line", copies=[[450, 0, 0]], soft=True)
d.box("switch", [60, 220, Z1 - 2, 92, 290, Z1 + 10], "dark", r=3)
d.decal("switch-label", [76, 310, Z1 + 0.5], [20, 8], "front", "dark", soft=True)
d.tube("cable", [[90, 60, Z1], [90, 30, Z1 + 40], [40, 8, Z1 + 80], [-10, 8, Z1 + 90]], 12, "dark", bend=40, soft=True)
d.cyl("fit", [700, 210, Z1], [700, 210, Z1 + 30], 28, "brass", copies=[[0, -120, 0]])
d.cyl("fit-nut", [700, 210, Z1 + 30], [700, 210, Z1 + 44], 36, "brass", sides=6, copies=[[0, -120, 0]])
d.decal("fit-label", [700, 255, Z1 + 0.5], [36, 16], "front", "line", copies=[[0, -120, 0]], soft=True)
# rim controls (front band): valve left, LCD keypad centre, valve right
RTOP = RY + RT
valve(d, "valve-l", 165, RTOP - 6, 650, ang=60, disc=95)
valve(d, "valve-l2", 245, RTOP - 6, 650, ang=-60, disc=95)
valve(d, "valve-r", 640, RTOP - 6, 640, ang=-60)
d.add("panel", "screen", box=[300, RTOP - 8, 575, 540, RTOP + 4, 735], r=8, face="top", bezel=0, mat="line",
      print="med_xy-sl-bii_screen")
# hand shower: hose outlet at the left rim, handset lying on the left rim band
d.cyl("hose-out", [60, RTOP - 6, 420], [60, RTOP + 14, 420], 30, "chrome")
d.tube("hose", [[60, RTOP + 10, 420], [50, RTOP + 30, 330], [60, RTOP + 26, 220]], 14, "chrome", bend=60, soft=True)
d.cyl("handset", [60, RTOP + 18, 220], [60, RTOP + 22, 90], 34, "chrome", d2=48)
d.decal("handset-strip", [60, RTOP + 45, 160], [10, 90], "top", "gloss#3a7fd0", soft=True)
# seat at the back right: white moulded seat + backrest on a stainless post, T-leg base with black feet to the right
SX, SZ = 870, 150
d.cyl("seat-post", [SX, 40, SZ + 40], [SX, 650, SZ + 40], 40, "frame")
d.bar("seat-leg", [SX - 60, 30, SZ + 40], [1000, 30, SZ + 40], [45, 30], "frame", r=6)
d.bar("seat-leg2", [SX, 30, 0], [SX, 30, SZ + 250], [45, 30], "frame", r=6)
d.box("seat-foot", [960, 0, SZ + 15, 1000, 22, SZ + 65], "dark", r=6, copies=[[-130, 0, -155], [-130, 0, 205]])
d.box("seat", [SX - 150, 650, SZ - 90, SX + 130, 705, SZ + 150], "seat", r=22, puff=6)
d.bar("back-post", [SX, 670, 20], [SX, 820, 20], [45, 25], "frame", r=6)
d.slab("back-edge", "front", P(rr(SX - 174, 776, SX + 174, 1020, 62)), [-1, 8], "dark", r=4)
d.slab("back", "front", P(rr(SX - 170, 780, SX + 170, 1020, 60)), [0, 45], "seat", r=18)
d.save()
