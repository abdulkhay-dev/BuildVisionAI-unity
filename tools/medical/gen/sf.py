"""XY-K-SF treatment tables (Treatment Table.pdf, batch table-1).
python3 sf.py <id> [<id> ...]   — writes only the named designs (all of this file's ids when none given).
The table's length runs along x (head at x = 0 unless the photo shows it on the right, then the design is flipped),
width along z (front z = D, the side the photo looks at)."""
import sys, math
from lib import rot
from sflib import *

W, DEP = 1950, 700


# ====================================================================== old electric base: two Z lift columns
def z_column(d, id, xa, span, yt, yb, z0, z1):
    """Lever column: anchor block under the top frame at xa (left), a slanted beam down to a post at xa+span (right);
    the beam's top is a grey cover (wider than the white body), the body is white."""
    xp = xa + span
    up = quad((xa + 110, yt), (xa + span * 0.5, yt - 50), (xp, yt - 180))         # top of the grey cover
    g = 48                                                                        # cover thickness
    cover = up + [(x, y - g) for x, y in reversed(up)]
    d.add(f"{id}-cover", "slab", "grey", plane="front", outline=poly_path(cover), w=[z0 - 6, z1 + 6], r=8)
    lo = quad((xp - 150, yb), (xa + span * 0.42, yb + span * 0.42), (xa, yt - 90))  # lower-left edge, nearly straight
    body = [(xa, yt), (xa + 110, yt)] + [(x, y - g + 4) for x, y in up[1:]] + [(xp, yb)] + lo
    d.add(f"{id}-body", "slab", "frame", plane="front", outline=poly_path(body), w=[z0, z1], r=5)
    # post caps (black) on the post block, bolts on the anchors and posts
    d.box(f"{id}-pcap", [xp - 46, yt - 180 - g - 2, z0 - 3, xp + 3, yt - 180 - g + 10, z0 + 42], "cap", r=3, copies=[[0, 0, z1 - z0 - 39]])
    d.bolt(f"{id}-b1", [xa + 50, yt - 40, z1], copies=[[0, 0, -(z1 - z0)]])
    d.bolt(f"{id}-b2", [xp - 30, yb + 70, z1], copies=[[0, 0, -(z1 - z0)]])


def z_base(d, top=595, xb0=125, xb1=None, cols=((300, 600), (1000, 600)), ctl="top", lettering=True, ctl_face="gloss#1d3f73",
           motor="apron", motor_x=None):
    """Rectangular white tube base on 4 square legs with black caps, castors inboard, two Z lift columns,
    the top frame (apron) they carry, XIANG YU / MEDICAL lettering and the control box at the foot end (x high)."""
    xb1 = xb1 or W - 125
    zf0, zf1 = 40, DEP - 40               # base frame outer z
    yr0, yr1 = 200, 260                   # base rails
    # rails (60 tall × 40) and end members
    d.box("rail", [xb0 + 30, yr0, zf1 - 40, xb1 - 30, yr1, zf1], "frame", r=4, copies=[[0, 0, -(zf1 - zf0 - 40)]])
    d.box("rail-end", [xb0 + 5, yr0, zf0 + 30, xb0 + 55, yr1, zf1 - 30], "frame", r=4, copies=[[xb1 - xb0 - 60, 0, 0]])
    d.leg("leg", xb0 + 30, zf1 - 25, yr1 + 8, copies=[[xb1 - xb0 - 60, 0, 0], [0, 0, -(zf1 - zf0 - 50)], [xb1 - xb0 - 60, 0, -(zf1 - zf0 - 50)]])
    # retractable castors just inboard of the legs, on short brackets under the rails
    d.add("castor", "caster", at=[xb0 + 110, 0, zf1 - 60], d=50, copies=[[xb1 - xb0 - 220, 0, 0], [0, 0, -(zf1 - zf0 - 120)], [xb1 - xb0 - 220, 0, -(zf1 - zf0 - 120)]])
    d.box("castor-br", [xb0 + 85, 72, zf1 - 85, xb0 + 135, yr0, zf1 - 35], "frame", r=4, copies=[[xb1 - xb0 - 220, 0, 0], [0, 0, -(zf1 - zf0 - 120)], [xb1 - xb0 - 220, 0, -(zf1 - zf0 - 120)]])
    # cross members under the column posts
    z0, z1 = 150, DEP - 150
    for i, (xa, span) in enumerate(cols):
        xp = xa + span
        d.box(f"post-x{i}", [xp - 150, yr0 + 5, zf0 + 20, xp, yr1, zf1 - 20], "frame", r=4)
        z_column(d, f"col{i}", xa, span, top, yr1, z0, z1)
    # top frame (apron) carried by the columns
    d.box("apron", [150, top, 70, W - 150, top + 70, 110], "frame", r=5, copies=[[0, 0, DEP - 180]])
    d.box("apron-x", [150, top + 10, 110, 200, top + 60, DEP - 110], "frame", r=4, copies=[[W - 350, 0, 0], [cols[1][0] - 175, 0, 0]])
    d.box("apron-plug", [146, top + 5, 66, 158, top + 65, 114], "cap", r=3, copies=[[W - 304, 0, 0], [0, 0, DEP - 180], [W - 304, 0, DEP - 180]])
    d.bolt("apron-bolt", [W - 300, top + 35, DEP - 70], copies=[[-(W - 600) / 2, 0, 0]])
    # white flat link plate between the columns just above the base (the photos show no motor down there)
    xm = cols[0][0] + cols[0][1]
    d.box("link", [xm - 40, yr1 + 45, 200, cols[1][0] + cols[1][1] * 0.45, yr1 + 75, DEP - 200], "frame", r=5)
    # small blue caps on the rails beside the legs
    d.cyl("rail-dot", [xb0 + 75, yr1, zf1 - 20], [xb0 + 75, yr1 + 5, zf1 - 20], 16, "gloss#2f7fd0", soft=True,
          copies=[[xb1 - xb0 - 150, 0, 0], [0, 0, -(zf1 - zf0 - 40)], [xb1 - xb0 - 150, 0, -(zf1 - zf0 - 40)]])
    if motor == "apron":     # black drive box hanging under the apron between the column anchors
        mx0 = motor_x if motor_x is not None else cols[0][0] + 190
        d.box("motor", [mx0, top - 70, DEP / 2 - 90, mx0 + 140, top + 5, DEP / 2 + 90], "plastic#2b2e33", r=12)
    elif motor == "rear":    # black round motor on the back rail at the foot end
        d.cyl("motor", [xb1 - 330, yr1 + 50, zf0 + 50], [xb1 - 190, yr1 + 50, zf0 + 50], 100, "plastic#2b2e33")
    if lettering:   # "XIANG YU" under the head-side column, "MEDICAL" under the other (lettering == "rev": swapped)
        a, b = cols[0][0] + 120, cols[1][0] + 260
        if lettering == "rev": a, b = W - b, W - a
        d.add("txt-xiangyu", "decal", at=[a, (yr0 + yr1) / 2, zf1 + 0.5], size=[230, 22], face="front", mat="letter")
        d.add("txt-medical", "decal", at=[b, (yr0 + yr1) / 2, zf1 + 0.5], size=[300, 22], face="front", mat="letter")
    # control box at the foot end, front side: white housing, dark-blue panel face
    if ctl == "top":
        d.box("ctl-box", [xb1 - 230, yr0 + 10, zf1 - 210, xb1 - 60, yr1 + 70, zf1 - 10], "frame", r=10)
        d.add("ctl-face", "screen", box=[xb1 - 220, yr1 + 62, zf1 - 200, xb1 - 70, yr1 + 72, zf1 - 20], face="top", mat=ctl_face, bezel=8, r=4)
        d.box("ctl-hang", [xb1 - 400, 60, zf1 - 50, xb1 - 330, yr0, zf1 - 10], "frame", r=4)
    elif ctl == "end":
        d.box("ctl-box", [xb1 - 260, yr1, zf1 - 260, xb1 - 70, yr1 + 190, zf1 - 30], "frame", r=10)
        # light blue-grey membrane panel with a dark display window and two rows of dark keys (photo)
        d.box("ctl-face", [xb1 - 250, yr1 + 20, zf1 - 32, xb1 - 80, yr1 + 175, zf1 - 24], ctl_face, r=4)
        d.box("ctl-win", [xb1 - 225, yr1 + 120, zf1 - 25, xb1 - 165, yr1 + 160, zf1 - 21], "screen", r=2, soft=True)
        d.box("ctl-key", [xb1 - 150, yr1 + 130, zf1 - 25, xb1 - 132, yr1 + 148, zf1 - 21], "plastic#2b3a4a", r=3, soft=True,
              repeat={"n": 3, "step": [25, 0, 0]}, copies=[[-60, -50, 0], [0, -50, 0]])
        d.box("ctl-hang", [xb1 - 260, 60, zf1 - 50, xb1 - 200, yr0, zf1 - 10], "frame", r=4)


