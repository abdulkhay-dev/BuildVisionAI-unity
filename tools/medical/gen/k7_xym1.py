"""xym-1 Gym rods and throwing balls, round rack. Size: the photo is a straight front view of the round rack, its
height/width ratio is 1.79 (printed 40×40×102 would be 2.55): W = D = 400 kept, H = 720 from the photo."""
import math
from k7lib import *

d = D("xym-1", [400, 400, 720], {
    "wood": "plastic#e8a02c", "wood2": "plastic#eeac40", "dark": "plastic#e39a28"})
C = (200, 200)
R = 199


def circle(cx, cz, r):
    return f"M {cx - r} {cz} A {r} {r} 0 1 0 {cx + r} {cz} A {r} {r} 0 1 0 {cx - r} {cz} Z"


def ring_outline(r0, r1):
    return circle(C[0], C[1], r1) + " " + circle(C[0], C[1], r0)


# --- round base and two ring shelves (annular boards)
d.slab("base", "top", circle(C[0], C[1], R), [0, 40], "dark", r=6)
d.slab("ring-mid", "top", ring_outline(150, R - 4), [236, 260], "wood", r=4)
d.slab("ring-top", "top", ring_outline(150, R - 4), [458, 484], "wood", r=4)
# --- back half: curved solid wall (half annulus extruded up), lower rounded ends at the two front edges
def arc_band(a0, a1, r0, r1, n=12):
    pts = [(C[0] + r1 * math.cos(math.radians(a0 + (a1 - a0) * k / n)), C[1] + r1 * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
    pts += [(C[0] + r0 * math.cos(math.radians(a1 - (a1 - a0) * k / n)), C[1] + r0 * math.sin(math.radians(a1 - (a1 - a0) * k / n))) for k in range(n + 1)]
    return "M " + " L ".join(f"{x:.1f} {z:.1f}" for x, z in pts) + " Z"
d.slab("wall", "top", arc_band(190, 350, R - 14, R - 2, 24), [40, 545], "wood2", r=5)
d.slab("wall-end-l", "top", arc_band(178, 190.5, R - 14, R - 2, 3), [40, 525], "wood2", r=6)
d.slab("wall-end-r", "top", arc_band(349.5, 362, R - 14, R - 2, 3), [40, 525], "wood2", r=6)
# --- 5 round gym rods standing in the front half of the rings
for k, dx in enumerate((-138, -69, 0, 69, 138)):
    z = C[1] + math.sqrt(176 ** 2 - dx ** 2)
    d.cyl(f"rod-{k}", [C[0] + dx, 30, z], [C[0] + dx, 718, z], 25, "wood")
    d.sphere(f"rod-end-{k}", [C[0] + dx, 707, z], 25, "wood")
# --- felt balls with coloured patches (patch = smaller sphere poking out of the ball)
cols = {"r": "fabric#d8362a", "o": "fabric#e8641c", "y": "fabric#f2d23a", "g": "fabric#5aa83a"}
balls = [((138, 130, 205), "r", "g"), ((258, 132, 215), "r", "yg"), ((168, 300, 215), "o", "gy"),
         ((250, 330, 185), "o", "y"), ((205, 530, 200), "o", "gy")]
BR = 88
for i, (c, base, patches) in enumerate(balls):
    d.sphere(f"ball-{i}", list(c), BR * 2, cols[base])
    dirs = [(-0.5, 0.55, 0.67), (0.6, -0.2, 0.77), (0.1, -0.8, 0.6)]
    for j, p in enumerate(patches):
        u = dirs[(i + j) % 3]; L = math.sqrt(sum(v * v for v in u)); u = [v / L for v in u]
        d.sphere(f"ball-{i}-p{j}", [c[0] + u[0] * BR * 0.2, c[1] + u[1] * BR * 0.2, c[2] + u[2] * BR * 0.2], BR * 1.7,
                 cols[p])
d.save()
