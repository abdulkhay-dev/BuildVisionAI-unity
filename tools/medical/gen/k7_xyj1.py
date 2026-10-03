"""xyj-1 Shoulder Rotation Exerciser (wall). Photo front, 1 mm/px: W 390 = left pin tip .. lever knob, H 980 incl.
the crank grip hanging below the bottom plate."""
import math
from k7lib import *

d = D("xyj-1", [390, 220, 980], {
    "teal": "plastic#08855f", "tealdk": "plastic#055a40", "chrome": "chrome", "steel": "metal#c9ccd0",
    "black": "plastic#1b1d1f", "rubber": "rubber#202224"})
CX = 105
rail_unit(d, CX, 980, 140, (425, 650), None, plate_h=(50, 48), bot_txt="MEDICAL", bot_txt_mat="plastic#2a3a33",
          lever=(372, 568, 32), lever_mat="metal#3a3d40")
# --- friction hub on the carriage front: green ring housing, black face with 4 screws, chrome boss
HX, HY = 105, 532
d.cyl("hub-ring", [HX, HY, 120], [HX, HY, 150], 114, "teal")
d.cyl("hub-face", [HX, HY, 149], [HX, HY, 158], 100, "black")
d.decal("hub-screw", [HX, HY + 38, 158.6], [6, 6], "chrome", face="front", soft=True,
        copies=[[0, -76, 0], [38, -38, 0], [-38, -38, 0]])
d.cyl("hub-boss", [HX, HY, 157], [HX, HY, 172], 48, "chrome")
# thin chrome pin to the left of the hub (photo: white rod to the carriage's left edge)
d.cyl("hub-pin", [HX - 20, HY - 8, 166], [4, HY - 10, 166], 10, "chrome")
# --- crank: flat chrome bar from the hub down and slightly right, green slotted sleeve, knurled collar + grip
A = [HX, HY, 177]
B = [160, 132, 177]
d.bar("crank", A, B, [46, 10], "steel", r=3)
d.cyl("crank-eye", [HX, HY, 172], [HX, HY, 183], 54, "steel")
d.cyl("crank-cap", [HX, HY, 182], [HX, HY, 190], 30, "chrome")
# chrome clamp block across the crank's top end (photo: wider than the bar, a dark slot in it)
d.box("crank-clamp", [HX - 30, HY - 22, 176, HX + 30, HY + 26, 188], "chrome", r=6)
d.box("crank-clamp-slot", [HX - 22, HY + 8, 188, HX + 22, HY + 14, 189], "black", r=2, soft=True)
t0 = 0.63  # sleeve over the lower half of the crank
S0 = [A[0] + (B[0] - A[0]) * t0, A[1] + (B[1] - A[1]) * t0, 179]
d.bar("sleeve", S0, [B[0] + 2, B[1] - 6, 179], [50, 18], "teal", r=4)
ang = math.degrees(math.atan2(B[1] - A[1], B[0] - A[0])) + 90  # tilt of the crank from vertical
mid = [(S0[0] + B[0]) / 2.0, (S0[1] + B[1]) / 2.0, 188.6]
d.decal("sleeve-slot", mid, [12, 110], "plastic#0e3e2f", face="front", soft=True, rot=rot("z", ang, mid))
# handle: black knurled collar then the chrome grip, hanging on below the bottom plate (photo)
G0 = [161, 130, 180]
G1 = [165, 95, 207]
G2 = [170, 40, 252]
d.cyl("grip-collar", [G0[0], G0[1] + 8, G0[2] - 6], G1, 42, "rubber")
d.cyl("grip", G1, G2, 32, "metal#9ea3a8")
d.sphere("grip-end", G2, 30, "metal#6f7478")
d.save()
