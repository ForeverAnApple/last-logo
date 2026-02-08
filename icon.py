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


def cube_verts(s):
    """Return named vertices of the isometric cube."""
    return {
        "fbl": iso(0, 0, 0),
        "fbr": iso(s, 0, 0),
        "bbl": iso(0, s, 0),
        "ftl": iso(0, 0, s),
        "ftr": iso(s, 0, s),
        "btl": iso(0, s, s),
        "btr": iso(s, s, s),
    }


def cube_hexagon(v):
    """The 6 outer vertices forming the cube silhouette (a hexagon)."""
    return [v["btr"], v["ftr"], v["fbr"], v["fbl"], v["bbl"], v["btl"]]


def cube_edges(v):
    """Return the 9 visible edges of an isometric cube as (start, end) pairs."""
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


def l_shape(s):
    """Build the L as 3 face polygons, one per visible cube face.

    The L runs the full length of the cube on each face — edge to edge
    on both the top and right faces, connected by the L-shaped elbow
    on the left face.
    """
    hw = s / 6  # half-width → total bar width = s/3

    # ── Top face (z=s plane) ─────────────────────────────────────────
    top = [
        iso(s, s / 2 + hw, s),
        iso(0, s / 2 + hw, s),
        iso(0, s / 2 - hw, s),
        iso(s, s / 2 - hw, s),
    ]

    # ── Left face (x=0 plane) — the L-shaped elbow ──────────────────
    left = [
        iso(0, s / 2 + hw, s),  # top outer
        iso(0, s / 2 - hw, s),  # top inner
        iso(0, s / 2 - hw, s / 2 + hw),  # inner corner of L
        iso(0, 0, s / 2 + hw),  # bottom-right outer
        iso(0, 0, s / 2 - hw),  # bottom-right inner
        iso(0, s / 2 + hw, s / 2 - hw),  # bottom-left outer
    ]

    # ── Right face (y=0 plane) ───────────────────────────────────────
    right = [
        iso(0, 0, s / 2 + hw),
        iso(s, 0, s / 2 + hw),
        iso(s, 0, s / 2 - hw),
        iso(0, 0, s / 2 - hw),
    ]

    return [top, left, right]


def draw_icon(filename, fg="black", bg="white"):
    v = cube_verts(SIDE)
    hexagon = cube_hexagon(v)
    edges = cube_edges(v)
    faces = l_shape(SIDE)

    pad = 6 / 2  # half of wireframe stroke_width
    xs = [p[0] for p in hexagon]
    ys = [p[1] for p in hexagon]
    cx = -min(xs) + pad
    cy = -min(ys) + pad
    w = max(xs) - min(xs) + 6
    h = max(ys) - min(ys) + 6

    dwg = svgwrite.Drawing(filename, size=(w, h))

    def shift(pt):
        return (pt[0] + cx, pt[1] + cy)

    # Filled cube background
    dwg.add(dwg.polygon([shift(p) for p in hexagon], fill=bg, stroke="none"))

    # Colored regions
    s = SIDE
    hw = s / 6
    color = "#5A9EA3"

    top_right = [
        iso(0, 0, s),
        iso(s, 0, s),
        iso(s, s / 2 - hw, s),
        iso(0, s / 2 - hw, s),
    ]
    left_square = [
        iso(0, 0, s),
        iso(0, s / 2 - hw, s),
        iso(0, s / 2 - hw, s / 2 + hw),
        iso(0, 0, s / 2 + hw),
    ]
    right_top = [
        iso(0, 0, s),
        iso(s, 0, s),
        iso(s, 0, s / 2 + hw),
        iso(0, 0, s / 2 + hw),
    ]

    for region in [top_right, left_square, right_top]:
        dwg.add(dwg.polygon([shift(p) for p in region], fill=color, stroke="none"))

    # L shape faces
    for face in faces:
        dwg.add(dwg.polygon([shift(p) for p in face], fill=fg, stroke="none"))

    # Wireframe
    for start, end in edges:
        dwg.add(
            dwg.line(
                start=shift(start),
                end=shift(end),
                stroke=fg,
                stroke_width=6,
                stroke_linecap="round",
            )
        )

    dwg.save()
    print(f"Saved {filename} ({w:.0f}x{h:.0f})")


def main():
    draw_icon("icon-light.svg", fg="black", bg="white")
    draw_icon("icon-dark.svg", fg="white", bg="black")


if __name__ == "__main__":
    main()
