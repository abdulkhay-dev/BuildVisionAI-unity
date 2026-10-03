"""xy-cpm-ib: finger CPM desk unit on a chrome tube frame. Front = the body's end face (inlet, DB9, switch)."""
from k1lib import *

d = D("xy-cpm-ib", [480, 560, 320], {
    "white": "gloss#f4f5f6", "panel": "plastic#c6cad0", "lcd": "gloss#a9b48c", "key": "gloss#1f3f8f",
    "chrome": "chrome", "alu": "metal#c9ccd0", "black": "plastic#18191b", "sling": "fabric#1c1d20",
    "foam": "rubber#202124", "blue": "gloss#2a62b8"})
# --- chrome rectangular tube frame lying on the table, black foam grip on the front edge (left half)
# (the frame reaches ~40 beyond the body's right side and ~55 in front of its end face, as in the photo)
d.tube("frame", [[12, 12, 12], [468, 12, 12], [468, 12, 448], [12, 12, 448], [12, 12, 12]], 20, "chrome", bend=45)
d.cyl("foam", [40, 12, 448], [215, 12, 448], 36, "foam")
d.cyl("ferrule", [30, 12, 448], [42, 12, 448], 30, "chrome", copies=[[183, 0, 0]])
d.box("cross-plate", [225, 18, 70, 470, 24, 420], "alu", r=4)
# --- white body on the right half, strongly rounded front-top edge
# body profile: short vertical end face, a 35 deg sloped facet carrying the oval panel, flat top to the back
body = "M 20 24 L 392 24 L 392 106 Q 392 122 381 131 L 258 217 Q 246 232 226 232 L 20 232 Z"
d.slab("body", "side", body, [232, 430], "white", r=26)
PC = [331, 174.5, 319.5]            # panel centre on the facet
tilt = rot("x", 35, PC)
dz = PC[2] - 250
d.slab("panel", "top", ellipse(331, PC[2], 88, 58), [PC[1], PC[1] + 2.5], "panel", r=1, rot=tilt)
t = PC[1] + 2.5
d.box("lcd", [292, t - 0.5, 222 + dz, 362, t + 1, 258 + dz], "lcd", r=3, soft=True, rot=tilt)
d.sphere("key", [290, t, 280 + dz], None, "key", radii=[11, 3, 8], repeat=rep(4, [26, 0, 0]), rot=tilt)
d.sphere("key-b", [302, t, 296 + dz], None, "key", radii=[11, 3, 8], repeat=rep(3, [26, 0, 0]), rot=tilt)
d.sphere("key-c", [372, t, 240 + dz], None, "key", radii=[11, 3, 8], rot=tilt)
d.decal("panel-logo", [270, t + 0.2, 222 + dz], [12, 12], "top", "blue", soft=True, rot=tilt)
# front face: power inlet, DB9 plug, green rocker switch
d.box("inlet", [250, 70, 390, 292, 124, 395], "black", r=4)
d.box("db9", [312, 62, 392, 362, 98, 418], "plastic#9a9da2", r=5)
d.box("switch", [372, 36, 391, 402, 72, 397], "gloss#1f9a4a", r=4)
# --- black forearm sling on a bracket on the left half, clamp knob
d.box("sling-bracket", [40, 20, 90, 220, 50, 360], "alu", r=6)
d.box("sling-a", [36, 50, 70, 222, 120, 380], "sling", r=26, puff=8)
d.box("sling-b", [52, 112, 96, 206, 158, 330], "sling", r=22, puff=8)
d.strap("sling-strap", [[30, 90, 250], [129, 168, 250], [226, 90, 250]], [42, 3], "sling", bend=40, soft=True)
d.lathe("sling-knob", [8, 70, 360], [[0, 0], [20, 2], [20, 20], [8, 22], [8, 30], [0, 30]], "black", axis="x")
# --- finger mechanism behind the body: post, motor cylinder (axis x), bar along x, 4 clamps with rods forward
# thin chrome post rising behind the body, aluminium motor cylinder with a vertical axis on top of it
# (beside the body's back-left corner: the bar reaches over the sling's back end toward -x)
d.cyl("mech-post", [212, 24, 40], [212, 262, 40], 22, "chrome")
d.cyl("motor", [212, 262, 40], [212, 318, 40], 62, "alu")
d.cyl("motor-cap", [212, 318, 40], [212, 320, 40], 56, "metal#aeb2b8")
d.bar("finger-bar", [30, 285, 40], [184, 285, 40], [20, 20], "chrome", r=3)
d.box("clamp", [36, 268, 25, 66, 305, 58], "chrome", r=4, repeat=rep(4, [40, 0, 0]))
d.bar("clamp-rod", [51, 280, 58], [51, 262, 175], [14, 6], "chrome", r=2, repeat=rep(4, [40, 0, 0]))
d.box("finger-strap", [30, 240, 60, 190, 262, 150], "sling", r=8, soft=True)
# --- hand controller in front, coiled cable to the DB9
controller(d, "controller", 285, 470, [337, 80, 418])
d.save()
