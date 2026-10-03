"""XY-K-SF treatment tables, batch table-2 (Treatment Table.pdf p5-8).
python3 sf2.py <id> [<id> ...]   — writes only the named designs (all of this file's ids when none given).
Reuses the bases of sf.py (batch table-1): the old Z-column base and the new swan-arm base.
Frame: the length along x, the width along z (front z = D = the long side the photo looks at), y up.
Each table is drawn in the base's own orientation and flipped (flip_design) when the photo shows the base mirrored:
 - old Z base unflipped: columns slope down to the right ("\\"), control box at the right end;
 - swan base unflipped: arms run from the upper left down to their posts on the right ("\\").
Every photo of this batch is checked for which way its columns/arms lean; the top is drawn so that after the flip
the head is where the photo shows it."""
import sys, math
import sf
from lib import rot
from sflib import *

DEP = 700


def z_column2(d, id, xa, span, yt, yb, z0, z1):
    """Old lift column as in the photos (SF-8 is the clearest; pre-flip, head on the left): a short top block under
    the apron at xa, a broad straight beam widening downwards and sloping ~40 deg down-right (grey upper face), landing
    on the far end of a long low foot block (it carries the lettering, black plugs on its corners at the beam end).
    Between the top block, the beam's underside and the foot block the column is open towards the head side."""
    xp = xa + span
    FB = 125                                         # foot block height
    lo = quad((xa + 180, yb + FB), (xa + 95, yb + FB + 70), (xa + 62, yt - 80), 8)   # beam underside, foot -> top block
    body = [(xa, yt), (xa + 150, yt), (xp, yb + FB + 25), (xp, yb), (xa + 10, yb), (xa + 10, yb + FB)] + lo + [(xa, yt - 80)]
    d.add(f"{id}-body", "slab", "frame", plane="front", outline=poly_path(body), w=[z0, z1], r=8)
    up = [(xa + 150, yt), (xp, yb + FB + 25)]
    cover = up + [(xp - 8, yb + FB + 25 - 30), (xa + 132, yt - 26)]
    d.add(f"{id}-cover", "slab", "grey", plane="front", outline=poly_path(cover), w=[z0 - 6, z1 + 6], r=6)
    # foot block wider than the beam (front and back faces proud), black plugs on its top corners at the beam end
    d.box(f"{id}-foot", [xa + 10, yb, z0 - 40, xp, yb + FB, z1 + 40], "frame", r=8)
    d.box(f"{id}-pcap", [xp - 46, yb + FB, z0 - 41, xp + 1, yb + FB + 12, z0 + 5], "cap", r=3, copies=[[0, 0, z1 - z0 - 5 + 0]])
    d.bolt(f"{id}-b1", [xa + 40, yt - 40, z1], copies=[[0, 0, -(z1 - z0)]])
    d.bolt(f"{id}-b2", [xp - 30, yb + FB - 30, z1 + 40], copies=[[0, 0, -(z1 - z0) - 80]])


COLS = ((460, 440), (1040, 440))


def old_base(d):
    """sf.z_base with this batch's columns, a round black drive under the apron in the gap between the columns
    (the photos show no box between the columns at base level) and Ø70 castors (the photos' castors are ~70)."""
    sf.z_base(d, top=TOP, cols=COLS, ctl=None, lettering=False, motor=None)
    xm = (COLS[0][0] + COLS[0][1] + COLS[1][0]) / 2
    d.cyl("motor", [xm, TOP - 35, DEP / 2 - 110], [xm, TOP - 35, DEP / 2 + 110], 90, "plastic#2b2e33")
    for p in d.d["parts"]:
        if p["kind"] == "caster" and p["id"] == "castor":
            p["d"] = 70


def old_lettering(d, flipped):
    """Lettering centred on the two foot blocks, XIANG YU on the left one."""
    W = d.d["size"][0]
    ls = sorted((W - xa - sp) if flipped else (xa + 10) for xa, sp in COLS)
    lettering(d, ls[0] + 100, ls[1] + 100, y=322, z=DEP - 150 + 40.5)


sf.z_column = z_column2


def ctl_box(d, xb1, zf1):
    """Control box in the base at the foot end (pre-flip x high): white tray, blue panel tilted to the front,
    three black knobs, black cable loop."""
    x0, x1 = xb1 - 270, xb1 - 60
    d.box("ctl-box", [x0, 150, zf1 - 250, x1, 245, zf1 - 15], "frame", r=10)
    r = rot("x", 20, [0, 245, zf1 - 15])
    d.box("ctl-face", [x0 + 12, 236, zf1 - 235, x1 - 12, 252, zf1 - 25], "gloss#2a66ad", r=4, rot=r)
    d.cyl("ctl-knob", [x0 + 55, 250, zf1 - 170], [x0 + 55, 266, zf1 - 170], 24, "bolt", rot=r, repeat={"n": 3, "step": [45, 0, 0]})
    d.tube("ctl-cable", [[x1 - 20, 240, zf1 - 200], [x1 + 30, 300, zf1 - 160], [x1 + 30, 270, zf1 - 60], [x1 - 10, 220, zf1 - 40]], 12, "bolt", bend=40, soft=True)


def setw(w, dep=700):
    global DEP
    sf.W = w; sf.DEP = dep; DEP = dep


