from pd1_lib import *
W, D_, H = 700, 980, 1220
d = K("xyrt-10", [W, D_, H], {"wt": "plastic#eef0f2", "blue": "leather#4a6ab8", "blued": "leather#3d5ba6",
                               "knob": "gloss#3a78d0", "wood": "plastic#e6d0a6", "woode": "plastic#c27a3e",
                               "box": "wood#d9a866", "grey": "metal#9ca1a7", "chrome": "chrome", "strap": "fabric#1a1a1a"})
cx = W / 2
# base: two side rails bent down to the castor sockets, a rear and a front crossbar
for s, x in (("l", 70),):
    d.tube("rail-" + s, [[x, 80, 50], [x, 100, 120], [x, 100, 860], [x, 80, 930]], 30, "wt", bend=50, mirror="x")
d.cyl("cross-r", [70, 100, 150], [W - 70, 100, 150], 28, "wt")
d.cyl("cross-f", [70, 100, 840], [W - 70, 100, 840], 28, "wt")
d.caster("cas", [70, 0, 50], 56, "gloss#4a6cad", copies=[[0, 0, 880]], mirror="x")
d.sphere("ball", [70, 28, 50 - 17], 56, "gloss#4a6cad", copies=[[0, 0, 880]], mirror="x")
# rear uprights carrying the back support
d.bar("up", [165, 100, 185], [165, 1000, 185], [30, 24], "wt", r=4, mirror="x")
d.decal("holes", [165, 250, 197.5], [8, 8], "front", "black#333333", repeat=rep(6, [0, 40, 0]), mirror="x")
# telescopic / hinge details on the uprights (photo, left upright): black collar, chrome pivot with a knob, a clamp,
# the thinner inner tube beside the square upright
d.box("collar", [146, 520, 172, 184, 556, 198], "black#2a2a2a", r=4, mirror="x")
d.box("pivot", [144, 628, 170, 186, 668, 200], "chrome", r=5, mirror="x")
d.cyl("pivot-bolt", [144, 648, 185], [112, 648, 185], 14, "chrome", mirror="x")
d.sphere("pivot-knob", [108, 648, 185], 26, "black#2a2a2a", mirror="x")
d.box("clamp-up", [148, 735, 172, 182, 760, 198], "chrome", r=4, mirror="x")
d.cyl("inner-up", [138, 110, 185], [138, 560, 185], 16, "wt", mirror="x")
# backrest (upper) with a padded strap across, two white crossbars, the lower pad of three rolls
d.box("back", [165, 760, 197, W - 165, 1218, 258], "blue", r=48, puff=4)
d.box("back-strap", [176, 925, 248, W - 176, 1035, 264], "blued", r=12, puff=2)
d.cyl("bk-bar", [165, 692, 200], [W - 165, 692, 200], 22, "wt", copies=[[0, 36, 0]])
# lower hip pad: one flat upholstered pad with a darker strap across its middle (photo)
d.box("low", [185, 330, 197, W - 185, 640, 262], "blue", r=32, puff=5)
d.box("low-strap", [178, 423, 254, W - 178, 496, 272], "blued", r=10, puff=2)
# tray: wood top with darker edge banding, blue crescent chest block on its back edge
d.box("tray-e", [25, 630, 400, W - 25, 648, 860], "woode", r=8)
d.box("tray", [28, 642, 403, W - 28, 658, 857], "wood", r=6)
arc = [(cx + 120 * math.cos(math.radians(a)), 400 + 85 * math.sin(math.radians(a))) for a in range(0, 181, 15)]
outline = [(110, 400), (cx - 120, 400)] + list(reversed(arc))[1:-1][::-1][::-1] + [(cx + 120, 400), (W - 110, 400), (W - 110, 520), (110, 520)]
pts = [(110, 400), (cx - 120, 400)] + [(cx - 120 * math.cos(math.radians(a)), 400 + 85 * math.sin(math.radians(a))) for a in range(15, 180, 15)] + [(cx + 120, 400), (W - 110, 400), (W - 110, 520), (110, 520)]
d.slab("chest", "top", rpoly(pts, 25), [658, 712], "blue", r=20)
# under the tray: chrome slide rails, grey clamp blocks, a white cross tube
d.cyl("slide", [60, 612, 520], [W + 0, 612, 520], 16, "chrome", copies=[[0, 0, 190]])
d.sphere("slide-cap", [W - 4, 612, 520], 22, "black#2a2a2a", copies=[[0, 0, 190]])
d.box("clamp", [190, 500, 560, 270, 610, 670], "grey", r=6, copies=[[240, 0, 0]])
d.cyl("tray-x", [150, 592, 640], [W - 150, 592, 640], 26, "wt")
# front posts (telescopic) with blue knobs
d.cyl("post", [150, 100, 640], [150, 630, 640], 36, "wt", mirror="x")
d.cyl("post-in", [150, 470, 640], [150, 630, 640], 40, "wt", mirror="x")
# blue knobs (photo): two locking knobs on the outer side of each front post, two on the tray clamp's left end
d.sphere("pknob", [122, 520, 640], 34, "knob", copies=[[0, 75, 0]], mirror="x")
d.sphere("tknob", [100, 600, 470], 32, "knob", copies=[[0, 0, 95]])
# foot box: plate + back board, black ankle and foot straps
d.box("fb-plate", [160, 100, 240, W - 160, 136, 600], "box", r=5)
d.box("fb-back", [160, 136, 240, W - 160, 255, 262], "box", r=5)
d.box("fb-div", [cx - 4, 136, 262, cx + 4, 150, 600], "woode", r=2)
d.box("ankle", [185, 170, 262, 330, 226, 278], "strap", r=6, copies=[[185, 0, 0]])
d.box("toe", [195, 136, 430, 320, 146, 490], "strap", r=6, copies=[[185, 0, 0]])
d.save()