def hinge(d, id, x, y, copies=None):
    """Black hinge bracket between two sections (under the boards, both sides)."""
    d.box(id, [x - 28, y - 55, 60, x + 28, y - 8, 85], "cap", r=4, copies=[[0, 0, DEP - 145]])


# ====================================================================== XY-K-SF-3 (old): 3 sections, Z columns
def sf3():
    global W; W = 1950
    d = T("xy-k-sf-3", [W, DEP, 1010])
    top = 595
    y = top + 82            # underside of the pads (board on the apron)
    t = 80
    hd = 28                 # head raised
    hr = rot("z", -hd, [552, y, DEP / 2])
    d.pad("head", 0, 545, 0, DEP, y, t=t, hole=(250, DEP / 2, 270, 105), r=hr)
    d.pad("mid", 556, 1125, 0, DEP, y, t=t)
    d.pad("foot", 1136, W, 0, DEP, y, t=t)
    # head bracket under the raised section (black), hinges
    d.box("head-arm", [300, y - 40, 70, 552, y - 12, 95], "cap", r=5, rot=hr, copies=[[0, 0, DEP - 165]])
    hinge(d, "hinge1", 552, y)
    hinge(d, "hinge2", 1131, y)
    z_base(d, top=top, cols=((300, 600), (1000, 600)), ctl="top", motor="rear")
    d.save()


def loft_pad(d, id, a, b, w, t=75, dome="end", mat="pad"):
    """A straight pad between two points a, b = [x, y_bottom, z_centre] (x along the length): loft along x, so the pad
    can both tilt and splay; rounded free end (b)."""
    secs = [{"at": a[0], "w": w, "d": t, "r": 26, "cx": a[1] + t / 2, "cz": a[2]},
            {"at": b[0], "w": w, "d": t, "r": 26, "cx": b[1] + t / 2, "cz": b[2]}]
    d.add(id, "loft", mat, axis="x", sections=secs, **({"dome": dome, "domeH": 26} if dome else {}))
    bs = [{"at": a[0] + 5, "w": w - 24, "d": 14, "r": 5, "cx": a[1] - 6, "cz": a[2]},
          {"at": b[0] - 12, "w": w - 24, "d": 14, "r": 5, "cx": b[1] - 6 + (b[1] - a[1]) * -12 / max(1, b[0] - a[0]), "cz": b[2]}]
    d.add(id + "-board", "loft", "frame", axis="x", sections=bs)


def foot_loop(d, id, x, y, z0, z1, out=110, drop=120, mat="steel", dia=20):
    """Foot bar loop at the end x (pointing out to +x, or to -x with out < 0), for raising/lowering the table."""
    d.tube(id, [[x, y, z0], [x + out, y - drop, z0], [x + out, y - drop, z1], [x, y, z1]], dia, mat, bend=30)


# ====================================================================== XY-K-SF-4 (old): head, seat, two leg sections
def sf4():
    global W; W = 1950
    d = T("xy-k-sf-4", [W, DEP, 1060])
    top = 595
    y = top + 82
    t = 80
    hr = rot("z", -30, [452, y, DEP / 2])
    d.pad("head", 0, 445, 0, DEP, y, t=t, hole=(215, DEP / 2, 270, 100), r=hr)
    d.box("head-arm", [260, y - 40, 70, 452, y - 12, 95], "cap", r=5, rot=hr, copies=[[0, 0, DEP - 165]])
    sa = 10                                    # seat raised at its foot end
    sr = rot("z", sa, [457, y, DEP / 2])
    d.pad("seat", 462, 930, 0, DEP, y, t=t, r=sr)
    d.box("seat-frame", [470, y - 50, 60, 925, y - 12, 100], "frame", r=5, rot=sr, copies=[[0, 0, DEP - 160]])
    hx = 457 + 473 * math.cos(math.radians(sa)); hy = y + 473 * math.sin(math.radians(sa))
    # two independent leg sections: near one tilted down, far one raised
    lr_n = rot("z", -8, [hx, hy, DEP / 2]); lr_f = rot("z", 12, [hx, hy, DEP / 2])
    d.pad("leg-near", hx + 8, W - 5, DEP / 2 + 6, DEP, hy, t=t, r=lr_n)
    d.pad("leg-far", hx + 8, W - 5, 0, DEP / 2 - 6, hy, t=t, r=lr_f)
    d.box("leg-near-rail", [hx + 20, hy - 45, DEP - 70, W - 120, hy - 12, DEP - 40], "frame", r=5, rot=lr_n)
    d.box("leg-far-rail", [hx + 20, hy - 45, 40, W - 120, hy - 12, 70], "frame", r=5, rot=lr_f)
    d.box("hinge-blk", [hx - 30, hy - 60, 50, hx + 30, hy + 5, 95], "cap", r=5, copies=[[0, 0, DEP - 145]])
    hinge(d, "hinge1", 452, y)
    # gas springs (black body, steel rod) from the apron up to the leg sections
    d.cyl("gas-far", [1250, top + 40, 120], [1560, hy + 50, 120], 26, "bolt")
    d.cyl("gas-far-rod", [1560, hy + 50, 120], [1720, hy + 85, 120], 12, "steel")
    d.cyl("gas-near", [1250, top + 40, DEP - 120], [1520, hy - 50, DEP - 120], 26, "bolt")
    d.cyl("gas-near-rod", [1520, hy - 50, DEP - 120], [1700, hy - 90, DEP - 120], 12, "steel")
    d.bolt("hinge-bolt", [hx - 60, top + 40, DEP - 110], copies=[[40, 0, 0]])
    z_base(d, top=top, cols=((300, 600), (1000, 600)), ctl="end", ctl_face="gloss#9cb3c6")
    foot_loop(d, "foot-bar", W - 125, 240, 160, DEP - 160)
    d.save()


# ====================================================================== XY-K-SF-5 (old): 5 sections with split legs (head right)
def sf5():
    global W; W = 2000
    d = T("xy-k-sf-5", [W, DEP, 930])
    top = 595
    y = top + 82
    t = 80
    hr = rot("z", -20, [422, y, DEP / 2])
    d.pad("head", 0, 415, 0, DEP, y, t=t, hole=(200, DEP / 2, 250, 95), r=hr)
    d.box("head-arm", [240, y - 40, 70, 422, y - 12, 95], "cap", r=5, rot=hr, copies=[[0, 0, DEP - 165]])
    d.pad("chest", 428, 800, 0, DEP, y, t=t)
    d.pad("pelvis", 811, 1355, 0, DEP, y, t=t)
    hinge(d, "hinge1", 422, y)
    hinge(d, "hinge2", 805, y)
    # two leg sections: far one level and slightly splayed, near one splayed and dropped
    d.add("leg-far", "slab", "pad", plane="top", outline=poly_path(rrect_pts(1366, 0, W - 10, 335, 55)), w=[y, y + t], r=28,
          rot=rot("y", -3, [1366, y, 335]))
    d.add("leg-far-board", "slab", "frame", plane="top", outline=poly_path(rrect_pts(1376, 10, W - 20, 325, 45)), w=[y - 12, y + 1], r=3,
          rot=rot("y", -3, [1366, y, 335]))
    loft_pad(d, "leg-near", [1366, y, DEP - 168], [W - 30, y - 115, DEP - 168 + 80], 330, t=t)
    d.box("leg-rail", [1370, y - 45, 345, W - 140, y - 12, 375], "frame", r=5, rot=rot("y", -3, [1366, y, 335]))
    d.cyl("gas-near", [1240, top + 40, DEP - 120], [1560, y - 50, DEP - 110], 26, "bolt")
    d.cyl("gas-near-rod", [1560, y - 50, DEP - 110], [1760, y - 100, DEP - 100], 12, "steel")
    d.box("hinge-blk", [1330, y - 60, 50, 1390, y + 5, 95], "cap", r=5, copies=[[0, 0, DEP - 145]])
    z_base(d, top=top, cols=((300, 620), (1020, 620)), ctl="top", lettering="rev", motor_x=1150)   # motor under the pelvis (photo)
    flip_design(d)
    d.save()


