"""lower-limb-rehab-system (batch robot-1): electric tilt table with a stepping mechanism, drawn in its HORIZONTAL
rest pose (the catalogue photo shows it tilted up with a patient). Foot end at x = 0 with the control pole and
monitor, head end at x = W with the chrome shoulder-harness frame; the front (z = D) is the logo side.
Review 2026-10-03: control pole at the back foot corner with its foot bent into the base rail (as in the photo),
heavy base tubes with castor sleeves, a scissor lift of wide white arms with pivot bolts and sub-frames, the deep
logo side panel with 翔宇医疗 / XIANGYU MEDICAL, shell foot pedals with straps, dark V links, springs and side
guide rods, wrap-around knee cuffs on brackets, a slate encoder handle with an orange tip."""
import math
import p1lib
from r_lib import *

# 医 疗 (the same strokes as t4lib; t4lib itself cannot be imported here: it restores lib's D methods)
p1lib._FONT.setdefault("医", (0.92, [[(0.92, 0.95), (0.04, 0.95), (0.04, 0), (0.94, 0)], [(0.3, 0.86), (0.22, 0.66)],
                                     [(0.26, 0.74), (0.74, 0.74)], [(0.16, 0.46), (0.84, 0.46)],
                                     [(0.47, 0.74), (0.45, 0.46), (0.22, 0.14)], [(0.5, 0.42), (0.8, 0.14)]]))
p1lib._FONT.setdefault("疗", (0.95, [[(0.52, 1), (0.52, 0.9)], [(0.2, 0.86), (0.95, 0.86)], [(0.2, 0.86), (0.2, 0.36), (0.04, 0.02)],
                                     [(0, 0.72), (0.1, 0.62)], [(0, 0.44), (0.1, 0.52)],
                                     [(0.38, 0.66), (0.86, 0.66), (0.62, 0.48)], [(0.62, 0.48), (0.62, 0), (0.5, 0.05)]]))


def poly(pts):
    return "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts) + " Z"


def arch(cz, cy, ro, ri, n=14):
    """half annulus (upper half) in a side plane (z, y) around (cz, cy)."""
    o = [(cz + ro * math.cos(math.pi * k / n), cy + ro * math.sin(math.pi * k / n)) for k in range(n + 1)]
    i = [(cz + ri * math.cos(math.pi * k / n), cy + ri * math.sin(math.pi * k / n)) for k in range(n, -1, -1)]
    return poly(o + i)


W, DP, H = 2150, 850, 1300
d = D("lower-limb-rehab-system", [W, DP, H], {
    "white": "plastic#f4f4f4", "blue": "leather#6aa9dc", "plate": "metal#c3c7cc", "chrome": "chrome",
    "black": "plastic#1d1f22", "web": "fabric#16181b", "pad": "leather#202226", "grey": "plastic#9aa0a8",
    "logo": "gloss#1f5fb8", "screen": "screen", "rubber": "rubber#8f969e", "slate": "plastic#465260",
    "link": "plastic#3a4049", "orange": "gloss#e8641e", "bolt": "metal#9aa0a8", "dgrey": "plastic#5a626c"})
