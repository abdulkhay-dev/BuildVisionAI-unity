from pd1_lib import *
W, D_, H = 1350, 960, 1230
d = K("soft-building-blocks", [W, D_, H], {"r": "leather#e02020", "y": "leather#f6d21a", "g": "leather#14915a", "b": "leather#1f3fb0"})
R = 18                                      # soft edge radius of the foam blocks


def arch_shape(x0, x1, y0, y1, ac, aw, ah, apex=None):
    """Front outline: block x0..x1, y0..y1 (or a gable to `apex` height) with a round-headed arch from below."""
    hw = aw / 2
    pts = [(x0, y0), (ac - hw, y0), (ac - hw, y0 + ah - hw)]
    pts += [(ac + hw * math.cos(math.radians(180 - 15 * i)), y0 + ah - hw + hw * math.sin(math.radians(180 - 15 * i))) for i in range(1, 12)]
    pts += [(ac + hw, y0 + ah - hw), (ac + hw, y0), (x1, y0), (x1, y1)]
    pts += [((x0 + x1) / 2, apex)] if apex else []
    pts += [(x0, y1)]
    return poly(pts)


# ---- left castle (behind): big blue block, two green pillars, yellow gable piece with an arch notch
# the left pillar stands on its own blue cube (hidden behind the big front cube in the photo)
d.box("blue-cube-l", [180, 0, 50, 400, 240, 260], "b", r=R)
d.box("pillar-l", [175, 240, 50, 405, 780, 270], "g", r=R)
# front left: the big blue cube well in front of the castle, a short red cylinder on its back part
d.box("blue-big", [20, 0, 470, 410, 250, 740], "b", r=R)
d.cyl("red-short", [185, 250, 545], [185, 445, 545], 150, "r")
d.box("blue-cube", [462, 0, 50, 668, 240, 260], "b", r=R)
d.box("pillar-r", [458, 240, 50, 668, 780, 270], "g", r=R)
d.slab("roof-l", "front", arch_shape(170, 676, 780, 860, 432, 140, 120, apex=1040), [55, 285], "y", r=R)
# ---- right castle (front right): green beam, yellow cubes, red cylinders, green blocks, yellow arch, gable roof
X0, X1, Z0, Z1 = 663, 1198, 250, 460
d.box("beam", [X0 - 5, 0, Z0 - 5, X1 + 5, 70, Z1 + 25], "g", r=R)
for s, (a, b) in (("l", (X0 + 5, X0 + 205)), ("r", (X1 - 205, X1 - 5))):
    d.box("cube-" + s, [a, 70, Z0 + 5, b, 270, Z1 - 5], "y", r=R)
    d.cyl("col-" + s, [(a + b) / 2, 270, (Z0 + Z1) / 2], [(a + b) / 2, 620, (Z0 + Z1) / 2], 178, "r")
    d.box("green-" + s, [a - 3, 620, Z0, b + 3, 790, Z1], "g", r=R)
ac = (X0 + X1) / 2
d.slab("arch", "front", arch_shape(X0, X1, 790, 970, ac, 136, 92), [Z0, Z1], "y", r=R)
d.slab("gable-l", "front", poly([(X0, 970), (ac, 970), (ac, 1225)]), [Z0 + 10, Z1 - 10], "y", r=R)
d.slab("gable-r", "front", poly([(ac, 970), (X1, 970), (ac, 1225)]), [Z0 + 10, Z1 - 10], "y", r=R)
d.slab("moon", "front", "M %.1f 970 A 68 68 0 0 1 %.1f 970 Z" % (ac - 68, ac + 68), [Z1 - 12, Z1 + 4], "b", r=6)
# ---- two long green wedges on the floor in front, red triangular ends facing each other
d.slab("wedge-l", "side", poly([(740, 0), (955, 0), (740, 135)]), [230, 770], "g", r=12, rot=rot("y", -8, [770, 0, 850]))
d.slab("wedge-l-end", "side", poly([(742, 2), (951, 2), (742, 131)]), [768, 778], "r", r=4, rot=rot("y", -8, [770, 0, 850]))
d.slab("wedge-r", "side", poly([(740, 0), (955, 0), (740, 135)]), [850, 1340], "g", r=12, rot=rot("y", 8, [850, 0, 850]))
d.slab("wedge-r-end", "side", poly([(742, 2), (951, 2), (742, 131)]), [842, 852], "r", r=4, rot=rot("y", 8, [850, 0, 850]))
d.save()
