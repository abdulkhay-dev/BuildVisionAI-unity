"""XY-101C hand rehabilitation table (4 patients): white X base, silver column, round white top with a black edge,
aluminium tower with 4 screens (the front one with the interface picture), light-blue station bases with black rods
and grips, thin cables to pulleys at the tower foot. Station places and shapes follow the main leaflet photo
(review 2026-10-03): seen from the front-right, the wrist lever on the left, pegs back-left, a ball post behind,
the grip pair in front, the crank wheel front-right, an arch-stand ball post and the roller on the right, the cradle
stool back-right."""
from k9_handtable import *
d = K("xy-101c", [1300, 1300, 1540], {
    "base": "plastic#e9ebec", "drawer": "plastic#f3f4f5", "black": "plastic#17181a", "tabletop": "plastic#f4f4f2",
    "alu": "metal#cfd3d8", "plate": "plastic#8fb4e8", "rod": "plastic#1d1e21", "chrome": "chrome"})
body(d, "plate", "base", print_front="med_xy-101c_screen")
R_ = "rod"
wrist_st(d, "st-a", *polar(480, 157), 157, R_)
pegs(d, "st-b", *polar(440, 222), 222, R_, hs=[150, 185, 160], dia=30, bar_mat="rod", extra=(70, -70, 140))
post_ball(d, "st-c", *polar(440, 255), 255, R_, h=110, ball=62, post=36)
grip_pair(d, "st-d", *polar(480, 103), 103, R_)
wheel_st(d, "st-e", *polar(480, 57), 57, R_)
roller_st(d, "st-f", *polar(540, 354), 354, R_, length=280, dia=62)
post_ball(d, "st-k", *polar(530, 22), 22, R_, h=120, ball=70, post=40, stand="arch")
cradle_stool(d, "st-g", *polar(500, 318), 318, R_, strap="fabric#c9ccd0", dome="rod")
knob_post(d, "st-i", *polar(250, 172), 172, R_)
pegs(d, "st-j", *polar(440, 290), 290, R_, hs=[160, 140], dia=30, bar_mat="rod")
# forearm rest of the wrist station hanging over the table edge (photo: left), a black cable grip hanging by it
hx, hz = polar(660, 160)
s_ = St(d, "hang", hx, hz, 160)
d.box("hang-plate", [hx - 70, TT - 230, hz - 8, hx + 70, TT - 10, hz + 8], "plastic#e4e6e8", r=6, rot=rot("x", 18, [hx, TT, hz]))
d.decal("hang-slot", [hx, TT - 200, hz + 8.6], [50, 20], "front", "plastic#9a9ea3", rot=rot("x", 18, [hx, TT, hz]))
d.cyl("hang-cable", [hx, TT - 10, hz - 10], [hx, TT + 40, hz - 60], 8, "rod")
s_.done()
gx, gz = polar(665, 150)
d.tube("hang-cord", [[gx, TT + 5, gz], [gx + 8, TT - 60, gz + 12], [gx + 8, TT - 120, gz + 14]], 6, "rod", soft=True, bend=20)
d.sphere("hang-grip", [gx + 8, TT - 165, gz + 14], 40, "rod", radii=[18, 50, 18])
for k, a in enumerate((157, 222, 103, 57, 354, 318, 22, 290)):
    cable(d, f"cable-{k}", a)
# black oval grips on the cables and a small cable clip (photo)
for k, (r, a) in enumerate(((330, 168), (360, 205), (380, 40), (300, 80))):
    oval_grip(d, f"grip-{k}", *polar(r, a), a)
cx_, cz_ = polar(370, 74)
d.box("clip-blk", [cx_ - 18, TT, cz_ - 14, cx_ + 18, TT + 30, cz_ + 14], "plastic#eceeef", r=4)
d.wheel("clip-pul", [cx_, TT + 30, cz_ + 22], 40, "rod", d2=16, axis="z")
d.tube("clip-wire", [[cx_ + 15, TT + 25, cz_], [cx_ + 80, TT + 22, cz_ - 20], [cx_ + 120, TT + 22, cz_ - 40]], 4, "chrome", soft=True, bend=20)
d.save()
