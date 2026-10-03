"""Helpers of batch kinesio-7 (shared by the k7_*.py generators only)."""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from p1lib import *  # noqa: F401,F403  (D, rot, rep, sec, text, text_len, rpoly, arc, rotx ...)


def label(d, id, s, cx, y0, z, h, mat, face="front"):
    """Centred stroke lettering on a front face: cx = centre x, y0 = baseline, z = face z."""
    w = text_len(s, h)
    return text(d, id, s, [cx - w / 2.0, y0, z + 0.6], h, mat, face=face)


def rail_unit(d, cx, plate_top, plate_bot, car, mats, plate_w=196, plate_h=(45, 45), plate_d=70, rail_gap=146,
              rail_d=20, rail_z=36, car_d=122, top_txt="XIANGYU", bot_txt="XIANGYU", bot_txt_mat=None, lever=None, lever_mat="chrome"):
    """The XYJ wall rail unit: teal end plates, 2 chrome guide bars, a box carriage.
    plate_top = y of the top plate's top, plate_bot = y of the bottom plate's bottom; car = (y0, y1) of the carriage.
    lever = (x_end, y_end, ball_d): thin chrome lever out of the carriage's right side to a black ball."""
    x0, x1 = cx - plate_w / 2.0, cx + plate_w / 2.0
    ht, hb = plate_h
    d.box("plate-top", [x0, plate_top - ht, 0, x1, plate_top, plate_d], "teal", r=5)
    d.box("plate-bot", [x0, plate_bot, 0, x1, plate_bot + hb, plate_d], "teal", r=5)
    for nm, x in (("l", cx - rail_gap / 2.0), ("r", cx + rail_gap / 2.0)):
        d.cyl(f"rail-{nm}", [x, plate_bot + hb - 2, rail_z], [x, plate_top - ht + 2, rail_z], rail_d, "metal#a3a29c")
        # collars where the bars enter the plates
        d.cyl(f"rail-collar-{nm}", [x, plate_top - ht - 6, rail_z], [x, plate_top - ht + 1, rail_z], rail_d + 8, "chrome",
              copies=[[0, plate_bot + hb - 1 - (plate_top - ht - 6), 0]])
    cy0, cy1 = car
    d.box("carriage", [x0, cy0, 4, x1, cy1, car_d], "teal", r=6)
    d.box("car-seam", [x0 + 4, cy0 + 4, car_d - 0.5, x1 - 4, cy1 - 4, car_d + 0.3], "tealdk", r=3, soft=True)
    d.box("car-face", [x0 + 6, cy0 + 6, car_d, x1 - 6, cy1 - 6, car_d + 1.5], "teal", r=4, soft=True)
    th = min(ht, hb) * 0.5
    if top_txt:
        label(d, "txt-top", top_txt, cx, plate_top - ht / 2.0 - th / 2.0, plate_d, th, "plastic#f4f6f5")
    if bot_txt:
        label(d, "txt-bot", bot_txt, cx, plate_bot + hb / 2.0 - th / 2.0, plate_d, th, bot_txt_mat or "plastic#f4f6f5")
    # wall screws
    d.decal("plate-screw", [x0 + 16, plate_top - ht / 2.0, plate_d + 0.6], [7, 7], "chrome", face="front", soft=True,
            copies=[[plate_w - 32, 0, 0], [0, plate_bot + hb / 2.0 - (plate_top - ht / 2.0), 0],
                    [plate_w - 32, plate_bot + hb / 2.0 - (plate_top - ht / 2.0), 0]])
    if lever:
        xe, ye, bd = lever
        ys = (cy0 + cy1) / 2.0 + 15
        d.cyl("lever-boss", [x1 - 2, ys, 70], [x1 + 14, ys, 70], 22, "chrome")
        d.cyl("lever", [x1 + 10, ys, 70], [xe - bd * 0.4, ye, 70], 9, lever_mat)
        d.sphere("lever-ball", [xe, ye, 70], bd, "gloss#16181a")
