"""interactive-training-cart — white computer cart with a 55" TV (kinesio-2)."""
from k2lib import *

d = D("interactive-training-cart", [1250, 900, 1800], {
    "white": "plastic#f2f3f5", "edge": "plastic#dfe1e4", "black": "plastic#1b1c1f", "bezel": "gloss#16171a",
    "steel": "metal#c9ccd0", "blue": "gloss#2f6fbf"})
CX = 625
# --- base: two long flat white rails under the side panels (well in front of and behind the cabinet), joined by a
# grey crossbar at the front and a white one at the back; grey end caps; 4 light-grey castors at the rail ends
BZ0, BZ1 = 0, 900
for i, (x0, x1) in enumerate(((250, 340), (910, 1000))):
    d.box(f"rail-{i}", [x0, 95, BZ0, x1, 145, BZ1 - 12], "white", r=8)
    d.box(f"cap-{i}", [x0 + 2, 97, BZ1 - 14, x1 - 2, 143, BZ1], "plastic#b8bbc0", r=6)
    for z in (BZ0 + 45, BZ1 - 50):
        caster(d, f"castor-{i}-{z}", [(x0 + x1) / 2, 0, z], 75, "plastic#c3c0b8")
d.box("crossbar-front", [340, 100, BZ1 - 120, 910, 138, BZ1 - 60], "plastic#c4c7cc", r=6)
d.box("crossbar-back", [340, 100, BZ0 + 40, 910, 138, BZ0 + 100], "white", r=6)
# --- cabinet 650 wide: open shelves on the left, closed PC compartment on the right
CX0, CX1, CZ0, CZ1, CY0, CY1 = 300, 950, 230, 670, 145, 720
# side panels (both sides): a narrow back post and a wide diagonal strut with a long slot (top back -> bottom front);
# the rest is open (the shelves show through)
def side_frame(nm, x0, x1):
    d.box(nm + "-post", [x0, CY0, CZ0 + 15, x1, CY1, CZ0 + 55], "white", r=3)
    t0, t1, b0, b1 = CZ0 + 60, CZ0 + 185, CZ1 - 130, CZ1 - 5     # strut: top edge z t0..t1 at CY1, bottom b0..b1 at CY0
    o = (f"M {t0} {CY1} L {t1} {CY1} L {b1} {CY0} L {b0} {CY0} Z "
         f"M {t0 + 52} {CY1 - 70} L {t1 - 40} {CY1 - 70} L {b1 - 40} {CY0 + 70} L {b0 + 52} {CY0 + 70} Z")
    d.slab(nm, "side", o, [x0, x1], "white", r=3)
side_frame("side-l", CX0, CX0 + 18)
side_frame("side-r", CX1 - 18, CX1)
d.box("back-panel", [CX0, CY0, CZ0, CX1, CY1, CZ0 + 15], "white", r=3)
d.box("bottom", [CX0, CY0, CZ0, CX1, CY0 + 18, CZ1], "white", r=3)
for i, y in enumerate((320, 500)):
    d.box(f"shelf-{i}", [CX0 + 18, y, CZ0 + 15, 742, y + 16, CZ1 - 40], "white", r=3)
# PC compartment (closed box) with the black front window and its ports
d.box("pc-box", [742, CY0, CZ0 + 15, CX1 - 18, CY1 - 20, CZ1 - 5], "white", r=6)
d.box("pc-window", [762, 500, CZ1 - 6, 900, 670, CZ1 + 2], "bezel", r=6)
d.box("pc-port", [790, 560, CZ1 + 2, 850, 600, CZ1 + 4], "plastic#3d4046", r=2)
d.decal("pc-led", [880, 585, CZ1 + 2.6], [16, 5], "front", "gloss#d23a2c", soft=True)
d.decal("pc-slot", [830, 630, CZ1 + 2.6], [90, 6], "front", "plastic#5a5e64", soft=True)
d.decal("pc-jacks", [800, 525, CZ1 + 2.6], [50, 8], "front", "plastic#6a6e75", soft=True)
# --- lectern top deck: flat back part, sloping front with the keyboard; logo on its left face
deck = f"M {CZ0 - 10} {CY1 - 10} L {CZ0 - 10} 810 L {CZ0 + 150} 810 L {CZ1 + 30} 740 L {CZ1 + 30} {CY1 - 10} Z"
d.slab("deck", "side", deck, [CX0 - 10, CX1 + 10], "white", r=8)
xy_logo(d, "logo", [CX0 - 10.8, 768, CZ1 - 160], 34, "left")
# keyboard tray pulled out in front of the deck, running out right for the mouse pad
d.box("tray", [CX0 + 20, 700, CZ1 + 30, CX1 - 10, 716, CZ1 + 85], "white", r=4)
d.box("mouse-shelf", [CX1 - 30, 703, CZ1 - 90, 1170, 715, CZ1 + 90], "black", r=4)
d.box("tray-rail", [CX0 + 40, 682, CZ1 - 40, CX1 - 40, 700, CZ1 + 40], "steel", r=2)
d.box("keyboard", [CX0 + 40, 716, CZ1 + 45, CX0 + 490, 736, CZ1 + 75], "black", r=4)
d.box("keys", [CX0 + 52, 736, CZ1 + 55, CX0 + 478, 740, CZ1 + 65], "plastic#2b2d31", r=2)
d.box("mousepad", [CX1 + 5, 715, CZ1 - 80, 1160, 719, CZ1 + 82], "plastic#2a2c30", r=8)
d.sphere("mouse", [CX1 + 40, 730, CZ1 + 50], 10, "black", radii=[32, 18, 50])
# --- single white upright from the back of the deck to the TV mount
d.box("upright", [CX - 100, 790, CZ0 + 10, CX + 100, 1300, CZ0 + 90], "white", r=8)
d.box("mount", [CX - 70, 1180, CZ0 + 90, CX + 70, 1380, CZ0 + 110], "steel", r=3)
# --- 55" TV, thin black bezel, the menu picture (the crop is a skewed photo: masked outside the TV outline)
TZ0, TZ1 = CZ0 + 110, CZ0 + 165
X0, X1, Y0, Y1 = 10, 1240, 1070, 1795
d.box("tv-back", [X0 + 20, Y0 + 20, TZ0, X1 - 20, Y1 - 20, TZ1 - 10], "bezel", r=10)
scr(d, "tv", [X0, Y0, TZ1 - 12, X1, Y1, TZ1], "bezel", r=4, face="front", bezel=1, print="med_interactive-training-cart_screen")
# the crop is a skewed photo of the TV: its albedo was rectified to the TV's outer edge
# (tools/medical/scratch/kinesio-2-review/rectify.py, quad TL (10.5,10) TR (540,97) BR (525,446) BL (23,479) -> 1024 x 588)
d.save()
