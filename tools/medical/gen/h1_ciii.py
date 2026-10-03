from h1lib import *
# XY-SL-CIII full-body massage bathtub: rectangular white tub on brass feet, front skirt with a raised panel moulding,
# flat rim, contoured basin with a headrest at the left, valves + hand shower + panel at the right (foot) end, a stainless
# pole at the right back corner with a white box showing two red LED windows. Tub 900 high (printed), pole to ~1420.
d = D("xy-sl-ciii", [2280, 950, 1420], {
    "shell": "gloss#f6f7f8", "inner": "gloss#eef1f4", "line": "plastic#dfe3e7", "brass": "metal#c8a24c",
    "hose": "plastic#f1efe6", "led": "black#1e1f22", "red": "gloss#e0262a", "panel": "plastic#c6ccd3"})
RY, RT = 830, 70
d.slab("skirt", "top", ring(rr(12, 12, 2268, 938, 14), rr(60, 60, 2220, 890, 40)), [70, RY + 5], "shell", r=12)
d.box("plinth", [30, 60, 30, 2250, 100, 925], "line", r=8)
hole = rr(110, 105, 1890, 845, 140)
tub(d, "", None, hole, rr(0, 0, 2280, 950, 18), RY, RT, 470, rr(60, 60, 1960, 890, 100), rim_r=18)
# Review 2026-10-02: the raised panel spans nearly the whole front (photo margins ~4 %), 125-760 high
d.box("panel", [95, 125, 935, 2170, 760, 946], "shell", r=12)
d.box("panel-line", [85, 115, 932, 2180, 770, 940], "line", r=8, soft=True)
d.cyl("foot", [300, 0, 120], [300, 72, 120], 46, "brass", copies=[[1550, 0, 0], [0, 0, 710], [1550, 0, 710]])
# inside: headrest moulding at the left, white flexible hose, white grab handle on the back wall
d.box("headrest", [115, 470, 300, 330, 760, 650], "inner", r=90, puff=10)
d.tube("hose-in", [[1870, 860, 790], [1700, 640, 760], [1300, 520, 600], [1000, 520, 400], [700, 600, 200], [500, 800, 110]],
       34, "hose", bend=220, soft=True)
d.lathe("hose-head", [1420, 470, 700], [[0, 0], [45, 0], [45, 60], [30, 70], [0, 70]], "hose")
d.cyl("handle", [1050, 730, 112], [1300, 730, 112], 32, "hose")
d.box("handle-mount", [1040, 710, 105, 1070, 750, 125], "hose", r=8, copies=[[230, 0, 0]])
# right (foot) end rim: lever valves back and front, a small control panel, hand shower lying at the back
T = RY + RT
for nm, x, z, a in (("v1", 1975, 150, 110), ("v2", 2140, 150, 110), ("v3", 1975, 800, 70), ("v4", 2140, 800, 70)):
    valve(d, nm, x, T - 4, z, disc=95, lever=75, ang=a)
d.box("ctrl", [1985, T - 4, 400, 2190, T + 8, 560], "panel", r=10)
d.lathe("ctrl-btn", [2030, T + 8, 440], [[0, 0], [16, 0], [16, 8], [0, 9]], "chrome", repeat=rep(3, [55, 0, 0]),
        copies=[[0, 0, 80]])
d.lathe("spout-base", [2080, T - 4, 120], [[0, 0], [30, 0], [30, 50], [22, 60], [0, 60]], "chrome")
d.tube("spout", [[2080, T + 40, 120], [1990, T + 50, 120], [1870, T + 45, 125]], 30, "chrome", bend=30)
# pole with the LED display box at the right back corner
d.cyl("pole", [2215, T - 4, 70], [2215, 1290, 70], 26, "chrome")
d.lathe("pole-base", [2215, T - 4, 70], [[0, 0], [30, 0], [30, 8], [16, 16], [0, 16]], "chrome")
d.lathe("pole-knob", [2215, 1250, 95], [[0, 0], [16, 0], [16, 34], [0, 34]], "led", axis="z")
d.box("display", [2080, 1285, 40, 2275, 1420, 100], "shell", r=10)
from p1lib import text
d.box("led-win", [2088, 1313, 99, 2172, 1368, 103], "led", r=2, copies=[[96, 0, 0]], soft=True)
for k, x in enumerate((2098, 2194)):
    text(d, f"led{k}", "88", [x, 1320, 103.5], 40, "red", gap=0.4, stroke=6)
d.box("display-logo", [2090, 1392, 99, 2135, 1402, 102], "gloss#2f6fd8", r=1, soft=True)
d.save()