ZC = DP / 2
Z0, Z1 = 125, 725                      # table top width
# --- base frame: heavy white rect tubes, castor sleeves over 4 castors Ø100
d.bar("base-rail", [40, 140, 90], [W - 60, 140, 90], [72, 70], "white", r=8, copies=[[0, 0, 670]])
d.bar("base-cross", [60, 140, 90], [60, 140, 760], [80, 70], "white", r=8, copies=[[W - 150, 0, 0]])
d.cyl("castor-sleeve", [60, 108, 90], [60, 200, 90], 112, "white", copies=[[W - 150, 0, 0], [0, 0, 670], [W - 150, 0, 670]])
d.caster("castor", [60, 0, 90], 100, "rubber", copies=[[W - 150, 0, 0], [0, 0, 670], [W - 150, 0, 670]])
# --- scissor lift under the torso part: wide white arms with pivot bolts, lower slide rails and an upper sub-frame
for k, z in enumerate((165, 685)):
    zi = z + (40 if k == 0 else -40)
    d.bar(f"lift-rail-{k}", [950, 205, z], [1960, 205, z], [70, 46], "white", r=6)
    d.bar(f"lift-sub-{k}", [950, 515, z], [1960, 515, z], [70, 50], "white", r=6)
    d.bar(f"scissor-a-{k}", [1010, 235, zi], [1880, 485, zi], [80, 40], "white", r=8)
    d.bar(f"scissor-b-{k}", [1010, 485, z], [1880, 235, z], [80, 40], "white", r=8)
    s = -1 if k == 0 else 1
    d.cyl(f"scissor-pin-{k}", [1445, 360, zi - s * 30], [1445, 360, z + s * 26], 30, "bolt")
    for j, (x, y) in enumerate(((1010, 235), (1880, 485), (1010, 485), (1880, 235))):
        zz = zi if j < 2 else z
        d.cyl(f"scissor-end-{k}-{j}", [x, y, zz - 24], [x, y, zz + 24], 46, "black" if j % 2 else "white")
        d.cyl(f"scissor-bolt-{k}-{j}", [x, y, zz - 30 * s], [x, y, zz + 30 * s], 16, "bolt")
d.cyl("lift-act", [1150, 250, ZC], [1700, 470, ZC], 60, "grey")
d.cyl("lift-rod", [1700, 470, ZC], [1790, 506, ZC], 34, "chrome")
d.cyl("tilt-act", [700, 210, ZC], [960, 540, ZC], 50, "grey")
d.cyl("tilt-pivot", [990, 560, Z0 + 20], [990, 560, Z1 - 20], 50, "dgrey")
# --- table frame, deep side panels (logo on the front one), grey leg plate, blue segmented mattress
d.box("frame", [420, 560, Z0 + 10, W - 80, 625, Z1 - 10], "white", r=10)
d.box("frame-side", [1150, 545, Z1 - 12, W - 80, 640, Z1 + 6], "white", r=10, copies=[[0, 0, Z0 - Z1 + 6]])
d.slab("side-panel", "front", rpoly([(420, 655), (1150, 655), (1150, 560), (1050, 455), (420, 455)], 45),
       [Z1 - 12, Z1 + 8], "white", r=8, copies=[[0, 0, Z0 - Z1 - 8]])
d.box("leg-plate", [420, 625, Z0, 1000, 650, Z1], "plate", r=8)
for k, (x0, x1) in enumerate(((1005, 1240), (1250, 1830), (1840, 2070))):
    d.box(f"mattress-{k}", [x0, 625, Z0, x1, 712, Z1], "blue", r=26, puff=6)
d.box("pillow", [1880, 708, ZC - 160, 2040, 765, ZC + 160], "blue", r=24, puff=6)
# brand on the panel: the round blue mark with the white cut, 翔宇医疗 and XIANGYU MEDICAL under it
ZF = Z1 + 8
d.cyl("logo-disc", [500, 560, ZF], [500, 560, ZF + 2], 100, "logo")
for j, sg in enumerate((1, -1)):           # the white "<" chevron cut into the right half of the mark
    a = math.degrees(math.atan2(sg * 36, 34))
    at = [500 + 22, 560 + sg * 17, ZF + 2.4]
    d.decal(f"logo-chev-{j}", at, [52, 10], "white", "front", soft=True, rot=rot("z", a, at))
