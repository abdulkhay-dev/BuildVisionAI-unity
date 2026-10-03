from k4lib import *
d = K("xy-3", [840, 1170, 430], {
    "alu": "metal#a7abb1", "tube": "metal#b8bbc0", "black": "plastic#1c1d20", "seat": "leather#1d1e21",
    "cap": "rubber#18191b", "hyd": "gloss#141517"})
CX = 420
# --- rear foot (chrome tube between black blocks), rear bracket with red label and knob
d.cyl("rear-foot", [300, 38, 70], [540, 38, 70], 34, "chrome")
d.box("rear-block", [245, 0, 25, 320, 72, 115], "cap", r=14, mirror="x")
d.box("rear-bracket", [372, 40, 40, 468, 150, 165], "alu", r=8)
# triangular red warning label with a white centre on the back of the bracket (photo)
d.slab("red-label", "front", "M 402 96 L 438 96 L 420 128 Z", [38.6, 39.6], "gloss#d62b25", soft=True)
d.slab("red-label-in", "front", "M 413 102 L 427 102 L 420 115 Z", [38.0, 38.6], "gloss#f2f2f2", soft=True)
d.lathe("rear-knob", [468, 95, 110], [[0, 0], [12, 0], [12, 12], [30, 16], [30, 38], [0, 42]], "black", axis="x")
# --- central beam rising slightly to the front
d.bar("beam", [CX, 150, 130], [CX, 248, 1100], [90, 50], "alu", r=6)
d.decal("beam-dot", [CX, 196, 650], [8, 8], "top", "plastic#5e6167")
d.lathe("beam-knob", [465, 205, 780], [[0, 0], [10, 0], [10, 12], [24, 15], [24, 34], [0, 37]], "black", axis="x")
# --- seat on its carriage
d.box("carriage", [368, 170, 205, 472, 210, 420], "alu", r=8)
d.box("seat", [230, 205, 175, 610, 268, 450], "seat", r=32, puff=8)
d.box("seat-pan", [250, 200, 195, 590, 212, 430], "black", r=8)
# --- bent U frame: across the front, arms sweeping back down to the floor; black end caps
U = [[60, 32, 470], [62, 110, 680], [100, 225, 980], [CX, 252, 1135], [740, 225, 980], [778, 110, 680], [780, 32, 470]]
d.tube("u-frame", U, 45, "tube", bend=170)
d.cyl("u-cap", [60, 34, 476], [60, 8, 412], 52, "cap", mirror="x")
# oar pivots, hydraulic cylinders along the arms, chrome oars with inward black grips
for nm, o in (("l", -1), ("r", 1)):
    xa = CX + o * 360           # arm x near the pivot
    xp = CX + o * 318
    d.lathe(f"pivot-{nm}", [xp, 92, 560], [[0, 0], [42, 0], [44, 10], [44, 34], [40, 42], [0, 44]], "black", axis="x",
            rot=rot("y", 0 if o < 0 else 180, [xp, 92, 560]))
    # photo: a chrome fork of two rounded cheek plates holds the oar foot on the drum axle, a flat chrome mounting
    # plate under it to the arm, a bolt and a small black clamp lever
    d.box(f"clamp-base-{nm}", [min(xa, xp) - 8, 58, 535, max(xa, xp) + 8, 72, 590], "chrome", r=4)
    xo = xp - o * 25
    for k, dx in (("a", -17), ("b", 17)):
        d.slab(f"clamp-{nm}{k}", "side", rpoly([(535, 66), (600, 66), (612, 128), (575, 140), (540, 112)], 10),
               [xo + dx - 2.5, xo + dx + 2.5], "chrome", r=1)
    d.cyl(f"clamp-bolt-{nm}", [xo - 24, 92, 560], [xo + 24, 92, 560], 12, "chrome")
    d.cyl(f"clamp-lever-{nm}", [xo + o * 22, 118, 590], [xo + o * 22, 165, 555], 9, "black")
    d.sphere(f"clamp-lever-end-{nm}", [xo + o * 22, 168, 553], 16, "black")
    d.cyl(f"hyd-{nm}", [xp, 105, 600], [CX + o * 335, 205, 900], 46, "hyd")
    d.cyl(f"hyd-rod-{nm}", [CX + o * 335, 205, 900], [CX + o * 330, 222, 960], 16, "chrome")
    d.tube(f"oar-{nm}", [[xp - o * 25, 95, 560], [xp - o * 30, 300, 790], [xp - o * 40, 412, 905]], 24, "chrome", bend=60)
    g0 = xp - o * 40
    d.cyl(f"grip-{nm}", [g0, 412, 905], [g0 - o * 125, 412, 905], 34, "rubber#1a1a1c")
# --- footplates on a bracket, straps, small LCD console
d.box("foot-bracket", [370, 215, 950, 470, 275, 1070], "alu", r=8)
FR = rot("x", -40, [CX, 265, 965])
for nm, x0 in (("l", 268), ("r", 452)):
    d.box(f"footplate-{nm}", [x0, 265, 965, x0 + 120, 283, 1215], "black", r=10, rot=FR)
    d.box(f"heel-{nm}", [x0, 265, 965, x0 + 120, 330, 985], "black", r=8, rot=FR)
    d.strap(f"strap-{nm}", [[x0 + 2, 284, 1110], [x0 + 60, 330, 1105], [x0 + 118, 284, 1110]], [45, 3], "fabric#202124",
            bend=35, rot=FR)
d.cyl("console-post", [CX, 250, 1040], [CX, 300, 1040], 30, "alu")
CR = rot("x", 30, [CX, 300, 1040])
d.box("console", [362, 295, 1028, 478, 380, 1060], "metal#d0d3d7", r=8, rot=CR)
d.screen("lcd", [382, 330, 1023, 458, 368, 1030], "black", face="back", bezel=4, rot=CR)
d.decal("btn", [400, 310, 1027.3], [12, 10], "back", "gloss#d62b25", rot=CR, copies=[[40, 0, 0]])
d.save()
