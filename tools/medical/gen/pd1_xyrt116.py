from pd1_lib import *
W, D_, H = 400, 800, 1000
d = K("xyrt-116", [W, D_, H], {"y": "gloss#f2b416", "blue": "leather#2a5db0", "red": "leather#d8282e",
                                "blk": "rubber#1a1a1a", "chrome": "chrome"})
cx = W / 2
# floor bars with black end caps
for nm, z in (("fb", 715), ("rb", 85)):
    d.cyl(nm, [25, 22, z], [W - 25, 22, z], 40, "y")
    d.cyl(nm + "-cap", [0, 22, z], [34, 22, z], 50, "blk", copies=[[W - 34, 0, 0]])
P = [cx, 360, 480]                          # scissor pivot
# rear link from the rear bar up to the pivot, continuing as the handle post
d.tube("rear-link", [[cx, 30, 85], P], 34, "y")
d.bar("post", [cx, 340, 474], [cx, 805, 582], [40, 40], "y", r=8)
d.bar("post-sleeve", [cx, 395, 487], [cx, 640, 544], [50, 50], "y", r=8)
d.cyl("post-knob", [cx + 25, 560, 525], [cx + 50, 560, 525], 22, "blk")
d.cyl("pivot-bolt", [cx - 30, 360, 480], [cx + 30, 360, 480], 26, "chrome")
# front link from the front bar through the pivot to the seat arm
d.tube("front-link", [[cx, 30, 715], [cx, 360, 492], [cx, 405, 390], [cx, 418, 250]], 34, "y", bend=90)
d.tube("brace", [[cx, 610, 543], [cx, 404, 400]], 20, "y")
# saddle on its plate, black end plug under the rear
d.box("seat-plate", [cx - 70, 418, 200, cx + 70, 434, 380], "y", r=4)
d.box("seat", [cx - 105, 432, 175, cx + 105, 508, 405], "red", r=32, puff=8)
d.cyl("plug", [cx, 410, 248], [cx, 410, 228], 32, "blk")
# handlebar: blue foam loop of two C halves with a gap at the top middle (leaning slightly back)
top = [cx, 840, 640]
def hz(y): return 584 - (y - 805) * 0.3
half = [[cx, 808, hz(808)], [72, 808, hz(808)], [26, 870, hz(870)], [30, 950, hz(950)], [85, 994, hz(994)], [178, 986, hz(986)]]   # loop ~400 × 195
d.tube("hb", half, 44, "blue", bend=55, mirror="x")
d.cyl("hb-core", [cx - 22, 808, hz(808)], [cx + 22, 808, hz(808)], 34, "y")
# pedals on short curved arms at the pivot, both sides
d.tube("ped-arm", [[cx - 20, 360, 480], [120, 330, 525], [75, 255, 615]], 24, "y", bend=40, mirror="x")
d.box("pedal", [20, 228, 575, 110, 252, 680], "blk", r=6, mirror="x")
d.box("pedal-heel", [20, 248, 572, 110, 298, 592], "blk", r=8, mirror="x")        # raised heel cup (photo)
d.box("pedal-side", [16, 248, 572, 30, 285, 680], "blk", r=5, mirror="x")
d.box("pedal-rib", [24, 252, 585, 106, 258, 593], "blk", r=2, repeat=rep(5, [0, 0, 20]), mirror="x")
d.save()
