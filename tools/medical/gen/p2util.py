"""Small helpers of the physio-2 generators (outline paths, vectors)."""
import math
def rr(x0, y0, x1, y1, r):
    """Rounded rectangle as an SVG subpath (absolute)."""
    return (f"M {x0 + r} {y0} L {x1 - r} {y0} Q {x1} {y0} {x1} {y0 + r} L {x1} {y1 - r} Q {x1} {y1} {x1 - r} {y1} "
            f"L {x0 + r} {y1} Q {x0} {y1} {x0} {y1 - r} L {x0} {y0 + r} Q {x0} {y0} {x0 + r} {y0} Z")
def add(a, b): return [a[i] + b[i] for i in range(3)]
def sub(a, b): return [a[i] - b[i] for i in range(3)]
def mul(a, s): return [a[i] * s for i in range(3)]
def lerp(a, b, s): return [a[i] + (b[i] - a[i]) * s for i in range(3)]
def norm(a):
    l = math.sqrt(sum(x * x for x in a)); return [x / l for x in a]
