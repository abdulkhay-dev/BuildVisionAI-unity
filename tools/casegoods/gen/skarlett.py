"""«Скарлетт» (Бобруйскмебель line БМ2.778, catalogue p. 107 = pp. 210–211): bedroom set, all modules by catalogue.

No instructions and no module cut-outs: the only source is the interior photo of p. 107 and the sizes printed there.
Construction (as the photo shows it, built like the Pinskdrev БМ2 sets): grey ЛДСП 16 carcass whose sides stand on the
floor, a recessed plinth rail between them, the top lying on the sides (its front edge postformed round), ХДФ backs in
grooves; МДФ 18 fronts inset between the sides (chests) or laid over the carcass (wardrobe): white high gloss, the top
drawer / the door band in the grey; long bar handles (satin chrome) centred on the fronts. The wardrobe's middle doors
carry a mirror glued edge to edge. Bed: grey headboard with an applied grey field and white gloss band, double side
rails (outer one with the foot corner rounded), a recessed plinth frame, slats on bearers and a middle beam.
Mirror: an oval (stadium) grey frame over a stadium mirror, hung on the wall.
"""
from common import dump

T = 16          # ЛДСП carcass
F = 18          # МДФ front
HB = dict(model="bar", dir="right", d=224, band=12, t=8, standoff=20)   # bar handle ≈ 224 mm long (photo: 216–228)


# ------------------------------------------------------------------------------------------------ helpers (also stambul)
def P(pid, box, **kw):
    p = {"id": pid, "box": [round(v, 1) for v in box]}
    p.update(kw)
    return p


def handle(pid, at, z, **kw):
    h = {"id": pid, "kind": "handle"}
    h.update(HB)
    h.update(kw)
    h["at"] = [round(at[0], 1), round(at[1], 1)]
    h["z"] = z
    return h


def box_drawer(tag, x0, x1, y0, h, z0, z1, t=T, bottom=3.5):
    """Drawer box between x0..x1 (outer), y0..y0+h, from z0 (back) to z1 (behind the front): sides, back, front board
    (the false front the facade is screwed to), bottom in grooves."""
    return [
        P(f"dr{tag}-l", [x0, y0, z0, x0 + t, y0 + h, z1]),
        P(f"dr{tag}-r", [x1 - t, y0, z0, x1, y0 + h, z1]),
        P(f"dr{tag}-back", [x0 + t, y0, z0, x1 - t, y0 + h, z0 + t]),
        P(f"dr{tag}-front", [x0 + t, y0, z1 - t, x1 - t, y0 + h, z1]),
        P(f"dr{tag}-bottom", [x0 + t - 6, y0 + 10, z0 + t - 6, x1 - t + 6, y0 + 10 + bottom, z1 - t + 6], kind="back"),
    ]


def stadium(x0, y0, x1, y1):
    """SVG outline of a stadium (a rectangle with half-round ends) in the front plane."""
    r = (y1 - y0) / 2
    return (f"M {x0 + r} {y0} L {x1 - r} {y0} A {r} {r} 0 0 1 {x1 - r} {y1} L {x0 + r} {y1} "
            f"A {r} {r} 0 0 1 {x0 + r} {y0} Z")


