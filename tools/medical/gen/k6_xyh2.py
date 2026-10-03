"""XYH-2 spring ankle exerciser: wooden base plate on black feet, two black footplates on chrome coil springs, a navy
hinge block in the middle, a thin chrome handspike rod with a black ball knob."""
from k6lib import *

W, DEP, H = 400, 250, 900
d = D("xyh-2", [W, DEP, H], {"wood": "wood#e8b860", "black": "rubber#26282b", "navy": "gloss#26388c",
                             "spring": "chrome"})
d.box("base", [0, 8, 0, W, 33, DEP], "wood", r=4)
d.cyl("foot", [25, 0, 25], [25, 8, 25], 22, "black", copies=[[W - 50, 0, 0], [0, 0, DEP - 50], [W - 50, 0, DEP - 50]])
YP = 140                       # underside of the footplates
# one big coil spring under the outer end of each plate (the plates hinge in the middle; the photo shows no second
# spring behind the front one)
for x in (80, W - 80):
    d.coil(f"spring{x}", [x, 33, DEP / 2], [x, YP, DEP / 2], 56, 6, 9, "spring")
    d.cyl(f"seat{x}", [x, 33, DEP / 2], [x, 38, DEP / 2], 60, "plastic#3a3d42")
d.cyl("sticker", [42, 33, DEP - 30], [42, 33.6, DEP - 30], 26, "plastic#f4f4f0", soft=True)
# footplates (black rubber with a raised outer toe lip), the centre plate between them
d.box("plate", [14, YP, 22, 172, YP + 30, DEP - 18], "black", r=10, mirror="x")
# raised toe tip at the outer back corner (photo), not a full-length lip
d.box("plate-lip", [14, YP + 22, 22, 40, YP + 50, 80], "black", r=8, mirror="x")
d.box("plate-tread", [50, YP + 30, 40, 160, YP + 32, DEP - 36], "rubber#33363a", r=1, mirror="x", soft=True)
d.box("centre", [168, YP + 4, 34, W - 168, YP + 28, DEP - 26], "black", r=8)
# navy hinge block (U bracket) under the centre, chrome bolt
d.box("hinge", [W / 2 - 38, 33, 85, W / 2 + 38, YP + 6, 175], "navy", r=4)
d.box("hinge-slot", [W / 2 - 20, 60, 174, W / 2 + 20, 130, 176], "plastic#16204f", r=2)
d.cyl("bolt", [W / 2 + 18, 120, 175], [W / 2 + 18, 120, 186], 18, "chrome")
# handspike rod and ball knob
d.cyl("rod", [W / 2, YP + 30, 90], [W / 2, H - 38, 90], 18, "chrome")
d.sphere("ball", [W / 2, H - 22, 90], 44, "plastic#1d1f22")
d.save()
