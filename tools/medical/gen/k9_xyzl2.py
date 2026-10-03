"""XYZL-2 standing frame (single). The patient stands on the wooden footboard at the front (+z), chest in the cut-out
of the wooden table, hips in the grey sling; white square-tube base, central telescopic post at the back, a round-tube
arch on both sides joining the post, chrome telescopic side rails with black knobs under the table."""
from k9lib import *
d = K("xyzl-2", [740, 850, 1300], {
    "frame": "plastic#f1f2f0", "wood": "wood#d9a66a", "pad": "leather#6c6f73", "sling": "fabric#727579",
    "strap": "fabric#1b1c1e", "knob": "plastic#18191b", "chrome": "chrome"})
CX = 370
TY = 1080                   # table underside (adjustable 1020-1300 incl. top)
# --- base (photo): a round-tube U loop at the back (rounded rear corners) whose side runs end in short square
# stubs at the front with black end plugs; the wooden footboard fills it (cut-outs: left at mid-depth, right near
# the back, wavy front edge)
d.tube("base-loop", [[55, 17, 700], [55, 17, 115], [685, 17, 115], [685, 17, 700]], 32, "frame", bend=95)
for nm, x in (("l", 55), ("r", 685)):
    d.bar(f"stub-{nm}", [x, 18, 690], [x, 18, 846], [36, 36], "frame", r=3)
    d.box(f"side-end-{nm}", [x - 15, 3, 843, x + 15, 33, 847], "knob", r=1)
fb = (f"M 75 270 H 665 V 385 A 55 55 0 0 0 665 495 V 830 Q 610 850 560 830 Q 520 805 470 832 Q 420 852 370 830 "
      f"Q 300 800 250 838 Q 170 856 75 836 V 610 A 55 55 0 0 0 75 500 Z")
d.slab("footboard", "top", fb, [30, 48], "wood", r=3)
# --- central post (outer square tube + inner telescopic tube with black knobs)
PZ = 200
d.bar("post", [CX, 30, PZ], [CX, 760, PZ], [60, 60], "frame", r=5)
d.bar("post-in", [CX, 700, PZ], [CX, TY - 20, PZ], [48, 48], "frame", r=4)
d.box("post-foot", [CX - 60, 28, PZ - 60, CX + 60, 40, PZ + 60], "frame", r=4)
for k, y in enumerate((900, 1000)):
    d.cyl(f"post-knob-{k}", [CX + 24, y, PZ], [CX + 60, y, PZ], 12, "chrome")
    d.lathe(f"post-knob-h-{k}", [CX + 60, y, PZ], [[0, 0], [14, 0], [16, 8], [16, 22], [0, 26]], "knob", axis="x")
# side arches (photo): one round-tube loop rising from the front stubs, running back along both sides at the top
# and across just in front of the post (the cross run carries the adjustment holes)
AZ = 790
d.tube("arch", [[55, 30, AZ], [55, 900, AZ], [55, 900, PZ + 45], [685, 900, PZ + 45], [685, 900, AZ], [685, 30, AZ]],
       34, "frame", bend=120)
d.box("post-clamp", [CX - 42, 875, PZ - 34, CX + 42, 925, PZ + 64], "frame", r=6)
d.decal("hbar-holes", [CX - 230, 900, PZ + 62.5], [5, 5], "front", "knob", repeat=rep(4, [48, 0, 0]), mirror="x")
# --- table: wood top with a chest cut-out at the front, white frame under it, chrome rails + black knobs
TZ0, TZ1 = 160, 560
top = (f"M 20 {TZ0} H 720 V {TZ1} H {CX + 165} Q {CX + 150} {TZ1 - 95} {CX} {TZ1 - 95} Q {CX - 150} {TZ1 - 95} {CX - 165} {TZ1} "
       f"H 20 Z")
