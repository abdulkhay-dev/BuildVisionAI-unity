# «Лари» (lari, П3.977) — wave 5b

Catalogue p. 137 (printed 270–271): the interior with 4.02, cut-outs of 4.01 and 4.02 (folded / unfolded), four top decors.
Site: 4.01 two views (one frame face-on), 4.02 four views. No instructions: both **by photo**. Generator `gen/lari.py`;
sheets `pilot/lari-*.png` (ok; refs = the site photos, the top's Ø on the photo as x-scale; 4.01's legs sit on the red
boxes). The chairs of the page (Бруно М, Чикаго М, Фернандо М, Моника Концепт) are skipped.

## Construction
- Tops ЛДСП 25 Ø1000 (the edge measures 24–26 mm), 2 mm edge; four decors = four finishes.
- **4.01** 1000×1000×765: two welded frames of black square tube crossing at 90° under the centre; each: a top rail □40
  under the top, two legs □60 splayed outwards 7.5° (outer width 757 at the top → 906 at the floor, measured face-on) and a
  floor rail □40; the floor rails cross in an X (photo 0).
- **4.02** 1000/1390×1000×770: the round top split across the middle, the halves run out 195 each on a black steel frame
  (820 × 540 × 110 under the top); the insert 390 × 1000 is a butterfly leaf — two 390 × 500 halves stored folded inside the
  frame, raised into the gap by two slides (to 745…770, z 500…1000 / 0…500). Base: a column □120 (y 470…635) and four legs
  □50 to the diagonals, feet ≈ 330 from the centre (the photos: the legs point at the frame's corners).

## Finishes
`lari-beton-layt` #cdcac4, `lari-mramor-nero` #292929, `lari-dub-ontario` #a08357, `lari-dub-kanzas` #74543b — p. 137
swatches (crops in `gen/lari_decors.md`), all textured (provisional). Metal: black («Опоры: металл (черный)»). The
colours index.json lists (Венге, Черный, Табак) are the chairs' paints.

## Sizes
The model size is the **folded** table: 4.02 = [1000, 1000, 770] (index.json had L1390 — corrected); unfolded L1390 in the
model note. The site writes 4.02 unfolded 1350 — the catalogue's 1390 was used.

## For the lead
- The butterfly leaf cannot unfold (no rotation in moves): its halves slide up out of the frame.
- Rods: the checker draws them as their bounding boxes; 4.01's floor rails carry a `box` so the extent reaches the floor.