# ------------------------------------------------------------------------------------------------ chests
def chest(did, W, D, H, plinth, fronts, grey_top=True):
    """Sides on the floor, top on the sides, bottom over a recessed plinth; fronts inset between the sides.
    fronts: list of front heights from the bottom up (3 mm gaps, the lowest 2 mm over the plinth)."""
    zf = D - F                                  # the fronts' back face
    p = [
        P("side-l", [0, 0, 0, T, H - T, D], edge=2),
        P("side-r", [W - T, 0, 0, W, H - T, D], edge=2),
        P("top", [0, H - T, 0, W, H, D], edge=7),
        P("bottom", [T, plinth, 0, W - T, plinth + T, zf - 2]),
        P("plinth-front", [T, 0, zf - 30, W - T, plinth, zf - 30 + T]),
        P("plinth-back", [T, 0, 20, W - T, plinth, 20 + T]),
        P("back", [10, plinth + 10, 6, W - 10, H - T + 6, 9.5], kind="back"),
    ]
    moves = []
    y = plinth + 2
    xl, xr = T + 2, W - T - 2
    for i, h in enumerate(fronts):
        top_drawer = i == len(fronts) - 1
        tag = str(i + 1)
        fr = P(f"front-{tag}", [xl, y, zf, xr, y + h, D], kind="front",
               mat="accent" if (top_drawer and grey_top) else "gloss")
        hy = y + h * (0.45 if top_drawer else 0.65)    # photo: grey drawer just below its middle, white ones a third down
        hd = handle(f"k-{tag}", [W / 2, hy], D)
        y0 = y + 20 if i else plinth + T + 4
        box = box_drawer(tag, T + 13, W - T - 13, y0, h - 40 - (y0 - y - 20), 30, zf)
        p += [fr] + box + [hd]
        moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": [fr["id"]] + [q["id"] for q in box] + [hd["id"]],
                      "travel": round((D - 60) * 0.75)})
        y += h + 3
    assert abs((y - 3) - (H - T - 3)) < 0.01, (did, y)
    return dump(did, [W, D, H], p, moves)


def komod():
    # 881 = plinth 60 + 2 + 210 + 3 + 210 + 3 + 211 + 3 + 160 (grey) + 3 + top 16
    return chest("skarlett-1-31", 1000, 428, 881, 60, [210, 210, 211, 160])


def tumba():
    # 427 = plinth 45 + 2 + 218 (white) + 3 + 140 (grey) + 3 + top 16
    return chest("skarlett-1-30", 500, 428, 427, 45, [218, 140])


