from pfx_lib import *
import math
# body (cart) on the left x 0..560; the two electrode arms reach right to x ~1040 and up to ~1440
d = D("xy-k-cdb-ii", [1050, 600, 1450], {
  "shell": "gloss#f4f5f7", "grey": "plastic#8a9099", "tray": "plastic#9097a0", "hub": "plastic#2e3238",
  "black": "gloss#121315", "acryl": "acrylic#e4ecf06a", "cable": "plastic#c4c8cd", "bolt": "metal#9aa0a8",
  "slit": "plastic#8d939b", "tyre": "rubber#9aa0a7"})
CX, CZ = 280, 300
# --- white X base: four flat arms to the corners, grey caps over the castor ends, big castors
d.box("base-hub", [150, 120, 170, 410, 165, 430], "shell", r=20)
for i, (x, z) in enumerate(((55, 55), (505, 55), (55, 545), (505, 545))):
    d.bar(f"base-arm{i}", [CX, 140, CZ], [x, 140, z], [75, 40], "shell", r=14)
    d.box(f"cap{i}", [x - 42, 128, z - 42, x + 42, 172, z + 42], "grey", r=14)
    d.box(f"fork{i}", [x - 28, 70, z - 30, x + 28, 130, z + 30], "shell", r=10)
    d.add(f"castor{i}", "caster", "tyre", at=[x, 0, z], d=120)
# --- column with the grey band, louvres, grilles, switch and socket
d.box("column", [100, 160, 135, 460, 925, 465], "shell", r=16)
d.box("band", [97, 480, 132, 463, 510, 468], "grey", r=6)
for nm, xf, s in (("l", 99, 1), ("r", 461, -1)):
    d.box(f"louvre-up-{nm}", [xf - 1.5, 850, 160, xf + 1.5, 856, 190], "slit", soft=True,
          rot=rot("x", 40, [xf, 853, 175]), repeat=rep(14, [0, -22, 0]))
    d.box(f"louvre-lo-{nm}", [xf - 1.5, 440, 405, xf + 1.5, 446, 435], "slit", soft=True,
          rot=rot("x", 40, [xf, 443, 420]), repeat=rep(8, [0, -22, 0]))
    d.slab(f"grille-{nm}", "side", "M 160 185 L 230 185 L 230 260 L 160 260 Z " + " ".join(
        f"M {166 + 9 * i} {191 + 9 * j} L {171 + 9 * i} {191 + 9 * j} L {171 + 9 * i} {196 + 9 * j} L {166 + 9 * i} {196 + 9 * j} Z"
        for i in range(7) for j in range(7)), [xf - 1.5, xf + 1.5] if s > 0 else [xf - 1.5, xf + 1.5], "plastic#c3c7cc")
d.box("switch", [96, 850, 400, 101, 895, 430], "black", r=3)
d.box("switch-rocker", [94, 858, 404, 98, 888, 426], "gloss#2e9a4a", r=3)
d.box("socket", [96, 400, 180, 101, 460, 225], "black", r=4)
d.box("socket-in", [94, 410, 188, 97, 450, 217], "plastic#4a4e55", r=3)
d.decal("front-slot", [240, 230, 465.5], [26, 5], "front", "slit", soft=True, repeat=rep(3, [36, 0, 0]))
d.decal("front-slot2", [258, 215, 465.5], [26, 5], "front", "slit", soft=True, repeat=rep(3, [36, 0, 0]))
# --- grey tray around the column top: wider plate, raised front handle bar, holes, cable hook under the right end
d.box("tray", [15, 900, 100, 545, 935, 515], "tray", r=14)
d.bar("tray-handle", [20, 950, 498], [540, 950, 498], [36, 34], "tray", r=14)
d.box("tray-handle-post", [20, 930, 480, 60, 950, 515], "tray", r=8, copies=[[480, 0, 0]])
d.decal("tray-hole", [40, 935.5, 220], [10, 10], "top", "plastic#3a3f45", soft=True, repeat=rep(3, [0, 0, 45]))
d.bar("cable-hook", [470, 860, 420], [560, 860, 420], [26, 20], "tray", r=8)
d.box("cable-hook-tip", [550, 860, 405, 566, 885, 435], "tray", r=6)
d.box("neck", [110, 935, 140, 450, 965, 455], "shell", r=10)
# --- head box: front face tilted back ~12 deg, black glass screen with the interface picture
# head measured on both photos: ~420 wide (only a little wider than the column) and ~445 deep
d.slab("head", "side", "M 30 960 L 475 960 L 430 1190 L 60 1190 Q 30 1190 30 1160 Z", [70, 490], "shell", r=32)
tilt = rot("x", -11.1, [280, 960, 475])
d.add("screen", "screen", "black", box=[80, 972, 465, 480, 1182, 479], r=14, face="front", bezel=4,
      print="med_xy-k-cdb-ii_screen", rot=tilt)
