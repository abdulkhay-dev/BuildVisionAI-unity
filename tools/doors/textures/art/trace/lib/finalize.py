"""Writes a traced art file in the pane coordinates of the design that sells the glass."""
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[2]
# traced pane (leaf mm, as measured on the photos) -> the design's visible glass (leaf mm)
PANES = {'sprig': ((141.5, 0, 277, 2000), (141.1, 0, 277.0, 2000)),          # Designs/glace-1.json
         'twig': ((141.5, 0, 277, 2000), (141.1, 0, 277.0, 2000)),
         'twig-2': ((272, 0, 518, 2000), (264.6, 0, 520.6, 2000)),           # Designs/glace-2.json
         'vitrazh': ((290.5, 199, 488.5, 1792.5), (290.1, 195, 492.8, 1792)),  # Designs/trend-14.json
         'print': ((130.5, 0, 667, 2000), (135.5, 0, 668, 2000)),            # Designs/s-13.json
         'stamp': ((130.5, 0, 667, 2000), (135.5, 0, 668, 2000)),
         'mystic': (None, (146, 916, 654, 1851)),                            # Designs/simpl-15-2.json
         'mystic-small': (None, (146, 679, 654, 764))}


def _shift(v, dx, dy):
    if isinstance(v, list) and v and isinstance(v[0], (int, float)):
        return [round(v[0] + dx, 3), round(v[1] + dy, 3)] + [round(q, 3) for q in v[2:]]
    return [_shift(q, dx, dy) for q in v]


def save_art(name, art):
    src, dst = PANES[name]
    if src is not None:
        dx, dy = src[0] - dst[0], src[1] - dst[1]
        for L in art['layers']:
            for it in L['items']:
                for key in ('poly', 'stroke'):
                    if key in it:
                        it[key] = _shift(it[key], dx, dy)
    for L in art['layers']:
        for it in L['items']:
            it.pop('depth', None)
    art['size'] = [round(dst[2] - dst[0], 2), round(dst[3] - dst[1], 2)]
    art['pane'] = list(dst)
    (ART / f'{name}.json').write_text(json.dumps(art, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
