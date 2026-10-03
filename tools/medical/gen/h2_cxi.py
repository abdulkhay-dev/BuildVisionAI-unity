from h2lib import *
# XY-SL-CXI ozone spa bath (photo front-right, head/controls at the RIGHT end): white glossy tub, rim lip with a seam,
# bulging body tapering to a rounded bottom, 4 short white legs, open basin shifted left, two chrome grab bars,
# valves / operation panel / hand shower at the right end, light-blue band with jet dots near the right end of the front,
# blue logo at the left of the front, a soft moulding line.
W, DP = 1970, 800
RY, RT = 792, 58                 # rim lip: 792..850
d = D("xy-sl-cxi", [W, DP, 990], {
    "shell": "gloss#f7f8f9", "inner": "gloss#eef1f4", "seam": "plastic#d9dde2", "blue": "gloss#2f6fd0",
    "band": "gloss#9cb4e8", "dot": "gloss#e8ecf4", "water": "acrylic#cfe4f0a0", "panel": "plastic#8e959e"})
d.loft("body", [sec(110, 1780, 640, 180, W / 2, DP / 2), sec(250, 1900, 740, 205, W / 2, DP / 2),
                sec(450, 1956, 790, 218, W / 2, DP / 2), sec(700, 1956, 790, 216, W / 2, DP / 2),
                sec(RY, 1946, 782, 212, W / 2, DP / 2)], "shell", dome="start", domeH=45)
d.slab("seam", "top", P(rr(14, 14, W - 14, DP - 14, 208)), [RY - 8, RY + 1], "seam", r=2)
hole = rr(110, 120, 1640, 680, [120, 120, 200, 200])
tub(d, "", None, hole, rr(0, 0, W, DP, 220), RY, RT, 410, offset(hole, 30), rim_r=24)
# legs
d.lathe("leg", [380, 0, 170], [[0, 0], [27, 0], [30, 60], [36, 130], [0, 130]], "shell",
        copies=[[W - 760, 0, 0], [0, 0, DP - 340], [W - 760, 0, DP - 340]])
T = RY + RT
# grab bars: front rim (left quarter) and back rim (60 %)
bar_handle(d, "grab-front", [330, T - 2, 740], [630, T - 2, 740], [0, 105, 0], dia=26)
bar_handle(d, "grab-back", [1000, T - 2, 60], [1320, T - 2, 60], [0, 105, 0], dia=26)
d.lathe("grab-foot", [330, T - 2, 740], [[0, 0], [24, 0], [24, 10], [0, 10]], "chrome",
        copies=[[300, 0, 0], [670, 0, -680], [990, 0, -680]])
# right end controls
valve(d, "valve1", 1350, T - 2, 742, disc=70, lever=60, ang=180)
d.box("valve2", [1455, T - 2, 712, 1515, T + 46, 772], "chrome", r=8)
d.box("valve2-top", [1450, T + 40, 707, 1520, T + 56, 777], "chrome", r=6)
d.box("panel", [1610, T - 2, 630, 1870, T + 16, 770], "chrome", r=6)
d.box("panel-face", [1625, T + 10, 645, 1855, T + 20, 755], "panel", r=4)
d.decal("panel-led", [1700, T + 20.5, 700], [70, 36], "top", "screen", soft=True)
d.box("valve3", [1700, T - 2, 380, 1770, T + 50, 450], "chrome", r=8)
d.box("valve3-top", [1695, T + 44, 375, 1775, T + 58, 455], "chrome", r=6)
d.lathe("shower-base", [1800, T - 2, 150], [[0, 0], [38, 0], [38, 10], [20, 18], [0, 18]], "chrome")
d.cyl("shower-post", [1800, T, 150], [1800, 960, 150], 30, "chrome")
d.box("shower-head", [1778, 945, 120, 1822, 990, 230], "chrome", r=12)
d.cyl("shower-nozzle", [1800, 960, 230], [1800, 930, 245], 22, "chrome")
# light-blue band with jet dots near the right end of the front
up = "M 1460 782 L 1752 782 L 1752 560 Q 1751 500 1746 450 L 1621 450 Q 1590 610 1460 782 Z"
lo = "M 1621 456 L 1746 456 Q 1736 380 1722 300 L 1718 246 L 1634 246 L 1636 300 Q 1640 400 1621 456 Z"
lo2 = "M 1634 254 L 1718 254 L 1714 140 L 1630 140 Z"
d.slab("band", "front", up, [DP - 8, DP + 1.5], "band", r=1)
d.slab("band-lo", "front", lo, [DP - 8, DP + 1.5], "band", r=1, rot=rot("x", 8, [0, 450, DP]))
d.slab("band-lo2", "front", lo2, [764, 773.5], "band", r=1, rot=rot("x", 20, [0, 250, 772]))
for i, (x, y) in enumerate([(1500, 750), (1570, 680), (1612, 590), (1632, 490), (1640, 390), (1640, 290),
                            (1640, 180), (1738, 740), (1738, 610), (1734, 480), (1722, 360), (1712, 250), (1706, 170)]):
    z = DP + 1 - min(200, max(0, 450 - y)) * 0.139 - max(0, 250 - y) * 0.36
    d.lathe(f"jet{i}", [x, y, z], [[0, 0], [8, 0], [8, 2], [0, 4]], "dot", axis="z", soft=True)
# logo
logo_round(d, "logo", [370, 630, DP + 1], 104)
text(d, "logo-t1", "XIANGYU", [440, 640, DP + 1.5], 46, "blue")
text(d, "logo-t2", "MEDICAL", [440, 570, DP + 1.5], 46, "blue")
# soft moulding line sweeping down from the left top across the front
d.tube("moulding", [[70, 760, DP - 22], [180, 640, DP - 6], [380, 470, DP - 4], [620, 420, DP - 4], [900, 412, DP - 4]],
       7, "plastic#e3e6ea", bend=150, soft=True)
d.save()