def letters(d, id, x, y, z, n, step=34, w=20, h=26, gap=None):
    """Grey lettering on a rail face: n letter blocks starting at x (gap = index after which a word gap follows)."""
    d.add(id, "decal", at=[x, y, z], size=[w, h], face="front", mat="letter", repeat={"n": n, "step": [step, 0, 0]})


def lettering(d, x1, x2, y=325, z=None):
    """'XIANG YU' on the left column's foot block, 'MEDICAL' on the right one (final coordinates, after any flip);
    x1, x2 = left ends of the two foot blocks."""
    z = z or DEP - 150 + 0.5
    letters(d, "txt-xiang", x1 + 25, y, z, 5, step=25, w=15, h=22)
    letters(d, "txt-yu", x1 + 165, y, z, 2, step=25, w=15, h=22)
    letters(d, "txt-medical", x2 + 30, y, z, 7, step=25, w=15, h=22)


def split3(d, id, x0, x1, y, t, wc, ang, piv, hole=True, z_far=None, flap_ang=None, hole_len=240, hole_w=95, hole_dz=0, plugs=True):
    """Head section split in three along the width: far flap, face piece (breathing hole), near flap.
    Pieces span x0..x1, all rotated by ang (deg about z) about piv = x of the hinge; flaps may use flap_ang."""
    zc0, zc1 = (DEP - wc) / 2, (DEP + wc) / 2
    if z_far is not None:
        zc0, zc1 = z_far, z_far + wc
    r = rot("z", ang, [piv, y, DEP / 2])
    rf = rot("z", flap_ang if flap_ang is not None else ang, [piv, y, DEP / 2])
    cx = (x0 + x1) / 2
    d.pad(id + "-face", x0, x1, zc0, zc1, y, t=t, cr=55, er=28, r=r,
          hole=(cx, (zc0 + zc1) / 2 + hole_dz, hole_len, hole_w) if hole else None, plug=plugs)
    d.pad(id + "-far", x0 + 20, x1, 0, zc0 - 6, y, t=t, cr=50, er=26, r=rf)
    d.pad(id + "-near", x0 + 20, x1, zc1 + 6, DEP, y, t=t, cr=50, er=26, r=rf)


def head_strut(d, id, x, y, z, out=-1, mat="steel"):
    """Steel arm-rest strut sticking out under the head end, down and out at ~30 deg, black knob."""
    d.add(id, "bar", mat, **{"from": [x, y, z], "to": [x + out * 170, y - 100, z]}, section=[30, 22], r=4)
    d.cyl(id + "-knob", [x + out * 20, y - 30, z - 40], [x + out * 20, y - 30, z - 80], 40, "bolt")


# ====================================================================== old Z base family
TOP, YP, TP = 595, 677, 80        # apron top, pad underside, pad thickness


def old_head_bar(d, xend=150, inward=False):
    """Steel U frame at rail height sticking out of the head end of the base (pre-flip: head at x = 0).
    inward: folded up into the base, rising from the end beam towards the column (SF-6 photo), black gas spring by it."""
    if inward:
        d.tube("head-loop", [[xend - 10, 262, 150], [xend + 230, 360, 150], [xend + 230, 360, DEP - 150], [xend - 10, 262, DEP - 150]],
               22, "steel", bend=30)
        d.cyl("head-loop-gas", [xend + 250, 262, DEP - 200], [xend + 250, 345, DEP - 200], 34, "bolt")
        return
    d.tube("head-loop", [[xend + 30, 240, 150], [xend - 110, 228, 150], [xend - 110, 228, DEP - 150], [xend + 30, 240, DEP - 150]],
           22, "steel", bend=30)


def sf6():
    """Head left (photo) = unflipped base: head raised 25 deg split in 3, body, two full-length leg pads."""
    setw(2000)
    d = T("xy-k-sf-6", [2000, DEP, 950])
    hx = 440
    split3(d, "head", 0, hx - 6, YP, TP, 280, -25, hx, hole_len=230, hole_w=100)
    d.box("head-arm", [250, YP - 40, 70, hx, YP - 12, 95], "cap", r=5, rot=rot("z", -25, [hx, YP, DEP / 2]), copies=[[0, 0, DEP - 165]])
    head_strut(d, "strut", 90, YP - 60, 120, out=-1, mat="bolt")
    d.pad("body", hx + 6, 1000, 0, DEP, YP, t=TP)
    d.pad("leg-far", 1011, 2000, 0, DEP / 2 - 5, YP, t=TP, cr=50)
    d.pad("leg-near", 1011, 2000, DEP / 2 + 5, DEP, YP, t=TP, cr=50)
    sf.hinge(d, "hinge1", hx, YP)
    sf.hinge(d, "hinge2", 1005, YP)
    old_base(d)
    old_head_bar(d, inward=True)
    ctl_box(d, 1875, DEP - 40)
    old_lettering(d, False)
    d.save()


