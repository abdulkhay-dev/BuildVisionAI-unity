from p1lib import *
d = D("xy-k-zwx-ii", [273, 202, 92], {
  "shell": "gloss#f2f3f5", "base": "plastic#3a3f46", "panel": "plastic#b4bbc4", "band": "plastic#8d959e",
  "blue": "gloss#2a62c9", "dark": "gloss#141516", "metal": "metal#c0c4c8"})
# graphite bottom tray and the white glossy upper shell, top sloping down to the front
d.box("base", [0, 0, 0, 273, 30, 202], "base", r=12)
d.slab("shell", "side", "M 3 26 L 199 26 L 199 76 Q 199 81 193 82 L 13 91 Q 3 91.5 3 84 Z", [2, 271], "shell", r=10)
def yt(z): return 91 - (z - 13) * 9 / 180.0
A = math.degrees(math.atan(9 / 180.0))
Q = [136, yt(103), 103]
R = rot("x", A, Q)
# label panel, raised title band with a step at its right end, rocker switch
d.box("panel", [12, yt(103) - 1.5, 16, 261, yt(103) + 0.6, 190], "panel", r=6, rot=R)
d.box("band", [12, yt(103) - 1, 16, 188, yt(103) + 3, 56], "band", r=4, rot=R)
d.box("band-r", [182, yt(103) - 1, 16, 261, yt(103) + 3, 44], "band", r=4, rot=R)
d.box("switch", [222, yt(30) + 2, 22, 248, yt(30) + 9, 40], "dark", r=2)
d.box("logo", [42, yt(36) + 3, 32, 66, yt(36) + 3.6, 40], "plastic#e8eaee", r=1)
# display window with the red LED digits, 3 indicator LEDs
d.box("window", [38, yt(92) - 0.5, 70, 214, yt(92) + 1.2, 116], "plastic#cfd3d8", r=6, rot=R)
d.box("led", [54, yt(92) + 1, 80, 108, yt(92) + 3, 106], "dark", r=2)
text(d, "led-digits", "888", [62, yt(92) + 3.2, 100], 16, "gloss#e0301e", face="top", stroke=2.2, gap=0.3)
for i, x in enumerate((152, 182, 208)):
    d.sphere(f"lamp-{i}", [x, yt(84) + 1, 84], 8, "gloss#e9ecef")
# four round buttons: blue + / - / treat, grey surface/cavity; yellow warning mark
for i, (x, m) in enumerate(((68, "blue"), (102, "blue"), (148, "blue"), (205, "gloss#34373c"))):
    d.lathe(f"key-{i}", [x, yt(152) - 0.5, 152], [[0, 0], [13, 0], [13, 4], [11, 6.5], [0, 6.5]], m)
d.lathe("key-3-ring", [205, yt(152) - 0.4, 152], [[13, 0], [15.5, 0], [15.5, 2.5], [13, 2.5]], "plastic#8c9299")
text(d, "plus", "+", [64.4, yt(152) + 6.6, 158], 12, "gloss#ffffff", face="top", stroke=2.6)
text(d, "minus", "-", [98.4, yt(152) + 6.6, 158], 12, "gloss#ffffff", face="top", stroke=2.6)
d.decal("treat-mark", [148, yt(152) + 6.4, 152], [10, 5], "gloss#e8eef8", face="top", soft=True)
# title band: white logo disc + lettering at the left, dark title text in the middle, frame line round display + lamps
d.cyl("logo-disc", [32, yt(36) + 3, 36], [32, yt(36) + 3.6, 36], 13, "plastic#eef0f3")
d.decal("title", [126, yt(40) + 3.4, 40], [62, 9], "plastic#2d3036", face="top", soft=True)
d.decal("title-2", [130, yt(50) + 3.4, 50], [70, 3], "plastic#5a6068", face="top", soft=True)
d.decal("corner-mark", [22, yt(176) + 0.9, 176], [7, 7], "plastic#30343a", face="top", soft=True)
# right side: grey label strip with the two metal sockets
d.decal("side-label", [273.3, 66, 100], [130, 20], "plastic#8f9aa6", face="right", soft=True)
d.decal("warn", [248, yt(150) + 0.8, 150], [9, 8], "gloss#f2c21a", face="top")
# two metal sockets on the right side
for i, z in enumerate((70, 132)):
    d.lathe(f"socket-{i}", [271, 48, z], [[0, 0], [11.5, 0], [11.5, 3], [10, 5], [7, 5], [7, 3], [0, 3]], "metal", axis="x")
    d.cyl(f"socket-in-{i}", [273, 48, z], [275.5, 48, z], 13, "dark")
d.save()
