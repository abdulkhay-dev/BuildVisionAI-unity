"""Flora wardrobes 1.06 (2 doors), 1.01 (2 doors + drawer), 1.07 (1 door): plinth on ФБ482 glides, frame mouldings."""
from common import dump, ring, drawer_box, feet

W, D, H = 900, 584, 2304          # carcass width, depth (moulding makes 600), height
Z = D                              # front face of the carcass / base of the mouldings


def carcass(w, back_rows):
    p = [
        {"n": "1", "box": [0, 100, 0, 16, 2288, D]},
        {"n": "2", "box": [w - 16, 100, 0, w, 2288, D]},
        {"n": "3", "box": [0, 2288, 0, w, 2304, D]},
        {"n": "4", "box": [0, 84, 0, w, 100, D]},
    ]
    return p


def plinth(w, nf="11", ns=("12", "12.1")):
    return [
        {"n": nf, "id": f"{nf}-front", "box": [1, 4, 547, w - 1, 84, 563]},
        {"n": nf, "id": f"{nf}-back", "box": [1, 4, 0, w - 1, 84, 16]},
        {"n": ns[0], "box": [1, 4, 16, 17, 84, 547]},
        {"n": ns[1], "box": [w - 17, 4, 16, w - 1, 84, 547]},
    ]


def frame(y0, y1, w, covers):
    return {"kind": "moulding", "profile": "flora-41", "closed": True, "z": Z,
            "path": [[0, y0], [w, y0], [w, y1], [0, y1]], "covers": covers}


def w106():
    p = carcass(W, None)
    p += [{"n": "5", "box": [442, 100, 9.5, 458, 2288, 567.5]}]
    p += plinth(W)
    p += [{"n": "13", "box": [16, 100, 519, 41, 2288, D]}, {"n": "13.1", "box": [859, 100, 519, 884, 2288, D]}]
    # left column: shelves (7 removable, 6 fixed in the middle); right: top shelf over the hanging rail
    for i, y in enumerate([458, 831, 1557, 1936]):
        p.append({"n": "7", "id": f"7-{i + 1}", "box": [17, y - 16, 20, 441, y, 518]})
    p.append({"n": "6", "id": "6-1", "box": [16, 1173, 20, 442, 1189, 518]})
    p.append({"n": "6", "id": "6-2", "box": [458, 1920, 20, 884, 1936, 518]})
    p.append({"id": "d2", "kind": "tube", "mat": "chrome", "box": [462, 1850, 282, 880, 1870, 302], "covers": ["d2"]})
    p += [{"n": "16", "id": "16-1", "kind": "back", "box": [10, 95, 6, 448, 1193, 9.5]},
          {"n": "16", "id": "16-2", "kind": "back", "box": [10, 1193, 6, 448, 2291, 9.5]},
          {"n": "15", "kind": "back", "box": [452, 95, 6, 890, 1968.5, 9.5]},
          {"n": "14", "kind": "back", "box": [452, 1968.5, 6, 890, 2291, 9.5]}]
    p.append(frame(84, 2304, W, ["9", "9", "10", "10"]))
    p.append({"n": "8", "id": "8-left", "kind": "front", "box": [43, 127, 568, 448.5, 2261, D]})
    p.append(ring("k1-left", [448.5, 1200], "left", Z))
    p.append({"n": "8", "id": "8-right", "kind": "front", "box": [451.5, 127, 568, 857, 2261, D]})
    p.append(ring("k1-right", [451.5, 1200], "right", Z))
    p += feet([60, 255, 450, 645, 840], [40, 530])   # 10 glides along the front and the back
    moves = [{"type": "door", "name": "door_left", "parts": ["8-left", "k1-left"], "hinge": "left", "angle": 100},
             {"type": "door", "name": "door_right", "parts": ["8-right", "k1-right"], "hinge": "right", "angle": 100}]
    return dump("flora-1-06", [900, 600, 2304], p, moves)