def sf7():
    """Head right (photo): drawn head-left, flipped. Head 40 deg in 3, chest, body, split legs (near dropped)."""
    setw(2000)
    d = T("xy-k-sf-7", [2000, DEP, 1030])
    hx = 440
    split3(d, "head", 0, hx - 6, YP, TP, 250, -40, hx, hole_len=250, hole_w=95)
    d.box("head-arm", [250, YP - 40, 70, hx, YP - 12, 95], "cap", r=5, rot=rot("z", -40, [hx, YP, DEP / 2]), copies=[[0, 0, DEP - 165]])
    d.pad("chest", hx + 6, 820, 0, DEP, YP, t=TP)
    d.pad("body", 831, 1310, 0, DEP, YP, t=TP)
    sf.hinge(d, "hinge1", hx, YP)
    sf.hinge(d, "hinge2", 825, YP)
    lx = 1321
    fr_ = rot("z", 3, [lx, YP, DEP / 2])
    d.pad("leg-far", lx, 2000, 0, DEP / 2 - 6, YP, t=TP, cr=50, r=fr_)
    # far leg: white rail and black gas spring along its underside (photo)
    d.box("leg-far-rail", [lx + 20, YP - 45, 40, 1880, YP - 12, 70], "frame", r=5, rot=fr_)
    d.cyl("gas-far", [lx + 60, YP - 60, 95], [lx + 330, YP - 60, 95], 30, "bolt", rot=fr_)
    d.cyl("gas-far-rod", [lx + 330, YP - 60, 95], [1860, YP - 60, 95], 12, "steel", rot=fr_)
    lr = rot("z", -11, [lx, YP, DEP / 2])
    d.pad("leg-near", lx, 2000, DEP / 2 + 6, DEP, YP, t=TP, cr=50, r=lr)
    d.box("leg-near-rail", [lx + 20, YP - 45, DEP - 70, 1880, YP - 12, DEP - 40], "frame", r=5, rot=lr)
    d.box("hinge-blk", [lx - 35, YP - 60, 50, lx + 25, YP + 5, 95], "cap", r=5, copies=[[0, 0, DEP - 145]])
    d.cyl("gas-near", [1180, TOP + 30, DEP - 30], [1560, YP - 85, DEP - 30], 30, "bolt")
    d.cyl("gas-near-rod", [1560, YP - 85, DEP - 30], [1800, YP - 125, DEP - 30], 12, "steel")
    old_base(d)
    old_head_bar(d)
    ctl_box(d, 1875, DEP - 40)
    flip_design(d)
    old_lettering(d, True)
    d.save()


def sf8():
    """Head right (photo): drawn head-left, flipped. Head 35 deg in 3 + strut, chest split in two halves,
    two leg sections in a V."""
    setw(2000)
    d = T("xy-k-sf-8", [2000, DEP, 1000])
    hx = 430
    split3(d, "head", 0, hx - 6, YP, TP, 280, -35, hx, z_far=170, hole_len=230, hole_w=80, flap_ang=-30)
    d.box("head-arm", [250, YP - 40, 70, hx, YP - 12, 95], "cap", r=5, rot=rot("z", -35, [hx, YP, DEP / 2]), copies=[[0, 0, DEP - 165]])
    head_strut(d, "strut", 110, YP - 40, 120, out=-1)
    d.pad("chest-far", hx + 6, 960, 0, DEP / 2 - 5, YP, t=TP, cr=50)
    d.pad("chest-near", hx + 6, 960, DEP / 2 + 5, DEP, YP, t=TP, cr=50)
    sf.hinge(d, "hinge1", hx, YP)
    lx = 971
    d.pad("leg-far", lx, 2000, 0, DEP / 2 - 8, YP, t=TP, cr=50, r=rot("y", -3, [lx, YP, DEP / 2 - 8]))
    d.pad("leg-near", lx, 1990, DEP / 2 + 8, DEP, YP, t=TP, cr=50, r=rot("y", 4, [lx, YP, DEP / 2 + 8]))
    d.box("hinge-blk", [lx - 35, YP - 60, 50, lx + 25, YP + 5, 95], "cap", r=5, copies=[[0, 0, DEP - 145]])
    d.box("leg-rail", [lx + 20, YP - 45, DEP / 2 - 40, 1860, YP - 12, DEP / 2 - 10], "frame", r=5, rot=rot("y", -3, [lx, YP, DEP / 2 - 8]))
    old_base(d)
    old_head_bar(d)
    ctl_box(d, 1875, DEP - 40)
    flip_design(d)
    old_lettering(d, True)
    d.save()


