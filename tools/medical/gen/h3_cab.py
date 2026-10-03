"""XYL-VIIA, XYL-VIID, XYL-VIIIB automatic paraffin wax cabinets: white cabinet on a graphite plinth with castors,
doors with tray windows, stainless worktop with a left lip and a recessed tray lid, black glass console with screen."""
import sys
from h3lib import *
Design = D

MATS = {"shell": "plastic#f2f3f5", "steel": "metal#c8ccd2", "plinth": "plastic#4a4040", "glass": "gloss#111214",
        "win": "plastic#3b3f45", "slat": "plastic#e9ecef", "lettr": "plastic#6f747a", "gap": "plastic#b9bdc2"}


def base(d, W, D, xs_castor, y_top=100, xs_feet=None):
    d.box("plinth", [12, 72, 22, W - 12, y_top, D - 22], "plinth", r=4)
    # review: the photo's castors are ~75 mm and stand inboard; the levelling feet are at the corners
    casters(d, "castor", [(x, z) for x in xs_castor for z in (80, D - 80)], 72, "rubber#9a9fa5")
    fx = list(xs_feet or (60, W - 60))
    d.cyl("foot", [fx[0], 12, D - 60], [fx[0], 72, D - 60], 22, "chrome",
          copies=[[fx[i] - fx[0], 0, dz] for i in range(len(fx)) for dz in (0, -(D - 120))][1:])
    d.cyl("foot-pad", [fx[0], 0, D - 60], [fx[0], 12, D - 60], 46, "rubber#5a5e63",
          copies=[[fx[i] - fx[0], 0, dz] for i in range(len(fx)) for dz in (0, -(D - 120))][1:])


# black glass face of the console in the screen pictures (u, v from the picture's top-left): TL, TR, BR, BL
FACE = {"med_xyl-viia_screen": [(0.125, 0.165), (0.93, 0.335), (0.893, 0.83), (0.078, 0.64)],
        "med_xyl-viid_screen": [(0.09, 0.145), (0.92, 0.345), (0.918, 0.82), (0.028, 0.71)]}


def worktop(d, W, D, yt, tray_x1, con_x0, con_x1, screen_mat, con_h=172):
    """Worktop at yt (top surface), left lip, recessed tray lid, console at the left rear."""
    d.box("top-band", [0, yt - 58, 0, W, yt - 30, D - 18], "shell", r=3)
    d.box("top", [-6, yt - 30, -2, W + 6, yt, D + 4], "steel", r=4)
    d.box("lip", [-6, yt - 2, 12, 22, yt + 38, D - 30], "steel", r=4)
    d.box("lip-back", [-6, yt - 2, 8, con_x0, yt + 38, 30], "steel", r=4)
    # tray lid: groove outline + pull
    d.slab("tray-groove", "top", rrp(40, 210, tray_x1, D - 25, 10) + " " + rrp(46, 216, tray_x1 - 6, D - 31, 6),
           [yt - 1, yt + 0.6], "plastic#8e9399", soft=True)
    d.box("tray-pull", [tray_x1 * 0.66, yt - 1, 470, tray_x1 * 0.66 + 90, yt + 6, 505], "chrome", r=3)
    # console: stainless body, sloped black front carrying the screen picture
    zb, zf, tilt = 40, 185, 15
    top_z = zf - con_h * math.tan(math.radians(tilt))
    d.slab("console", "side", rp([(zb, yt), (zf, yt), (top_z, yt + con_h), (zb, yt + con_h)], [0, 4, 10, 10]),
           [con_x0, con_x1], "steel", r=4)
    sx0, sy0, sx1, sy1 = con_x0 + 6, yt + 4, con_x1 - 6, yt + con_h - 4
    d.add("screen", "screen", "glass", box=[sx0, sy0, zf - 4, sx1, sy1, zf + 1], r=2,
          face="front", bezel=0, print=screen_mat, rot=rot("x", -tilt, [0, yt, zf]))
    # review: the picture is the whole console in perspective (grey cheeks, worktop): a black glass plate with a hole
    # the shape of the picture's black face covers the rest, so the console reads as one black glass face
    quad = [(sx0 + u * (sx1 - sx0), sy1 - v * (sy1 - sy0)) for u, v in FACE[screen_mat]]
    d.slab("screen-mask", "front", rrp(sx0 - 1, sy0 - 1, sx1 + 1, sy1 + 1, 2) + " " + P(quad), [zf + 2, zf + 3],
           "glass", soft=True, rot=rot("x", -tilt, [0, yt, zf]))
    return zf


