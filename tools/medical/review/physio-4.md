# physio-4 — detail review (2026-10-02)

Each device was compared with the catalogue photo(s) at full size and on its compare sheet. Generators were edited
(`tools/medical/gen/p4_*.py`) and regenerated until no difference was visible at compare-sheet scale. All 14 render `ok`.
The originals of the edited generators and of the two screen crops are in this session's scratch folder.

**Screen crops (Unity needs a refresh):** the screen crops of `xy-k-sjjd-ii` and `xy-k-czr-iii` were perspective-corrected
and cropped to the display (`tools/medical/reference/<id>_screen.jpg`, and the albedo in
`External/Materials/med_<id>_screen/` was rewritten the same way `textures/screens.py` does it). Unity has not reimported
the changed jpgs yet, so the current renders still show the old crops: blue background at the corners of the sjjd-ii
monitor, and grey housing corners on czr-iii. After the next asset refresh (focus the editor, or Assets → Refresh), touch
the two jsons to get new renders.

## xyd-iii (electroacupuncture unit)
- Fixed: the knobs were flat white washers with blue buttons. They are now tall white fluted bodies (14-sided) with blue
  domed caps of the same diameter. Each knob has a white index mark and a 270° white scale arc (gap at the front).
- Fixed: the bottom band was light grey, 12 mm tall, and the jacks were on the white face. The band is now dark grey
  (#5f6566), about 40 % of the front, and the 6 jacks sit in it, as in the photo.
- Fixed: the panel colour is now the photo's blue-grey (#7a8b99). Added the LED connecting line with its ticks and the
  OUTPUT(1-6) bracket with its ticks down to the jacks. The power rocker is now a square black frame with a rocker.
  The body is 48 mm tall, so the knob tops reach 65 mm = the size.
- Not matched: the Chinese/English text is drawn as bars, the knob numbers and OFF/MAX as small bars, and the knob
  flutes come from the facets only (the format has no fluted profile).

## xy-k-pdj-ii (pelvic floor trainer, pole trolley)
- Fixed: the screen was dark. The photo shows a white touch UI, and the device has no crop. The display is now white
  with 2 rows × 4 light tiles with pink icons and text, plus a blue header with 2 keys. On a tilted part, copies are
  offset in world space, so the second row's offset follows the tilt.
- Fixed: the tablet was a uniform tilted slab. It is now a wedge (deep at the foot, thin at the top), with pink sides
  and a white front frame. The control strip under the screen is white, not pink. The 3 sockets are dark navy with grey
  centres, and the pink end knobs are bigger (Ø42) and carry index marks.
- Fixed: the castors now have big pink hub caps that show; before, they were hidden inside the wheel. The legs are
  wider and flatter, with turned-down ends over the castors. The storage box has a thicker pink lid and a handle slot
  with a light inner. The tray has a darker pink rim. The probe cradle is a pink fork with a grey probe. Added the pink
  label low on the column.
- Not matched: the photo is low-resolution and hazy, so the number of base legs cannot be read (kept 5). The real legs
  are curved organic plates; here they are straight bars.

## xy-k-pdj-iv (portable pelvic floor trainer)
- Fixed: the side spines were flat pink plates. They are now the photo's keyhole shape: a rounded strip with a groove
  that ends in a round lobe around the power button (ribbed white ring, chrome centre, symbol). The sockets are grey
  rings with dark centres.
- Fixed: the rocker is now only on the right side, at the front edge. The left side has a recessed USB plate with
  2 ports, a round jack and a small hole, placed higher, where photo 2 shows them.
- Fixed: the screen glass now sits flush; before, it stood proud and showed a dark edge line. The knobs are lower
  (y 72), with white index arcs. The labels are slanted grey pills with the channel letter, at the lower left of each knob.
- Not matched: the knob knurling (plain lathe). The text is drawn as bars.

## xy-k-sjjd-ii (EMG biofeedback workstation)
- Fixed: the monitor was a thick dark slab. It is now thin, with silver-grey edges and a narrow black border.
- Fixed: the screen crop was a perspective shot with a wide blue background. It is now corrected to the display (see
  the note above; it shows after a Unity refresh).
- Fixed: the castors now have light grey hubs. The base legs are broader (92 × 46). The deck's connector knobs are on
  the front rim: a light pair at the left and a dark pair left of the middle. The blue-grey pair stays on the top at
  the right.
- Not matched: the main photo shows the monitor switched off (black). The model uses the JDSW-VIII UI, as the brief
  asks for a screen crop.

## xy-k-siss-c / xy-k-sjd-c (NMES / TENS carts)
- Fixed (the main difference): the socket panel and the doors were left-aligned and narrow (0.6 of the front). In the
  photos they are centred and about 3/4 of the front width. Both are now centred: socket frame x 142–448, doors
  138–452. The door handles and the warning triangle are centred with them.
- Fixed: the inner socket panel was hidden behind the frame's front face, so the whole window read as one teal/grey
  block. It now sits in front of the frame (white-grey panel inside a coloured frame), with the sockets moved forward.
- Fixed: the logo moved right (to ~x 225–330, as in the photo). The NMES/TENS letter column, line and squiggle moved to
  x 374–400, and the coloured tag moved to x 417 with white character blocks. The castor tyres are lighter grey.
- Not matched: the letters and the Chinese tag are colour blocks. The top touch panel is plain glass.

## xy-k-siss-a-table / xy-k-sjd-a-table (desktop NMES / TENS)
- Fixed: the socket window was a flat light-blue plate standing proud of the front. It is now a recessed window: a
  translucent-looking light frame (a ring), a grey-blue panel set back behind it, the 6 sockets in its upper part, a
  lighter lower lip, and the coloured label bar at the lower right, as in both photos. The window is taller (y 38–158).
- Fixed: the 3 channel blocks on the black top start ~1/4 of the width in, leaving the left area for the logo, as in
  the photos.
- Not matched: the printing on the glass top is block outlines with grey LED windows and key dashes. The staggered
  perspective of the blocks in the photos is a photo effect (they are parallel).

## xy-k-lc-2 (pneumatic compression box)
- Fixed: the front was flat. The bezel now bows forward in plan: an arc 28 mm proud at the middle, built from 3 bowed
  top-plane slabs (bottom lip, recessed connector strip, upper bezel). The label panel follows the same curve, and the
  decals are placed on it.
- Fixed: the blue border was a closed ring around the panel. In the photos it is a U: down the left, along the bottom,
  up the right, with nothing across the top. The panel now has white margins, the top margin wider.
- Fixed: the LED windows show red digit blocks (3 + 3 + 1) with labels. Added 2 rows of round indicator lamps and an
  outlined leg graphic. The hose connectors are white housings with navy slots and 4 red pins (they were gold). The
  body behind the bezel is a slightly darker grey than the bezel.
- Not matched: the leg graphic is a white outlined bar, not the drawing. The text is drawn as bars.

## xy-k-wic-1 (pneumatic compression, 2 knobs)
- Fixed: added a lower shell (skirt) under a seam ridge, slightly wider than the upper shell, as in the photo. The
  blue base is raised on 4 blue corner feet.
- Fixed: the hump is a wider trapezoid with sloping shoulders (x 36–364 at its foot). It was narrow and box-like.
- Fixed: the knob grip ridges are turned diagonal (bars in the tilted face's world coordinates; they were horizontal).
  Added the blue pressure arc around the left knob and the tick marks around the right one.
- Not matched: the photo's top surface rises softly into the hump. Here it is a separate rounded trapezoid, because the
  format has no blended surface. The scale numbers and text are drawn as bars or ticks.

## xy-k-lc-5 (pneumatic compression cart)
- Fixed: the screen was dark, but the photo shows a light UI and the device has no crop. The screen is now light, with
  a blue leg-chamber drawing, an icon column at the right and text lines.
- Fixed: the side handle bars ran only over the middle of the depth. They now run from a mount near the front corner
  back past the cabinet (z 60–420), as in the photo, where the bar's front mount is at the front corner.
- Not matched: in the photo the cabinet flares smoothly into the corner feet. Here the plinth is a separate lobed slab.

## xy-k-czr-ii (magnetic vibration heat cart)
- Fixed: the body, frame and panels were bright white. The photo shows light grey (#dee1e6 front, #d1d1d1 side), so
  the colours are now plastic #e3e5e8, frame #d8dbdf, panels #eaedf0. The head's label panel is the photo's darker
  warm grey (#a9a7a7).
- Checked with no change needed: the orange U handles, the drawer notches at the top edges, the vertical door text, the
  dark socket strip, the vents and the splayed plinth.
- Not matched: the vent-hole grids are dot rows, and the keys and text on the label panel are flat bars.

## xy-k-cdb-iv (shortwave cabinet, printed 430×330×830)
- Fixed: the control head was wider and deeper than the body, overhanging it. In the photo it is flush: same width and
  depth, with a seam at ~640. The head is now x 25–405, z 15–301, and its front rolls into the sloping membrane top.
  The dark corner trims stop at the seam.
- Fixed: the drawer grip was a big black chevron. It is now the photo's thin dark slot along most of the drawer's top
  edge. The logo characters are 4 separate blocks plus a thin English line, not one solid black slab.
- Not matched: the membrane graphics are simplified. The knob rises ~20 mm above the printed 830.

## xy-k-czr-iii (magnetic vibration heat tower)
- Fixed: the plinth had no castor lobes. It now has round lobes bulging at the four corners over the castors, as in
  the photo.
- Fixed: the monitor now has a thick black rounded bezel in the upper part of the grey housing (wider grey chin below)
  and a 4:3 display inside it. The crop was re-made from the display only (perspective-corrected, see the note at the
  top), so the grey housing corners go away after a Unity refresh. The brand text on the tower is thinner and lighter.
- Not matched: the hose is a smooth tube (the real hose is smooth too). The hub faces left, so the angle render
  (camera front-right) cannot show it. The photo is taken from the front-left.