def sf9():
    """Head right (photo): drawn head-left, flipped. Head 25 deg in 3 + strut, chest with a near arm flap (lower),
    body, split legs (near dropped on a gas spring)."""
    setw(2000, 720)
    d = T("xy-k-sf-9", [2000, DEP, 950])
    hx = 430
    split3(d, "head", 0, hx - 6, YP, TP, 300, -25, hx, z_far=150, hole_len=250, hole_w=100, flap_ang=-15)
    d.box("head-arm", [250, YP - 40, 70, hx, YP - 12, 95], "cap", r=5, rot=rot("z", -25, [hx, YP, DEP / 2]), copies=[[0, 0, DEP - 165]])
    head_strut(d, "strut", 110, YP - 40, 120, out=-1)
    d.pad("chest", hx + 6, 840, 0, 470, YP, t=TP, cr=50)
    d.pad("arm-near", hx + 40, 840, 478, DEP, YP - 30, t=TP, cr=50)
    d.box("arm-near-post", [600, TOP + 20, 560, 660, YP - 30, 620], "steel", r=4)
    d.pad("body", 851, 1330, 0, DEP, YP, t=TP)
    sf.hinge(d, "hinge1", hx, YP)
    sf.hinge(d, "hinge2", 845, YP)
    lx = 1341
    d.pad("leg-far", lx, 2000, 0, DEP / 2 - 6, YP, t=TP, cr=50)
    lr = rot("z", -12, [lx, YP, DEP / 2])
    d.pad("leg-near", lx, 2000, DEP / 2 + 6, DEP, YP, t=TP, cr=50, r=lr)
    d.box("leg-near-rail", [lx + 20, YP - 45, DEP - 70, 1880, YP - 12, DEP - 40], "frame", r=5, rot=lr)
    d.box("hinge-blk", [lx - 35, YP - 60, 50, lx + 25, YP + 5, 95], "cap", r=5, copies=[[0, 0, DEP - 145]])
    d.cyl("gas-near", [1180, TOP + 30, DEP - 30], [1560, YP - 85, DEP - 30], 30, "bolt")
    d.cyl("gas-near-rod", [1560, YP - 85, DEP - 30], [1800, YP - 130, DEP - 30], 12, "steel")
    old_base(d)
    old_head_bar(d)
    ctl_box(d, 1875, DEP - 40)
    flip_design(d)
    old_lettering(d, True)
    d.save()


# ====================================================================== new swan-arm base family (all flipped)
STOP = 632                     # swan top frame
SY, ST = STOP + 60, 60         # pad underside, thickness


def swan_fix(d, arms=((300, 780), (1050, 1530))):
    """Call right after sf.swan_base (pre-flip). The photos of this batch show no grey actuator sloping between the
    arms but a white horizontal beam just above the rails from the first arm's foot to the second arm's posts."""
    d.d["parts"] = [p for p in d.d["parts"] if p["id"] not in ("actuator", "actuator-rod")]
    d.ids -= {"actuator", "actuator-rod"}
    d.box("lift-beam", [arms[0][1] + 40, 262, DEP / 2 - 35, arms[1][1] - 40, 330, DEP / 2 + 35], "frame", r=6)


def sf5new():
    """Photo: head right raised 25 deg (face piece with slot, flaps), chest, long body; arms lean '/'.
    Drawn head-left on the unflipped swan base, then flipped."""
    setw(2000)
    d = T("xy-k-sf-5-new", [2000, DEP, 920])
    hx = 406
    # head (photo): a wide face piece from the far edge (slot near its near edge) and one narrow near flap lower
    hr_ = rot("z", -25, [hx, SY, DEP / 2])
    d.pad("head-face", 0, hx - 6, 0, 474, SY, t=ST, cr=55, er=24, r=hr_, hole=(hx / 2 - 10, 340, 220, 60))
    d.pad("head-near", 20, hx - 6, 482, DEP, SY, t=ST, cr=50, er=22, r=rot("z", -12, [hx, SY, DEP / 2]))
    d.box("head-rail", [120, SY - 45, 160, hx - 10, SY - 12, 195], "frame", r=5, rot=rot("z", -25, [hx, SY, DEP / 2]), copies=[[0, 0, DEP - 355]])
    head_strut(d, "strut", 120, SY - 40, DEP - 90, out=-1)
    d.pad("chest", hx + 6, 850, 0, DEP, SY, t=ST, er=22, cr=45)
    d.pad("body", 861, 2000, 0, DEP, SY, t=ST, er=22, cr=50)
    d.box("hinge", [hx - 25, SY - 50, 55, hx + 25, SY - 5, 80], "cap", r=4, copies=[[0, 0, DEP - 135], [450, 0, 0], [450, 0, DEP - 135]])
    d.cyl("head-gas", [700, 300, DEP / 2 - 60], [hx + 40, SY - 20, DEP / 2 - 60], 30, "bolt")
    d.box("lever", [1180, SY - 50, DEP - 150, 1260, SY - 20, DEP - 100], "cap", r=6, copies=[[-400, 0, 0]])
    sf.swan_base(d, top=STOP, xb0=250, xb1=1800, frame=(150, 1880))
    swan_fix(d)
    flip_design(d)
    d.save()