# ====================================================================== new electric base: two swan-neck lift arms
def swan_arm(d, id, xl, xf, yt, yb, z0, z1, th=150, cover="fillet", ct=34):
    """Curved lift arm arching up-right: upper pivot at xl (head side, under the top frame), foot at xf on two posts.
    White body across the width, dark-grey cover on its outer (upper-right) face."""
    P, F = (xl + 30, yt - 35), (xf, yb)
    mx, my = (P[0] + F[0]) / 2, (P[1] + F[1]) / 2
    nx, ny = norm((F[1] - P[1], -(F[0] - P[0])))          # perpendicular, pointing up-right
    if ny < 0: nx, ny = -nx, -ny
    L = math.dist(P, F)
    Q = (mx + nx * 0.2 * L, my + ny * 0.2 * L)
    c = quad(P, Q, F, 14)
    def off(pts, k):
        out = []
        for i, (x, y) in enumerate(pts):
            a_, b_ = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
            tx, ty = norm((b_[0] - a_[0], b_[1] - a_[1]))
            out.append((x - ty * k, y + tx * k))       # left normal of the direction P->F (points up-right)
        return out
    outer, inner = off(c, -th / 2), off(c, th / 2)
    if outer[3][1] < inner[3][1]: outer, inner = inner, outer
    body = outer + list(reversed(inner))
    d.add(f"{id}-body", "slab", "frame", plane="front", outline=poly_path(body), w=[z0, z1], r=6)
    # grey cover: band between the outer edge and 20 mm inside it
    # the cover: a band ct thick along the convex (upper) edge over the whole width, a little wider than the body
    sgn = -1 if off(c, -10)[3][1] > c[3][1] else 1
    band = off(c, sgn * (th / 2 + 5)) + list(reversed(off(c, sgn * (th / 2 - ct))))
    d.add(f"{id}-fillet", "slab", cover, plane="front", outline=poly_path(band[1:-1]), w=[z0 - 5, z1 + 5], r=6)
    d.cyl(f"{id}-pivot", [P[0], P[1], z0 - 14], [P[0], P[1], z1 + 14], 34, "bolt")
    # posts at both sides of the foot, black caps, pivot bolts
    for k, (a, b) in enumerate(((z0 - 62, z0 - 2), (z1 + 2, z1 + 62))):
        d.box(f"{id}-post{k}", [xf - 30, 250, a, xf + 30, yb + 110, b], "frame", r=4)
        d.box(f"{id}-pcap{k}", [xf - 32, yb + 110, a - 1, xf + 32, yb + 120, b + 1], "cap", r=3)
    d.cyl(f"{id}-lowpin", [xf, yb + 20, z0 - 66], [xf, yb + 20, z1 + 66], 26, "bolt")


def swan_base(d, top=620, xb0=250, xb1=1800, arms=((300, 780), (1050, 1530)), loop=True, z0=190, z1=None, frame=None,
              cover="fillet", buttons=(("gloss#2f7fd0", 0),), tri=True, label_end=0, castor_d=55):
    """Ladder base as in the photos: a transverse beam at each end across the whole width on two square legs (the beam
    ends plugged black), two long rails inboard joining the beams (their ends plugged black, a blue button on top at the
    head end), twin castors under the rails' ends; two swan arms on posts, the top frame they carry, an actuator in the
    middle and the stainless foot-control loop at the foot end (x high)."""
    z1 = z1 or DEP - 190
    zf0, zf1 = 60, DEP - 60               # beam ends (outer faces of the legs)
    yr0, yr1 = 190, 250
    rz = (zf1 - 150, zf1 - 100)           # front long rail (z range); the back one mirrored
    rails = (rz, (DEP - rz[1], DEP - rz[0]))
    for k, (za, zb) in enumerate(rails):
        d.box(f"rail{k}", [xb0 - 15, yr0, za, xb1 + 15, yr1, zb], "frame", r=4)
        d.box(f"rail{k}-plug", [xb0 - 21, yr0 + 3, za + 3, xb0 - 13, yr1 - 3, zb - 3], "cap", r=2, copies=[[xb1 - xb0 + 34, 0, 0]])
    for k, xa in enumerate((xb0, xb1 - 60)):
        d.box(f"beam{k}", [xa, yr0, zf0, xa + 60, yr1, zf1], "frame", r=4)
        d.box(f"beam{k}-plug", [xa + 3, yr0 + 3, zf1 - 2, xa + 57, yr1 - 3, zf1 + 6], "cap", r=2, copies=[[0, 0, -(zf1 - zf0 + 4)]])
    d.box("rail-mid", [xb0 + 60, yr0 + 5, DEP / 2 - 25, xb1 - 60, yr1 - 5, DEP / 2 + 25], "frame", r=4)
    d.leg("leg", xb0 + 30, zf1 - 30, yr0 + 2, cap=False, copies=[[xb1 - xb0 - 60, 0, 0], [0, 0, -(zf1 - zf0 - 60)], [xb1 - xb0 - 60, 0, -(zf1 - zf0 - 60)]])
    rc = (rz[0] + rz[1]) / 2
    for k, (dx, dz) in enumerate(((0, 0), (xb1 - xb0 - 190, 0), (0, -(2 * rc - DEP)), (xb1 - xb0 - 190, -(2 * rc - DEP)))):
        x, z = xb0 + 95 + dx, rc + dz
        d.add(f"castor{k}", "caster", at=[x, 0, z - 14], d=castor_d)
        d.add(f"castor{k}-b", "caster", at=[x, 0, z + 14], d=castor_d)
        d.box(f"castor{k}-br", [x - 25, castor_d + 25, z - 30, x + 25, yr0, z + 30], "frame", r=4)
    for k, (mat, end) in enumerate(buttons):     # round caps on the front rail's top at the head (0) / foot (1) end
        x = xb0 + 30 if end == 0 else xb1 - 30
        d.cyl(f"button{k}", [x, yr1, rc], [x, yr1 + 8, rc], 30, mat, soft=True)
    if tri:     # small blue warning triangle on the top frame near the foot end
        fx1_ = (frame or (xb0 - 60, xb1 + 40))[1]
        d.add("tri", "decal", at=[fx1_ - 160, top + 30, DEP - 70 + 0.5], size=[26, 22], face="front", mat="gloss#2f6fb8")
    for i, (xl, xr) in enumerate(arms):
        d.box(f"post-x{i}", [xr - 35, yr0 + 5, rails[1][0], xr + 35, yr1 + 10, rails[0][1]], "frame", r=4)
        swan_arm(d, f"arm{i}", xl, xr, top, 300, z0, z1, cover=cover)
        # pivot bracket under the top frame
        d.add(f"arm{i}-bracket", "slab", "frame", plane="front",
              outline=poly_path([(xl - 30, top + 2), (xl + 200, top + 2), (xl + 90, top - 60), (xl + 10, top - 75), (xl - 30, top - 40)]),
              w=[z0 - 16, z1 + 16], r=5)
    # top frame under the pad (white channel, black end plugs)
    fx0, fx1 = frame or (xb0 - 60, xb1 + 40)
    d.box("topframe", [fx0, top, 70, fx1, top + 60, 115], "frame", r=5, copies=[[0, 0, DEP - 185]])
    d.box("topframe-x", [fx0, top + 5, 115, fx0 + 45, top + 55, DEP - 115], "frame", r=4, copies=[[fx1 - fx0 - 45, 0, 0]])
    d.box("topframe-plug", [fx1 - 2, top + 6, 72, fx1 + 6, top + 54, 113], "cap", r=2, copies=[[0, 0, DEP - 185], [-(fx1 - fx0 + 4), 0, 0], [-(fx1 - fx0 + 4), 0, DEP - 185]])
    d.box("topframe-tab", [(fx0 + fx1) / 2 - 30, top + 20, DEP - 70, (fx0 + fx1) / 2 + 30, top + 55, DEP - 62], "cap", r=2, copies=[[-(fx1 - fx0) / 2 + 150, 0, 0]])
    # actuator (grey Linak) from the base to the second arm
    d.cyl("actuator", [arms[0][1] + 60, yr1 + 15, DEP / 2], [arms[1][1] - 260, yr1 + 60, DEP / 2], 46, "act")
    d.cyl("actuator-rod", [arms[1][1] - 260, yr1 + 60, DEP / 2], [arms[1][1] - 120, yr1 + 80, DEP / 2], 18, "steel")
    # Sunnyou label and blue button at the head end of the near rail
    lx = xb0 + 200 if label_end == 0 else xb1 - 200
    d.add("label", "decal", at=[lx, (yr0 + yr1) / 2, rz[1] + 0.5], size=[90, 34], face="front", mat="plastic#e8eef6")
    d.add("label-logo", "decal", at=[lx - 25, (yr0 + yr1) / 2 + 2, rz[1] + 1], size=[22, 22], face="front", mat="gloss#2f6fb8")
    if loop:
        d.tube("foot-loop", [[xb1 - 20, 170, zf1 - 120], [xb1 + 90, 70, zf1 - 120], [xb1 + 90, 70, zf0 + 120], [xb1 - 20, 170, zf0 + 120]], 18, "steel", bend=25)
        d.cyl("foot-loop-hub", [xb1 - 25, 175, zf0 + 100], [xb1 - 25, 175, zf1 - 100], 40, "act")