def door_window(d, id, x0, x1, y0, y1, zf, n):
    d.box(id, [x0, y0, zf - 4, x1, y1, zf + 1.5], "win", r=6)
    d.box(id + "-frame", [x0 - 6, y0 - 6, zf - 5, x1 + 6, y1 + 6, zf + 0.6], "plastic#9da2a8", r=8)
    step = (y1 - y0 - 30) / (n - 1)
    d.box(id + "-slat", [x0 + 10, y0 + 15, zf + 1.6, x1 - 10, y0 + 25, zf + 2.6], "slat", r=1, soft=True,
          repeat=rep(n, [0, step, 0]))


def bar_handle(d, id, x, y0, y1, zf, **kw):
    d.sweep(id, [[x, y0, zf], [x, y0, zf + 30], [x, y1, zf + 30], [x, y1, zf]], [16, 10], "chrome", bend=10, r=3, **kw)


def xyl_viia():
    W, D, H = 1200, 700, 1100
    d = Design("xyl-viia", [W, D, H], dict(MATS))
    base(d, W, D, (200, W - 200))
    yt = 925
    d.box("body", [0, 100, 0, W, yt - 58, D - 20], "shell", r=6)
    zf = D - 20
    d.box("door-l", [14, 112, zf - 2, W / 2 - 4, yt - 72, zf + 6], "shell", r=4)
    d.box("door-r", [W / 2 + 4, 112, zf - 2, W - 14, yt - 72, zf + 6], "shell", r=4)
    d.box("gap", [W / 2 - 4, 112, zf - 1, W / 2 + 4, yt - 72, zf + 3], "gap")
    d.box("gap-top", [8, yt - 66, zf - 1, W - 8, yt - 60, zf + 3], "gap")
    door_window(d, "win", 795, 975, 190, 760, zf + 6, 18)
    bar_handle(d, "handle", W / 2 + 28, 520, 650, zf + 6)
    d.box("hinge", [W - 14, 160, zf - 6, W - 6, 220, zf + 4], "chrome", r=2, copies=[[0, 300, 0], [0, 560, 0]])
    text3(d, "model", "XYL-VIIC", [46, 760, zf + 7.5], 44, "lettr", gap=0.3)
    worktop(d, W, D, yt, 640, 165, 680, "med_xyl-viia_screen")
    return d


def xyl_viid():
    W, D, H = 1800, 700, 1100
    d = Design("xyl-viid", [W, D, H], dict(MATS))
    base(d, W, D, (200, 900, W - 200), xs_feet=(60, 830, W - 60))
    yt = 925
    d.box("body", [0, 100, 0, W, yt - 58, D - 20], "shell", r=6)
    zf = D - 20
    d.box("door-l", [14, 112, zf - 2, 548, yt - 72, zf + 6], "shell", r=4)
    d.box("post", [552, 100, zf - 2, 578, yt - 58, zf + 4], "shell", r=3)
    d.box("door-a", [582, 112, zf - 2, 1186, yt - 72, zf + 6], "shell", r=4)
    d.box("door-b", [1194, 112, zf - 2, W - 14, yt - 72, zf + 6], "shell", r=4)
    d.box("gap", [1186, 112, zf - 1, 1194, yt - 72, zf + 3], "gap", copies=[[-638, 0, 0]])
    d.box("gap-top", [8, yt - 66, zf - 1, W - 8, yt - 60, zf + 3], "gap")
    door_window(d, "win-a", 790, 970, 170, 770, zf + 6, 19)
    door_window(d, "win-b", 1395, 1575, 170, 770, zf + 6, 19)
    bar_handle(d, "handle", 1168, 500, 640, zf + 6, copies=[[44, 0, 0]])
    d.box("hinge", [W - 14, 160, zf - 6, W - 6, 220, zf + 4], "chrome", r=2, copies=[[0, 300, 0], [0, 560, 0]])
    text3(d, "model", "XYL-VIIF", [44, 760, zf + 7.5], 44, "lettr", gap=0.3)
    text3(d, "abox", "A-box", [1000, 760, zf + 7.5], 40, "lettr", gap=0.3)
    text3(d, "bbox", "B-box", [1240, 760, zf + 7.5], 40, "lettr", gap=0.3)
    worktop(d, W, D, yt, 610, 160, 670, "med_xyl-viid_screen")
    return d


