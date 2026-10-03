"""xyj-7 Wrist Rotation Exerciser (desk). Photo from the front-left above; x = (px - 40) * 0.86."""
from k7lib import *

d = D("xyj-7", [610, 220, 270], {
    "wood": "wood#e2c48c", "pad": "leather#1d3a6e", "white": "plastic#eff0ec", "chrome": "chrome",
    "black": "plastic#17181a", "strap": "plastic#f7f7f4"})
# --- base board, two steps
d.box("board", [0, 0, 0, 610, 14, 220], "wood", r=3)
d.box("board-top", [8, 13, 8, 602, 24, 212], "wood", r=3)
# --- wooden box with the navy cushion, two white velcro straps, black star knob on the front
d.box("box", [16, 24, 18, 304, 128, 204], "wood", r=4)
d.box("cushion", [18, 127, 20, 302, 172, 202], "pad", r=16, puff=6)
for nm, x in (("a", 72), ("b", 200)):
    # flat band over the cushion and down its front and back (side-plane outline, 64 wide)
    band = ("M 8 100 L 8 168 Q 8 187 28 187 L 192 187 Q 212 187 212 168 L 212 100 L 208 100 L 208 168 "
            "Q 208 183 192 183 L 28 183 Q 12 183 12 168 L 12 100 Z")
    d.slab(f"strap-{nm}", "side", band, [x - 32, x + 32], "strap", r=1)
def star(id, at, axis, r, h):
    d.lathe(id, at, [[0, 0], [r * 0.45, 0], [r * 0.45, h * 0.3], [r, h * 0.35], [r, h * 0.9], [r * 0.6, h], [0, h]], "black", axis=axis)
    for k in range(6):
        import math
        a = math.radians(k * 60)
        if axis == "z":
            p = [at[0] + r * math.cos(a), at[1] + r * math.sin(a), at[2] + h * 0.35]
            d.cyl(f"{id}-lobe{k}", p, [p[0], p[1], at[2] + h * 0.9], r * 0.42, "black")
        else:
            p = [at[0] + r * math.cos(a), at[1] + h * 0.35, at[2] + r * math.sin(a)]
            d.cyl(f"{id}-lobe{k}", p, [p[0], at[1] + h * 0.9, p[2]], r * 0.42, "black")
star("box-knob", [205, 68, 204], "z", 20, 30)
# round metal badge on the box's left end (photo): a light disc with a dark ring
d.cyl("box-badge", [16, 84, 110], [14, 84, 110], 36, "metal#b9bcc0", soft=True)
d.cyl("box-badge-ring", [14.2, 84, 110], [13.6, 84, 110], 28, "plastic#4a5560", soft=True)
d.cyl("box-badge-in", [13.8, 84, 110], [13.2, 84, 110], 22, "metal#c9ccd0", soft=True)
# --- white bracket: foot plate with 4 bolts, upright plate with a rounded top
d.box("foot-plate", [478, 24, 40, 570, 30, 200], "white", r=3)
d.cyl("bolt", [492, 30, 58], [492, 36, 58], 14, "chrome", copies=[[64, 0, 0], [0, 0, 124], [64, 0, 124]])
d.slab("upright", "side", "M 70 30 L 170 30 L 170 165 A 50 50 0 0 1 70 165 Z", [545, 567], "white", r=5)
# --- drum on a horizontal axis (x): chrome drum, black disc facing the cushion, chrome hub, star knob on top
AY, AZ = 162, 120
d.cyl("drum", [486, AY, AZ], [545, AY, AZ], 126, "chrome")
d.cyl("disc", [468, AY, AZ], [488, AY, AZ], 130, "black")
d.cyl("hub", [446, AY, AZ], [470, AY, AZ], 46, "chrome")
d.decal("hub-mark", [445.4, AY, AZ], [22, 22], "plastic#8a8d93", face="left", soft=True)
star("drum-knob", [515, AY + 60, AZ], "y", 15, 24)
# --- crank: chrome post rising from the hub, clamp at the top, chrome lever with a black grip pointing left
d.cyl("post", [458, AY, AZ], [458, 268, AZ], 16, "chrome")
d.box("clamp", [447, 234, AZ - 13, 470, 258, AZ + 13], "chrome", r=4)
# cam lever (photo): a black knurled nut by the post, then a tapered chrome handle pointing left and a little forward
d.cyl("lever-nut", [446, 246, AZ + 1], [426, 247, AZ + 4], 30, "black")
d.cyl("lever", [426, 247, AZ + 4], [372, 250, AZ + 14], 22, "chrome", d2=16)
d.sphere("lever-end", [370, 250, AZ + 14], 22, "chrome")
d.save()