def breath_slit(d, id, cx, cz, ly, y, r=None):
    """Closed breathing slit (SF-1 new): a shallow arc groove."""
    arc = quad((cx - ly / 2, cz + 15), (cx, cz - 45), (cx + ly / 2, cz + 15), 12)
    band = arc + [(x, z + 7) for x, z in reversed(arc)]
    d.add(id, "slab", "plastic#7d9fc4", plane="top", outline=poly_path(band), w=[y - 2, y + 1], r=1, soft=True, rot=r)


# ====================================================================== XY-K-SF-1 (new): one section on swan arms
def sf1new():
    global W; W = 1950
    d = T("xy-k-sf-1-new", [W, 690, 750])
    global DEP
    keep = DEP; DEP = 690
    top = 620
    y = top + 72
    d.pad("top", 0, W, 0, DEP, y, t=58, er=22, outline=chamfer_pts(0, 0, W, DEP, 110, 90, 45))
    breath_slit(d, "slit", 260, DEP / 2, 240, y + 58)
    d.box("lever", [W - 120, y - 40, DEP - 150, W - 40, y - 15, DEP - 110], "cap", r=6, rot=rot("z", -15, [W - 120, y - 20, 0]))
    swan_base(d, top=top + 12, xb0=250, xb1=1800)
    d.save()
    DEP = keep


def foot_pedal(d, id, x, z, n=2, cable_to=None, mat="frame"):
    """Floor foot switch: white plate with n dark-grey pedal pads, cable to the base."""
    w = 110 * n + 40
    d.box(id, [x - w / 2, 0, z - 90, x + w / 2, 38, z + 90], mat, r=12)
    d.box(id + "-pad", [x - w / 2 + 30, 36, z - 60, x - w / 2 + 110, 44, z + 60], "plastic#5a5f66", r=6,
          repeat={"n": n, "step": [110, 0, 0]})
    if cable_to:
        d.tube(id + "-cable", [[x, 20, z - 90], [x, 10, z - 200], cable_to], 8, "bolt", bend=80, soft=True)


# ====================================================================== XY-K-SF-2 (new): head section + body on swan arms
def sf2new():
    global W, DEP; W = 1950
    keep = DEP; DEP = 690
    d = T("xy-k-sf-2-new", [W, DEP, 1130])
    top = 632
    y = top + 60
    hx = 650
    hr = rot("z", -35, [hx, y, DEP / 2])
    d.pad("head", 0, hx - 6, 0, DEP, y, t=58, er=22, cr=50, hole=(300, DEP / 2, 290, 105), r=hr)
    d.box("head-rail", [120, y - 45, 70, hx - 10, y - 12, 105], "frame", r=5, rot=hr, copies=[[0, 0, DEP - 175]])
    d.cyl("head-gas", [hx + 60, top + 20, DEP / 2 - 120], [380, y - 30, DEP / 2 - 120], 24, "bolt", rot=None)
    d.pad("body", hx + 6, W, 0, DEP, y, t=58, er=22, cr=50)
    d.box("hinge", [hx - 25, y - 50, 55, hx + 25, y - 5, 80], "cap", r=4, copies=[[0, 0, DEP - 135]])
    d.box("lever", [W - 140, y - 45, DEP - 160, W - 50, y - 18, DEP - 115], "cap", r=6, rot=rot("z", -15, [W - 140, y - 25, 0]))
    d.box("end-handle", [W - 120, y - 70, DEP / 2 - 120, W - 60, y - 40, DEP / 2 + 120], "cap", r=8)
    swan_base(d, top=top, xb0=250, xb1=1800)
    d.save()
    DEP = keep


# ====================================================================== XY-K-SF-3 (new): 3 sections, chair pose
def sf3new():
    global W, DEP; W = 1950
    keep = DEP; DEP = 690
    d = T("xy-k-sf-3-new", [W, DEP, 1500])
    top = 632
    y = top + 60
    bx, sx = 800, 1225                                      # back / seat and seat / leg hinges
    br = rot("z", -65, [bx + 5, y, DEP / 2])
    d.pad("back", 0, bx, 0, DEP, y, t=60, er=22, cr=50, r=br)
    d.box("back-rail", [80, y - 45, 70, bx - 10, y - 12, 105], "frame", r=5, rot=br, copies=[[0, 0, DEP - 175]])
    d.box("back-lever", [420, y - 70, -8, 500, y - 20, 22], "cap", r=8, rot=br, copies=[[0, 0, DEP - 14]])
    d.cyl("back-gas", [bx + 60, top + 10, DEP / 2], [bx - 160, y + 330, DEP / 2], 22, "steel")
    d.pad("seat", bx + 10, sx - 5, 0, DEP, y, t=60, er=22, cr=40)
    lr = rot("z", -32, [sx, y, DEP / 2])
    d.pad("legrest", sx + 6, W, 0, DEP, y, t=60, er=22, cr=50, r=lr)
    d.box("leg-rail", [sx + 20, y - 45, 70, W - 80, y - 12, 105], "frame", r=5, rot=lr, copies=[[0, 0, DEP - 175]])
    d.box("leg-lever", [W - 120, y - 70, DEP - 10, W - 50, y - 25, DEP + 18], "cap", r=8, rot=lr)
    d.box("seat-lever", [sx - 60, y - 60, DEP - 8, sx, y - 20, DEP + 18], "cap", r=6)
    d.box("hinge", [bx - 20, y - 50, 55, bx + 30, y - 5, 80], "cap", r=4, copies=[[0, 0, DEP - 135], [sx - bx, 0, 0], [sx - bx, 0, DEP - 135]])
    d.cyl("leg-gas", [sx + 40, top + 10, DEP / 2], [sx + 300, y - 230, DEP / 2], 22, "steel")
    # the top is drawn head-left and mirrored (head right as in the photo); the base is added after the mirror because
    # its swan arms keep the SF-1 new orientation in the photo (pivot up on the left, posts on the right)
    flip_design(d)
    swan_base(d, top=top, xb0=250, xb1=1800, arms=((600, 1040), (1100, 1540)), loop=False, frame=(560, 1600),
              cover="metal#a9aeb4", buttons=(("gloss#2fae5a", 0), ("gloss#2fae5a", 1)), tri=False, label_end=1)
    # round grey motor under the head end, foot switch on the floor in front of it
    d.cyl("motor", [W - 330, 110, DEP / 2 - 100], [W - 330, 110, DEP / 2 + 100], 140, "act")
    foot_pedal(d, "pedal", W - 520, DEP + 170, n=2, cable_to=[W - 420, 180, DEP - 80])
    d.save()
    DEP = keep


def notched_pts(x0, z0, x1, z1, nx0, nx1, depth, cr=50):
    """Rounded-rect pad outline with a concave waist notch on both long sides between nx0..nx1."""
    m = (nx0 + nx1) / 2
    raw = [(x0, z0), (nx0, z0), (m - 15, z0 + depth), (m + 15, z0 + depth), (nx1, z0), (x1, z0),
           (x1, z1), (nx1, z1), (m + 15, z1 - depth), (m - 15, z1 - depth), (nx0, z1), (x0, z1)]
    return round_poly(raw, cr, 5)


def rrect_hole(cx, cz, lx, lz, r=30):
    return rrect_pts(cx - lx / 2, cz - lz / 2, cx + lx / 2, cz + lz / 2, r)


def sq_base(d, xb0, xb1, yr0, yr1, zf0=70, zf1=None, feet=True):
    """Rectangular white tube base on 4 square legs with black top caps and black adjustable feet."""
    zf1 = zf1 or DEP - 70
    d.box("rail", [xb0 + 30, yr0, zf1 - 40, xb1 - 30, yr1, zf1], "frame", r=4, copies=[[0, 0, -(zf1 - zf0 - 40)]])
    d.box("rail-end", [xb0 + 5, yr0, zf0 + 30, xb0 + 55, yr1, zf1 - 30], "frame", r=4, copies=[[xb1 - xb0 - 60, 0, 0]])
    d.leg("leg", xb0 + 30, zf1 - 25, yr1 + 5, foot=feet, copies=[[xb1 - xb0 - 60, 0, 0], [0, 0, -(zf1 - zf0 - 50)], [xb1 - xb0 - 60, 0, -(zf1 - zf0 - 50)]])


