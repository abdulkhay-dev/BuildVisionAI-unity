"""Steam beds HYZ-IIC (+ trolley), HYZ-IIF, HYZ-IIK (+ console), HYZ-IIB (+ console), HYZ-IA.
Head end at the left (x = 0 side) as in the photos; consoles stand left of the head end."""
import sys
from h3lib import *
Design = D

MATS = {"shell": "gloss#f6f7f8", "dark": "plastic#2e3238", "grey": "plastic#9ea4ab", "green": "gloss#2fb24a",
        "steel": "metal#c9ccd0"}


def sx(at, w, dd, r, cy, cz):
    """loft section for axis x: at = x, w across z, dd across y, centre (y = cy, z = cz)."""
    return {"at": at, "w": w, "d": dd, "r": r, "cx": cy, "cz": cz}


def z_surf(w, dd, r, cy, cz, y):
    hw, hd = w / 2, dd / 2
    dy = abs(y - cy)
    if dy <= hd - r: return cz + hw
    t = min(dy - (hd - r), r)
    return cz + hw - r + math.sqrt(max(r * r - t * t, 0))


def green_buttons(d, id, x, y, z, nx=2, ny=2, dx=50, dy=95, face="front", labels=True):
    d.lathe(id + "-ring", [x, y, z], [[0, 0], [17, 0], [17, 3], [0, 3]], "plastic#d8dadd", axis="z", soft=True,
            copies=[[i * dx, j * dy, 0] for i in range(nx) for j in range(ny)][1:])
    d.lathe(id, [x, y, z + 3], [[0, 0], [11, 0], [11, 6], [7, 10], [0, 10]], "green", axis="z", soft=True,
            copies=[[i * dx, j * dy, 0] for i in range(nx) for j in range(ny)][1:])
    if not labels: return
    d.box(id + "-lbl", [x - 14, y + 21, z, x + 14, y + 33, z + 1.2], "plastic#c9cdd2", soft=True,
          copies=[[i * dx, j * dy, 0] for i in range(nx) for j in range(ny)][1:])


