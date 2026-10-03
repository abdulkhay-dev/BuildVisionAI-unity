from p1lib import *
d = D("xy-k-shock-master-500", [560, 560, 1250], {
  "shell": "plastic#f4f5f6", "side": "plastic#c6c9d0", "black": "plastic#24262a", "bezel": "plastic#3a3f46",
  "line": "gloss#151618", "green": "gloss#7cc243", "dgreen": "gloss#4f8f2a"})
# black base: plinth under the cabinet, four arms to black castor housings, light-grey castors, kick plate
for k, (x, z) in enumerate(((45, 45), (515, 45), (45, 515), (515, 515))):
    d.bar(f"arm-{k}", [280, 108, 280], [x, 108, z], [52, 30], "black", r=8)
    d.cyl(f"housing-{k}", [x, 84, z], [x, 132, z], 58, "black")
    d.caster(f"castor-{k}", [x, 0, z - 6], 75, "rubber#d3d6da")
d.box("plinth", [95, 96, 75, 465, 132, 485], "black", r=8)
# cabinet: grey sides, white front block, black logo cut-out on the right side
d.box("cabinet", [82, 130, 60, 478, 950, 470], "side", r=10)
d.box("front", [80, 130, 452, 480, 950, 500], "shell", r=16)
d.box("kick", [140, 100, 470, 420, 128, 492], "black", r=4)
d.slab("logo", "side", "M 252 600 L 300 600 L 300 715 L 324 715 L 324 745 L 230 745 L 230 715 L 252 715 Z "
       "M 226 730 Q 196 670 248 606 L 248 640 Q 226 680 238 730 Z M 282 745 L 302 745 L 302 778 L 282 772 Z", [477, 480], "line", r=0.5)
# two drawers drawn as thin black outlines with notch handles
dr = ("M 135 655 L 425 655 Q 440 655 440 670 L 440 870 Q 440 885 425 885 L 135 885 Q 120 885 120 870 L 120 670 Q 120 655 135 655 Z "
      "M 128 663 L 128 765 L 432 765 L 432 663 Z M 128 775 L 128 877 L 432 877 L 432 775 Z")
d.slab("drawers", "front", dr, [499, 502], "line", r=0.8)
for i, y in enumerate((877, 765)):
    d.box(f"notch-{i}", [225, y - 24, 498, 335, y - 2, 503], "line", r=3)
    d.box(f"notch-b-{i}", [248, y - 44, 498, 312, y - 22, 503], "line", r=6)
# dark top plate reaching out to the right as the handpiece holder
d.box("top", [80, 950, 60, 480, 962, 500], "black", r=4)
d.box("holder", [470, 950, 290, 552, 962, 450], "black", r=6)
# 12" screen: white rim, thick dark bezel, tilted back 12 deg (print)
Q = [280, 966, 470]
R = rot("x", -12, Q)
d.box("neck", [200, 958, 420, 360, 980, 480], "black", r=6)
d.box("screen-rim", [76, 966, 458, 484, 1252, 474], "shell", r=34, rot=R)
d.screen("screen", [80, 970, 462, 480, 1248, 480], "bezel", r=30, face="front", bezel=3,
         print="med_xy-k-shock-master-500_screen", rot=R)
# two green handpieces hanging in the holder
for i, z in enumerate((410, 335)):
    x = 512
    d.cyl(f"hp-ring-{i}", [x, 940, z], [x, 968, z], 46, "chrome")
    d.box(f"hp-head-{i}", [x - 26, 968, z - 32, x + 26, 1040, z + 30], "green", r=14)
    d.cyl(f"hp-conn-{i}", [x + 20, 1012, z], [x + 52, 1012, z], 20, "shell")
    d.cyl(f"hp-grip-{i}", [x, 850, z], [x, 940, z], 40, "green")
    d.cyl(f"hp-band-{i}", [x, 838, z], [x, 852, z], 38, "chrome")
    d.cyl(f"hp-tip-{i}", [x, 790, z], [x, 838, z], 34, "black")
    d.lathe(f"hp-tip-end-{i}", [x, 778, z], [[0, 0], [14, 0], [17, 12], [0, 12]], "black")
d.save()
