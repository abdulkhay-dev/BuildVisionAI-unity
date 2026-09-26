"""The height model of the plot: natural ground, the stream (pools between cascades) carved into it,
the house pad and the path beds. Every other module asks `Site.height(x, y)` and `Site.stream_at(x, y)`."""
import math
import random

from . import layout as L
from .util import Polyline, ValueNoise, lerp, smoothstep


class Pool:
    def __init__(self, s0, s1, level):
        self.s0, self.s1, self.level = s0, s1, level


class Site:
    def __init__(self):
        self.noise = ValueNoise(L.SEED)
        self.wnoise = ValueNoise(L.SEED + 1)
        self.stream = Polyline(L.STREAM, step=0.08)
        self.paths = {p["id"]: (Polyline(p["points"], step=0.1), p["width"]) for p in L.PATHS}
        h = L.HOUSE
        self.house_pad = self.natural((h["x0"] + h["x1"]) / 2, (h["y0"] + h["y1"]) / 2)
        self._build_pools()

    # ------------------------------------------------------------ natural ground

    def natural(self, x, y):
        """Ground without the stream: a slope to the north, soft undulation, hills beyond the plot."""
        h = L.SLOPE * (y - L.GROUND_Y0)
        h += 0.32 * self.noise.fbm(x / 16.0, y / 16.0, 3) + 0.06 * self.noise.fbm(x / 3.5, y / 3.5, 2)
        # a rise behind the plot and on its sides (bounded: the far land adds the big hills)
        far = min(max(0.0, y - 44.0), 60.0)
        h += 0.0009 * far * far + 7.0 * smoothstep(60.0, 260.0, y) * (0.6 + 0.4 * self.noise.fbm(x / 60, y / 60, 3))
        side = min(max(0.0, abs(x - 2.0) - 30.0), 60.0)
        h += 0.0012 * side * side
        return h

    def ground(self, x, y):
        """Natural ground with the house pad levelled."""
        h = self.natural(x, y)
        hs = L.HOUSE
        dx = max(hs["x0"] - 1.5 - x, 0.0, x - (hs["deck"][2] + 1.0))
        dy = max(hs["y0"] - 1.5 - y, 0.0, y - (hs["y1"] + 1.5))
        t = smoothstep(0.0, 4.0, math.hypot(dx, dy))
        return lerp(self.house_pad, h, t)

    # ------------------------------------------------------------ stream

    def _cascade_s(self, y):
        best, s_best = 1e9, 0.0
        for p, s in zip(self.stream.pts, self.stream.s):
            if abs(p.y - y) < best:
                best, s_best = abs(p.y - y), s
        return s_best

    def _build_pools(self):
        cuts = sorted(self._cascade_s(y) for y in L.CASCADES_Y)
        bounds = [0.0] + cuts + [self.stream.length]
        self.pools = []
        for s0, s1 in zip(bounds[:-1], bounds[1:]):
            p, _ = self.stream.at(s1)
            # the pool is level at the height of its downstream lip, a little below the ground there
            self.pools.append(Pool(s0, s1, self.ground(p.x, p.y) - 0.2))
        self.cascades = []
        rnd = random.Random(L.SEED + 5)
        for i in range(len(self.pools) - 1):
            up, down = self.pools[i], self.pools[i + 1]
            # water pours over the lip in 2–3 tongues between stones: (lateral position -1..1, half width -1..1)
            n = rnd.choice((2, 3, 3))
            slots = sorted(rnd.uniform(-0.55, 0.55) for _ in range(n))
            tongues = []
            for u in slots:
                if all(abs(u - t[0]) > 0.34 for t in tongues):
                    tongues.append((u, rnd.uniform(0.1, 0.19)))
            self.cascades.append({"s": up.s1, "top": up.level, "bottom": down.level, "tongues": tongues})

    def pool_at(self, s):
        for p in self.pools:
            if s <= p.s1:
                return p
        return self.pools[-1]

    def half_width(self, s):
        w = L.STREAM_WIDTH * (1.0 + 0.32 * self.wnoise.fbm(s / 7.0, 0.5, 2))
        # plunge pools below each cascade are wider
        for c in self.cascades:
            k = s - c["s"]
            if 0.0 < k < 3.5:
                w *= 1.0 + 0.2 * math.sin(math.pi * k / 3.5)
        return 0.5 * w

    def stream_at(self, x, y):
        """(distance to the centre line, arclength, half width, water level)."""
        d, s, _, _ = self.stream.nearest(x, y)
        return d, s, self.half_width(s), self.pool_at(s).level

    # ------------------------------------------------------------ final height

    def height(self, x, y):
        nat = self.ground(x, y)
        d, s, hw, w = self.stream_at(x, y)
        if d < hw:
            t = d / hw
            bed = w - L.STREAM_DEPTH * (1.0 - t * t) - 0.03 + 0.05 * self.noise.noise(x * 1.7, y * 1.7)
            return min(nat, bed)
        cut = w + 0.04 + (d - hw) * 0.55            # banks never steeper than ~29°
        floor = w + 0.06 - max(0.0, d - hw - 1.2) * 0.35  # levee where the ground would dip under the water
        return min(max(nat, floor), cut)

    def path_distance(self, x, y):
        """Distance to the nearest path centre line minus its half width (<0 = on the path)."""
        best = 1e9
        for poly, width in self.paths.values():
            d, _, _, _ = poly.nearest(x, y)
            best = min(best, d - width / 2)
        return best

    def in_house(self, x, y, margin=0.0):
        h = L.HOUSE
        return (h["x0"] - margin <= x <= h["deck"][2] + margin) and (h["y0"] - margin <= y <= h["y1"] + margin)

    def in_plot(self, x, y, margin=0.0):
        x0, y0, x1, y1 = L.PLOT
        return x0 + margin <= x <= x1 - margin and y0 + margin <= y <= y1 - margin
