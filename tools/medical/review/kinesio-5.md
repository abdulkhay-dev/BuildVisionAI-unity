# Detail review: batch kinesio-5 (14 devices)

Generators changed: `tools/medical/gen/k5lib.py` (new `shift()` helper), `k5_boards.py`, `k5_xy5.py`, `k5_stands.py`,
`k5_pulleys.py`, `k5_wallbars.py`, `k5_steps.py`, `k5_xy54.py`, `k5_zh.py`. The originals (generators and designs)
are in `scratch/kinesio-5-review/*.orig.*`. That folder also holds `run.sh` (regenerate, wait for the render, build the
compare sheet) and `bounds.py` (rough part extents, used to check that `size` covers the model). All 14 designs
re-rendered `ok`. Each was checked again on `renders/<id>-compare.png` after its last change.

**Size changes** (the size is the placement footprint, so it now covers the whole model):

| device | old size | new size |
|---|---|---|
| xy-51 | 800 × 800 × 2050 | 1255 × 800 × 2050 |
| xy-54 | 1890 × 1030 × 940 | 1890 × 1030 × 1130 |
| xy-zh-1 | 1300 × 900 × 1750 | 1460 × 980 × 1750 |
| xy-zh-2 | 1900 × 800 × 2100 | 2070 × 1100 × 2100 |

**Lettering**: no visible brand names or Xiangyu logos appear in any of these 14 photos, so `brand()` and `text()`
were not needed. The only badge is the round sticker on xy-47; it is drawn as a picture badge (see below). The LCDs
have no screenCrop, so they stay dark `screen` boxes.

## Per device

- **xy-47** (rocker board)
  - The glossy orange top rendered pale peach. It is now a satin, more yellow orange (`plastic#ea8c10`), with a
    satin red-orange rocker.
  - The rocker was set back 70 mm from the board edges. The photo shows it nearly flush, so it now spans z 25–675.
  - The badge was a small dark ring. It is now a Ø62 white disc with a thin dark rim and a dark diagonal figure over
    a baseline, as in the photo.
  - Cannot match: the faint wood grain under the lacquer.

- **xy-49** (board with handle): no difference found at sheet scale. Board, edge band, rocker and handle were left
  as they were.

- **xy-5** (arched sit-up bench)
  - The tufting buttons were chrome domes. They are now recessed buttons: a darker dimple disc, a flat chrome ring
    and a dark centre, laid on the board's slope.
  - The spring latch at the post top was a chrome block. It is now a chrome wire clip on a small plate.
  - The T-foot caps stuck out 12 mm past the 370 width. The feet were shortened so the caps end at the width.

- **xy-51** (upper-limb hanging frame)
  - **Size**: the hanging pairs point to +x, as photographed, so the right pair overhangs the 800 base. The width is
    now 1255; the base stays at x 0–800.
  - Re-measured at the columns (4.2 mm/px):
    - The J top is a tight dark bend into a light arm. The scale hangs 235 mm out from the column.
    - The spreader is 450 mm long, from the column outward, centred under the scale.
    - The slings are 140 × 410 mm and hang from about 1500 to 1060.
    - The old model had a long dark J and a short 310 mm spreader with 250 mm slings.
  - The right column's clamp collar and knob are at about 880, as in the photo. The left one is hidden behind the
    sling (drawn at 1150).
  - The scale is now a flat chrome tube with a window.
  - **Slings** were stiff boxes. Each is now a soft strap loop: a wide khaki band that is flat from the front and a
    narrow U from the side. It has creases, a darker hem, a slight twist on its hook, an S-hook and a chrome triangle
    buckle.
  - Cannot match: real cloth folds; the slings are strap sweeps.

- **xy-kgj-1** (hip rotation trainer)
  - **The posts stood mid-depth.** The photo shows both base plates just behind the front rim, so they are now at
    z = 442 and the disc sits behind the post line.
  - The rail and posts have the photo's warm, brassy chrome tint.
  - The clamp knobs are on the +x side of each post, at about 110 and 1080 (they were at 870). A sleeve collar was
    added at 1080.
  - The grip is now a dark teal-black foam.
  - The disc stop is a flat blade under the disc front.
  - Rivets were added on the platform ends.
  - **Foot holders** were plain blocks. Each is now a contoured binding: a rounded black plate with a curved
    heel/toe cup and side wings at the outer end.
    - Left holder: low heel cup and two arched straps with buckles.
    - Right holder: tall toe clip and one strap, on a slotted rail plate with a chrome lock screw.
    - Both sit on the photo's line, turned so the left end is toward the front, and tilt with the disc.

- **xy-6** (hemiplegia device)
  - **Rope routing** now follows the photo:
    - Each top pulley sits under a bar end on a fork. Its outer strand carries the big ring.
    - Its inner strand drops vertically to the mid pulley on the same side.
    - From the mid pulley, the rope runs out and down over a small guide pulley. It then hangs to the small yellow
      loop and continues to the pedal clamp.
    - The old model had diagonal crossing strands and pulleys out at the bar tips.
  - The big hand rings were narrow-bottomed trapezoids. They are now the photo's wide, rounded stirrups with a
    small peak at the rope tie. All rings and loops stay inside the 480 width.
  - The small loops are lower (630–710).
  - A clear clamp block was added under the blue scale.
  - The pedals are flatter (12° instead of 22°).
  - Approximation: the ropes are straight segments between pulleys; they do not wrap the pulleys.