text(d, "logo-cn", "翔宇医疗", [570, 560, ZF + 0.6], 52, "logo", stroke=6, gap=0.12)
text(d, "logo-en", "XIANGYU MEDICAL", [572, 528, ZF + 0.6], 19, "logo", stroke=2.6, gap=0.3)
text(d, "xiangyu", "XIANGYU", [1250, 575, Z1 + 6.6], 34, "dgrey", stroke=4.5)
# --- foot end: white housing wedge, blue foot block and side blocks
d.slab("foot-housing", "front", "M 70 210 L 420 210 L 420 640 L 190 640 L 70 470 Z", [160, 690], "white", r=20)
d.box("foot-block", [330, 640, Z0 + 20, 420, 765, Z1 - 20], "blue", r=24, puff=4)
d.box("foot-side", [420, 650, Z1 - 95, 620, 735, Z1], "blue", r=22, puff=4, copies=[[0, 0, Z0 - Z1 + 95]])
# --- stepping drive: chrome guide rods along both sides, a shell pedal per foot (sole, heel cup, toe and ankle
#     straps), a slate carriage, dark V links to a pivot under the leg plate, a spring towards the head end
for k, z in enumerate((105, 745)):
    d.cyl(f"guide-{k}", [240, 440, z], [830, 440, z], 40, "chrome")
    d.cyl(f"guide-cap-{k}", [225, 440, z], [242, 440, z], 46, "dgrey", copies=[[603, 0, 0]])
    d.box(f"guide-bracket-{k}", [200, 405, z - 30, 245, 475, z + 30], "white", r=8, copies=[[625, 0, 0]])
for k, z in enumerate((ZC - 130, ZC + 130)):
    x = 300 - k * 40                                # the two pedals stand at different steps
    so = -1 if k == 0 else 1                        # outer side
    zo = z + so * 88
    d.box(f"pedal-sole-{k}", [x, 650, z - 72, x + 30, 935, z + 72], "black", r=14)
    d.box(f"pedal-heel-{k}", [x + 20, 650, z - 72, x + 115, 690, z + 72], "black", r=12)
    d.box(f"pedal-wall-{k}", [x + 20, 650, z - 78, x + 105, 770, z - 64], "black", r=6, copies=[[0, 0, 142]])
    d.strap(f"toe-strap-{k}", [[x + 28, 845, z - 74], [x + 85, 850, z - 52], [x + 112, 855, z], [x + 85, 850, z + 52],
                               [x + 28, 845, z + 74]], [80, 5], "web", bend=30, roll=90)
    d.strap(f"ankle-strap-{k}", [[x + 28, 735, z - 74], [x + 95, 740, z - 52], [x + 120, 742, z], [x + 95, 740, z + 52],
                                 [x + 28, 735, z + 74]], [50, 5], "web", bend=30, roll=90)
    d.box(f"pedal-carriage-{k}", [x - 70, 700, z - 45, x, 810, z + 45], "slate", r=14)
    d.cyl(f"pedal-axle-{k}", [x - 40, 760, zo - so * 50], [x - 40, 760, zo + so * 6], 34, "chrome")
    d.sphere(f"pedal-dot-{k}", [x - 40, 760, zo + so * 10], 18, "orange")
    piv = [x + 190, 470, zo]
    d.bar(f"link-a-{k}", [x - 40, 760, zo], piv, [34, 20], "link", r=5, roll=90)
    d.bar(f"link-b-{k}", [x + 10, 925, zo], piv, [30, 18], "link", r=5, roll=90)
    d.cyl(f"link-pivot-{k}", [piv[0], piv[1], zo - 22], [piv[0], piv[1], zo + 22], 36, "dgrey")
    d.coil(f"spring-{k}", [piv[0] + 20, piv[1], zo], [piv[0] + 400, piv[1] + 20, zo], 42, 6, 16, "chrome")
    d.cyl(f"step-rod-{k}", [piv[0] + 400, piv[1] + 20, zo], [piv[0] + 470, piv[1] + 24, zo], 30, "chrome")
# --- knee cuffs: black wrap-around pads with a strap and a buckle, on grey brackets from the leg plate
for k, z in enumerate((ZC - 130, ZC + 130)):
    d.bar(f"knee-bracket-{k}", [760, 650, z - 98], [760, 770, z - 98], [44, 12], "plate", r=4, copies=[[0, 0, 196]])
    d.slab(f"knee-cuff-{k}", "side", arch(z, 770, 96, 66), [690, 830], "pad", r=12)
    d.slab(f"knee-strap-{k}", "side", arch(z, 770, 100, 94), [732, 788], "web", r=2, soft=True)
    d.box(f"knee-buckle-{k}", [742, 862, z - 22, 778, 872, z + 22], "bolt", r=3, soft=True)
