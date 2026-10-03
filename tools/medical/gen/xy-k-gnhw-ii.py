# review 2026-10-02: broad flat grey star base, taller lower body (top ~1255) with the S logo / speaker / sockets on
# its BACK face (photo 2 is taken from the back-left: the lamp's fan faces the camera), bigger lamp drum (~290),
# wider upper column, chrome loop on the yoke plate, "Sunnyou" lettering on the yoke plate and the body foot
from p1lib import *
d = D("xy-k-gnhw-ii", [650, 800, 1650], {
  "shell": "plastic#f1f2f4", "grey": "plastic#8a8f96", "chan": "plastic#9a9fa6", "dark": "plastic#3f444b",
  "blue": "gloss#2f86d6", "lens": "gloss#2b6fd0", "red": "gloss#c8262a"})
H = (325, 200)
tips = [(70, 650), (580, 650), (115, 35), (535, 35)]
order = [tips[0], tips[2], tips[3], tips[1]]   # round the hub: front-left, back-left, back-right, front-right
pts = []
for (tx, tz) in order:
    dx, dz = tx - H[0], tz - H[1]; L = math.hypot(dx, dz); ux, uz = dx / L, dz / L; vx, vz = -uz, ux
    wr, wt = 70, 42
    pts += [(H[0] + ux * 90 - vx * wr, H[1] + uz * 90 - vz * wr), (tx - vx * wt, tz - vz * wt), (tx + ux * 34, tz + uz * 34),
            (tx + vx * wt, tz + vz * wt), (H[0] + ux * 90 + vx * wr, H[1] + uz * 90 + vz * wr)]
d.slab("base", "top", rpoly(pts, 34), [95, 145], "grey", r=16)
for k, (x, z) in enumerate(tips):
    d.caster(f"castor-{k}", [x, 0, z], 75, "rubber#e6e8eb")
d.box("pedal", [292, 60, 40, 358, 105, 92], "dark", r=8)
# lower body: white column, grey J channel on its front, dark sloped top with a small display
d.box("body", [220, 135, 100, 430, 1240, 290], "shell", r=45)
d.box("channel", [258, 360, 287, 392, 1180, 294], "chan", r=50)
d.box("rail", [292, 420, 293, 297, 780, 295.5], "shell", copies=[[41, 0, 0]])
d.slab("top", "side", "M 108 1225 L 282 1225 L 282 1240 L 108 1262 Z", [228, 422], "dark", r=6)
d.box("display", [285, 1252, 140, 365, 1256, 185], "gloss#141a22", r=3, rot=rot("x", 7, [325, 1252, 160]))
# chrome bar handle on the left side
d.cyl("handle-l", [188, 830, 200], [188, 1140, 200], 15, "chrome")
d.cyl("handle-l-a", [188, 830, 200], [222, 830, 200], 13, "chrome", copies=[[0, 310, 0]])
# back face: blue S logo, blue speaker dot field, two sockets low
d.cyl("logo", [325, 1130, 100], [325, 1130, 98.5], 46, "blue")
d.cyl("logo-in", [325, 1130, 98.4], [325, 1130, 97.6], 30, "shell")
d.add("logo-s", "decal", "blue", at=[325, 1130, 97.4], size=[34, 9], face="back", soft=True, rot=rot("z", 40, [325, 1130, 97.4]))
d.add("dots", "decal", "blue", at=[289, 600, 99.4], size=[5, 5], face="back", soft=True,
      copies=[[12 * i, -14 * j, 0] for i in range(7) for j in range(8) if i + j > 0])
d.box("socket", [308, 400, 97, 342, 430, 101], "dark", r=3, copies=[[0, -62, 0]])
d.decal("foot-text", [325, 300, 294.5], [60, 8], "plastic#c2c6cc", face="front", soft=True)
# upper column sliding in front of the body, curving forward into the boom
d.box("column", [250, 790, 290, 400, 1520, 400], "shell", r=34)
d.slab("boom", "side", "M 290 1450 L 290 1550 Q 290 1650 390 1650 L 682 1650 Q 702 1650 702 1630 L 702 1576 "
       "Q 702 1557 683 1557 L 425 1557 Q 400 1557 400 1532 L 400 1490 Z", [250, 400], "shell", r=25)
d.cyl("handle-f", [325, 960, 448], [325, 1180, 448], 16, "chrome")
d.cyl("handle-f-a", [325, 960, 398], [325, 960, 448], 13, "chrome", copies=[[0, 220, 0]])
# yoke: crossbar under the boom end, flat side plates around the drum, grey pivots, chrome loop on the left plate
Lz, Ly = 440, 1350
d.box("yoke-bar", [150, 1530, 500, 500, 1558, 650], "shell", r=10)
d.slab("yoke-plate", "side", "M 530 1290 L 620 1290 Q 660 1290 660 1330 L 660 1545 L 490 1545 L 490 1330 Q 490 1290 530 1290 Z",
       [158, 176], "shell", r=8, mirror="x")
d.cyl("pivot", [140, Ly, 575], [158, Ly, 575], 42, "chan", mirror="x")
d.tube("plate-loop", [[156, 1500, 515], [128, 1500, 515], [128, 1360, 515], [156, 1360, 515]], 11, "chrome", bend=14)
d.decal("plate-txt", [474.6, 1410, 575], [80, 10], "plastic#9aa0a8", face="right", soft=True)
# lamp drum along the boom: back fan grille with a red ring, front grey vented ring and blue lens, distance rod
R0 = 145
d.lathe("lamp", [325, Ly, Lz], [[0, 0], [100, 0], [132, 8], [R0, 24], [R0, 240], [140, 254], [130, 260]], "shell", axis="z")
d.lathe("fan", [325, Ly, Lz - 4], [[0, 0], [108, 0], [108, 6], [0, 6]], "dark", axis="z")
d.lathe("fan-ring", [325, Ly, Lz - 6], [[104, 0], [114, 0], [114, 4], [104, 4], [104, 0]], "red", axis="z", caps=False)
d.lathe("vent-ring", [325, Ly, Lz + 256], [[88, 0], [124, 0], [124, 8], [88, 8], [88, 0]], "dark", axis="z", caps=False)
for k in range(12):
    a = math.radians(30 * k + 15)
    c, s = math.cos(a), math.sin(a)
    d.bar(f"vent-{k}", [325 + 95 * c, Ly + 95 * s, Lz + 265], [325 + 118 * c, Ly + 118 * s, Lz + 265], [6, 2], "plastic#c9cdd2", r=1)
d.lathe("lens", [325, Ly, Lz + 252], [[0, 0], [88, 0], [88, 10], [72, 14], [0, 15]], "lens", axis="z")
d.cyl("rod", [395, Ly - 105, Lz + 262], [395, Ly - 105, 785], 7, "chrome")
d.sphere("rod-tip", [395, Ly - 105, 788], 16, "chrome")
d.save()