# ====================================================================== XY-K-SF-1B: one-piece top on a scissor lift
def sf1b():
    global W; W = 1950
    d = T("xy-k-sf-1b", [W, DEP, 900])
    y, t = 825, 75
    pts = notched_pts(0, 0, W, DEP, 540, 720, 48, cr=45)
    d.pad("top", 0, W, 0, DEP, y, t=t, outline=pts, er=26, board=0, hole=rrect_hole(250, DEP / 2, 180, 115, 28))
    d.add("hole-bottom", "slab", "plastic#5d6f86", plane="top", outline=poly_path(rrect_hole(250, DEP / 2, 200, 135, 30)), w=[y + 4, y + 12], r=2)
    d.add("seam", "decal", at=[330, y + t / 2, DEP + 0.5], size=[5, t - 24], face="front", mat="plastic#7f9fc4")
    # white sheet-steel apron under the top, black corner caps
    d.box("apron", [60, 765, 25, W - 60, y, 45], "frame", r=4, copies=[[0, 0, DEP - 70]])
    d.box("apron-end", [60, 765, 45, 80, y, DEP - 45], "frame", r=4, copies=[[W - 140, 0, 0]])
    d.box("apron-cap", [55, 740, 20, 85, y - 5, 50], "cap", r=3, copies=[[W - 140, 0, 0], [0, 0, DEP - 70], [W - 140, 0, DEP - 70]])
    d.box("apron-floor", [80, 760, 45, W - 80, 768, DEP - 45], "frame", r=2)
    # base
    xb0, xb1 = 150, 1800
    sq_base(d, xb0, xb1, 150, 210)
    d.box("base-mid", [xb0 + 60, 155, DEP / 2 - 20, xb1 - 60, 205, DEP / 2 + 20], "frame", r=4)
    # two asymmetric X linkages of white flat bars (both sides), as in the photo: a long shallow bar rising from the
    # head side to the top, crossed by a shorter steep bar falling from the top to the base; cross tubes at the ends
    for i, (x0, x1) in enumerate(((330, 830), (1080, 1580))):
        bx0, bx1 = x0 + 170, x1 - 140                     # the steep bar: top at bx0, foot at bx1
        # crossing point of a (x0,235)-(x1,735) and b (bx0,735)-(bx1,235)
        ta = ((bx0 - x0) + (bx1 - bx0) * 0.5) / ((x1 - x0) + (bx1 - bx0))
        t = ((bx0 - x0)) / ((x1 - x0) + (bx1 - bx0))
        xc, yc = x0 + (x1 - x0) * t, 235 + 500 * t
        for k, z in enumerate((140, DEP - 140)):
            dz = 16 if k == 0 else -16
            d.add(f"x{i}a{k}", "bar", "frame", **{"from": [x0, 235, z], "to": [x1, 735, z]}, section=[22, 80], r=6)
            d.add(f"x{i}b{k}", "bar", "frame", **{"from": [bx0, 735, z + dz], "to": [bx1, 235, z + dz]}, section=[22, 70], r=6)
        d.cyl(f"x{i}-pin", [xc, yc, 110], [xc, yc, DEP - 110], 30, "bolt")
        d.cyl(f"x{i}-tube-lo", [x0, 235, 120], [x0, 235, DEP - 120], 40, "frame")
        d.cyl(f"x{i}-tube-hi", [x1, 735, 120], [x1, 735, DEP - 120], 40, "frame")
        d.box(f"x{i}-shoe", [bx1 - 40, 205, 115, bx1 + 40, 260, 165], "frame", r=5, copies=[[0, 0, DEP - 280]])
        d.box(f"x{i}-top", [bx0 - 40, 735, 115, bx0 + 40, 765, 165], "frame", r=5, copies=[[0, 0, DEP - 280]])
    # grey Linak actuator standing under the head part, a dark push rod from the motor, control box, black motor
    d.cyl("actuator", [520, 760, DEP / 2], [560, 420, DEP / 2], 52, "act")
    d.cyl("actuator-rod", [600, 250, DEP / 2 + 40], [780, 400, DEP / 2 + 40], 24, "bolt")
    d.box("ctl-box", [230, 210, DEP - 260, 520, 330, DEP - 75], "frame", r=10)
    d.box("ctl-switch", [270, 330, DEP - 200, 310, 338, DEP - 160], "gloss#2e9a4a", r=3)
    d.cyl("ctl-knob", [400, 330, DEP - 180], [400, 350, DEP - 180], 22, "bolt", copies=[[50, 0, 60]])
    d.box("motor", [540, 215, DEP - 220, 620, 430, DEP - 140], "bolt", r=12, rot=rot("z", -12, [580, 215, 0]))
    # blue hand switch clipped on the apron, black cables
    d.box("hand-switch", [760, 700, DEP - 25, 840, 800, DEP + 8], "gloss#2f78c8", r=8)
    d.tube("cable", [[800, 700, DEP - 8], [780, 520, DEP - 20], [700, 330, DEP - 40], [580, 290, DEP - 120]], 10, "bolt", bend=120, soft=True)
    d.tube("cable-floor", [[300, 300, DEP - 75], [240, 200, DEP + 20], [190, 60, DEP + 60], [120, 8, DEP + 80]], 8, "bolt", bend=80, soft=True)
    d.add("label", "decal", at=[1050, 180, DEP - 70 + 0.5], size=[260, 30], face="front", mat="plastic#2f78c8")
    d.save()


# ====================================================================== XY-K-SF-2 (old): body + raised head section (head right)
def sf2():
    global W; W = 1950
    d = T("xy-k-sf-2", [W, DEP, 990])
    y, t = 515, 95
    hx = 1245
    d.pad("body", 0, hx - 6, 0, DEP, y, t=t, cr=45, er=32)
    hr = rot("z", 30, [hx, y, DEP / 2])
    d.pad("head", hx + 6, W, 0, DEP, y, t=t, cr=45, er=32, r=hr)
    # the photo shows only a thin closed breathing slit along the head section (a seam with a stud at each end)
    d.add("head-slit", "slab", "plastic#5f7fa6", plane="top", outline=poly_path(stadium_pts(1700, DEP / 2, 320, 9)),
          w=[y + t - 1, y + t + 1.5], r=0.5, soft=True, rot=hr)
    d.cyl("head-stud", [1545, y + t, DEP / 2], [1545, y + t + 3, DEP / 2], 12, "bolt", soft=True, rot=hr, copies=[[310, 0, 0]])
    d.box("head-rail", [hx + 20, y - 45, 60, W - 60, y - 12, 95], "frame", r=5, rot=hr, copies=[[0, 0, DEP - 155]])
    d.box("head-clamp", [W - 70, y - 60, DEP - 120, W - 20, y - 5, DEP - 60], "cap", r=6, rot=hr)
    d.box("hinge", [hx - 30, y - 60, DEP - 60, hx + 30, y - 5, DEP - 25], "cap", r=4, copies=[[0, 0, -(DEP - 85)]])
    # top frame under the body, black end caps; two steel bars running out under the head
    d.box("apron", [30, 455, 30, hx + 400, y - 12, 70], "frame", r=4, copies=[[0, 0, DEP - 100]])
    d.box("apron-cap", [24, 455, 26, 36, y - 12, 74], "cap", r=3, copies=[[0, 0, DEP - 100]])
    d.box("apron-x", [30, 460, 70, 70, y - 15, DEP - 70], "frame", r=4)
    d.cyl("arm-bar", [hx - 150, 470, 15], [hx + 420, 470, 15], 30, "steel", copies=[[0, 0, DEP - 30]])
    # base: square tube frame, 4 legs with black caps and feet
    xb0, xb1 = 125, 1825
    sq_base(d, xb0, xb1, 135, 200, zf0=60, zf1=DEP - 60)
    # two lift levers per side (white flat bars) with their lower plates
    for k, z in enumerate((95, DEP - 95)):
        d.add(f"lev1a{k}", "bar", "frame", **{"from": [60, 440, z], "to": [590, 385, z]}, section=[22, 60], r=6)
        d.add(f"lev1b{k}", "bar", "frame", **{"from": [60, 420, z], "to": [470, 300, z]}, section=[22, 60], r=6)
        d.add(f"lev2a{k}", "bar", "frame", **{"from": [1135, 450, z], "to": [1580, 390, z]}, section=[22, 60], r=6)
        d.add(f"lev2b{k}", "bar", "frame", **{"from": [1135, 425, z], "to": [1460, 310, z]}, section=[22, 60], r=6)
    d.box("plate1", [450, 200, 80, 600, 400, DEP - 80], "frame", r=6)
    d.box("plate2", [1440, 200, 80, 1590, 400, DEP - 80], "frame", r=6)
    d.bolt("plate-bolt", [520, 330, DEP - 80], copies=[[990, 0, 0]])
    d.cyl("pivot", [70, 430, 70], [70, 430, DEP - 70], 30, "bolt", copies=[[1075, 15, 0]])
    d.box("plate-cap", [450, 400, 75, 500, 412, 115], "cap", r=3, copies=[[990, 0, 0], [0, 0, DEP - 190], [990, 0, DEP - 190]])
    # grey actuator, black motor/pedal assembly on the base, control box with buttons at the head end
    d.box("mid-beam", [600, 250, DEP / 2 - 40, 1440, 300, DEP / 2 + 40], "frame", r=5)
    d.box("motor", [1180, 205, DEP / 2 - 90, 1420, 300, DEP / 2 + 120], "plastic#3a3d42", r=14)
    d.box("ctl-box", [1600, 200, DEP - 260, 1760, 380, DEP - 75], "frame", r=8)
    d.cyl("ctl-btn-r", [1660, 340, DEP - 75], [1660, 340, DEP - 68], 26, "gloss#c8322e")
    d.cyl("ctl-btn-g", [1710, 340, DEP - 75], [1710, 340, DEP - 68], 26, "gloss#2e9a4a")
    d.add("ctl-label", "decal", at=[1690, 270, DEP - 74.5], size=[110, 70], face="front", mat="plastic#d9dde2")
    # blue hand switch on the apron, black cable down to the floor and to the control box
    d.box("hand-switch", [700, 440, DEP - 40, 840, 500, DEP - 8], "gloss#2f78c8", r=6)
    d.tube("cable", [[830, 470, DEP - 8], [930, 400, DEP + 10], [1100, 120, DEP + 30], [1200, 15, DEP + 40], [1550, 25, DEP + 20], [1660, 210, DEP - 80]], 10, "bolt", bend=120, soft=True)
    d.add("label", "decal", at=[790, 168, DEP - 60 + 0.5], size=[290, 26], face="front", mat="plastic#2f78c8")
    d.save()


