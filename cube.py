import math
import svgwrite

SIDE = 100
# Isometric axes: 30° from horizontal
ANG = math.radians(30)
IX = (math.cos(ANG), -math.sin(ANG))  # x-axis projects right and up
IY = (-math.cos(ANG), -math.sin(ANG))  # y-axis projects left and up
IZ = (0, -1)  # z-axis projects straight up


def iso(x, y, z):
    """Project (x, y, z) into 2D isometric coordinates."""
    px = x * IX[0] + y * IY[0] + z * IZ[0]
    py = x * IX[1] + y * IY[1] + z * IZ[1]
    return (px, py)


def cube_edges(s):
    """Return the 9 visible edges of an isometric cube as (start, end) pairs."""
    v = {
        "fbl": iso(0, 0, 0),
        "fbr": iso(s, 0, 0),
        "bbl": iso(0, s, 0),
        "ftl": iso(0, 0, s),
        "ftr": iso(s, 0, s),
        "btl": iso(0, s, s),
        "btr": iso(s, s, s),
    }
    return [
        # Hexagon outline
        (v["btr"], v["ftr"]),
        (v["ftr"], v["fbr"]),
        (v["fbr"], v["fbl"]),
        (v["fbl"], v["bbl"]),
        (v["bbl"], v["btl"]),
        (v["btl"], v["btr"]),
        # 3 internal edges from center
        (v["ftl"], v["fbl"]),
        (v["ftl"], v["ftr"]),
        (v["ftl"], v["btl"]),
    ]


def l_bars(s):
    """The L as two overlapping bar polygons — their overlap is the connector box.

    A single polygon self-intersects in isometric 2D, so we split into:
    - Vertical bar: top face → down the left face
    - Horizontal bar: across the left face → right face
    Start cap parallel to top-right edge (y-axis), end cap vertical (z-axis).
    """
    hw = s / 6  # half-width → total width = s/3

    vertical = [
        iso(s / 2, s / 2 + hw, s),  # start outer (top face)
        iso(0, s / 2 + hw, s),  # outer at top-left edge
        iso(0, s / 2 + hw, s / 2 - hw),  # outer at bottom of vertical bar
        iso(0, s / 2 - hw, s / 2 - hw),  # inner at bottom of vertical bar
        iso(0, s / 2 - hw, s),  # inner at top-left edge
        iso(s / 2, s / 2 - hw, s),  # start inner (top face)
    ]

    horizontal = [
        iso(0, s / 2 + hw, s / 2 + hw),  # left outer (overlaps vertical bar)
        iso(0, 0, s / 2 + hw),  # outer at left-right boundary
        iso(s / 2, 0, s / 2 + hw),  # end outer (right face)
        iso(s / 2, 0, s / 2 - hw),  # end inner (right face)
        iso(0, 0, s / 2 - hw),  # inner at left-right boundary
        iso(0, s / 2 + hw, s / 2 - hw),  # left inner (overlaps vertical bar)
    ]

    return vertical, horizontal


def main():
    w, h = 300, 300
    dwg = svgwrite.Drawing("cube.svg", size=(w, h))

    edges = cube_edges(SIDE)
    vert_bar, horiz_bar = l_bars(SIDE)

    all_pts = [p for edge in edges for p in edge] + vert_bar + horiz_bar
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    cx = w / 2 - (min(xs) + max(xs)) / 2
    cy = h / 2 - (min(ys) + max(ys)) / 2

    # L shape — two overlapping bars (overlap = connector box at the corner)
    for bar in (vert_bar, horiz_bar):
        shifted = [(x + cx, y + cy) for x, y in bar]
        dwg.add(dwg.polygon(shifted, fill="black", stroke="none"))

    # Cube wireframe on top
    for start, end in edges:
        dwg.add(
            dwg.line(
                start=(start[0] + cx, start[1] + cy),
                end=(end[0] + cx, end[1] + cy),
                stroke="black",
                stroke_width=6,
                stroke_linecap="round",
            )
        )

    dwg.save()
    print(f"Saved cube.svg ({w}x{h})")


if __name__ == "__main__":
    main()