def sf6b():
    """Photo: split leg pads left, seat, long back right in two halves - near half raised 30 deg, far half flat
    (arm board); arms lean '/'. Drawn back-left, flipped."""
    setw(2000)
    d = T("xy-k-sf-6b", [2000, DEP, 1200])
    bx = 895
    br = rot("z", -30, [bx, SY, DEP / 2])
    d.pad("back", 0, bx - 6, 230, DEP, SY, t=ST, er=22, cr=50, r=br)
    d.pad("arm-board", 60, bx - 6, 0, 220, SY, t=ST, er=22, cr=50)
    d.box("back-rail", [120, SY - 45, DEP - 90, bx - 20, SY - 12, DEP - 55], "frame", r=5, rot=br, copies=[[0, 0, -(DEP - 360)]])
    # dark rail along the raised back's underside (photo: a dark line under the whole back), steel strut from the
    # top frame up to the back on the near side
    d.box("back-dark", [90, SY - 42, DEP / 2 + 30, bx - 70, SY - 14, DEP / 2 + 80], "bolt", r=6, rot=br)
    d.cyl("back-strut", [760, STOP + 30, DEP - 60], [600, SY + 150, DEP - 60], 24, "steel")
    d.cyl("back-strut-end", [760, STOP + 10, DEP - 60], [760, STOP + 50, DEP - 60], 34, "bolt")
    d.pad("seat", bx + 6, 1390, 0, DEP, SY, t=ST, er=22, cr=45)
    lx = 1401
    d.pad("leg-far", lx, 2000, 0, DEP / 2 - 5, SY, t=ST, er=22, cr=55, r=rot("z", 3, [lx, SY, DEP / 2]))
    d.pad("leg-near", lx, 1990, DEP / 2 + 5, DEP, SY - 15, t=ST, er=22, cr=55, r=rot("z", -3, [lx, SY, DEP / 2]))
    d.box("hinge", [bx - 25, SY - 50, 55, bx + 25, SY - 5, 80], "cap", r=4, copies=[[0, 0, DEP - 135], [500, 0, 0], [500, 0, DEP - 135]])
    # steel strut sticking down from under the leg end, black knob (photo)
    d.add("leg-strut", "bar", "steel", **{"from": [1670, SY - 30, DEP - 70], "to": [1760, SY - 190, DEP - 70]}, section=[30, 22], r=4)
    d.cyl("leg-knob", [1600, SY - 85, DEP - 60], [1600, SY - 85, DEP - 20], 40, "bolt")
    d.add("leg-coil", "coil", "plastic#e9ecef", **{"from": [1880, SY - 20, DEP - 60], "to": [1870, 260, DEP - 60]}, d=40, d2=8, turns=22, soft=True)
    sf.swan_base(d, top=STOP, xb0=350, xb1=1760, arms=((400, 830), (1140, 1630)), frame=(170, 1880))
    swan_fix(d, ((400, 830), (1140, 1630)))
    flip_design(d)
    d.save()


def sf7new():
    """Photo: head left (split in 3 with hole) continuing a chest raised 20 deg, middle, split legs right;
    arms lean '/' - drawn head-right, flipped. Grey gas-spring armrest post with a black handle at the head corner."""
    setw(2000)
    d = T("xy-k-sf-7-new", [2000, DEP, 1100])
    cx = 1100                                         # middle / chest hinge (pre-flip)
    a = 20
    d.pad("middle", 650, cx - 6, 0, DEP, SY, t=ST, er=22, cr=45)
    cr_ = rot("z", a, [cx, SY, DEP / 2])
    d.pad("chest", cx + 6, 1609, 0, DEP, SY, t=ST, er=22, cr=45, r=cr_)
    d.box("chest-rail", [cx + 30, SY - 45, 70, 1590, SY - 12, 105], "frame", r=5, rot=cr_, copies=[[0, 0, DEP - 175]])
    px = cx + 515 * math.cos(math.radians(a)); py = SY + 515 * math.sin(math.radians(a))
    split3(d, "head", px + 6, px + 380, py, ST, 280, a + 8, px, hole_len=200, hole_w=80, flap_ang=a + 4)
    lx = 639
    d.pad("leg-far", 0, lx, 0, DEP / 2 - 5, SY, t=ST, er=22, cr=55, r=rot("z", -4, [lx + 5, SY, DEP / 2]))
    d.pad("leg-near", 10, lx, DEP / 2 + 5, DEP, SY, t=ST, er=22, cr=55, r=rot("z", 8, [lx + 5, SY, DEP / 2]))
    d.box("leg-clamp", [40, SY - 70, DEP / 2 + 120, 120, SY - 25, DEP / 2 + 180], "cap", r=6, rot=rot("z", 8, [lx + 5, SY, DEP / 2]))
    d.box("leg-clamp2", [40, SY - 70, 80, 120, SY - 25, 140], "cap", r=6, rot=rot("z", -4, [lx + 5, SY, DEP / 2]))
    d.cyl("leg-gas", [lx - 30, STOP - 20, 140], [200, SY - 60, 140], 22, "steel")
    d.box("mid-lever", [880, SY - 55, DEP - 60, 960, SY - 20, DEP + 10], "cap", r=8)
    d.box("hinge", [cx - 25, SY - 50, 55, cx + 25, SY - 5, 80], "cap", r=4, copies=[[0, 0, DEP - 135], [lx - cx + 5, 0, 0], [lx - cx + 5, 0, DEP - 135]])
    # gas-spring armrest post at the head corner (near side) with a black handle bar
    d.cyl("arm-post", [1800, 250, DEP - 40], [1800, py + 120, DEP - 40], 22, "act")
    d.cyl("arm-post-top", [1800, py + 120, DEP - 40], [1800, py + 170, DEP - 40], 40, "bolt")
    # handle bar from the post top out past the head end and down (photo), steel with a black grip end
    d.add("arm-handle", "bar", "steel", **{"from": [1800, py + 160, DEP - 40], "to": [1950, py + 80, DEP + 20]}, section=[30, 30], r=8)
    d.cyl("arm-grip", [1950, py + 80, DEP + 20], [1990, py + 59, DEP + 25], 38, "bolt")
    sf.swan_base(d, top=STOP, xb0=250, xb1=1800, loop=False, frame=(600, 1700), cover="grey")
    swan_fix(d)
    flip_design(d)
    d.save()


def back_dark(d, id, x0, x1, z0, z1, y, r, mat="plastic#3a3f46"):
    """Dark-grey board under a raised back section."""
    d.box(id, [x0 + 8, y - 16, z0 + 8, x1 - 8, y + 1, z1 - 8], mat, r=6, rot=r)


