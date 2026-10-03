"""JY-CT-II hand rehabilitation table, pediatric: the XY-101C body (white X base with black arm caps, white column,
round white top) with a narrower, taller tower (4 large dark screens, a wide weight-stack window and a blue power
button on each face) and child-colour stations: light-blue frames and dusty-pink metallic rods and ball knobs, blue
padded saddles and forearm rest with black straps. Places and shapes follow the leaflet photo (review 2026-10-03,
seen from the front-right)."""
from k9_handtable import *
d = K("jy-ct-ii", [1300, 1300, 1540], {
    "base": "plastic#eceeef", "drawer": "plastic#f3f4f5", "black": "plastic#17181a", "tabletop": "plastic#f4f4f2",
    "alu": "metal#cfd3d8", "plate": "plastic#9cc3e6", "rod": "gloss#b8606c", "chrome": "chrome"})
# tower of the photo: ~300 wide, ~440 tall; screen 236 x 150 from 61 below the top; slot window 77 x 180
body(d, "plate", "black", button=True, colmat="plastic#eef0f1", tw=300, th=440, scr=(-112, 124, 211, 61),
     slot=(10, 10, 190, 77), btn=(93, 183), logo_cn=True)
R_ = "rod"
BL = "leather#9cc3e6"
cradle_stool(d, "st-a", *polar(520, 172), 172, R_, pad=BL)
post_ball(d, "st-b", *polar(450, 150), 150, R_, h=170, ball=60, post=40, stand="arch")
pegs(d, "st-c", *polar(420, 212), 212, R_, hs=[240, 260, 250], dia=36)
roller_st(d, "st-d", *polar(450, 118), 118, R_, length=300, dia=56, cy=120, ends=("cap", "dome"), thin=(20, 46))
cradle_stool(d, "st-e", *polar(400, 88), 88, R_, pad=BL)
lever_st(d, "st-f", *polar(270, 102), 102, R_)
wrist_st(d, "st-g", *polar(470, 335), 335, R_, piv=(230, 70), foot=-170, mid=(120, -60), cradle=False, loop="fabric#202124")
post_ball(d, "st-h", *polar(520, 2), 2, R_, h=190, ball=56, post=36, stand="cage")
forearm_pad(d, "st-i", *polar(470, 35), 35)
grip_pair(d, "st-j", *polar(430, 290), 290, R_)
lev2 = St(d, "st-l", *polar(330, 228), 228)
x_, z_ = polar(330, 228)
d.cyl("st-l-post", [x_, TT, z_], [x_, TT + 110, z_], 26, "plate")
d.box("st-l-clamp", [x_ - 30, TT + 100, z_ - 20, x_ + 30, TT + 125, z_ + 20], "chrome", r=6)
d.cyl("st-l-lever", [x_ - 20, TT + 115, z_], [x_ - 150, TT + 125, z_ + 20], 30, "rod")
lev2.done()
for k, a in enumerate((172, 150, 212, 118, 335, 2, 35, 290)):
    cable(d, f"cable-{k}", a)
for k, (r, a) in enumerate(((360, 140), (330, 125), (380, 20), (300, 60))):
    oval_grip(d, f"grip-{k}", *polar(r, a), a)
d.save()
