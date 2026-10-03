from pfx_lib import *
# console (head) at the back z~0, the walking end (tail) at the front z = 1965 where the user steps on, facing the console
d = D("xyj-j9", [800, 1965, 1278], {
  "bronze": "metal#6e6359", "black": "plastic#26272a", "belt": "rubber#232426", "foam": "rubber#2b2c2f",
  "chrome": "metal#cfc8bd", "red": "gloss#d8261f", "panel": "plastic#33363b", "txt": "plastic#9a9ea6"})
# --- deck: bronze side members, black foot rails, belt with the script, black tail cap and rear feet
d.box("side-member", [62, 45, 300, 112, 170, 1900], "bronze", r=10, mirror="x")
d.box("deck-board", [112, 140, 300, 688, 168, 1910], "black", r=4)
d.box("belt", [152, 168, 320, 648, 182, 1915], "belt", r=6)
d.box("foot-rail", [88, 168, 420, 152, 198, 1905], "black", r=10, mirror="x")
d.decal("belt-script", [190, 182.6, 1060], [14, 18], "top", "plastic#d9d9d9", soft=True, repeat=rep(24, [0, 0, 24]))
d.box("tail-cap", [66, 50, 1885, 734, 180, 1962], "black", r=30)
d.box("tail-roller", [152, 150, 1905, 648, 184, 1935], "plastic#3a3c40", r=14)
d.add("tail-wheel", "wheel", "rubber#1d1e20", at=[95, 32, 1920], d=64, d2=26, axis="x", mirror="x")
# --- motor hood at the console end, round logo
d.loft("hood", [sec(140, 610, 400, 40, 400, 250), sec(270, 600, 380, 70, 400, 245), sec(330, 540, 300, 80, 400, 250)], "black")
d.box("hood-front", [150, 60, 50, 650, 230, 140], "black", r=30)
d.decal("hood-logo", [400, 330.6, 300], [50, 50], "top", "plastic#8a8d93", soft=True)
# --- front base: bronze cross tube with transport wheels; side links to the deck
d.box("base-cross", [40, 20, 40, 760, 80, 110], "bronze", r=14)
d.box("base-link", [50, 30, 100, 110, 110, 330], "bronze", r=10, mirror="x")
d.add("front-wheel", "wheel", "rubber#1d1e20", at=[28, 45, 75], d=80, d2=26, axis="x", mirror="x")
# --- uprights: oval bronze profiles leaning toward the console end, curving back under the console
up = [[100, 175, 300], [100, 450, 170], [100, 760, 120], [100, 980, 140], [100, 1130, 230]]
d.sweep("upright", up, [48, 88], "bronze", shape="oval", bend=260, mirror="x")
d.box("upright-boot", [70, 150, 250, 130, 250, 370], "black", r=16, mirror="x")
d.cyl("upright-cross", [100, 990, 150], [700, 990, 150], 60, "bronze")
d.lathe("upright-knob", [76, 1050, 185], [[0, 0], [10, 0], [10, 6], [0, 7]], "black", axis="x",
        rot=rot("y", 180, [76, 1050, 185]), copies=[[0, -40, -5]], mirror="x")
# --- console: wide black tray with wings sloping toward the user (side profile extruded across x)
tray = "M 90 1125 Q 100 1190 150 1190 L 470 1098 Q 492 1090 486 1070 L 470 1052 L 150 1100 Z"
d.slab("console", "side", tray, [25, 775], "black", r=16)
S = (1098 - 1190) / (470 - 150)          # slope of the tray top (y per z)
def on_tray(z): return 1190 + (z - 150) * S
for nm, x0, x1 in (("l", 50, 245), ("r", 555, 750)):
    d.slab(f"wing-panel-{nm}", "side", f"M 190 {on_tray(190) + 1} L 430 {on_tray(430) + 1} L 430 {on_tray(430) + 3} "
           f"L 190 {on_tray(190) + 3} Z", [x0, x1], "panel", soft=True)
    d.slab(f"wing-text-{nm}", "side", f"M 205 {on_tray(205) + 3} L 211 {on_tray(211) + 3} L 211 {on_tray(211) + 4} "
           f"L 205 {on_tray(205) + 4} Z", [x0 + 20, x1 - 20], "txt", soft=True,
           repeat=rep(10, [0, 22 * S, 22]))
    xb = 120 if nm == "l" else 620
    d.sphere(f"btn-{nm}", [xb, on_tray(440) + 4, 440], None, "plastic#8d9198", radii=[26, 10, 18], copies=[[60, 0, 0]])
