from pfx_lib import *
d = D("xy-cryo-3", [500, 620, 1260], {
  "shell": "plastic#f0f1f3", "frame": "plastic#3a3f46", "grey": "plastic#8d939b", "black": "rubber#141517",
  "hose": "rubber#161719", "bezel": "gloss#111214", "slot": "plastic#5d636b", "logo": "gloss#2f6fbf"})
F = 540   # cabinet front face (z); the hose runs in front of it
# --- chassis plinth and four arms to the castors
d.box("plinth", [50, 80, 50, 450, 128, 500], "frame", r=12)
for i, (x, z) in enumerate(((30, 35), (470, 35), (30, 520), (470, 520))):
    d.bar(f"arm-{i}", [250, 104, 275], [x, 104, z], [44, 30], "frame", r=8)
    d.box(f"cap-{i}", [x - 30, 92, z - 30, x + 30, 124, z + 30], "grey", r=10)
    d.add(f"castor-{i}", "caster", "rubber#9aa0a7", at=[x, 0, z], d=85)
# --- cabinet
d.box("cabinet", [10, 125, 10, 490, 1000, F], "shell", r=40)
# vertical-slot grilles: front lower left, right side lower back half (mirrored to the left side)
d.decal("grille-f", [75, 440, F + 0.6], [6, 22], "front", "slot", soft=True, repeat=rep(12, [16, 0, 0]),
        copies=[[0, -30 * k, 0] for k in range(1, 9)])
d.decal("grille-s", [490.6, 440, 60], [6, 22], "right", "slot", soft=True, repeat=rep(14, [0, 0, 16]),
        copies=[[0, -30 * k, 0] for k in range(1, 9)])
d.decal("grille-s-l", [9.4, 440, 60], [6, 22], "left", "slot", soft=True, repeat=rep(14, [0, 0, 16]),
        copies=[[0, -30 * k, 0] for k in range(1, 9)])
# blue logo: icon + Chinese name + small English line
d.decal("logo-icon", [95, 640, F + 0.6], [30, 40], "front", "logo", soft=True)
d.decal("logo-text", [175, 650, F + 0.6], [115, 26], "front", "logo", soft=True)
d.decal("logo-sub", [175, 625, F + 0.6], [110, 6], "front", "logo", soft=True)
# black hook on the right side near the front, small grey plug at the top of the right side
d.box("hook", [490, 560, 430, 510, 700, 470], "black", r=6)
d.box("hook-arm", [490, 690, 400, 525, 715, 500], "black", r=6)
d.box("plug", [490, 930, 300, 498, 970, 330], "grey", r=4)
# --- deck and the tilted tablet screen with the interface picture
d.box("deck", [12, 998, 12, 488, 1012, F - 2], "frame", r=10)
tilt = rot("x", -28, [250, 1012, F - 8])
d.box("screen-rim", [5, 1012, F - 40, 495, 1305, F - 8], "shell", r=22, rot=tilt)
d.add("screen", "screen", "bezel", box=[9, 1016, F - 12, 491, 1301, F - 4], r=20, face="front", bezel=4,
      print="med_xy-cryo-3_screen", rot=tilt)
d.box("screen-stand", [150, 1000, F - 160, 350, 1080, F - 40], "frame", r=14)
# --- hose outlet and the hose sagging across the front up to the nozzle holder
d.lathe("outlet", [150, 850, F], [[0, 0], [56, 0], [56, 70], [48, 78], [0, 78]], "black", axis="z")
# the photo's hose is smooth matte rubber (not corrugated); its lowest point is ~1/3 of the cabinet height
d.tube("hose", [[150, 850, F + 45], [80, 830, F + 55], [40, 640, 585], [75, 430, 588], [250, 335, 588],
                [430, 410, 585], [455, 650, 585], [455, 900, 585], [455, 1010, 585]],
       60, "hose", bend=170, soft=True)
# nozzle holder plate on the top right and the pistol nozzle
d.box("holder-plate", [380, 995, 470, 500, 1012, 620], "black", r=6)
d.cyl("nozzle-tube", [455, 1012, 585], [455, 1140, 585], 60, "black")
d.cyl("nozzle-head", [455, 1120, 590], [455, 1225, 480], 72, "black", d2=86)
d.lathe("nozzle-mouth", [455, 1225, 480], [[38, 0], [44, 0], [44, 18], [0, 18], [0, 4], [38, 4]], "plastic#2a2c30",
        rot=rot("x", -46, [455, 1225, 480]))
d.save()
