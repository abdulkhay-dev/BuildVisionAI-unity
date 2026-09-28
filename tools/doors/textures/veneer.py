#!/usr/bin/env python3
"""Door finishes "Шпон натуральный" (Mr.Wood: WOOD FLAT / MODERN / CLASSIC) - real oak veneer: Natur Oak, Golden
Oak (stained dark), and Ivory / Latte / Whitey (the veneer under an opaque-ish paint whose open pores still show).

    python3 tools/doors/textures/veneer.py [ids] [--compare] [--no-write] [--fit] [--analyze]

The catalogue (pages 82-91) shows rift-cut oak: straight rings with visible pore lines, broad soft bands with a gentle
flame-like wander, lighter streaks (strong on Golden Oak) and no cathedrals or knots; the "H" doors lay the same
veneer across the leaf. Structure: finish_kit.oak_structure (growth rings with earlywood pore dashes, transition and
latewood, ray flecks, long streaks, broad bands); the pores are open (normal map). The painted colourways use the
same veneer with the wood's tone almost gone: paint settles in the pores, so they read as fine slightly darker dashes.
"""
import finish_kit as kit

PATTERNS = {
    "veneer": dict(
        seed=7202, warp=[(1.8, 350.0, 35.0), (0.35, 60.0, 5.0)],
        ring=(2.4, 0.5), ring_rho=0.65, early=(0.28, 0.07), trans=0.2,
        ring_tone=(-1.0, -0.35, 0.5), ring_var=0.45, drift=0.6, drift_len=40.0, hp=5.0,
        pores=dict(len=3.0, duty=0.6, alpha=0.85, late=0.2),
        rays=dict(per_cm=3.0, width=(0.8, 0.35), length=(5.0, 0.6), alpha=(0.25, 0.8), fade=0.3, slope=0.08),
        dark=dict(per_cm=0.3, width=(0.6, 0.4), length=(220.0, 0.8), alpha=(0.2, 0.8), fade=0.7, slope=0.003),
        light=dict(per_cm=0.35, width=(1.0, 0.45), length=(140.0, 0.8), alpha=(0.25, 0.9), fade=0.8, slope=0.003),
        fade_len=20.0, bands=(20.0, 700.0), cluster=(4.0, 140.0), cluster_share=0.5, band_warp=(6.0, 300.0, 45.0),
        fibre=(0.5, 2.0), fibre_share=0.25,
        relief=dict(pore=1.0, ring=0.25, fibre=0.25, tilt_deg=3.0),
    ),
}


def veneer(scale=1.0, seed=None):
    return kit.oak_structure(PATTERNS["veneer"], scale, seed)


# color: catalogue mean (sRGB, linear-light mean of the REFS); dark / light: full-strength streak colours (the ground
# tone goes towards them); pore / fleck: pore and ray colours at strength pore_k / fleck_k; comb / tone: L* std of the
# fine lines / broad bands (--fit); smooth: satin lacquer / paint; tilt: rms tilt of the open pores (deg).
FINISHES = [
    dict(id="natur-oak", material="door_natur_oak", name="Natur Oak", pattern="veneer",
         color="#a6772f", dark="#7a4d12", light="#c6974e", pore="#6f4312", fleck="#cb9d53",
         comb=2.77, tone=2.20, pore_k=0.6, fleck_k=0.5, smooth=0.40),
    dict(id="golden-oak", material="door_golden_oak", name="Golden Oak", pattern="veneer",
         color="#513726", dark="#3a2110", light="#6d5342", pore="#361d0a", fleck="#725847",
         comb=3.64, tone=1.49, pore_k=0.6, fleck_k=0.5, smooth=0.40),
    dict(id="veneer-ivory", material="door_veneer_ivory", name="Ivory", pattern="veneer",
         color="#ebe4d1", dark="#cfc8b5", light="#f4edda", pore="#c9c2b0", fleck="#f4edda",
         comb=0.25, tone=0.29, pore_k=0.35, fleck_k=0.0, dark_k=0.0, light_k=0.0, smooth=0.40, tilt=3.5),
    dict(id="veneer-latte", material="door_veneer_latte", name="Latte", pattern="veneer",
         color="#d0bfb1", dark="#b5a496", light="#dbcabc", pore="#ad9c8e", fleck="#dbcabc",
         comb=0.20, tone=0.25, pore_k=0.30, fleck_k=0.0, dark_k=0.0, light_k=0.0, smooth=0.40, tilt=3.5),
    dict(id="veneer-whitey", material="door_veneer_whitey", name="Whitey", pattern="veneer",
         color="#f9f5f2", dark="#e2dedb", light="#fffbf8", pore="#dcd9d6", fleck="#fffbf8",
         comb=0.15, tone=0.15, pore_k=0.25, fleck_k=0.0, dark_k=0.0, light_k=0.0, smooth=0.40, tilt=3.5),
]

# (file, box[, "rot" = grain horizontal in the photo: the "H" doors])
REFS = {
    "natur-oak": [
        ("p084_vud-flet-0v1__natur-oak-v.jpg", (110, 40, 338, 790)),
        ("p083_vud-flet-0v1__natur-oak-h.jpg", (110, 40, 338, 790), "rot"),
        ("p084_vud-flet-0v1__natur-oak-v.jpg", (31, 40, 100, 400)),
        ("p085_vud-flet-1v1__natur-oak.jpg", (31, 40, 75, 400)),
    ],
    "golden-oak": [
        ("p086_vud-modern-22-bs__golden-oak.jpg", (300, 40, 339, 790)),
        ("p086_vud-modern-22-bs__golden-oak.jpg", (34, 40, 74, 400)),
        ("p084_vud-flet-0v1__golden-oak-v.jpg", (45, 15, 136, 330)),
        ("p083_vud-flet-0v1__golden-oak-h.jpg", (45, 15, 136, 330), "rot"),
    ],
    "veneer-ivory": [
        ("p084_vud-flet-0v1__ivory-v.jpg", (110, 40, 338, 790)),
        ("p083_vud-flet-0v1__ivory-h.jpg", (110, 40, 338, 790), "rot"),
    ],
    "veneer-latte": [
        ("p085_vud-modern-21__latte.jpg", (302, 40, 341, 790)),
        ("p087_vud-modern-23-mf__latte.jpg", (302, 40, 341, 790)),
        ("p084_vud-flet-0-v__latte.jpg", (45, 15, 136, 330)),
        ("p083_vud-flet-0-h__latte.jpg", (45, 15, 136, 330), "rot"),
    ],
    "veneer-whitey": [
        ("p087_vud-modern-29-mf__whitey.jpg", (298, 40, 337, 790)),
        ("p084_vud-flet-0-v__whitey.jpg", (45, 15, 136, 330)),
        ("p083_vud-flet-0-h__whitey.jpg", (45, 15, 136, 330), "rot"),
    ],
}

FAMILY = dict(id="veneer", line="Шпон натуральный", suffix="шпон Mr.Wood", module="veneer.py",
              patterns={"veneer": veneer}, finishes=FINISHES, refs=REFS)

if __name__ == "__main__":
    kit.main(FAMILY)