def xyl_viiib():
    W, D, H = 700, 650, 1100
    d = Design("xyl-viiib", [W, D, H], dict(MATS))
    base(d, W, D, (175, W - 175))
    yt = 960
    zf = D - 20
    d.box("body", [0, 100, 0, W, yt, zf], "shell", r=8)
    d.box("deck", [0, yt - 2, 0, W, yt + 12, zf], "plastic#e4e6e9", r=4)
    # lower door + upper flap standing proud with a chamfered top
    d.box("door", [14, 112, zf - 2, W - 14, 548, zf + 6], "shell", r=4)
    d.slab("flap", "side", rp([(zf - 4, 560), (zf + 28, 560), (zf + 28, 880), (zf + 4, 930), (zf - 4, 930)], [0, 6, 14, 8, 0]),
           [12, W - 12], "shell", r=6)
    d.box("gap", [12, 549, zf - 1, W - 12, 556, zf + 3], "gap")
    text3(d, "model", "XYL-VIIIB", [120, 800, zf + 29.5], 56, "plastic#c9cdd2", gap=0.3, stroke=9)
    # console at the rear over 3/4 of the width: stainless body, black glass front with a blue touch screen
    zb, zc, tilt, ch = 30, 160, 14, 140
    top_z = zc - ch * math.tan(math.radians(tilt))
    d.slab("console", "side", rp([(zb, yt + 12), (zc, yt + 12), (top_z, yt + 12 + ch), (zb, yt + 12 + ch)], [0, 4, 10, 10]),
           [10, 540], "steel", r=4)
    r_ = rot("x", -tilt, [0, yt + 12, zc])
    # review: the photo's console face is the same as XYL-VIIA/C's (logo, title, touch screen at the right): no crop
    # of its own, so the VIIA console picture is used with the same black-glass mask
    sx0, sy0, sx1, sy1 = 16, yt + 16, 534, yt + 8 + ch
    scr = "med_xyl-viia_screen"
    d.add("screen", "screen", "glass", box=[sx0, sy0, zc - 4, sx1, sy1, zc + 1], r=2, face="front", bezel=0,
          print=scr, rot=r_)
    quad = [(sx0 + u * (sx1 - sx0), sy1 - v * (sy1 - sy0)) for u, v in FACE[scr]]
    d.slab("screen-mask", "front", rrp(sx0 - 1, sy0 - 1, sx1 + 1, sy1 + 1, 2) + " " + P(quad), [zc + 2, zc + 3],
           "glass", soft=True, rot=r_)
    # vent holes on the console's left cheek
    d.box("vent", [9, yt + 50, 52, 10.5, yt + 56, 58], "plastic#9aa0a8", soft=True,
          repeat=rep(6, [0, 0, 12]), copies=[[0, 12 * k, 0] for k in range(1, 5)])
    # indicator pill under the flap: light grey with a chrome rim and blue lettering
    d.box("pill", [400, 568, zf + 24, 500, 600, zf + 32], "plastic#e6e9ec", r=14)
    d.box("pill-rim", [396, 564, zf + 22, 504, 604, zf + 30], "chrome", r=16)
    d.box("pill-txt", [425, 581, zf + 32, 475, 587, zf + 33], "gloss#4a90d8", soft=True)
    return d


if __name__ == "__main__":
    for i in (sys.argv[1:] or ["xyl-viia", "xyl-viid", "xyl-viiib"]):
        go({"xyl-viia": xyl_viia, "xyl-viid": xyl_viid, "xyl-viiib": xyl_viiib}[i]())
