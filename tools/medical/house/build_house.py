"""Builds the house/1 document of the rehabilitation centre with all catalogue devices (python3 build_house.py out.json).

Eight halls (one per library section) on two sides of a corridor; devices packed in rows from the back wall, fronts
towards the door: wall devices on the back wall, desk devices on counters, ceiling devices hung from the ceiling."""
import json, os, sys, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RES = os.path.join(ROOT, "Assets/House4696/Resources/Medical")
cat = {m["id"]: m for m in json.load(open(f"{RES}/catalog.json"))["models"] if not m["id"].startswith("_")}
order = [i for b in json.load(open(os.path.join(ROOT, "tools/medical/batches.json"))) for i in b["ids"]]
order = [i for i in order if i in cat] + [i for i in cat if i not in order]
QUOTA = json.loads(os.environ.get("QUOTA", "{}"))   # {"physio": 8, ...}: that many devices per section, evenly spread
H = 3.2            # storey height
ROOMD = float(os.environ.get("ROOMD", "20"))       # room depth
FREE = 2.4         # kept free in front of the door
CORR = 3.0
T = 0.4            # exterior wall
SECTIONS = [("physio", "Физиотерапия"), ("table", "Столы и кушетки"), ("hydro", "Гидро- и термотерапия"),
            ("kinesio", "ЛФК и тренажёры"), ("robot", "Реабилитационные роботы"), ("pediatric", "Детская реабилитация"),
            ("sensory", "Сенсорная комната"), ("other", "Медоборудование")]
if QUOTA:
    keep = []
    for key, n in QUOTA.items():
        ids = [i for i in order if cat[i]["category"] == key and max(json.load(open(f"{RES}/Designs/{i}.json"))["size"][:2]) <= 3000]
        keep += [ids[int(k * len(ids) / n)] for k in range(n)]
    order = keep
    cat = {i: cat[i] for i in order}
size = {}
for i in order:
    d = json.load(open(f"{RES}/Designs/{i}.json")); size[i] = [v / 1000.0 for v in d["size"]]

def pack(ids, W, spread=None):
    """Rows from the back wall. Returns (placements, counters, depth); v = offset of the back of the item from the
    back wall. Each row is centred across the room; with `spread` (usable depth) the spare depth goes between the rows."""
    walls = [i for i in ids if cat[i].get("mount") == "wall"]
    ceil = [i for i in ids if cat[i].get("mount") == "ceiling"]
    desk = [i for i in ids if cat[i].get("mount") == "desk"]
    floor = [i for i in ids if cat[i].get("mount", "floor") == "floor"]
    rows = []   # (kind, [(id, x-from-left-edge-of-row, w)], row depth, gap after, x gap)
    def split(items, kind, pad_d, gapx):
        x, rowd, row = 0.0, 0.0, []
        for i in items:
            w, d, _ = size[i]
            if x + w > W - 0.8 and row:
                rows.append((kind, row, rowd, pad_d, x - gapx)); x, rowd, row = 0.0, 0.0, []
            row.append((i, x + w / 2)); x += w + gapx; rowd = max(rowd, d + (0.3 if kind == "desk" else 0.0))
        if row: rows.append((kind, row, rowd, pad_d, x - gapx))
    split(walls, "wall", 0.8, 0.5)
    split(desk, "desk", 1.0, 0.3)
    split(floor, "floor", 1.0, 0.6)
    used = sum(r[2] + r[3] for r in rows) - (rows[-1][3] if rows else 0.0)
    extra = max(0.0, (spread - used) / max(1, len(rows))) if spread else 0.0
    out, counters, v = [], [], 0.0
    for k, (kind, row, rd, pad, rowW) in enumerate(rows):
        off = (W - rowW) / 2           # centre the row
        if kind == "wall":
            for i, cx in row: out.append((i, off + cx, 0.0, 0.0))
        elif kind == "desk":
            x0 = off + min(cx - size[i][0] / 2 for i, cx in row) - 0.15; x1 = off + max(cx + size[i][0] / 2 for i, cx in row) + 0.15
            counters.append((x0, v, x1, v + rd))
            for i, cx in row: out.append((i, off + cx, v + 0.15, 0.78))
        else:
            for i, cx in row: out.append((i, off + cx, v, 0.0))
        v += rd + pad + (extra if k < len(rows) - 1 else 0.0)
    # ceiling devices hang over the aisle in front of the rows, spread across the room
    if ceil:
        step = W / (len(ceil) + 1)
        for k, i in enumerate(ceil):
            out.append((i, step * (k + 1), min(v + 0.4, (spread or v) + 0.2), H))
    return out, counters, v

