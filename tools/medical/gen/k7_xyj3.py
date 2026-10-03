"""xyj-3 Forearm and Wrist Exerciser (desk). Photo front-ish, ~1 mm/px horizontally; W 700 = grip to grip."""
from k7lib import *

d = D("xyj-3", [700, 200, 220], {
    "white": "plastic#f3f4f2", "wood": "plastic#e8cc98", "chrome": "chrome", "teal": "plastic#13907e",
    "dark": "plastic#23262e", "rubber": "rubber#1c1d1f"})
AY, AZ = 165, 100   # roller axis
# --- base plate on 4 small black feet
d.box("base", [70, 8, 0, 560, 22, 200], "white", r=6)
d.cyl("foot", [92, 0, 22], [92, 9, 22], 18, "rubber", copies=[[446, 0, 0], [0, 0, 156], [446, 0, 156]])
d.decal("label", [330, 22.6, 150], [40, 14], "plastic#b9bcc2", face="top", soft=True)
# --- two white upright plates with rounded tops
for nm, x0 in (("l", 118), ("r", 442)):
    d.slab(f"upright-{nm}", "front", f"M {x0} 22 L {x0 + 54} 22 L {x0 + 54} {AY + 28} A 27 27 0 0 1 {x0} {AY + 28} Z",
           [55, 145], "white", r=8)
# --- stepped light-wood roller
d.cyl("roller-a", [172, AY, AZ], [250, AY, AZ], 38, "wood")
d.cyl("roller-b", [247, AY, AZ], [350, AY, AZ], 47, "wood")
d.cyl("roller-c", [347, AY, AZ], [442, AY, AZ], 56, "wood")
d.cyl("roller-step", [247, AY, AZ], [257, AY, AZ], 40, "wood", d2=47)
d.cyl("roller-step2", [347, AY, AZ], [355, AY, AZ], 49, "wood", d2=56)
# --- friction drum at the right of the right upright: chrome with dark rims, lock collar, small hanging lever
d.cyl("drum", [496, AY, AZ], [564, AY, AZ], 112, "chrome")
d.cyl("drum-rim", [496, AY, AZ], [505, AY, AZ], 114, "dark", copies=[[59, 0, 0]])
d.cyl("drum-face", [564, AY, AZ], [566, AY, AZ], 96, "dark")
d.cyl("collar", [564, AY, AZ], [586, AY, AZ], 52, "chrome")
d.box("lock-lever", [574, 92, AZ - 6, 586, AY, AZ + 6], "chrome", r=4, rot=rot("z", -6, [580, AY, AZ]))
# --- shafts and teal D grips at both ends
d.cyl("shaft-l", [110, AY, AZ], [120, AY, AZ], 22, "chrome")
d.cyl("shaft-r", [584, AY, AZ], [594, AY, AZ], 22, "chrome")
def grip(nm, sgn, xs, L):
    xo = xs + sgn * L           # outer end of the D
    path = [[xs, AY + 12, AZ], [xo - sgn * 10, AY + 38, AZ], [xo, AY + 32, AZ], [xo, AY - 34, AZ], [xo - sgn * 10, AY - 40, AZ], [xs, AY - 12, AZ]]
    d.sweep(f"grip-{nm}", path, [20, 26], "teal", shape="oval", bend=14)
    d.cyl(f"grip-bar-{nm}", [xo, AY - 36, AZ], [xo, AY + 36, AZ], 30, "teal")
    d.cyl(f"grip-hub-{nm}", [xs - sgn * 2, AY, AZ], [xs + sgn * 14, AY, AZ], 34, "teal")
grip("l", -1, 112, 98)
grip("r", 1, 592, 94)
d.save()
