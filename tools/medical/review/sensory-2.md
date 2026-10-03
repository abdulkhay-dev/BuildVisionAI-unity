# Detail review: batch sensory-2 (11 devices)

Reviewer pass of 2026-10-03. I compared every device on `renders/<id>-compare.png` with the photo, enlarged on its own
and measured in pixels where the photo allowed it. I fixed the generators (`gen/s2_*.py`, `gen/s2lib.py`) and
regenerated the designs. Every design was re-rendered `ok` and checked again on a fresh compare sheet.
`s2lib.panel()` got two optional parameters, `grille_off` and `logo_d`. Their defaults keep the old look.

## sound-and-light-wall-panel
Differences found and fixed:
- The LED dots were square; the photo's are round. They are now Ø 12 discs.
- Colour band: above the 7 bright rainbow rows, every dot was black. The photo shows each column's own colour
  darkened, with only the top 2–3 dots black. It is now drawn that way: bright rows, then darkened colour, then black.
  The hue now runs from blue to violet, as on the photo (the old range ended at magenta).
- The display was flat grey. It is now 6 grey bands, darker at the top (the photo measures 213 → 228).
- The bezel and display were narrower than on the photo. The measured sizes are now bezel 74–516 × 118–822 and
  display 90–500 × 135–803.
- The ears were too small (r 73). On the photo they measure r 87, centred at (87, 813), with the body top at 880.
- The ear grilles are now in the upper-outer part of the ears, as on the photo. Each is Ø 60.
- The logo disc was too small: it is now Ø 44, measured.

The format cannot match: the photo's dot grid is denser and slightly irregular inside the band (the photo is too
low-resolution to copy dot by dot), and the display has no emissive glow.

## wall-of-blisters
Differences found and fixed:
- Pattern: the old one was a coarse random 32 × 52 pattern with too much white. The bubble picture is now sampled from
  the photo's own panel on a 40 × 72 grid (left half, mirrored about the seam as on the photo). It is reduced to 8
  blues by k-means, and the 3 lightest are lifted towards white. Light at the top and bottom, a deep-navy middle, the
  diamond pattern and the vertical streaks now follow the photo. Each column's runs are merged into one box each, so
  the panel takes 62 parts.
- The centre seam was dark. On the photo it is a thin grey-blue line; it is now drawn that way.
- The ears, grilles and logo are corrected to the photo's measurements (r 88, centred at (88, 812); grille offset;
  logo Ø 44). The bezel is now 79–491 × 125–811.

The format cannot match: the photo's finest bubble sparkle is below the grid size. There is no picture material,
because the inventory has no screenCrop and the external catalogue is out of scope.

## smell-perception-game-box
Differences found and fixed:
- Everything right of the dots was ≈ 17 mm too far left. On the photo the colour strip is at x 222–256 (not
  206–238), the squares at x 310–364 (not 293–346), and the scent outlets are Ø 56 centred at x 448 (not Ø 61 at 428).
  The rows are now at y 650 / 527 / 405 / 284.
- The colour strip is now red | yellow | green at 10 mm each, as on the photo (the stripes were too thin).
- The inner panel's frame was almost invisible. The photo shows two darker-pink lines (the lip edge and the groove),
  and both are now drawn in darker pink, at the measured places.
