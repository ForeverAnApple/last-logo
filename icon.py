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


def main():
    v = cube_verts(SIDE)
    hexagon = cube_hexagon(v)
    edges = cube_edges(v)
    faces = l_shape(SIDE)

    # Compute tight bounding box around hexagon + stroke padding
    stroke_w = 18
    pad = stroke_w / 2
    xs = [p[0] for p in hexagon]
    ys = [p[1] for p in hexagon]
    cx = -min(xs) + pad
    cy = -min(ys) + pad
    w = max(xs) - min(xs) + stroke_w
    h = max(ys) - min(ys) + stroke_w

    dwg = svgwrite.Drawing("icon.svg", size=(w, h))

    # White filled cube silhouette with white outline
    shifted_hex = [(x + cx, y + cy) for x, y in hexagon]
    dwg.add(
        dwg.polygon(
            shifted_hex,
            fill="white",
            stroke="white",
            stroke_width=18,
            stroke_linejoin="round",
        )
    )

    # Colored regions in the areas "cut out" by the L shape
    s = SIDE
    hw = s / 6
    color = "#5A9EA3"

    # 1. Top face — rectangle to the right of the L bar (low-y strip)
    top_right = [
        iso(0, 0, s),
        iso(s, 0, s),
        iso(s, s / 2 - hw, s),
        iso(0, s / 2 - hw, s),
    ]

    # 2. Left face — top-right square (the gap in the L elbow)
    left_square = [
        iso(0, 0, s),
        iso(0, s / 2 - hw, s),
        iso(0, s / 2 - hw, s / 2 + hw),
        iso(0, 0, s / 2 + hw),
    ]

    # 3. Right face — top rectangle bar above the L
    right_top = [
        iso(0, 0, s),
        iso(s, 0, s),
        iso(s, 0, s / 2 + hw),
        iso(0, 0, s / 2 + hw),
    ]

    for region in [top_right, left_square, right_top]:
        shifted = [(x + cx, y + cy) for x, y in region]
        dwg.add(dwg.polygon(shifted, fill=color, stroke="none"))

    # L shape — one polygon per face
    for face in faces:
        shifted = [(x + cx, y + cy) for x, y in face]
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
    print(f"Saved icon.svg ({w}x{h})")


if __name__ == "__main__":
    main()
