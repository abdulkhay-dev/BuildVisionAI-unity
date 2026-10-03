from k4lib import *
# size: printed 30 x 12 x 45 cm; the photo shows the flight running 300 deep and 120 wide -> W 120, D 300
d = K("xy-41", [120, 300, 450], {"pine": "wood#f4d69c", "pine2": "wood#efcf92"})
d.box("board", [0, 0, 0, 120, 450, 20], "pine", r=2)
d.box("base", [0, 0, 20, 120, 20, 300], "pine2", r=2)
for i in range(11):
    d.box(f"step{i}", [0, 20 + 24 * i, 20, 120, 44 + 24 * i, 282 - 23.5 * i], "pine" if i % 2 else "pine2", r=2)
d.slab("side", "side", poly([(20, 20), (282, 20), (282 - 23.5 * 10, 284), (20, 284)]), [117, 121], "pine", r=1)
# white paper label at the top-left corner: model line, grey text rows, a QR square (photo)
d.decal("label", [26, 432, 20.4], [45, 31], "front", "plastic#f4f5f2")
text(d, "label-t", "XY-41", [7, 440, 20.8], 5, "plastic#3a3d44", stroke=0.9)
d.decal("label-lines", [30, 433, 20.8], [34, 1.3], "front", "plastic#9a9ca2", repeat=rep(3, [0, -4.5, 0]))
d.decal("label-qr", [10, 423, 20.8], [7, 7], "front", "plastic#30333a")
d.decal("label-ln2", [32, 422, 20.8], [26, 1.3], "front", "plastic#9a9ca2", copies=[[0, -3.5, 0]])
# oval logo at the top-right: black ring, white face, blue band with white letters
d.sphere("logo", [94, 438, 20], None, "gloss#16181c", radii=[17.5, 10.5, 1.4], soft=True)
d.sphere("logo-in", [94, 438, 20.4], None, "gloss#eef0f4", radii=[15.5, 8.8, 1.4], soft=True)
d.decal("logo-band", [94, 438, 21.9], [27, 5.2], "front", "gloss#2050b0")
text(d, "logo-t", "XY", [89.5, 436.2, 22.2], 3.6, "plastic#ffffff", stroke=0.7)
d.decal("logo-l", [94, 443.6, 21.9], [16, 1], "front", "plastic#8a92a6", copies=[[0, -11.2, 0]])
d.decal("knot", [40, 274, 47.4], [5, 5], "front", "plastic#6b4a2a")
d.save()