def sf8b():
    """Photo: chair pose, back (hole, two narrow side pads, dark back cover) raised 65 deg at the left, seat,
    thigh in two halves, leg section (two halves) hanging 70 deg at the right; arms lean '/'. Drawn head-right, flipped."""
    W = 1750
    setw(W)
    top = 580
    y, t = top + 60, 60
    d = T("xy-k-sf-8b", [W, DEP, 1260])
    bx = W - 380                                       # seat / back hinge (pre-flip)
    br = rot("z", 65, [bx, y, DEP / 2])
    d.pad("back", bx + 6, bx + 660, 130, DEP - 130, y, t=t, er=24, cr=60, r=br, hole=(bx + 470, DEP / 2 + 30, 260, 110), board=0)
    back_dark(d, "back-cover", bx + 6, bx + 660, 130, DEP - 130, y, br)
    fr = rot("z", 62, [bx, y + 30, DEP / 2])
    d.pad("arm-far", bx + 20, bx + 560, 0, 118, y + 30, t=t, er=22, cr=50, r=fr, board=0)
    d.pad("arm-near", bx + 20, bx + 560, DEP - 118, DEP, y + 30, t=t, er=22, cr=50, r=fr, board=0)
    back_dark(d, "arm-far-cover", bx + 20, bx + 560, 0, 118, y + 30, fr)
    back_dark(d, "arm-near-cover", bx + 20, bx + 560, DEP - 118, DEP, y + 30, fr)
    d.add("arm-coil", "coil", "metal#c4c8cc", **{"from": [bx + 70, 300, DEP - 60], "to": [bx + 70, y + 120, DEP - 60]}, d=30, d2=6, turns=30)
    gy = y + 300 * math.sin(math.radians(65))
    gx = bx + 300 * math.cos(math.radians(65))
    d.cyl("grab-rod", [gx, gy, DEP - 60], [gx + 260, gy, DEP - 60], 22, "steel")
    d.box("grab-plate", [gx + 180, gy - 20, DEP - 90, gx + 280, gy + 20, DEP - 30], "bolt", r=6)
    d.pad("seat", W - 820, bx - 6, 0, DEP, y, t=t, er=22, cr=45)
    sx = W - 1270                                      # leg / thigh hinge (pre-flip)
    d.pad("thigh-far", sx + 6, W - 831, 0, DEP / 2 - 5, y, t=t, er=22, cr=45)
    d.pad("thigh-near", sx + 6, W - 831, DEP / 2 + 5, DEP, y - 15, t=t, er=22, cr=45)
    lr = rot("z", 70, [sx, y, DEP / 2])
    d.pad("leg-far", sx - 560, sx - 6, 0, DEP / 2 - 5, y, t=t, er=22, cr=55, r=lr)
    d.pad("leg-near", sx - 560, sx - 6, DEP / 2 + 5, DEP, y, t=t, er=22, cr=55, r=lr)
    d.cyl("thigh-gas", [W - 700, top - 20, DEP - 110], [sx - 40, y - 60, DEP - 110], 34, "steel")
    d.box("hinge", [bx - 25, y - 50, 55, bx + 25, y - 5, 80], "cap", r=4, copies=[[0, 0, DEP - 135], [sx - bx, 0, 0], [sx - bx, 0, DEP - 135]])
    # hand switch on a coiled cable hanging at the leg end (near side)
    lend = (sx - 520 * math.cos(math.radians(70)), y - 520 * math.sin(math.radians(70)))
    d.add("hs-coil", "coil", "bolt", **{"from": [lend[0] - 30, lend[1] + 200, DEP + 15], "to": [lend[0] - 20, lend[1] + 30, DEP + 35]}, d=40, d2=6, turns=12, soft=True)
    d.box("hand-switch", [lend[0] - 50, lend[1] - 100, DEP + 18, lend[0] + 10, lend[1] + 30, DEP + 58], "plastic#25282c", r=12)
    # photo: the base is short - its leg end lies under the thigh/leg hinge (the second arm's pivot is right there) and
    # the hanging leg section reaches out beyond it; the first arm's posts stand close to the head end
    sf.swan_base(d, top=top, xb0=460, xb1=1690, arms=((460, 865), (1160, 1500)), loop=False, frame=(420, 1370))
    swan_fix(d, ((460, 865), (1160, 1500)))
    # grey foot-control box hanging under the base at the head end, its white cable looping down to the floor
    d.box("pedal", [1430, 115, DEP / 2 - 110, 1600, 188, DEP / 2 + 110], "plastic#8e949b", r=10)
    d.tube("pedal-cable", [[1500, 120, DEP / 2 + 110], [1490, 30, DEP - 90], [1400, 25, DEP - 80], [1380, 120, DEP - 70]], 8, "plastic#e9ecef", bend=50, soft=True)
    flip_design(d)
    d.save()


