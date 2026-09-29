#!/usr/bin/env python3
"""Merge a wave's catalogue fragments (tools/casegoods/gen/*_catalog.json) into catalog.json.

    python3 tools/casegoods/gen/merge_catalog.py [--remove]

Parallel sessions / subagents cannot edit catalog.json at once, so each writes gen/<slug>_catalog.json; this appends their
finishes, profiles, collections and models to catalog.json, one entry per line like the file's own. Entries already in
catalog.json are never changed; an id that is already there with other content is an error (nothing is written).
--remove deletes the merged fragments (check.py merges any fragment left over, so keep one source of truth).
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.abspath(os.path.join(HERE, "..", "..", "..", "Assets/House4696/Resources/Casegoods/catalog.json"))


def line(entry):
    return "{ " + json.dumps(entry, ensure_ascii=False, separators=(", ", ": "))[1:-1] + " }"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--only", help="comma-separated slugs: merge just these fragments (the others may still be in work)")
    a = ap.parse_args()
    with open(CATALOG) as fh:
        text = fh.read()
    cat = json.loads(text)
    frags = sorted(glob.glob(os.path.join(HERE, "*_catalog.json")))
    if a.only:
        want = {x.strip() for x in a.only.split(",")}
        frags = [f for f in frags if os.path.basename(f)[:-len("_catalog.json")] in want]
    add = {"finishes": [], "collections": [], "models": []}
    profiles = {}
    errors = []
    for frag in frags:
        with open(frag) as fh:
            f = json.load(fh)
        for k in add:
            have = {x["id"]: x for x in cat[k] + add[k]}
            for x in f.get(k, []):
                if x["id"] in have:
                    if have[x["id"]] != x:
                        errors.append(f"{os.path.basename(frag)}: {k} '{x['id']}' is already there with other content")
                    continue
                add[k].append(x)
        for pid, p in f.get("profiles", {}).items():
            old = cat["profiles"].get(pid) or profiles.get(pid)
            if old is not None and old != p:
                errors.append(f"{os.path.basename(frag)}: profile '{pid}' is already there with other content")
            elif old is None:
                profiles[pid] = p
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    # text insertion keeps every existing line as it is
    lines = text.rstrip("\n").split("\n")

    def section_end(key):
        start = next(i for i, l in enumerate(lines) if l.startswith(f'  "{key}":'))
        depth = 0
        for i in range(start, len(lines)):
            depth += lines[i].count("[") + lines[i].count("{") - lines[i].count("]") - lines[i].count("}")
            if depth == 0:
                return i
        raise ValueError(key)

    for key in ("models", "collections", "finishes"):          # from the bottom up: indices stay valid
        if not add[key]:
            continue
        end = section_end(key)                                   # the line with the closing bracket
        prev = end - 1
        if not lines[prev].rstrip().endswith(","):
            lines[prev] = lines[prev].rstrip() + ","
        new = [f"    {line(x)}," for x in add[key]]
        new[-1] = new[-1][:-1]
        lines[end:end] = new
    if profiles:
        end = section_end("profiles")
        prev = end - 1
        if not lines[prev].rstrip().endswith(","):
            lines[prev] = lines[prev].rstrip() + ","
        new = []
        for pid, p in profiles.items():
            new.append(f'    "{pid}": {json.dumps(p, ensure_ascii=False, separators=(", ", ": "))},')
        new[-1] = new[-1][:-1]
        lines[end:end] = new
    out = "\n".join(lines) + "\n"
    merged = json.loads(out)                                     # must stay valid JSON
    for k in add:
        assert len(merged[k]) == len(cat[k]) + len(add[k])
    with open(CATALOG, "w") as fh:
        fh.write(out)
    print(f"+{len(add['finishes'])} finishes, +{len(profiles)} profiles, +{len(add['collections'])} collections, "
          f"+{len(add['models'])} models from {len(frags)} fragments")
    if a.remove:
        for frag in frags:
            os.remove(frag)
        print(f"removed {len(frags)} fragments")


if __name__ == "__main__":
    main()
