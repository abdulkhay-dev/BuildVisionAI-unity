# Medical equipment inventory — notes

Source: Xiangyu Medical / Sunnyou English leaflets (`单彩页-英语/`, 131 files: 75 PDFs, 56 JPG/PNG). Every file and page was opened.
Result: `inventory.json` — **455 devices** (physio 76, kinesio 150, robot 18, table 60, hydro 47, pediatric 61, sensory 25, other 18);
**201 with printed sizes** (mostly the Adult and Pediatric catalogues, which print sizes for almost every item; the leaflets for electronic devices rarely do).
Reference crops: `reference/` (602 JPG, all ≤300 KB): `<id>.jpg` photo, `<id>_2/_3.jpg` other angles, `<id>_screen.jpg` (47 screens),
`variantPhotos` (look of a variant merged into one entry), `groupPhoto` (the 9 hydraulic exercisers shown together).

The count is far above the expected ~100: the Adult catalogue (129 items), Pediatric series and Hydrotherapy/Treatment/Traction/Tilt
leaflets list many separate coded models. Nothing was dropped for size; if the library needs a shortlist, the candidates to skip are the
small desk OT items (xy-28, -29, -30a, -30b, -34, -50, -57…-60, xyh-3, xyhj-3, xym-5, xyn-1, xyt-1), xy-ap-yyzl-i (tablet + headphones),
sd-hl-pdj-7 (home intravaginal probe), xy-91 (car wheelchair lift).

## Cross-leaflet duplicates resolved at merge
- XY-K-E1 / E2 / E3 gait frames: in `减重步态/Gait Training Device.pdf` and the pediatric series p2 → one entry each (from the gait leaflet).
- XYC-T2 staircase, XY-71 PT mat table, XY-72 electric PT table: in the Adult catalogue and the pediatric series p7 → one entry each (Adult).
  XY-72 sizes disagree: single leaflet 2100×1200×500–1000, pediatric 1990×1200×500–800, Adult catalogue the same as the single leaflet.
- XY-1A / XY-2B bikes: in `四肢联动/Exercise Equipment 1.jpg` (no size) and the Adult catalogue p12 (printed) → Adult entry, with the more detailed form.
- The treadmill with handrails shown with the gait frames (`减重步态` p5) = XYJ-J9 (`跑台`) → one entry, gait-leaflet photo added as a view.
- XY-1 Static Bike, XYGS-2 Quadriceps chair, XY-72 PT Table single leaflets (`成人康复/单独产品`) duplicate Adult-catalogue items (sizes differ slightly; leaflet values used). XYG-3 exists only as a single leaflet.
- `冲击波/Shock wave therapy.jpg` = `XY-K-MEDICAL.jpg`; `熏蒸` photos 1–7 duplicate HYZ-IIC / HYZ-IIIB / HYZ-IIIE leaflets; `Passive and Active device.pdf` repeats the five XY-ZBD JPGs;
  `电疗/XY-K-GR-AI.jpg` and `Interfertial therapy XY-K-GR-AI.jpg` show the same unit.
- One code, several bodies (kept as separate entries, same `code`): XY-K-GR-AI (desk silver, `-v2` white desk, `-trolley`), XY-K-GR-CI (`-v2`), XY-MCB-I (standard / deluxe), XY-K-SISS-A (3 bodies), YHZ-II (microwave traction bed vs steel table).
- Several codes, one body (merged as `variants`, look shown in `variantPhotos`): GR-AI ← SISS-A old / RH-JPSJ-A; SJJD-II ← JDSW-VIII; LC-2 ← WIC-3 Enh., WIC-4, LC-1, LC-2 Enh., LC-3;
  LC-5 ← LC-4, LC-4 Enh., LC-5 Enh.; WIC-2 ← WIC-3; CZLD-V ← CZLD-VI; XYD-II ← XYD-I; XYL-VIIA ← B/C; XYL-VIID ← E/F; ZBD-IIIDL/IIDL/IDL stay separate though one body with different attachments.
  Undo these if each code must be its own model.

## Not in the catalogue / gaps
- `冲击波/瑞禾冲击波/瑞禾治疗头/*.png` — six shockwave heads (A6 acupoint, D10 deep, D20/D35 variable-frequency, F15 focused, R15 standard): accessories, described in xy-k-medical. The Ruihe device body itself is not shown anywhere.
- Folder `上下肢机器人K-1 K-9`: neither photo prints a model code → `upper-limb-rehab-robot`, `lower-limb-rehab-system` (code null); which is K-1 and which K-9 is unknown.
- 24 of the 25 multi-sensory items have no code (slug ids) and no printed sizes; their source thumbnails are 100–250 px.

---

<!-- group g1_electro -->
## g1_electro — 电疗 (electrotherapy) folder

34 devices, 3 with printed sizes (xy-k-gr-ai via its SISS-A / RH-JPSJ-A variants, rh-jpsj-b, xy-k-ty-1).
Every page and photo of the 25 files was opened. Crops are in `tools/medical/reference/`.

## Merge rule used
- A different body means a separate entry, even when the model code is the same (GR-AI ×3 bodies, GR-CI ×2 bodies).
- The same body with different channels, electronics or panel print means one entry with `variants`, even across different model codes. This applied to:
  - the silver desk box: GR-AI, SISS-A (old) and RH-JPSJ-A;
  - the E-series heads: none (CII and DII heads differ);
  - XYZP-IE and the XYZP-ID trolley;
  - XYZP-ID table and IC vacuum;
  - SISS-A/C/D carts;
  - SJD-A/C carts;
  - GR-EI and GR-EII;
  - XYD-I and XYD-II;
  - SJJD-II and JDSW-VIII.
- The same mould in a different colour or with different branding stays a separate entry, and the note says to share the mesh:
  - NMES cart (teal) vs TENS cart (grey);
  - desk boxes: SISS-A table (teal), SJD-A table (grey) and XYZP-ID table (blue);
  - handhelds: TY-IB (gold keypad) vs SWFK-III (blue keypad).
- Variant crops are saved as `<id>_v-<variant>.jpg` (and `xy-k-gr-ai_panel-b.jpg`). They are not listed in `views`, because they are not other angles; the `note` of each entry names them.

## File → device ids
| file (slug) | contents | ids |
|---|---|---|
| 087 Interferential therapy XY-K-GR-BII.jpg | real photo, grey cart | xy-k-gr-bii |
| 088 Interfertial therapy XY-K-GR-AI.jpg | silver desk box, arrow-button panel | xy-k-gr-ai (variant panel) |
| 089 Muscle Stimulator XY-K-SISS-A.jpg | same silver box, 4 knobs, 6 sockets; prints 420×360×232 | xy-k-gr-ai (variant SISS-A) |
| 090 TENS RH-JPSJ-A.jpg | same silver box, 5 knobs; prints 420*360*235 | xy-k-gr-ai (variant RH-JPSJ-A) |
| 091 TENS RH-JPSJ-B.jpg | white/light-blue cart; prints 65*37*115 cm | rh-jpsj-b |
| 092 XY-K-GR-AI.jpg | silver desk box, blue-button panel (main photo) | xy-k-gr-ai |
| 093 XY-K-GR-CI.jpg | real photo, tilted panel on white/blue box (old design) | xy-k-gr-ci |
| 094 XY-K-ZPJZ-II brochure.pdf (3 p.) | spine stimulator cart + blue spine electrode board; 8" screen | xy-k-zpjz-ii |
| 095 Low Frequency Electrotherapy XY-α-TRON-II (2 p.) | desk console + optional column trolley | xy-alpha-tron-ii |
| 096 Wearable Foot Drop XY-K-ZXC-II (2 p.) | wearable pod + cuff; phone app | xy-k-zxc-ii |
| 097 Dysphagia stimulator.jpg | handheld XY-K-TY-1, 13.4×6.4×2.4 cm printed | xy-k-ty-1 |
| 098 Swallowing … XY-K-TY-IB (2 p.) | handheld with gold keypad + tablet | xy-k-ty-ib |
| 099 Interferential Current Therapy Device (6 p.) | GR-EI (case), GR-EII, GR-AI classic (silver), GR-AI new white desk, GR-AI trolley, GR-CI new desk + trolley, GR-CII E-series cart (cover), GR-DII E-series cart with 15" screen | xy-k-gr-eii, xy-k-gr-ai, xy-k-gr-ai-v2, xy-k-gr-ai-trolley, xy-k-gr-ci-v2, xy-k-gr-cii, xy-k-gr-dii |
| 100 Hand Electrical Stimulator XY-K-SRD-I (2 p.) | hand-rest platform with finger cradles | xy-k-srd-i |
| 101 Biofeedback Electrical Stimulator XY-K-FKZL-Ⅳ (4 p.) | handheld master + satellites | xy-k-fkzl-iv |
| 102 Medium Frequency Electrotherapy Device (4 p.) | XYZP-IE cart, XYZP-ID trolley + table, XYZP-IC, XYZP-IC vacuum, XYZP-IB, XYZP-II (scene photo), XY-CDZP-I wearable | xyzp-ie, xyzp-id-table, xyzp-ic, xyzp-ib, xyzp-ii, xy-cdzp-i |
| 103 Electroacupuncture Therapy Device.jpg | XYD-I, XYD-II (same flat body), XYD-III | xyd-ii, xyd-iii |
| 104 Pelvic Floor Muscle Trainer XY-K-PDJ-II (3 p.) | pink pole trolley + tablet unit; prints unit 285*255*60 | xy-k-pdj-ii |
| 105 Pelvic Floor … SD-HL-PDJ-7 (2 p.) | HEALUV home probe + charging case | sd-hl-pdj-7 |
| 106 Pelvic Floor … XY-K-PDJ-IV (4 p.) | portable pink/white unit with stand | xy-k-pdj-iv |
| 107 Neurorehabilitation EMG … XY-K-SJJD-II (2 p.) | computer workstation cart | xy-k-sjjd-ii |
| 108 NMES (2 p.) | SISS-A table (teal), SISS-A/C/D carts (teal) | xy-k-siss-a-table, xy-k-siss-c |
| 109 TENS (2 p.) | SJD-A table (grey), SJD-A/C carts (grey) | xy-k-sjd-a-table, xy-k-sjd-c |
| 110 EMG Biofeedback Stimulator XY-K-SWFK-III (2 p.) | handheld, blue keypad + iPad | xy-k-swfk-iii |
| 111 EMG Biofeedback Training System XY-K-JDSW-VIII (3 p.) | same workstation cart as SJJD-II | xy-k-sjjd-ii (variant) |

