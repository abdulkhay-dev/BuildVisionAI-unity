"""XYQ-1 / 2 / 3 / 5 / 6 tilt tables (Tilt Table.pdf) in the photo poses — batch table-4.
python3 t4_xyq.py [ids]  writes only these ids.
Frame: the base runs along x, the head end at x = 0, the foot end and the pivot at x = W; the board rises over the base
with its face looking to +x (towards the foot end); front z = D."""
import sys, math
from t4lib import *

BLUE = "leather#8ab4e6"


class Tilt:
    def __init__(s, id, W, DP, ang, mats, py=410):
        s.W, s.DP, s.ang = W, DP, ang
        s.t = math.radians(ang)
        s.px, s.py = W - 200, py                     # pivot (under the board's foot end)
        s.xf = W - 160                               # board foot end (flat)
        s.xh = s.xf - 1900                           # board head end (flat)
        m = {"pad": BLUE, "strap": "fabric#78a9de", "frame": "plastic#f1f2f4", "chrome": "chrome", "steel": "metal#c3c7cc",
             "cap": "rubber#1f2124", "dark": "plastic#2a2d32", "act": "plastic#1d1f22", "wood": "wood#c9a77a"}
        m.update(mats)
        s.d = D(id, [W, DP, 0], m)
        s.r = rot("z", -ang, [s.px, s.py, 0])
        s.top = s.py + 100

    def R(s, x, y):
        c, sn = math.cos(s.t), math.sin(s.t)
        return (s.px + (x - s.px) * c + (y - s.py) * sn, s.py - (x - s.px) * sn + (y - s.py) * c)

    # ------------------------------------------------------------------ board
    def board(s, slot=True, straps=True):
        d, r, xh, xf, DP, py = s.d, s.r, s.xh, s.xf, s.DP, s.py
        z0, z1 = (DP - 650) / 2, (DP + 650) / 2
        d.box("b-plate", [xh + 20, py, z0 + 10, xf - 10, py + 22, z1 - 10], "frame", r=6, rot=r)
        d.box("b-rail", [xh + 40, py - 55, z0 + 5, xf - 20, py, z0 + 35], "chrome", r=6, rot=r, copies=[[0, 0, z1 - z0 - 40]])
        for k, dx in enumerate((120, 820, 1570)):       # (copies are world offsets, so explicit parts on the board)
            d.box(f"b-cross{k}", [xh + dx, py - 50, z0 + 30, xh + dx + 50, py - 5, z1 - 30], "steel", r=4, rot=r)
        top_pad(d, "head-pad", xh, xh + 380, z0, z1, py + 18, s.top, "pad", cr=45, r=22, rot=r)
        main = poly_path(rrect_pts(xh + 392, z0, xf, z1, 45))
        if slot:
            zc = DP / 2
            # (photos: the leg slot runs from ~150 to ~840 above the foot end, crossed by the lowest strap)
            main += " " + poly_path(stadium_pts(xf - 495, zc, 690, 84))
            d.box("slot-in", [xf - 830, py + 5, zc - 36, xf - 160, py + 25, zc + 36], "chrome", r=4, rot=r)
        d.add("main-pad", "slab", "pad", plane="top", outline=main, w=[py + 18, s.top], r=22, rot=r)
        if straps:
            for k, x in enumerate((xh + 640, xh + 1060, xh + 1470)):
                d.box(f"strap{k}", [x, py + 25, z0 - 6, x + 125, s.top + 7, z1 + 6], "strap", r=8, rot=r)
                d.decal(f"strap-seam{k}", [x + 62, s.top + 7.5, DP / 2], [4, 640], "top", "fabric#6492c8", soft=True, rot=r)

    # ------------------------------------------------------------------ base
    def base(s, lift=False, rest="bar", sticker=True):
        d, W, DP = s.d, s.W, s.DP
        yc0, yc1 = 225, 285
        for nm, x0 in (("h", 30), ("f", W - 90)):
            d.box(f"cross-{nm}", [x0, yc0, 10, x0 + 60, yc1, DP - 10], "frame", r=4)
            d.box(f"leg-{nm}", [x0, 12, 10, x0 + 60, yc1, 70], "frame", r=4, copies=[[0, 0, DP - 80]])
            d.box(f"legcap-{nm}", [x0 + 2, 0, 12, x0 + 58, 14, 68], "cap", r=3, copies=[[0, 0, DP - 80]])
            d.box(f"endcap-{nm}", [x0 - 1, yc0 + 2, 9, x0 + 61, yc1 - 2, 12], "plastic#7b8087", r=2, copies=[[0, 0, DP - 21]])
        d.box("rail", [60, yc1 - 10, 115, W - 60, yc1 + 45, 165], "frame", r=4, copies=[[0, 0, DP - 280]])
        d.box("mid-x", [W / 2 - 30, yc1 - 5, 165, W / 2 + 30, yc1 + 40, DP - 165], "frame", r=4)
        for x in (210, W - 260):
            d.box(f"cpost{x}", [x - 18, 70, 122, x + 18, yc1 - 10, 158], "steel", r=3, copies=[[0, 0, DP - 280]])
        castor(d, "castor", 210, 140, 60, [[W - 470, 0, 0], [0, 0, DP - 280], [W - 470, 0, DP - 280]])
        if sticker:
            d.decal("sticker", [W - 300, (yc0 + yc1) / 2, DP + 0.5], [60, 30], "front", "gloss#3a78c8", soft=True) if False else \
                d.decal("sticker", [W - 60, (yc0 + yc1) / 2, DP - 10 + 0.5], [40, 34], "front", "gloss#3a78c8", soft=True)
        top = yc1 + 45
        if lift:
            yl0, yl1 = top + 70, top + 160
            d.box("lift-rail", [180, yl0, 120, W - 220, yl1, 175], "frame", r=6, copies=[[0, 0, DP - 295]])
            d.box("lift-x", [180, yl0, 175, 240, yl1, DP - 175], "frame", r=5, copies=[[W - 460, 0, 0]])
            tl = text_len("XIANG YU", 36, 0.3)
            text(d, "lift-txt", "XIANG YU", [W / 2 - 150 - tl / 2, (yl0 + yl1) / 2 - 18, DP - 120 + 0.6], 36, "plastic#7d828a", gap=0.3)
            for x in (300, W - 340):
                d.box(f"lpost{x}", [x - 25, top, 125, x + 25, yl1 + 10, 170], "frame", r=4, copies=[[0, 0, DP - 295]])
                d.cyl(f"lcap{x}", [x, yl1 + 10, 147], [x, yl1 + 28, 147], 40, "gloss#e2c14a", copies=[[0, 0, DP - 295]])
            # (photos: no scissors — the frame rises on the four corner posts; black actuators lie in the lower frame)
            d.cyl("lift-act", [460, top + 40, DP / 2], [1150, top + 60, DP / 2], 70, "act")
            d.cyl("lift-act-rod", [1150, top + 60, DP / 2], [1400, top + 70, DP / 2], 30, "chrome")
            top = yl1
        # pivot posts at the foot end
        d.box("pivot-post", [s.px - 35, top - 10, 115, s.px + 35, s.py - 40, 165], "frame", r=5, copies=[[0, 0, DP - 280]])
        d.cyl("pivot", [s.px, s.py - 30, 100], [s.px, s.py - 30, DP - 100], 40, "steel")
        if rest == "bar":
            d.box("rest-post", [130, top - 10, 125, 170, 560, 165], "frame", r=4, copies=[[0, 0, DP - 290]])
            d.cyl("rest-bar", [150, 560, 120], [150, 560, DP - 120], 34, "steel")
        elif rest == "rect":
            d.box("rest-post", [630, top - 10, 130, 670, 680, 170], "frame", r=4, copies=[[0, 0, DP - 300]])
            d.box("rest-top", [630, 650, 130, 670, 690, DP - 130], "frame", r=4)
            d.cyl("rest-knob", [650, 690, 150], [650, 715, 150], 22, "dark", copies=[[0, 0, DP - 300]])
        elif rest == "u":
            d.box("rest-post", [300, top - 10, 125, 340, 500, 165], "frame", r=4, copies=[[0, 0, DP - 290]])
            d.box("up-rail", [300, 460, 125, s.px - 120, 500, 165], "frame", r=4, copies=[[0, 0, DP - 290]])
            for k, z in enumerate((145, DP - 145)):
                d.add(f"brace{k}", "bar", "frame", **{"from": [W / 2 - 100, top, z], "to": [W / 2 + 250, 470, z]}, section=[40, 40], r=4)
                d.add(f"brace{k}b", "bar", "frame", **{"from": [W / 2 - 100, top, z], "to": [420, 470, z]}, section=[40, 40], r=4)
            d.tube("rest-u", [[120, 470, 140], [120, 610, 140], [120, 610, DP - 140], [120, 470, DP - 140]], 30, "frame", bend=40)
            d.box("rest-u-foot", [100, 455, 125, 340, 480, 155], "frame", r=4, copies=[[0, 0, DP - 280]])
        s.base_top = top
        # actuator from the centre crossmember / lift frame to the board underside
        if lift:   # (XYQ-5/6 photos: a slender black actuator from the lift frame to the board low near the pivot)
            bx, by = s.R(s.xf - 450, s.py - 30)
            x0a = W / 2 - 300
            d.cyl("act", [x0a, top + 20, DP / 2], [x0a + 0.55 * (bx - x0a), top + 20 + 0.55 * (by - top - 20), DP / 2], 50, "act")
            d.cyl("act-rod", [x0a + 0.5 * (bx - x0a), top + 20 + 0.5 * (by - top - 20), DP / 2], [bx, by, DP / 2], 24, "act")
            return
        bx, by = s.R(s.xf - 950, s.py - 30)
        d.cyl("act", [W / 2 - 80, top + 20, DP / 2], [W / 2 + 0.55 * (bx - W / 2), top + 20 + 0.55 * (by - top - 20), DP / 2], 75, "act")
        d.cyl("act-rod", [W / 2 + 0.5 * (bx - W / 2), top + 20 + 0.5 * (by - top - 20), DP / 2], [bx, by, DP / 2], 36, "chrome")

    # ------------------------------------------------------------------ foot plates
    def foot(s, kind):
        d, r, xf, py, DP = s.d, s.r, s.xf, s.py, s.DP
        if kind == "plate":
            d.box("foot", [xf - 15, py - 40, 60, xf + 10, py + 300, DP - 60], "plastic#6f747b", r=6, rot=r)
            d.box("foot-rim", [xf - 22, py - 40, 50, xf + 14, py + 300, 70], "steel", r=4, rot=r, copies=[[0, 0, DP - 120]])
            d.cyl("foot-lever", [xf - 60, py - 30, 40], [xf - 60, py - 30, -60], 16, "dark", rot=r)
        else:
            top_mat = "plastic#e4e6e9" if kind == "pedals" else ("gloss#2f9e86" if kind == "green" else "plastic#9fc0dd")
            for nm, z0 in (("a", 80), ("b", DP / 2 + 15)):
                z1 = z0 + DP / 2 - 95
                d.box(f"pedal-{nm}", [xf - 30, py - 60, z0, xf + 5, py + 310, z1], "frame", r=8, rot=r)
                d.box(f"pedal-top-{nm}", [xf - 34, py - 30, z0 + 15, xf - 28, py + 290, z1 - 15], top_mat, r=4, rot=r)
                d.box(f"pedal-arm-{nm}", [xf - 10, py - 90, (z0 + z1) / 2 - 25, xf + 60, py + 120, (z0 + z1) / 2 + 25], "frame", r=6, rot=r)
                if kind == "pedals":
                    d.cyl(f"pedal-knob-{nm}", [xf - 30, py + 310, (z0 + z1) / 2], [xf - 30, py + 345, (z0 + z1) / 2], 60, "dark", rot=r)
                else:
                    d.box(f"pedal-motor-{nm}", [xf + 5, py - 20, (z0 + z1) / 2 - 45, xf + 90, py + 60, (z0 + z1) / 2 + 45], "act", r=12, rot=r)

    # ------------------------------------------------------------------ trays
    def tray(s, kind, xa, out=470, tilt=0, over=-15):
        """Tray anchored on the board face at flat x = xa: kind wood (horizontal-ish wood on chrome brackets),
        grey (grey panel in a white frame), lectern (wood standing upright on a chrome U frame)."""
        d, DP = s.d, s.DP
        ax, ay = s.R(xa, s.top)
        z0, z1 = -over, DP + over
        if kind in ("wood", "grey"):
            tr = rot("z", tilt, [ax + 40, ay, 0])
            if kind == "wood":
                top_pad(d, "tray", ax + 40, ax + 40 + out, z0, z1, ay - 12, ay + 12, "wood", cr=35, r=5, rot=tr)
                top_pad(d, "tray-edge", ax + 44, ax + 36 + out, z0 + 4, z1 - 4, ay - 22, ay - 10, "plastic#8b6a47", cr=32, r=3, rot=tr)
                d.tube("tray-rim", [[ax + 40, ay - 30, z0 + 20], [ax + out + 20, ay - 30, z0 + 20], [ax + out + 20, ay - 30, z1 - 20],
                                    [ax + 40, ay - 30, z1 - 20]], 20, "chrome", bend=30, rot=tr)
            else:
                top_pad(d, "tray-frame", ax + 40, ax + 40 + out, z0 + 30, z1 - 30, ay - 10, ay + 10, "frame", cr=30, r=6, rot=tr)
                top_pad(d, "tray", ax + 75, ax + 5 + out, z0 + 65, z1 - 65, ay - 13, ay + 13, "plastic#9a9fa6", cr=12, r=3, rot=tr)
            # brackets from the board side rails to the tray's back corners
            for nm, z in (("a", (DP - 650) / 2 + 20), ("b", (DP + 650) / 2 - 20)):
                bx, by = s.R(xa + 60, s.py - 30)
                d.add(f"tray-brk-{nm}", "bar", "chrome", **{"from": [bx, by, z], "to": [ax + 60, ay - 25, z]}, section=[30, 30], r=6)
            d.cyl("tray-knob-rod", [ax + 30, ay - 40, (DP - 650) / 2], [ax + 30, ay - 40, -40], 14, "chrome")
            d.lathe("tray-knob", [ax + 30, ay - 40, -40], [[0, 0], [24, 0], [24, 30], [0, 30]], "dark", axis="z")
            if kind == "grey":   # (XYQ-2 photo: a long black rod from the tray bracket down behind the board side)
                d.cyl("tray-rod", [ax + 30, ay - 40, (DP - 650) / 2 - 10], [ax + 120, ay - 380, -30], 18, "dark")
        elif kind == "lectern":
            # wooden lectern standing up from the board, on a chrome U frame lying on its foot-side face (the frame's
            # side tubes along the tray edges, a top bar and a middle bar), hinged on the board sides with black knobs
            ux, uy = math.cos(s.t), -math.sin(s.t)
            nx, ny = math.sin(s.t), math.cos(s.t)
            bx, by = ax + nx * 300, ay + ny * 300                  # lower edge of the tray, above the face
            ta = rot("z", 75, [bx, by, 0])
            s.hmax = by + 620 * math.sin(math.radians(75)) + 20
            d.box("tray", [bx, by - 12, z0 + 60, bx + 620, by + 12, z1 - 60], "wood", r=6, rot=ta)
            za, zb = (DP - 650) / 2 + 30, (DP + 650) / 2 - 30
            for nm, z in (("a", za), ("b", zb)):
                d.tube(f"tray-u-{nm}", [[bx - 120, by - 34, z], [bx + 600, by - 34, z]], 22, "chrome", rot=ta)
            d.cyl("tray-u-top", [bx + 600, by - 34, za], [bx + 600, by - 34, zb], 22, "chrome", rot=ta)
            d.cyl("tray-u-mid", [bx + 260, by - 34, za], [bx + 260, by - 34, zb], 18, "chrome", rot=ta)
            c, sn = math.cos(math.radians(75)), math.sin(math.radians(75))
            lx, ly = bx - 120 * c + 34 * sn, by - 120 * sn - 34 * c        # the frame's lower ends (world)
            hx, hy = ax - ux * 40, ay - uy * 40 - 25                        # hinge on the board side
            for nm, z, sg in (("a", za, -1), ("b", zb, 1)):
                d.cyl(f"tray-link-{nm}", [hx, hy, z], [lx, ly, z], 22, "chrome")
                d.cyl(f"tray-knob-{nm}", [hx, hy, z], [hx, hy, z + sg * 70], 16, "chrome")
                d.lathe(f"tray-knobh-{nm}", [hx, hy, z + sg * 70], [[0, 0], [26, 0], [26, 28], [0, 28]], "dark", axis="z",
                        rot=None if sg > 0 else rot("y", 180, [hx, hy, z + sg * 70]))
            mx, my = bx + 260 * c + 34 * sn, by + 260 * sn - 34 * c
            d.cyl("tray-midknob", [mx, my, zb], [mx, my, zb + 60], 14, "chrome")
            d.lathe("tray-midknob-h", [mx, my, zb + 60], [[0, 0], [24, 0], [24, 26], [0, 26]], "dark", axis="z")

    def bow_tray(s, xa):
        """XYQ-5/6: wooden tray on a chrome bow frame with diagonal struts, black knob on a threaded rod."""
        d, DP = s.d, s.DP
        ax, ay = s.R(xa, s.top)
        tr = rot("z", 12, [ax + 50, ay + 40, 0])
        top_pad(d, "tray", ax + 50, ax + 500, 20, DP - 20, ay + 40, ay + 62, "wood", cr=30, r=5, rot=tr)
        for nm, z in (("a", 70), ("b", DP - 70)):
            d.tube(f"bow-{nm}", [[ax + 60, ay + 30, z], [ax + 470, ay + 30, z]], 20, "chrome", rot=tr)
            bx, by = s.R(xa + 150, s.py - 20)
            d.cyl(f"strut-{nm}", [bx, by, z], [ax + 300, ay + 60, z], 18, "chrome")
            d.cyl(f"strut2-{nm}", [bx, by, z], [ax + 470, ay + 110, z], 18, "chrome")
        d.cyl("knob-rod", [ax + 100, ay - 60, 60], [ax + 100, ay - 60, -100], 16, "chrome")
        d.lathe("knob", [ax + 100, ay - 60, -100], [[0, 0], [26, 0], [26, 30], [0, 30]], "dark", axis="z")
        bx, by = s.R(xa + 330, s.py - 30)
        d.cyl("knob2-rod", [bx, by, DP - 60], [bx, by, DP + 60], 16, "chrome")
        d.lathe("knob2", [bx, by, DP + 60], [[0, 0], [24, 0], [24, 28], [0, 28]], "dark", axis="z")

    def console(s, x, panel="plastic#1f5a63"):
        d, DP = s.d, s.DP
        z = DP - 45
        d.box("con-post", [x - 30, 285, z - 30, x + 30, 1040, z + 30], "frame", r=6)
        d.box("con-foot", [x - 90, 225, z - 40, x + 90, 300, z + 40], "frame", r=6)
        cr = rot("x", 35, [x, 1080, z])
        d.box("con-box", [x - 200, 1030, z - 140, x + 200, 1110, z + 140], "frame", r=14, rot=cr)
        d.box("con-panel", [x - 175, 1110, z - 115, x + 175, 1114, z + 110], panel, r=6, rot=cr)
        d.box("con-led", [x - 100, 1113, z - 90, x - 55, 1117, z - 60], "gloss#ff3b30", r=2, soft=True, rot=cr,
              repeat=rep(3, [55, 0, 0]))
        d.box("con-led2", [x + 95, 1113, z - 90, x + 160, 1117, z - 60], "gloss#ff3b30", r=2, soft=True, rot=cr)
        d.box("con-keys", [x - 70, 1113, z + 10, x - 40, 1116, z + 35], "plastic#c9d6dc", r=2, soft=True, rot=cr,
              repeat=rep(5, [45, 0, 0]), copies=[[0, 0, 45]])
        d.lathe("con-knob", [x - 150, 1118, z - 40], [[0, 0], [40, 0], [44, 18], [30, 40], [0, 44]], "chrome", rot=cr)
        d.tube("con-wire", [[x - 120, 1040, z + 60], [x - 150, 700, z + 70], [x - 140, 420, z + 40]], 5, "dark", bend=200, soft=True)
        d.tube("con-wire2", [[x - 60, 1040, z + 70], [x - 80, 650, z + 80], [x - 60, 430, z + 40]], 5, "dark", bend=200, soft=True)
        d.coil("con-coil", [x - 210, 560, z + 20], [x - 260, 320, z + 30], 30, 8, 16, "dark", soft=True)

    def save(s):
        hx, hy = s.R(s.xh, s.top)
        H = max(hy, s.R(s.xh, s.py - 55)[1], getattr(s, "hmax", 0)) + 10
        s.d.d["size"][2] = int(round(H / 10) * 10)
        s.d.save()


