# Lift panels (family `panels`)

Generator `panels.py`: the catalogue's own front-view crops (`tools/lifts/reference/panels/<id>.jpg`, already
front-on, no perspective) cleaned up - page background at rounded corners filled from the panel edge, the single
variant kept where a crop shows several (DL300 / DL320: single display; DL500A: the triangle-button single), the
render's lighting gradient divided out (masked low-frequency blur of the steel / glass lightness flattened to its
median), stainless levelled to ~#cccccc neutral grey, gold kept. Check sheet `sheets/panels.png`
(ref | albedo | metallic | smoothness | lit).

Mask: metallic 1 on steel / gold and button rims, 0 on display glass, LED rings and digits, printed marks; black-glass
panels (DC5000A, DL500A) are dielectric everywhere. Smoothness: hairline 0.6, mirror finish (DC1200B) 0.88, glass 0.9 -
0.92. Normal: a gentle relief from the lightness (button rims), flat on glass. maskSize 512 (same as albedo).
No emission: the lit digits / LED rings are albedo only (the importer has no emission for this category).

Each picture keeps the panel's own aspect (w:h below); the engine box should match it or buttons turn oval.
Engine boxes now: COP 0.17 x 1.15 m (0.148) - fits the vertical COPs (0.139-0.154; DC5000A is wider, 0.197);
LOP 0.10 x 0.35 m (0.286) - fits DL300 / DL320 / DL400 / DL450 / DL500A / DL300B / DL100A (0.26-0.31); DL100A
double is 0.461 (needs ~0.16 wide). DC1200A / DC4200A are **horizontal** (1.66 / 1.98, e.g. 0.50 x 0.30 m and
0.40 x 0.20 m) and DC1200B is a handrail strip (17.7:1) - they do not fit the vertical COP box.

| id | kind | layout | px | w:h | finish | metallic mean |
|---|---|---|---|---|---|---|
| liftpanel_dc1000a | cop | vertical | 75 x 512 | 0.146 | stainless-hairline | 0.91 |
| liftpanel_dl300 | lop | vertical | 157 x 512 | 0.307 | stainless-hairline | 0.70 |
| liftpanel_dc1000c | cop | vertical | 76 x 512 | 0.148 | stainless-hairline | 0.92 |
| liftpanel_dl320 | lop | vertical | 145 x 512 | 0.283 | stainless-hairline | 0.87 |
| liftpanel_dc2000a | cop | vertical | 72 x 512 | 0.141 | stainless-hairline | 0.71 |
| liftpanel_dl400 | lop | vertical | 149 x 512 | 0.291 | stainless-hairline | 0.51 |
| liftpanel_dc2000b | cop | vertical | 79 x 512 | 0.154 | titanium-gold-hairline | 0.73 |
| liftpanel_dl450 | lop | vertical | 137 x 512 | 0.268 | titanium-gold-hairline | 0.64 |
| liftpanel_dc5000a | cop | vertical | 101 x 512 | 0.197 | black-glass | 0.00 |
| liftpanel_dl500a | lop | vertical | 147 x 512 | 0.287 | black-glass | 0.00 |
| liftpanel_dc9000a | cop | vertical | 71 x 512 | 0.139 | stainless-hairline | 0.97 |
| liftpanel_dl300b | lop | vertical | 151 x 512 | 0.295 | stainless-hairline | 0.67 |
| liftpanel_dc1200a | cop | horizontal | 512 x 308 | 1.662 | stainless-hairline | 0.97 |
| liftpanel_dc4200a | cop | horizontal | 512 x 259 | 1.977 | stainless-hairline | 0.93 |
| liftpanel_dc1200b | cop | handrail | 512 x 29 | 17.655 | stainless-mirror | 0.99 |
| liftpanel_dl100a | lop | vertical | 135 x 512 | 0.264 | stainless-hairline | 0.83 |
| liftpanel_dl100a_double | lop | vertical | 236 x 512 | 0.461 | stainless-hairline | 0.80 |
| liftpanel_dc1000a_freight | cop | vertical | 73 x 512 | 0.143 | stainless-hairline | 0.92 |

Weak spots: at 512 px the COP is only ~75 px wide, so floor numbers on the buttons are soft (the budget asked for ≤512);
DC1200B (handrail buttons) keeps the handrail's own shading at its ends.