def acrylic_bed(d, X, ZD=900, yl=690):
    """HYZ-IIC / IIF bed, 2000 long from x = X; returns the lid section used at the handle."""
    u = lambda v: X + v
    # base plate with a raised rim, grooves, feet
    plate = rr(u(210), 40, u(1880), ZD - 40, 300)
    d.slab("plate", "top", P(plate), [14, 72], "shell", r=22)
    d.slab("plate-rim", "top", ring(plate, offset(plate, -45)), [70, 84], "shell", r=7)
    d.box("groove", [u(300), 72, 160, u(600), 74, 166], "plastic#dfe2e5", soft=True, repeat=rep(6, [0, 0, 110]),
          copies=[[1110, 0, 0]])
    d.cyl("foot", [u(330), 0, 160], [u(330), 14, 160], 46, "grey",
          copies=[[0, 0, ZD - 320], [1400, 0, 0], [1400, 0, ZD - 320]])
    # pedestal with concave fillets up into the tub (front flush with the tub front)
    # review: the photo's top rim is a thick band (~110) from ~580 to ~690
    yt, yb = yl - 110, 330
    d.slab("pedestal", "front", f"M {u(640)} 80 L {u(1450)} 80 L {u(1450)} {yb - 90} Q {u(1460)} {yb} {u(1570)} {yb + 30} "
           f"L {u(530)} {yb + 30} Q {u(632)} {yb} {u(640)} {yb - 90} Z", [110, ZD - 40], "shell", r=40)
    # tub with bulging rounded ends
    d.slab("tub", "front", f"M {u(95)} {yt} C {u(40)} {yt} {u(35)} {yt - 150} {u(110)} {yt - 210} "
           f"C {u(210)} {yt - 280} {u(390)} {yb + 10} {u(560)} {yb} L {u(1560)} {yb} "
           f"C {u(1760)} {yb + 10} {u(1900)} {yb + 90} {u(1958)} {yt - 130} C {u(1990)} {yt - 60} {u(1985)} {yt} {u(1940)} {yt} Z",
           [40, ZD - 40], "shell", r=70)
    # ledge over the whole length; the head end an open shallow tray with a raised rim
    d.slab("ledge", "top", rrp(u(0), 22, u(2000), ZD - 22, 60), [yt - 2, yl], "shell", r=22)
    d.box("tray-rim", [u(0), yl - 4, 22, u(26), yl + 18, ZD - 22], "shell", r=9)
    d.box("tray-rim-f", [u(0), yl - 4, ZD - 48, u(330), yl + 18, ZD - 22], "shell", r=9, copies=[[0, 0, -(ZD - 70)]])
    # domed lid: tall, rounded at both ends, widest a little above the ledge
    cz, cy = ZD / 2, yl + 100
    # review: flat-ish head face (so the arched opening reads), dome only at the foot end
    secs = [sx(u(318), 690, 400, 190, cy - 35, cz), sx(u(340), 740, 445, 220, cy - 28, cz), sx(u(400), 760, 470, 235, cy - 20, cz), sx(u(560), 800, 540, 270, cy, cz), sx(u(800), 810, 560, 280, cy, cz),
            sx(u(1250), 810, 520, 260, cy - 10, cz), sx(u(1650), 800, 460, 230, cy - 20, cz),
            sx(u(1880), 760, 380, 190, cy - 30, cz)]
    d.loft("lid", secs, "shell", axis="x", dome="end", domeH=110)
    # head opening: dark recess on the rounded head end
    # review: the photos show an arched head opening (dark blue-grey inside) in the lid's head end
    d.slab("head-hole", "side", f"M {cz - 165} {yl + 1} L {cz + 165} {yl + 1} L {cz + 165} {yl + 120} "
           f"Q {cz + 165} {yl + 265} {cz} {yl + 265} Q {cz - 165} {yl + 265} {cz - 165} {yl + 120} Z",
           [u(314), u(470)], "plastic#566173", r=4)
    # chrome U handle on the lid front
    yh = yl + 100          # review: the photo's handle sits low on the lid front, ~100 above the rim
    zs = z_surf(810, 560, 280, cy, cz, yh) - 4
    d.tube("handle", [[u(930), yh, zs], [u(940), yh, zs + 46], [u(1170), yh, zs + 46], [u(1180), yh, zs]], 20, "chrome",
           bend=18)
    d.lathe("handle-base", [u(930), yh, zs - 2], [[0, 0], [17, 0], [17, 6], [11, 10], [0, 10]], "chrome", axis="z",
            copies=[[250, 0, 0]])
    # service door on the pedestal: raised panel, round embossed logo, small handle
    zf = ZD - 40
    # review: door and buttons placed as measured on the photo (door u 940-1250, y 150-500, its catch at the right
    # edge; the 2 x 2 green buttons left of it, rows at ~165 / ~235)
    d.box("door", [u(940), 150, zf - 6, u(1250), 500, zf + 8], "shell", r=14)
    d.box("door-panel", [u(962), 172, zf + 4, u(1228), 478, zf + 14], "shell", r=22)
    disc(d, "door-emb", [u(1095), 325, zf + 14], 52, "front", "gloss#e9ecef", t=3)
    d.box("door-emb-v", [u(1093), 287, zf + 16, u(1105), 345, zf + 18], "gloss#e3e6e9", soft=True)
    d.box("door-emb-h", [u(1062), 343, zf + 16, u(1126), 355, zf + 18], "gloss#e3e6e9", soft=True)
    d.box("door-handle", [u(944), 300, zf + 6, u(954), 352, zf + 20], "chrome", r=4)
    d.box("door-hinge", [u(1247), 200, zf - 2, u(1254), 232, zf + 10], "chrome", r=2, copies=[[0, 215, 0]])
    green_buttons(d, "btn", u(810), 165, zf, dx=75, dy=70)
    return yl


