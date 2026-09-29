#!/usr/bin/env python3
"""preview2d.py without the instruction PDFs: the cut list comes from the committed JSON instead.

    python3 tools/casegoods/gen/check.py Assets/House4696/Resources/Casegoods/Designs/<id>.json
        [--ref <page png> --ref-box x0,y0,x1,y1] [--out tools/casegoods/pilot/<id>.png] [--finish <id>] [--open]

The instruction PDFs (reference/<slug>/is/) are git-ignored and a cloud session cannot download them, so preview2d.py would
only warn "нет файла инструкции". This wrapper runs preview2d's own checks and drawings with:
  * the cut list of tools/casegoods/gen/cutlists/<id>.json when it exists (the reference rows completed by hand from the
    page image: rows the PDF text lost, or the whole table of an instruction without a text layer), otherwise
    tools/casegoods/reference/<slug>/cutlists/<id>.json;
  * catalog.json merged with the wave fragments tools/casegoods/gen/*_catalog.json (finishes, profiles, collections,
    models written by parallel sessions before they are merged into catalog.json).
A model with "is" whose cut list is empty and not completed is an error: transcribe the table first.

One check is finer than preview2d's: a part with `shape: path` (a bottom notched round corner legs, a leg with a curved
edge) is tested for overlaps by its outline, not by its box — preview2d warns about the box, the lead's 3D build uses the
outline.
"""
import glob
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import preview2d  # noqa: E402

REF = os.path.join(TOOLS, "reference")


def merged_catalog():
    with open(preview2d.CATALOG) as fh:
        cat = json.load(fh)
    have = {k: {x["id"] for x in cat[k]} for k in ("finishes", "collections", "models")}
    for frag in sorted(glob.glob(os.path.join(HERE, "*_catalog.json"))):
        with open(frag) as fh:
            f = json.load(fh)
        for k in ("finishes", "collections", "models"):
            for x in f.get(k, []):
                if x["id"] not in have[k]:
                    cat[k].append(x)
                    have[k].add(x["id"])
        cat["profiles"].update(f.get("profiles", {}))
    return cat


def cutlist_path(did, model):
    own = os.path.join(HERE, "cutlists", did + ".json")
    if os.path.exists(own):
        return own
    slug = (model or {}).get("collection", "")
    ref = os.path.join(REF, slug, "cutlists", did + ".json")
    if os.path.exists(ref):
        return ref
    found = glob.glob(os.path.join(REF, "*", "cutlists", did + ".json"))
    return found[0] if found else None


def rows_of(path):
    with open(path) as fh:
        data = json.load(fh)
    return data["rows"] if isinstance(data, dict) else data


def outline_polygon(svg):
    """Absolute SVG path (M L H V C Q A Z) → polygon points; curves sampled, arcs by their end points."""
    toks = re.findall(r"[MLHVCQAZmlhvcqaz]|-?\d+(?:\.\d+)?(?:e-?\d+)?", svg)
    pts, cur, i, cmd = [], (0.0, 0.0), 0, None

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i].upper()
            i += 1
            if cmd == "Z":
                continue
        if cmd in ("M", "L"):
            cur = (num(), num())
            pts.append(cur)
        elif cmd == "H":
            cur = (num(), cur[1])
            pts.append(cur)
        elif cmd == "V":
            cur = (cur[0], num())
            pts.append(cur)
        elif cmd in ("C", "Q"):
            ctrl = [(num(), num()) for _ in range(2 if cmd == "C" else 1)]
            end = (num(), num())
            ps = [cur] + ctrl + [end]
            for k in range(1, 17):
                t = k / 16
                q = ps
                while len(q) > 1:
                    q = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(q, q[1:])]
                pts.append(q[0])
            cur = end
        elif cmd == "A":
            for _ in range(5):
                num()
            cur = (num(), num())
            pts.append(cur)
        else:
            i += 1
    return pts


def plane_axes(b):
    """Axes (indices into x, y, z) of the plane across a box's thinnest axis, as preview2d / the engine read outlines."""
    dims = [b[3] - b[0], b[4] - b[1], b[5] - b[2]]
    thin = dims.index(min(dims))
    return {2: (0, 1), 1: (0, 2), 0: (2, 1)}[thin]