def w101():
    p = carcass(W, None)
    p += plinth(W, "14", ("15", "15.1"))
    p += [
        {"n": "8", "box": [16, 503, 16, 884, 519, D]},
        {"n": "19", "box": [16, 487, 504, 884, 503, D]},
        {"n": "7", "box": [16, 1964, 16, 884, 1980, 514]},
        {"n": "5", "box": [386, 519, 9.5, 514, 1964, 25.5]},
        {"n": "20", "id": "20-1", "box": [16, 519, 519, 41, 2288, D]},
        {"n": "20", "id": "20-2", "box": [859, 519, 519, 884, 2288, D]},
        {"n": "21", "id": "21-top", "box": [41.5, 2263, 519, 858.5, 2288, D]},
        {"n": "21", "id": "21-bottom", "box": [41.5, 519, 519, 858.5, 544, D]},
        {"n": "10", "id": "10-1", "box": [16, 359.5, 16, 41, 403.5, D]},
        {"n": "10", "id": "10-2", "box": [859, 359.5, 16, 884, 403.5, D]},
        {"n": "10", "id": "10-3", "box": [16, 192.5, 16, 41, 236.5, D]},
        {"n": "10", "id": "10-4", "box": [859, 192.5, 16, 884, 236.5, D]},
        {"n": "18", "kind": "back", "box": [11, 95, 6, 889, 510, 9.5]},
        {"n": "17", "id": "17-1", "kind": "back", "box": [10, 514, 6, 448, 1972, 9.5]},
        {"n": "17", "id": "17-2", "kind": "back", "box": [452, 514, 6, 890, 1972, 9.5]},
        {"n": "16", "kind": "back", "box": [11, 1972, 6, 889, 2293, 9.5]},
        {"id": "d2", "kind": "tube", "mat": "chrome", "box": [20, 1890, 282, 880, 1910, 302], "covers": ["d2"]},
        frame(503, 2304, W, ["11", "11", "12", "12"]),
        frame(84, 503, W, ["11", "11", "13", "13"]),
        {"n": "9", "kind": "front", "box": [43, 546, 568, 448.5, 2261, D]},
        ring("k1-left", [448.5, 1210], "left", Z),
        {"n": "9.1", "kind": "front", "box": [451.5, 546, 568, 857, 2261, D]},
        ring("k1-right", [451.5, 1210], "right", Z),
    ]
    moves = [{"type": "door", "name": "door_left", "parts": ["9", "k1-left"], "hinge": "left", "angle": 100},
             {"type": "door", "name": "door_right", "parts": ["9.1", "k1-right"], "hinge": "right", "angle": 100}]
    for tag, (n, y0, d) in {"1": ("6.1", 127, "down"), "2": ("6", 294, "up")}.items():
        p.append({"n": n, "kind": "front", "box": [43, y0, 568, 857, y0 + 165, D]})
        box = drawer_box(tag, 54.5, 845.5, y0 + 25, 125, 68, 568)
        p += box
        h = ring(f"k1-d{tag}", [450, 293], d, Z)
        p.append(h)
        moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": [n] + [q["id"] for q in box] + [h["id"]], "travel": 400})
    p += feet([60, 255, 450, 645, 840], [40, 530])
    return dump("flora-1-01", [900, 600, 2304], p, moves)


def w107():
    w = 492
    p = carcass(w, None)
    p += plinth(w, "8", ("9", "9.1"))
    p += [
        {"n": "10", "box": [16, 100, 519, 41, 2288, D]},
        {"n": "11", "id": "11-top", "box": [41, 2263, 519, 475, 2288, D]},
        {"n": "11", "id": "11-bottom", "box": [41, 100, 519, 475, 125, D]},
        {"n": "5", "id": "5-1", "box": [16, 452, 16, 476, 468, 514]},
        {"n": "5", "id": "5-2", "box": [16, 1964, 16, 476, 1980, 514]},
        {"n": "16", "kind": "back", "box": [11, 95, 6, 481, 455.5, 9.5]},
        {"n": "15", "kind": "back", "box": [11, 459.5, 6, 481, 1972, 9.5]},
        {"n": "14", "kind": "back", "box": [11, 1972, 6, 481, 2293, 9.5]},
        {"id": "d2", "kind": "tube", "mat": "chrome", "box": [20, 1920, 282, 472, 1940, 302], "covers": ["d2"]},
        frame(84, 2304, w, ["12", "12", "13", "13"]),
        {"n": "7", "kind": "front", "box": [43, 127, 568, 448.5, 2261, D]},
        ring("k1", [448.5, 1200], "left", Z),
    ]
    for i, y in enumerate([821, 1190, 1550]):
        p.append({"n": "6", "id": f"6-{i + 1}", "box": [17, y - 16, 20, 475, y, 518]})
    p += feet([45, 185, 307, 447], [40, 530])
    moves = [{"type": "door", "name": "door", "parts": ["7", "k1"], "hinge": "left", "angle": 100}]
    return dump("flora-1-07", [492, 600, 2304], p, moves)


if __name__ == "__main__":
    print(w106())
    print(w101())
    print(w107())