def sf9new():
    """Photo: chair pose, back raised 62 deg at the left (chest with side bolsters + head with hole and flaps), seat
    with side pads, far leg section level to the right, near one hanging 65 deg; arms lean '/'. Drawn head-right, flipped."""
    W = 1950
    setw(W)
    d = T("xy-k-sf-9-new", [W, DEP, 1360])
    bx = W - 480
    a = 62
    br = rot("z", a, [bx, SY, DEP / 2])
    d.pad("chest", bx + 6, bx + 430, 0, DEP, SY, t=ST, er=22, cr=40, r=br, board=0)
    back_dark(d, "chest-cover", bx + 6, bx + 430, 0, DEP, SY, br, mat="frame")
    for k, (z0, z1) in enumerate(((0, 110), (DEP - 110, DEP))):
        d.pad(f"bolster{k}", bx + 30, bx + 420, z0, z1, SY + ST - 10, t=30, er=12, cr=30, r=br, board=0)
    px = bx + 436 * math.cos(math.radians(a)); py = SY + 436 * math.sin(math.radians(a))
    split3(d, "head", px + 6, px + 300, py, ST, 420, a, px, hole_len=170, hole_w=80, flap_ang=a - 4)
    d.pad("seat", W - 900, bx - 6, 0, DEP, SY, t=ST, er=22, cr=45)
    for k, (z0, z1) in enumerate(((0, 90), (DEP - 90, DEP))):
        d.pad(f"seat-side{k}", W - 880, bx - 30, z0, z1, SY + ST - 6, t=26, er=10, cr=30, board=0)
    sx = W - 906
    d.pad("leg-far", sx - 960, sx - 6, 0, DEP / 2 - 5, SY, t=ST, er=22, cr=55, r=rot("z", -2, [sx, SY, DEP / 2]))
    lr = rot("z", 65, [sx, SY, DEP / 2])
    d.pad("leg-near", sx - 640, sx - 6, DEP / 2 + 5, DEP, SY, t=ST, er=22, cr=55, r=lr)
    d.box("leg-far-rail", [sx - 900, SY - 45, 40, sx - 20, SY - 12, 70], "frame", r=5)
    d.box("leg-far-lever", [sx - 960, SY - 75, 120, sx - 880, SY - 25, 260], "cap", r=8)
    d.box("seat-lever", [sx + 40, SY - 70, DEP / 2 - 90, sx + 140, SY - 20, DEP / 2 + 20], "cap", r=8)
    d.box("hinge", [bx - 25, SY - 50, 55, bx + 25, SY - 5, 80], "cap", r=4, copies=[[0, 0, DEP - 135], [sx - bx, 0, 0], [sx - bx, 0, DEP - 135]])
    d.cyl("back-pole", [W - 200, 250, DEP - 50], [bx + 180, SY + 330, DEP - 50], 24, "steel")
    sf.swan_base(d, top=STOP, xb0=300, xb1=1800, arms=((650, 1100), (1150, 1600)), loop=False, frame=(600, 1500), cover="grey")
    swan_fix(d, ((650, 1100), (1150, 1600)))
    flip_design(d)
    d.save()



