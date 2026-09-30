#!/usr/bin/env python3
"""Put the decor texture materials into the casegoods finishes (catalog.json), from tools/casegoods/decor_map.json.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/apply_decors.py            # dry run: the report only
    /private/tmp/claude-501/venv/bin/python tools/casegoods/apply_decors.py --write    # rewrite catalog.json
    ... --prints [--write]      # also rename the British Bum fronts' "print": british_bum_<motif> → cgprint_british_bum_<motif>
    ... --only cg_dub_kanon,cgfab_velur    # just these materials

A mapped role is replaced only when its material is ready: the folder Assets/House4696/External/Materials/<id>/ holds an
albedo and external.json lists the id (merge_entries.py ran; --no-registry skips that check). Baked materials are
written bare ("cg_dub_kanon"); tintable ones (decor_map.json "tintable") as "<id>#rrggbb", where the tint = the target
colour ÷ the albedo's mean, per channel in linear space (URP multiplies _BaseColor into the albedo), clamped to 1 —
a clamped channel is reported. "@gloss" is kept. A role whose catalogue value is neither the mapped "old" value nor
the result is left alone and reported as changed.

catalog.json is edited as text inside each finish's line(s), so every other byte stays as it was (the style of
gen/merge_catalog.py); the result is checked against the same edit made on the parsed JSON.
Needs Pillow (the albedo mean); python3 without it works while no material exists yet.
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CATALOG = os.path.join(ROOT, "Assets/House4696/Resources/Casegoods/catalog.json")
DESIGNS = os.path.join(ROOT, "Assets/House4696/Resources/Casegoods/Designs")
EXTERNAL = os.path.join(ROOT, "Assets/House4696/External")
MAP = os.path.join(ROOT, "tools/casegoods/decor_map.json")

PRINT_OLD = "british_bum_"
PRINT_NEW = "cgprint_british_bum_"


# ------------------------------------------------------------------ colour
def to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def to_srgb(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_lin(hx):
    return [to_lin(int(hx[i:i + 2], 16) / 255) for i in (1, 3, 5)]


def lin_hex(lin):
    return "#" + "".join(f"{max(0, min(255, round(to_srgb(max(0.0, min(1.0, c))) * 255))):02x}" for c in lin)


LUT = [to_lin(v / 255) for v in range(256)]


def albedo_mean_lin(path):
    """Mean albedo colour in linear space (exact, from the image's histogram)."""
    from PIL import Image
    with Image.open(path) as im:
        h = im.convert("RGB").histogram()
    out = []
    for ch in range(3):
        counts = h[ch * 256:(ch + 1) * 256]
        n = sum(counts)
        out.append(sum(c * LUT[v] for v, c in enumerate(counts)) / n)
    return out


# ------------------------------------------------------------------ materials
class Library:
    def __init__(self, registry=True):
        self.registry = registry
        try:
            with open(os.path.join(EXTERNAL, "external.json")) as fh:
                self.entries = {m["id"]: m for m in json.load(fh)["materials"]}
        except (OSError, ValueError, KeyError):
            self.entries = {}
        self._albedo, self._mean = {}, {}

    def albedo(self, mid):
        """Path of the material's albedo, or None."""
        if mid in self._albedo:
            return self._albedo[mid]
        folder = os.path.join(EXTERNAL, "Materials", mid)
        path = None
        e = self.entries.get(mid)
        if e and e.get("textures", {}).get("albedo"):
            p = os.path.join(EXTERNAL, e.get("folder", f"Materials/{mid}"), e["textures"]["albedo"])
            path = p if os.path.isfile(p) else None
        if path is None and os.path.isdir(folder):
            hits = sorted(p for p in glob.glob(os.path.join(folder, "*albedo*")) if not p.endswith(".meta"))
            path = hits[0] if hits else None
        self._albedo[mid] = path
        return path

    def missing(self, mid):
        """Why the material cannot be used yet, or None."""
        if not self.albedo(mid):
            return "no albedo in External/Materials/" + mid
        if self.registry and mid not in self.entries:
            return "not in external.json (merge_entries.py)"
        return None

    def mean(self, mid):
        if mid not in self._mean:
            self._mean[mid] = albedo_mean_lin(self.albedo(mid))
        return self._mean[mid]


# ------------------------------------------------------------------ catalogue text edits
def get_role(f, role):
    return f.get("roles", {}).get(role[6:]) if role.startswith("roles.") else f.get(role)


def set_role(f, role, value):
    if role.startswith("roles."):
        f.setdefault("roles", {})[role[6:]] = value
    else:
        f[role] = value


def match_close(text, i):
    """Index of the bracket closing the one at text[i] (JSON strings skipped)."""
    depth, s = 0, False
    while i < len(text):
        ch = text[i]
        if s:
            if ch == "\\":
                i += 1
            elif ch == '"':
                s = False
        elif ch == '"':
            s = True
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("unbalanced JSON")


def finish_span(text, fid):
    m = re.search(r'\{\s*"id":\s*' + re.escape(json.dumps(fid, ensure_ascii=False)) + r"\s*,", text)
    if not m:
        raise KeyError(fid)
    return m.start(), match_close(text, m.start()) + 1


def top_level_pairs(text, a, b):
    """{key: (start, end) of the value} for the object text[a:b] (its own keys only)."""
    out, i = {}, a + 1
    while i < b - 1:
        ch = text[i]
        if ch == '"':
            m = re.compile(r'"((?:[^"\\]|\\.)*)"\s*:\s*').match(text, i)
            if m:
                key = json.loads('"' + m.group(1) + '"')
                vs = m.end()
                if text[vs] in "{[":
                    ve = match_close(text, vs) + 1
                elif text[vs] == '"':
                    ve = re.compile(r'"(?:[^"\\]|\\.)*"').match(text, vs).end()
                else:
                    ve = re.compile(r"[^,}\]\s]+").match(text, vs).end()
                out[key] = (vs, ve)
                i = ve
                continue
        i += 1
    return out


def edit_finish(text, fid, role, value):
    """text with the finish's role set to value (replaced in place, or added)."""
    a, b = finish_span(text, fid)
    pairs = top_level_pairs(text, a, b)
    new = json.dumps(value, ensure_ascii=False)
    if role.startswith("roles."):
        key = role[6:]
        if "roles" in pairs:
            ra, rb = pairs["roles"]
            inner = top_level_pairs(text, ra, rb)
            if key in inner:
                vs, ve = inner[key]
                return text[:vs] + new + text[ve:]
            close = rb - 1                                      # the roles' "}"
            body = text[ra + 1:close].strip()
            sep = ", " if body else ""
            return text[:close] + f'{sep}{json.dumps(key, ensure_ascii=False)}: {new}' + text[close:]
        anchor = max((pairs[k][1] for k in ("back", "front", "body") if k in pairs), default=None)
        if anchor is None:
            raise KeyError(f"{fid}: no body to anchor roles on")
        return text[:anchor] + f', "roles": {{{json.dumps(key, ensure_ascii=False)}: {new}}}' + text[anchor:]
    if role in pairs:
        vs, ve = pairs[role]
        return text[:vs] + new + text[ve:]
    anchor = pairs["body"][1]
    return text[:anchor] + f', {json.dumps(role)}: {new}' + text[anchor:]


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="rewrite catalog.json (and the designs with --prints)")
    ap.add_argument("--prints", action="store_true", help="also rename the designs' british_bum_* prints")
    ap.add_argument("--only", help="comma-separated material ids")
    ap.add_argument("--no-registry", action="store_true", help="do not require the id in external.json")
    ap.add_argument("-v", "--verbose", action="store_true", help="list every skipped role")
    a = ap.parse_args()

    with open(MAP) as fh:
        dmap = json.load(fh)
    tintable = set(dmap["tintable"])
    only = {x.strip() for x in a.only.split(",")} if a.only else None
    lib = Library(registry=not a.no_registry)

    with open(CATALOG) as fh:
        text = fh.read()
    cat = json.loads(text)
    fins = {f["id"]: f for f in cat["finishes"]}

    replaced, already, skipped, stale, warn = [], [], {}, [], []
    for e in dmap["entries"]:
        mid = e["material"]
        if only and mid not in only:
            continue
        f = fins.get(e["finish"])
        if f is None:
            stale.append((e, "finish not in catalog.json"))
            continue
        cur = get_role(f, e["role"])
        why = lib.missing(mid)
        if why:
            skipped.setdefault(mid, [why, []])[1].append(e)
            continue
        if mid in tintable:
            target = hex_lin(e["tint"])
            mean = lib.mean(mid)
            ratio = [t / m if m > 0 else 1.0 for t, m in zip(target, mean)]
            if max(ratio) > 1.0:
                got = lin_hex([min(r, 1.0) * m for r, m in zip(ratio, mean)])
                warn.append(f"{e['finish']} {e['role']}: {mid} albedo too dark for {e['tint']} — clamped, reads {got}")
            value = mid + lin_hex(ratio)
        else:
            value = mid
        if e["gloss"]:
            value += "@gloss"
        if cur == value:
            already.append(e)
            continue
        if cur != e["old"]:
            stale.append((e, f"catalog.json has {cur!r}, the map expects {e['old']!r}"))
            continue
        replaced.append((e, value))

    # the edit, as text and on the parsed copy
    out = text
    for e, value in replaced:
        out = edit_finish(out, e["finish"], e["role"], value)
        set_role(fins[e["finish"]], e["role"], value)
    if replaced and json.loads(out) != cat:
        sys.exit("internal error: the text edit does not match the JSON edit — nothing written")

    # unmapped: finish roles that are neither mapped nor declared kept
    known = {(e["finish"], e["role"]) for e in dmap["entries"]} | {(k["finish"], k["role"]) for k in dmap["keep"]}
    unmapped = []
    for f in json.loads(text)["finishes"]:
        roles = [r for r in ("body", "front", "back") if r in f] + ["roles." + k for k in f.get("roles", {})]
        unmapped += [(f["id"], r, get_role(f, r)) for r in roles if (f["id"], r) not in known]

    # prints
    print_edits, print_skip = [], {}
    if a.prints:
        for path in sorted(glob.glob(os.path.join(DESIGNS, "*.json"))):
            with open(path) as fh:
                d = fh.read()
            hits = sorted(set(re.findall(r'"print":\s*"(' + PRINT_OLD + r'[^"]+)"', d)))
            if not hits:
                continue
            nd = d
            for old in hits:
                new = PRINT_NEW + old[len(PRINT_OLD):]
                if only and new not in only:
                    continue
                why = lib.missing(new)
                if why:
                    print_skip.setdefault(new, [why, []])[1].append(os.path.basename(path))
                    continue
                nd = re.sub(r'("print":\s*)"' + re.escape(old) + '"', r'\1"' + new + '"', nd)
            if nd != d:
                json.loads(nd)
                print_edits.append((path, d, nd))

    # report
    mode = "WRITE" if a.write else "dry run"
    print(f"== apply_decors ({mode}) — {len(dmap['entries'])} mapped roles in "
          f"{len({e['finish'] for e in dmap['entries']})} finishes")
    print(f"replaced{'' if a.write else ' (would)'}: {len(replaced)}")
    for e, value in replaced:
        print(f"  {e['finish']:32} {e['role']:18} {e['old']} → {value}")
    if already:
        print(f"already applied: {len(already)}")
    n_skip = sum(len(v[1]) for v in skipped.values())
    print(f"skipped (material not ready): {n_skip} roles, {len(skipped)} materials")
    for mid, (why, es) in sorted(skipped.items()):
        print(f"  {mid:26} {len(es):3}  {why}")
        if a.verbose:
            for e in es:
                print(f"      {e['finish']} {e['role']} {e['old']}")
    if stale:
        print(f"changed since the map (left alone): {len(stale)}")
        for e, why in stale:
            print(f"  {e['finish']} {e['role']}: {why}")
    for w in warn:
        print("  WARNING " + w)
    print(f"unmapped finish roles: {len(unmapped)}")
    for fid, r, v in unmapped:
        print(f"  {fid} {r} = {v}")
    un = dmap.get("unattributed", [])
    if un:
        print(f"unattributed (decor_map.md; nothing to apply): {len(un)}")
        for u in un:
            print(f"  {u['finish']} {u['role']}: {u['why']}")
    if a.prints:
        print(f"prints: {len(print_edits)} designs to rename; skipped {len(print_skip)} materials not ready "
              f"({sum(len(v[1]) for v in print_skip.values())} design uses)")
        for mid, (why, files) in sorted(print_skip.items()):
            print(f"  {mid:40} {len(files)} designs  {why}")
        for path, _, _ in print_edits:
            print(f"  rename in {os.path.basename(path)}")

    if a.write:
        if replaced:
            with open(CATALOG, "w") as fh:
                fh.write(out)
            print(f"catalog.json: {len(replaced)} roles written")
        for path, _, nd in print_edits:
            with open(path, "w") as fh:
                fh.write(nd)
        if print_edits:
            print(f"designs: {len(print_edits)} written")
    elif replaced or print_edits:
        print("dry run — nothing written (--write to apply)")


if __name__ == "__main__":
    main()
