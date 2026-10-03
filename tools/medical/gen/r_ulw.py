"""upper-limb-rehab-workstation (batch robot-1): mobile computer cart of the upper-limb system.
Review 2026-10-03: the photo looks from the FRONT-LEFT: the keyboard and the monitor are parallel to the solid face
with the black handle slot (= the front, z = D), so the open shelves with the slotted diagonal plank are on the cart's
LEFT side (x = 0), the pole and the printer stand at the back left, the keyboard tray overhangs the front at the right.
Base: two white rect bars along z with castors at their ends, a white platform and a grey metal front crossbar.
The monitor UI is drawn as the photo's rows of small book-cover tiles with captions (no screenCrop exists)."""
from r_lib import *

W, DP, H = 650, 560, 2250
d = D("upper-limb-rehab-workstation", [W, DP, H], {
    "white": "gloss#f4f5f6", "shelf": "plastic#e9ebee", "black": "plastic#1c1e21", "pad": "plastic#2a2c30",
    "grey": "plastic#b9bdc3", "print": "plastic#d3d6da", "ptop": "plastic#3a3d42", "paper": "gloss#2f6fc0",
    "green": "gloss#3aa35a", "bezel": "plastic#16181a", "metal": "metal#a9adb3",
    "ui": "gloss#f4f6f8", "bar": "gloss#dfe6ee", "cap": "plastic#b5bac0",
    "t1": "gloss#8e2f2a", "t2": "gloss#2f7d46", "t3": "gloss#24467e", "t4": "gloss#1f2226", "t5": "gloss#3a8f9a",
    "rubber": "rubber#b8bcc2", "vent": "plastic#2a2d32"})
# --- base: white rect bars along z at both sides, castors at their ends, white platform, grey front crossbar
d.bar("base-bar", [45, 100, 10], [45, 100, DP - 10], [60, 44], "white", r=6, copies=[[W - 90, 0, 0]])
d.caster("castor", [45, 0, 45], 75, "rubber", copies=[[W - 90, 0, 0], [0, 0, DP - 90], [W - 90, 0, DP - 90]])
d.box("base-plate", [75, 82, 25, W - 75, 102, 470], "white", r=6)
d.bar("base-cross", [75, 92, 505], [W - 75, 92, 505], [30, 22], "metal", r=4)
# --- cabinet: closed back, right side and front (black handle slot), open LEFT side with two shelves and the
#     slotted diagonal plank running from the top at the back to the bottom at the front
X0, X1, Z0, Z1, Y0, Y1 = 110, 560, 20, 470, 102, 790
d.box("cab-back", [X0, Y0, Z0, X1, Y1, Z0 + 20], "white", r=4)
d.box("cab-right", [X1 - 22, Y0, Z0, X1, Y1, Z1], "white", r=4)
d.box("cab-front", [X0, Y0, Z1 - 22, X1, Y1, Z1], "white", r=4)
d.box("cab-handle", [X1 - 70, 600, Z1, X1 - 50, 720, Z1 + 1.5], "vent", r=4, soft=True)
d.box("cab-shelf", [X0, 300, Z0 + 20, X1 - 22, 318, Z1 - 22], "shelf", r=3, copies=[[0, 210, 0]])
d.box("cab-floor", [X0, Y0, Z0 + 20, X1 - 22, Y0 + 20, Z1 - 22], "shelf", r=3)
d.box("cab-post", [X0, Y0, Z0, X0 + 22, Y1, Z0 + 30], "white", r=4, copies=[[0, 0, Z1 - Z0 - 30]])
d.slab("cab-plank", "side", "M 60 790 L 190 790 L 430 120 L 300 120 Z M 118 760 L 160 760 L 370 160 L 328 160 Z",
       [X0 - 4, X0 + 18], "white", r=6)
