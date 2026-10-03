"""XY-MSZ-I smart OT (sanding) table. x = the long axis (the patient sits at the +x end), front = the long edge the
photo looks at. White top with a 3-stripe black edge, a recessed light-blue glass window, a silver carriage across the
window with the handle and forearm cradle, round blue/chrome buttons, an all-in-one PC at the back, two white lift legs
on T feet."""
from k9lib import *
d = K("xy-msz-i", [1200, 800, 1300], {
    "white": "plastic#f3f4f5", "black": "plastic#1e1f22", "blue": "gloss#2f86d0", "glass": "gloss#7cc4ec",
    "alu": "metal#c9ccd1", "chrome": "chrome", "leg": "plastic#eef0f1", "strap": "fabric#1f55b5", "dark": "black#16171a"})
W, D = 1200, 800
TY = 800                                     # top surface
WX0, WX1, WZ0, WZ1 = 300, 1110, 270, 690      # window
top_ol = rpoly([(0, 0), (W, 0), (W, D), (0, D)], 40)
win = f"M {WX0} {WZ0} V {WZ1} H {WX1} V {WZ0} Z"
# edge stripes (black / white layers), the white top with the window hole
lay = [(TY - 58, TY - 46, "black"), (TY - 46, TY - 41, "white"), (TY - 41, TY - 29, "black"), (TY - 29, TY - 24, "white"), (TY - 24, TY - 12, "black")]
for k, (a, b, m) in enumerate(lay):
    d.slab(f"edge-{k}", "top", top_ol, [a, b], m, r=2)
d.slab("top", "top", top_ol + " " + win, [TY - 12, TY], "white", r=3)
d.box("win-well", [WX0 - 2, TY - 40, WZ0 - 2, WX1 + 2, TY - 12, WZ1 + 2], "white", r=2)
d.box("win-glass", [WX0 + 2, TY - 16, WZ0 + 2, WX1 - 2, TY - 10, WZ1 - 2], "glass", r=2)
# thin dark slot lines along the window's long edges (rails)
d.decal("rail-f", [(WX0 + WX1) / 2, TY + 0.6, WZ1 + 18], [WX1 - WX0 + 60, 4], "top", "dark")
d.decal("rail-b", [(WX0 + WX1) / 2, TY + 0.6, WZ0 - 18], [WX1 - WX0 + 60, 4], "top", "dark")
# carriage: a silver beam across the window, its front end rounded down onto the rail
CXg = 720
d.sweep("carriage", [[CXg, TY + 30, WZ0 - 30], [CXg, TY + 30, WZ1 - 20], [CXg, TY + 20, WZ1 + 15], [CXg, TY, WZ1 + 28]],
        [80, 60], "alu", shape="rect", r=16, bend=40)
d.lathe("cbtn", [CXg, TY + 60, WZ1 - 60], [[0, 0], [28, 0], [28, 8], [24, 12], [0, 13]], "blue")
d.lathe("cbtn-top", [CXg, TY + 72, WZ1 - 60], [[0, 0], [22, 0], [20, 3], [0, 4]], "chrome")
# handle block on the carriage, vertical blue/black handle, forearm cradle towards the patient (+x) with blue straps
HZ = 470
d.box("hblock", [CXg - 60, TY + 55, HZ - 40, CXg + 60, TY + 85, HZ + 40], "alu", r=8)
d.cyl("handle", [CXg, TY + 85, HZ], [CXg, TY + 165, HZ], 42, "blue")
d.cyl("handle-top", [CXg, TY + 165, HZ], [CXg, TY + 215, HZ], 40, "black")
d.sphere("handle-cap", [CXg, TY + 215, HZ], 40, "black")
d.box("cradle", [CXg + 40, TY + 75, HZ - 55, CXg + 320, TY + 90, HZ + 55], "alu", r=6)
d.box("cradle-wall", [CXg + 120, TY + 85, HZ - 60, CXg + 320, TY + 140, HZ - 50], "alu", r=4, copies=[[0, 0, 110]])
for k, x in enumerate((CXg + 150, CXg + 260)):
    d.strap(f"strap-{k}", [[x, TY + 140, HZ - 58], [x, TY + 200, HZ - 30], [x, TY + 205, HZ + 30], [x, TY + 140, HZ + 58]],
            [38, 6], "strap", bend=40)
d.decal("cradle-logo", [CXg + 230, TY + 82, HZ + 55.6], [60, 12], "front", "blue")
# round push buttons: blue ring + chrome top
BTN = [(85, 720), (85, 630), (85, 540), (85, 450), (85, 360), (85, 270), (185, 730), (640, 745), (690, 105),
       (1010, 95), (1160, 300)]
for k, (x, z) in enumerate(BTN):
    d.lathe(f"btn-{k}", [x, TY, z], [[0, 0], [29, 0], [29, 9], [25, 13], [0, 14]], "blue")
    d.lathe(f"btn-top-{k}", [x, TY + 13, z], [[0, 0], [23, 0], [21, 3], [0, 4]], "chrome")
# all-in-one PC at the back, on a flat silver foot
MX = 420
d.box("pc-foot", [MX - 140, TY, 60, MX + 140, TY + 8, 230], "alu", r=6)
d.bar("pc-neck", [MX, TY + 8, 100], [MX, TY + 120, 140], [160, 14], "alu", r=4)
PR = rot("x", -12, [MX, TY + 45, 170])
# (review 2026-10-03) the leaflet crop was skewed: now straightened (reference/<id>_screen.jpg + albedo, 1280 x 720,
# the UI only) and laid over the whole picture area; thin black bezel, white chin
d.box("pc", [MX - 290, TY + 42, 150, MX + 290, TY + 447, 185], "black", r=10, rot=PR)
d.box("pc-chin", [MX - 290, TY + 42, 183, MX + 290, TY + 112, 192], "white", r=6, rot=PR)
d.box("pc-grille", [MX - 250, TY + 66, 191.6, MX + 250, TY + 86, 192.6], "plastic#dfe1e3", r=0.3, soft=True, rot=PR)
d.screen("pc-screen", [MX - 265, TY + 122, 184, MX + 265, TY + 420, 187.5], "black", print="med_xy-msz-i_screen", bezel=0.2, r=1, rot=PR)
# lift legs: white columns with a black motor housing under the top, T feet with black end caps
for k, x in enumerate((330, 900)):
    d.box(f"leg-head-{k}", [x - 70, 700, 330, x + 70, 762, 470], "black", r=8)
    d.box(f"leg-{k}", [x - 45, 50, 340, x + 45, 700, 460], "leg", r=8)
    d.box(f"foot-{k}", [x - 38, 12, 60, x + 38, 62, 740], "leg", r=8)
    d.box(f"foot-cap-a-{k}", [x - 40, 0, 40, x + 40, 64, 85], "black", r=10)
    d.box(f"foot-cap-b-{k}", [x - 40, 0, 715, x + 40, 64, 760], "black", r=10)
d.save()