## Doubts / ambiguities
- **Merging across model codes.** I followed the "same body = variants" rule, so:
  - TENS RH-JPSJ-A and the old Muscle Stimulator SISS-A are variants of xy-k-gr-ai;
  - the pelvic-floor JDSW-VIII is a variant of the neuro workstation SJJD-II.
  
  If the library needs every product as its own entry, split these back out. The variant crops are already saved.
- **Same code, different bodies.**
  - XY-K-GR-AI appears as 3 bodies: old silver (088/092/099 "Classic Type"), new white desk (099 p.4) and a trolley cabinet (099 p.5). The 3 bodies are entered as xy-k-gr-ai, -v2 and -trolley.
  - XY-K-GR-CI appears as 2 bodies: 093 photo and 099 p.5. Entered as xy-k-gr-ci and -v2.
  - XY-K-SISS-A appears as the old silver box (089), the new teal table type and a trolley type (108).
- **xy-k-pdj-ii.** Only the tablet unit size is printed (285×255×60). The trolley size is estimated, so `printed` is false.
- **Small or scene-only images.**
  - xyzp-ii is only in a small scene photo with a seated woman, so its form is approximate.
  - xy-k-swfk-iii is only a small image.
- **Mentioned but not pictured.**
  - XYZP-IC "lightweight trolley".
  - XY-K-PDJ-IV "trolley style".
  - XY-α-TRON-II trolley is pictured and is in views.