- **xy-6a** (limbs passive trainer)
  - **Column**: the photo's column is vertical to the mid bar and then curves toward the chair into the top bar. It
    was a straight leaning bar. Black end caps were added on the top and mid bars, and black blocks on the mid bar.
  - **Handles**: the cross bar on the front post is black foam. The green stirrup handles hang from it, closer
    together (±120). Their grips are green, as in the photo, not black. A second thin post was added beside the
    front post.
  - **Rope routing**:
    - The top pulley's outer strand runs long and diagonal to the upper handle.
    - The inner strand drops to the mid pulley.
    - The mid pulley sends one rope to the lower handle and one to the pedal lever.
    - The lower handles' tail ropes gather at a chrome eye on the column at 780 and run on down to the pedals.
    - This gives the photo's bundle of ropes converging on the front post.
  - Cannot match: the chair mesh is a translucent dark panel.

- **xy-7** (wall bar)
  - The green rungs are teal (`#0c7d68`), as in the photo; the rails stay green.
  - The wood rungs are golden (`#d3a02a`), not orange.
  - The brackets now use the rail colour.
  - The wall plates sat outside the rails and made the model 64 mm wider on each side. They now sit behind the
    rails, so the model stays inside 970.
  - A small white label was added on the right rail, as in the photo.

- **xy-8** (wall bar with pull-up frame)
  - The rails are a darker green, as in the photo.
  - The green rungs are teal-green.
  - The frame and brackets use the rail colour.
  - Black clamps were added where the J side members hook onto the rung.
  - The pull-up bar's left cap is now inside the width.
  - Unchanged on purpose: the frame is drawn folded, as photographed.

- **xyc-t1** (steps + platform + ramp)
  - The platform's front face had a hand slot. The photo's platform front is plain, so the slot was removed.
  - The anti-slip mats are a slightly bluer `#86a5d6`, from a sample of the photo.

- **xyc-t2** (nesting step boxes)
  - The biggest box had a front slot. The photo has slots only on its ends, so the front slot was removed.
  - The three smaller boxes are now open-bottom boxes: front and back panels, and end panels with the bottom cut out
    between two feet (the photo's notches), with a dark interior.
  - The hand slots are smaller and oval (86 × 24).

- **xy-54** (OT table)
  - **Proportions**: the photos give a worktop at about 860 (body height/width ≈ 0.64 on photo 2). The bead-maze
    loops reach about 270 mm above the top. The cabinet was 135 mm too low. The body is now 120–835 and the size is
    1130 high, so the whole dressed table fits. The printed 940 cannot be the overall height of the table with its
    toys.
  - The door pulls are light wooden bows, as in photo 2.
  - The bead-maze wires form taller loops.
  - The phone is now a desk phone (sloped base with a key pad, handset with ear and mouth bulbs). It was two white
    pillows.
  - Added: the tray of small wooden cubes in front of the skittles.
  - The back fold-down tray moved up to about 1/3 of the body, as in photo 1.
  - Cannot match: the toys are simplified shapes (175 parts).

- **xy-zh-1** (four-unit trainer)
  - **Size**: the units stick out of the frame, so everything moved +115 and the size is now 1460 × 980.
  - The low frame rectangle is at about 85–135, as in the photo. It was at 220.
  - **SXZ-1**:
    - Strap pedals are black stirrups (side plates) with a strap loop hanging under the grip. The loop used to arch
      above the grip.
    - The neck is longer and the small head sits at 1520–1580, with a grey display.
  - **JGJ-1**:
    - It moved down to the photo's centre height of about 1260.
    - It has a real black dumbbell grip, pointing outward on the crank arm. Before, it was a zero-length handle with
      one ball.
    - Its knobs are at 1560 and 970.
  - **WGJ-1**: the black joystick (with a pistol-grip top) stands on a chrome bent arm offset from the round base,
    as in the photo. It was on a post in the base centre with a loose separate lever.
  - Cannot match: the screw heads and the dial markings.

- **xy-zh-2** (six-unit trainer)
  - **Size**: the units stick out of the frame, so everything moved +95 and the size is now 2070 × 1100.
  - Heights were re-measured on the photo (1.87 mm/px). Several units were 150–250 mm too tall or too high:
    - **Upper-limb pedal trainer**: the whole unit is about 450 tall (head top about 1330, pedals about 1100). It
      had been about 655 tall.
    - **Shoulder-lifting gauge**: the head top is at about 1480 (it was 1760). The column now slants up toward −x,
      so the front view shows the photo's slant; before, it tilted backward. White ticks were added on the purple
      scale.
    - **JGJ-2**: the housing centre is at about 1360 (it was 1450) and the LCD at 1575–1650. The crank grip is at
      1615.
  - **Pulley gantry**:
    - The post ends 130 mm above the top frame.
    - A short white top arm carries a blue knob, with the yellow bar under it (1790; it was 1950).
    - X braces go to the post.
    - Each pulley hangs from a yellow-bar end on a dark strap, at top-rail level.
    - The left rope is on the left side of its pulley, as in the photo.
  - **Finger ladder**: five green/white spiky segments now run from 720 to 1490, as in the photo. They went up to
    1740.
  - Approximation: the rope routing over the gantry is simplified to vertical strands.