def outline_overlap_area(p, region):
    """Area (mm²) of the part's outline inside the region box, in the outline's plane."""
    b = preview2d.box_of(p)
    ax = plane_axes(b)
    poly = outline_polygon(p["outline"])
    e = 0.5  # the region's rim: the outline's own edge rasterises onto it
    a0, a1 = region[ax[0]] + e, region[ax[0] + 3] - e
    c0, c1 = region[ax[1]] + e, region[ax[1] + 3] - e
    if a1 <= a0 or c1 <= c0:
        return 0.0
    k = 4.0  # px per mm
    w, h = max(1, int(math.ceil((a1 - a0) * k))), max(1, int(math.ceil((c1 - c0) * k)))
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).polygon([((u - a0) * k, (v - c0) * k) for u, v in poly], fill=255)
    return int((np.asarray(im) > 0).sum()) / (k * k)


def refine_overlaps(d, warns):
    parts = {preview2d.pid(p): p for p in d.get("parts", [])}
    out = []
    for w in warns:
        m = re.match(r"детали (\S+) и (\S+) пересекаются", w)
        if not m or m.group(1) not in parts or m.group(2) not in parts:
            out.append(w)
            continue
        a, b = parts[m.group(1)], parts[m.group(2)]
        A, B = preview2d.box_of(a), preview2d.box_of(b)
        region = [max(A[k], B[k]) for k in range(3)] + [min(A[k + 3], B[k + 3]) for k in range(3)]
        shaped = [p for p in (a, b) if p.get("shape") == "path" and p.get("outline")]
        if shaped and any(outline_overlap_area(p, region) < 1.0 for p in shaped):
            continue
        out.append(w)
    return out


def extent_without_handles(d, errors):
    """Pinskdrev's catalogue depth is the carcass / top depth (Рокси 0.01: sides 383 + front 19 + gap = top 404 = B;
    Шарли: stiles 19 + sides 366 + stiles 19 + back 3 = top 407 = B) — handles stand out of it. When the extent errors
    vanish without the handles, they are replaced by a note of how far the handles stand out."""
    if not any(e.startswith("габарит") for e in errors):
        return errors
    boxes = [preview2d.box_of(p) for p in d.get("parts", []) if p.get("kind") != "handle" and not (p.get("kind") == "rod" and not p.get("box"))]
    boxes = [b for b in boxes if b]
    size = d.get("size")
    if not boxes or not size:
        return errors
    ext = [max(b[3] for b in boxes) - min(b[0] for b in boxes), max(b[5] for b in boxes) - min(b[2] for b in boxes),
           max(b[4] for b in boxes) - min(b[1] for b in boxes)]
    if any(abs(g - w) > 1.0 for g, w in zip(ext, size)):
        return errors
    for e in errors:
        if e.startswith("габарит"):
            print(f"примечание {e} — только из-за ручек (каталог меряет корпус без ручек)")
    return [e for e in errors if not e.startswith("габарит")]


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        sys.exit(2)
    design = argv[0]
    cat = merged_catalog()
    with open(design) as fh:
        did = json.load(fh).get("id") or os.path.splitext(os.path.basename(design))[0]
    model = next((m for m in cat["models"] if (m.get("design") or m["id"]) == did), None)
    if model is None:
        print(f"ОШИБКА  модели {did} нет ни в catalog.json, ни в gen/*_catalog.json")
        sys.exit(1)

    orig_load = preview2d.load

    def load(path):
        d, _, _ = orig_load(path)
        return d, cat, model

    preview2d.load = load
    orig_check = preview2d.check

    def check(d, cat_, model_, is_pdf):
        errors, warns = orig_check(d, cat_, model_, is_pdf)
        return extent_without_handles(d, errors), refine_overlaps(d, warns)

    preview2d.check = check
    extra = []
    if model.get("is"):
        path = cutlist_path(did, model)
        if not path:
            print(f"ОШИБКА  у модели есть инструкция {model['is']}, но нет её спецификации (reference/…/cutlists/{did}.json)")
            sys.exit(1)
        rows = rows_of(path)
        if not rows:
            print(f"ОШИБКА  спецификация {os.path.relpath(path, TOOLS)} пуста (инструкция без текста): перепишите таблицу "
                  f"со страниц pages/{did}-p*.png в gen/cutlists/{did}.json")
            sys.exit(1)
        preview2d.cutlist.parse = lambda _pdf: rows
        extra = ["--is", path]
        print(f"спецификация из {os.path.relpath(path, TOOLS)}")
    sys.argv = [sys.argv[0], design] + extra + argv[1:]
    preview2d.main()


if __name__ == "__main__":
    main()
