"""XY-α-TRON-II low frequency electrotherapy console: white pillow flanks with ribbed grey side panels, a grey centre
tray over the top and front with the screen, two white knobs and the 2 × 6 socket panel."""
from p3lib import *

d = D("xy-alpha-tron-ii", [370, 324, 134], {
    "shell": "gloss#f3f4f6", "tray": "plastic#8d9298", "rib": "plastic#3e434a", "panel": "plastic#dcdfe3",
    "bezel": "gloss#131416", "ui": "gloss#f4f6f8", "teal": "gloss#3cb8c8", "knob": "gloss#eceef0", "frame": "plastic#c4c8cd",
    "yel": "gloss#d9c23a", "blu": "gloss#2e7fd0", "hole": "rubber#151618", "label": "gloss#f7f8f9", "foot": "rubber#1b1c1e",
    "ink": "plastic#5d636b", "panel2": "plastic#5a5f66", "warn": "gloss#f2c230", "pale": "gloss#d6eef1"})
W, D_, Y0, H = 370, 320, 6, 128
d.cyl("foot", [50, 0, 50], [50, Y0 + 2, 50], 30, "foot", copies=[[270, 0, 0], [0, 0, 220], [270, 0, 220]])
# white pillow shell, the grey tray let into it over the top and the front
d.box("flank", [0, Y0, 0, 80, H, D_], "shell", r=26, mirror="x")
d.box("base", [40, Y0, 0, W - 40, Y0 + 30, D_ - 2], "shell", r=14)
d.box("back", [40, Y0, 0, W - 40, H - 6, 40], "shell", r=20)
FZ = D_ - 6
d.box("tray", [64, Y0 + 14, 10, W - 64, H + 2, FZ], "tray", r=24)
# ribbed side panels on both flanks
# (the panel covers almost the whole flat side: black ribbed border ~9, light grey field, 3 lines of print at the front)
d.box("rib", [-1.5, Y0 + 16, 24, 2, H - 16, D_ - 22], "rib", r=18, mirror="x")
d.box("rib-groove", [-2.2, Y0 + 20, 28, 1, H - 20, D_ - 26], "panel2", r=15, mirror="x")
d.box("side-panel", [-2.8, Y0 + 24, 32, 1, H - 24, D_ - 30], "panel", r=12, mirror="x")
d.box("side-text", [-3.3, Y0 + 50, 140, -2, Y0 + 53, 250], "ink", soft=True, mirror="x", copies=[[0, -11, 0], [0, -22, 40]])
d.box("side-logo", [-3.3, Y0 + 62, 220, -2, Y0 + 68, 270], "ink", soft=True, mirror="x")
# screen: black bezel, white welcome UI with a teal wave, two white knobs at its front corners
d.add("screen", "screen", "bezel", box=[80, H - 2, 44, W - 80, H + 4, D_ - 26], r=16, face="top", bezel=16)
# the welcome UI fills the rear ~3/4 of the black glass, the teal wave along its lower edge
d.decal("ui", [W / 2, H + 6, 144], [180, 170], "top", "ui", soft=True)
d.decal("ui-pale", [W / 2, H + 6.1, 214], [180, 30], "top", "pale", soft=True)
d.decal("wave", [W / 2, H + 6.2, 222], [180, 9], "top", "teal", soft=True)
d.decal("ui-title", [W / 2, H + 6.3, 92], [56, 7], "top", "ink", soft=True)
d.decal("ui-sub", [W / 2, H + 6.3, 118], [128, 7], "top", "ink", soft=True)
d.decal("ui-bar", [W / 2 - 12, H + 6.3, 150], [80, 4], "top", "teal", soft=True)
d.decal("ui-bar2", [W / 2 + 28, H + 6.25, 150], [50, 4], "top", "pale", soft=True)
for i, x in enumerate((112, W - 112)):
    d.add(f"knob{i}", "lathe", "knob", at=[x, H + 4, 254], profile=[[0, 0], [23, 0], [23, 4], [22.5, 18], [20, 22], [0, 23]])
    d.add(f"knob{i}-mark", "box", "ink", box=[x - 1.5, H + 26.5, 238, x + 1.5, H + 27.5, 250], soft=True)
d.decal("cn", [W / 2, H + 6.3, 250], [60, 7], "top", "frame", soft=True)
# front socket panel: light frame, 2 rows × 6 sockets (yellow rings over blue rings), 'I / II' label in the middle
d.box("sock-frame", [86, Y0 + 20, FZ - 1, W - 86, Y0 + 96, FZ + 4], "frame", r=8)
d.box("sock-panel", [90, Y0 + 24, FZ + 2, W - 90, Y0 + 92, FZ + 5], "tray", r=6)
# each group of 3 columns in a thin printed frame; the inner column's sockets are smaller
xs = [106, 134, 160, W - 160, W - 134, W - 106]
for k, x in enumerate(xs):
    small = k in (2, 3)
    for row, (y, m) in enumerate(((Y0 + 72, "yel"), (Y0 + 42, "blu"))):
        yy = y
        d.cyl(f"ring{k}{row}", [x, yy, FZ + 4], [x, yy, FZ + 7], 16 if small else 21, m)
        d.cyl(f"hole{k}{row}", [x, yy, FZ + 6], [x, yy, FZ + 8.5], 12 if small else 16.5, "hole", soft=True)
for gx in (94, W - 170):
    d.box(f"grp{gx}", [gx, Y0 + 27, FZ + 5, gx + 76, Y0 + 89, FZ + 5.4], "frame", soft=True)
    d.box(f"grpin{gx}", [gx + 1.2, Y0 + 28.2, FZ + 5.2, gx + 74.8, Y0 + 87.8, FZ + 5.6], "tray", soft=True)
d.box("label", [W / 2 - 14, Y0 + 50, FZ + 4, W / 2 + 14, Y0 + 66, FZ + 6], "label", r=2)
d.box("label-ink", [W / 2 - 9, Y0 + 55, FZ + 5.5, W / 2 + 9, Y0 + 61, FZ + 6.5], "ink", soft=True)
d.box("label-icon", [W / 2 - 3, Y0 + 72, FZ + 4.5, W / 2 + 3, Y0 + 80, FZ + 5.5], "hole", soft=True)
d.slab("warn", "front", poly([(W / 2 - 5, Y0 + 38), (W / 2 + 5, Y0 + 38), (W / 2, Y0 + 46)]), [FZ + 4.5, FZ + 5.5], "warn", soft=True)
d.save()
