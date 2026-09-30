# Decor map: provisional finish colours → decor materials

`decor_map.json` maps every textured-decor role of the casegoods finishes (catalog.json `body` / `front` / `back` /
`roles.*`) to its library material; `apply_decors.py` applies it as materials land. Sources: `decors.md` (with the
merged per-collection decor lists), `notes/*.md` and the generators `gen/*.py`.

- **124 roles in 75 finishes mapped** (47 materials). **76 roles kept** as they are (`keep`: plain unis, gloss / metal
  specials, the `_test` finish), each with a reason. **0 finish roles unmapped.** 7 roles unattributed (below).
- Tintable (`cg_massiv`, `cgfab_*`): `tint` = the provisional colour (the target); the script writes
  `<id>#<target ÷ albedo mean, linear, clamped>`. Baked materials are written bare, so every finish of one decor gets the
  material's single colour — see the conflicts.
- No mapped role carries `@gloss` now (the only `@gloss` is Монако's plain white front).

```
/private/tmp/claude-501/venv/bin/python tools/casegoods/apply_decors.py                  # dry run (report)
/private/tmp/claude-501/venv/bin/python tools/casegoods/apply_decors.py --prints -v      # + British Bum prints, list skipped roles
/private/tmp/claude-501/venv/bin/python tools/casegoods/apply_decors.py --write --prints  # apply the ready ones
    --only cg_dub_kanon,cgfab_velur   just these materials;   --no-registry   do not require the id in external.json
```
A material is "ready" when `External/Materials/<id>/` holds an albedo **and** external.json lists the id (the engine
resolves names from the imported catalogue; an unregistered id would fall back to the body colour). Re-runnable: applied
roles report as "already applied"; a role changed by hand since the map reports as "changed" and is left alone.

## Attributions to check (in the map, but judgement calls)

| finish · role | now | mapped to | why unsure |
|---|---|---|---|
| kanon-loft-kanon-black · frame | `#2b2c30` | `cg_cherny_660` | notes say «Черный 660 ТМ»; decors.md lists only Блэквуд's «Черный 660 WML» |
| linel-belyi, linel-moloko-belyi · birch | `#d9bf94` | `cg_massiv` tint | bed slats, photo colour; notes/linel.md says «no textured decors» |
| brauni-kanon-black · fabric | `velvet#1f1f1f` | `cgfab_velur` | may be eco-leather (notes/brauni.md) → `cgfab_ekokozha` |
| yunona-layt-kanon-bordo · fabric | `velvet#846d5d` | `cgfab_velur` | decors.md: «velour / matt eco-leather» |
| british-bum-krem-tryufel · fabric, fabric_light | `door_enamel_whitey#9e958e` / `#bfbbb2` | `cgfab_velur` | decors.md: «plain velour / matting» → maybe `cgfab_rogozhka` |
| blekvud-loft-votan-cherny · fabric; holten-loft-lancelot-stirling · fabric | `velvet#5a544d` / `#645c4d` | `cgfab_velur` | not in decors.md; colour from product photos |
| marlen-zhemchug-gikori · fabric | *(absent → engine default Linen)* | `cgfab_rogozhka` tint `#c9bcab` | the role is **added**; colour from notes/w1.md (photo) |
| eliza-vanil · ornament | `gold#d2b479` | `cgprint_eliza_rozy` | a flat gilded plate now; the print must carry its own gold and ground |
| martina-moloko-silver · carve | `#b4b6b8` | `cg_martina_listya` | the lily blocks (pilasters, table legs, mirror) share role `carve` and get the leaves too — give them their own role |
| nord-loft-dub-massiv / nord-loft-votan · body | = top colour | the top's decor | the tables' body colour equals the top; check what `body` covers there |
| ken-ontario · body | `#a8937c` | `cg_dub_ontario` | the «ёлочка» УФ print stays milled grooves — no print material was ordered |

Also: Агата's decors are «under high-gloss lacquer» in decors.md (Береза; Бордо лайт «glossy on the fronts») but its
finishes have no `@gloss`; the map keeps them matt. Add `@gloss` in decor_map.json if the lead wants it.

## Unattributed (nothing to apply)

Roles that fall to the engine's default fabric (library **Linen**, CaseBuilder `fabric` → `M.Linen`) because the finish
has no `fabric` role — no fabric named or colour sampled, so no target:

| finishes | pieces | what is known |
|---|---|---|
| agata-bereza, agata-bordo-light | bed's upholstered pads | nothing |
| arista-nubuk | channelled headboards 1.24 / 1.45 | «light grey in the catalogue» (notes/w1.md) |
| flora-samshit, flora-pepel | bed soft panel | nothing |
| turin-sosna-karelia, turin-dub-kanyon | soft headboards | «ivory / beige leatherette» (notes/w1.md) → `cgfab_ekokozha`, colour not sampled |

Sample a colour (`gen/catpage.py <page> --swatch …`), then add an entry with `"old": null` (the script adds the role).

Out of scope of the map (design-level, not finish roles): the designs also carry literal provisional colours —
`door_enamel_whitey#c9a877` / `#c9a877` (drawer boxes, slats; 1760 uses), `#d8bf95` (Блэквуд), `#c9a77c` (Монако),
`#8a9ba7` (Акцент), `#8c8c8c` (Призма) and a few more. If some are decors (birch-ply drawer boxes), they need a role or a
design edit.

## Colour conflicts (one baked material, several catalogue colours)

The same decor sampled from different swatch prints / collections; ΔE76 = the largest pair distance. A baked material
has one colour, so the lead picks (or orders a tinted variant / second material) where the spread is large.

| material | ΔE76 | provisional colours (finish · role) |
|---|---|---|
| `cg_dub_votan` | 28.8 | `#7a5b41` nord-loft-votan body, top · `#9b7146` plato-dub-votan · `#9f836e` blekvud-loft-votan-cherny body · `#c4a58c` layn-kamen-votan body (Лайн's «376 WML» prints much lighter) |
| `cg_dub_kanon` | 25.5 | `#7f6951` veres · `#856649` brauni body, front · `#8a6b4e` turin, format, globus · `#8b6c4f` plato · `#8c6d51` oskar · `#978071` yunona body, kanon · **`#b29e96` kanon-loft body, front** (light grey-beige — nearly a different decor) |
| `cg_dub_kantri_zolotoy` | 16.2 | `#846c48` roksi-green body · `#a88059` parma top · `#b39266` denver front, simpl body |
| `cg_dub_tryufelny` | 15.0 | `#786657` british-bum body · `#9c886c` plato-dub-tryufelnyy |
| `cg_dub_ontario` | 14.1 | `#a08357` lari, myunhen · `#a8937c` ken |
| `cg_sosna_kareliya` | 13.1 | `#c6c4c5` vizit (darker print) · `#e4e5e1` myunhen · `#e6e7e1` turin, format, sonata-bum · `#e7e7e1` globus, plato · `#e7e8e1` oskar |
| `cg_dub_stirling` | 11.7 | `#755a4a` holten-loft body · `#8b6b4b` grande-stirling |
| `cg_dub_kanzas` | 9.9 | `#705b4e` forte-loft · `#74543b` lari · `#74543c` myunhen · `#7d6752` arista oak · `#7e6753` denver front |
| `cg_dub_bordo_layt` | 9.3 | `#cecece` chelsi-bum front · `#d4d4d8` yunona front, back, bordo, edge · `#dbd8d7` veres front · `#e7e7e1` agata, sorrento body, front |
| `cg_dub_madura` | 9.1 | `#b09989` ardo · `#beb1a1` aktsent |
| `cg_sosna_randers` | 6.8 | `#c7c8c3` luna · `#d9d9d9` parma body, front |
| `cg_dub_sonoma` | 5.8 | `#b99c85` boro · `#caab92` gress («Сонома светлый») |
| `cg_cherny_660` | 3.5 | `#26252b` blekvud front · `#2b2c30` kanon-loft frame |
| `cg_gikori_kingston` | 0.6 | `#a1876f` triniti ×2, vena · `#a2886f` marlen |

(`cg_massiv` and `cgfab_*` are tinted per role, so their different colours are not conflicts.)
