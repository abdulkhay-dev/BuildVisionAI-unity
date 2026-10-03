from h1lib import *
# XY-SL-BI seated tub for the hands/arms: white tub body tapering to a rounded bottom, standing on a pedestal at the left
# and a round leg at the right (the seated patient's knees go under it); thick rounded rim with a wide L-shaped deck at
# the front left (valve, LCD keypad, valve, hand shower diagonally from back-left to front-right); raised back wall at
# the back left and a thick rolled collar that dips into the basin where the patient's chest rests; water inside.
# Review 2026-10-02: pedestal + leg instead of a full plinth (open under the tub), body/rim/pedestal proportions from the
# photo, wide left deck, rolled chest collar curving into the basin, controls placed as in the photo.
d = D("xy-sl-bi", [1000, 750, 900], {
    "shell": "gloss#f7f8f9", "inner": "gloss#eef2f5", "water": "acrylic#cfe9f2a8", "grey": "plastic#b9bfc6",
    "lcd": "plastic#cfc9dc", "dark": "black#2a2d31"})
CX, CZ = 500, 390
RY, RT = 680, 85
RTOP = RY + RT
d.loft("bowl", [sec(300, 740, 540, 110, CX, CZ), sec(345, 770, 575, 105, CX, CZ)], "shell", dome="start", domeH=40)
d.loft("body", [sec(345, 770, 575, 105, CX, CZ), sec(RY + 10, 900, 665, 100, CX, CZ)], "shell", caps=False)
# pedestal (left) and leg (right)
d.box("pedestal", [130, 0, 170, 470, 330, 600], "shell", r=30)
d.cyl("leg", [770, 0, 520], [770, 330, 520], 60, "shell")
d.lathe("leg-foot", [770, 0, 520], [[0, 0], [36, 0], [36, 12], [0, 12]], "grey")
hole = rr(270, 120, 900, 515, [90, 60, 60, 120])
tub(d, "", None, hole, rr(30, 40, 970, 740, 120), RY, RT, 450, rr(100, 95, 900, 685, 90), water=RY + 40)
d.loft("lip", [sec(RY - 18, 902, 667, 100, CX, CZ), sec(RY - 10, 908, 673, 102, CX, CZ)], "inner", caps=False)
# raised back wall at the back left, its right end sweeping down into the collar
d.slab("back-wall", "front", "M 60 750 L 60 820 Q 60 845 90 845 L 470 845 Q 560 845 610 770 L 610 750 Z", [42, 130], "shell", r=35)
# thick rolled collar: from the back left, dipping forward into the basin (chest rest) and back to the right back rim
d.tube("collar", [[90, RTOP + 45, 90], [470, RTOP + 50, 95], [600, RTOP + 20, 170], [720, RTOP + 5, 225],
                  [830, RTOP + 15, 160], [890, RTOP + 5, 90], [950, RTOP - 10, 80]], 80, "shell", bend=110)
# deck controls
valve(d, "valve-l", 125, RTOP - 6, 420, disc=130, ang=40)
d.box("panel", [150, RTOP - 6, 545, 345, RTOP + 14, 690], "grey", r=10)
d.add("lcd", "screen", box=[175, RTOP + 8, 570, 320, RTOP + 16, 665], r=4, face="top", bezel=4, mat="lcd")
valve(d, "valve-r", 380, RTOP - 6, 640, disc=130, ang=-40)
d.lathe("shower-base", [500, RTOP - 6, 640], [[0, 0], [30, 0], [30, 10], [14, 18], [0, 18]], "chrome")
d.cyl("shower", [500, RTOP + 10, 640], [500, RTOP + 130, 640], 26, "chrome", d2=34)
d.decal("shower-strip", [500, RTOP + 85, 657.5], [10, 90], "front", "gloss#3a7fd0", soft=True)
d.save()
