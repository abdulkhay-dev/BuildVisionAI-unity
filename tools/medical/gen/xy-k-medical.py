from p1lib import *
d = D("xy-k-medical", [520, 400, 260], {
  "shell": "plastic#eef0f2", "black": "gloss#111214", "green": "gloss#7cc243", "dgreen": "gloss#4f8f2a",
  "hose": "plastic#d8dbdf", "dot": "plastic#9aa0a8", "rec": "plastic#d3d6da"})
# white wedge body: front leaning back ~9 deg, almost flat top with a shallow raised rear part
d.slab("body", "side", "M 0 0 L 375 0 Q 386 0 384 12 L 346 236 Q 342 252 324 252 L 22 258 Q 0 258 0 236 Z", [0, 400], "shell", r=18)
d.slab("top-rear", "side", "M 20 250 L 190 250 Q 220 251 240 256 L 236 260 L 24 260 Q 18 260 18 254 Z", [30, 370], "shell", r=3)
# black glass front panel with the UI (print)
A = math.degrees(math.atan(38 / 236.0))
zf = lambda y: 384 - (y - 6) * 38 / 236.0
Q = [200, 122, zf(122)]
d.screen("panel", [12, 14, Q[2] - 3, 388, 238, Q[2] + 2], "shell", r=14, face="front", bezel=1,
         print="med_xy-k-medical_screen", rot=rot("x", -A, Q))
# the crop's bottom-left corner is the catalogue's green background: cover it with the white body (review)
d.slab("crop-mask", "front", "M 8 8 L 248 8 L 226 19.5 L 120 28 L 8 38 Z", [Q[2] + 3.7, Q[2] + 4.7], "shell", r=0.5, rot=rot("x", -A, Q))
# right side: round speaker grille, handpiece recess low at the front
dots = []
for i in range(-6, 7):
    for j in range(-6, 7):
        if i * i + j * j <= 36 and (i, j) != (-6, 0):
            dots.append([0, 9 * i, 9 * j])
d.box("speaker", [399.5, 175 - 1.8 + 9 * -6, 110 - 1.8, 401.5, 175 + 1.8 + 9 * -6, 110 + 1.8], "dot", copies=[[0, c[1] + 54, c[2]] for c in dots])
d.box("recess", [398, 28, 190, 402, 132, 352], "rec", r=10)
# green handpiece: vertical grip outside the right side, barrel to the right with a ribbed tip, grey hose
G = [430, 0, 300]
d.loft("grip", [sec(58, 52, 58, 25, 430, 320), sec(150, 62, 70, 30, 432, 318), sec(196, 60, 72, 29, 432, 316)], "green", dome="end", domeH=22)
d.cyl("barrel", [456, 180, 316], [490, 180, 316], 44, "green", d2=36)
d.cyl("barrel-2", [490, 180, 316], [502, 180, 316], 34, "dgreen")
d.cyl("tip-rib", [502, 180, 316], [506, 180, 316], 42, "dgreen", repeat={"n": 3, "step": [6, 0, 0]})
d.lathe("tip", [518, 180, 316], [[0, 0], [16, 0], [14, 4], [0, 5]], "black", axis="x")
d.cyl("grip-end", [430, 38, 320], [430, 62, 320], 32, "dgreen")
d.tube("hose", [[430, 40, 320], [430, 12, 310], [426, 8, 200], [410, 14, 80], [395, 40, 30]], 14, "hose", bend=40, soft=True)
d.save()
