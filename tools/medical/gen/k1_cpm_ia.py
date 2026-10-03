"""xy-cpm-ia: wrist CPM desk unit. Long axis x; x=0 end = console end (power inlet + DB9 plug);
front (z max) = the long face with the slot and the lever linkage; hand controller lies in front."""
from k1lib import *


d = D("xy-cpm-ia", [500, 380, 320], {
    "white": "gloss#f4f5f6", "panel": "plastic#c6cad0", "lcd": "gloss#a9b48c", "key": "gloss#1f3f8f",
    "chrome": "chrome", "black": "plastic#18191b", "sling": "fabric#1c1d20", "grey": "plastic#9a9ea4",
    "blue": "gloss#2a62b8"})
X0 = 25
# --- body: console part (x 25-275, 160 high) and the lower step at the far end (120 high)
d.box("console", [X0, 0, 0, X0 + 250, 160, 240], "white", r=20)
d.box("step", [X0 + 230, 0, 0, 495, 120, 240], "white", r=16)
d.box("slot", [X0 + 270, 52, 239, X0 + 420, 70, 242], "black", r=6)
d.cyl("slot-rod", [X0 + 275, 61, 242], [X0 + 415, 61, 242], 10, "chrome")
# --- oval membrane panel on the console top (major axis along z), LCD toward the far end, 8 dark-blue keys
d.slab("panel", "top", ellipse(X0 + 118, 120, 88, 108), [160, 162.5], "panel", r=1)
d.box("lcd", [X0 + 135, 162, 72, X0 + 180, 164, 168], "lcd", r=3, soft=True)
d.sphere("key", [X0 + 100, 163, 70], None, "key", radii=[9, 3, 13], repeat=rep(4, [0, 0, 32]))
d.sphere("key-b", [X0 + 72, 163, 86], None, "key", radii=[9, 3, 13], repeat=rep(4, [0, 0, 32]))
d.decal("panel-logo", [X0 + 182, 162.8, 50], [14, 14], "top", "blue", soft=True)
# --- console end: power inlet, grey DB9 plug with the cable
d.box("inlet", [X0 - 3, 70, 30, X0 + 2, 118, 78], "black", r=4)
d.box("db9", [X0 - 26, 38, 150, X0 + 1, 76, 205], "plastic#9a9da2", r=5)
# --- forearm sling cradle on the step between two chrome rails, rails to the hubs at the far end
d.box("sling-a", [X0 + 240, 112, 22, X0 + 455, 178, 218], "sling", r=24, puff=8)
d.box("sling-b", [X0 + 250, 168, 36, X0 + 440, 222, 204], "sling", r=22, puff=8)
d.strap("sling-strap", [[X0 + 330, 150, 18], [X0 + 330, 228, 60], [X0 + 330, 230, 180], [X0 + 330, 150, 222]],
        [40, 3], "sling", bend=40, soft=True)
for nm, z in (("b", 28), ("f", 212)):
    d.cyl(f"rail-{nm}", [X0 + 175, 218, z], [458, 262, z], 18, "chrome")
    d.cyl(f"rail-cap-{nm}", [X0 + 150, 214, z], [X0 + 178, 218.5, z], 22, "black")
    d.cyl(f"hub-post-{nm}", [458, 118, z], [458, 230, z], 22, "chrome")
    # hub discs on the wrist axis (along z, across the forearm): a drum with a narrower boss on the inner side,
    # a blue logo on the inner face
    sz = 1 if z < 100 else -1          # toward the sling
    d.cyl(f"hub-{nm}", [458, 262, z - sz * 26], [458, 262, z + sz * 18], 84, "chrome")
    d.cyl(f"hub-boss-{nm}", [458, 262, z + sz * 18], [458, 262, z + sz * 30], 60, "chrome")
    d.cyl(f"hub-logo-{nm}", [458, 262, z + sz * 30], [458, 262, z + sz * 31], 26, "blue", soft=True)
# lever linkage on the front face from the slot up to the front hub, clamp knob at the end
d.bar("link-a", [X0 + 290, 62, 246], [430, 205, 250], [20, 6], "chrome", r=2)
d.bar("link-b", [430, 205, 250], [458, 258, 250], [20, 6], "chrome", r=2)
d.cyl("link-pin", [430, 205, 240], [430, 205, 258], 16, "chrome")
d.box("clamp-block", [462, 120, 232, 488, 160, 262], "black", r=4)
d.lathe("clamp-knob", [488, 140, 247], [[0, 0], [8, 0], [8, 6], [16, 8], [16, 20], [0, 22]], "chrome", axis="x")
# --- hand controller lying in front, coiled cable to the DB9 plug
controller(d, "controller", 250, 292, [X0 - 26, 56, 178])
d.save()
