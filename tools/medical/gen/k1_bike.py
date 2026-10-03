"""upright-exercise-bike: generic upright bike (seen in the XY-K-M2 photo behind a harness). Front = handlebar end (z max)."""
from k1lib import *

d = D("upright-exercise-bike", [550, 1000, 1350], {
    "silver": "plastic#b8bcc2", "black": "plastic#1d1e20", "grey": "plastic#6c7077", "rubber": "rubber#1a1b1d",
    "seat": "leather#1c1d1f"})
CX = 275
# --- stabilizer feet front and rear (oval tubes along x) with levelling caps
for nm, z in (("rear", 110), ("front", 890)):
    d.sweep(f"foot-{nm}", [[25, 45, z], [525, 45, z]], [60, 50], "black", shape="oval")
    d.sphere(f"foot-cap-{nm}", [30, 30, z], None, "grey", radii=[30, 30, 32], mirror="x")
# --- frame tubes to the housing
d.sweep("frame-rear", [[CX, 60, 120], [CX, 140, 220], [CX, 220, 320]], [70, 50], "black", shape="oval", bend=80)
d.sweep("frame-front", [[CX, 120, 640], [CX, 70, 780], [CX, 60, 880]], [70, 50], "black", shape="oval", bend=80)
# --- silver flywheel housing, darker centre band and vents
# photo: the silver housing is tall (~600) and fairly wide (~220)
hous = "M 290 95 L 650 95 Q 700 95 695 150 L 650 535 Q 635 595 570 595 L 370 595 Q 300 595 290 525 Z"
d.slab("housing", "side", hous, [165, 385], "silver", r=45)
d.slab("housing-band", "side", hous, [270, 280], "grey", r=4)
d.lathe("flywheel-cap", [CX - 111, 300, 470], [[0, 0], [70, 0], [70, 4], [0, 4]], "grey", axis="x",
        rot=rot("y", 180, [CX - 111, 300, 470]))
d.lathe("flywheel-cap-r", [CX + 111, 300, 470], [[0, 0], [70, 0], [70, 4], [0, 4]], "grey", axis="x")
# --- pedal cranks (180 deg) and pedals with straps
for s, dy, dz in ((-1, -150, 80), (1, 150, -80)):
    x = CX + s * 122
    d.bar(f"crank-{s}", [x, 300, 470], [x, 300 + dy, 470 + dz], [30, 14], "black", r=4)
    px = CX + s * 172
    d.cyl(f"pedal-axle-{s}", [x, 300 + dy, 470 + dz], [px, 300 + dy, 470 + dz], 16, "black")
    d.box(f"pedal-{s}", [px - 50, 285 + dy, 410 + dz, px + 50, 312 + dy, 530 + dz], "black", r=6)
    d.strap(f"pedal-strap-{s}", [[px - 52, 312 + dy, 440 + dz], [px, 360 + dy, 450 + dz], [px + 52, 312 + dy, 440 + dz]],
            [36, 3], "black", bend=30, soft=True)
# --- front stem, small console, handlebar horns
d.sweep("stem", [[CX, 470, 610], [CX, 800, 690], [CX, 1080, 760]], [64, 48], "black", shape="oval", bend=150)
d.box("console", [CX - 70, 1090, 700, CX + 70, 1160, 780], "black", r=12, rot=rot("x", 30, [CX, 1120, 740]))
d.decal("console-lcd", [CX, 1161, 740], [90, 40], "top", "plastic#5f6b62", soft=True, rot=rot("x", 30, [CX, 1120, 740]))
d.tube("handlebar", [[CX - 210, 1300, 930], [CX - 210, 1110, 900], [CX - 200, 1075, 790], [CX, 1075, 765],
                     [CX + 200, 1075, 790], [CX + 210, 1110, 900], [CX + 210, 1300, 930]], 32, "black", bend=70)
d.cyl("grip", [CX - 210, 1160, 912], [CX - 210, 1300, 930], 38, "rubber", mirror="x")
# --- seat post leaning back, saddle
d.sweep("seat-tube", [[CX, 480, 340], [CX, 700, 290], [CX, 880, 250]], [60, 46], "black", shape="oval", bend=100)
d.cyl("seat-knob", [CX - 30, 600, 315], [CX - 70, 600, 315], 30, "black")
saddle = (f"M {CX - 85} 140 Q {CX - 85} 105 {CX} 105 Q {CX + 85} 105 {CX + 85} 140 L {CX + 75} 230 "
          f"Q {CX + 30} 300 {CX + 22} 400 L {CX - 22} 400 Q {CX - 30} 300 {CX - 75} 230 Z")
d.slab("saddle", "top", saddle, [880, 940], "seat", r=18)
d.box("saddle-rail", [CX - 25, 860, 200, CX + 25, 882, 320], "black", r=6)
d.save()
