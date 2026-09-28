#!/usr/bin/env python3
"""Door finishes of the line "ПВХ" (catalogue pp. 76-79, swatches p. 76): PVC film pressed on MDF - white, Shimo ash
(light, dark), Italian and Milan walnut (П-17 / П-18 and the SKINNY series' П-31 / П-32); a fine emboss, satin-matt.

    python3 tools/doors/textures/pvc.py [ids] [--compare] [--no-write] [--fit] [--slopes]

See tools/doors/textures/grain.py for the structures, the colour model and the outputs.
"""
import grain

FAMILY = "pvc"
LINE = "ПВХ"
SOURCE = "procedural:tools/doors/textures/pvc.py"

# as laminate.py; seed = another print of the pattern (П-31 / П-32 are other films than П-17 / П-18)
FINISHES = [
    dict(id="p-23-white", material="door_p_23_white", name="П-23 Белый", tag="ПВХ",
         pattern="film", color="#e3e3e2", dark="#dadada", light="#e8e8e7", comb=0.2, tone=0.3, smooth=0.42),
    dict(id="p-34-shimo-light", material="door_p_34_shimo_light", name="П-34 Шимо Светлый", tag="ПВХ",
         pattern="shimo", color="#c7b8a0", dark="#968675", light="#e2d2b7", comb=1.6, tone=2.4, smooth=0.42),
    dict(id="p-35-shimo-dark", material="door_p_35_shimo_dark", name="П-35 Шимо Тёмный", tag="ПВХ",
         pattern="shimo", seed=1402, color="#9c735f", dark="#754a36", light="#b8937e", comb=1.8, tone=3.0,
         smooth=0.42),
    dict(id="p-17-italoreh", material="door_p_17_italoreh", name="П-17 ИталОрех", tag="ПВХ",
         pattern="ital", seed=1102, color="#7b3620", dark="#621c0e", light="#945134", comb=1.47, tone=3.14,
         smooth=0.42),
    dict(id="p-18-milanoreh", material="door_p_18_milanoreh", name="П-18 МиланОрех", tag="ПВХ",
         pattern="milan", seed=1202, color="#c78546", dark="#a96324", light="#dda263", comb=1.29, tone=3.25,
         smooth=0.42),
    dict(id="p-31-italoreh", material="door_p_31_italoreh", name="П-31 ИталОрех", tag="ПВХ",
         pattern="ital", seed=1103, color="#7f3a22", dark="#651f0d", light="#96543a", comb=1.17, tone=1.9,
         smooth=0.42),
    dict(id="p-32-milanoreh", material="door_p_32_milanoreh", name="П-32 МиланОрех", tag="ПВХ",
         pattern="milan", seed=1203, color="#cf884a", dark="#b06523", light="#e4a468", comb=1.77, tone=1.63,
         smooth=0.42),
]