- **sd-hl-pdj-7.** This is a home-use intravaginal probe with a charging case (HEALUV brand). I set it to category `other` and mount `desk`. It is questionable whether it belongs in a clinic room library at all.
- **Wearables and handhelds** are set to mount `desk` (placed on a table or shelf), with sizes as they lie flat: xy-k-zxc-ii, xy-cdzp-i, xy-k-ty-1, xy-k-ty-ib, xy-k-fkzl-iv, xy-k-swfk-iii and xy-k-gr-eii.
- **Possible duplicate with another group.** `tools/medical/reference/xyd-1.jpg` already existed (created 19:25 by a parallel session), so another leaflet probably also lists XYD-I. Here XYD-I is a variant of xyd-ii.
- **The E-series cart body is shared by GR-CII and GR-DII.** The heads differ (LED panel vs 15" touch screen) and the handle is on the other side, so they are separate entries.
- **Shared housings across NMES, TENS and XYZP.** NMES and TENS carts are the same mould as each other. They resemble the XYZP-IE cart (same swoosh language), but XYZP-IE has no front door/flap, so it is kept separate.

## Not devices / left out
- **Apps and tablets:**
  - foot-drop phone app;
  - iPad game software for TY-1, TY-IB and SWFK-III;
  - Sunnyou cloud/HIS functions.
- **Electrodes and cables:**
  - silicone, self-adhesive and suction electrodes;
  - vacuum cups;
  - throat electrode patches;
  - intracavity, vaginal and rectal probes for PDJ-II, PDJ-IV and JDSW-VIII;
  - medium-frequency and iontophoresis electrode plates (102 p.1);
  - output lines;
  - the RH-JPSJ-B accessory row.
- **Carry case** of GR-EI (described in form).
- **Spine electrode board of ZPJZ-II.** It is an accessory but large, so it is described in form and should be modelled as a separate prop.

<!-- group g2_physio_a -->
## g2_physio_a — notes

28 devices, 4 with printed sizes (xy-k-cdb-iv, xy-k-csb-i, xy-k-csb-ii, xy-cryo-1).

## Folder → device map

| slug / file | contents | device ids |
|---|---|---|
| 113 短波/Shortwave Therapy Device XY-K-CDB-II.pdf (2 p) | p1: 2 renders of the same cart (two angles); p2: features + same render | xy-k-cdb-ii |
| 114 短波/XY-K-CDB-IV.jpg | photo of the cabinet + accessory set photo; size printed 430×330×830 | xy-k-cdb-iv |
| 129 超声波/Ultrasound Therapy Device.pdf (2 p) | XY-K-CSB-I (1 probe, segment LCD), XY-K-CSB-II (2 probes, colour LCD), optional trolley; specs incl. size 380×310×135 for both | xy-k-csb-i, xy-k-csb-ii |
| 063 极超短波 微波/Mircrowave Therapy Device.pdf (4 p) | p1 indications (no product); p2 HYJ-IV hero; p3 HYJ-IV; p4 HYJ-III, HYJ-II Enhanced, HYJ-II, HYJ-I | hyj-iv, hyj-iii, hyj-ii-enhanced, hyj-ii, hyj-i |
| 064 微波治疗仪XY-WB-EI/Microwave Therapy Device XY-WB-EI.pdf (2 p) | p1 hero render; p2 scene with hospital bed + mannequins | xy-wb-ei |
| 046 射频理疗仪XY-K-SPLL-V/Radio Frequency Therapy Device XY-K-SPLL-V.pdf (2 p) | p1 hero render; p2 TECAR text/illustrations | xy-k-spll-v |
| 019 冲击波/Shock wave therapy.jpg | XY-K-MEDICAL leaflet — identical content to 020 (different file bytes) | (duplicate of xy-k-medical) |
| 020 冲击波/XY-K-MEDICAL.jpg | desktop pneumatic shockwave + 6 heads | xy-k-medical |
| 021 冲击波/台式压电式冲击波治疗仪/…XY-FSWT-IC.pdf (2 p) | desktop piezo shockwave, 2 angles | xy-fswt-ic |
| 022 冲击波/德款自制冲击波/Shock Wave Therapy.pdf (2 p) | XY-K-SHOCK MASTER-500 trolley; p1 two renders (old lilac-side + new), 6 UI screenshots; p2 scene with blue treatment chair + small render | xy-k-shock-master-500 |
| 023–028 冲击波/瑞禾冲击波/瑞禾治疗头/*.png | 6 treatment-head renders only, no device body | — (accessories) |
| 029 冷疗/Cryotherapy XY-CRYO-1.jpg | photo + specs (595×500×1200, 70 kg) | xy-cryo-1 |
| 030 冷疗/Cryotherapy Device XY-CRYO-3.pdf (4 p) | p1 hero, p2 text, p3 render + treatment photos, p4 text/department photos | xy-cryo-3 |
| 083 物理加压冷热敷治疗仪/Hot and Cold Compression Therapy Device.pdf (2 p) | p1 in-use photo on couch; p2 sleeve photos + cart render; code XY-LRF-Ⅰ from Chinese header text | xy-lrf-i |
| 128 蜡疗/Paraffin Wax Therapy Device.pdf (5 p) | p1 group + accessories; p2 text; p3 group; p4 semi-automatic XYL-I/II/V; p5 automatic VIIA–C, VIID–F, table incl. VIIIB, TCM wood-grain insets | xyl-i, xyl-ii, xyl-v, xyl-viiib, xyl-viia, xyl-viid |
| 067 湿热敷/XY-SRF-I and RH-SR-II.jpg | SRF-I (lid open) + RH-SR-II, hot packs | xy-srf-i (view _2), rh-sr-ii |
| 068 湿热敷/XY-SRF-I.jpg | SRF-I lid closed, specs (70 L) | xy-srf-i |
| 069 湿热敷/XY-SRF-IV.jpg | SRF-IV, specs (140 L) | xy-srf-iv |
| 009 充气式医用升温仪XY-K-SWY-II/…XY-K-SWY-II.pdf (2 p) | p1 hero with hose; p2 3/4 view + front view (fault-log screen), blanket types | xy-k-swy-ii |
| 043 多功能清创仪/Multifunctional Debridement XY-QC-I.pdf (2 p) | p1 front 3/4; p2 rear 3/4 + UI mock-up | xy-qc-i |

## Shockwave heads (瑞禾治疗头, files 023–028) — accessories, not devices
A6 穴位 (acupoint), D10 深层 (deep), D20 变频 (frequency-conversion), D35 变频 (frequency-conversion, large Ø), F15 聚焦 (focused), R15 标准 (standard).
All six are black ribbed cylindrical caps with a metal (silver / gold for D10) transmitter face — no device body in any of the six images.
They match the six heads printed on the XY-K-MEDICAL leaflet (Standard, Freq. conversion ×2, Deep, Focused, Acupoint), so they are mentioned in the xy-k-medical form. The 瑞禾 (Ruihe) shockwave device itself is not shown anywhere; the folder 冲击波/压电式冲击波 is empty.

## Doubts / ambiguities
- All sizes except the 4 printed ones are estimates from photo proportions; carts with arms (shortwave, microwave, XY-WB-EI) give the body envelope, arm reach is in sizeNote.
- XY-K-CDB-IV printed 430×330×830 — mapped W=430 (logo front) / D=330 judging by the photo; could be the other way.
- XY-CRYO-1 printed "length 595, width 500" — mapped W 500 (front with hose outlet) × D 595.
- HYJ-II Enhanced vs HYJ-II: same code root, completely different carts → two entries. HYJ-III and HYJ-II Enhanced share one cart and differ only by radiator (rectangular vs round) → kept separate (separate codes).
- XYL-VIIA/B/C and VIID/E/F: leaflet shows one body per group (renders labelled VIIC and VIIF); tray layer counts suggest the cabinets may differ in height — grouped as variants. "TCM type" = same cabinets with brown wood-grain doors, listed as a variant. Leaflet misprints "XYL-VIF".
- XYL-VIIIB is only visible in group photos (p1, p3), partly hidden behind XYL-II.
- XYL-I: mount "desk" (no casters, could also stand on floor/stool).
- XY-LRF-Ⅰ code comes only from the extracted Chinese header text, not visibly printed in English.
- XY-K-SHOCK MASTER-500: two handpiece configs (1 handpiece/8 applicators on p1, 2/12 on p2) — one entry with variants; old render (_3) has lilac-grey side panel.
- Crops: xyl-viia photo has the TCM inset circle in the top-right corner (unavoidable without cutting the console); xyl-i has a bit of leaflet text in the top corners; xy-qc-i and xy-lrf-i had overlapping leaflet text painted white; xy-srf-i casters slightly trimmed at the bottom (caption right below).
- xy-qc-i screenCrop is the printed UI mock-up, not a photo of the device screen.

## Not devices / left out
- Shockwave treatment heads A6, D10, D20, D35, F15, R15 (above); XY-K-MEDICAL's six handpiece heads.
- Ultrasound optional trolley (described in xy-k-csb-ii form).
- Shortwave XY-K-CDB-IV accessories: plate electrodes (3 pairs), felt pads, cables.
- Hot/cold compression sleeves (8 kinds); hot packs and racks for hydrocollators; wax laminating tool and tool kit; disposable warming blankets (adult full/upper/lower, child); RF electrodes/handpieces; debridement handpieces, waste bottle.
- Scene props: hospital bed + mannequins (064 p2), blue treatment chair (022 p2), treatment couch (083 p1) — not part of this group's products.
- 063 p1, 046 p2, 030 p2/p4, 128 p2 — text/illustration pages without products.

<!-- group g3_physio_b -->
## g3_physio_b — notes

33 devices, 3 with printed full dimensions (xy-k-zwx-ii, xy-k-jlc-d, xy-dms-102c); 2 more have only a printed height range (xy-k-czld-iii, xy-k-czld-vii) and are marked printed:false.

## Folder / file → device ids

| slug | file (rel) | devices |
|---|---|---|
| 010_Infrared_therapy | 光疗/智能疼痛/Infrared therapy.jpg | xyg-500ib |
| 011_High_Power_Laser_Therapy_Device_XY_SCJG_ | 光疗/深层组织激光治疗仪/High Power Laser Therapy Device  XY-SCJG-II.pdf (2 p) | xy-scjg-ii |
| 012_Ultraviolet_Radiation_Therapy_Device | 光疗/紫外线/Ultraviolet Radiation Therapy Device.pdf (2 p) | xy-k-zwx-ii (printed 273×202×92) |
| 013_Ultraviolet_light_therapy | 光疗/紫外线/Ultraviolet light therapy.jpg | xy-k-zwx-ii (duplicate; main photo taken from here) |
| 014_UV_sterilizer_1 | 光疗/紫外线消毒器/UV sterilizer 1.jpg | xdd-i, xdd-ii |
| 015_UV_sterilizer_2 | 光疗/紫外线消毒器/UV sterilizer 2.jpg | xdd-ii (duplicate, cover + kill-rate table) |
| 016_Spectrum_Therapy_Device | 光疗/频谱治疗仪/Spectrum Therapy Device.pdf (2 p) | xy-ppzl-ii |
| 017_High_Power_Infrared_Therapy_Device | 光疗/高能红外治疗仪/High Power Infrared Therapy Device.pdf (2 p) | xy-k-gnhw-ii |
| 120_Specification | 经颅磁刺激器/Specification.pdf (2 p) | xy-k-jlc-d (printed size; real photo = view _2) |
| 121_Transcranial_magnetic_stimulator | 经颅磁刺激器/Transcranial magnetic stimulator.pdf (2 p) | xy-k-jlc-d |
| 122_Transcranial_Magnetic_Stimulator | 经颅磁刺激器/经颅磁刺激器+经颅磁导航机器人/Transcranial Magnetic Stimulator.pdf (4 p) | xy-k-jlc-j, tms-navigation-robot, tms-treatment-chair, tms-special-bed (also small xy-k-jlc-d thumbnail p3) |
| 123_TMS | 经颅磁脑病/TMS.jpg | tms-physiotherapy-device |
| 127_Pulse_Magnetic_Therapy | 脉冲磁/Pulse Magnetic Therapy.jpg | pulse-magnetic-therapy-device |
| 115_XY_K_CZR_II | 磁振热/XY-K-CZR-II.jpg | xy-k-czr-ii |
| 116_XY_K_CZR_III | 磁振热/XY-K-CZR-III.jpg | xy-k-czr-iii |
| 070_Laser_Magnetic_Stimulation_Therapy_Devic | 激光磁场理疗仪-康复科/…XY-JGC-III.pdf (4 p) | xy-jgc-iii |
| 071_Pelvic_Floor_Magnetic_Therapy_Device | 激光磁场理疗仪-盆底磁/Pelvic Floor Magnetic Therapy Device.pdf (6 p) | sd-pdc-2 (chair), xy-jgc-iii (pelvic variant of the cart; main photo from here) |
| 125_Deep_Muscle_Stimulator | 罗汉锤/Deep Muscle Stimulator.pdf (2 p) | xy-dms-102b |
| 126_XY_DMS_102C | 罗汉锤/XY-DMS-102C.jpg | xy-dms-102c (printed 90×46×140) |
| 131_Deep_Muscle_Stimulator_XY_DMS_103A | 雷神锤XY-DMS-103A/…XY-DMS-103A.pdf (2 p) | xy-dms-103a |
| 007_Sonic_Wave_Vibration_Massager | 体感音波健智仪/Sonic Wave Vibration Massager.pdf (2 p) | xy-ap-yyzl-i |
| 018_Whole_Body_Sonic_Vibration_Device | 全身音波律动/Whole Body Sonic Vibration Device.pdf (4 p) | xy-k-czld-i, -ii, -iii, -v (+VI variant), -vii |
| 124_Integrated_Physiotherapy_System | 综合物理治疗系统/Integrated Physiotherapy System.pdf (4 p) | xy-k-gzz-iii |
| 117_Air_Compression_Therapy | 空气波/老款/Air Compression Therapy.pdf (5 p) | xy-k-wic-1, xy-k-wic-2 (+WIC-3), xy-k-lc-2 (box family, 6 models), xy-k-lc-5 (cart family, 4 models) |
| 118_Intermittent_Pneumatic_Compression_Devic | 空气波/间歇充气加压/Intermittent Pneumatic Compression Device.pdf (4 p) | xy-ipc-iid |

## Merges (same body, different electronics/panel)
- **xy-k-wic-2** ← WIC-2, WIC-3 (identical two-tone dome box).
- **xy-k-lc-2** ← WIC-3 Enhance, WIC-4, LC-1, LC-2, LC-2 Enhance, LC-3: one white box chassis with a blue-framed front panel; only the panel artwork differs (LED groups, gauge dial on WIC-4, LCD window on LC-1). A modeller can use one mesh plus panel textures; variant photos are saved as xy-k-wic-3-enhanced / xy-k-wic-4 / xy-k-lc-1 / xy-k-lc-2-enhanced / xy-k-lc-3 .jpg. If separate entries are wanted, split them.
- **xy-k-lc-5** ← LC-4, LC-4 Enhance, LC-5, LC-5 Enhance (the same white cart with a touch-screen head). Variant photos: xy-k-lc-4.jpg, xy-k-lc-5-enhanced.jpg.
- **xy-k-czld-v** ← CZLD-VI (the render looks identical; xy-k-czld-vi.jpg is kept for reference). The white-bodied version shown in use on 018 p4 has no model name. It is kept as views _2/_3 and flagged as a colour variant.
- **xy-jgc-iii**: the rehab leaflet and the pelvic-floor leaflet show the same cart (the pelvic version has a pink icon on the front).

## Doubts
- **SD-PDC-2 vs XY-JGC-III**: the pelvic-floor cover prints "SD-PDC-2 (Perineal + Sacral Nerve Stimulation)" next to the chair + cart set, but p5 names the set "XY-JGC-III (Perineal + Sacral Nerve Stimulation)". I gave SD-PDC-2 to the upholstered magnetic chair (the perineal seat). It may instead be the code of the whole set.
- **XY-K-ZWX-II wavelength**: the PDF says 254 nm and the JPG says narrow-band UVB. It is the same box, so I treated it as one device.
- **XY-DMS-102B**: the comparison table on p2 is headed "XY-DMS-101B", which is probably a typo. The only figures given are the 1.175 kg weight and the 12 mm stroke.
- **XY-AP-YYZL-I** (also "XYZP-IB" in the text): this is just a tablet and Bluetooth headphones, so category is "other". It may not be worth modelling.
- **tms-physiotherapy-device (123)**: no code is printed. It is a low-field magnetic + electrical stimulation cart, not a high-field TMS. The source photo is low-res.
- **tms-special-bed** comes only from a small thumbnail ("Special Bed" option, 122 p3), so the crop is low-res. **tms-treatment-chair** comes from round inset photos on 122 p4, so circle edges show in the crop.
- **tms-navigation-robot**: I chose category robot (cobot arm positioning a TMS coil). It could also be physio. Its photo also shows a dark TMS host cart beside it, which I counted as part of the system.
- **XDD-I view _2**: a second white column with a gooseneck stands next to the XDD-I lamp. It is probably the same lamp's mast from another side, but this is unclear.
- **Categories**: I put the vibration plates (CZLD-I/II/V) under physio, CZLD-III (vibration couch) under table, and CZLD-VII (vibration walkway with parallel bars) under kinesio. Change these if you prefer one category for all of them.
- **Crop quality**: the xy-ppzl-ii crop contains part of the teal background curve and the word "Device". The xy-k-gzz-iii crop has bits of the surrounding module icons at its edges. The text overlaps the product, so a clean rectangle was not possible.

## Items not counted as devices
- Coils and heads (TMS figure-8/round coils, positioning caps, MEP module), UV illuminators, light guides and goggles, magnetic pads and transducers (CZR orange pads, pulse-magnetic S/N pads), massage-gun heads and weights, the DMS-103A aluminium trolley case, compression sleeves (17 types), hoses, foot plates and electrodes. All are accessories and are described in the device `form` or `note`.
- The software and apps: the Non-VTE ward central workstation (118 p4: PC, routers, login and records software), the TMS patient-management software and the tablet app UI.
- The ring of ~10 small devices around the Integrated Physiotherapy System (124 p1/p2). These are illustrations of the function modules (they look like other Xiangyu catalogue products) and are not separate devices in this leaflet.
- The PT/treatment tables and recliners that appear only as scene furniture: the UV treatment couch on 012 p2, the reclining chair in the compression scene on 117 p1/p4, and the bed under the laser-magnetic scene on 070. The wheelchair in the 121/122 scenes was skipped too.

<!-- group g4_robot -->
## g4_robot — notes

42 devices, 1 printed size (XY-K-G1: "Specification (cm): 120 * 109 * 180"). Every page and photo was opened.

## Folder → device ids

| slug / file | what it contained | ids |
|---|---|---|
| 002 上下肢主被动康复训练仪 / Passive and Active Rehabilitation Training System… .pdf (4 pp) | Seatless cycle-type active/passive trainer, 3 models on p3 | xy-zbd-iiidl (upper+lower), xy-zbd-iidl (lower only), xy-zbd-idl (upper only) |
| 003 上下肢机器人K-1 K-9 / Lower Limb Rehabilitation System.jpg | Tilt table with a stepping robot, patient in the photo | lower-limb-rehab-system |
| 004 上下肢机器人K-1 K-9 / Upper Limb Rehabilitation System.jpg | Arm exoskeleton on a lifting column with a bucket chair + computer cart | upper-limb-rehab-robot, upper-limb-rehab-workstation |
| 005 上肢综合康复训练系统 / Upper Limb Rehabilitation Training System.pdf (4 pp) | Round ADL/OT table with an auto-rotating component turntable | xy-ct-iv (with screen tower), xy-ct-iii (no screen) |
| 006 上肢运动机器人 / Upper Limb Training Robot XY-SZGJK-II.pdf (2 pp) | Lifting work table with a 2-link end-effector arm, monitor and camera | xy-szgjk-ii |
| 031 减重步态 / Gait Training Device.pdf (8 pp) | 12 body-weight-support frames + treadmills/bike in the sets | xy-k-e1, xy-k-e2, xy-k-e3, xy-k-g1, xy-k-g2, xy-k-g3, xy-k-g6, xy-k-g7, xy-k-m1, xy-k-m2, xy-k-m3, xy-k-m4, gait-obstacle-treadmill, rehab-treadmill-handrails, upright-exercise-bike |
| 045 天轨步态减重平衡训练系统 / Gait Weightloss Blance Training System.pdf (8 pp) | Ceiling rail "Smart Sky Track" with a motor head | smart-sky-track (mount: ceiling) |
| 062 智能辅助行走机器人 / Smart Assisted Walking Robot.pdf (4 pp) | Mobile walking robot with pelvic support | xy-r-sdk-i, xy-r-sdk-iv |
| 042 多关节等速… / Multi-Joint Isokinetic … XY-DGDX-I.pdf (2 pp) | Dynamometer tower with a monitor arm | xy-dgdx-i |
| 119 等速 / Isokinetic Series.pdf (2 pp, scan) | "Exerciser series": 9 hydraulic circuit machines + a group photo | xy-dssz-01a, xy-dssz-02a, xy-dssz-03a, xy-dsxb-01a, xy-dsxb-02a, xy-dsxb-03a, xy-dsxz-01a, xy-dsxz-02a, xy-dsxz-03a |
| 047 平衡 / Balance Training and Evaluation System.pdf (2 pp) | Seated and standing balance platforms + a shared PC trolley | xy-ph-iv, xy-ph-v, xy-ph-workstation |
| 048 情景互动 / Interactive Evaluation System.pdf (2 pp) | Big-screen stands with a 3D depth camera | xy-qjhd-bh (landscape), xy-qjhd-bv (portrait + operator monitor) |

## Categories (decisions)
- **robot:** limb and gait robots, the ceiling track, and every **electric or pneumatic** body-weight-support frame (E2, E3, G2, G3, G6, G7, M1–M4). The two **manual** frames (E1, G1) are **kinesio** because they have no motorised mechanics.
- **kinesio:**
  - XY-ZBD (active/passive trainer).
  - XY-CT (OT/ADL table): it has a motorised turntable, but it is an OT table and not a limb robot. This is a doubt; robot would also be defensible.
  - Isokinetic dynamometer, the 9 exercisers and the balance platforms.
  - Interactive evaluation stands: they are exercise/assessment by camera-driven games, so I chose kinesio over other.
  - Treadmills and the bike.
- The **workstation/PC trolleys** (upper-limb-rehab-workstation, xy-ph-workstation) take the category of their system. They are listed as separate items because they are free-standing objects.

## Ambiguities and doubts
- **Folder "上下肢机器人K-1 K-9":** neither JPG prints a model code. The folder name suggests K-1 and K-9, but which photo is which cannot be told, so both have `code: null`.
- **XY-ZBD screen:** the leaflet says "27.5-inch" but the proportions look like about 21–24". The form gives both values.
- **XY-ZBD-IIIDL / IIDL / IDL:** these share one body and differ only in which attachments are fitted (upper crank, pedals, calf supports). Each is its own entry that refers back to IIIDL. They could be merged into one model with toggled parts.
- **XY-R-SDK-I vs SDK-IV:** same chassis. The pelvic module differs (a single arm with a cylindrical cuff, versus a 4-DOF bar frame), so they are separate entries.
- **XY-K-E3 frame:** looks identical to E2. The set adds a separate treadmill, which is modelled as `gait-obstacle-treadmill`. XY-K-G3 is likewise a G2-like frame plus `rehab-treadmill-handrails`.
- **XY-K-M2:** the M1 frame plus `rehab-treadmill-handrails` plus `upright-exercise-bike`. The same photo is on p2 and p6.
- **XY-K-M4 (pneumatic):** only an in-use scene photo exists, so its frame size is uncertain.
- **Cover p1 (031):** a white BWS frame with a stepped white base over the bronze treadmill. It matches no listed code exactly (closest G3) and is used only as `rehab-treadmill-handrails_2`.
- **Smart Sky Track:**
  - No dimensions are printed. The rail profile (about 160 × 90 mm aluminium box) and the head (about 560 × 300 × 250) are estimates from the renders.
  - The rail layout depends on the project: straight, curved, S, Y and cross switch, with a turntable.
  - `size` covers the head plus strap plus spreader in the working position. The rail footprint is described in `sizeNote`.
- **"Isokinetic Series" (119):** despite the file name, these are hydraulic exercise machines. The leaflet heading is "Isokinetic muscle rehabilitation trainer – Exerciser series". Where each machine sits on the page was matched by its shape to the description:
  - press levers: shoulder press 01A
  - elbow pads: pec dec 02A
  - roller arm pads: biceps 03A
  - chest roller with tall handles: abdominal DSXB-01A
  - footplate with levers: chest/back DSXB-02A
  - arch with rollers and footplate: back extension DSXB-03A
  - footboard: leg press DSXZ-01A
  - stirrups: abductor DSXZ-02A
  - knee/ankle rollers: leg extension DSXZ-03A
- Except G1, all sizes are estimates. No other leaflet in this group prints overall dimensions; the spec items found are travel ranges and angles only.

## Duplicates and possible overlaps with other groups
- The bronze `rehab-treadmill-handrails` appears in four places in 031: G3, M2, the cover, and the M4 scene. If another group has a medical treadmill with parallel bars, it may be the same unit.
- `upright-exercise-bike` is a generic bike, seen only in the M2 photo and partly hidden by a harness.
- XY-CT-IV appears on p1, p2 (in use), p3 and p4.
- XY-R-SDK-IV appears on p1, p3 and p4.

## Devices visible only in group or scene photos
- upright-exercise-bike (XY-K-M2 photo).
- gait-obstacle-treadmill (a small inset next to XY-K-E3).
- rehab-treadmill-handrails (in sets and scenes, never on its own).
- xy-k-m4 (scene photo only).

## Left out (not devices or not separate)
- **Accessories:**
  - Harness vests, slings (transfer, toilet, mesh, training vest) and leg bands.
  - The 12 ADL components of XY-CT: door knob, key, tap, lever, keypad, steering wheel, joystick and so on.
  - The quick-change handles of the SZGJK (oval and prone types).
  - The steering-wheel attachment of the DGDX.
  - The VR headset (SDK-IV).
  - The handheld remote of the sky track.
  - Keyboards, mice and printers. These are mentioned in the `form` fields.
- **Software, games and reports** (all leaflets).
- **Generic items in scenes:** the grey chair and mannequin with the SZGJK, the parallel bars and treadmill under the sky track, and the mannequins with the SDK. These are not catalogue products of these leaflets.
- **Other content:** the factory aerial photo (031 p2) and the doctor stock photo (047 p1).
- **Crops:**
  - `exerciser-series-group.jpg` is the group photo of the 9 exercisers. It is referenced in their notes, not in `views`.
  - Text fragments from neighbouring items were whitened in xy-k-g3, xy-k-g6, xy-k-m3, rehab-treadmill-handrails, xy-dssz-03a and xy-dsxz-03a.
  - `upright-exercise-bike.jpg` necessarily includes the hanging harness in front of the bike.

<!-- group g5_kinesio -->
## g5_kinesio — notes

24 devices, 3 with printed dimensions (XY-SZLD-IA, JY-CT-II, XYJ-J9). All are in category `kinesio`.

## Folder / file → device ids

| slug | file (rel) | contents → ids |
|---|---|---|
| 001_CPM | CPM系列/CPM.pdf (3 pp) | p1 `xy-cpm-iib` (one photo printed twice); p2 `xy-cpm-ic` (on a desk and on a mobile stand), `xy-cpm-id`; p3 `xy-cpm-ia`, `xy-cpm-ib` |
| 032_Exercise_Equipment_1 | 四肢联动/Exercise Equipment 1.jpg | `xy-1a`, `xy-2b`, `recumbent-cross-trainer-interactive` (no code; the middle photo and the cover photo with people), `interactive-training-cart` |
| 033_Exercise_Equipment_2 | 四肢联动/Exercise Equipment 2.jpg | `xy-zbd-ic`, `xy-zbd-iie`, `xy-zbd-ib` (**only here**), `xy-zbd-id`, `xy-zbd-iid`, `xy-zbd-iiid` (all small thumbnails; the ZBD photos are taken from the single leaflets) |
| 034_Recumbent_cross_trainer | 四肢联动/Recumbent cross trainer.jpg | `xy-szld-ia` |
| 036_Passive_and_Active_device | 多关节主被动/Passive and Active device.pdf (5 pp) | p1 IC, p2 ID, p3 IID, p4 IIE, p5 IIID. These are the same pages as 037–041, so they duplicate those leaflets. The entries cite the single JPGs |
| 037_XY_ZBD_IC | 多关节主被动/XY-ZBD-IC.jpg | `xy-zbd-ic` |
| 038_XY_ZBD_ID | 多关节主被动/XY-ZBD-ID.jpg | `xy-zbd-id` |
| 039_XY_ZBD_IID | 多关节主被动/XY-ZBD-IID.jpg | `xy-zbd-iid` |
| 040_XY_ZBD_IIE | 多关节主被动/XY-ZBD-IIE.jpg | `xy-zbd-iie` |
| 041_XY_ZBD_IIID | 多关节主被动/XY-ZBD-IIID.jpg | `xy-zbd-iiid` |
| 054_Hand_Rehabilitation_Training_System | 手功能综合康复训练平台XY-101C/Hand Rehabilitation Training System.pdf | `xy-101c` (variant XY-101B); p2 has a top-view render and software screenshots |
| 055_Hand_Rehabilitation_Training_System_JY_C | …/儿童手功能/Hand Rehabilitation Training System JY-CT-II.pdf | `jy-ct-ii` |
| 058_Smart_peg_board | 智能木插板/Smart peg board.jpg | `xy-mcb-i` (standard), `xy-mcb-i-deluxe` |
| 059_Smart_Posture_Mirror_XY_JZJ_I | 智能矫正镜/Smart Posture Mirror XY-JZJ-I.pdf | `xy-jzj-i` |
| 060_Smart_Posture_Mirror_pro | 智能矫正镜/智能矫正镜Pro/Smart Posture Mirror pro.pdf | `xy-jzj-ii`; XY-JZJ-I is also shown here for comparison |
| 061_Smart_OT_table | 智能磨砂桌/Smart OT table.jpg | `xy-msz-i` |
| 130_Treadmill_XYJ_J9 | 跑台/Treadmill XYJ-J9.jpg | `xyj-j9` |

## Different bodies or variants (multi-joint active-passive 多关节主被动)
- **IC and IIE**: both are bedside mobile units with the same blue U-base, white box housing, column and bed-docking saddle. The boom is different. IC has a horizontal boom with a down-angled arm to a white drum with leg cradles. IIE has a long boom that slopes down, pendulum rods and white foot shells. The look differs, so they are 2 entries.
- **ID, IID and IIID**: they share the same family chassis (navy-blue frame, white cowl) but have different heads. ID has arm cranks only. IID has a leg drum and a handlebar. IIID has both an arm drum and a leg drum and a T-base without the white cowl. That makes 3 entries.
- **IB**: a different design (white peanut-shaped housing with a turntable and multi-grip, on a light-blue H-base). It appears only in Exercise Equipment 2.
- XY-ZBD-IC: the title says "lower limbs" but feature 5 says "upper limb training part". The photo shows leg cradles, so I treat it as lower limb.

## Ambiguities and doubts
- `recumbent-cross-trainer-interactive` has no model code. It is clearly a different body from XY-SZLD-IA: white shell, armrest seat and graphite plinth, against a grey shell with green seat handles. It may be a newer "XY-SZLD-II…" model, but that is not printed.
- `interactive-training-cart` is a generic TV, PC and keyboard cart from the "scenario interactive mode" block. Its menu lists several Xiangyu machine families, so it is shared hardware rather than a training device. I kept it because it is a separate physical object. Delete it if it is unwanted.
- `xy-cpm-ic`: the page shows the head unit on a desk and on a mobile pole stand. I made one entry with two mounting variants, and the stand photo is in `views`.
- XY-CPM-IA is called "waist" in the leaflet. This is a mistranslation of 腕 (wrist), and the text confirms the wrist.
- Lower-limb CPM: mount=`desk` because it lies on the patient's bed.
- `xy-101c`: only the table height is printed (670–1070). The overall size comes from the JY-CT-II leaflet, which shows the same body, so printed=false.
- `jy-ct-ii` (pediatric): the body is the same as XY-101C, with pink rods and 2 visible screens. I put it in `kinesio` with a note. It could also go in `pediatric`.
- `xy-mcb-i` and `xy-mcb-i-deluxe` share one code, XY-MCB-I. I split them because the deluxe adds a 27" monitor and a different board (gold frame, 64 lit holes), so it looks different.
- `xy-jzj-ii`: the leaflet says "94-inch mirror touch screen", which must be a typo (probably 49"). All mirror sizes are estimated from screen proportions. The heights (~2.0 m and ~1.95 m) are uncertain.
- `xy-msz-i`: in the promo photo the patient sits at the short end. The described layout (window along the long axis, gantry in X/Y) is my reading of the photo.
- `xyj-j9` and `xy-1a`/`xy-2b` are OEM units ("AMERICAN MOTION" decal; "R007" on the recumbent bike).

## Only in group photos
- `xy-zbd-ib`, `xy-1a`, `xy-2b`, `recumbent-cross-trainer-interactive` and `interactive-training-cart` appear only in the Exercise Equipment 1/2 group leaflets.

## Not devices or left out
- Wired hand controllers of the CPMs, interchangeable peg-board modules and pegs, the 12 hand-station attachments of XY-101C/JY-CT-II, and the software (evaluation reports, games): these are mentioned in `form`/`specs`.
- The white swivel stool in the OT-table photo and the people in the photos are scene props.
- XY-101B is listed as a variant of XY-101C (non-rotating top, same look).

## Crops
All saved in `tools/medical/reference/` and checked by eye. There is no clean second angle for XY-CPM-IIB (the page prints the same photo twice). The ZBD photos have a light-blue gradient background from the leaflet. I made screen crops only where a screen shows content: interactive-training-cart, xy-101c, xy-mcb-i-deluxe, xy-jzj-i, xy-jzj-ii, xy-msz-i.

<!-- group g6_table_hydro -->
## g6_table_hydro — notes

84 devices (45 table, 37 hydro, 2 pediatric); 15 with printed sizes.

## Folder / file → device ids

- **多体位医用诊疗床/Treatment Table.pdf** (8 pp.; p1 cover scene, pp2–8 catalogue) → 23 tables:
  p2 xy-k-sf-1, xy-k-sf-1b, xy-k-sf-1-new · p3 xy-k-sf-2-new, xy-k-sf-3-new, xy-k-sf-2, xy-k-sf-3 ·
  p4 xy-k-sf-4b, xy-k-sf-4c, xy-k-sf-4, xy-k-sf-4d · p5 xy-k-sf-4-new, xy-k-sf-5, xy-k-sf-5-new ·
  p6 xy-k-sf-6b, xy-k-sf-7-new, xy-k-sf-6, xy-k-sf-7 · p7 xy-k-sf-8, xy-k-sf-8b · p8 xy-k-sf-9-new, xy-k-sf-9b, xy-k-sf-9.
  The p1 cover chair-table (patient sitting) looks like SF-4/SF-9 (new model) in chair position; not counted separately.
- **按摩/ALC-3.jpg** → alc-3. **按摩/Massage Table.jpg** → alc-1, alc-2.
- **牵引/Traction Table.pdf** (5 pp.) → p2 jyz-iiib, yhz-ii-microwave · p3 jyz-iiia, jyz-ib, jyz-iib, yhz-iv · p4 yhz-ii, rh-qyc-b ·
  p5 yhz-iaj, yz-4, yz-3, yz-2a. p1 = cover scene (traction bed + attached PC desk).
- **牵引/脊柱减压牵引床/Spinal Decompression Traction Table.pdf** → xy-k-rxqy-iii (pp1, 3, 4 show the same unit; p2 infographic).
- **牵引/脊柱减压牵引系统/Spinal Decompression Traction System.pdf** → xy-jzjy-iii (table + PC console cart as one entry).
- **直立床/Tilt Table.pdf** → p1 xyq-1, xyq-2 · p2 xyq-6, xyq-3, xyq-5, xyrt-41.
- **水疗/Aquatic Underwater Treadmill.pdf** → aquatic-underwater-treadmill (No-filtration / Filtration versions as variants).
- **水疗/Hydrotherapy.pdf** (12 pp.) → p1 oval-hydromassage-bathtub (cover only) · p2 butterfly tub = xy-sl-ci · p3 xy-sl-bi, -bii, -biii, -biv ·
  p4 xy-sl-cxi, xy-sl-cviii-luxury, xy-sl-cviii · p5 xy-sl-ciii, xy-sl-cix · p6 xy-sl-ci · p7 xy-sl-bvii, limb-whirlpool-bath-prototype ·
  p8 xy-sl-cv · p9 xy-sl-cvi · p10 floor-plan render (no new devices) · p11 xy-sl-ri, xy-sl-rii, baby-hydrotherapy-station · p12 xy-sl-riii, xy-sl-rv, xy-sl-riv.
- **熏蒸 (steam / fumigation)** — the "unlabelled" photos 1–7 are actually pages of one brochure, each with printed model names:
  - 1.jpg — cover: HYZ-IIIE capsule + its LCD trolley (→ hyz-iiie, view `hyz-iiie_2`)
  - 2.jpg — HYZ-IIY (2012) perianal fumigation chair + console → hyz-iiy
  - 3.jpg — HYZ-IIIE (→ hyz-iiie) and HYZ-IIIC (→ hyz-iiic)
  - 4.jpg — HYZ-IIID (→ hyz-iiid) and HYZ-IIIB "LCD model (new)" (→ hyz-iiib, view `hyz-iiib_3`)
  - 5.jpg — HYZ-IIK + console (→ hyz-iik) and HYZ-IIB + console (→ hyz-iib)
  - 6.jpg — HYZ-IA (→ hyz-ia), HYZ-IIC with trolley (→ hyz-iic, view `hyz-iic_2`), HYZ-IIF no trolley (→ hyz-iif)
  - 7.jpg — HYZ-IID, HYZ-IIE, HYZ-IB, HYZ-IC (→ hyz-iid, hyz-iie, hyz-ib, hyz-ic)
  - HYZ-IIC.jpg → hyz-iic (main photo) · HYZ-IIIB.pdf → hyz-iiib (printed size) · Steam therapy.jpg → hyz-iir (pediatric) · 熏蒸HYZ-IIIA.jpg → hyz-iiia.

## Duplicates between files
- HYZ-IIC: 熏蒸/HYZ-IIC.jpg and 熏蒸/6.jpg (one entry).
- HYZ-IIIB: 熏蒸/HYZ-IIIB.pdf and 熏蒸/4.jpg (one entry; size from the PDF).
- HYZ-IIIE: 熏蒸/1.jpg (cover) and 熏蒸/3.jpg.
- XY-SL-CI: Hydrotherapy p2 scene and p6.

## Doubts / ambiguities
- **YHZ-II** is used for two different products in Traction Table.pdf: p2 "Multifunctional traction bed YHZ-II (microwave therapy)" (green-top fibreglass body) and p4 "YHZ-II" steel traction table with console → ids `yhz-ii-microwave` and `yhz-ii`.
- **XY-K-SF-x vs "new model"**: same code, completely different bases (old: Z-columns / scissor; new: swan-neck arms) → separate ids with `-new` suffix.
- Unlabelled product photos assigned by thumbnails: Treatment Table p5 top-left = SF-4 (new model); p8 top-right = SF-9B.
- **XY-SL-CIX** printed "Size(cm): 196*75*685" — 685 is a misprint; height estimated 850.
- **XY-SL-CVI** prints both "Size: 1270 x 860 x 720/1000mm" and "Bathtub size: 1700 x 1530 x 1480mm" (contradictory); used 1270×860×1000.
- **XY-SL-RIV vs RV**: practically the same body in the photos; kept as two entries (different codes).
- **XY-SL-CVIII** luxury vs standard: same table, luxury adds hood → two entries.
- **HYZ-IIIA**: code only in the file name (photo label unreadable).
- **HYZ-IIIB** L×W×H mapped as printed to [1450, 840, 1900]; the capsule is tilted, so orientation of "length" is uncertain.
- XYRT-41: only the bed surface (1600×630, height 550) is printed; overall footprint estimated.
- RH-QYC-B carries "Rehamaster" branding (OEM product in Xiangyu leaflet).
- Category choices: children's tubs (XY-SL-R*) kept as `hydro` (tubs); XYRT-41 and HYZ-IIR are explicitly "pediatric" → `pediatric`. ALC far-infrared massage beds → `table`. Cervical traction chairs YZ-* → `table`.
- Some crops unavoidably contain leaflet text/callout lines (JYZ-IIIA, JYZ-IIB, XYQ-3, XYQ-6, XY-SL-BI, XY-SL-CXI, XY-SL-CI, limb prototype) because text overlaps the product's bounding box.

## Scene-only / unidentified
- `oval-hydromassage-bathtub` — only on the Hydrotherapy cover (p1), no code.
- `baby-hydrotherapy-station` — unlabelled 4-module photo on Hydrotherapy p11.
- `limb-whirlpool-bath-prototype` — "Under designing..." on p7, no code (sizes printed).
- Traction Table cover p1: JYZ-type traction bed with an attached PC desk (monitor, keyboard) — treated as the optional PC workstation of JYZ-IIIA/IIIB, not counted.
- Hydrotherapy p10: floor-plan render of a children's hydrotherapy centre (rehab pool, steam beds, showers) — illustration only, not counted.

## Not devices (accessories) — left out
- Patient transfer stretcher-lift and mobile patient hoists (Hydrotherapy p6 circles) — accessories of XY-SL-CI.
- Transfer chair for XY-SL-CVI (p9) — accessory.
- Cervical traction stool shipped with XY-K-RXQY-III — accessory.
- Separate consoles/trolleys of steam units (HYZ-IIIE, IIIB, IIK, IIB, IIC, IIY) — described inside each device's `form`, not separate entries.
- Foot pedals, handhold switches, traction harnesses, head halters, pillows, wedges — parts/accessories.
- Optional side pedals / front ramp of the aquatic treadmill — options (ramp described in form).

<!-- group g7_adult -->
## g7_adult — notes

129 devices, 122 with printed sizes (7 estimated: xyt-3, xy-30b, xy-zh-1, xy-zh-2, xy-90, xy-96, xy-97).
Categories: kinesio 103, table 12, other 12, physio 1 (xy-24 vibration belt massager), hydro 1 (xy-90 pool hoist).

## Files → device ids

### 049_Adult_Rehabilitation_Items — `成人康复/Adult Rehabilitation Items.pdf` (17 image-only spread pages, 2021 catalogue; all spec text readable at 150 dpi, zoomed where needed)
- p1 cover; no devices.
- p2 (left: About Us): xyf-z1, xyf-z2, xyf-z3, xyf-z4, xyf-t1, xyf-t2
- p3: xyf-t3, xyf-t4, xyc-t1, xyc-t2, xyz-5, xyz-6, xyg-1, xyg-2, xyj-1, xyj-2 (left out: crutches/canes XYZ-1, XYZ-2, XYZ-3, XYZ-4, XYZ-1A, XYZ-7)
- p4: xyj-3, xyj-4, xyj-5, xyj-6, xyj-7, xyn-1, xyn-2, xyn-3, xyn-4, xyn-7, xyn-6, xym-1, xym-2, xym-3, xym-4, xym-5, xym-6 (left out: XYN-5)
- p5: xyzg-1, xyyl-1, xyh-1, xyh-2, xyh-3, xygs-2, xygs-1, xy-kgj-1, xy-kgj-2
- p6: xyd-1, xyzl-1, xyql-1, xyhj-1, xyhj-2, xyzl-2, xyzl-3, xyhj-3, xyhj-4, xyt-1
- p7: xyt-2, xyt-3, xyx-1, xy-3, xy-4, xy-1, xy-2, xy-2a, xy-5, xy-6, xy-6a
- p8: xy-7, xy-8, xy-10, xy-11, xy-100, xy-12, xy-15, xy-16 (left out: XY-9)
- p9: xy-13, xy-14, xy-14-8a
- p10: xy-14-8b, xy-zh-1 (and its component units XY-JGJ-1, XY-SXZ-1, XY-WGJ-1, XY-JZ-1)
- p11: xy-zh-2 (component XY-JGJ-2), xy-20, xy-21 (left out: XY-17, XY-18, XY-19, XY-22)
- p12: xy-23, xy-24, xy-2b, xy-1a, xy-28, xy-29, xy-31, xy-30a, xy-30b, xy-32 (left out: XY-25, XY-26, XY-27)
- p13: xy-33, xy-34 (+XY-35 as a variant), xy-36, xy-39, xy-40, xy-41, xy-43, xy-44, xy-45, xy-46 (left out: XY-37, XY-38, XY-42)
- p14: xy-47, xy-49, xy-54, xy-50, xy-51, xy-57, xy-58, xy-59, xy-60 (left out: XY-48, XY-52, XY-53, XY-55, XY-56)
- p15: xy-78, xy-79, xy-80 (left out: XY-61 to XY-67, XY-65A, XY-75, XY-76, XY-77, XY-98, XY-99)
- p16: xy-70, xy-71, xy-72, xy-73, xy-91, xy-92 (left out: XY-93, XY-94, XY-95)
- p17: xy-81, xy-82, xy-83, xy-84, xy-85, xy-87, xy-88, xy-89, xy-90, xy-96, xy-97 (left out: XY-86)

### Single-product leaflets (`成人康复/单独产品/`)
- 050_Static_Bike → xy-1. Duplicate of catalogue p7. Leaflet photo is used (it is better). Sizes differ: the leaflet says 880×520×1250 mm, the catalogue says 90×45×106 cm. I used the leaflet size.
- 051_XY_72_PT_Table → xy-72. Duplicate of catalogue p16 (same size). Weight is 127 kg in the leaflet and 150 kg in the catalogue. Leaflet photo is used.
- 052_XYG_3 → xyg-3, Electrical Parallel Bar. This one is NOT in the catalogue; the leaflet is its only source.
- 053_XYGS_2 → xygs-2. Duplicate of catalogue p5. Sizes differ: the leaflet says 106×105×116 cm, the catalogue says 113×112×116 cm. I used the leaflet size and the leaflet photo.

## Category / scope decisions
- Following the group instruction (tables/chairs → `table`): exercise chairs xyzg-1, xygs-2, xy-kgj-2, xy-100, plus PT tables xy-70..73, OT desk xy-46, PT stool xy-81, overbed table xy-83, nesting stools xy-80 are `table`.
  OT workstation cabinet xy-54 and tilting OT board xy-33 kept `kinesio` (brief: OT tables → kinesio). Shower chairs xy-84/85, commodes xy-78/79, wheelchair, hoist, kitchens, lifts → `other`.
- Small table-top OT items with a model code and a real 3D structure (peg boards, geometry/cylinder ladders, quoits, bead maze, wire mazes, screws/nuts boards, labyrinth, finger ladder, toy chair) were kept as `desk` devices, since the brief lists peg boards under kinesio. They are small (≤ 1100 mm, mostly 200–400 mm).
- Racks that hold accessories were kept, because they are furniture-like items that stand in a room: dumbbell rack xyyl-1, ball/rod racks xym-1/xym-2, sandbag trolleys xy-15/xy-16.
- Walkers kept: the frame walkers XYF-Z1..Z4 and the folding walkers XYZ-5/XYZ-6.

## Left out (not devices / loose accessories), with reason
- Crutches, canes, walking sticks: XYZ-1 crutch, XYZ-2 elbow crutch, XYZ-3 axillary crutches, XYZ-4 walking stick (quad base), XYZ-1A tactile stick, XYZ-7 cane with stool. Reason: personal hand-held walking aids, not room equipment.
- XYN-5 Fingers Exerciser. Reason: a wooden carry case with cones and pegs, i.e. a loose kit.
- XY-9 Elastic Band. Reason: accessory.
- Mats and positioning items: XY-17 / XY-18 / XY-19 mattresses (178–200×120×5–10 cm), XY-22 hand underprops, XY-52 foam roller, XY-75 wedge, XY-76 soft wedging pads, XY-98 transfer board. Reason: these are mats and soft positioning items.
- Small loose OT accessories:
  - XY-25 / XY-26 / XY-27 finger boards (hand splint boards)
  - XY-37 geometric drawing flashboard and XY-38 cognition flashboard (flat puzzles)
  - XY-42 finger inserting balls box and XY-48 hand function exerciser box (cases)
  - XY-53 dressing boards (cloth)
  - XY-55 stacking cups and XY-56 simulation tools set
  - XY-86 speech training cards case
- Assessment instruments: XY-61 upper limb function evaluator (case), XY-62 goniometer set, XY-63 joint motion goniometer, XY-64 pedometer, XY-65 stopwatch, XY-65A bathroom scale, XY-66 / XY-66A hand dynamometers, XY-67 back strength meter.
- Daily-living hand aids: XY-77 fetching tool and XY-99 dressing aid rod.
- Accessibility fittings: XY-93 portable sloping plate (aluminium ramp, 242×76×9.5 cm), XY-94 tactile floor tiles (30×30 cm), XY-95 toilet handrails. Reason: fittings, not stand-alone equipment.
- Component units listed only as variants inside xy-zh-1 / xy-zh-2: XY-JGJ-1, XY-SXZ-1, XY-WGJ-1, XY-JZ-1, XY-JGJ-2. They are also sold separately, but their only photos are small cut-outs.
- Modules inside the combo trainers xy-13 / xy-14 / xy-14-8a / xy-14-8b are the same as the stand-alone wall units xyj-1/2/4/5/6, xyn-4, xy-7, xy-12. They are not counted again.

## Doubts / ambiguities
- **L×W×H mapping.** For devices the user walks into or sits on facing along the length (walkers, standing frames, bikes, rower, steppers, ankle trainers), I mapped size as [W, L, H]. For everything else it is [L, W, H]. Each sizeNote says which mapping was used.
- **Height ranges.** Where a height range is printed, `size` uses the maximum.
- **xyql-1.** Height is printed as "125~113", which looks like a typo for 113–125.
- **xy-71.** The first digit of "191*125*49" is blurred in the source, so it could be 191 or 197.
- **xy-30b.** The printed size "7×7×7 cm" cannot be the whole board; it is probably one block. I estimated the board at 300×250×80 and set printed:false.
- **xy-45.** All three parts (shelf, small tablet, large tablet) are printed with the same 70×49×54. The value is suspicious.
- **xy-14-8b.** Two photos on p10, one with a blue table and one with a grey table. I treated them as one model. The main photo is the labelled grey one; the blue one is view _2.
- **xyf-z4.** The photo shows a walker plus a separate wheeled seat module. I kept it as one device.
- **xy-34 / XY-35.** These are identical-size ring-toss boards, so they are one entry with variants. View _2 shows the XY-35 board.
- **xy-54.** The main photo is the front view with the fold-down work tray (cleaner crop). View _2 is the door-front view.
- **xy-79.** The source photo has a semi-transparent text overlay ("135kg …") baked into it. It cannot be removed.
- **xy-91.** This is a vehicle accessory (wheelchair lift for a car), so it hardly belongs in a room. It is included as `other`. Its third photo was dropped because overlay text covers it.
- **Text in crops.** Leftover catalogue title/label text inside some crops was painted white (xy-39, xy-40, xy-54, xy-60, etc.). Only text was painted out; no product parts were.
- **No screens.** No device has a readable screen face, so there is no screenCrop anywhere. The bikes' and the XY-ZH units' displays are too small.

<!-- group g8_ped_sensory -->
## g8_ped_sensory — notes

Files: `儿童康复/Pediatric rehabilitation series.pdf` (slug 008, 14 image-only pages) → 65 devices (category pediatric);
`多感官房间/Multi-sensory Training Room.pdf` (slug 044, 2 wide text pages) → 25 devices (category sensory). Total 90, of them 53 with printed sizes (all in the pediatric leaflet; the sensory leaflet prints no dimensions at all).

Legend: **[D]** = became a device entry (id in brackets); **[N]** = left in notes (small loose toy / accessory / consumable).

## 008 Pediatric rehabilitation series — every item in leaflet order

- p1 — cover (no products).
- p2 (left half "About us", right half):
  - Gait training system XY-K-E1 **[D xy-k-e1]**
  - Gait training system XY-K-E2 **[D xy-k-e2]**
  - Gait training system XY-K-E3 (E2-type frame + treadmill) **[D xy-k-e3]**
  - Medical treadmill XYRT-122 (running area 400×1210 mm) **[D xyrt-122]**
  - Training swing device XYRT-4 **[D xyrt-4]**
  - Training swing device XYRT-5 **[D xyrt-5]**
- p3:
  - Children parallel bar XYRT-6 **[D]** · Children training stairs XYRT-7 **[D]** · Children standing frame XYRT-10 **[D]** · Standing board XYRT-106 **[D]** · Inclined standing frame XYRT-107 **[D]**
  - Children standing frame XYRT-8 **[D]** · Children sitting posture correction chair XYRT-9 **[D]** (two photos: without/with tray → view) · Upper limb pushing XYRT-108 **[D]** · Children wall bars XYRT-11 **[D]** · Child ladder chair XYRT-12 **[D]**
- p4:
  - Horse riding machine XYRT-116 **[D]** · Boating exerciser XYRT-117 **[D]** · Ladder chair XYRT-13 **[D]** · Trampoline with handrail XYRT-15 **[D]** · Trampoline XYRT-16 **[D]** · Children safety chair XYRT-19 **[D]**
  - Waist twisting machine XYRT-118 **[D]** · Exercise bicycle XYRT-119 **[D]** · Space walker XYRT-120 **[D]** · Treadmills XYRT-121 **[D]** · Adjustable sanding board XYRT-14 **[D]** · Wooden bed XYRT-17 **[D]** · Guided training set XYRT-18 **[D]**
- p5:
  - Children PT stool XYRT-21 **[D]** · Finger correcting board XYRT-22 (22×19×2 cm) **[N]** · Extremities recovery device XYRT-26 **[D]** · Tow-castor walking assistant XYRT-27 **[D]** · Hydraulic children treadle XYRT-28 **[D]**
  - Finger correcting board with universal wheel XYRT-23 (24×22×6) **[N]** · Correcting back belt XYRT-24 (orthosis) **[N]** · Tow-castor walking assistant XYRT-25 **[D]** · Tumbling barrel XYRT-29 **[D]** · Drilling cage XYRT-30 **[D]** · Drilling cage XYRT-31 **[D]**
- p6:
  - Gym ball 75 cm XYRT-32 **[N]** · Gym ball 85 cm XYRT-33 **[N]** · Gym ball 65 cm XYRT-33A **[N]** · Hip-joint training device XYRT-38 **[D]** · Children quadriceps chair XYRT-39 **[D]** · Ankle joint training device XYRT-40 **[D]**
  - Jump ball 45 cm XYRT-34 **[N]** · Jump ball 55 cm XYRT-35 **[N]** · Peanut ball 70 cm XYRT-37 **[N]** · Children OT table XYRT-36 **[D]** · OT desk XYRT-36A **[D]**
- p7:
  - PT training table XY-71 **[D]** · Electric lifting PT training table (folding) XY-72 **[D]** · Staircase XYC-T2 **[D]** · Ball bath XYRT-44 **[D]**
  - Children helmet XYRT-42 **[N]** · Sliding board XYRT-43 **[D]** · Children sand bag (bandage type) XYRT-45 **[D]** (the cart with bags) · Children sand bag (lifting type) XYRT-46 **[D]** · Protective belt XYRT-47 (gait belt) **[N]**
- p8 (all small desk toys/OT tools except one):
  - Children roller XYRT-48 (Ø22×80) **[N]** · Children dumbbell XYRT-110 **[N]** · Training quoit XYRT-49 **[N]** · Cylinder ladder XY-30B **[N]** · Quoits XY-34 **[N]** · Quoits XY-35 **[N]**
  - Training quoit XYRT-49A **[N]** · Creeping frame XYRT-50 **[D]** · Children tools table XYRT-51 (toy work bench; printed spec copies XYRT-50's 80×40×47~62 — probably a leaflet error) **[N]** · Geometric drawing flashboard XY-37 **[N]** · Cognition drawing flash board XY-38 **[N]** · Hand function combined trainer XY-48 (50×40×14 box) **[N]**
  - Colorful chain XYRT-51B **[N]** · Color plates XYRT-51C **[N]** · Geometry ladder XY-30A **[N]** · Upper limbs coordination training chair XY-50 (24×23×12 toy) **[N]** · Hand balance coordination trainer XY-59 **[N]** · Puzzles XYRT-52 **[N]**
- p9 (all toys) **[N]**: Word cognitive puzzle XYRT-52A · Geometry cognitive puzzle XYRT-52B · Shaped wheel XYRT-53 · Wearing shoe trainer XYRT-55B · Multifunctional learning toys XYRT-56 · Intelligence development assembly XYRT-56B · Toy bricks XYRT-54 · Children splicing toy bricks XYRT-54A · Intelligence development assembly (walker cart with blocks) XYRT-56C · Hammer ball trainer XYRT-57B · Children cognition training groupware XYRT-58 (50×37×36 box) · Holding balls XYRT-55 · Stress ball XYRT-111 · Cognition toys XYRT-59 (30 cm cube) · Cognition toys XYRT-59A.
- p10:
  - Magnetic buttons XYRT-60 **[N]** · Children cognitive groupware XYRT-61 **[N]** · Big drawing board XYRT-100 **[D]** (easel) · Colourful drawing board XYRT-101 **[D]** (easel) · Cognitive blocks XYRT-102 **[N]**
  - Nut assembly XYRT-62 **[N]** · Multifunctional perception assembly XYRT-95 **[N]** · Eye function assembly XYRT-96 **[N]** · Multifunctional cognitive assembly XYRT-103 **[D]** (child table + 2 stools) · Intelligence puzzle assembly XYRT-105 **[N]** · Plasticene XYRT-63 **[N]**
  - Balance coordination assembly XYRT-97 **[N]** · Colorful fifteen tones assembly (xylophone) XYRT-98 **[N]** · Intellectual development assembly (doll house) XYRT-99 **[N]** · Finger coordination XYRT-63A **[N]** · Fruit model XYRT-64 **[N]**
- p11:
  - Balance footpath XYRT-67 **[D]** (floor mat set)
  - Ball group **[N]**: XYRT-68 colored tellurian Ø50 · XYRT-69 jump ball Ø46 · XYRT-70 massage ball Ø70 · XYRT-71 jump ball Ø56 · XYRT-72 massage ball Ø46 · XYRT-73 pull-tap jump ball Ø36 · XYRT-74 soft ball Ø12 · XYRT-75 foot massage ball · XYRT-76 soft soccer Ø18 · XYRT-77 soft ball Ø15 · XYRT-78 pull-tap jump ball Ø36
  - Balance pedal XYRT-66 **[D]** · Round trochlea XYRT-79 **[D]** · Round rotary tables XYRT-80 **[D]** · Spine cushion XYRT-81 (33×33×6) **[N]** · Snail balance board XYRT-82 (Ø54) **[N]** · Jumping bag XYRT-85 **[N]** · Balance board XYRT-86 (55×23×14) **[N]** · Magnetic geometry balance XYRT-94 **[N]**
- p12:
  - Balance lines XYRT-83 **[D]** (16-piece beam set) · Manifold assembly XYRT-65 **[D]** (obstacle course kit)
  - Montessori teaching set "Montgomery Teaching Elite Edition" (138 categories model A / 88 model B; 14 wooden boxes: eight-colour ball, three-body, 6 cm cubes, Gabe sets) — no code **[N]** (desk teaching material).
- p13:
  - Bosu ball (stepping half-balls), Aerated horse (inflatable hop horse), Stone for trampling, 88 pathway (S-track ball game, 34×21×4 cm), Magic wheel (Ø17 cm) — no codes **[N]** (small loose toys)
  - Kid's heaven: Training stairs XYRT-87 + Drill tube tunnel XYRT-88 **[D xyrt-87]** (one combined soft-play assembly, both codes in `variants`)
  - Soft package of building block (with soft balance beam) — no code **[D soft-building-blocks]**
- p14:
  - Square combined training frame and background protection — no code **[D square-combined-training-frame]** (2 photos, treated as two sides of one frame)
  - Triangle ball pool — no code **[D triangle-ball-pool]**
  - XYRT-93 Rock climbing equipment (Ø160 cm ring of four 1/4 arcs) **[D xyrt-93]**
  - Circular walking (soft S-path) — no code **[D circular-walking]**

## 044 Multi-sensory Training Room — every item in leaflet order (no codes except JY-TYHD-Ⅰ; no sizes printed)

- p1: two room renders (scene) · Multimedia Scenario Interactive Training System JY-TYHD-Ⅰ **[D jy-tyhd-i]** · Piano Water Column **[D]** · Dynamic Color Wheel **[D]** · Wall of Blisters **[D]** · Sound and Light Wall Panel **[D]** · Variable Speed Fan Game Box **[D]** · Cognitive Training Board **[D]** · Endless Depth Light Mirror **[D]** · Fiber Optic Curtain Wall **[D]** · Color Conversion Control Panel **[D]** · Smell Perception Game Box **[D]** · LED Piano Pedals **[D]**
- p2: Lighting Color Changing Puzzle Table **[D]** · Music Training Device **[D]** · Visual Perceptual Trainer (bubble tubes) **[D]** · Multimedia Scenario Interactive System (ceiling floor-projection) **[D]** · Colorful Fluorescent Drawing Board **[D]** · Butterfly Fiber Falls **[D]** · Color LED Ball **[D]** · Symphony Hemisphere Light **[D]** · Bean Bag **[D]** · Sound Amplifier **[D]** (amp + 2 speakers) · Multi-sensory Master Control Machine **[D]** · Multi-sensory Matching Projection System (projector) **[D]**
- Scene-only (room renders p1): soft ball pool with red/green foam walls **[D sensory-soft-ball-pool]**. Also visible but not made devices: padded wall cushions (red/blue/green/yellow vertical panels ~1000 high), interlocking EVA foam floor tiles (pink/yellow/blue/green ~600), a ceiling fibre-optic "shower" (vertical clear strands from a ceiling ring — possibly the Butterfly Fiber Falls/fibre item in another form), ceiling LED rings, a wall projection screen (part of the projection system), a teal wall-mounted TV-like panel and an operator desk — room finishes/furniture, mentioned for the room builder.
- Ids of the 044 file use English slugs (no codes); `code` = null except jy-tyhd-i.

## Doubts / ambiguities

- **Duplicates with another leaflet:** XY-71, XY-72 and XYC-T2 also appear in another group's leaflet (another agent saved `xy-71.jpg`, `xy-72.jpg`, `xy-72_2.jpg`, `xyc-t1.jpg`, `xyc-t2.jpg` after my crops, overwriting them with equivalent photos of the same products). My entries point to those same files; dedupe by id when merging. Other XYRT codes may also repeat in OT/PT leaflets (e.g. XYRT-41 tilt table exists elsewhere, not in my file).
- **Size interpretation:** XYRT-19 "105×53×86" mapped as H 1050 / W 530 / D 860 (photo shows the chair taller than deep); XYRT-15 "ϕ97×12" — 12 cm is mat/frame height, overall with handrail ~1000 estimated; XYRT-100 "95×43×4" read as easel 950 high, board 430 wide, 40 thick; XYRT-103 "48×6×60.5" read as table 480 wide/605 high (6 = board thickness?); XYC-T2 "60×33~120×40" read as nested 600×330 → unfolded 1200×400, depth not printed; XYRT-27 47×43×43 seems low for a walker; XYRT-38 height 72 seems low versus photo (backrest); XYRT-65 printed size is one bridge assembly, not the whole kit; XYRT-36A only height/width printed. Lengths along the "use direction" (walkers, bikes, standers) were mapped to depth; long items (bars, stairs, beds, slides) to width.
- **XYRT-51** prints exactly the XYRT-50 dimensions — likely copy error; it is a toy tool bench → notes.
- **XY-K-E3**: E2 frame + treadmill shown together; one entry (treadmill not separately coded).
- **Kid's heaven**: XYRT-87 (stairs) and XYRT-88 (tunnel) are parts of one assembly → one entry `xyrt-87`, both codes in `variants`.
- **Sensory wall panels**: the leaflet thumbnails show coloured "bear-ear" cases; the room renders show the same panel family as white rounded cases with 3 buttons, ~600×900, ~400 above floor. All 9 panel items share size estimates [600, 90–150, 900]. No screenCrops made (panels' faces are the photo itself; tiny thumbnails ~120 px).
- **Sensory thumbnails are very small** (≈100–250 px source); photos are low-res. JY-TYHD-Ⅰ is the only large clean render.
- `printed` for partially printed items (XYRT-36A, XYRT-103, XYRT-65, XYRT-83 per-piece, XYRT-67 per-piece, XYC-T2) set true with mapping explained in `sizeNote`.

## Left out (not devices)
- All balls (gym, jump, peanut, massage, soft), desk toys/puzzles/OT kits on p8–p10, Montessori set, small balance toys (spine cushion, snail/balance boards, jumping bag, magnetic balance), stepping stones, Bosu, aerated horse, 88 pathway, magic wheel — small loose toys/accessories.
- Correcting back belt XYRT-24, helmet XYRT-42, protective gait belt XYRT-47 — wearables/accessories.
- Finger correcting boards XYRT-22/23 — small hand boards.
- Removed weak views: tiny cone pieces of XYRT-30/31 (pixelated, accessory pieces).
