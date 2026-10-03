"""xyj-6 Shoulder (finger) ladder (wall). The photo is a SIDE view (wall on the left): an aluminium rail on two white
wall brackets, a white slider block with two black knobs, and the ladder hanging in front of the slider: white back
strip with two columns of sawtooth steps, colour sections alternating green / red (checkerboard). 1.8 mm/px vertically."""
from k7lib import *

d = D("xyj-6", [150, 140, 1240], {
    "alu": "metal#b9b6a6", "white": "plastic#f1f2f0", "black": "plastic#1b1d1f",
    "green": "gloss#1e9a4c", "red": "gloss#d82a3a"})
# --- wall rail on white brackets
d.box("bracket-top", [52, 1192, 0, 98, 1240, 44], "white", r=6)
d.box("bracket-bot", [52, 28, 0, 98, 76, 44], "white", r=6)
d.box("rail", [60, 40, 18, 90, 1230, 46], "alu", r=3)
d.decal("rail-screw", [75, 1216, 44.6], [8, 8], "chrome", face="front", soft=True, copies=[[0, -1164, 0]])
# --- slider block (photo: ~270 tall, 420..690) with two black clamp knobs on the side the photo shows (-x), 220 apart
d.box("slider", [48, 425, 26, 102, 698, 70], "white", r=6)
d.lathe("slider-knob", [48, 672, 50], [[0, 0], [7, 0], [7, 6], [13, 8], [13, 20], [0, 22]], "black", axis="x",
        copies=[[0, -220, 0]], rot=rot("y", 180, [48, 672, 50]))
d.box("hanger", [40, 600, 60, 110, 680, 68], "white", r=3)
# --- ladder: white back strip, sawtooth steps in two columns; the columns' teeth are staggered by half a pitch
# (photo: the tips alternate green / red within a section) and their colours alternate per ~200 mm section
Y0, Y1, NS, NT = 40, 1060, 5, 5
SEC = (Y1 - Y0) / NS
PITCH = SEC / NT
ZB, ZT = 84, 137           # valley and tip z of the teeth
d.box("strip", [4, Y0 - 4, 62, 146, Y1 + 8, 82], "white", r=4)
d.slab("strip-top", "side", f"M 62 {Y1} L 140 {Y1} L 82 {Y1 + 32} L 62 {Y1 + 32} Z", [4, 146], "white", r=3)
cols = [(8, 74), (76, 142)]


def prof(y, phase):
    """z of the tooth surface at y: triangular wave, tips at phase (+ k*PITCH)."""
    t = ((y - Y0 - phase) / PITCH) % 1.0
    t = min(t, 1 - t) * 2           # 0 at a tip, 1 at a valley
    return ZT - (ZT - ZB) * t


for sct in range(NS):
    ys, ye = Y0 + sct * SEC, Y0 + (sct + 1) * SEC
    for c, (x0, x1) in enumerate(cols):
        phase = PITCH / 2 if c == 0 else 0.0
        ys_ = sorted(set([ys, ye] + [Y0 + phase + k * PITCH / 2 for k in range(-2, 2 * NS * NT + 3)
                                      if ys < Y0 + phase + k * PITCH / 2 < ye]))
        pts = [(82, ys)]
        for y in ys_:
            z = prof(y, phase)
            if z > ZT - 0.5 and ys < y < ye:     # small flat on the tip
                pts += [(ZT, y - 1.5), (ZT, y + 1.5)]
            else:
                pts += [(round(z, 1), y)]
        pts += [(82, ye)]
        outline = "M " + " L ".join(f"{z:.1f} {y:.1f}" for z, y in pts) + " Z"
        mat = "green" if (sct + c) % 2 == 0 else "red"
        d.slab(f"teeth-{sct}-{c}", "side", outline, [x0, x1], mat, r=1.5)
d.save()