def frame_base(d, xb0, xb1, yr0=230, yr1=300, zf0=50, zf1=None, stirrups=True, bar=False):
    """Box-section white base (4C / 4D): rails, legs with black caps at the ends, twin castors inboard,
    grey stirrup pedals at both ends, optional long stainless foot bar along the front."""
    zf1 = zf1 or DEP - 50
    d.box("rail", [xb0 + 30, yr0, zf1 - 50, xb1 - 30, yr1, zf1], "frame", r=5, copies=[[0, 0, -(zf1 - zf0 - 50)]])
    d.box("rail-end", [xb0 + 5, yr0, zf0 + 40, xb0 + 65, yr1, zf1 - 40], "frame", r=5, copies=[[xb1 - xb0 - 70, 0, 0]])
    # legs flush with the rails' top; the rail ends show black plugs on the legs' outer faces (photos)
    d.leg("leg", xb0 + 35, zf1 - 30, yr1, w=70, cap=False, copies=[[xb1 - xb0 - 70, 0, 0], [0, 0, -(zf1 - zf0 - 60)], [xb1 - xb0 - 70, 0, -(zf1 - zf0 - 60)]])
    d.box("leg-plug", [xb0 + 4, yr0 + 4, zf1 + 4, xb0 + 66, yr1 - 4, zf1 + 10], "cap", r=2,
          copies=[[xb1 - xb0 - 70, 0, 0], [0, 0, -(zf1 - zf0 + 14)], [xb1 - xb0 - 70, 0, -(zf1 - zf0 + 14)]])
    for k, (dx, dz) in enumerate(((0, 0), (xb1 - xb0 - 260, 0), (0, -(zf1 - zf0 - 140)), (xb1 - xb0 - 260, -(zf1 - zf0 - 140)))):
        x, z = xb0 + 130 + dx, zf1 - 70 + dz
        d.add(f"castor{k}", "caster", at=[x, 0, z - 16], d=70)
        d.add(f"castor{k}-b", "caster", at=[x, 0, z + 16], d=70)
        d.box(f"castor{k}-br", [x - 30, 95, z - 35, x + 30, yr0, z + 35], "frame", r=4)
    if stirrups:
        for k, (x, o) in enumerate(((xb0 + 10, -120), (xb1 - 10, 120))):
            d.tube(f"stirrup{k}", [[x, 200, DEP / 2 - 150], [x + o, 90, DEP / 2 - 110], [x + o, 90, DEP / 2 + 110], [x, 200, DEP / 2 + 150]], 26, "plastic#a3a8af", bend=30)
            d.box(f"stirrup{k}-hub", [min(x, x + o * 0.2) - 20, 170, DEP / 2 - 170, max(x, x + o * 0.2) + 20, 230, DEP / 2 + 170], "plastic#a3a8af", r=10)
    if bar:
        d.cyl("foot-bar", [xb0 + 20, 120, zf1 + 30], [xb1 - 20, 120, zf1 + 30], 22, "steel")
        d.box("foot-bar-arm", [xb0 + 10, 105, zf1 - 20, xb0 + 40, 135, zf1 + 40], "plastic#a3a8af", r=6, copies=[[xb1 - xb0 - 50, 0, 0]])


# ====================================================================== XY-K-SF-4B: split legs in a V, raised back (head right)
def sf4b():
    global W; W = 1950
    d = T("xy-k-sf-4b", [W, DEP, 1330])
    top = 632
    y = top + 60
    t = 60
    lh = 900                                            # legs / seat hinge
    # two leg sections splayed in a V: far one raised, near one lowered (head at x = W)
    for nm, zc, yaw, tilt in (("leg-far", DEP / 2 - 160, -210, 110), ("leg-near", DEP / 2 + 160, 210, -120)):
        loft_pad(d, nm, [10, y + tilt, zc + yaw], [lh - 8, y, zc], 300, t=t, dome="start")
        d.box(nm + "-clamp", [20, y + tilt - 45, zc + yaw - 20, 80, y + tilt - 5, zc + yaw + 20], "cap", r=6)
    d.cyl("leg-gas", [lh - 120, top + 20, DEP / 2 + 160], [380, y - 70, DEP / 2 + 230], 22, "steel")
    d.cyl("leg-gas-body", [lh - 120, top + 20, DEP / 2 + 160], [640, y - 40, DEP / 2 + 190], 30, "bolt")
    d.pad("seat", lh + 6, 1300, 0, DEP, y, t=t, er=22, cr=40)
    br = rot("z", 60, [1305, y, DEP / 2])
    d.pad("back", 1312, W, 0, DEP, y, t=t, er=22, cr=50, hole=(1700, DEP / 2, 300, 110), r=br)
    d.box("back-rail", [1330, y - 45, 70, W - 60, y - 12, 105], "frame", r=5, rot=br, copies=[[0, 0, DEP - 175]])
    d.cyl("back-gas", [1150, top + 20, DEP / 2], [1520, y + 520, DEP / 2], 18, "steel")
    d.box("hinge", [lh - 25, y - 50, 55, lh + 25, y - 5, 80], "cap", r=4, copies=[[0, 0, DEP - 135], [405, 0, 0], [405, 0, DEP - 135]])
    swan_base(d, top=top, xb0=150, xb1=1750, arms=((380, 820), (1060, 1500)), loop=False, frame=(300, 1450), cover="grey", tri=False)
    d.add("motor", "loft", "plastic#d9dce0", axis="x", sections=[
        {"at": 1460, "w": 280, "d": 150, "r": 70, "cx": 135, "cz": DEP / 2}, {"at": 1700, "w": 280, "d": 150, "r": 70, "cx": 135, "cz": DEP / 2}],
        dome="both", domeH=50)
    foot_pedal(d, "pedal1", 1700, DEP + 230, n=2, cable_to=[1600, 120, DEP / 2])
    foot_pedal(d, "pedal2", 1960, DEP + 200, n=2, cable_to=[1650, 120, DEP / 2 + 60])
    d.save()


