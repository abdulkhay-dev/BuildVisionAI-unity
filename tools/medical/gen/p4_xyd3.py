"""XYD-III electroacupuncture desk unit. Writes only xyd-iii.json."""
from lib import *
from p4lib import arc, band

T = 48  # top of the grey panel
d = D("xyd-iii", [300, 210, 65], {"shell": "gloss#f4f5f6", "band": "plastic#5f6566", "panel": "plastic#7a8b99",
                                  "blue": "gloss#4a92d0", "cap": "gloss#2a7ccc", "white": "plastic#f2f3f5",
                                  "line": "plastic#e8ecef"})
# dark grey bottom band (about 40 % of the front) carrying the 6 output jacks; white rounded upper shell
d.add("bottom", "slab", "band", plane="top", box=[1, 0, 1, 299, 20, 209], radii=[20], r=3)
d.add("shell", "slab", "shell", plane="top", box=[0, 18, 0, 300, T - 1, 210], radii=[22], r=7)
d.box("panel", [14, T - 4, 14, 286, T, 188], "panel", r=5)
d.slab("header", "top", "M 14 14 L 286 14 L 286 40 L 200 40 L 184 56 L 14 56 Z", [T - 0.5, T + 0.6], "blue", r=0.4)
d.cyl("logo", [34, T + 0.5, 35], [34, T + 1.3, 35], 22, "white", soft=True)
d.decal("logo-t", [34, T + 1.4, 35], [3, 14], "top", "blue", soft=True)
d.decal("brand", [62, T + 1.4, 33], [26, 7], "top", "white", soft=True)
d.decal("title", [118, T + 1.4, 30], [76, 9], "top", "plastic#f2f4f7", soft=True)
d.decal("title-en", [118, T + 1.4, 44], [90, 4], "top", "plastic#f2f4f7", soft=True)
d.decal("led-power", [212, T + 1.4, 24], [5, 5], "top", "gloss#5bd34a", soft=True)
# power rocker: black square frame with the rocker
d.box("rocker-frame", [236, T, 16, 258, T + 3, 34], "black#141517", r=1.5)
d.box("rocker", [239, T + 2, 19, 255, T + 5.5, 26], "black#2a2c30", r=1.5, rot=rot("x", -12, [247, T + 3, 25]))
d.decal("power-text", [247, T + 1.4, 38], [34, 3.5], "top", "plastic#f2f4f7", soft=True)
# treatment-mode slide switch
d.box("slide", [52, T - 1, 96, 74, T + 2, 108], "black#1d1f22", r=1.5)
d.box("slide-knob", [55, T + 1, 98, 63, T + 4, 106], "plastic#d9dce0", r=1)
d.decal("slide-text", [63, T + 0.2, 118], [26, 3], "top", "line", soft=True)

def knob(nm, x, z, dc, copies=None):
    r = dc / 2
    # white fluted body (a 14-sided lathe reads as the ribs) under a blue domed cap of the same diameter
    d.lathe(nm + "-body", [x, T, z], [[0, 0], [r + 1.2, 0], [r + 1.2, 1.5], [r, 2.5], [r, 11], [0, 11]], "white", sides=14, copies=copies)
    d.lathe(nm + "-cap", [x, T + 11, z], [[0, 0], [r, 0], [r, 2.5], [r * 0.82, 5], [r * 0.45, 6.2], [0, 6.5]], "cap", sides=28, copies=copies)
    d.decal(nm + "-mark", [x + r * 0.2, T + 17.6, z - r * 0.25], [1.4, r * 0.8], "top", "white", soft=True, copies=copies,
            rot=rot("y", 30, [x, T + 17.6, z]))
    # 270-degree white scale arc around it, the gap at the front (OFF / MAX)
    d.slab(nm + "-scale", "top", band(arc(x, z, r + 5, 125, 415, 20), 0.5), [T, T + 0.25], "line", soft=True, copies=copies)
    d.decal(nm + "-offmax", [x, T + 0.3, z + r + 5], [dc + 6, 2.5], "top", "line", soft=True, copies=copies)

knob("knob-time", 112, 90, 24)
knob("knob-wave", 172, 84, 22)
knob("knob-freq", 232, 80, 26)
outs = [[34 * k, 0, 0] for k in range(1, 6)]
knob("knob-out", 70, 150, 19, outs)
# output indicator LEDs with their connecting line, and the OUTPUT(1-6) bracket down to the jacks
d.decal("led-out", [70, T + 0.3, 127], [3.5, 3.5], "top", "gloss#5bd34a", soft=True, copies=outs)
d.decal("led-line", [155, T + 0.3, 134], [176, 0.9], "top", "line", soft=True)
d.decal("led-tick", [70, T + 0.3, 131.5], [0.9, 5], "top", "line", soft=True, copies=outs)
d.decal("bracket", [155, T + 0.3, 176], [176, 0.9], "top", "line", soft=True)
d.decal("bracket-tick", [70, T + 0.3, 181], [0.9, 10], "top", "line", soft=True, copies=outs)
d.decal("output-text", [155, T + 0.3, 172], [40, 3], "top", "line", soft=True)
d.cyl("jack", [70, 10, 208.5], [70, 10, 211], 9, "metal#c9ccd0", copies=outs)
d.cyl("jack-hole", [70, 10, 210], [70, 10, 211.6], 4.5, "black#111214", copies=outs)
d.save()
