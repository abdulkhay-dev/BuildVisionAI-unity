"""E-series interferential trolleys: XY-K-GR-CII (black LED panel, handle + 2-tier cup rack on the LEFT) and
XY-K-GR-DII (15" touch screen, handle + 1-tier cup rack on the RIGHT). Same white drawer body on a dark grey base."""
from p3lib import *

MATS = {"shell": "gloss#f4f5f7", "base": "plastic#4a4f57", "seam": "plastic#9aa0a7", "slot": "rubber#1a1b1d",
        "bar": "plastic#b9bec4", "chrome": "chrome", "cup": "plastic#9a9fa6", "cable": "plastic#c9cdd2",
        "blue": "gloss#2f7fd0", "navy": "plastic#2a5c9c", "window": "plastic#a9c3d9", "bezel": "gloss#111214",
        "plug-b": "gloss#2e6fd0", "plug-o": "gloss#e8742b", "plug-y": "gloss#f0c419", "plug-r": "gloss#d8332a",
        "dish": "plastic#dfe2e6", "wheel": "rubber#c9cdd2"}

CX, X0, X1 = 300, 120, 480          # body centre / sides
ZB, ZF, BULGE = 100, 500, 34        # body back, front (middle of the bulge)
Y_BODY, SEAMS, Y_TOP = 262, [480, 645, 785], 916


def plan(x0, x1, zb, zf, b, rr=24, rf=70):
    return rpoly([(x0, zb), (x1, zb), (x1, zf - b), ((x0 + x1) / 2, zf), (x0, zf - b)], [rr, rr, rf, 400, rf])