# ====================================================================== XY-K-SF-4C: 4 sections on a box frame (head right)
def sf4c():
    global W; W = 2000
    d = T("xy-k-sf-4c", [W, DEP, 1040])
    y, t = 640, 82
    secs = ((0, 560), (571, 1000), (1011, 1500))
    for i, (a, b) in enumerate(secs):
        d.pad(f"sec{i}", a, b, 0, DEP, y, t=t, cr=55, er=32)
    hr = rot("z", 45, [1505, y, DEP / 2])
    d.pad("head", 1511, W, 0, DEP, y, t=t, cr=55, er=32, hole=(1760, DEP / 2, 300, 100), r=hr)
    d.box("head-rail", [1530, y - 45, 60, W - 60, y - 12, 95], "frame", r=5, rot=hr, copies=[[0, 0, DEP - 155]])
    d.box("hinge", [1480, y - 60, DEP - 60, 1530, y - 5, DEP - 25], "cap", r=4, copies=[[0, 0, -(DEP - 85)], [-500, 0, 0], [-940, 0, 0]])
    # deep white box apron under the sections, black corner plugs
    d.box("apron", [120, 520, 40, 1880, y - 10, 85], "frame", r=6, copies=[[0, 0, DEP - 125]])
    d.box("apron-end", [120, 520, 85, 170, y - 10, DEP - 85], "frame", r=6, copies=[[1710, 0, 0]])
    d.box("apron-plug", [116, 600, 36, 132, y - 12, 89], "cap", r=3, copies=[[1752, 0, 0], [0, 0, DEP - 125], [1752, 0, DEP - 125]])
    d.bolt("apron-bolt", [1200, 560, DEP - 40], copies=[[-400, 0, 0], [500, 0, 0]])
    d.cyl("release", [480, 520, DEP - 140], [480, 470, DEP - 140], 50, "bolt", copies=[[530, 0, 0]])
    d.box("release-tag", [465, 498, DEP - 112, 495, 512, DEP - 108], "gloss#e8c21e", r=2, copies=[[530, 0, 0]])
    # lift: white drum at the foot side, curved white lever block in the middle, grey actuator
    d.cyl("drum", [400, 430, 120], [400, 430, DEP - 120], 190, "frame")
    d.add("lever", "slab", "frame", plane="front",
          outline=poly_path(quad((780, 300), (900, 330), (1000, 515)) + [(1080, 515), (1080, 420)] + quad((1080, 420), (980, 300), (900, 300))[1:]),
          w=[150, DEP - 150], r=6)
    d.cyl("lever-pin", [1000, 470, 130], [1000, 470, DEP - 130], 40, "bolt")
    d.cyl("actuator", [480, 400, DEP / 2], [880, 360, DEP / 2], 60, "act")
    d.box("lift-post", [1180, 300, 120, 1280, 520, DEP - 120], "frame", r=8)
    d.box("motor", [200, 140, DEP / 2 - 120, 560, 225, DEP / 2 + 120], "act", r=14)
    frame_base(d, 100, 1900, yr0=230, yr1=330, bar=True)
    d.save()


# ====================================================================== XY-K-SF-4D: 4 sections, single central column (head right)
def sf4d():
    global W; W = 2000
    d = T("xy-k-sf-4d", [W, DEP, 1050])
    y, t = 660, 75
    d.pad("body", 0, 890, 0, DEP, y, t=t, cr=45, er=28)
    d.pad("mid", 901, 1340, 0, DEP, y, t=t, cr=45, er=28)
    fr = rot("z", 40, [1345, y, DEP / 2])
    d.pad("flex", 1350, 1790, 0, DEP, y, t=t, cr=45, er=28, r=fr)
    d.box("flex-rail", [1370, y - 45, 70, 1770, y - 12, 105], "frame", r=5, rot=fr, copies=[[0, 0, DEP - 175]])
    d.pad("end", 1600, W, 0, DEP, y, t=t, cr=45, er=28)
    d.box("end-clamp", [W - 140, y - 75, DEP - 75, W - 70, y - 25, DEP - 35], "steel", r=6)
    d.box("hinge", [1320, y - 60, DEP - 60, 1370, y - 5, DEP - 25], "cap", r=4, copies=[[0, 0, -(DEP - 85)], [-450, 0, 0], [-450, 0, -(DEP - 85)]])
    d.box("apron", [60, y - 70, 40, W - 50, y - 10, 80], "frame", r=5, copies=[[0, 0, DEP - 120]])
    d.box("apron-plug", [54, y - 68, 36, 64, y - 12, 84], "cap", r=3, copies=[[0, 0, DEP - 120], [W - 108, 0, 0], [W - 108, 0, DEP - 120]])
    d.box("clamp", [400, y - 120, DEP - 80, 470, y - 60, DEP - 40], "cap", r=8)
    # single white Z column: anchored under the middle, sloping down to a post at the head side
    out = [(720, y - 70), (1020, y - 70)] + quad((1020, y - 70), (1180, 420), (1420, 340))[1:] + [(1420, 260), (1180, 260)] \
        + quad((1180, 260), (980, 300), (900, 330))[1:] + quad((900, 330), (840, 430), (760, 500))[1:]
    d.add("column", "slab", "frame", plane="front", outline=poly_path(out), w=[140, DEP - 140], r=8)
    d.add("column-cover", "slab", "plastic#e2e5e9", plane="front",
          outline=poly_path(quad((1030, y - 74), (1185, 425), (1425, 345)) + list(reversed(quad((1030, y - 120), (1180, 380), (1425, 300))))),
          w=[146, DEP - 146], r=5)
    # grey gas strut running above the column's sloping top (photo)
    d.cyl("col-strut", [1060, y - 75, DEP / 2], [1300, 450, DEP / 2], 44, "act")
    d.cyl("col-strut-rod", [960, y - 70, DEP / 2], [1060, y - 75, DEP / 2], 18, "steel")
    d.box("post", [900, 300, 110, 970, 470, 180], "frame", r=5, copies=[[0, 0, DEP - 290]])
    d.box("post-cap", [898, 470, 108, 972, 480, 182], "cap", r=3, copies=[[0, 0, DEP - 290]])
    d.box("post2", [330, 300, 110, 400, 470, 180], "frame", r=5, copies=[[0, 0, DEP - 290]])
    d.box("post2-cap", [328, 470, 108, 402, 480, 182], "cap", r=3, copies=[[0, 0, DEP - 290]])
    d.bolt("col-bolt", [870, 600, DEP - 140], copies=[[90, -260, 0], [470, -300, 0]])
    d.bolt("post-bolt", [365, 420, DEP - 110], copies=[[570, 0, 0]])
    d.tube("hose", [[330, 470, DEP / 2], [550, 560, DEP / 2 + 40], [820, 430, DEP / 2]], 20, "act", bend=150, soft=True)
    d.box("cross", [330, 300, 110, 1420, 330, DEP - 110], "frame", r=5)
    d.box("pedal-plate", [230, 170, DEP / 2 - 160, 620, 190, DEP / 2 + 160], "plastic#a3a8af", r=6)
    frame_base(d, 160, 1840, yr0=230, yr1=300, bar=False)
    d.save()


