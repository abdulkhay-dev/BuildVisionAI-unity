from k4lib import *
d = K("xy-31", [600, 290, 300], {"or": "gloss#f07a26", "ord": "gloss#d8661f", "peg": "plastic#f0d690"})
A = 44                                   # board tilt (front edge low)
H = [300, 20, 286]                       # hinge at the front edge of the base
BR = rot("x", A, H)
# base plate, ratchet steps, prop leaf from the board's top edge down to the back of the base (tent shape)
L = 245                                   # board length along the slope
d.box("base", [0, 0, 0, 600, 20, 290], "or", r=3)
ca, sa = math.cos(math.radians(A)), math.sin(math.radians(A))
tz, ty = H[2] - L * ca, 20 + L * sa       # underside of the board's top edge
d.box("step", [25, 20, 40, 575, 32, 58], "ord", r=2, repeat=rep(3, [0, 0, 26]))
d.slab("prop", "side", poly([(4, 20), (26, 20), (tz + 12, ty - 4), (tz - 8, ty + 4)]), [14, 586], "or", r=2)
# inclined board with ribs across, rows of pegs perpendicular to it
d.box("board", [0, 20, H[2] - L, 600, 46, H[2]], "or", r=4, rot=BR)
# rounded ribs across the face between the rows of pegs (the photo's corrugated face)
d.cyl("rib", [10, 46, H[2] - L + 19], [590, 46, H[2] - L + 19], 18, "or", rot=BR, repeat={"n": 6, "step": [0, 0, 42], "local": True})
for nm, x, h in (("a", 45, 80), ("b", 128, 70), ("c", 211, 82), ("d", 300, 68), ("e", 389, 80), ("f", 472, 72), ("g", 555, 82)):
    d.cyl(f"peg-{nm}", [x, 40, H[2] - L + 40], [x, 46 + h, H[2] - L + 40], 25, "peg", rot=BR, repeat={"n": 5, "step": [0, 0, 42], "local": True})
d.save()
