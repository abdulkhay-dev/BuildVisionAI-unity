from p1lib import *
d = D("xy-cryo-1", [500, 595, 1200], {
  "shell": "plastic#e4e5e7", "frame": "plastic#3a3f46", "dark": "plastic#2a2c30", "slot": "plastic#5d636b",
  "black": "rubber#141517", "white": "plastic#f3f4f5", "seam": "plastic#b4b8be"})
# dark under-frame with four arms to castors on short posts
d.box("plinth", [60, 95, 70, 440, 130, 510], "frame", r=12)
for k, (x, z) in enumerate(((40, 45), (460, 45), (40, 550), (460, 550))):
    d.bar(f"arm-{k}", [250, 112, 290], [x, 112, z], [44, 32], "frame", r=8)
    d.cyl(f"post-{k}", [x, 80, z], [x, 128, z], 46, "frame")
    d.caster(f"castor-{k}", [x, 0, z - 6], 75, "rubber#cfd2d6")
# sheet-metal cabinet: rounded vertical edges, seam between front and side panels
d.box("cabinet", [20, 128, 25, 480, 1060, 560], "shell", r=30)
d.box("seam", [478, 135, 528, 481.5, 1052, 531], "seam", mirror="x")
d.box("seam-f", [30, 135, 558, 470, 138, 561], "seam")
# slot vent fields (review: rows of short slots as in the photo): front lower middle, right side lower rear
for r in range(9):
    y = 268 + 30 * r
    d.decal(f"vent-f{r}", [150, y, 560.5], [3.5, 20], "slot", face="front", soft=True, repeat={"n": 24, "step": [8.5, 0, 0]})
    d.decal(f"vent-s{r}", [480.5, y, 140], [3.5, 20], "slot", face="right", soft=True, repeat={"n": 30, "step": [0, 0, 9]})
# hand grip recess on the right side, near the middle at ~700-820
d.box("grip", [476, 700, 290, 482, 820, 410], "plastic#cdd0d4", r=20)
d.box("grip-in", [480, 725, 310, 483, 760, 390], "plastic#a9adb3", r=12)
# dark lid, overhanging at the right rear as the nozzle holder
d.box("lid", [18, 1058, 22, 482, 1072, 562], "dark", r=5)
d.box("holder", [470, 1056, 60, 530, 1072, 170], "dark", r=6)
# white tablet frame with a grey screen, tilted back 38 deg at the front left
# white tablet frame as wide as the cabinet, leaning back ~45 deg, its switched-off screen mid grey (photo)
Q = [250, 1072, 520]
R = rot("x", -45, Q)
d.box("tablet", [25, 1070, 500, 475, 1425, 520], "white", r=26, rot=R)
d.box("screen", [90, 1135, 517, 410, 1385, 521.5], "gloss#6e7277", r=4, rot=R)
# black nozzle standing in the holder; white outlet with a black sleeve on the front upper left
d.cyl("nozzle-sleeve", [500, 1072, 115], [500, 1130, 115], 60, "black")
d.cyl("nozzle", [500, 1130, 115], [500, 1205, 115], 52, "black", d2=34)
d.lathe("outlet", [110, 880, 560], [[0, 0], [52, 0], [52, 30], [46, 34], [0, 34]], "white", axis="z")
d.cyl("sleeve", [110, 880, 590], [110, 880, 640], 80, "black")
# corrugated black hose: down in a big U across the front and up the right side to the nozzle
d.tube("hose", [[110, 880, 638], [80, 872, 664], [-10, 700, 690], [-15, 400, 690], [140, 200, 690], [420, 230, 690],
                [530, 380, 600], [535, 650, 300], [520, 900, 160], [500, 1070, 115]], 60, "black", bend=200,
       rib=4, pitch=14, soft=True)
d.save()
