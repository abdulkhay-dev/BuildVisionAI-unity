"""Flora bed 2-16 (1.05) and round mirror (1.03)."""
from common import dump, feet


def bed():
    W = 1764
    p = [
        {"n": "1", "box": [0, 4, 0, W, 970, 25]},
        {"kind": "moulding", "profile": "flora-41", "z": 25, "side": -1,
         "path": [[0, 4], [0, 970], [W, 970], [W, 4]], "covers": ["5", "6", "6.1"]},
        {"n": "3", "box": [50, 170, 25, 75, 370, 2035]},
        {"n": "3.1", "box": [1689, 170, 25, 1714, 370, 2035]},
        {"n": "2", "box": [50, 124, 2035, 1714, 446, 2060]},
        {"kind": "moulding", "profile": "flora-41", "closed": True, "z": 2060,
         "path": [[50, 124], [1714, 124], [1714, 446], [50, 446]], "covers": ["7", "7", "8", "8"]},
        {"n": "4", "box": [90.5, 4, 2003, 1673.5, 124, 2019]},
        # the metal base (m, 2000×1600): rails, slats and its middle legs
        {"id": "m-frame-l", "kind": "panel", "mat": "black", "box": [82, 320, 35, 112, 360, 2035], "covers": ["m"]},
        {"id": "m-frame-r", "kind": "panel", "mat": "black", "box": [1652, 320, 35, 1682, 360, 2035]},
        {"id": "m-leg-1", "kind": "tube", "mat": "black", "box": [869.5, 4, 700, 894.5, 320, 725]},
        {"id": "m-leg-2", "kind": "tube", "mat": "black", "box": [869.5, 4, 1350, 894.5, 320, 1375]},
        {"id": "mattress", "kind": "mattress", "box": [82, 360, 35, 1682, 560, 2035]},
    ]
    for i in range(24):
        z = 60 + i * 81
        p.append({"id": f"m-slat-{i + 1}", "kind": "panel", "mat": "#c9a877", "box": [112, 348, z, 1652, 356, z + 53]})
    p += feet([60, 1704], [12])
    p += [{"id": "g-3", "kind": "tube", "mat": "black", "box": [110, 0, 2001, 130, 4, 2021], "covers": ["g"]},
          {"id": "g-4", "kind": "tube", "mat": "black", "box": [1634, 0, 2001, 1654, 4, 2021], "covers": ["g"]},
          {"id": "g-5", "kind": "tube", "mat": "black", "box": [872, 0, 702.5, 892, 4, 722.5], "covers": ["g"]},
          {"id": "g-6", "kind": "tube", "mat": "black", "box": [872, 0, 1352.5, 892, 4, 1372.5], "covers": ["g"]}]
    return dump("flora-1-05", [1764, 2076, 970], p, [])


def mirror():
    p = [
        {"n": "1", "shape": "ring", "inner": 560, "box": [0, 0, 5, 700, 700, 21], "edge": 3},
        {"n": "2", "kind": "mirror", "shape": "circle", "box": [60, 60, 1, 640, 640, 5]},
        {"id": "bumpers", "kind": "panel", "mat": "black", "box": [340, 40, 0, 360, 60, 5], "covers": []},
    ]
    return dump("flora-1-03", [700, 21, 700], p, [])


if __name__ == "__main__":
    print(bed())
    print(mirror())
