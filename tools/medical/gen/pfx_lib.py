import json, os, sys
OUT = "/Users/abdulxay/Documents/works/ansormed/unity/Assets/House4696/Resources/Medical/Designs"
class D:
    def __init__(s, id, size, mats):
        s.d = {"id": id, "size": size, "mats": mats, "parts": []}
        s.ids = set()
    def add(s, id, kind, mat=None, **kw):
        assert id not in s.ids, id
        s.ids.add(id)
        p = {"id": id, "kind": kind}
        if mat: p["mat"] = mat
        for k, v in kw.items():
            if v is None: continue
            p[k] = rnd(v)
        s.d["parts"].append(p)
        return p
    def box(s, id, b, mat, r=None, **kw): return s.add(id, "box", mat, box=b, r=r, **kw)
    def cyl(s, id, a, b, d, mat, **kw): return s.add(id, "cyl", mat, **{"from": a, "to": b, "d": d}, **kw)
    def tube(s, id, path, d, mat, bend=None, **kw): return s.add(id, "tube", mat, path=path, d=d, bend=bend, **kw)
    def bar(s, id, a, b, sec, mat, r=None, **kw): return s.add(id, "bar", mat, **{"from": a, "to": b}, section=sec, r=r, **kw)
    def sweep(s, id, path, sec, mat, shape=None, bend=None, r=None, **kw): return s.add(id, "sweep", mat, path=path, section=sec, shape=shape, bend=bend, r=r, **kw)
    def strap(s, id, path, sec, mat, bend=None, **kw): return s.add(id, "strap", mat, path=path, section=sec, bend=bend, **kw)
    def coil(s, id, a, b, d, d2, turns, mat, **kw): return s.add(id, "coil", mat, **{"from": a, "to": b}, d=d, d2=d2, turns=turns, **kw)
    def decal(s, id, at, size, face, mat=None, **kw): return s.add(id, "decal", mat, at=at, size=size, face=face, **kw)
    def sphere(s, id, at, d, mat, **kw): return s.add(id, "sphere", mat, at=at, d=d, **kw)
    def lathe(s, id, at, prof, mat, axis=None, **kw): return s.add(id, "lathe", mat, at=at, profile=prof, axis=axis, **kw)
    def loft(s, id, secs, mat, axis=None, **kw): return s.add(id, "loft", mat, sections=secs, axis=axis, **kw)
    def slab(s, id, plane, outline, w, mat, r=None, **kw): return s.add(id, "slab", mat, plane=plane, outline=outline, w=w, r=r, **kw)
    def save(s):
        p = os.path.join(OUT, s.d["id"] + ".json")
        txt = json.dumps(s.d, ensure_ascii=False, indent=None, separators=(", ", ": "))
        txt = txt.replace('"parts": [', '"parts": [\n    ').replace('}, {"id"', '},\n    {"id"')
        open(p, "w").write(txt + "\n")
        print("wrote", p, len(s.d["parts"]), "parts")
def rnd(v):
    if isinstance(v, float): return round(v, 1)
    if isinstance(v, list): return [rnd(x) for x in v]
    if isinstance(v, dict): return {k: rnd(x) for k, x in v.items()}
    return v
def rot(axis, deg, about): return {"axis": axis, "deg": deg, "about": about}
def sec(at, w, d, r, cx, cz): return {"at": at, "w": w, "d": d, "r": r, "cx": cx, "cz": cz}
def rep(n, step): return {"n": n, "step": step}
