# «Глобус» (globus, П7.038) — wave 5b

Catalogue p. 64 (printed 125): the 3.18 interior photo («Дуб Каньон»), the cut-outs of 3.12 / 3.18 with tiny interior
schemes, swatches «Сосна Карелия» / «Дуб Каньон». Site: 3.18 — closed (both decors), middle door open (Каньон: a shelf column
with two drawers), left door open (Сосна: two-tier hanging), the scheme; 3.12 («П038.120») — closed and left door open. No
instructions: both **by photo** (heights from the open-door photos, scale = H at the front corner, ±20 mm). Generator
`gen/globus.py` (also writes Мокко). Sheets `pilot/globus-*.png` (ok; refs = the closed 3/4 site photos — the doors' profiles
fall on our door joints).

## Construction (the photos' corners)
- ЛДСП 16: sides on the floor over the full depth 610, the top on them, the bottom between the sides on a plinth 80 set 30
  back (its edge band shows under the doors), ХДФ back in grooves split behind a partition. Partitions / shelves 520 deep.
- Sliding doors between the sides on two tracks (bottom track on the bottom board, top track under the top hiding the doors'
  top); doors 106…2294, framed by aluminium profiles (vertical handle-profiles 20 × 28, top 30 / bottom 40 rails) round a
  ЛДСП 10 filling in the carcass decor; they overlap by 25. 3Д: the middle door on the front track (the photo with the left
  door open shows it hidden behind the middle one); 2Д: the right door in front. `slide` moves by ±(door − 25).
- **3.18** 1800: partitions at 628 / 1108. Left 604: two-tier hanging (rail 2180 under the top, a shelf 1346 with a rail
  1270 under it — the Сосна photo). Middle column 464: shelves 1978 / 1670 / 1362, two inner drawers 1130–1340 / 910–1120,
  shelves 896 / 536 (the Каньон photo). Right 668: rail 2180, shelf 1150 (the scheme only — no photo of it).
- **3.12** 1200: a full-width top shelf 1980 (the partition stops under it); left column 400: shelves 1515 / 1130, drawers
  875–1065 / 684–870, shelves 680 / 380; right hanging section: rail 1920, low shelf 470.
- Inner drawers: inset fronts, no handles (the photos), ЛДСП boxes 420 deep with ХДФ bottoms.

## Finishes
`globus-sosna-kareliya` #e7e7e1 (p. 64 crop 0.79,0.865,0.84,0.905), `globus-dub-kanon` #8a6b4e (crop 0.87,0.865,0.92,0.905);
textured, provisional (`gen/globus_decors.md`). Metal `gold#c0c3c6` — matte silver aluminium profiles and tracks (read off
the photos); rails chrome.

## For the lead
- The interior schemes are tiny bitmaps and disagree with the photos in places (the 3.18 scheme draws a top shelf over the
  left and middle sections; the photo of the left section shows none) — the photos were followed.
- Door profiles are plain boxes (the real handle-profile is a C-section with a rounded grip).
Sizes as in the catalogue. Skipped: nothing.