# ------------------------------------------------------------------------------------------------ wardrobe
def wardrobe():
    W, D, H = 1900, 643, 2200
    C = D - F - 4                 # carcass depth 621: doors 18 + the mirror 4 glued on the middle doors
    pl = 70
    p = [
        P("side-l", [0, 0, 0, T, H - T, C], edge=2),
        P("side-r", [W - T, 0, 0, W, H - T, C], edge=2),
        P("top", [0, H - T, 0, W, H, C], edge=7),
        P("bottom", [T, pl, 0, W - T, pl + T, C]),
        P("plinth-front", [T, 0, C - T, W - T, pl, C]),
        P("plinth-back", [T, 0, 20, W - T, pl, 20 + T]),
        P("plinth-mid", [942, 0, 36, 958, pl, C - T]),
    ]
    # three sections: 1 door | 2 doors (hanging) | 1 door
    parts_x = [(467, 483), (1417, 1433)]
    for i, (a, b) in enumerate(parts_x):
        p.append(P(f"partition-{i + 1}", [a, pl + T, 9.5, b, H - T, C]))
    for i, (a, b) in enumerate([(10, 475), (475, 1425), (1425, W - 10)]):
        p.append(P(f"back-{i + 1}", [a, pl + 10, 6, b, H - T + 6, 9.5], kind="back"))
    # shelves in the side sections, a hat shelf and the rail in the middle
    for s, (a, b) in (("l", (T, 467)), ("r", (1433, W - T))):
        for j, y in enumerate([450, 800, 1150, 1500, 1850]):
            p.append(P(f"shelf-{s}{j + 1}", [a + 1, y, 20, b - 1, y + T, C - 20]))
    p.append(P("shelf-m", [483, 1850, 20, 1417, 1866, C - 20]))
    p.append(P("rail", [487, 1760, C / 2 - 10, 1413, 1780, C / 2 + 10], kind="tube", mat="chrome"))
    # doors: 472 wide, 3 mm gaps, from 72 up to 2182 (the top's edge shows above)
    y0, y1 = pl + 2, H - T - 2
    moves = []
    xs = [(1.5 + i * 475, 473.5 + i * 475) for i in range(4)]
    band = (1019, 1264)           # the grey band with the handle (photo: 245 mm, its top 1264)
    for i, (a, b) in enumerate(xs):
        tag = str(i + 1)
        hinge = "left" if i in (0, 1) else "right"
        if i in (0, 3):
            ids = [f"door{tag}-low", f"door{tag}-band", f"door{tag}-up", f"k-{tag}"]
            p += [P(ids[0], [a, y0, C, b, band[0] - 2, C + F], kind="front", mat="gloss"),
                  P(ids[1], [a, band[0], C, b, band[1], C + F], kind="front", mat="accent"),
                  P(ids[2], [a, band[1] + 2, C, b, y1, C + F], kind="front", mat="gloss"),
                  handle(ids[3], [(a + b) / 2, (band[0] + band[1]) / 2], C + F)]
        else:
            ids = [f"door{tag}", f"mirror-{tag}"]
            p += [P(ids[0], [a, y0, C, b, y1, C + F], kind="front"),
                  P(ids[1], [a + 3, y0 + 3, C + F, b - 3, y1 - 3, D], kind="mirror")]
        moves.append({"type": "door", "name": f"door_{tag}", "parts": ids, "hinge": hinge, "angle": 100})
    return dump("skarlett-1-27-01", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ bed
def bed():
    W, L, H = 1672, 2057, 1050    # catalogue L2057 × B1672: x = the width, z = the length
    p = [
        P("headboard", [0, 0, 0, W, H, T], edge=3),
        P("head-field", [45, 812, T, W - 45, 1005, T + F], kind="front", mat="accent"),
        P("head-band", [45, 400, T, W - 45, 809, T + F], kind="front", mat="gloss"),
        # double side rails: the outer ones run to the foot with the corner rounded, the inner ones stop at the footboard
        P("rail-l", [0, 60, T, T, 330, L], shape="path", edge=3,
          outline=f"M {T} 60 L {L} 60 L {L} 290 A 40 40 0 0 1 {L - 40} 330 L {T} 330 Z"),
        P("rail-r", [W - T, 60, T, W, 330, L], shape="path", edge=3,
          outline=f"M {T} 60 L {L} 60 L {L} 290 A 40 40 0 0 1 {L - 40} 330 L {T} 330 Z"),
        P("rail-l-in", [T, 60, T, 2 * T, 330, L - T]),
        P("rail-r-in", [W - 2 * T, 60, T, W - T, 330, L - T]),
        P("footboard", [T, 60, L - T, W - T, 330, L], edge=6),
        # recessed plinth frame 60 in from the rails
        P("plinth-front", [60, 0, L - 76, W - 60, 60, L - 60]),
        P("plinth-back", [60, 0, 76, W - 60, 60, 92]),
        P("plinth-l", [60, 0, 92, 76, 60, L - 76]),
        P("plinth-r", [W - 76, 0, 92, W - 60, 60, L - 76]),
        # slat bearers, the middle beam, the slats and the mattress 2000 × 1600
        P("bearer-l", [2 * T, 230, T, 2 * T + 25, 270, L - T]),
        P("bearer-r", [W - 2 * T - 25, 230, T, W - 2 * T, 270, L - T]),
        P("beam", [W / 2 - 8, 0, 92, W / 2 + 8, 270, L - 76]),
        P("mattress", [36, 278, 36, W - 36, 478, 2036], kind="mattress"),
    ]
    n = 24
    for i in range(n):
        z = 40 + i * 83
        p.append(P(f"slat-{i + 1}", [2 * T + 4, 270, z, W - 2 * T - 4, 278, z + 53], mat="#c9a877"))
    return dump("skarlett-1-10", [W, L, H], p, [])


# ------------------------------------------------------------------------------------------------ mirror
def mirror():
    W, D, H = 1000, 16, 400
    frame = stadium(0, 0, W, H) + " " + stadium(22, 22, W - 22, H - 22)
    p = [
        P("frame", [0, 0, 4, W, H, D], shape="path", outline=frame, edge=4),
        P("mirror", [18, 18, 0, W - 18, H - 18, 4], kind="mirror", shape="path", outline=stadium(18, 18, W - 18, H - 18)),
    ]
    return dump("skarlett-1-32", [W, D, H], p, [])


if __name__ == "__main__":
    for f in (komod, tumba, wardrobe, bed, mirror):
        print(f())
