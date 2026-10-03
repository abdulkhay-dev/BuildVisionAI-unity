from k4lib import *
d = K("xy-39", [2000, 1300, 1690], {"frame": "metal#c8b88a", "wire": "metal#d6cdab", "rope": "plastic#b9bbbd",
                                    "sling": "leather#3d4c5a", "green": "gloss#22a447", "hook": "metal#9a9ea4"})
YM = 1220                                    # height of the horizontal net
# Photo read (camera low at the left, below the net): the wall net spans the whole width under the net's back edge;
# at each end an A-shaped side truss rises above the net (apex ~470 above it, ~60 % of the depth from the front):
# a leg to the net's front corner and a long strut from the apex down through the net to the wall post at ~700;
# a ridge rail joins the two apexes. No wall rail at the top.
for x in (20, 1980):
    d.bar(f"wall-post-{x}", [x, 200, 20], [x, 1690, 20], [40, 40], "frame", r=2)
    d.bar(f"wall-clamp-{x}", [x, 1640, 0], [x, 1640, 90], [44, 30], "frame", r=2)
# --- horizontal net: angle-bar frame, middle bars, wire mesh
d.box("net-back", [0, YM - 20, 0, 2000, YM + 20, 40], "frame", r=2)
d.box("net-front", [0, YM - 20, 1260, 2000, YM + 20, 1300], "frame", r=2)
d.box("net-side", [0, YM - 20, 40, 40, YM + 20, 1260], "frame", r=2, mirror="x")
d.box("net-mid-z", [980, YM - 18, 40, 1020, YM + 18, 1260], "frame", r=2)
d.box("net-mid-x", [40, YM - 18, 630, 1960, YM + 18, 670], "frame", r=2)
mesh(d, "net", 40, 1960, 40, 1260, YM, 100, 4, "wire")
# --- A-shaped end trusses, ridge rail, middle hanger truss
AZ, AY = 560, 1675
for x in (30, 1970):
    d.bar(f"leg-front-{x}", [x, AY, AZ], [x, YM + 15, 1280], [40, 30], "frame", r=2)
    d.bar(f"strut-{x}", [x, AY, AZ], [x, 700, 30], [40, 30], "frame", r=2)
    d.bar(f"leg-back-{x}", [x, AY - 60, AZ - 20], [x, YM + 15, 30], [30, 26], "frame", r=2)
d.bar("ridge", [0, AY, AZ], [2000, AY, AZ], [40, 40], "frame", r=2)
d.bar("mid-hanger", [1000, AY - 20, AZ], [1000, YM + 18, AZ], [30, 30], "frame", r=2)
# --- vertical wall net (right part) with its frame
X0, X1, Y0, Y1 = 60, 1940, 230, YM - 30          # full width under the net (photo)
d.box("wall-net-frame", [X0 - 20, Y0 - 20, 10, X1 + 20, Y0 + 15, 40], "frame", r=2, copies=[[0, Y1 - Y0 + 5, 0]])
d.box("wall-net-side", [X0 - 20, Y0, 10, X0 + 15, Y1, 40], "frame", r=2, copies=[[X1 - X0 + 5, 0, 0]])
d.box("wall-net-tab", [X0 - 40, 820, 8, X0 - 18, 860, 40], "frame", r=2, copies=[[X1 - X0 + 58, 0, 0], [0, -330, 0], [X1 - X0 + 58, -330, 0]])
d.box("wall-net-mid", [990, Y0, 10, 1010, Y1, 40], "frame", r=2)
vmesh(d, "wall-net", X0, X1, Y0, Y1, 26, 100, 4, "wire")
# --- S-hooks, ropes, slings on triangular hangers, green stirrups
def hang(id, x, z, ybot, kind):
    d.tube(f"{id}-s", [[x, YM - 5, z], [x + 12, YM - 25, z], [x, YM - 45, z], [x - 12, YM - 65, z], [x, YM - 80, z]], 5, "hook", bend=8, soft=True)
    if kind == "sling":
        top = ybot + 430
        d.cyl(f"{id}-rope", [x, YM - 80, z], [x, top + 70, z], 6, "rope", soft=True)
        d.tube(f"{id}-hanger", [[x, top + 75, z], [x - 75, top + 5, z], [x + 75, top + 5, z], [x, top + 75, z]], 7, "hook", bend=6)
        d.box(f"{id}-pad", [x - 70, ybot, z - 22, x + 70, top, z + 22], "sling", r=12, puff=5)
        d.box(f"{id}-loop", [x - 72, top - 30, z - 24, x + 72, top + 6, z + 24], "fabric#2b3640", r=6)
    else:
        d.cyl(f"{id}-rope", [x, YM - 80, z], [x, ybot + 95, z], 6, "rope", soft=True)
        d.tube(f"{id}-d", [[x, ybot + 95, z], [x - 45, ybot + 60, z], [x - 45, ybot, z], [x + 45, ybot, z], [x + 45, ybot + 60, z], [x, ybot + 95, z]],
               14, "green", bend=18)
        d.cyl(f"{id}-grip", [x - 45, ybot, z], [x + 45, ybot, z], 26, "green")
hang("sl1", 500, 1150, 120, "sling")
hang("sl2", 1170, 1050, 10, "sling")
hang("sl3", 1440, 800, 260, "sling")
hang("st1", 920, 900, 400, "stirrup")
hang("st2", 1700, 600, 480, "stirrup")
d.save()