# ====================================================================== XY-K-SF-1: fixed-height steel couch (head right)
def sf1():
    global W, DEP; W = 1900
    keep = DEP; DEP = 650
    d = T("xy-k-sf-1", [W, DEP, 700], {"pad": "leather#78a8dc"})     # the photo's pad is a deeper blue
    y, t = 632, 68
    pts = notched_pts(0, 0, W, DEP, 1250, 1460, 60, cr=40)
    d.pad("top", 0, W, 0, DEP, y, t=t, outline=pts, er=24, board=0,
          hole=[(x, z) for x, z in reversed(ellipse_pts(1690, DEP / 2, 110, 62))])
    d.add("hole-plug", "slab", "pad", plane="top", outline=poly_path(ellipse_pts(1690, DEP / 2, 98, 50)), w=[y + 14, y + t - 8], r=8)
    d.add("band", "slab", "plastic#2a2c30", plane="top", outline=poly_path(inset(pts, 6)), w=[y - 9, y + 1], r=2)
    # apron: white rectangular tube frame, black end plugs at the four corners
    # side rails stop at the waist notch with black plugs; a set-back piece runs behind the notch
    d.box("apron", [40, 565, 35, 1245, y - 9, 70], "frame", r=4, copies=[[0, 0, DEP - 105]])
    d.box("apron-h", [1465, 565, 35, W - 40, y - 9, 70], "frame", r=4, copies=[[0, 0, DEP - 105]])
    d.box("apron-n", [1245, 565, 95, 1465, y - 9, 130], "frame", r=4, copies=[[0, 0, DEP - 225]])
    d.box("apron-nplug", [1245, 563, 31, 1253, y - 8, 74], "cap", r=2, copies=[[212, 0, 0], [0, 0, DEP - 105], [212, 0, DEP - 105]])
    d.box("apron-end", [45, 570, 70, 85, y - 12, DEP - 70], "frame", r=4, copies=[[W - 130, 0, 0]])
    d.box("apron-plug", [34, 563, 31, 44, y - 8, 74], "cap", r=2, copies=[[W - 78, 0, 0], [0, 0, DEP - 105], [W - 78, 0, DEP - 105]])
    d.add("label", "decal", at=[W - 130, 598, DEP - 35 + 0.5], size=[150, 22], face="front", mat="plastic#2f5fa8")
    # legs 40 x 40 with black feet (the head pair set ~330 in from the head end, as in the photo), H stretcher frame
    xh = W - 330
    for k, (x, z) in enumerate(((95, 75), (xh, 75), (95, DEP - 75), (xh, DEP - 75))):
        d.box(f"leg{k}", [x - 20, 45, z - 20, x + 20, 566, z + 20], "frame", r=3)
        d.box(f"leg{k}-foot", [x - 23, 0, z - 23, x + 23, 50, z + 23], "cap", r=3)
        d.bolt(f"leg{k}-bolt", [x, 540, z + 20 if z > DEP / 2 else z - 20], face="front" if z > DEP / 2 else "back", d=10)
    d.box("stretch-end", [80, 260, 75, 110, 300, DEP - 75], "frame", r=3, copies=[[xh - 95, 0, 0]])
    d.box("stretch-long", [110, 235, DEP / 2 - 15, xh - 15, 275, DEP / 2 + 15], "frame", r=3)
    # under the head: stepped bracket (near side) carrying the arm/face rest pads, upper rest on the far side
    d.add("bracket", "sweep", "frame", path=[[1170, 566, DEP - 50], [1170, 480, DEP - 50], [1320, 480, DEP - 50], [1320, 360, DEP - 50], [1560, 360, DEP - 50]],
          section=[30, 22], r=3, bend=8)
    d.box("rest-plate", [1300, 342, 330, 1780, 352, DEP - 30], "frame", r=3)
    d.box("rest-arm", [1300, 352, 520, 1560, 392, DEP - 15], "pad", r=16, puff=3)
    d.box("rest-face", [1545, 352, 310, 1785, 400, DEP - 15], "pad", r=18, puff=3)
    d.box("rest-up-plate", [1560, 460, 40, 1790, 470, 300], "frame", r=3)
    d.box("rest-up", [1570, 470, 50, 1785, 505, 290], "pad", r=14, puff=3)
    d.box("rest-up-hang", [1560, 470, 40, 1590, 566, 70], "frame", r=3)
    d.save()
    DEP = keep


# ====================================================================== XY-K-SF-4 (new): multi-position chair-table, chair pose
def sf4new():
    global W, DEP; W = 1900
    keep = DEP; DEP = 700
    d = T("xy-k-sf-4-new", [W, DEP, 1400], {"fillet": "plastic#dfe2e6", "arm": "leather#26282c"})
    top = 600
    y, t = top + 60, 62
    bx, sx = 700, 1150                                     # back / seat, seat / leg hinges
    # backrest with an arched top, raised 75 deg, head roll and its black side pad
    R = DEP / 2 - 10
    arch = [(R + 40 - R * math.sin(math.radians(a)), DEP / 2 + R * math.cos(math.radians(a))) for a in range(0, 181, 12)]
    back = [(bx - 6, 10), (bx - 6, DEP - 10)] + list(reversed(arch))
    back = [(bx - 6, DEP - 10)] + [(x, z) for x, z in arch] + [(bx - 6, 10)]
    br = rot("z", -75, [bx, y, DEP / 2])
    bo = round_poly(back, 30, 4)
    d.pad("back", 40, bx - 6, 10, DEP - 10, y, t=t, outline=bo, er=24, r=br, board=0)
    d.add("back-board", "slab", "frame", plane="top", outline=poly_path(inset(bo, 25)), w=[y - 14, y + 1], r=3, rot=br)
    d.cyl("head-roll", [190, y + t + 70, 120], [190, y + t + 70, DEP - 120], 150, "pad", rot=br)
    d.box("back-rail", [120, y - 50, 60, bx - 20, y - 14, 100], "frame", r=5, rot=br, copies=[[0, 0, DEP - 160]])
    d.box("back-lever", [180, y - 60, -20, 230, y - 20, 10], "cap", r=6, rot=br)
    # armrests (photo): the far one horizontal on a chrome bracket, the near one folded up beside the backrest
    d.box("armrest-far", [520, 880, -85, 900, 945, -10], "arm", r=22, puff=3)
    d.add("armrest-bracket", "sweep", "chrome", path=[[640, 880, -45], [640, 760, -45], [660, 700, 20]], section=[30, 20], r=4, bend=40)
    d.box("armrest-near", [560, 620, DEP + 10, 650, 1000, DEP + 80], "arm", r=26, puff=3, rot=rot("z", 12, [600, 620, 0]))
    d.box("armrest-near-br", [590, 590, DEP - 20, 620, 680, DEP + 15], "chrome", r=4)
    # seat
    d.pad("seat", bx + 6, sx - 5, 0, DEP, y, t=t, er=22, cr=40)
    # two leg sections: far one level, near one hanging down
    d.pad("leg-far", sx + 6, W - 10, 0, DEP / 2 - 8, y, t=t, er=22, cr=45)
    d.box("leg-far-rail", [sx + 20, y - 45, 20, W - 120, y - 12, 50], "frame", r=5)
    lr = rot("z", -78, [sx, y, DEP / 2])
    d.pad("leg-near", sx + 6, sx + 570, DEP / 2 + 8, DEP, y, t=t, er=22, cr=45, r=lr)
    d.box("leg-near-rail", [sx + 20, y - 45, DEP - 50, sx + 540, y - 12, DEP - 20], "frame", r=5, rot=lr)
    d.box("leg-near-clamp", [sx + 490, y - 70, DEP / 2 + 60, sx + 550, y - 20, DEP / 2 + 120], "cap", r=5, rot=lr)
    d.cyl("leg-gas", [sx - 80, top + 10, DEP / 2], [sx + 420, y - 40, DEP / 2 - 160], 22, "steel")
    d.box("hinge", [bx - 22, y - 50, 55, bx + 22, y - 5, 80], "cap", r=4, copies=[[0, 0, DEP - 135], [sx - bx, 0, 0], [sx - bx, 0, DEP - 135]])
    swan_base(d, top=top, xb0=250, xb1=1650, arms=((560, 960), (1020, 1420)), loop=False, frame=(520, 1320), tri=False,
              castor_d=90)
    # black brake levers at the corners, triple foot switch with blue caps
    for k, (x, z) in enumerate(((250, DEP - 40), (1650, DEP - 40), (250, 40), (1650, 40))):
        d.box(f"brake{k}", [x - 60, 120, z - 15, x + 60, 145, z + 15], "cap", r=8, rot=rot("z", -20 if x < 900 else 20, [x, 130, z]))
    # triple foot switch on the floor in front of the head half (photo), cable up into the base
    d.box("pedal", [300, 0, DEP + 140, 640, 45, DEP + 300], "plastic#b8bcc3", r=14)
    d.add("pedal-btn", "sphere", "gloss#2a8fd8", at=[355, 50, DEP + 180], radii=[34, 24, 34], repeat={"n": 3, "step": [115, 0, 0]}, copies=[[0, 0, 85]])
    d.tube("pedal-cable", [[470, 20, DEP + 140], [440, 40, DEP + 40], [330, 200, DEP - 70]], 8, "bolt", bend=80, soft=True)
    flip_design(d)            # the photo shows the backrest (head) on the right of the visible long side
    d.save()
    DEP = keep


# ====================================================================== main
ALL = {"xy-k-sf-4-new": sf4new, "xy-k-sf-1": sf1, "xy-k-sf-4b": sf4b, "xy-k-sf-4c": sf4c, "xy-k-sf-4d": sf4d, "xy-k-sf-1b": sf1b, "xy-k-sf-2": sf2, "xy-k-sf-2-new": sf2new, "xy-k-sf-3-new": sf3new, "xy-k-sf-1-new": sf1new, "xy-k-sf-3": sf3, "xy-k-sf-4": sf4, "xy-k-sf-5": sf5}
if __name__ == "__main__":
    for k in (sys.argv[1:] or list(ALL)):
        ALL[k]()
