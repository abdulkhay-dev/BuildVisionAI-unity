# «Плато» (plato, П3.403) — wave 5b

П3.403.0.22 «Стол журнальный» L745/1490 × B800 × H500/770, catalogue p. 140 (printed 276–277: the interior raised and
unfolded, three cut-outs — folded, raised with the leaf opening, raised and unfolded — five decors). No product page, no
instruction: **by catalogue** (scale: L745 / H500 folded, L1490 / H770 unfolded), ±20 mm. Generator `gen/plato.py`; sheet
`pilot/plato-0-22.png` (ok; ref = the folded cut-out, 3/4). Chairs of the page skipped.

## Construction
A box ЛДСП 16 681 × 740 on four castors 50: base board, two full-height sides, back, an open niche 184 under a fixed shelf,
the upper box's front panel 218; the top is two leaves ЛДСП 16 745 × 800 lying one on the other (468…500, overhanging the
box ≈ 32 all round). Two black lift mechanisms inside: base rails on the shelf, four lower arms (fixed), four upper arms and
a plate under the leaves (moving).

## Moves (the transformer)
- `lift`: the plates and upper arms rise 286;
- `unfold_a`: the lower leaf by [−372.5, 286, 0]; `unfold_b`: the upper leaf by [372.5, 270, 0] → the unfolded top 1490 × 800
  at 754…770, centred over the box (the catalogue's H770 / L1490).

## Finishes
`plato-dub-votan` #9b7146, `plato-dub-tryufelnyy` #9c886c, `plato-venge` #2d211b, `plato-dub-kanon` #8b6c4f,
`plato-sosna-kareliya` #e7e7e1 — p. 140 swatches (crops in `gen/plato_decors.md`), textured, provisional. Metal black.

## Sizes
Model size = the folded table [745, 800, 500] (index.json had [1490, 800, 500] — corrected); unfolded in the model note.

## Engine limits for the lead
The real mechanism is a pair of scissor / parallelogram arms and the upper leaf flips over like a book page. With straight
slides only: the arms telescope (a 58 mm gap shows between lower and upper arms when raised) and the upper leaf slides
sideways instead of turning. A hinge-flip move (a door-like turn of 180° about a horizontal axis after a lift) would express
it exactly.
