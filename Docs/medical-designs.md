# Medical device designs (`Resources/Medical`)

Rehabilitation and physiotherapy equipment of the manufacturers' catalogues, placeable in houses like furniture
(`items[].model` = the device id). `Resources/Medical/catalog.json` lists the models; each has a design
`Resources/Medical/Designs/<id>.json` — the device as a list of its visible parts. Engine: `Runtime/Medical/MedBuilder.cs`.

## Frame and units

Millimetres. **x** from the left seen from the front, **y** up from the floor, **z** from the back: the front of the
device (where the screen, the patient's seat or the control panel faces) is at `z = depth`. `size` = [W, D, H] — the
overall width (x), depth (z) and height (y). In the house the item's origin is the middle of its back on the floor;
`rotation` turns its front. Wall devices (`mount: "wall"`) hang from their middle.

```json
{
  "id": "xy-k-cdb-iv",
  "size": [560, 600, 1250],
  "mats": { "shell": "plastic#f2f3f5", "accent": "plastic#2f8fd8", "frame": "metal#c9ccd0", "dark": "plastic#3a3f45", "pad": "leather#5b86b8" },
  "parts": [ { "id": "base", "kind": "box", "box": [30, 90, 30, 530, 190, 570], "r": 45, "mat": "shell" }, … ]
}
```

## Materials

`mats` maps roles to materials; a part's `mat` names a role or a material directly.

| spec | look |
|---|---|
| `plastic#hex` | satin moulded plastic (fine orange-peel), the default for housings |
| `gloss#hex` | glossy plastic / lacquer (buttons, glossy covers, indicator lamps) |
| `metal#hex` | brushed stainless / aluminium (frames, rails, columns) |
| `chrome` | polished chrome (castor forks, knobs, poles) |
| `black`, `black#hex` | black painted metal |
| `rubber`, `rubber#hex` | tyres, grips, feet |
| `leather#hex` | upholstery (PU leather: tables, seats, pads) |
| `fabric#hex` | textile (straps, harnesses, soft covers) |
| `screen` | a dark switched-off display |
| `glass` | clear glass / acrylic (goes to the glass mesh: no collider, no shadow) |
| `mirror`, `wood#hex` | mirror, light wood |
| any library material | e.g. `med_xy-k-cdb-iv_screen` (a picture prepared for this device), optionally `#hex` tinted |

## Parts

Every part: `id`, `kind`, `mat`, optional `soft: true` (no collider: cables, lamps, thin knobs, decals),
`rot` {`axis` x|y|z, `deg`, `about` [x,y,z]} (+deg about x turns y towards +z; about y turns z towards x; about z
turns x towards y), `mirror: "x"` (also the copy mirrored about the middle of the width), `copies` [[dx,dy,dz], …]
(more copies shifted by these offsets; each copy is mirrored too when `mirror` is set).

| kind | fields | use |
|---|---|---|
| `box` | `box` [x0,y0,z0,x1,y1,z1], `r` edge radius, `puff` (mm the faces bulge: cushions, mattresses) | housings, pads, plates, seats |
| `cyl` | `from`, `to` [x,y,z], `d`, `d2` (tapers to d2), `sides` | columns, poles, legs, axles, handles, grips |
| `tube` | `path` [[x,y,z], …], `d`, `bend` (corner radius) | bent tube frames, rails, U-handles, cables (`soft`) |
| `lathe` | `at` [x,y,z], `profile` [[r,h], …] from the base, `axis` y (default) / x / z, `caps` | knobs, lamp heads, round bases, treatment heads, cups |
| `sphere` | `at`, `d` or `radii` [rx,ry,rz] | balls, joints, round knobs |
| `slab` | `plane` front (x/y, extruded along z) / side (z/y, along x) / top (x/z, along y); `outline` (SVG path, absolute mm in the plane's axes) + `w` [from,to] along the normal, or `box` (+ `radii` [corner radius]); `r` edge rounding | shaped side panels, curved frames, arches, contoured pads, bases with notches |
| `loft` | `sections` [{`at`, `w`, `d`, `r`, `cx`, `cz`}, …] along `axis` (y default: at = height; sections centred at (cx, cz), w across x, d across z, r = corner radius; axis x: w across z, d across y; axis z: w across x, d across y) | tapered columns, smooth curved housings, shells of carts, robots, capsules |
| `screen` | `box`, `r`, `face` front/back/left/right/top, `print` (picture material), `bezel` | displays, touch panels, control faces |
| `caster` | `at` [x,0,z] (floor point of the wheel), `d` (default 75) | swivel castors under carts, tables, frames |
| `wheel` | `at` (centre), `d`, `d2` width, `axis` x/y/z | big wheels, pulleys, rollers |
| `bar` | `from`, `to`, `section` [w, h], `r` (corner), `roll` | straight square / rectangular tubes and posts at any angle (frames, uprights, arms) |
| `sweep` | `path`, `section` [w, h], `shape` rect (rounded by `r`) / oval / round, `bend`, `roll`; `rib` + `pitch` | oval or rectangular profiles along a bent path: treadmill uprights, handlebars, curved frames; ribbed = corrugated hose |
| `strap` | `path`, `section` [width, thickness] (default 40 × 3), `bend`, `roll` | harness straps, belts, Velcro bands, cords that are flat |
| `coil` | `from`, `to`, `d` (coil diameter), `d2` (wire), `turns` | coiled cables of hand controllers and pendants |
| `decal` | `at` (centre on the face), `size` [w, h], `face`, `mat` or `print` | logos, labels, coloured stripes and markings on a flat face |

Also: `tube` takes `rib` + `pitch` (corrugated hose); `loft` takes `dome` start/end/both (+ `domeH`) for rounded ends
(capsules, tubs, covers); every part takes `repeat` {`n`, `step` [dx,dy,dz], `local`} (a row of n copies: vents, slats, keys; `local: true` steps in the part's turned frame — a row along a tilted face).
A `slab` outline with an inner subpath makes a hole (perforated discs, grilles). Materials also take `acrylic#rrggbbaa`
(solid-looking translucent coloured plastic; no collider). **Screens**: when the inventory has a `screenCrop` for the
device, use `"print": "med_<id>_screen"` on its main screen — the picture of its interface.
**Loft axes** (section centre and size): `axis: "y"` — `cx` = x, `cz` = z, `w` across x, `d` across z;
`axis: "z"` — `cx` = x, `cz` = **y**, `w` across x, `d` across y; `axis: "x"` — `cz` = z, `cx` = **y**, `w` across z,
`d` across y.

Curves: a `slab` with an SVG `outline` (M L H V Q C A Z) gives any 2D shape extruded and edge-rounded; a `loft` gives
smoothly changing rounded-rectangle sections (a circle = r of half the size). Combine with `rot` for tilted parts.

## Quality bar

The model must read as THIS device at a glance from 2–3 m in a room: overall proportions and silhouette right, the
main masses as smooth rounded shells (not bare boxes), the colour scheme of the photo (white/light grey bodies, the
brand's blue accents, black/grey details), screens where the device has them, real castors, handles, pads, rails.
Small details (screws, labels, buttons) only when they are visible at 2 m.