d.box("safety-key", [380, on_tray(445) - 4, 430, 420, on_tray(445) + 18, 470], "red", r=6)
d.box("key-row", [270, on_tray(380) + 1, 300, 530, on_tray(380) + 3, 420], "panel", soft=True)
d.decal("keys", [290, on_tray(360) + 3.5, 360], [24, 14], "top", "plastic#5b5f66", soft=True, repeat=rep(9, [27, 0, 0]))
# raised display pod tilted toward the user
pod = rot("x", -32, [400, 1150, 210])
d.box("pod", [250, 1120, 150, 550, 1300, 210], "black", r=16, rot=pod)
d.add("display", "screen", "panel", box=[262, 1140, 206, 538, 1290, 212], r=8, face="front", bezel=8, rot=pod)
d.decal("led", [305, 1268, 212.6], [72, 16], "front", "red", soft=True, rot=pod, repeat=rep(3, [95, 0, 0]))
d.decal("track", [400, 1215, 212.6], [80, 34], "front", "plastic#4f6f8f", soft=True, rot=pod)
d.decal("pod-keys", [300, 1170, 212.6], [18, 8], "front", "plastic#7a7f88", soft=True, rot=pod, repeat=rep(9, [25, 0, 0]))
# --- front handlebars: big black foam loops from the console sides toward the user and down to the uprights
# photo: the loops are tall D shapes (~400 high): the top runs from the wing toward the user, the front bend drops to
# ~680 and the bottom part rises back to the upright just under the console
hb = [[75, 1085, 330], [28, 1060, 500], [20, 960, 660], [30, 760, 680], [70, 700, 520], [95, 800, 300], [100, 880, 150]]
d.sweep("handlebar", hb, [44, 36], "foam", shape="oval", bend=110, mirror="x")
# --- side parallel handrails
for nm, z in (("a", 1000), ("b", 1720)):
    d.box(f"post-{nm}", [30, 45, z - 30, 82, 870, z + 30], "bronze", r=6, mirror="x")
    d.box(f"post-in-{nm}", [35, 860, z - 24, 77, 975, z + 24], "chrome", r=4, mirror="x")
    d.box(f"post-collar-{nm}", [26, 850, z - 34, 86, 876, z + 34], "bronze", r=6, mirror="x")
    d.lathe(f"lock-knob-{nm}", [30, 810, z], [[0, 0], [12, 0], [12, 8], [30, 10], [30, 26], [0, 28]], "black", axis="x",
            rot=rot("y", 180, [30, 810, z]), mirror="x")
    d.decal(f"knob-label-{nm}", [1.5, 810, z], [36, 36], "left", "plastic#6f7278", soft=True)
    d.decal(f"post-screw-{nm}", [56, 70, z + 30.6], [8, 8], "front", "black", soft=True, copies=[[0, 50, 0]], mirror="x")
d.cyl("rail", [56, 1000, 960], [56, 1000, 1760], 40, "chrome", mirror="x")
d.sweep("j-hook", [[56, 1000, 1750], [56, 1000, 1885], [50, 900, 1950], [45, 560, 1950]], [44, 44], "foam",
        shape="round", bend=110, mirror="x")
# --- AMERICAN MOTION decal on the near side frame (x = 800 side faces right, front = tail); put it on the right side
d.decal("am-logo", [800 - 61.5, 105, 1300], [30, 26], "right", "gloss#d8401f", soft=True)
d.decal("am-text", [800 - 61.5, 105, 1420], [180, 18], "right", "plastic#2a2a2a", soft=True)
d.save()
