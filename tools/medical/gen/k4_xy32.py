from k4lib import *
d = K("xy-32", [280, 280, 470], {"wood": "wood#d9a05a", "edge": "wood#deae6c", "white": "plastic#f4f2ec"})
C = 140
# stepped base: 3 white discs with light-wood edges
for i, (dd, y0) in enumerate(((280, 0), (200, 10), (124, 20))):   # thin discs (photo)
    d.cyl(f"disc{i}", [C, y0, C], [C, y0 + 10, C], dd, "edge")
    d.cyl(f"disc{i}-top", [C, y0 + 1, C], [C, y0 + 10.6, C], dd - 5, "white")
# pole and short pegs in different directions
d.cyl("pole", [C, 30, C], [C, 470, C], 32, "wood")      # pole/base ratio as in the photo
d.sphere("pole-top", [C, 468, C], 30, "wood")
for i, (y, a) in enumerate(((95, 90), (215, 150), (232, 20), (292, 205), (300, -15), (412, 190), (455, 70))):
    ux, uz = math.cos(math.radians(a)), math.sin(math.radians(a))
    d.cyl(f"peg{i}", [C + 12 * ux, y, C + 12 * uz], [C + 88 * ux, y, C + 88 * uz], 15, "wood")
# white card target with a wooden edge slipped on the pole, tilted
# white card target (~180 x 150) with a wooden edge, slipped on the pole near its back edge, tilted 30 deg
# (front edge low); a second round cut-out at a back corner (photo). Top-plane outline coords are (x, z).
CR = rot("x", 30, [C, 400, C])
def card_o(m):
    return (poly([(C - 90 + m, C + 105 - m), (C + 90 - m, C + 105 - m), (C + 90 - m, C - 45 + m), (C - 90 + m, C - 45 + m)])
            + " " + circle(C, C, 19 - m) + " " + circle(C - 62, C - 22, 11 - m))
d.slab("card-edge", "top", card_o(0), [396, 399], "edge", r=1, rot=CR)
d.slab("card", "top", card_o(2.5), [399, 401.5], "white", r=1, rot=CR)
d.save()