def trolley_iic(d, x0, z0, base_mat="plastic#4f5459", variant="iic", tw=15):
    """HYZ-IIC / IIB trolley, 440 wide from x0, 450 deep from z0 (front at z0 + 450); tw = the tower's inset each side."""
    x1 = x0 + 440
    Z = lambda v: z0 + v
    # dark-grey rear base
    d.slab("tr-base", "side", f"M {Z(5)} 70 L {Z(210)} 70 L {Z(210)} 520 Q {Z(5)} 520 {Z(5)} 330 Z", [x0 + tw - 9, x1 - tw + 9],
           base_mat, r=30)
    # white tower: S-curved front
    d.slab("tr-tower", "side", f"M {Z(190)} 70 L {Z(445)} 70 Q {Z(405)} 420 {Z(370)} 610 Q {Z(345)} 760 {Z(440)} 905 "
           f"L {Z(110)} 905 L {Z(110)} 520 Q {Z(110)} 470 {Z(190)} 470 Z", [x0 + tw, x1 - tw], "shell", r=40)
    # teardrop lighter panel on the front; review: in the photo it reaches from ~360 up under the top with a soft grey
    # outline. Upper part follows the S front (side slab 3 mm proud), the rounded bottom is a plate tilted with the front.
    xm, hw = (x0 + x1) / 2, (x1 - x0) / 2 - tw - 25
    def qz(p0, p1, p2, y):           # z on a quadratic (z, y) segment at height y (bisection on t)
        lo, hi = 0.0, 1.0
        for _ in range(40):
            t = (lo + hi) / 2
            yy = (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * p1[1] + t * t * p2[1]
            lo, hi = (t, hi) if yy < y else (lo, t)
        return (1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * p1[0] + t * t * p2[0]
    def front_z(y):
        return qz((445, 70), (405, 420), (370, 610), y) if y <= 610 else qz((370, 610), (345, 760), (440, 905), y)
    ys = [560 + 20 * k for k in range(17)]
    up = [(Z(front_z(y) + 3), y) for y in ys] + [(Z(300), 880), (Z(300), 560)]
    d.slab("tr-drop", "side", P(up), [xm - hw, xm + hw], "gloss#fdfdfe", soft=True)
    d.slab("tr-drop-line", "side", P([(Z(front_z(y) + 2), y) for y in ys] + [(Z(300), 880), (Z(300), 560)]),
           [xm - hw - 3, xm + hw + 3], "plastic#d6dade", soft=True)
    zb = Z(front_z(365))
    drop = f"M {xm - hw} 565 L {xm + hw} 565 Q {xm + hw} 380 {xm} 362 Q {xm - hw} 380 {xm - hw} 565 Z"
    tilt = -math.degrees(math.atan2(front_z(365) - front_z(565), 200))
    d.slab("tr-drop-low", "front", drop, [zb - 2, zb + 3], "gloss#fdfdfe", rot=rot("x", tilt, [0, 365, zb]), soft=True)
    d.slab("tr-drop-low-line", "front", drop.replace(" 362 ", " 359 ").replace(f"{xm - hw} ", f"{xm - hw - 3} ").replace(f"{xm + hw} ", f"{xm + hw + 3} "),
           [zb - 3, zb + 2], "plastic#d6dade", rot=rot("x", tilt, [0, 365, zb]), soft=True)
    # blue-grey control panel on the front at mid-height
    tp = rot("x", 12, [0, 905, Z(225)])
    top_ol = rp([(x0 - 15, Z(30)), (x1 + 15, Z(30)), (x1 + 15, Z(445)), ((x0 + x1) / 2, Z(395)), (x0 - 15, Z(445))],
                [40, 40, 60, 260, 60])
    if variant == "iic":
        # review: the photo's panel sits at ~465-665 with a rounded (D-shaped) bottom: green key, red LED, 3 keys
        zp = Z(front_z(465))
        cr = rot("x", -math.degrees(math.atan2(front_z(465) - front_z(665), 200)), [0, 465, zp])
        d.slab("tr-ctl", "front", f"M {x0 + 105} 665 L {x1 - 105} 665 L {x1 - 105} 540 Q {x1 - 105} 465 {xm} 465 "
               f"Q {x0 + 105} 465 {x0 + 105} 540 Z", [zp - 4, zp + 9], "plastic#3d5f86", r=4, rot=cr)
        d.box("tr-led", [xm - 30, 560, zp + 8, xm + 30, 592, zp + 11], "gloss#b03030", r=2, rot=cr)
        btn(d, "tr-gbtn", [xm, 632, zp + 9], 16, "front", "green", h=5, rot=cr)
        btn(d, "tr-key", [xm - 42, 505, zp + 9], 14, "front", "plastic#e8eaec", h=4, rot=cr, copies=[[42, 0, 0], [84, 0, 0]])
        d.box("tr-ctl-txt", [x0 + 125, 615, zp + 9, x0 + 165, 619, zp + 10], "plastic#a9bdd3", soft=True, rot=cr)
        # wide dark-grey top with a concave front edge, sloping to the front, light-blue display panel
        d.slab("tr-top", "top", top_ol, [905, 965], "plastic#55595f", r=18, rot=tp)
        d.box("tr-disp", [x0 + 70, 964, Z(150), x1 - 70, 967, Z(330)], "gloss#a8cdea", r=8, rot=tp)
        d.box("tr-disp-led", [x0 + 110, 966, Z(200), x1 - 110, 968, Z(240)], "gloss#4a5a6a", r=2, rot=tp)
        d.box("tr-disp-key", [x0 + 110, 966, Z(270), x0 + 140, 969, Z(295)], "gloss#e8c330", r=3, rot=tp,
              copies=[[45, 0, 0], [90, 0, 0], [135, 0, 0], [180, 0, 0]])
        d.box("tr-sw", [x1 - 45, 964, Z(80), x1 - 15, 975, Z(110)], "plastic#2b2f33", r=4, rot=tp)
    else:
        # white saddle top, dark-blue framed panel with 3 red LED windows and 6 blue keys, green lamps and switch
        d.slab("tr-top", "top", top_ol, [905, 975], "shell", r=22, rot=tp)
        d.box("tr-frame", [x0 + 60, 974, Z(150), x1 - 40, 977, Z(360)], "gloss#24479a", r=10, rot=tp)
        d.box("tr-face", [x0 + 68, 976, Z(158), x1 - 48, 978, Z(352)], "gloss#e9eef6", r=8, rot=tp)
        d.box("tr-led", [x0 + 150, 977, Z(190), x0 + 200, 979.5, Z(225)], "gloss#8a2020", r=2, rot=tp,
              copies=[[70, 0, 0], [140, 0, 0]])
        d.box("tr-key", [x0 + 90, 977, Z(290), x0 + 122, 980, Z(322)], "gloss#2f6fd0", r=4, rot=tp,
              repeat={"n": 6, "step": [44, 0, 0]})
        d.box("tr-band", [x0 + 68, 977, Z(250), x1 - 48, 978.6, Z(258)], "gloss#24479a", soft=True, rot=tp)
        btn(d, "tr-lamp", [x0 + 25, 975, Z(170)], 14, "top", "green", h=5, rot=tp, copies=[[0, 0, 60]])
        d.box("tr-sw", [x1 - 32, 974, Z(150), x1 - 8, 984, Z(176)], "gloss#2fae4a", r=3, rot=tp)
    casters(d, "tr-castor", [(x0 + 50, Z(60)), (x1 - 50, Z(60)), (x0 + 50, Z(400)), (x1 - 50, Z(400))], 55)


def hyz_iif():
    d = Design("hyz-iif", [2000, 900, 1100], dict(MATS))
    yl = acrylic_bed(d, 0)
    # blue head tray + neck pad
    d.slab("tray-top", "top", rrp(24, 46, 330, 854, 30), [yl - 3, yl + 1], "plastic#7aa0d6")
    d.box("neck-pad", [50, yl, 260, 300, yl + 72, 640], "leather#6f97d8", r=26, puff=6)
    # stainless-framed control panel on the tub front, left of the pedestal door
    zt, x0, x1, y0, y1 = 860, 470, 880, 390, 560
    d.box("ctl-frame", [x0, y0, zt - 10, x1, y1, zt + 6], "steel", r=4)
    d.box("ctl-face", [x0 + 12, y0 + 10, zt + 5, x1 - 10, y1 - 10, zt + 8], "gloss#f4f6fa", r=2)
    d.slab("ctl-line", "front", rrp(x0 + 30, y0 + 22, x1 - 26, y1 - 22, 6) + " " + rrp(x0 + 33, y0 + 25, x1 - 29, y1 - 25, 4),
           [zt + 8, zt + 8.8], "plastic#2f5fb0", soft=True)
    d.slab("ctl-win", "front", rrp(0, 0, 44, 30, 4).replace("M ", "M ") and
           " ".join(rrp(x0 + 90 + 55 * k, y0 + 95, x0 + 134 + 55 * k, y0 + 125, 4) + " " +
                    rrp(x0 + 93 + 55 * k, y0 + 98, x0 + 131 + 55 * k, y0 + 122, 3) for k in range(4)),
           [zt + 8, zt + 8.8], "plastic#2f4f8a", soft=True)
    btn(d, "ctl-key", [x0 + 100, y0 + 52, zt + 8], 16, "front", "plastic#33405a", h=4, repeat=rep(5, [48, 0, 0]))
    d.box("ctl-sw", [x1 - 78, y0 + 92, zt + 8, x1 - 42, y0 + 134, zt + 18], "gloss#1c2420", r=3)
    d.box("ctl-sw-i", [x1 - 62, y0 + 104, zt + 18, x1 - 58, y0 + 122, zt + 19], "gloss#3fbf5a", soft=True)
    d.box("ctl-txt", [x0 + 60, y0 + 34, zt + 8, x1 - 120, y0 + 38, zt + 8.8], "plastic#6b7b99", soft=True, copies=[[0, 106, 0]])
    disc(d, "port", [130, 520, 860], 14, "front", "plastic#1d1f22", t=6)
    return d


def hyz_iic():
    d = Design("hyz-iic", [2600, 900, 1100], dict(MATS))
    acrylic_bed(d, 600)
    logo(d, "logo", [600 + 450, 470, 860], 95, "front")
    trolley_iic(d, 20, 225, tw=55)
    # light window patch on the lid top near the head
    d.sphere("window", [600 + 600, 1052, 450], None, "acrylic#a9cdeac8", radii=[150, 14, 190])
    return d


def console_iik(d, x0, z0):
    """HYZ-IIK console: 500 wide from x0, 450 deep from z0; sloped top panel framed blue, blue teardrop."""
    x1 = x0 + 500
    Z = lambda v: z0 + v
    d.slab("co-body", "side", f"M {Z(40)} 95 L {Z(440)} 95 L {Z(440)} 780 L {Z(345)} 1040 Q {Z(330)} 1095 {Z(290)} 1095 "
           f"L {Z(75)} 1095 Q {Z(30)} 1095 {Z(35)} 1050 Q {Z(140)} 600 {Z(40)} 95 Z", [x0, x1], "shell", r=36)
    d.box("co-foot", [x0 + 30, 60, Z(40), x1 - 30, 100, Z(220)], "plastic#5b6068", r=10)
    # sloped top panel: blue frame, light face with 4 LED windows, keys, green switch
    ang = math.degrees(math.atan2(1040 - 780, 440 - 345))
    tr = rot("x", -(90 - ang), [0, 780, Z(440)])
    # panel drawn flat on the front face (y up) then tilted back about its lower edge
    d.box("co-frame", [x0 + 10, 775, Z(434), x1 - 10, 1060, Z(446)], "gloss#2a55c8", r=8, rot=tr)
    d.box("co-face", [x0 + 34, 800, Z(444), x1 - 34, 1040, Z(448)], "gloss#e3e8ef", r=6, rot=tr)
    d.box("co-win", [x0 + 75, 985, Z(447), x0 + 145, 1015, Z(449.5)], "plastic#4a5260", r=3, rot=tr,
          repeat={"n": 4, "step": [88, 0, 0]})
    d.box("co-sw", [x0 + 70, 920, Z(447), x0 + 110, 955, Z(458)], "gloss#2fae4a", r=4, rot=tr)
    d.slab("co-box", "front", rrp(x0 + 150, 900, x1 - 60, 960, 6) + " " + rrp(x0 + 153, 903, x1 - 63, 957, 5),
           [Z(447), Z(448.5)], "plastic#6a7488", soft=True, rot=tr)
    d.slab("co-box2", "front", rrp(x0 + 90, 815, x1 - 60, 885, 6) + " " + rrp(x0 + 93, 818, x1 - 63, 882, 5),
           [Z(447), Z(448.5)], "plastic#6a7488", soft=True, rot=tr)
    btn(d, "co-key", [x0 + 200, 930, Z(448)], 12, "front", "plastic#2b3f6a", h=3, rot=tr, copies=[[160, 0, 0]])
    btn(d, "co-key2", [x0 + 150, 850, Z(448)], 12, "front", "plastic#2b3f6a", h=3, rot=tr,
        copies=[[110, 0, 0], [220, 0, 0]])
    d.box("co-band", [x0 - 2, 770, Z(300), x1 + 2, 790, Z(442)], "gloss#2a55c8", r=6)
    # dark-blue teardrop panel on the front
    xc = (x0 + x1) / 2
    d.slab("co-drop", "front", f"M {xc - 95} 660 L {xc + 95} 660 Q {xc + 95} 470 {xc} 400 Q {xc - 95} 470 {xc - 95} 660 Z",
           [Z(432), Z(452)], "gloss#2440b8", r=8)
    # side: dark handle slot (left side), blue logo low on the left side
    d.box("co-slot", [x0 - 4, 830, Z(150), x0 + 6, 990, Z(260)], "plastic#22262c", r=20)
    logo(d, "co-logo", [x0, 260, Z(300)], 90, "left", words=False)
    casters(d, "co-castor", [(x0 + 60, Z(70)), (x1 - 60, Z(70)), (x0 + 60, Z(390)), (x1 - 60, Z(390))], 70)


def hyz_iik():
    X = 620
    d = Design("hyz-iik", [X + 2100, 900, 1150], dict(MATS))
    u = lambda v: X + v
    yl = 650
    # body: tub + two legs joined by a wide shallow arch; slightly narrower at the bottom
    # review: the photo's arch is shallow (~180 at its top) and asymmetric: it rises right after the left leg and runs
    # long and low to the right end; the upper tub (from ~400) overhangs the lower body with a shoulder line
    body = (f"M {u(330)} 70 L {u(800)} 70 C {u(870)} 170 {u(980)} 235 {u(1120)} 240 "
            f"C {u(1330)} 245 {u(1520)} 120 {u(1660)} 92 L {u(2030)} 78 L {u(2045)} 420 L {u(310)} 420 Z")
    d.slab("body", "front", body, [55, 845], "shell", r=55)
    # the right end (tall door) is flush with the upper tub down to the bottom
    d.slab("tub-right", "front", f"M {u(1665)} 90 L {u(2040)} 78 Q {u(2075)} 80 {u(2075)} 140 L {u(2075)} {yl - 30} "
           f"L {u(1665)} {yl - 30} Z", [38, 862], "shell", r=40)
    d.slab("tub-up", "front", f"M {u(250)} 400 L {u(2050)} 400 Q {u(2075)} 400 {u(2075)} 440 L {u(2075)} {yl - 30} "
           f"L {u(150)} {yl - 30} Q {u(180)} 470 {u(250)} 400 Z", [38, 862], "shell", r=40)
    d.slab("ledge", "top", rrp(u(0), 25, u(2100), 875, 50), [yl - 55, yl], "shell", r=18)
    # hood: bulbous towards the head, rounded both ends
    cz = 450
    S = [(410, 760, 640, 300, yl + 190), (700, 820, 860, 400, yl + 60), (1100, 820, 820, 400, yl + 40),
         (1600, 810, 700, 350, yl + 20), (1950, 760, 560, 280, yl + 10)]
    d.loft("hood", [sx(u(a), w, dd, r, cy, cz) for a, w, dd, r, cy in S], "shell", axis="x", dome="both", domeH=90)
    d.sphere("knob", [u(720), yl + 488, cz], None, "gloss#f2f4f6", radii=[60, 22, 50])
    d.sphere("head-hole", [u(320), yl + 150, cz], None, "plastic#3a4250", radii=[30, 160, 120])
    d.box("head-hole-sill", [u(300), yl - 4, cz - 125, u(330), yl + 2, cz + 125], "plastic#3a4250", soft=True)
    # perforated stainless plate on the shelf in front of the head opening
    d.box("perf", [u(170), yl - 2, 330, u(300), yl + 14, 570], "steel", r=4)
    d.box("perf-dot", [u(185), yl + 14, 345, u(192), yl + 15, 352], "plastic#55595f", soft=True,
          repeat={"n": 9, "step": [0, 0, 25]}, copies=[[k * 20, 0, 0] for k in range(1, 6)])
    # recessed handle pocket on the hood front
    yh0, yh1 = yl + 110, yl + 250
    zs = z_surf(820, 820, 400, yl + 40, cz, (yh0 + yh1) / 2)
    d.box("pocket", [u(900), yh0, zs - 60, u(1190), yh1, zs + 6], "shell", r=26)
    d.box("pocket-in", [u(922), yh0 + 18, zs - 50, u(1168), yh1 - 18, zs + 8], "gloss#e4e7ea", r=18)
    d.cyl("pocket-bar", [u(930), yh0 + 70, zs + 2], [u(1160), yh0 + 70, zs + 2], 34, "shell")
    # front: logo, doors, green buttons, castors, pipe fitting at the left end
    zf = 845
    logo(d, "logo", [u(900), 500, 862], 88, "front")
    d.box("door-s", [u(560), 95, zf - 6, u(720), 300, zf + 8], "shell", r=12)
    d.box("door-s-h", [u(700), 160, zf + 6, u(710), 230, zf + 18], "plastic#9aa0a6", r=3)
    # review: the tall door reaches from under the rim nearly to the bottom; its lock at the upper left, hinges right
    d.box("door-l", [u(1700), 110, 862 - 6, u(1975), 600, 862 + 8], "shell", r=16)
    d.box("door-l-in", [u(1718), 128, 862 + 6, u(1957), 582, 862 + 10], "gloss#f2f3f5", r=12)
    d.cyl("door-l-key", [u(1735), 420, 862 + 8], [u(1735), 420, 862 + 24], 24, "chrome")
    d.box("door-l-hinge", [u(1972), 470, 862 - 2, u(1980), 510, 862 + 10], "chrome", r=2, copies=[[0, -300, 0]])
    green_buttons(d, "btn", u(930), 300, zf, nx=2, ny=1, dx=70, labels=False)
    green_buttons(d, "btn2", u(860), 245, zf, nx=4, ny=1, dx=70, labels=False)
    d.cyl("pipe", [u(330), 260, 650], [u(270), 260, 650], 40, "plastic#26292d", copies=[[0, -40, -60]])
    casters(d, "castor", [(u(420), 160), (u(420), 740), (u(1960), 160), (u(1960), 740)], 45, "rubber#1c1c1c")
    console_iik(d, 0, 225)
    return d


def hyz_iib():
    X = 620
    d = Design("hyz-iib", [X + 2100, 860, 1320], dict(MATS, blue="gloss#2f4fb0"))
    u = lambda v: X + v
    yt = 620                     # top of the white body
    # body: upper band over the length, left end slanting in to the lower body, shallow arch cut in the bottom
    # review (photo measured): the front face's left edge is near vertical from the floor up to ~110 below the top,
    # a short fairing slants from there up-left under the overhanging head shelf; the arch is shallow (~95) u 850-1480
    body = (f"M {u(310)} 25 L {u(850)} 25 Q {u(1165)} 165 {u(1480)} 25 L {u(2040)} 25 L {u(2060)} {yt} "
            f"L {u(70)} {yt} L {u(80)} {yt - 30} Q {u(140)} {yt - 100} {u(300)} {yt - 112} Z")
    d.slab("body", "front", body, [45, 815], "shell", r=45)
    # stainless trim band + light-blue padded top (slightly wider than the body)
    d.slab("trim", "top", rrp(u(40), 30, u(2090), 830, 40), [yt - 2, yt + 38], "steel", r=10)
    d.box("pad", [u(28), yt + 36, 18, u(2100), yt + 92, 842], "leather#8fa9d8", r=22, puff=4)
    # fabric tunnel: two half-cylinder sections with a seam, dark opening at the head end
    yp = yt + 90
    def tun(id, a, b):
        d.loft(id, [sx(u(a), 600, 600, 298, yp, 430), sx(u(b), 600, 600, 298, yp, 430)], "fabric#9fb6e4", axis="x")
    # review: the tunnel reaches from just behind the pillow nearly to the foot end (two sections ~820 each)
    tun("tunnel-a", 335, 1150)
    tun("tunnel-b", 1157, 1975)
    d.loft("seam", [sx(u(1147), 612, 612, 304, yp, 430), sx(u(1160), 612, 612, 304, yp, 430)], "fabric#8ca3d4", axis="x")
    d.slab("tunnel-hole", "side", f"M 330 {yp} L 330 {yp + 190} C 330 {yp + 290} 530 {yp + 290} 530 {yp + 190} L 530 {yp} Z",
           [u(331), u(336)], "plastic#22262c", soft=True)
    d.box("pillow", [u(180), yp, 320, u(325), yp + 52, 560], "gloss#f4f5f7", r=18)
    d.box("pillow-holes", [u(195), yp + 52, 340, u(306), yp + 53, 346], "plastic#9aa1aa", soft=True,
          repeat={"n": 7, "step": [0, 0, 30]}, copies=[[k * 18, 0, 0] for k in range(1, 7)])
    # blue piping: sweep from the top left down and along, around the arch, door outline
    zf = 815
    d.tube("pipe-a", [[u(305), yt - 108, zf + 2], [u(330), 410, zf + 2], [u(460), 350, zf + 2], [u(1470), 165, zf + 2],
                      [u(1565), 110, zf + 2], [u(1600), 25, zf + 2]], 12, "blue", bend=90, soft=True)
    d.tube("pipe-arch", [[u(850 + 630 * k / 8), 27 + 140 * (k / 8) * (1 - k / 8) * 2 * 0.5 * 2, zf + 2] for k in range(9)],
           12, "blue", bend=40, soft=True)
    # review: the tall door reaches from near the floor to ~40 under the top
    d.box("door-l", [u(1700), 60, zf - 4, u(1990), 575, zf + 6], "shell", r=16)
    d.tube("door-l-line", [[u(1700), 140, zf + 7], [u(1700), 575, zf + 7], [u(1990), 575, zf + 7], [u(1990), 60, zf + 7],
                           [u(1780), 60, zf + 7], [u(1700), 140, zf + 7]], 10, "blue", bend=20, soft=True)
    d.box("door-l-h", [u(1712), 290, zf + 6, u(1722), 350, zf + 18], "plastic#9aa0a6", r=3)
    d.box("door-s", [u(520), 40, zf - 4, u(650), 250, zf + 6], "shell", r=12)
    d.slab("door-s-line", "front", rrp(u(520), 40, u(650), 250, 12) + " " + rrp(u(525), 45, u(645), 245, 9),
           [zf + 6, zf + 7.5], "plastic#9aa3b0", soft=True)
    d.box("door-s-h", [u(632), 120, zf + 6, u(640), 165, zf + 14], "plastic#9aa0a6", r=3)
    # 2 small green lamps over 4 green keys (white rings), labels over each, left of the arch
    green_buttons(d, "btn", u(900), 178, zf, nx=2, ny=1, dx=52)
    green_buttons(d, "btn2", u(845), 108, zf, nx=4, ny=1, dx=52)
    d.box("btn2-red", [u(835), 132, zf, u(855), 142, zf + 1.4], "gloss#d0342c", soft=True, copies=[[52 * k, 0, 0] for k in (1, 2, 3)])
    logo(d, "logo", [u(1040), 500, zf], 105, "front")
    d.cyl("foot", [u(380), 0, 90], [u(380), 25, 90], 40, "grey", copies=[[0, 0, 680], [1620, 0, 0], [1620, 0, 680]])
    trolley_iic(d, 30, 205, base_mat="plastic#8ea5cf", variant="iib", tw=40)
    return d


def hyz_ia():
    W, Dp = 2300, 700
    d = Design("hyz-ia", [W, Dp, 1000], dict(MATS, shell="plastic#eef0f3", lilac="plastic#c3c2d8"))
    # bed box on black feet
    d.box("bed", [340, 70, 10, W - 10, 600, Dp - 10], "shell", r=6)
    d.box("rim-in", [365, 560, 35, W - 35, 602, Dp - 35], "lilac", r=3)
    d.box("panel", [380, 110, Dp - 14, 1310, 520, Dp - 8], "shell", r=4, copies=[[950, 0, 0]])
    d.slab("panel-line", "front", rrp(380, 110, 1310, 520, 4) + " " + rrp(386, 116, 1304, 514, 3), [Dp - 9, Dp - 7.5],
           "plastic#b9bec6", soft=True, copies=[[950, 0, 0]])
    d.box("top-line", [345, 535, Dp - 11, W - 15, 541, Dp - 9], "plastic#c9cdd3", soft=True)
    # lilac top panels with slot vents and lift-out lids
    d.box("lid", [700, 600, 60, 1150, 606, Dp - 60], "lilac", r=3, copies=[[480, 0, 0], [900, 0, 0]])
    d.box("vent", [900, 606, 200, 1080, 609, 214], "plastic#9a99b4", soft=True, repeat={"n": 3, "step": [0, 0, 60]})
    d.box("vent2", [1300, 606, 150, 1420, 609, 162], "plastic#9a99b4", soft=True, repeat={"n": 4, "step": [0, 0, 60]},
          copies=[[200, 0, 0]])
    d.box("pillow", [W - 290, 602, 170, W - 60, 680, 530], "leather#bcbbd3", r=20, puff=8)
    # review: the photo's feet are short grey square legs on black pads
    d.box("feet", [372, 0, 42, 428, 30, 98], "black", r=4, copies=[[1830, 0, 0], [0, 0, 556], [1830, 0, 556]])
    d.box("legs", [380, 30, 50, 420, 72, 90], "metal#b9bdc3", r=3, copies=[[1830, 0, 0], [0, 0, 556], [1830, 0, 556]])
    # control cabinet at the head end: sloped top with a dark-blue digital panel
    d.slab("cab", "side", rp([(10, 70), (Dp - 10, 70), (Dp - 10, 880), (Dp - 160, 1000), (10, 1000)], [4, 4, 10, 10, 4]),
           [10, 340], "shell", r=6)
    ang = math.degrees(math.atan2(120, 150))
    tr = rot("x", ang, [0, 1000, Dp - 160])
    # review: the photo's panel covers the outer ~2/3 of the slope: LED windows, red/green keys, a light window
    d.box("cab-panel", [28, 998, Dp - 150, 240, 1003, Dp - 25], "gloss#20356e", r=4, rot=tr)
    d.box("cab-disp", [50, 1002, Dp - 140, 130, 1005, Dp - 112], "gloss#3a9a4a", r=2, rot=tr, copies=[[0, 0, 36]])
    d.box("cab-win", [150, 1002, Dp - 140, 215, 1005, Dp - 100], "gloss#dfe8f5", r=2, rot=tr)
    btn(d, "cab-key", [60, 1003, Dp - 50], 12, "top", "gloss#d23a32", h=3, rot=tr, repeat={"n": 2, "step": [30, 0, 0]})
    btn(d, "cab-key2", [130, 1003, Dp - 50], 12, "top", "gloss#3fbf5a", h=3, rot=tr, repeat={"n": 3, "step": [30, 0, 0]})
    d.box("cab-recess", [8, 110, 60, 12, 860, Dp - 60], "plastic#dfe2e6", soft=True)
    d.box("cab-feet", [32, 0, 42, 88, 30, 98], "black", r=4, copies=[[230, 0, 0], [0, 0, 556], [230, 0, 556]])
    d.box("cab-legs", [40, 30, 50, 80, 72, 90], "metal#b9bdc3", r=3, copies=[[230, 0, 0], [0, 0, 556], [230, 0, 556]])
    d.box("cab-front", [20, 120, Dp - 12, 330, 860, Dp - 8], "shell", r=4)
    d.slab("cab-front-line", "front", rrp(20, 120, 330, 860, 4) + " " + rrp(26, 126, 324, 854, 3), [Dp - 9, Dp - 7.5],
           "plastic#b9bec6", soft=True)
    return d


if __name__ == "__main__":
    fns = {"hyz-iif": hyz_iif, "hyz-iic": hyz_iic, "hyz-iik": hyz_iik, "hyz-iib": hyz_iib, "hyz-ia": hyz_ia}
    for i in (sys.argv[1:] or list(fns)):
        go(fns[i]())
