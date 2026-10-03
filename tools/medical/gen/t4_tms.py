"""TMS special bed and TMS treatment chair — batch table-5.  python3 t4_tms.py [ids]  writes only these ids.
Inventory frame kept: length along z, the foot end at z = D (front), the head end at z = 0, x across."""
import sys, math
from t4lib import *


def special_bed():
    d = D("tms-special-bed", [700, 1750, 1200], {
        "pad": "leather#4f97da", "steel": "metal#dadde1", "lgrey": "plastic#d9dce0", "white": "plastic#f3f4f6",
        "dark": "plastic#2d3036", "chrome": "chrome", "board": "plastic#9aa0a8"})
    ys = 600                                   # seat board top
    # floor frame, castors, H lift, top frame
    # (photo: a compact deep floor frame under the seat and back only; the leg section is cantilevered)
    d.box("floor-l", [130, 70, 270, 180, 270, 1320], "steel", r=6, copies=[[390, 0, 0]])
    d.box("floor-x", [130, 70, 270, 570, 270, 320], "steel", r=6, copies=[[0, 0, 1000]])
    castor(d, "castor", 155, 295, 50, corners(155, 295, 545, 1295))
    d.box("lift", [200, 80, 760, 260, 470, 820], "steel", r=6, copies=[[240, 0, 0], [0, 0, 260], [240, 0, 260]])
    d.box("lift-x", [200, 300, 760, 500, 340, 1080], "steel", r=6)
    d.box("lift-box", [230, 120, 830, 470, 260, 1010], "lgrey", r=12)
    d.box("top-frame", [120, ys - 90, 600, 580, ys - 40, 1720], "steel", r=6)
    # sections: leg (slightly raised), seat, backrest 43 deg, boards under them
    d.box("seat-board", [80, ys - 40, 650, 620, ys, 1100], "board", r=6)
    d.box("seat", [70, ys - 5, 650, 630, ys + 90, 1100], "pad", r=26, puff=6)
    lr = rot("x", -6, [350, ys, 1110])
    d.box("leg-board", [80, ys - 40, 1110, 620, ys, 1750], "board", r=6, rot=lr)
    d.box("leg", [70, ys - 5, 1110, 630, ys + 90, 1750], "pad", r=26, puff=6, rot=lr)
    br = rot("x", 43, [350, ys, 645])          # +deg about x turns y towards +z: the board's -z end rises
    d.box("back-board", [80, ys - 40, -105, 620, ys, 640], "board", r=6, rot=br)
    d.box("back", [70, ys - 5, -105, 630, ys + 90, 640], "pad", r=26, puff=6, rot=br)
    # headrest support at the top end (white stem and pad)
    t = math.radians(43)
    hz, hy = 645 - 760 * math.cos(t), ys + 760 * math.sin(t)
    d.cyl("head-stem", [350, hy - 30, hz + 40], [350, hy + 80, hz - 40], 30, "white")
    d.box("head-pad", [250, hy + 60, hz - 70, 450, hy + 110, hz - 20], "white", r=18)
    # padded armrests: top bar forward from the backrest, the front curving down to the seat side
    for nm, x in (("l", 35), ("r", 665)):
        d.add(f"arm-{nm}", "sweep", "pad", path=[[x, 830, 420], [x, 845, 880], [x, ys + 60, 1010]], section=[70, 75], r=26, bend=150)
        d.box(f"arm-brk-{nm}", [x - 15, ys - 40, 860, x + 15, ys + 60, 900], "steel", r=4)
    # white half-disc ratchets at the seat/back joint, struts
    # (photo: half-discs with the round side up, below the seat at the seat/back joint; a short chrome strut
    #  from the floor frame end up under the leg section; a vertical post at the back end up to the backrest)
    for nm, x0 in (("l", 40), ("r", 645)):
        d.add(f"ratchet-{nm}", "slab", "white", plane="side",
              outline=poly_path(arc_pts(640, 420, 135, 0, 180, 12)), w=[x0, x0 + 15], r=4)
        d.cyl(f"ratchet-hub-{nm}", [x0 - 4, 440, 640], [x0 + 19, 440, 640], 30, "dark", soft=True)
    d.cyl("leg-strut", [170, 265, 1310], [170, ys - 50, 1450], 30, "chrome", copies=[[360, 0, 0]])
    d.cyl("leg-rod", [130, 360, 1385], [570, 360, 1385], 20, "chrome")
    d.cyl("leg-rod-k", [570, 360, 1385], [610, 360, 1385], 40, "dark")
    d.box("back-post", [325, 265, 345, 375, 805, 395], "lgrey", r=8)
    d.save()