# ====================================================================== XY-K-SF-9B: lumbar table, wide paddle, X-truss lift (head left, no flip)
def sf9b():
    W = 2100
    setw(W, 750)
    d = T("xy-k-sf-9b", [W, DEP, 800])
    y, t = 700, 70
    hx = 405
    # head raised ~10 deg in a fan (photo): face piece with an oval hole and plug, the two flaps splayed out ~8 deg in plan
    hr_ = rot("z", -10, [hx, y, DEP / 2])
    zc0, zc1 = (DEP - 330) / 2, (DEP + 330) / 2
    d.pad("head-face", 0, hx - 6, zc0, zc1, y, t=t, cr=55, er=28, r=hr_, hole=(hx / 2 - 10, DEP / 2, 200, 120))
    def fan(z0, z1, zp, deg):
        c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        pts = rrect_pts(20, z0, hx - 6, z1, 50)
        return [(hx + (x - hx) * c - (z - zp) * s_, zp + (x - hx) * s_ + (z - zp) * c) for x, z in pts]
    d.pad("head-far", 0, 0, 0, 0, y, t=t, er=26, r=hr_, outline=fan(0, zc0 - 6, zc0 - 6, 8))
    d.pad("head-near", 0, 0, 0, 0, y, t=t, er=26, r=hr_, outline=fan(zc1 + 6, DEP, zc1 + 6, -8))
    head_strut(d, "strut", 120, y - 40, 110, out=-1)
    d.pad("chest", hx + 6, 880, 0, DEP, y, t=t, cr=50, er=26)
    # wide lower-body paddle with rounded shoulders at the chest end
    yp = y - 25
    raw = [(1110, 0), (W, 0), (W, DEP), (1110, DEP), (895, DEP - 190), (895, 190)]
    po = round_poly(raw, 150, 8)
    d.pad("paddle", 895, W, 0, DEP, yp, t=t, outline=po, er=28, board=0)
    d.add("paddle-board", "slab", "frame", plane="top", outline=poly_path(inset(po, 14)), w=[yp - 12, yp + 1], r=3)
    d.box("hinge", [hx - 25, y - 50, 60, hx + 25, y - 5, 85], "cap", r=4, copies=[[0, 0, DEP - 145]])
    d.box("clamp", [860, y - 60, DEP - 90, 930, y - 10, DEP - 40], "cap", r=6, copies=[[0, 0, -(DEP - 130)]])
    # top frame under the chest and the paddle
    d.box("topframe", [330, y - 60, 60, 1900, y - 12, 100], "frame", r=5, copies=[[0, 0, DEP - 160]])
    d.box("topframe-x", [330, y - 55, 100, 380, y - 17, DEP - 100], "frame", r=4, copies=[[1520, 0, 0], [560, 0, 0]])
    d.box("topframe-plug", [326, y - 58, 56, 334, y - 14, 104], "cap", r=2, copies=[[0, 0, DEP - 160]])
    # base: rails, end members, legs with black caps and feet, castors inboard
    xb0, xb1 = 300, 1800
    zf0, zf1 = 55, DEP - 55
    d.box("rail", [xb0 + 30, 200, zf1 - 50, xb1 - 30, 260, zf1], "frame", r=5, copies=[[0, 0, -(zf1 - zf0 - 50)]])
    d.box("rail-end", [xb0, 200, zf0 + 40, xb0 + 60, 260, zf1 - 40], "frame", r=5, copies=[[xb1 - xb0 - 60, 0, 0]])
    d.leg("leg", xb0 + 30, zf1 - 30, 280, w=60, foot=True, copies=[[xb1 - xb0 - 60, 0, 0], [0, 0, -(zf1 - zf0 - 60)], [xb1 - xb0 - 60, 0, -(zf1 - zf0 - 60)]])
    for k, (x, z) in enumerate(((xb0 + 120, zf1 - 30), (xb1 - 120, zf1 - 30), (xb0 + 120, zf0 + 30), (xb1 - 120, zf0 + 30))):
        d.add(f"castor{k}", "caster", at=[x, 0, z], d=70)
        d.box(f"castor{k}-br", [x - 25, 90, z - 25, x + 25, 200, z + 25], "frame", r=4)
    # lift truss on both sides as in the photo: bar A from the top frame at the head end down to post 1, bar B from
    # post 1 up to the chest/paddle joint, bar C (parallel to A) from there down to post 2 at the foot end;
    # posts with black caps on the rails, pins at the bar ends, cross tubes at the top
    for k, z in enumerate((110, DEP - 110)):
        dz = 18 if k == 0 else -18
        d.add(f"xa{k}", "bar", "frame", **{"from": [545, y - 70, z + dz], "to": [805, 330, z + dz]}, section=[24, 70], r=6)
        d.add(f"xb{k}", "bar", "frame", **{"from": [805, 330, z], "to": [1085, y - 70, z]}, section=[24, 70], r=6)
        d.add(f"xc{k}", "bar", "frame", **{"from": [1000, y - 70, z + dz], "to": [1550, 330, z + dz]}, section=[24, 70], r=6)
        for j, x in enumerate((805, 1550)):
            d.box(f"post{j}-{k}", [x - 35, 255, z - 30, x + 35, 400, z + 30], "frame", r=5)
            d.box(f"post{j}-{k}-cap", [x - 37, 400, z - 32, x + 37, 412, z + 32], "cap", r=3)
            d.bolt(f"post{j}-{k}-pin", [x, 340, z + (32 if k else -32)], face="front" if k else "back")
        for j, x in enumerate((545, 1000, 1085)):
            d.bolt(f"top-pin{j}-{k}", [x, y - 70, z + (40 if k else -40)], face="front" if k else "back")
    d.cyl("x-tube", [545, y - 70, 110], [545, y - 70, DEP - 110], 40, "frame", copies=[[495, 0, 0]])
    d.box("post0-lever", [835, 380, DEP - 100, 905, 400, DEP - 70], "bolt", r=6, rot=rot("z", 30, [835, 390, 0]))
    d.box("mid-plate", [880, 300, 180, 1150, 315, DEP - 180], "frame", r=4)
    d.cyl("gas", [1100, 330, DEP / 2], [1300, 360, DEP / 2], 30, "act")
    d.cyl("gas-rod", [1300, 360, DEP / 2], [1440, 380, DEP / 2], 14, "steel")
    # black motor beside post 2; the control box at the foot end between the rails: white, its dark-blue panel on TOP,
    # a small blue label on the front (photo)
    d.box("motor", [1440, 230, DEP - 290, 1545, 430, DEP - 140], "plastic#26292d", r=10)
    d.box("ctl-box", [1590, 230, DEP - 330, 1790, 400, DEP - 70], "frame", r=10)
    d.box("ctl-face", [1602, 396, DEP - 318, 1778, 405, DEP - 82], "gloss#1f3f73", r=4)
    d.decal("ctl-label", [1650, 300, DEP - 70 + 0.5], [70, 45], "front", "gloss#3f8fe0")
    d.tube("ctl-cable", [[1780, 380, DEP - 200], [1880, 480, DEP - 120], [1990, 430, DEP - 40], [2030, 300, DEP - 60]], 12, "bolt", bend=80, soft=True)
    d.save()


ALL = {"xy-k-sf-6": sf6, "xy-k-sf-7": sf7, "xy-k-sf-8": sf8, "xy-k-sf-9": sf9,
       "xy-k-sf-5-new": sf5new, "xy-k-sf-6b": sf6b, "xy-k-sf-7-new": sf7new, "xy-k-sf-8b": sf8b, "xy-k-sf-9-new": sf9new, "xy-k-sf-9b": sf9b}

if __name__ == "__main__":
    for k in (sys.argv[1:] or list(ALL)):
        ALL[k]()
