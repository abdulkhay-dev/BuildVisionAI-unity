"""Contact sheet of the look-dev views: Blender -b --python tools/interior/sheet.py -- <out.png> <img> …  (3 per row, half size)."""
import sys

import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
out, paths = argv[0], argv[1:]
tiles = []
for p in paths:
    im = bpy.data.images.load(p)
    w, h = im.size
    a = np.array(im.pixels[:], np.float32).reshape(h, w, 4)[::2, ::2]
    tiles.append(a)
th, tw = tiles[0].shape[:2]
cols, gap = 3, 8
rows = (len(tiles) + cols - 1) // cols
H, W = rows * th + (rows - 1) * gap, cols * tw + (cols - 1) * gap
sheet = np.ones((H, W, 4), np.float32)
for i, t in enumerate(tiles):
    r, c = divmod(i, cols)
    y0 = H - (r + 1) * th - r * gap
    x0 = c * (tw + gap)
    sheet[y0:y0 + th, x0:x0 + tw] = t
img = bpy.data.images.new("sheet", W, H)
img.pixels.foreach_set(sheet.ravel())
img.filepath_raw = out
img.file_format = "PNG"
img.save()
print("sheet", out)