rooms = []
for key, name in SECTIONS:
    ids = [i for i in order if cat[i]["category"] == key]
    W = 8
    while True:
        out, counters, depth = pack(ids, W)
        if depth <= ROOMD - FREE: break
        W += 1
    out, counters, depth = pack(ids, W, ROOMD - FREE)
    rooms.append(dict(key=key, name=name, ids=ids, W=W, out=out, counters=counters, depth=depth))

# two rows of rooms: greedy balance by width
south, north, ws, wn = [], [], 0, 0
for r in sorted(rooms, key=lambda r: -r["W"]):
    if ws <= wn: south.append(r); ws += r["W"]
    else: north.append(r); wn += r["W"]
south.sort(key=lambda r: [k for k, _ in SECTIONS].index(r["key"])); north.sort(key=lambda r: [k for k, _ in SECTIONS].index(r["key"]))
WIDTH = max(ws, wn) + 3.0          # a lobby 3 m wide at the west end
x0 = T                              # inner west face
z_s0, z_s1 = T, T + ROOMD           # south rooms
z_n0, z_n1 = T + ROOMD + CORR, T + 2 * ROOMD + CORR
inner_w = WIDTH
X1 = x0 + inner_w
outer = [[0, 0], [X1 + T, 0], [X1 + T, z_n1 + T], [0, z_n1 + T]]

doc = dict(format="house/1", meta=dict(name=os.environ.get("HOUSE_NAME", "Реабилитационный центр: все аппараты каталога"),
           description=os.environ.get("HOUSE_DESC", "Одноэтажный центр: 8 залов по разделам библиотеки, все аппараты Xiangyu Medical"), author="AI"),
           levels=[dict(id="ground", name="1 этаж", elevation=0.3, height=H, slab=0.3)],
           walls=[], openings=[], rooms=[], roofs=[], items=[], elements=[], lights=[])
for k, (a, b) in enumerate(zip(outer, outer[1:] + outer[:1]), 1):
    doc["walls"].append(dict(id=f"w{k}", level="ground", a=a, b=b, outside="render#e9e4da", plinth=0.45, thickness=T))
def iw(id, a, b): doc["walls"].append(dict(id=id, level="ground", kind="interior", a=a, b=b))
def hole(id, wall, at, w=2.0): doc["openings"].append(dict(id=id, wall=wall, type="hole", at=at, width=w, sill=0, height=2.4))

# corridor walls are per room (a door in each); partitions between rooms
# the shorter row of halls shares the spare width (devices stay centred), so both rows end at the east wall
for row_ in (south, north):
    spare = (WIDTH - 3.0 - sum(r["W"] for r in row_)) / len(row_)
    for r in row_: r["dx"] = spare / 2; r["W"] += spare

def place(row, zdoorwall, zback, sign, rot, rooms_):
    x = x0 + 3.0
    for r in rooms_:
        xa, xb = x, x + r["W"]
        r["xa"], r["xb"], r["side"] = xa, xb, "south" if sign > 0 else "north"
        wid = f"c-{r['key']}"
        iw(wid, [xa, zdoorwall], [xb, zdoorwall]); hole(f"d-{r['key']}", wid, r["W"] / 2 - 1.0)
        if xb < x0 + WIDTH - 0.01:
            iw(f"p-{r['key']}", [xb, z_s0 if sign > 0 else z_n0], [xb, z_s1 if sign > 0 else z_n1])
        doc["rooms"].append(dict(id=f"r-{r['key']}", name=r["name"], level="ground", type="other",
                                  outline=[[xa, z_s0 if sign > 0 else z_n0], [xb, z_s0 if sign > 0 else z_n0],
                                           [xb, z_s1 if sign > 0 else z_n1], [xa, z_s1 if sign > 0 else z_n1]], floor="tile"))
        for (cx0, cv0, cx1, cv1) in r["counters"]:
            cx0 += r["dx"]; cx1 += r["dx"]
            if sign > 0: mn, mx = [xa + cx0, 0.0, zback + cv0], [xa + cx1, 0.75, zback + cv1]
            else: mn, mx = [xa + cx0, 0.0, zback - cv1], [xa + cx1, 0.75, zback - cv0]
            doc["elements"].append(dict(id=f"cnt-{r['key']}-{len(doc['elements'])}", type="platform", min=[mn[0], 0.3, mn[2]],
                                        max=[mx[0], 0.3 + 0.75, mx[2]], material="oak_light", top="porcelain"))
        for (i, cx, v, y) in r["out"]:
            w, d, h = size[i]; mt = cat[i].get("mount", "floor")
            z = zback + v if sign > 0 else zback - v
            py = y
            if mt == "wall": py = max(h / 2 + 0.1, 1.3)
            if y and mt == "desk": py = y
            if mt == "ceiling": py = H
            doc["items"].append(dict(id=f"i-{i}", model=i, level="ground", position=[round(xa + r["dx"] + cx, 3), round(py, 3), round(z, 3)], rotation=rot))
        x = xb
    return x
