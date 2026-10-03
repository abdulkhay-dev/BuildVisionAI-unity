"""XY-K-PDJ-IV portable pelvic floor trainer. Writes only xy-k-pdj-iv.json."""
from lib import *
import math
from p4lib import *

d = D("xy-k-pdj-iv", [340, 170, 350], {"shell": "gloss#eceef1", "pink": "plastic#c4909f", "knob": "plastic#e0a0b1",
                                       "gold": "metal#c9a46a", "glass": "gloss#101113", "grey": "plastic#9aa0a6", "dark": "plastic#3a3f45"})
d.slab("body", "front", rrect(3, 4, 337, 350, 42), [95, 170], "shell", r=16)
d.add("screen", "screen", "glass", box=[35, 104, 165, 308, 307, 170.3], r=8, bezel=1.5, print="med_xy-k-pdj-iv_screen")
d.decal("brand", [57, 324, 170.4], [22, 7], "front", "plastic#55595f", soft=True)
d.decal("title", [176, 326, 170.4], [48, 5], "front", "plastic#7a7f86", soft=True)
d.decal("title-en", [176, 318, 170.4], [66, 2.5], "front", "plastic#8a8f96", soft=True)
d.box("sensor", [290, 316, 168, 296, 331, 172], "glass", r=2.5)
xs = [[69 * k, 0, 0] for k in range(1, 4)]
d.lathe("knob-rim", [67, 72, 169], [[0, 0], [21, 0], [21, 4], [0, 4]], "gold", axis="z", sides=28, copies=xs)
d.lathe("knob", [67, 72, 172], [[0, 0], [19.5, 0], [19.5, 18], [17, 22], [0, 22]], "knob", axis="z", sides=30, copies=xs)
d.slab("knob-arc", "front", band(arc(67, 72, 14, 20, 75, 8), 0.8), [194, 194.4], "plastic#fbfbfb", soft=True, copies=xs)
# grey pill label slanting at the lower left of each knob, the channel letter in a circle at its end
d.decal("knob-label", [54, 43, 170.4], [24, 7], "front", "plastic#8a8d93", soft=True, copies=xs, rot=rot("z", -28, [54, 43, 170.4]))
d.cyl("knob-letter", [72, 37, 169], [72, 37, 171], 7, "plastic#8a8d93", soft=True, copies=xs)
# pink spines on both sides: a rounded strip with a groove, ending at the bottom in a round lobe around the power button
zc, zl, zr, yt, yb, R = 134, 112, 156, 312, 50, 33
dy = (R * R - (zc - zl) ** 2) ** 0.5
a0 = math.degrees(math.atan2(dy, zl - zc))
spine = poly(arc(zc, yt, (zr - zl) / 2, 0, 180, 10) + arc(zc, yb, R, a0, 540 - a0, 28))
d.slab("spine", "side", spine, [-1.5, 6], "pink", r=2.5, mirror="x")
d.decal("spine-groove", [-1.7, 245, zc], [4, 130], "left", "plastic#a8788a", soft=True, mirror="x")
d.cyl("socket", [3, 142, zc], [-4, 142, zc], 26, "plastic#a9acb1", mirror="x", copies=[[0, -38, 0]])
d.cyl("socket-in", [-1, 142, zc], [-5.5, 142, zc], 15, "plastic#3d4046", mirror="x", copies=[[0, -38, 0]])
d.cyl("button-ring", [3, yb, zc], [-4, yb, zc], 50, "plastic#f4f4f5", sides=16, mirror="x")
d.cyl("button", [-1, yb, zc], [-6, yb, zc], 28, "chrome", mirror="x")
d.cyl("button-sym", [-5.8, yb, zc], [-6.4, yb, zc], 12, "plastic#7b8087", soft=True, mirror="x")
# right side: small grey rocker at the front edge; left side: 2 USB ports, a round jack, a small hole near the front edge
d.box("rocker", [336, 222, 160, 340, 252, 168], "plastic#c9ccd0", r=2)
d.box("usb-plate", [0.5, 214, 158, 4, 266, 168], "plastic#e4e6e9", r=2)
d.box("usb", [-0.5, 220, 160, 1.5, 233, 166], "dark", r=1, copies=[[0, 24, 0]])
d.cyl("jack", [2, 196, 163], [-1, 196, 163], 9, "dark")
d.cyl("hole", [2, 182, 163], [-1, 182, 163], 4, "dark")
# folding kickstand
d.cyl("hinge", [90, 222, 93], [250, 222, 93], 12, "plastic#b7bbc0")
d.add("stand", "bar", "plastic#b7bbc0", **{"from": [170, 222, 92], "to": [170, 2, 4]}, section=[170, 5], r=2)
d.box("foot", [40, 0, 110, 90, 5, 160], "rubber#4a4d52", r=2, copies=[[210, 0, 0]])
d.save()
