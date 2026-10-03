"""Batch table-2, Adult Rehabilitation catalogue items: XY-46 OT desk, XY-70 strap table, XY-71 mat table,
XY-100 cervical traction chair.  python3 table2.py <id> [<id> ...] (all when none given)."""
import sys, math
from lib import D, rot
from sflib import T, poly_path, rrect_pts, stadium_pts, round_poly, inset


# ====================================================================== XY-46: OT desk, crank height adjustment
def xy46():
    W, DP, H = 1500, 800, 850
    d = D("xy-46", [W, DP, H], {"wood": "wood#e6c28c", "edge": "wood#f0d9b0", "frame": "plastic#f1f2f4",
                                  "dark": "metal#4b4f55", "cap": "rubber#1f2124", "crank": "metal#7a4b40"})
    t = 28
    d.box("top", [0, H - t, 0, W, H, DP], "wood", r=5)
    d.box("top-edge", [-1, H - t + 4, -1, W + 1, H - t + 10, DP + 1], "edge", r=2)       # laminate core line
    for k, x in enumerate((360, W - 360)):          # legs ~a quarter of the length in from each end (photo)
        d.box(f"plate{k}", [x - 55, H - t - 12, DP / 2 - 110, x + 55, H - t, DP / 2 + 110], "frame", r=4)
        d.box(f"leg{k}", [x - 36, 250, DP / 2 - 36, x + 36, H - t - 12, DP / 2 + 36], "frame", r=5)
        d.box(f"sleeve{k}", [x - 40, 55, DP / 2 - 40, x + 40, 260, DP / 2 + 40], "dark", r=4)
        d.box(f"foot{k}", [x - 30, 12, 50, x + 30, 62, DP - 50], "frame", r=6)
        d.box(f"glide{k}", [x - 26, 0, 55, x + 26, 14, 110], "cap", r=4, copies=[[0, 0, DP - 165]])
        d.box(f"footcap{k}", [x - 31, 14, 46, x + 31, 60, 54], "cap", r=3, copies=[[0, 0, DP - 100]])
    d.box("stretcher", [390, 20, DP / 2 - 28, W - 390, 70, DP / 2 + 28], "frame", r=5)
    # crank on the right end: shaft out under the top, arm down, grip
    # crank (photo): the shaft runs out of the right leg's head towards the right end, the arm drops, the grip points
    # out to the right; it all stays under the top
    xs, ys, zs = W - 360, H - t - 45, DP / 2 + 60
    d.cyl("crank-shaft", [xs, ys, zs], [W - 140, ys, zs], 16, "crank")
    d.add("crank-arm", "bar", "crank", **{"from": [W - 140, ys, zs], "to": [W - 115, ys - 160, zs + 50]}, section=[16, 26], r=6)
    d.cyl("crank-grip", [W - 115, ys - 160, zs + 50], [W - 30, ys - 160, zs + 50], 26, "crank")
    d.save()


