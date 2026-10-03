"""XYD-1 electric standing frame. The patient stands at the front (z = depth) on the wooden footboard, knees against
the blue knee pad, held by the striped sling from two chrome J hooks under the tray table; blue square-tube box
frame on 4 small castors, an electric actuator lifts the central column with the tray table and its chest pad."""
from k6lib import *

W, DEP, H = 800, 1000, 1150
d = D("xyd-1", [W, DEP, H], {"blue": "gloss#2f4fa6", "pad": "leather#5876c4", "wood": "wood#f2bb55",
                             "black": "plastic#1d1f22", "foam": "rubber#1f2124", "chrome": "chrome",
                             "red": "fabric#b3261e", "yel": "fabric#e8c21e", "grn": "fabric#23873a",
                             "navy": "fabric#25285a"})
S = [30, 30]
XL, XR = 40, W - 40
ZB, ZF = 40, DEP - 40
YB = 75                     # base rails centre
YM = 620                    # mid frame
# --- base frame and castors
d.bar("base-l", [XL, YB, ZB - 15], [XL, YB, ZF + 15], S, "blue", r=3, mirror="x")
d.bar("base-b", [XL, YB, ZB], [XR, YB, ZB], S, "blue", r=3)
d.bar("base-f", [XL, YB, ZF], [XR, YB, ZF], S, "blue", r=3)
for z in (ZB, ZF):
    caster(d, f"cas{z}", [XL, 0, z], 50, "rubber#222326", mirror="x")
# chrome outrigger rods with clamps along both sides
d.cyl("out-rod", [14, 110, 60], [14, 110, DEP - 60], 22, "chrome", mirror="x")
d.box("out-clamp", [2, 90, 50, 40, 130, 110], "chrome", r=6, mirror="x", copies=[[0, 0, DEP - 160]])
# --- uprights and the mid frame (ladder at the back), control box, white end cap
for z in (60, 600):
    d.bar(f"up{z}", [XL, YB + 15, z], [XL, YM, z], S, "blue", r=3, mirror="x")
d.bar("mid-l", [XL, YM, ZB], [XL, YM, 620], S, "blue", r=3, mirror="x")
for z in (ZB, 200, 330, 620):
    d.bar(f"mid-x{z}", [XL, YM, z], [XR, YM, z], S, "blue", r=3)
d.box("ctl-box", [110, YM + 15, 70, 300, YM + 80, 190], "black", r=8)
d.box("ctl-box2", [300, YM + 15, 90, 380, YM + 50, 150], "black", r=6)
d.cyl("roller", [XL + 15, YM - 60, 560], [XL + 75, YM - 60, 560], 46, "plastic#efefe8")
# --- central lifting column on the actuator, chrome inner tubes up to the table
CX = W / 2
d.box("act", [CX - 60, 95, 260, CX + 60, 330, 380], "black", r=14)
d.cyl("act-motor", [CX - 55, 160, 400], [CX - 55, 160, 260], 70, "black")
d.box("act-label", [CX - 20, 200, 380, CX + 20, 240, 381], "plastic#d8d8d8", soft=True)
d.bar("column", [CX, 330, 320], [CX, 900, 320], [110, 90], "blue", r=6)
d.cyl("col-in", [CX - 32, 880, 320], [CX - 32, 1000, 320], 28, "chrome", copies=[[64, 0, 0]])
d.box("col-head", [CX - 70, 985, 290, CX + 70, 1000, 350], "chrome", r=3)
# knee pad on a bracket in front of the column
d.bar("knee-arm", [CX, 600, 365], [CX, 600, 470], [80, 50], "blue", r=4)
d.box("knee-pad", [CX - 155, 440, 470, CX + 155, 790, 540], "pad", r=22, puff=6)
# --- tray table with a front cut-out and a standing chest pad at its inner edge
TZ0, TZ1 = 240, 830
tout = (f"M 20 {TZ0 + 20} Q 20 {TZ0} 40 {TZ0} L {W - 40} {TZ0} Q {W - 20} {TZ0} {W - 20} {TZ0 + 20} L {W - 20} {TZ1 - 20} "
        f"Q {W - 20} {TZ1} {W - 40} {TZ1} L {CX + 130} {TZ1} L {CX + 130} {TZ1 - 150} Q {CX + 130} {TZ1 - 190} {CX + 90} {TZ1 - 190} "
        f"L {CX - 90} {TZ1 - 190} Q {CX - 130} {TZ1 - 190} {CX - 130} {TZ1 - 150} L {CX - 130} {TZ1} L 40 {TZ1} "
        f"Q 20 {TZ1} 20 {TZ1 - 20} Z")
