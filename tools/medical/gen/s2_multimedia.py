"""multimedia-scenario-interactive-system: the ceiling unit — a white square ceiling plate with a small white projector
+ motion camera hanging under its centre (the projected floor game is light, not part of the item)."""
from s2lib import *

W, Dp, H = 450, 350, 255
d = D("multimedia-scenario-interactive-system", [W, Dp, H], {"shell": "plastic#ebe8e2", "dark": "black#18191c"})
c, cz = W / 2, Dp / 2
d.loft("plate", [sec(75, 375, 290, 16, c, cz), sec(82, 388, 300, 14, c, cz), sec(H - 6, 448, 348, 10, c, cz), sec(H, 450, 350, 10, c, cz)], "shell")
d.lathe("plate-mark", [c, 74.5, cz], [[46, 0], [50, 0], [50, 0.8], [46, 0.8], [46, 0]], "plastic#dfe2e4", soft=True)
# faint round mark on the sloping front face (as in the photo)
d.lathe("front-mark", [c, 118, 330.4], [[15, 0], [18, 0], [18, 1.2], [15, 1.2], [15, 0]], "plastic#d6d9dc", axis="z",
        soft=True, rot=rot("x", 8.2, [c, 118, 330.4]))
# photo: a thin rod between the plate and the projector
d.cyl("neck", [c, 64, cz], [c, 76, cz], 16, "shell")
d.cyl("neck-base", [c, 73, cz], [c, 76, cz], 40, "shell")
d.box("projector", [c - 83, 0, cz - 55, c + 83, 66, cz + 55], "shell", r=12)
F = cz + 55
# front (photo): the lit lens a little right of the middle, a dark sensor window at the lower right, a small grey
# label at the upper left
d.cyl("lens-ring", [c + 4, 38, F - 2], [c + 4, 38, F + 3], 34, "plastic#d4d6d8")
d.cyl("lens", [c + 4, 38, F + 3], [c + 4, 38, F + 4.5], 24, "led", soft=True)
d.box("camera", [c + 38, 9, F - 1, c + 62, 18, F + 1.5], "dark", r=2)
d.box("label", [c - 64, 44, F - 0.5, c - 36, 47, F + 0.6], "plastic#a8abae", soft=True, copies=[[0, -6, 0]])
d.box("vent", [c - 84, 20, cz - 40, c - 83, 52, cz + 40], "plastic#c6cacd", soft=True)
d.save()
