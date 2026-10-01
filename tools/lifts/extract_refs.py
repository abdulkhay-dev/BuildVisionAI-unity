"""Reference crops from the GLZ/NBSL lift catalogue (glz2024catalog.pdf).

Coordinates are in 100-dpi pixels of the PDF spread (pt * 100/72), as measured on
thumbnails. Cabin photos are extracted from the embedded image at native
resolution when the photo is a single image; everything else is clip-rendered.

usage: python tools/lifts/extract_refs.py /path/to/glz2024catalog.pdf
"""
import io, os, sys
import pymupdf as fitz
from PIL import Image, ImageStat

PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/Downloads/glz2024catalog.pdf')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reference')
MAX_BYTES = 400_000

doc = fitz.open(PDF)


def rect(box, pad=0):
    x0, y0, x1, y1 = box
    k = 72 / 100
    return fitz.Rect((x0 - pad) * k, (y0 - pad) * k, (x1 + pad) * k, (y1 + pad) * k)


def save_jpg(img, path):
    img = img.convert('RGB')
    q = 92
    while True:
        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=q, optimize=True)
        if buf.tell() <= MAX_BYTES or q <= 50:
            break
        q -= 6
    if buf.tell() > MAX_BYTES:  # still too big: downscale
        w, h = img.size
        img = img.resize((int(w * .8), int(h * .8)), Image.LANCZOS)
        return save_jpg(img, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(buf.getvalue())
    return img.size, buf.tell()


def render(page, box, dpi=300, pad=0):
    pix = doc[page].get_pixmap(dpi=dpi, clip=rect(box, pad), alpha=False)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def embedded(xref):
    pix = fitz.Pixmap(doc, xref)
    if pix.colorspace and pix.colorspace.n != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    img = Image.frombytes('RGBA' if pix.alpha else 'RGB', (pix.width, pix.height), pix.samples)
    smask = doc.xref_get_key(xref, 'SMask')
    if smask[0] == 'xref':
        m = fitz.Pixmap(doc, int(smask[1].split()[0]))
        mask = Image.frombytes('L', (m.width, m.height), m.samples).resize(img.size)
        bg = Image.new('RGB', img.size, 'white')
        bg.paste(img.convert('RGB'), mask=mask)
        img = bg
    return img


def out(kind, name, img, log):
    path = os.path.join(OUT, kind, name + '.jpg')
    size, nbytes = save_jpg(img, path)
    log.append(f'{kind}/{name}.jpg {size[0]}x{size[1]} {nbytes // 1024}KB')


def main():
    log = []
    # --- cabins: (page, xref or None, box) -------------------------------
    cabins = {
        'sl-1036': (7, 140, [339, 262, 753, 912]),
        'sl-1072': (7, 142, [1169, 262, 1621, 912]),
        'sl-1134': (8, 157, [938, 640, 1227, 1093]),
        'sl-1095': (8, 159, [1308, 640, 1596, 1093]),
        'sl-1109': (9, 178, [81, 640, 369, 1093]),
        'sl-1135': (9, 168, [450, 640, 739, 1093]),
        'sl-1136': (9, 180, [938, 640, 1227, 1093]),
        'sl-1137': (9, 166, [1318, 640, 1607, 1093]),
        'sl-621': (10, 202, [911, 199, 1082, 638]),
        'sl-1037': (10, 191, [1165, 200, 1343, 637]),
        'sl-1130': (10, 204, [1412, 199, 1569, 638]),
        'sl-1152': (20, 440, [335, 301, 776, 871]),
        'sl-1146': (20, 438, [1163, 301, 1604, 871]),
        'sl-1156': (21, None, [333, 305, 780, 860]),
    }
    for cid, (p, xref, box) in cabins.items():
        img = None
        if xref:
            try:
                img = embedded(xref)
            except Exception as e:  # fall back to a render
                print('embed failed', cid, e)
        if img is None or img.width < 300:
            img = render(p, box, dpi=250)
        out('cabins', cid, img, log)

    # --- landing doors (composites: frame + leaf + LOP) -> clip render ------
    doors = {
        'sl-7061': (14, [328, 262, 524, 583]),
        'sl-7105': (14, [83, 695, 279, 1016]),
        'sl-8055': (14, [568, 695, 764, 1016]),
        'sl-7001': (14, [950, 264, 1145, 585]),
        'sl-7014': (14, [1434, 264, 1630, 585]),
        'sl-7037': (14, [1195, 697, 1391, 1018]),
        'painted-b531p': (20, [80, 299, 276, 556]),
        'plain-stainless': (20, [902, 299, 1098, 556]),
        'plain-stainless-4p': (21, [80, 299, 276, 556]),
    }
    for did, (p, box) in doors.items():
        out('doors', did, render(p, box, dpi=300), log)

    ceilings = {
        'sl-2132j': [80, 199, 335, 306], 'sl-2007e': [456, 200, 712, 305],
        'sl-2053': [80, 363, 335, 463], 'sl-2155j': [456, 362, 712, 464],
        'sld-600j': [80, 531, 335, 630], 'sl-2227j': [456, 531, 712, 626],
    }
    for k, box in ceilings.items():
        out('ceilings', k, render(13, box, dpi=300, pad=2), log)

    handrails = {
        'sl-3001': [1068, 198, 1575, 218], 'sl-3101tj': [1068, 286, 1575, 313],
        'sl-3201': [1068, 383, 1575, 409], 'sl-3301': [1068, 481, 1575, 515],
        'sl-3401': [1068, 586, 1575, 621], 'sl-3501j': [1068, 692, 1575, 726],
    }
    for k, box in handrails.items():
        out('handrails', k, render(13, box, dpi=300, pad=3), log)

    floors = {
        'sl-4006p': (13, [82, 827, 184, 928]), 'sl-4021p': (13, [211, 827, 313, 928]),
        'sl-4025p': (13, [342, 827, 444, 928]), 'sl-4027p': (13, [82, 965, 184, 1067]),
        'sl-4034p': (13, [211, 965, 313, 1067]), 'sl-4173p': (13, [342, 965, 444, 1067]),
        'sl-4106d': (13, [483, 827, 584, 928]), 'sl-4145d': (13, [617, 827, 718, 928]),
        'sl-4157d': (13, [483, 965, 584, 1067]), 'sl-4182d': (13, [617, 965, 718, 1067]),
        'checker-steel': (20, [593, 955, 734, 1060]),
        'checker-stainless': (20, [1426, 955, 1567, 1060]),
    }
    for k, (p, box) in floors.items():
        out('floors', k, render(p, box, dpi=400), log)

    # --- colour swatches: crop + mean colour --------------------------------
    colors = {
        'b501p': (13, [961, 890, 1141, 954]), 'b505p': (13, [1179, 890, 1359, 954]),
        '535p': (13, [1397, 890, 1577, 954]), 'b509p': (13, [961, 1003, 1141, 1066]),
        'b104p': (13, [1179, 1003, 1359, 1066]), 'c403h': (13, [1397, 1003, 1577, 1066]),
        'b519p': (20, [80, 1003, 173, 1059]), 'a405p': (20, [197, 1003, 290, 1059]),
        'a109p': (20, [314, 1003, 407, 1059]), 'b531p': (20, [431, 1003, 524, 1059]),
    }
    means = {}
    for k, (p, box) in colors.items():
        img = render(p, box, dpi=200)
        w, h = img.size
        inner = img.crop((int(w * .1), int(h * .15), int(w * .9), int(h * .85)))
        r, g, b = (round(v) for v in ImageStat.Stat(inner).mean)
        means[k] = f'#{r:02x}{g:02x}{b:02x}'
        out('colors', k, img, log)

    panels = {
        'dc1000a': (11, [85, 281, 192, 1033]), 'dl300': (11, [236, 590, 342, 1036]),
        'dc1000c': (11, [464, 280, 573, 1034]), 'dl320': (11, [617, 590, 713, 1036]),
        'dc2000a': (11, [936, 281, 1042, 1034]), 'dl400': (11, [1088, 790, 1163, 1036]),
        'dc2000b': (11, [1298, 281, 1414, 1034]), 'dl450': (11, [1455, 790, 1523, 1036]),
        'db20': (11, [237, 305, 294, 362]), 'db10': (11, [237, 392, 294, 449]),
        'dc5000a': (12, [84, 281, 232, 1034]), 'dl500a': (12, [260, 578, 406, 1036]),
        'dc9000a': (12, [479, 281, 584, 1034]), 'dl300b': (12, [627, 784, 704, 1036]),
        'dc1200a': (12, [968, 296, 1166, 416]), 'dc4200a': (12, [961, 479, 1173, 588]),
        'dc1200b': (12, [1264, 328, 1597, 385]),
        'db60': (12, [260, 303, 318, 362]), 'db31': (12, [618, 392, 725, 449]),
        'displays-hall': (12, [945, 734, 1604, 825]),
        'displays-lcd': (12, [945, 924, 1589, 1037]),
        'dl100a': (21, [1125, 788, 1198, 1052]), 'dl100a-double': (21, [1244, 788, 1369, 1052]),
        'dc1000a-freight': (21, [1446, 281, 1560, 1054]),
        'db10-db11-db20-freight': (21, [1122, 572, 1372, 642]),
        'displays-freight': (21, [1122, 328, 1372, 432]),
    }
    for k, (p, box) in panels.items():
        out('panels', k, render(p, box, dpi=300), log)

    drawings = {
        'k600-mr-rear': (15, [75, 180, 700, 720]),
        'k600-mr-side': (15, [1020, 180, 1520, 720]),
        'k600l-mrl': (16, [90, 230, 790, 1085]),
        'k600g-mr': (17, [150, 170, 640, 720]),
        'k600g-mrl': (17, [1010, 170, 1530, 720]),
        'h700-mr-2-1': (22, [130, 190, 640, 800]),
        'h700-mr-4-1': (22, [950, 190, 1540, 840]),
        'h700-car-2-1': (23, [100, 190, 680, 860]),
        'h700-car-4-1': (23, [975, 200, 1540, 860]),
        'h700-mrl-2-1': (24, [100, 210, 700, 860]),
        'h700-mrl-4-1': (24, [990, 210, 1580, 860]),
    }
    for k, (p, box) in drawings.items():
        img = render(p, box, dpi=200).convert('L')
        path = os.path.join(OUT, 'drawings', k + '.png')
        img.save(path, optimize=True)
        log.append(f'drawings/{k}.png {img.size[0]}x{img.size[1]} {os.path.getsize(path) // 1024}KB')

    print('\n'.join(log))
    print('colour means:', means)


if __name__ == '__main__':
    main()
