"""sound-amplifier: black karaoke amplifier with blue-lit VU dials, and its two black SAST speakers beside it."""
from s2lib import *

# Layout as the catalogue picture: the two speakers stand above the amplifier. The composite is to one scale (the
# right speaker's front is 140 x 112 px against the amp's 305 px = 430 mm), so each speaker is ≈ 205 x 160 and the
# pair stands side by side on the amp; the set keeps the amplifier's footprint (430 x 330).
SW, SH, SD = 205, 160, 150        # speaker (landscape, as in the photo)
AW, AH, AD = 430, 165, 330        # amplifier
G = 20
W, Dp, H = AW, AD, AH + SH
d = D("sound-amplifier", [W, Dp, H], {
    "body": "black#151619", "panel": "gloss#0a0a0c", "strip": "metal#5a5e66", "gold": "gloss#b48c3c",
    "blue": "gloss#2a78ff", "mesh": "black#26272b", "silver": "metal#c4c8cd", "knob": "black#0e0e10"})
# ---------------- speakers on the amplifier, fronts 10 mm behind its front
for k, x0 in enumerate((0, W - SW)):
    z0, z1 = Dp - 10 - SD, Dp - 10
    y0 = AH
    d.box(f"spk{k}", [x0, y0, z0, x0 + SW, y0 + SH, z1], "body", r=6)
    d.box(f"spk{k}-mesh", [x0 + 6, y0 + 6, z1 - 2, x0 + SW - 6, y0 + SH - 6, z1 + 1.5], "mesh", r=3)
    fr = (f"M {x0+8} {y0+8} L {x0+SW-8} {y0+8} L {x0+SW-8} {y0+SH-8} L {x0+8} {y0+SH-8} Z "
          f"M {x0+10} {y0+10} L {x0+SW-10} {y0+10} L {x0+SW-10} {y0+SH-10} L {x0+10} {y0+SH-10} Z")
    d.slab(f"spk{k}-frame", "front", fr, [z1 + 0.5, z1 + 2], "silver", r=0.3, soft=True)
    tl = text_len("SAST", 20, gap=0.2)
    text(d, f"spk{k}-logo", "SAST", [x0 + SW / 2 - tl / 2 + 6, y0 + SH / 2 - 8, z1 + 2.2], 20, "silver", stroke=4.5, gap=0.2)
    d.cyl(f"spk{k}-screw", [x0 + 0.31 * SW, y0 + SH - 2, z0 + 70], [x0 + 0.31 * SW, y0 + SH, z0 + 70], 7, "chrome",
          copies=[[0.38 * SW, 0, 0]], soft=True)
    d.cyl(f"spk{k}-foot", [x0 + 25, y0 - 0.1, z0 + 25], [x0 + 25, y0 + 1, z0 + 25], 16, "rubber", soft=True,
          copies=[[SW - 50, 0, 0], [0, 0, SD - 50], [SW - 50, 0, SD - 50]])
d.cyl("spk1-port", [W - 24, AH + 26, Dp - 10 + 1], [W - 24, AH + 26, Dp - 10 + 3], 22, "black#08080a", soft=True)
# ---------------- amplifier
ax = 0
d.box("amp", [ax, 8, 0, ax + AW, AH, AD], "body", r=4)
d.cyl("amp-foot", [ax + 30, 0, 30], [ax + 30, 8, 30], 26, "rubber", copies=[[AW - 60, 0, 0], [0, 0, AD - 60], [AW - 60, 0, AD - 60]])
F = AD
d.box("amp-panel", [ax + 4, 66, F - 2, ax + AW - 4, AH - 3, F + 2], "panel", r=3)
fr = (f"M {ax+10} 71 L {ax+AW-10} 71 L {ax+AW-10} {AH-8} L {ax+10} {AH-8} Z "
      f"M {ax+12} 73 L {ax+AW-12} 73 L {ax+AW-12} {AH-10} L {ax+12} {AH-10} Z")
d.slab("amp-frame", "front", fr, [F + 2, F + 3], "gold", r=0.3, soft=True)
# VU meters: upright ovals (≈ 68 x 86) — a glowing blue ring round a grey face, gold tick marks round it
for k, cx in enumerate((ax + 52, ax + 378)):
    for nm, (w_, h_, z_, m_) in (("glow", (66, 84, 2.0, "gloss#7ab4ff")), ("ring", (62, 80, 2.6, "blue")),
                                 ("face", (44, 60, 3.4, "black#4a4e56"))):
        d.add(f"vu{k}-{nm}", "loft", m_, axis="z", soft=nm != "ring", sections=[
            sec(F + 1, w_, h_, w_ / 2, cx, 112), sec(F + z_, w_, h_, w_ / 2, cx, 112)])
    d.sphere(f"vu{k}-hub", [cx, 112, F + 3.4], 10, "black#62666e", soft=True)
    d.decal(f"vu{k}-ticks", [cx, 157, F + 2.2], [50, 2.5], "front", "gold", soft=True)
for k, bx in enumerate((ax + 98, ax + 322)):
    d.box(f"bbtn{k}", [bx - 9, 128, F + 1, bx + 9, 150, F + 5], "blue", r=4, copies=[[0, -42, 0]])
# display digits (red and blue) and the gold label
text(d, "disp-a", "18", [ax + 112, 101, F + 2.5], 16, "gloss#e8303a", stroke=2.6)
text(d, "disp-b", "8", [ax + 180, 101, F + 2.5], 16, "gloss#e8303a", stroke=2.6)
text(d, "disp-c", "88", [ax + 212, 101, F + 2.5], 16, "gloss#3a8cff", stroke=2.6)
text(d, "disp-d", "8", [ax + 256, 101, F + 2.5], 16, "gloss#c8d0d8", stroke=2.6)
d.decal("label", [ax + 171, 151, F + 2.6], [34, 6], "front", "gold", soft=True)
d.decal("label2", [ax + 215, 78, F + 2.6], [190, 3], "front", "gold", soft=True)
# lower control strip: 5 knobs, mic jacks, USB and SD slots
d.box("amp-strip", [ax + 4, 12, F - 2, ax + AW - 4, 63, F + 1], "strip", r=2)
for k, kx in enumerate((18, 124, 162, 200, 236)):
    d.lathe(f"knob{k}", [ax + kx, 34, F + 1], [[0, 0], [11, 0], [11, 14], [9, 17], [0, 18]], "knob", axis="z")
d.box("jacks", [ax + 50, 24, F + 1, ax + 106, 46, F + 3], "black#1b1c1f", r=3)
d.cyl("jack", [ax + 65, 35, F + 3], [ax + 65, 35, F + 4], 12, "chrome", copies=[[26, 0, 0]], soft=True)
d.box("media", [ax + 270, 22, F + 1, ax + 370, 48, F + 2.5], "black#1b1c1f", r=4)
d.box("usb", [ax + 282, 30, F + 2, ax + 300, 37, F + 3.2], "silver", soft=True)
d.box("sd", [ax + 318, 33, F + 2, ax + 358, 36, F + 3.2], "black#050506", soft=True)
d.decal("strip-txt", [ax + 150, 55, F + 1.6], [250, 2.5], "front", "silver", soft=True)
# side vent (right side of the amplifier)
d.box("vent", [ax + AW - 0.5, 98, 250, ax + AW + 1, 104, 256], "black#050506", soft=True,
      copies=[[0, j * 10, i * 10] for i in range(5) for j in range(5) if (i, j) != (0, 0)])
d.save()