def cart(id, size, side, head):
    d = D(id, size, dict(MATS))
    hx = (lambda x: x) if side == "R" else (lambda x: 2 * CX - x)     # handle side: +x for R, mirrored for L
    # ---- base: rounded dark plinth under the body, four splayed legs, castors
    d.slab("plinth", "top", plan(X0 - 12, X1 + 12, ZB - 12, ZF + 8, BULGE), [168, Y_BODY + 2], "base", r=20)
    for nm, (x, z) in {"fl": (CX - 255, 575), "fr": (CX + 255, 575), "bl": (CX - 240, 70), "br": (CX + 240, 70)}.items():
        d.add("leg-" + nm, "bar", "base", **{"from": [CX + (x - CX) * 0.3, 200, 300 + (z - 300) * 0.3], "to": [x, 150, z]},
              section=[66, 44], r=18)
        d.add("hub-" + nm, "lathe", "base", at=[x, 122, z], profile=[[0, 0], [30, 0], [30, 28], [24, 44], [0, 44]])
        d.add("castor-" + nm, "caster", "wheel", at=[x, 0, z + 12], d=100)
    # ---- body: stacked drawer fronts on a dark core (the seams), side seam lines
    d.slab("core", "top", plan(X0 + 3, X1 - 3, ZB + 3, ZF - 3, BULGE), [Y_BODY, Y_TOP], "seam", r=10)
    ys = [Y_BODY] + SEAMS + [Y_TOP]
    for i in range(4):
        d.slab(f"body{i}", "top", plan(X0, X1, ZB, ZF, BULGE), [ys[i] + (2 if i else 0), ys[i + 1] - 2], "shell", r=10)
    d.box("side-seam", [X0 - 1, Y_BODY + 10, ZF - BULGE - 62, X1 + 1, Y_TOP - 6, ZF - BULGE - 60], "seam", soft=True)
    # drawer 1: two vertical black slot handles at its top; drawer 2 grey bar; drawer 3 bar (DII) or a dish recess (CII)
    zf1 = ZF - 6
    d.box("slot", [CX - 105, Y_TOP - 92, zf1 - 8, CX - 85, Y_TOP - 6, zf1 + 3.5], "slot", r=6, copies=[[190, 0, 0]])
    d.box("bar2", [CX - 42, 718, ZF - 3, CX + 42, 730, ZF + 4], "bar", r=5)
    if head == "panel":
        d.slab("dish3", "front", rpoly([(CX - 55, 655), (CX + 55, 655), (CX + 38, 628), (CX, 620), (CX - 38, 628)], [0, 0, 18, 30, 18]),
               [ZF - 4, ZF + 1.5], "dish", r=2)
        d.box("dish3-shadow", [CX - 50, 650, ZF - 3, CX + 50, 655, ZF + 1.8], "bar", soft=True)
    else:
        d.box("bar3", [CX - 42, 585, ZF - 3, CX + 42, 597, ZF + 4], "bar", r=5)
    # bottom door: XIANGYU logo
    d.decal("logo", [CX - 18, 380, ZF + 0.5], [70, 13], "front", "blue", soft=True)
    d.decal("logo-cn", [CX + 30, 380, ZF + 0.5], [26, 13], "front", "blue", soft=True)
    d.decal("logo-sub", [CX, 362, ZF + 0.5], [80, 5], "front", "seam", soft=True)
    # chrome knob on the side opposite the handle, light window low on the left side
    kx = hx(X0)
    d.cyl("side-knob-stem", [kx, 885, ZF - BULGE - 30], [kx - (12 if side == "R" else -12), 885, ZF - BULGE - 30], 14, "chrome")
    d.add("side-knob", "sphere", "chrome", at=[kx - (22 if side == "R" else -22), 885, ZF - BULGE - 30], d=30)
    d.box("side-window", [X0 - 1.5, 385, ZF - BULGE - 105, X0 + 1, 495, ZF - BULGE - 80], "window", r=6)
    # ---- collar: wider rounded block over the drawers with a sloped top
    d.slab("collar", "side", rpoly([(ZB - 4, Y_TOP), (ZF + 26, Y_TOP), (ZF + 26, 1035), (ZF - 40, 1112), (ZB - 4, 1112)], [8, 12, 60, 40, 30]),
           [X0 - 8, X1 + 8], "shell", r=34)
    d.decal("eseries-e", [X0 + 42, Y_TOP + 30, ZF + 26.5], [13, 20], "front", "blue", soft=True)
    d.decal("eseries", [X0 + 80, Y_TOP + 28, ZF + 26.5], [56, 10], "front", "navy", soft=True)
    # rear housing rising behind the screen
    d.add("rear", "loft", "shell", sections=[
        {"at": 1100, "w": 300, "d": 250, "r": 60, "cx": CX, "cz": 260},
        {"at": 1200, "w": 260, "d": 190, "r": 60, "cx": CX, "cz": 250},
        {"at": 1270, "w": 200, "d": 120, "r": 50, "cx": CX, "cz": 260}], dome="end", domeH=30)
    if head == "panel":
        # 2 white dome buttons on the collar front, the big black LED panel on a white back shell, tilted ~20°
        for i, x in enumerate((CX - 60, CX + 70)):
            d.add(f"dome{i}", "lathe", "shell", at=[x, 1066, ZF - 6], profile=[[0, 0], [28, 0], [28, 6], [22, 16], [10, 20], [0, 21]],
                  rot=rot("x", 50, [x, 1066, ZF - 6]))
        tl = rot("x", -20, [CX, 1100, 400])
        # the crop has white body at its edges: the picture covers the whole front of the white panel shell (no black
        # outline) and is sized so that its black glass is ~410 × 340 as in the photo
        d.box("panel-back", [CX - 237, 1092, 360, CX + 237, 1466, 396], "shell", r=16, rot=tl)
        d.add("panel", "screen", "shell", box=[CX - 236, 1093, 392, CX + 236, 1465, 402], r=10, face="front", bezel=0.5,
              print="med_xy-k-gr-cii_screen", rot=tl)
        # one more vacuum cup on the right side of the collar (blue plug), its cable straight down that side
        d.box("rcup-bracket", [X1 + 6, 1062, 430, X1 + 44, 1076, 490], "shell", r=5)
        d.add("rcup", "lathe", "cup", at=[X1 + 28, 1076, 460], profile=[[0, 0], [12, 0], [16, 8], [27, 20], [29, 34], [24, 46], [0, 50]])
        d.cyl("rplug", [X1 + 28, 1062, 460], [X1 + 28, 1014, 460], 13, "plug-b")
        d.tube("rcable", [[X1 + 28, 1014, 460], [X1 + 30, 700, 474], [X1 + 26, 330, 484], [X1 + 16, 262, 478]], 5, "cable", bend=120, soft=True)
    else:
        # one silver knob on the collar front-left; 15" touch screen in a black bezel on a white back shell, tilted ~15°
        x = CX - 75
        d.add("knob", "lathe", "chrome", at=[x, 1066, ZF - 6], profile=[[0, 0], [27, 0], [27, 14], [24, 20], [0, 21]],
              rot=rot("x", 50, [x, 1066, ZF - 6]))
        d.add("knob-cap", "lathe", "shell", at=[x, 1066, ZF - 6], profile=[[0, 0], [20, 0], [20, 22], [0, 23]], rot=rot("x", 50, [x, 1066, ZF - 6]))
        # photo: a wide black glass (~424 × 344) with the UI in its middle (~270 × 200): a broad top strip with the logo
        # and the title, a bottom strip with a line of grey print
        tl = rot("x", -15, [CX, 1105, 410])
        d.box("screen-back", [CX - 216, 1090, 368, CX + 216, 1442, 404], "shell", r=20, rot=tl)
        d.box("glass", [CX - 212, 1096, 398, CX + 212, 1440, 410], "bezel", r=12, rot=tl)
        d.add("screen", "screen", "bezel", box=[CX - 135, 1162, 404, CX + 135, 1363, 412], r=2, face="front", bezel=0.5,
              print="med_xy-k-gr-dii_screen", rot=tl)
        d.box("screen-logo", [CX - 178, 1398, 409, CX - 152, 1420, 411], "blue", soft=True, rot=tl)
        d.box("screen-title", [CX - 60, 1408, 409, CX + 60, 1418, 411], "cable", soft=True, rot=tl)
        d.box("screen-title2", [CX - 50, 1394, 409, CX + 50, 1398, 411], "seam", soft=True, rot=tl)
        d.box("screen-foot", [CX - 160, 1128, 409, CX - 70, 1133, 411], "seam", soft=True, rot=tl, copies=[[0, -9, 0], [190, 0, 0], [190, -9, 0]])
    # ---- handle: chrome Ø28 loop in a plane beside the handle-side wall, reaching past the back; it carries the cables
    HX = hx(X1 + 72)
    up, lo = 1075, 870
    d.tube("handle", [[hx(X1 + 6), up, 300], [HX, up, 280], [HX, up, 10], [HX, lo, 10], [HX, lo, 450], [hx(X1 + 6), lo, 470]],
           28, "chrome", bend=55)
    d.cyl("handle-end", [hx(X1 - 2), lo, 470], [hx(X1 + 14), lo, 470], 34, "chrome")
    d.cyl("handle-mount", [hx(X1 - 2), up, 300], [hx(X1 + 14), up, 300], 34, "chrome")
    for k in range(5):
        z = 400 - 80 * k
        d.tube(f"hook{k}", [[HX, lo + 12, z], [HX, lo - 25, z], [hx(X1 + 72 + 18), lo - 30, z]], 5, "chrome", bend=8, soft=True)
    # ---- cup rack(s): white bracket along the side wall with grey cups and coloured plugs; cables hang in loops
    tiers = [(1080, [("plug-y", 1), ("plug-y", 1)], 420), (1000, [("plug-o", 1), ("plug-o", 1), ("plug-b", 1), ("plug-b", 1)], 470)] \
        if head == "panel" else [(1020, [("plug-b", 1), ("plug-b", 1), ("plug-o", 1), ("plug-o", 1)], 470)]
    ci = 0
    for t_i, (y, cups, z0) in enumerate(tiers):
        n = len(cups)
        z1 = z0 - 70 * n
        bx0, bx1 = sorted((hx(X1 + 4), hx(X1 + 62)))
        d.box(f"rack{t_i}", [bx0, y - 14, z1, bx1, y, z0], "shell", r=6)
        d.box(f"rack{t_i}-lip", [min(hx(X1 + 56), hx(X1 + 66)), y - 40, z1, max(hx(X1 + 56), hx(X1 + 66)), y, z0], "shell", r=4)
        for k, (pm, _) in enumerate(cups):
            z = z0 - 35 - 70 * k
            cx = hx(X1 + 34)
            d.add(f"cup{ci}", "lathe", "cup", at=[cx, y, z], profile=[[0, 0], [12, 0], [16, 8], [27, 20], [29, 34], [24, 46], [0, 50]])
            d.cyl(f"plug{ci}", [cx, y - 14, z], [cx, y - 62, z], 13, pm)
            # cable: from the plug down in a loop to near the floor and back up to a hook on the handle bar
            hz = 400 - 80 * (ci % 5)
            # (photo: the loops fan out sideways and in depth and reach down to 100–250 above the floor)
            sx = 1 if side == "R" else -1
            d.tube(f"cable{ci}", [[cx, y - 62, z], [cx + sx * (6 + 7 * ci), 620, z - 15 * k],
                                  [hx(X1 + 14 + 16 * ci), 110 + 45 * (ci % 3), (z + hz) / 2 + 20 * (ci % 2)], [HX, 560, hz], [HX, lo - 28, hz]],
                   5, "cable", bend=160, soft=True)
            ci += 1
    return d


cart("xy-k-gr-cii", [620, 620, 1440], "L", "panel").save()
cart("xy-k-gr-dii", [620, 620, 1440], "R", "screen").save()