- The ears are now r 90, centred at (90, 810), with the body top at 873. The grilles and the logo (Ø 40) are moved to
  their measured places. The case colour is matched to the photo sample (#d286b8).

Left as is: nothing visible at the compare scale.

## variable-speed-fan-game-box
Differences found and fixed:
- The fan grilles were black. On the photo they are dark navy (≈ #1d3f58). Two concentric guard rings and slightly
  brighter blades were added.

Left as is: the bottom corner bumps have a small "paw" notch on the CAD picture; here they are rounded squares with
a ring.

## music-training-device
Differences found and fixed:
- The pad corners were chamfered at 28 mm; the photo's are round. The pad ends now follow a quarter circle of
  r 42, so both the lower corners on the side and the inner corners on the top are round.

Checked and matching: the spot pairs on the front and right faces (photo left and right faces), their size and
colour, the plinth arches and the pad extent.
Left as is: the faint embossed "flower" on the top centre (one embossed ring).

## piano-water-column
Differences found and fixed:
- The mirror back and the left inner mirror rendered flat grey in the studio. On the photo they reflect the dim
  room: dark navy-teal. They are now dark glossy glass of that colour (#1f3a50 / #2b4a5e). The niche reads as on the
  photo.
- The bubbles were sparse. They are now dense fizz: ≈ 3 small white discs per 12 mm of height, on the front and
  inside each tube.
- The tube colours were pastel. They are now the photo's saturated pink, blue, cyan, green, yellow, orange and red.
- The colour keys were too small (44 wide). They are now 64 × 38, as on the photo.
- The button ring was light metal. The photo's ring is dark grey-teal, and it is now that colour.

The format cannot match: the light glow of the tubes and the white platform (no emissive light on a white studio
background). The square tubes are kept; the photo's first, clear tube may be round.

## sensory-soft-ball-pool
Differences found and fixed:
- The colours of the side and back blocks were guessed. Read from both photos, they are now:
  - back wall: red | green | red (top of photo 1);
  - left wall: green at the front, red at the back;
  - right wall: red at the front, green at the back.

  Photo 2 is the front-right corner: front green, front red | corner | right red, right green. The angle render now
  shows exactly that sequence. The side walls are now 2 blocks each (the old design had 3 + 2).

Left as is: the pool depth (1500, the inventory estimate). The balls are glossy; on photo 2 they look slightly matte.

## sound-amplifier
Differences found and fixed:
- Layout: the speakers stood beside the amp (a set 1310 wide). The catalogue picture puts the speakers above the
  amp, and it is to one scale: the right speaker's front is 140 × 112 px against the amp's 305 px = 430 mm. The two
  speakers (each ≈ 205 × 160 × 150) now stand side by side on the amplifier, and the set keeps the amp's footprint
  (430 × 330, H 325).
- The VU meters were round. On the photo they are upright ovals (≈ 62 × 80): a glowing blue ring round a grey face,
  with gold ticks. They are inside the gold frame line.
- The blue buttons were round discs. On the photo they are rounded squares.
- The lower strip was silver. On the photo it is dark graphite, and the knob positions are re-measured. The USB and
  SD slots now sit in a black bezel, as on the photo.

The format cannot match: the left speaker on the photo is turned for display; here both stand upright. The real
speaker size is uncertain, because the picture is a composite.

## symphony-hemisphere-light
Differences found and fixed:
- The dome was a smooth, opaque white shell. It is now faceted: 7 polygonal frustum bands, every other one turned
  half a facet, in translucent grey-white acrylic. A dark LED-lens cluster sits inside, as on the photo.
- The ring band was a white band. It is now clear, 16-sided glass over the black interior, with the silver line under
  it, as on the photo.
- The front plate was too small and low (y 0–84). It is now 124 × 64 at y 22–86, flush over the body, and the logo
  block and text lines are larger.
- The foot bracket was 6 mm thick. It is now 116 × 23, measured.
- The remote lay flat. The photo shows it standing; it now stands upright, facing front, to the right of the light.
  It has the 2 red keys, the middle key, 3 × 3 small dark keys, and a white lower panel with 3 × 3 black round keys
  (the old panel was grey).

The format cannot match: the photo's sparkle inside the crystal dome. The cord is a loose loop, not the photo's
bundled figure-of-eight.

## visual-perceptual-trainer
Differences found and fixed:
- The glow was weak on white. The pink tubes now have a light-pink core (#f7a6dc) under saturated pink acrylic, and
  the short tubes have a bluer tint. Every tube has a bright white glowing foot, as on the photo.
- Height: on the photo the tall tubes are ≈ 7.6 × their diameter (≈ 1400). H goes from 1500 to 1420, and the tall
  tubes are 1400.

The format cannot match: real light (bloom on the floor, coloured spill). The cube is a separate inset picture on
the photo; here it stands on the floor to the right.

## multimedia-scenario-interactive-system
Differences found and fixed:
- The neck was a thick Ø 44 post. The photo shows a thin rod; it is now Ø 16 with a small base.
- The lens was dark. The photo shows it lit (bright white); it is now that way.
- The sensor was at the middle right. It is now a dark window at the lower right.
- The green LED does not exist on the photo; it is replaced by the photo's small grey label at the upper left.
- The shell colour is now the photo's warm white (#ebe8e2).

The format cannot match: the projected floor game is light on the floor. The unit hangs from its top in placement.
