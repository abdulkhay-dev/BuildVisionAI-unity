"""XY-JZJ-II smart posture mirror pro: wide black mirror panel with a portrait touch screen, white pedestal with a
vent grille, X base of flat arms (white top skin over dark grey) on 4 twin castors."""
from k9lib import *
d = K("xy-jzj-ii", [1050, 800, 1950], {
    "glass": "gloss#18191c", "body": "plastic#141517", "white": "plastic#eceeef", "grey": "plastic#4a4d52",
    "dot": "black#050505"})
CX, CZ = 525, 400
PW, PB, PT = 830, 370, 1950     # (review) panel 830 x 1580: the photo's 1 : 1.9
Z0, Z1 = 372, 428
x0, x1 = CX - PW / 2, CX + PW / 2
d.box("panel", [x0, PB, Z0, x1, PT, Z1 - 5], "body", r=6)
d.box("glass", [x0 + 1, PB + 1, Z1 - 7, x1 - 1, PT - 1, Z1], "glass", r=2)
SW, SH, ST = 615, 1185, PT - 95
crop_screen(d, "screen", "dot", "med_xy-jzj-ii_screen", [CX - SW / 2, ST - SH, CX + SW / 2, ST], Z1 + 2, (441, 800),
            (12, 16, 418, 800), "glass", outer=[x0 + 1, PB + 1, x1 - 1, PT - 1])
d.decal("sensor", [CX, ST - SH - 45, Z1 + 6.2], [11, 11], "front", "plastic#3a3c40")
d.box("back-plate", [CX - 220, PB + 60, Z0 - 25, CX + 220, PB + 700, Z0 + 2], "body", r=10)
# pedestal: white rounded box with a vertical-slot vent, dark band at its foot
# (review) the photo's base stands higher (castors ~90, arms ~60 thick), so less of the white pedestal shows
d.box("ped", [CX - 220, 190, CZ - 85, CX + 220, PB + 20, CZ + 85], "white", r=40)
d.box("ped-band", [CX - 228, 178, CZ - 93, CX + 228, 205, CZ + 93], "grey", r=36)
d.box("vent", [CX - 70, 240, CZ + 84, CX - 64, 300, CZ + 87], "body", r=2, repeat=rep(9, [16, 0, 0]))
# X base: flat arms, dark grey body with a white top skin, castors under the arm ends
ARM = [(-480, -330), (480, -330), (480, 330), (-480, 330)]
def xshape(inset):
    w = 72 - inset
    # X outline as a polygon: centre square + 4 arms (each arm a parallelogram towards its corner)
    import math
    out = []
    corners = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    for k, (sx, sz) in enumerate(corners):
        ex, ez = CX + sx * (480 - inset), CZ + sz * (330 - inset)
        L = math.hypot(480, 330); ux, uz = sx * 480 / L, sz * 330 / L      # arm direction
        nx, nz = -uz, ux                                                      # normal
        out.append((ex - nx * w, ez - nz * w))
        out.append((ex + nx * w, ez + nz * w))
        # inner corner between this arm and the next
        sx2, sz2 = corners[(k + 1) % 4]
        mx, mz = (sx + sx2) / 2, (sz + sz2) / 2
        out.append((CX + mx * (170 - inset) , CZ + mz * (120 - inset)))
    return rpoly(out, 40)
d.slab("base", "top", xshape(0), [115, 172], "grey", r=10)
d.slab("base-top", "top", xshape(8), [170, 179], "white", r=4)
d.decal("base-logo", [CX, 179.6, CZ + 175], [90, 16], "top", "plastic#d9534f")
for k, (sx, sz) in enumerate([(1, 1), (-1, 1), (-1, -1), (1, -1)]):
    d.caster(f"castor-{k}", [CX + sx * 440, 0, CZ + sz * 300], 90, "rubber#8c9096")
d.save()