# flat areas of the catalogue photos (stiles beside the pressed mouldings); the first one is on the check sheet
REFS = {
    "p-23-white": [
        ("p077_graffiti-2-p-23__belyy.jpg", (40, 40, 330, 400)),
        ("p077_status-14-p-23__belyy.jpg", (122, 15, 138, 330)),
        ("p077_status-15-p-23__belyy.jpg", (122, 15, 138, 330)),
    ],
    "p-34-shimo-light": [
        ("p077_status-14-p-34__shimo-svetlyy.jpg", (14, 15, 28, 160)),
        ("p077_status-14-p-34__shimo-svetlyy.jpg", (14, 210, 28, 300)),
        ("p077_status-14-p-34__shimo-svetlyy.jpg", (122, 15, 136, 300)),
        ("p077_status-15-p-34__shimo-svetlyy.jpg", (14, 15, 28, 160)),
        ("p077_status-15-p-34__shimo-svetlyy.jpg", (14, 210, 28, 300)),
        ("p077_status-15-p-34__shimo-svetlyy.jpg", (122, 15, 136, 300)),
    ],
    "p-35-shimo-dark": [
        ("p077_status-14-p-35__shimo-temnyy.jpg", (14, 15, 28, 160)),
        ("p077_status-14-p-35__shimo-temnyy.jpg", (14, 210, 28, 300)),
        ("p077_status-14-p-35__shimo-temnyy.jpg", (122, 15, 136, 300)),
        ("p077_status-15-p-35__shimo-temnyy.jpg", (14, 15, 28, 160)),
        ("p077_status-15-p-35__shimo-temnyy.jpg", (14, 210, 28, 300)),
        ("p077_status-15-p-35__shimo-temnyy.jpg", (122, 15, 136, 300)),
    ],
    "p-17-italoreh": [
        ("p078_lotos-p-17__italoreh.jpg", (124, 15, 136, 330)),
        ("p078_lotos-p-17__italoreh.jpg", (14, 15, 24, 160)),
        ("p078_lotos-p-17__italoreh.jpg", (14, 210, 24, 330)),
        ("p079_orbita-plyus-p-17__italoreh.jpg", (14, 15, 26, 160)),
        ("p079_orbita-plyus-p-17__italoreh.jpg", (14, 210, 26, 330)),
        ("p079_orbita-plyus-p-17__italoreh.jpg", (122, 15, 136, 330)),
        ("p078_alfa-p-17__italoreh.jpg", (14, 15, 26, 160)),
        ("p078_alfa-p-17__italoreh.jpg", (14, 210, 26, 330)),
        ("p078_alfa-p-17__italoreh.jpg", (122, 15, 136, 330)),
        ("p079_virazh-plyus-p-17__italoreh.jpg", (108, 15, 136, 330)),
    ],
    "p-18-milanoreh": [
        ("p078_lotos-p-18__milanoreh.jpg", (124, 15, 136, 330)),
        ("p078_lotos-p-18__milanoreh.jpg", (14, 15, 24, 160)),
        ("p078_lotos-p-18__milanoreh.jpg", (14, 210, 24, 330)),
        ("p079_orbita-plyus-p-18__milanoreh.jpg", (14, 15, 26, 160)),
        ("p079_orbita-plyus-p-18__milanoreh.jpg", (14, 210, 26, 330)),
        ("p079_orbita-plyus-p-18__milanoreh.jpg", (122, 15, 136, 330)),
        ("p078_alfa-p-18__milanoreh.jpg", (14, 15, 26, 160)),
        ("p078_alfa-p-18__milanoreh.jpg", (14, 210, 26, 330)),
        ("p078_alfa-p-18__milanoreh.jpg", (122, 15, 136, 330)),
        ("p079_virazh-plyus-p-18__milanoreh.jpg", (108, 15, 136, 330)),
    ],
    "p-31-italoreh": [
        ("p078_skinni-32-p-31__italoreh.jpg", (130, 30, 146, 300)),
        ("p078_skinni-32-p-31__italoreh.jpg", (22, 30, 38, 160)),
        ("p078_skinni-32-p-31__italoreh.jpg", (22, 210, 38, 300)),
        ("p078_skinni-33-p-31__italoreh-st-hud.jpg", (22, 30, 38, 160)),
        ("p078_skinni-33-p-31__italoreh-st-hud.jpg", (22, 210, 38, 300)),
        ("p078_skinni-33-p-31__italoreh-st-hud.jpg", (130, 30, 146, 300)),
    ],
    "p-32-milanoreh": [
        ("p078_skinni-32-p-32__milanoreh.jpg", (130, 30, 146, 300)),
        ("p078_skinni-32-p-32__milanoreh.jpg", (22, 30, 38, 160)),
        ("p078_skinni-32-p-32__milanoreh.jpg", (22, 210, 38, 300)),
        ("p078_skinni-33-p-32__milanoreh-st-hud.jpg", (22, 30, 38, 160)),
        ("p078_skinni-33-p-32__milanoreh-st-hud.jpg", (22, 210, 38, 300)),
        ("p078_skinni-33-p-32__milanoreh-st-hud.jpg", (130, 30, 146, 300)),
    ],
}

if __name__ == "__main__":
    grain.run(FAMILY, LINE, FINISHES, REFS, SOURCE)