d.slab("table", "top", top, [TY, TY + 22], "wood", r=4)
d.bar("tframe-f", [60, TY - 15, TZ1 - 30], [680, TY - 15, TZ1 - 30], [40, 28], "frame", r=4)
d.bar("tframe-b", [60, TY - 15, TZ0 + 40], [680, TY - 15, TZ0 + 40], [40, 28], "frame", r=4)
for nm, s in (("l", -1), ("r", 1)):
    x = CX + s * 300
    d.bar(f"tframe-{nm}", [x, TY - 15, TZ0 + 40], [x, TY - 15, TZ1 - 30], [30, 28], "frame", r=4)
    xe = CX + s * 345
    d.cyl(f"rail-{nm}", [CX + s * 310, TY - 15, TZ1 - 30], [xe, TY - 15, TZ1 - 30], 26, "chrome")
    d.lathe(f"rail-knob-{nm}", [xe, TY - 15, TZ1 - 30], [[0, 0], [18, 0], [20, 10], [20, 26], [0, 30]], "knob", axis="x",
            rot=rot("y", 180, [xe, TY - 15, TZ1 - 30]) if s < 0 else None)
    d.cyl(f"rail-knob2-{nm}", [CX + s * 250, TY - 30, TZ1 - 30], [CX + s * 250, TY - 75, TZ1 - 30], 26, "knob")
# chest pad under the cut-out on two flat white brackets
d.loft("chest-pad", [sec(TY - 150, 330, 70, 30, CX, TZ1 - 80), sec(TY - 5, 330, 70, 30, CX, TZ1 - 80)], "pad")
d.box("chest-pad-face", [CX - 150, TY - 140, TZ1 - 46, CX + 150, TY - 15, TZ1 - 42], "pad", r=2, puff=4)
for nm, x in (("l", CX - 100), ("r", CX + 100)):
    d.box(f"pad-bracket-{nm}", [x - 18, TY - 160, TZ1 - 40, x + 18, TY - 10, TZ1 - 34], "frame", r=3)
    d.decal(f"pad-bolt-{nm}", [x, TY - 60, TZ1 - 33.4], [8, 8], "front", "chrome")
# hip sling (photo): a soft grey trough (open at the top) hung at its 4 corners; the rims sag between the corners and
# the front wall bulges; drawn as 16 thin slices across x. Black strap bundles from the table frame to the corners;
# two belts cross the front from the upper left down to the lower right.
SW = 380
X0, X1 = CX - SW / 2, CX + SW / 2
d.strap("sling", [[CX, 790, 661], [CX, 650, 610], [CX, 625, 520], [CX, 660, 440], [CX, 800, 418]], [SW, 12], "sling", bend=80, soft=True)
def sag(y_end, y_mid):          # quadratic rim between the two hung corners, through y_mid at the middle
    return y_end, 2 * y_mid - y_end
ye, yc = sag(880, 790)
d.slab("sling-front", "front", f"M {X0} 770 L {X0} {ye} Q {CX} {yc} {X1} {ye} L {X1} 770 Q {CX} 760 {X0} 770 Z", [655, 668], "sling", r=5, soft=True)
d.tube("sling-rim", [[X0 + (X1 - X0) * t, (1 - t) ** 2 * ye + 2 * t * (1 - t) * yc + t * t * ye, 662] for t in (0, .17, .33, .5, .67, .83, 1)],
       16, "fabric#8e9195", bend=40, soft=True)
ye2, yc2 = sag(905, 850)
d.slab("sling-back", "front", f"M {X0} 790 L {X0} {ye2} Q {CX} {yc2} {X1} {ye2} L {X1} 790 Z", [412, 425], "sling", r=5, soft=True)
for nm, s in (("l", -1), ("r", 1)):
    xa, xc = CX + s * 250, CX + s * (SW / 2 - 14)
    d.strap(f"sling-strap-{nm}", [[xa, TY - 75, TZ1 - 30], [xa - s * 25, 985, 610], [xc, 880, 652]], [42, 4], "strap", bend=60, soft=True)
    d.strap(f"sling-strap2-{nm}", [[xa - s * 12, TY - 75, TZ1 - 36], [xc + s * 4, 990, 470], [xc, 900, 424]], [42, 4], "strap", bend=60, soft=True)
d.strap("belt-a", [[CX - 180, 868, 671], [CX - 20, 800, 672], [CX + 150, 690, 668], [CX + 185, 655, 645]], [50, 4], "strap", bend=50, roll=90, soft=True)
d.strap("belt-b", [[CX - 186, 800, 671], [CX - 40, 730, 670], [CX + 90, 650, 640]], [46, 4], "strap", bend=50, roll=90, soft=True)
d.save()