def xyq_1():
    t = Tilt("xyq-1", 1950, 750, 72, {"frame": "metal#c6c9ce"})
    t.board(); t.base(rest="bar", sticker=False); t.foot("plate"); t.tray("wood", t.xh + 600, out=500, over=55); t.save()


def xyq_2():
    t = Tilt("xyq-2", 2000, 800, 50, {})
    t.board(); t.base(rest="rect"); t.foot("pedals"); t.tray("grey", t.xh + 520, out=520, tilt=50); t.save()


def xyq_3():
    t = Tilt("xyq-3", 2000, 800, 35, {})
    t.board(); t.base(rest="u"); t.foot("blue"); t.tray("lectern", t.xh + 420)
    d = t.d
    d.box("ctl", [560, t.base_top, 300, 900, t.base_top + 90, 560], "frame", r=12)
    d.box("ctl-scr", [600, t.base_top + 90, 330, 760, t.base_top + 94, 470], "gloss#3a86c8", r=4)
    d.cyl("ctl-btn", [800, t.base_top + 90, 360], [800, t.base_top + 96, 360], 18, "dark", copies=[[40, 0, 0], [0, 0, 50], [40, 0, 50]])
    d.box("ctl-plate", [520, t.base_top - 10, 280, 940, t.base_top, 580], "frame", r=4)
    t.console(t.W - 330)
    t.save()


def xyq_5():
    t = Tilt("xyq-5", 2000, 800, 62, {}, py=600)
    t.board(); t.base(lift=True, rest=None); t.foot("green"); t.bow_tray(t.xh + 520); t.save()


def xyq_6():
    t = Tilt("xyq-6", 2000, 800, 62, {"pad": "leather#a9cdef", "strap": "fabric#9cc4ec"}, py=600)
    t.board(); t.base(lift=True, rest=None); t.foot("green"); t.bow_tray(t.xh + 520)
    t.console(t.W - 330, panel="plastic#d9dde2")   # (photo: a light panel with red LED windows)
    t.save()


ids = sys.argv[1:] or ["xyq-1", "xyq-2", "xyq-3", "xyq-5", "xyq-6"]
for i, fn in (("xyq-1", xyq_1), ("xyq-2", xyq_2), ("xyq-3", xyq_3), ("xyq-5", xyq_5), ("xyq-6", xyq_6)):
    if i in ids: fn()
