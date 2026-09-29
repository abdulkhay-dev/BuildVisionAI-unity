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
"""
import glob
import json
import os
import sys

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