# --- arms: grey bracket on the tray end, black hubs, translucent acrylic plates, double knuckle, electrodes
d.box("arm-bracket", [530, 905, 330, 640, 950, 470], "tray", r=12)
def hub(nm, p, dd=72, L=66):
    d.cyl(nm, [p[0], p[1], p[2] - L / 2], [p[0], p[1], p[2] + L / 2], dd, "hub")
    d.cyl(nm + "-cap", [p[0], p[1], p[2] + L / 2], [p[0], p[1], p[2] + L / 2 + 3], dd * 0.55, "bolt", soft=True)
def plate(nm, a, b):
    d.bar(nm, a, b, [16, 62], "acryl", r=6)
    for t in (0.33, 0.66):
        q = [a[i] + (b[i] - a[i]) * t for i in range(3)]
        d.cyl(f"{nm}-bolt{int(t * 100)}", [q[0], q[1], q[2] - 12], [q[0], q[1], q[2] + 12], 16, "bolt", soft=True)
def arm(nm, h0, h1, kn, el, tilt_deg):
    hub(f"{nm}-hub0", h0)
    hub(f"{nm}-hub1", h1)
    plate(f"{nm}-plate0", h0, h1)
    plate(f"{nm}-plate1", h1, kn)
    hub(f"{nm}-knuckle", kn, 66, 72)
    d.cyl(f"{nm}-knuckle2", [kn[0] - 36, kn[1] - 70, kn[2]], [kn[0] + 36, kn[1] - 70, kn[2]], 62, "hub")
    d.cyl(f"{nm}-stem", [kn[0], kn[1] - 30, kn[2]], [el[0], el[1] + 50, el[2]], 34, "hub")
    t = rot("z", tilt_deg, el)
    d.lathe(f"{nm}-disc", el, [[0, 0], [100, 0], [100, 30], [94, 36], [0, 36]], "plastic#f6f7f8", rot=t)
    d.lathe(f"{nm}-rim", [el[0], el[1] - 1, el[2]], [[0, 0], [101, 0], [101, 6], [0, 6]], "plastic#b9bec5", rot=t)
    d.lathe(f"{nm}-cap", [el[0], el[1] + 36, el[2]], [[0, 0], [64, 0], [60, 24], [42, 44], [0, 50]], "black", rot=t)
arm("up", [575, 985, 440], [720, 1225, 440], [800, 1405, 440], [905, 1260, 440], 30)
arm("lo", [650, 978, 380], [860, 1015, 380], [930, 1195, 380], [945, 1075, 380], 15)
# light-grey cables from the electrode knuckles arcing high and down to the hook under the tray
d.tube("cable-up", [[800, 1440, 440], [760, 1448, 430], [620, 1350, 420], [560, 1150, 420], [545, 890, 420]],
       14, "cable", bend=160, soft=True)
d.tube("cable-lo", [[930, 1230, 380], [880, 1300, 380], [740, 1260, 400], [620, 1080, 410], [560, 890, 425]],
       14, "cable", bend=160, soft=True)
d.save()
