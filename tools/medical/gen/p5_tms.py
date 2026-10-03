"""Transcranial magnetic + electrical stimulation physiotherapy cabinet (no model code).
Writes only tms-physiotherapy-device.json."""
from p5lib import *
import math

W, DP, H = 500, 450, 1050
CX = W / 2
d = D("tms-physiotherapy-device", [W, DP, H],
      {"body": "plastic#d4d7dc", "panel": "plastic#dfe2e6", "base": "plastic#3a3f46", "blue": "gloss#2f7fd8",
       "key": "gloss#7fb2ea", "wkey": "gloss#f2f3f5", "led": "gloss#1c1e22", "line": "plastic#b4b8be",
       "cable": "rubber#9ea3aa", "red": "gloss#d8322a"})
# graphite plinth with chamfered top on 4 castors
d.add("castor", "caster", "rubber#cfd2d6", at=[42, 0, 42], d=70, copies=[[W - 84, 0, 0], [0, 0, DP - 84], [W - 84, 0, DP - 84]])
d.loft("plinth", [sec(84, 484, 434, 52, CX, DP / 2), sec(150, 488, 438, 54, CX, DP / 2),
                  sec(176, 456, 410, 40, CX, DP / 2)], "base")
# upright cabinet (narrower than the plinth, as in the photo), front recessed panel with two grooves and the logo
ZC = 220
CW, CD = 400, 380
ZF = ZC + CD / 2
d.loft("cabinet", [sec(172, CW, CD, 30, CX, ZC), sec(830, CW, CD, 30, CX, ZC)], "body")
d.box("front-panel", [CX - 180, 236, ZF - 3, CX + 180, 790, ZF + 1.5], "panel", r=14)
d.box("groove", [CX - 176, 588, ZF + 1, CX + 176, 591, ZF + 2], "line", copies=[[0, -162, 0]])
d.decal("logo", [CX - 92, 632, ZF + 1.9], [30, 30], "front", "blue", soft=True)
d.decal("logo-t", [CX - 22, 638, ZF + 1.9], [96, 20], "front", "blue", soft=True)
d.decal("logo-s", [CX - 22, 620, ZF + 1.9], [96, 6], "front", "plastic#6a9ed8", soft=True)
d.decal("side-label", [CX + CW / 2 + 0.4, 430, ZC - 20], [56, 170], "right", "gloss#3a8ee0", soft=True)
d.box("side-groove", [CX + CW / 2 - 3, 200, ZC - CD / 2 + 70, CX + CW / 2 + 1, 800, ZC - CD / 2 + 74], "line")
# head: a taller band, slightly wider than the cabinet (groove/step under it), top panel sloping down to the front
HW, HD = 424, 404
d.loft("head-groove", [sec(822, CW - 8, CD - 8, 26, CX, ZC), sec(834, CW - 8, CD - 8, 26, CX, ZC)], "line")
Z0, Z1, YB, YF = ZC - HD / 2, ZC + HD / 2, 1046, 1000
d.slab("head", "side", f"M {Z0} 832 L {Z1} 832 L {Z1} {YF} L {Z0} {YB} Z", [CX - HW / 2, CX + HW / 2], "body", r=26)
d.decal("sticker", [CX + 108, 868, Z1 + 0.4], [80, 48], "front", "gloss#3a8ee0", soft=True)
d.decal("sticker-t", [CX + 108, 876, Z1 + 0.8], [64, 3], "front", "plastic#e8eef6", soft=True, copies=[[0, -8, 0], [0, -16, 0]])
ang = math.degrees(math.atan((YB - YF) / (Z1 - Z0)))
tilt = rot("x", ang, [CX, YB, Z0])
yt = YB - 3
d.box("ctrl", [CX - 196, yt - 2, Z0 + 26, CX + 196, yt + 1.5, Z1 - 24], "panel", r=6, rot=tilt)
d.box("ledwin", [CX - 176, yt + 1, Z0 + 52, CX - 146, yt + 2.5, Z0 + 70], "led", soft=True, rot=tilt,
      repeat=rep(9, [40, 0, 0]))
for i, z in enumerate((112, 160, 208, 256)):
    d.box(f"keys{i}", [CX - 182, yt + 1, Z0 + z, CX - 164, yt + 4, Z0 + z + 12], "key", r=2, rot=tilt,
          repeat=rep(14, [26, 0, 0]))
d.box("wkeys", [CX - 182, yt + 1, Z0 + 312, CX - 156, yt + 4, Z0 + 326], "wkey", r=2, rot=tilt, repeat=rep(10, [36, 0, 0]))
d.box("rkey", [CX + 146, yt + 1, Z0 + 340, CX + 176, yt + 4.5, Z0 + 356], "red", r=3, rot=tilt)
# blue holders on the head sides (two right, one left at the back) with hanging electrode cables and clips
XR = CX + HW / 2
for k, z in enumerate((ZC + 120, ZC + 30)):
    d.box(f"holder{k}", [XR - 4, 944, z - 26, XR + 36, 1006, z + 26], "blue", r=10)
    d.box(f"holder-slot{k}", [XR + 24, 986, z - 18, XR + 37, 1007, z + 18], "plastic#1f4f9a", r=4, soft=True)
    for j, dz in enumerate((-12, 0, 12)):
        x = XR + 30 + 3 * j
        d.tube(f"cable{k}{j}", [[x, 996, z + dz], [x + 6, 900, z + dz + 4], [x + 2, 760 - 50 * j, z + dz - 6]], 6,
               "cable", bend=60, soft=True)
        d.box(f"clip{k}{j}", [x - 5, 704 - 50 * j, z + dz - 10, x + 9, 760 - 50 * j, z + dz + 4],
              "red" if j == 1 else "blue", r=4, soft=True)
d.box("holder-l", [CX - HW / 2 - 36, 944, ZC - 150, CX - HW / 2 + 4, 1006, ZC - 98], "blue", r=10)
d.save()
