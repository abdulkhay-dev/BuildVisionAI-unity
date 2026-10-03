from pd1_lib import *
W, D_, H = 850, 200, 1680
d = K("xyrt-11", [W, D_, H], {"oak": "wood#c8883e", "rung": "wood#c07a38", "white": "plastic#f2f2f0", "steel": "metal#e8e8e8"})
RW, RD = 60, 45                 # rail section (x across, z deep)
zc = D_ - RD / 2                # rails at the front, the brackets reach back to the wall (z = 0)
xl, xr = 20 + RW / 2, W - 20 - RW / 2
# one bent rail: up the left, over the arch, down the right
d.add("rail", "sweep", "oak", path=[[xl, 0, zc], [xl, H - RW / 2, zc], [xr, H - RW / 2, zc], [xr, 0, zc]],
      section=[RW, RD], shape="rect", r=3, bend=230)
ys = [221, 363, 513, 664, 814, 965, 1115, 1274, 1425]
for i, y in enumerate(ys):
    end = i in (0, len(ys) - 1)                  # top and bottom rungs white and thicker, the rest thin oak
    d.cyl(f"rung{i}", [xl - 10, y, zc], [xr + 10, y, zc], 32 if end else 25, "white" if end else "rung")
# wall brackets: a white flat bar on the outer side of each rail, turned in to a wall flange
d.box("br-l", [12, 1440, 6, 20, 1490, zc + 12], "white", r=1, mirror="x")
d.box("brw-l", [0, 1440, 0, 20, 1490, 6], "white", r=1, mirror="x")
d.save()