# ====================================================================== XY-70: low training table with three straps
def xy70():
    W, DP, H = 1960, 720, 450
    d = T("xy-70", [W, DP, H], {"pad": "leather#8fb8e0", "strap": "leather#86b0dc"})
    y, t = 370, 80
    d.pad("top", 0, W, 0, DP, y, t=t, cr=45, er=30, hole=(260, DP / 2, 260, 120), plug=False, board=0)
    d.add("hole-floor", "slab", "frame", plane="top", outline=poly_path(stadium_pts(260, DP / 2, 280, 140)), w=[y - 12, y - 4], r=2)
    # white apron, end rails
    d.box("apron", [60, y - 70, 30, W - 60, y, 70], "frame", r=4, copies=[[0, 0, DP - 100]])
    d.box("apron-end", [60, y - 70, 70, 100, y, DP - 70], "frame", r=4, copies=[[W - 160, 0, 0]])
    # legs (white square) with black feet, knee braces, end stretchers
    for k, (x, z) in enumerate(((140, 55), (W - 140, 55), (140, DP - 55), (W - 140, DP - 55))):
        d.box(f"leg{k}", [x - 25, 40, z - 25, x + 25, y - 70, z + 25], "frame", r=4)
        d.box(f"foot{k}", [x - 28, 0, z - 28, x + 28, 45, z + 28], "cap", r=4)
        o = 1 if x < W / 2 else -1
        d.add(f"brace{k}", "bar", "frame", **{"from": [x, 210, z], "to": [x + o * 170, y - 70, z]}, section=[22, 30], r=4)
    d.box("end-stretch", [115, 130, 55, 165, 170, DP - 55], "frame", r=4, copies=[[W - 280, 0, 0]])
    d.box("long-stretch", [165, 130, DP / 2 - 20, W - 165, 170, DP / 2 + 20], "frame", r=4)
    # chrome bars along both sides under the apron (the straps wrap round them), brackets
    for k, z in enumerate((DP + 12, -12)):
        d.cyl(f"bar{k}", [260, y - 95, z], [1460, y - 95, z], 26, "chrome")
        for j, x in enumerate((260, 1460)):
            d.box(f"bar{k}-br{j}", [x - 15, y - 110, min(z, 30 if z < 0 else DP - 30), x + 15, y - 70, max(z, 30 if z < 0 else DP - 30)], "frame", r=3)
    # three wide padded straps over the top, down the front and back round the chrome bars
    # positions from the photo: the first strap crosses the face hole, the second is ~a third of the way, the third
    # just past the middle
    for k, (x, w) in enumerate(((240, 150), (620, 160), (1320, 180))):
        d.box(f"strap{k}", [x - w / 2, y + t - 6, -8, x + w / 2, y + t + 14, DP + 8], "strap", r=8, puff=2)
        d.box(f"strap{k}-f", [x - w / 2, y - 120, DP + 2, x + w / 2, y + t + 10, DP + 20], "strap", r=8)
        d.box(f"strap{k}-b", [x - w / 2, y - 120, -20, x + w / 2, y + t + 10, -2], "strap", r=8)
        d.decal(f"strap{k}-seam", [x, y + t + 14.5, DP / 2], [w - 40, DP - 40], "top", "leather#a7c6e8")
        d.box(f"strap{k}-buckle", [x - 18, y - 70, DP + 18, x + 18, y - 52, DP + 24], "plastic#9aa3ad", r=3)
    d.save()


# ====================================================================== XY-71: PT mat table
def xy71():
    W, DP, H = 1910, 1250, 490
    d = T("xy-71", [W, DP, H], {"pad": "leather#8fb8e0"})
    y, t = 400, 90
    d.pad("top", 0, W, 0, DP, y, t=t, cr=70, er=38, board=0)
    d.box("apron", [70, y - 70, 50, W - 70, y, 90], "frame", r=4, copies=[[0, 0, DP - 140]])
    d.box("apron-end", [70, y - 70, 90, 110, y, DP - 90], "frame", r=4, copies=[[W - 180, 0, 0]])
    d.box("apron-x", [W / 2 - 20, y - 60, 90, W / 2 + 20, y - 10, DP - 90], "frame", r=4)
    for k, (x, z) in enumerate(((120, 100), (W - 120, 100), (120, DP - 100), (W - 120, DP - 100))):
        d.box(f"leg{k}", [x - 35, 45, z - 35, x + 35, y - 70, z + 35], "frame", r=5)
        d.box(f"foot{k}", [x - 38, 0, z - 38, x + 38, 50, z + 38], "cap", r=5)
        d.box(f"cap{k}", [x - 38, y - 70, z - 38, x + 38, y - 50, z + 38], "cap", r=3)
    # black plugs on the ends of the long apron rails (photo: at the corners, on the end faces)
    d.box("apron-plug", [62, y - 66, 52, 70, y - 4, 88], "cap", r=2, copies=[[W - 132, 0, 0], [0, 0, DP - 140], [W - 132, 0, DP - 140]])
    # labels on the END apron (photo: the dark-blue label mid-way along the right end, a small one by the front corner)
    d.decal("label", [W - 70 + 0.5, y - 35, DP * 0.46], [330, 30], "right", "gloss#2f5fa8")
    d.decal("label-txt", [W - 70 + 1, y - 35, DP * 0.46 - 20], [240, 8], "right", "plastic#dfe6f0")
    d.decal("label2", [W - 70 + 0.5, y - 35, DP - 130], [60, 30], "right", "gloss#2f5fa8")
    d.save()


