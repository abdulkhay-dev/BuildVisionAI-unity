from k4lib import *
# size: printed 79 x 17 x 23 cm, but the photo shows the rods far taller than 23 cm: measured against the 790 base,
# the rod tops stand ~660 / 580 / 505 / 390 above the floor and the shapes are ~130 across -> H 660 (photo followed)
d = K("xy-36", [790, 170, 660], {"wood": "wood#e8b45e", "rod": "wood#b5703a", "red": "plastic#d8291f",
                                 "yel": "plastic#f2c418", "blue": "plastic#2147b8"})
# stepped base: bottom board, raised top board
d.box("base", [0, 0, 0, 790, 20, 170], "wood", r=3)
d.box("base-top", [30, 20, 30, 760, 40, 140], "wood", r=3)
d.box("groove", [30, 39.6, 82, 760, 40.4, 88], "wood#b88d58", soft=True)
X = [126, 310, 490, 656]
for i, (x, top) in enumerate(zip(X, [660, 580, 505, 390])):
    d.cyl(f"rod{i}", [x, 38, 85], [x, top, 85], 20, "rod")
    d.sphere(f"rod-top{i}", [x, top - 1, 85], 19, "rod")
# coloured shapes: red disc (2 layers) on rod 1, yellow square on rod 2, blue triangle on rod 4
d.cyl("red-a", [126, 40, 85], [126, 54, 85], 132, "red")
d.cyl("red-b", [130, 54, 83], [130, 68, 83], 128, "red")
d.box("yel-a", [248, 40, 23, 372, 54, 147], "yel", r=2)
d.box("yel-b", [250, 54, 25, 370, 68, 145], "yel", r=2, rot=rot("y", 7, [310, 61, 85]))
tri = poly([(712, 20), (712, 150), (585, 85)])
d.slab("blue-a", "top", tri, [40, 53], "blue", r=1)
d.slab("blue-b", "top", tri, [53, 66], "blue", r=1, rot=rot("y", -5, [656, 58, 85]))
d.save()