def treatment_chair():
    d = D("tms-treatment-chair", [700, 1500, 900], {
        "pad": "leather#d3d7dc", "white": "gloss#f4f5f6", "cyan": "gloss#44c6d8", "dark": "plastic#2a2d32",
        "chrome": "chrome", "logo": "gloss#2f86d0"})
    # white moulded plinth, cyan accent line, castors
    # (photos: a LOW rounded plinth, ~300 tall, narrower than the seat, flaring out to the cyan line at the bottom,
    #  from under the seat/leg joint to the head end; the leg rest is cantilevered; a dark gap under the sections)
    d.loft("plinth", [sec(85, 566, 880, 95, 350, 655), sec(105, 570, 884, 97, 350, 655), sec(270, 526, 854, 115, 350, 650),
                      sec(440, 478, 820, 130, 350, 650)], "white")
    d.loft("accent", [sec(88, 568, 882, 96, 350, 655), sec(98, 570, 884, 97, 350, 655)], "cyan")
    d.box("gap", [190, 430, 320, 510, 492, 1000], "plastic#5d6168", r=16)
    castor(d, "castor", 110, 290, 80, corners(110, 290, 590, 1010))
    d.cyl("logo", [602, 300, 760], [618, 300, 760], 36, "logo", soft=True)
    d.cyl("logo-t", [600, 268, 760], [612, 268, 760], 10, "logo", soft=True, rot=rot("x", 90, [606, 268, 760]))
    d.cyl("lamp", [596, 330, 470], [612, 330, 470], 16, "gloss#45c24a", soft=True)
    d.cyl("socket", [596, 330, 410], [614, 330, 410], 30, "dark", soft=True)
    # sections: leg rest (wide, rounded), seat, backrest rising to the head end, black hinge gaps
    top_pad(d, "leg", 30, 670, 1080, 1500, 470, 560, "pad", cr=120, r=34)
    d.box("hinge1", [140, 480, 1060, 560, 540, 1085], "dark", r=6)
    top_pad(d, "seat", 50, 650, 640, 1060, 500, 590, "pad", cr=40, r=34)
    d.box("hinge2", [140, 520, 620, 560, 575, 645], "dark", r=6)
    br = rot("x", 10, [350, 500, 625])
    top_pad(d, "back", 60, 640, 60, 625, 500, 590, "pad", cr=70, r=34, rot=br)
    d.box("back-shell", [80, 440, 80, 620, 505, 610], "white", r=20, rot=br)
    d.tube("back-handle", [[250, 450, 120], [250, 400, 120], [450, 400, 120], [450, 450, 120]], 22, "chrome", bend=20, rot=br)
    # headrest on a black stem above the head end
    hz, hy = 625 - 600 * math.cos(math.radians(10)), 545 + 600 * math.sin(math.radians(10))
    d.cyl("head-stem", [350, hy - 20, hz + 30], [350, hy + 150, hz - 60], 34, "dark")
    d.box("head-pad", [210, hy + 130, hz - 120, 490, hy + 230, hz - 20], "pad", r=40, rot=rot("x", 15, [350, hy + 180, hz - 70]))
    # far armrest raised (upright pad), near armrest lowered with a chrome U handle
    d.box("arm-far", [20, 560, 700, 110, 860, 980], "pad", r=40, puff=4)
    d.box("arm-far-brk", [40, 460, 760, 90, 570, 920], "white", r=14)
    d.box("arm-near", [640, 540, 700, 700, 610, 1020], "pad", r=24)
    d.tube("arm-handle", [[700, 575, 780], [740, 575, 790], [740, 575, 940], [700, 575, 950]], 18, "chrome", bend=20)
    d.save()


ids = sys.argv[1:] or ["tms-special-bed", "tms-treatment-chair"]
if "tms-special-bed" in ids: special_bed()
if "tms-treatment-chair" in ids: treatment_chair()
