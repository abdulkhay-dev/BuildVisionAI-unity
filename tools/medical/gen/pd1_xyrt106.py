from pd1_lib import *
W, D_, H = 650, 650, 1000
d = K("xyrt-106", [W, D_, H], {"g": "plastic#3f8a32", "gl": "plastic#6cb04a", "blk": "black#1e1e1e", "white": "plastic#f4f4f2"})
T = 25
d.box("base", [0, 0, 0, W, T, D_], "plastic#78bc4a", r=4)
# the stepped board (front face at zf), cut out of one slab: bands alternately ~200 and ~244 wide
zb, zf = 270, 295
cx = W / 2
bands = [(T, 325, 114), (325, 575, 100), (575, 725, 114), (725, H, 100)]   # y0, y1, half width (photo: wide/narrow/wide/narrow)
pts = []
for y0, y1, hw in bands:
    pts += [(cx - hw, y0), (cx - hw, y1)]
right = []
for y0, y1, hw in bands:
    right += [(cx + hw, y0), (cx + hw, y1)]
pts += list(reversed(right))
d.slab("board", "front", poly(pts), [zb, zf], "g", r=2)
# label plate with FUSHOU at the top
d.box("label", [cx - 52, 932, zf, cx + 52, 968, zf + 2], "white", r=1)
L = text_len("FUSHOU", 22)
text(d, "lbl", "FUSHOU", [cx - L / 2, 939, zf + 2.6], 22, "black#111111", stroke=3.4)
# abduction wedge in front of the board on its centre line
d.slab("wedge", "side", poly([(zf, T), (zf + 230, T), (zf, T + 270)]), [cx - 10, cx + 10], "gl", r=2)
# black side gussets at the foot of the board (both edges) and the angle brackets behind
for s, x in (("l", cx - 120), ("r", cx + 114)):
    d.slab(f"gus-{s}", "side", poly([(zb - 120, T), (zf + 120, T), (zf + 10, T + 110), (zb - 10, T + 110)]), [x, x + 6], "blk", r=1)
d.box("ang-b", [cx - 90, T, zb - 70, cx + 90, T + 6, zb], "blk", r=1)
d.box("ang-v", [cx - 90, T, zb - 6, cx + 90, T + 90, zb], "blk", r=1)
d.cyl("knob", [cx - 60, T + 50, zb - 6], [cx - 60, T + 50, zb - 40], 26, "blk", copies=[[120, 0, 0]])
# black foot stops in front, both sides of the wedge (L brackets turned outwards), and strap slots at the board foot
for s_, x, a in (("l", cx - 120, 25), ("r", cx + 120, -25)):
    d.box(f"fs-{s_}", [x - 60, T, zf + 70, x + 60, T + 5, zf + 150], "blk", r=1, rot=rot("y", a, [x, 0, zf + 110]))
    d.box(f"fsv-{s_}", [x - 60, T, zf + 70, x + 60, T + 55, zf + 76], "blk", r=1, rot=rot("y", a, [x, 0, zf + 110]))
d.box("slot", [cx - 88, 130, zf, cx - 81, 280, zf + 0.8], "black#1a1a1a", soft=True, copies=[[35, 0, 0], [134, 0, 0], [169, 0, 0]])
d.save()