# --- top: white slab, a raised deck under the printer at the back left, keyboard tray overhanging the front right
d.box("top", [X0 - 12, Y1, Z0 - 10, X1 + 12, Y1 + 28, Z1 + 12], "white", r=10)
d.box("deck", [X0 - 12, Y1 + 28, Z0 - 10, 420, Y1 + 48, 330], "white", r=8)
d.slab("deck-ramp", "side", "M 330 818 L 330 838 L 390 818 Z", [X0 - 12, 420], "white", r=4)
d.box("tray", [250, Y1 + 14, 300, X1 + 60, Y1 + 32, DP], "white", r=8)
d.box("mousepad", [450, Y1 + 32, 320, X1 + 52, Y1 + 35, DP - 8], "pad", r=8)
kb = rot("y", 12, [395, 0, 465])
d.box("keyboard", [265, Y1 + 32, 410, 525, Y1 + 50, 520], "black", r=8, rot=kb)
d.box("keys", [275, Y1 + 50, 420, 515, Y1 + 52, 505], "pad", r=4, soft=True, rot=kb)
d.box("mouse", [570, Y1 + 35, 360, 610, Y1 + 62, 425], "black", r=18)
d.tube("mouse-cable", [[590, Y1 + 40, 360], [560, Y1 + 40, 320], [430, Y1 + 50, 300]], 6, "black", bend=30, soft=True)
# --- laser printer on the deck: light grey body, dark top with the output recess (blue paper), vent grille on the
#     left face, green label at the right of the front face
PY = Y1 + 48
d.box("printer", [120, PY, 40, 400, PY + 200, 330], "print", r=14)
d.box("printer-top", [126, PY + 200, 46, 394, PY + 222, 324], "ptop", r=10)
d.box("printer-tray", [170, PY + 216, 90, 350, PY + 224, 280], "black", r=4, soft=True)
d.box("printer-paper", [200, PY + 220, 120, 320, PY + 226, 230], "paper", r=3, soft=True)
d.box("printer-vent", [118.5, PY + 110, 120, 120, PY + 150, 220], "grey", r=3, soft=True)
d.box("printer-vent-lines", [118, PY + 115, 125, 119, PY + 145, 215], "cap", soft=True)
d.box("printer-label", [345, PY + 40, 330, 385, PY + 150, 331.5], "green", r=4, soft=True)
d.box("printer-slot", [150, PY + 168, 330, 330, PY + 180, 331.5], "ptop", r=3, soft=True)
d.tube("printer-cable", [[160, PY + 10, 40], [150, Y1 + 40, 20], [160, Y1 + 30, 10]], 7, "black", bend=20, soft=True)
# --- pole at the back left and the portrait monitor facing the front
PX, PZ = 160, 70
d.box("pole", [PX - 40, Y1 + 48, PZ - 40, PX + 40, 1500, PZ + 40], "white", r=8)
d.box("vesa", [PX - 30, 1380, PZ + 40, 330, 1480, PZ + 90], "black", r=8)
MX0, MX1, MY0, MY1, MZ = 30, 620, 1240, 2250, PZ + 90
d.box("monitor", [MX0, MY0, MZ, MX1, MY1, MZ + 55], "bezel", r=14)
d.box("monitor-ui", [MX0 + 18, MY0 + 18, MZ + 55, MX1 - 18, MY1 - 18, MZ + 57], "ui", r=4)
d.box("ui-bar", [MX0 + 18, MY1 - 60, MZ + 57, MX1 - 18, MY1 - 18, MZ + 58], "bar", soft=True)
d.box("ui-logo", [MX0 + 40, MY1 - 50, MZ + 58, MX0 + 120, MY1 - 30, MZ + 59], "t5", soft=True)
cols = ["t3", "t1", "t4", "t2", "t3", "t2", "t5", "t1"]
for row, (y, n) in enumerate(((2050, 8), (1850, 8), (1650, 2))):
    for k in range(n):
        x = 75 + k * 60
        d.box(f"tile-{row}-{k}", [x, y, MZ + 57, x + 46, y + 80, MZ + 58.5], cols[(k + row * 3) % len(cols)], r=2, soft=True)
        d.box(f"cap-{row}-{k}", [x + 4, y - 22, MZ + 57, x + 42, y - 14, MZ + 58], "cap", soft=True)
d.box("ui-links", [180, 1480, MZ + 57, 300, 1490, MZ + 58], "cap", soft=True, copies=[[150, 0, 0]])
d.box("monitor-ports", [MX0 - 2, MY0 + 300, MZ + 10, MX0, MY0 + 600, MZ + 45], "vent", r=2, soft=True)
d.save()