place(0, z_s1, z_s0, +1, 0, south)       # south hall: back wall at the south, fronts to the north
xe = place(0, z_n0, z_n1, -1, 180, north)  # north hall: back wall at the north, fronts to the south
# corridor ends and the lobby: the corridor runs along the whole width; partitions of the lobby
iw("lobby-s", [x0 + 3.0, z_s0], [x0 + 3.0, z_s1]); iw("lobby-n", [x0 + 3.0, z_n0], [x0 + 3.0, z_n1])
doc["rooms"].append(dict(id="r-corridor", name="Коридор", level="ground", type="corridor", floor="tile",
                         outline=[[x0, z_s1], [X1, z_s1], [X1, z_n0], [x0, z_n0]]))
doc["rooms"].append(dict(id="r-lobby-s", name="Холл", level="ground", type="hall", floor="tile",
                         outline=[[x0, z_s0], [x0 + 3.0, z_s0], [x0 + 3.0, z_s1], [x0, z_s1]]))
doc["rooms"].append(dict(id="r-lobby-n", name="Холл", level="ground", type="hall", floor="tile",
                         outline=[[x0, z_n0], [x0 + 3.0, z_n0], [x0 + 3.0, z_n1], [x0, z_n1]]))
# main entrance in the west wall (w4: from the north-west corner down to the south-west one), into the corridor
doc["openings"].append(dict(id="entry", wall="w4", type="entryDoor", at=(z_n1 + T) - (z_s1 + CORR / 2) - 0.6, width=1.2, sill=0, height=2.3))
doc["roofs"].append(dict(id="roof", type="flat", outline=outer, parapet=0.3))
# high windows above the devices standing at the back walls (sill 1.9 m): two per hall, one at the corridor's east end
XO = X1 + T
for r in south + north:
    # tall devices at the back wall (rows starting ≤ 0.4 m from it) would cover a window: keep the windows clear of them
    tall = [(r["xa"] + r["dx"] + cx - size[i][0] / 2 - 0.1, r["xa"] + r["dx"] + cx + size[i][0] / 2 + 0.1) for (i, cx, v, y) in r["out"]
            if v <= 0.4 and y < H and size[i][2] + y > 1.85]
    spots = [f for f in (0.3, 0.7, 0.15, 0.85, 0.5) if not any(a < r["xa"] + f * (r["xb"] - r["xa"]) + 0.8 and b > r["xa"] + f * (r["xb"] - r["xa"]) - 0.8 for a, b in tall)][:2]
    for k, f in enumerate(spots):
        cx = r["xa"] + f * (r["xb"] - r["xa"])
        if r["side"] == "south": doc["openings"].append(dict(id=f"win-{r['key']}-{k}", wall="w1", type="window", at=round(cx - 0.8, 3), width=1.6, sill=1.9, height=0.9))
        else: doc["openings"].append(dict(id=f"win-{r['key']}-{k}", wall="w3", type="window", at=round(XO - cx - 0.8, 3), width=1.6, sill=1.9, height=0.9))
doc["openings"].append(dict(id="win-corridor", wall="w2", type="window", at=round(z_s1 + CORR / 2 - 0.8, 3), width=1.6, sill=0.9, height=1.6))
# a few walk views for the presentation
doc["views"] = [dict(name="Фасад", type="orbit", yaw=200, pitch=18, distance=0)]
for r in south + north:
    cx = (r["xa"] + r["xb"]) / 2
    if r["side"] == "south": doc["views"].append(dict(name=r["name"], type="walk", position=[cx, 0.3, z_s1 - 0.6], yaw=180, pitch=-12))
    else: doc["views"].append(dict(name=r["name"], type="walk", position=[cx, 0.3, z_n0 + 0.6], yaw=0, pitch=-12))
json.dump(doc, open(sys.argv[1], "w"), ensure_ascii=False)
tot = sum(len(r["ids"]) for r in rooms)
print("devices", tot, "items", len(doc["items"]), "rooms", [(r["key"], r["W"], round(r["depth"], 1)) for r in rooms], "inner", X1 - x0, "x", z_n1 - z_s0)