# --- head end: chrome harness frame (two posts, crossbar), black harness straps lying on the torso, pelvic belt
d.cyl("hframe-post", [2090, 560, Z0 - 10], [2090, 1080, Z0 - 10], 25, "chrome", copies=[[0, 0, Z1 - Z0 + 20]])
d.cyl("hframe-bar", [2090, 1080, Z0 - 10], [2090, 1080, Z1 + 10], 25, "chrome")
d.sphere("hframe-corner", [2090, 1080, Z0 - 10], 25, "chrome", copies=[[0, 0, Z1 - Z0 + 20]])
for k, z in enumerate((ZC - 110, ZC + 110)):
    d.strap(f"shoulder-{k}", [[2090, 1065, z], [1990, 900, z], [1880, 780, z], [1760, 762, z]], [55, 4], "web", bend=80)
d.box("chest-vest", [1450, 708, ZC - 190, 1760, 765, ZC + 190], "pad", r=24, puff=4)
for k in range(3):
    d.box(f"vest-buckle-{k}", [1500 + k * 90, 765, ZC - 28, 1550 + k * 90, 773, ZC + 28], "dgrey", r=3, soft=True)
d.box("pelvic-belt", [1120, 708, Z0 + 20, 1220, 740, Z1 - 20], "web", r=12)
d.box("pelvic-buckle", [1140, 740, ZC - 30, 1200, 752, ZC + 30], "dgrey", r=4)
# --- control pole at the back foot corner: white pole whose foot bends into the base rail, black monitor tilted up,
#     a hand pendant on a cable, the encoder handle (slate barrel, orange tip, pistol grip, coiled cable)
PX, PZ = 170, 90
d.tube("pole", [[PX, 1150, PZ], [PX, 215, PZ], [PX + 190, 205, PZ]], 56, "white", bend=120)
d.box("pole-head", [PX - 30, 1150, PZ - 30, PX + 30, 1200, PZ + 30], "black", r=8)
d.box("monitor-mount", [PX - 45, 1185, PZ - 20, PX + 45, 1215, PZ + 60], "black", r=6)
tilt = rot("x", 32, [PX, 1225, PZ + 40])
d.screen("monitor", [PX - 160, 1215, PZ - 70, PX + 160, 1242, PZ + 160], "black", face="top", r=10, rot=tilt, bezel=18)
d.box("pendant", [PX - 70, 900, PZ + 34, PX - 20, 1100, PZ + 64], "black", r=12)
d.box("pendant-keys", [PX - 60, 990, PZ + 64, PX - 30, 1080, PZ + 66], "dgrey", r=3, soft=True)
d.tube("pendant-cable", [[PX - 45, 1100, PZ + 50], [PX - 40, 1170, PZ + 40], [PX - 10, 1190, PZ + 20]], 7, "black",
       bend=30, soft=True)
d.tube("encoder-arm", [[PX + 28, 830, PZ], [PX + 90, 830, PZ]], 26, "chrome")
d.cyl("encoder", [PX + 90, 830, PZ], [PX + 260, 830, PZ], 56, "slate")
d.cyl("encoder-nose", [PX + 260, 830, PZ], [PX + 300, 830, PZ], 30, "chrome")
d.sphere("encoder-tip", [PX + 300, 830, PZ], 22, "orange")
d.bar("encoder-grip", [PX + 120, 820, PZ], [PX + 100, 700, PZ], [36, 46], "slate", r=12)
d.coil("encoder-cable", [PX + 100, 700, PZ], [PX + 110, 560, PZ + 10], 34, 6, 10, "black", soft=True)
d.tube("pole-cable", [[PX - 45, 900, PZ + 50], [PX - 30, 860, PZ + 40], [PX + 80, 830, PZ + 20]], 7, "black",
       bend=40, soft=True)
d.save()