# ====================================================================== XY-100: cervical traction chair
def spool_row(d, id, x0, n, step, y, z):
    """A row of yellow/black massage spools on a horizontal axle along x (spool length 95)."""
    rp = {"n": n, "step": [step, 0, 0]}
    d.cyl(id + "-axle", [x0 - 20, y, z], [x0 + (n - 1) * step + 115, y, z], 14, "frame")
    d.cyl(id + "-a", [x0, y, z], [x0 + 26, y, z], 74, "black", repeat=rp)
    d.cyl(id + "-y", [x0 + 26, y, z], [x0 + 69, y, z], 62, "yellow", repeat=rp)
    d.cyl(id + "-b", [x0 + 69, y, z], [x0 + 95, y, z], 74, "black", repeat=rp)


def xy100():
    W, DP, H = 980, 1050, 1980
    d = D("xy-100", [W, DP, H], {"frame": "metal#b9bdc3", "seat": "leather#7f9dcd", "black": "rubber#1d1e20",
                                   "yellow": "plastic#f2b31f", "teal": "gloss#2fb2a6", "sling": "fabric#1f4f4c",
                                   "white": "plastic#f1f2f4", "dark": "plastic#2b2e33", "grey": "plastic#b8bec6",
                                   "blue": "gloss#2b3f9a"})
    cx = 450                                         # chair centre line
    # ---- base: side floor rails, cross tubes, curved front legs, castors
    for k, x in enumerate((170, 730)):
        d.tube(f"rail{k}", [[x, 60, 110], [x, 60, 720], [x + (60 if x < cx else -60), 380, 800]], 34, "frame", bend=120)
        d.add(f"castor{k}", "caster", at=[x, 0, 130], d=50)
    d.cyl("cross-back", [170, 60, 140], [730, 60, 140], 30, "frame")
    d.cyl("cross-mid", [170, 60, 600], [730, 60, 600], 30, "frame")
    for k, x in enumerate((240, 660)):           # front legs from the seat front down to the foot board
        d.tube(f"fleg{k}", [[x, 400, 780], [x, 330, 860], [x, 60, 930]], 32, "frame", bend=110)
        d.add(f"fcastor{k}", "caster", at=[x + (-30 if x < cx else 30), 0, 925], d=50)
    # ---- foot roller board at the front
    d.box("fb-frame", [250, 40, 900, 650, 70, 1045], "frame", r=6)
    for k, x0 in enumerate((265, 460)):
        d.box(f"fb-pad{k}", [x0, 70, 915, x0 + 175, 100, 1030], "yellow", r=6)
        d.box(f"fb-rib{k}", [x0 + 8, 98, 920, x0 + 18, 112, 1025], "plastic#e09a10", r=4, repeat={"n": 7, "step": [24, 0, 0]})
        d.box(f"fb-end{k}", [x0 - 8, 60, 1028, x0 + 183, 95, 1045], "black", r=4)
    # ---- seat on a dark mechanism
    d.box("seat", [cx - 225, 430, 380, cx + 225, 490, 830], "seat", r=26, puff=4)
    d.box("seat-mech", [cx - 110, 330, 500, cx + 110, 430, 700], "dark", r=12)
    d.cyl("seat-post", [cx, 60, 600], [cx, 300, 600], 70, "frame")
    for k, x in enumerate((240, 660)):
        d.box(f"seat-rail{k}", [x - 15, 400, 380, x + 15, 430, 800], "frame", r=4)
        d.cyl(f"seat-leg{k}", [x, 60, 420], [x, 400, 420], 30, "frame")
    # ---- armrests: black curved loops on grey supports
    for k, x in enumerate((205, 695)):
        d.add(f"arm{k}", "sweep", "black", path=[[x, 470, 790], [x, 770, 800], [x, 800, 650], [x, 720, 470], [x, 580, 450]],
              section=[34, 34], shape="round", bend=110)
        d.cyl(f"arm{k}-bar", [x, 470, 760], [x, 720, 560], 22, "frame")
    # ---- column with the pulley arm, hand wheel, halter
    colx, colz = 330, 230
    d.box("column", [colx - 30, 60, colz - 30, colx + 30, 1760, colz + 30], "frame", r=5)
    d.box("column-foot", [colx - 45, 40, colz - 60, colx + 45, 80, colz + 60], "frame", r=6)
    tip = [cx + 10, 1965, 480]
    d.add("boom", "bar", "frame", **{"from": [colx, 1740, colz], "to": tip}, section=[40, 40], r=5)
    d.cyl("boom-pulley", [tip[0] - 15, tip[1] - 20, tip[2]], [tip[0] + 15, tip[1] - 20, tip[2]], 44, "frame")
    d.cyl("rope", [tip[0], tip[1] - 40, tip[2]], [tip[0], 1500, tip[2]], 5, "white", soft=True)
    d.cyl("rope2", [colx, 1745, colz + 30], [tip[0] - 5, tip[1] - 20, tip[2] - 10], 5, "white", soft=True)
    d.cyl("spreader", [cx - 135, 1490, 480], [cx + 145, 1490, 480], 22, "white")
    for k, x in enumerate((cx - 130, cx + 140)):
        d.strap(f"halter-side{k}", [[x, 1490, 480], [x + (15 if k == 0 else -15), 1330, 500]], [36, 4], "white")
    d.strap("halter-sling", [[cx - 115, 1335, 500], [cx - 80, 1240, 540], [cx + 10, 1215, 560], [cx + 95, 1250, 540], [cx + 125, 1335, 500]],
            [70, 6], "sling", bend=60)
    d.cyl("wheel", [colx - 110, 1300, colz + 20], [colx - 60, 1300, colz + 20], 200, "teal")
    d.cyl("wheel-hub", [colx - 125, 1300, colz + 20], [colx - 30, 1300, colz + 20], 60, "teal")
    d.cyl("wheel-spool", [colx + 30, 1300, colz + 20], [colx + 70, 1300, colz + 20], 130, "teal")
    # ---- massage-roller back frame: two posts, rows of spools
    for k, x in enumerate((340, 560)):
        d.box(f"rpost{k}", [x - 18, 430, 300, x + 18, 1160, 336], "frame", r=4)
    d.box("rpost-top", [322, 1140, 300, 578, 1170, 336], "frame", r=4)
    spool_row(d, "row1", 220, 4, 125, 1130, 360)
    spool_row(d, "row2", 220, 4, 125, 1050, 380)
    spool_row(d, "row3", 340, 2, 125, 950, 380)
    spool_row(d, "row4", 340, 2, 125, 850, 380)
    # ---- T handle post on the right, twist disc on an arm at the front right
    d.box("t-post", [700, 60, 430, 730, 1150, 460], "frame", r=4)
    d.cyl("t-bar", [610, 1155, 445], [830, 1190, 445], 30, "blue")
    d.cyl("t-knob", [730, 820, 445], [775, 820, 445], 36, "black")
    d.cyl("t-collar", [715, 1100, 445], [715, 1160, 445], 40, "dark")
    d.add("disc-arm", "bar", "frame", **{"from": [730, 90, 760], "to": [850, 90, 780]}, section=[30, 30], r=4)
    # twist disc (photo): a flat round plate with a ribbed rim on a small black foot
    d.lathe("disc-foot", [855, 0, 780], [[50, 0], [50, 30], [28, 40], [0, 40]], "black")
    d.lathe("disc", [855, 40, 780], [[28, 0], [28, 40], [130, 45], [135, 62], [130, 78], [0, 78]], "grey")
    d.lathe("disc-ring", [855, 118, 780], [[95, 0], [95, 3], [0, 3]], "plastic#7f868f")
    d.save()


ALL = {"xy-46": xy46, "xy-70": xy70, "xy-71": xy71, "xy-100": xy100}
if __name__ == "__main__":
    for k in (sys.argv[1:] or list(ALL)):
        ALL[k]()
