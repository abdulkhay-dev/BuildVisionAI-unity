from pd1_lib import *
W, D_, H = 420, 560, 680
d = K("xyrt-108", [W, D_, H], {"ply": "wood#dcbc8e", "rail": "wood#c8803e", "floor": "wood#d6ae80",
                                "rod": "plastic#f2f2f0", "red": "gloss#d41e1e", "dowel": "wood#d9b67a"})
T = 15
d.box("base", [0, 0, 0, W, T, D_], "ply", r=3)
# light grooves across the base behind the prop (angle notches)
d.box("notch", [140, T, 60, 280, T + 1, 72], "plastic#efe6d2", soft=True, repeat=rep(3, [0, 0, 50]))
# the trough, drawn lying flat (foot at zF, running back along −z) then tilted up about its foot
A = 62
zF, L = 520, 720
TR = rot("x", A, [0, T, zF])             # +deg about x: the far end (−z) rises
x0, x1 = 85, 335
d.box("tfloor", [x0, T, zF - L, x1, T + 12, zF], "floor", r=2, rot=TR)
d.box("tside", [x0 - 6, T, zF - L, x0 + 22, T + 58, zF], "rail", r=3, rot=TR)
d.box("tside2", [x1 - 22, T, zF - L, x1 + 6, T + 58, zF], "rail", r=3, rot=TR)
d.box("tend", [x0 - 6, T, zF - L, x1 + 6, T + 58, zF - L + 24], "rail", r=3, rot=TR)
d.box("tfoot", [x0 - 6, T, zF - 22, x1 + 6, T + 40, zF], "rail", r=3, rot=TR)
for i, x in enumerate((140, 280)):
    d.cyl(f"rod{i}", [x, T + 34, zF - L + 24], [x, T + 34, zF - 22], 20, "rod", rot=TR)
# sliding block at the foot of the trough: plywood plate with a raised right edge, a dowel through it across
d.box("block", [x0 - 55, T + 46, zF - 250, x1 + 10, T + 64, zF - 26], "ply", r=3, rot=TR)
d.box("blk-edge", [x1 - 20, T + 46, zF - 250, x1 + 10, T + 104, zF - 26], "dowel", r=3, rot=TR)
d.box("blk-foot", [x0 - 55, T + 46, zF - 46, x1 + 10, T + 84, zF - 26], "dowel", r=3, rot=TR)   # light rim along its lower end
d.cyl("dowel", [0, T + 90, zF - 150], [W, T + 90, zF - 150], 26, "dowel", rot=TR)
d.cyl("peg", [95, T + 70, zF - 190], [175, T + 74, zF - 150], 22, "dowel", rot=TR)
d.sphere("knob", [x1 - 30, T + 70, zF - 236], 24, "red", rot=TR)
d.sphere("knob2", [x0 - 45, T + 70, zF - 60], 24, "red", rot=TR)
# prop leg: a plywood triangle under the upper part of the trough
s1, s2 = 330, 560                          # where it meets the trough's underside (distance from the foot)
ca, sa = math.cos(math.radians(A)), math.sin(math.radians(A))
p1 = (zF - s1 * ca, T + s1 * sa); p2 = (zF - s2 * ca, T + s2 * sa)
d.slab("prop", "side", poly([(p1[0] - 6, p1[1] - 6), (p2[0] - 6, p2[1] - 6), (p2[0] - 40, T), (p1[0] - 140, T)]), [W / 2 - 8, W / 2 + 8], "rail", r=2)
# small wooden stops at the foot
d.box("stop", [x0 - 10, T, zF, x0 + 30, T + 30, zF + 26], "dowel", r=3, copies=[[x1 - x0 - 20, 0, 0]])
d.save()