d.slab("table", "top", tout, [1000, 1026], "wood", r=4)
d.box("chest-pad", [CX - 85, 900, TZ1 - 240, CX + 85, H, TZ1 - 185], "pad", r=18, puff=4)
d.box("chest-bracket", [CX - 40, 900, TZ1 - 265, CX + 40, 1000, TZ1 - 238], "chrome", r=3)
# --- side handles: from the front base corners rising backward, black foam grips on the top, down at the back
for s, x in (("l", XL), ("r", XR)):
    d.tube(f"handle-{s}", [[x, YB + 15, ZF - 20], [x, 960, 470], [x, 960, 170], [x, YM + 15, 150]], 30, "blue", bend=90)
    d.tube(f"foam-{s}", [[x, 700, 610], [x, 960, 460], [x, 960, 190]], 44, "foam", bend=80)
# chrome lever with a black grip at the back-left
d.cyl("lever", [16, 125, 110], [22, 760, 70], 22, "chrome")
d.cyl("lever-grip", [22, 760, 70], [24, 900, 62], 32, "black")
d.box("lever-link", [6, 100, 100, 30, 140, 160], "chrome", r=4)
# --- wooden footboard with a round cut-out at its right end and two heel hollows
FZ0, FZ1 = 560, 985
fout = (f"M 60 {FZ0 + 30} Q 60 {FZ0} 90 {FZ0} L {W - 70} {FZ0} Q {W - 40} {FZ0} {W - 40} {FZ0 + 30} L {W - 40} {(FZ0 + FZ1) / 2 - 95} "
        f"A 95 95 0 0 0 {W - 40} {(FZ0 + FZ1) / 2 + 95} L {W - 40} {FZ1 - 30} Q {W - 40} {FZ1} {W - 70} {FZ1} L 90 {FZ1} "
        f"Q 60 {FZ1} 60 {FZ1 - 30} Z")
d.slab("footboard", "top", fout, [YB + 15, YB + 40], "wood", r=4)
d.decal("heel", [CX - 120, YB + 40.6, 800], [110, 150], "top", "wood#e4a645", soft=True, copies=[[240, 0, 0]])
# --- chrome J hooks under the table's front corners and the striped sling
for s, x in (("l", 110), ("r", W - 110)):
    d.tube(f"hook-{s}", [[x, 1000, 700], [x, 1000, 790], [x, 930, 815], [x, 860, 790], [x, 880, 740]], 18, "chrome", bend=40)


def strap(id, path, bend=80):
    """Woven multi-stripe strap (photo): navy edges, then red, yellow and a green middle - stacked straps of falling
    width and rising thickness make the stripes."""
    d.strap(id, path, [50, 3], "navy", bend=bend, soft=True)
    d.strap(id + "-r", path, [40, 4], "red", bend=bend, soft=True)
    d.strap(id + "-y", path, [28, 5], "yel", bend=bend, soft=True)
    d.strap(id + "-g", path, [14, 6], "grn", bend=bend, soft=True)


# upper sling: from the left J hook down round the patient's back and up to the right hook
strap("sling", [[115, 860, 760], [220, 700, 850], [CX, 630, 880], [W - 220, 700, 850], [W - 115, 860, 760]], bend=160)
# a single strap hangs straight from the right hook, black buckle at its end
strap("hang", [[W - 100, 860, 800], [W - 100, 470, 805]], bend=10)
d.box("hang-buckle", [W - 128, 455, 798, W - 72, 480, 812], "black", r=3, soft=True)
# lower (thigh) harness: buckled to both sides of the knee pad, two straps hang forward and down in loops above the
# footboard; a loose end lies on the footboard
for s_, x in (("l", CX - 168), ("r", CX + 168)):
    d.box(f"kp-buckle-{s_}", [x - 14, 520, 535, x + 14, 560, 560], "black", r=4)
strap("harness", [[CX - 168, 540, 560], [CX - 160, 360, 690], [CX - 70, 230, 780], [CX + 70, 230, 780],
                  [CX + 160, 360, 690], [CX + 168, 540, 560]], bend=120)
strap("harness2", [[CX - 168, 520, 562], [CX - 110, 300, 640], [CX + 10, 200, 700], [CX + 120, 290, 640],
                   [CX + 168, 520, 562]], bend=110)
strap("loose", [[CX - 260, YB + 42, 900], [CX - 100, YB + 42, 930], [CX + 20, YB + 42, 900]], bend=60)
d.save()
