"""Computational geometry utilities."""

from __future__ import annotations

import math
from typing import List, Tuple

from .catalog import register_algorithm

Point = Tuple[float, float]


def _cross(o: Point, a: Point, b: Point) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


@register_algorithm(category="geometry")
def distance_point_point(p: Point, q: Point) -> float:
    """Euclidean distance between two points."""
    return math.hypot(p[0] - q[0], p[1] - q[1])


@register_algorithm(category="geometry")
def distance_point_line(point: Point, line_a: Point, line_b: Point) -> float:
    """Perpendicular distance from point to infinite line through line_a and line_b."""
    num = abs(
        (line_b[0] - line_a[0]) * (line_a[1] - point[1])
        - (line_a[0] - point[0]) * (line_b[1] - line_a[1])
    )
    den = distance_point_point(line_a, line_b)
    return 0.0 if den == 0 else num / den


@register_algorithm(category="geometry")
def cross_product(a: Point, b: Point) -> float:
    """2D cross product of vectors a and b."""
    return a[0] * b[1] - a[1] * b[0]


@register_algorithm(category="geometry")
def dot_product(a: Point, b: Point) -> float:
    """Dot product of vectors a and b."""
    return a[0] * b[0] + a[1] * b[1]


@register_algorithm(category="geometry")
def orientation(a: Point, b: Point, c: Point) -> int:
    """Orientation of triplet (a,b,c): -1 clockwise, 0 collinear, 1 counter-clockwise."""
    val = _cross(a, b, c)
    if abs(val) < 1e-12:
        return 0
    return 1 if val > 0 else -1


@register_algorithm(category="geometry")
def convex_hull(points: List[Point]) -> List[Point]:
    """Convex hull via Graham scan."""
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts
    lower: List[Point] = []
    for p in pts:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: List[Point] = []
    for p in reversed(pts):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


@register_algorithm(category="geometry")
def point_in_polygon(point: Point, polygon: List[Point]) -> bool:
    """Ray-casting test for point inside polygon (boundary inclusive)."""
    x, y = point
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-18) + xi
        ):
            inside = not inside
        j = i
    return inside


@register_algorithm(category="geometry")
def polygon_area(polygon: List[Point]) -> float:
    """Signed area of polygon (positive for CCW)."""
    n = len(polygon)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += polygon[i][0] * polygon[j][1]
        area -= polygon[j][0] * polygon[i][1]
    return area / 2.0


@register_algorithm(category="geometry")
def line_intersection(p1: Point, p2: Point, p3: Point, p4: Point) -> Point | None:
    """Intersection of lines (p1,p2) and (p3,p4), or None if parallel."""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-12:
        return None
    px = (
        (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
    ) / denom
    py = (
        (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
    ) / denom
    return (px, py)


@register_algorithm(category="geometry")
def segment_intersection(a1: Point, a2: Point, b1: Point, b2: Point) -> bool:
    """Return True if segments a1-a2 and b1-b2 intersect."""
    o1 = orientation(a1, a2, b1)
    o2 = orientation(a1, a2, b2)
    o3 = orientation(b1, b2, a1)
    o4 = orientation(b1, b2, a2)
    if o1 != o2 and o3 != o4:
        return True
    if o1 == 0 and _point_on_segment(b1, a1, a2):
        return True
    if o2 == 0 and _point_on_segment(b2, a1, a2):
        return True
    if o3 == 0 and _point_on_segment(a1, b1, b2):
        return True
    if o4 == 0 and _point_on_segment(a2, b1, b2):
        return True
    return False


def _point_on_segment(p: Point, a: Point, b: Point) -> bool:
    """Return True if p lies on segment ab."""
    return (
        min(a[0], b[0]) - 1e-12 <= p[0] <= max(a[0], b[0]) + 1e-12
        and min(a[1], b[1]) - 1e-12 <= p[1] <= max(a[1], b[1]) + 1e-12
        and orientation(a, b, p) == 0
    )


@register_algorithm(category="geometry")
def centroid_triangle(a: Point, b: Point, c: Point) -> Point:
    """Centroid of triangle abc."""
    return ((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3)


@register_algorithm(category="geometry")
def circumcircle(a: Point, b: Point, c: Point) -> Tuple[Point, float] | None:
    """Circumcenter and radius of triangle abc, or None if collinear."""
    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    if abs(d) < 1e-12:
        return None
    ux = (
        (a[0] ** 2 + a[1] ** 2) * (b[1] - c[1])
        + (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1])
        + (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])
    ) / d
    uy = (
        (a[0] ** 2 + a[1] ** 2) * (c[0] - b[0])
        + (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0])
        + (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])
    ) / d
    center = (ux, uy)
    return center, distance_point_point(center, a)


@register_algorithm(category="geometry")
def bounding_box(points: List[Point]) -> Tuple[Point, Point]:
    """Axis-aligned bounding box as (min_corner, max_corner)."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys)), (max(xs), max(ys))


@register_algorithm(category="geometry")
def point_in_circle(point: Point, center: Point, radius: float) -> bool:
    """Return True if point is inside or on circle."""
    return distance_point_point(point, center) <= radius + 1e-12


@register_algorithm(category="geometry")
def polar_angle(origin: Point, point: Point) -> float:
    """Angle from origin to point in radians (-pi, pi]."""
    return math.atan2(point[1] - origin[1], point[0] - origin[0])


@register_algorithm(category="geometry")
def perimeter_polygon(polygon: List[Point]) -> float:
    """Perimeter of closed polygon."""
    n = len(polygon)
    if n < 2:
        return 0.0
    total = 0.0
    for i in range(n):
        total += distance_point_point(polygon[i], polygon[(i + 1) % n])
    return total


@register_algorithm(category="geometry")
def shoelace_area(polygon: List[Point]) -> float:
    """Absolute area via shoelace formula."""
    return abs(polygon_area(polygon))


@register_algorithm(category="geometry")
def closest_pair_distance(points: List[Point]) -> float:
    """Brute-force closest pair distance."""
    n = len(points)
    if n < 2:
        return float("inf")
    best = float("inf")
    for i in range(n):
        for j in range(i + 1, n):
            d = distance_point_point(points[i], points[j])
            if d < best:
                best = d
    return best


@register_algorithm(category="geometry")
def reflect_point_line(point: Point, line_a: Point, line_b: Point) -> Point:
    """Reflect point across infinite line through line_a and line_b."""
    ax, ay = line_a
    bx, by = line_b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return point
    t = ((point[0] - ax) * dx + (point[1] - ay) * dy) / (dx * dx + dy * dy)
    proj = (ax + t * dx, ay + t * dy)
    return (2 * proj[0] - point[0], 2 * proj[1] - point[1])


@register_algorithm(category="geometry")
def rotate_point(point: Point, center: Point, angle_rad: float) -> Point:
    """Rotate point around center by angle_rad radians."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    px, py = point[0] - center[0], point[1] - center[1]
    return (
        center[0] + px * cos_a - py * sin_a,
        center[1] + px * sin_a + py * cos_a,
    )


@register_algorithm(category="geometry")
def translate_point(point: Point, dx: float, dy: float) -> Point:
    """Translate point by (dx, dy)."""
    return (point[0] + dx, point[1] + dy)


@register_algorithm(category="geometry")
def is_collinear(a: Point, b: Point, c: Point) -> bool:
    """Return True if points a, b, c are collinear."""
    return orientation(a, b, c) == 0


@register_algorithm(category="geometry")
def angle_between_vectors(a: Point, b: Point) -> float:
    """Angle between vectors a and b in radians [0, pi]."""
    dot = dot_product(a, b)
    mag = math.hypot(a[0], a[1]) * math.hypot(b[0], b[1])
    if mag == 0:
        return 0.0
    return math.acos(max(-1.0, min(1.0, dot / mag)))


@register_algorithm(category="geometry")
def triangle_area(a: Point, b: Point, c: Point) -> float:
    """Area of triangle abc."""
    return abs(_cross(a, b, c)) / 2.0


@register_algorithm(category="geometry")
def circle_circle_intersection(
    c1: Point, r1: float, c2: Point, r2: float
) -> List[Point]:
    """Intersection points of two circles (0, 1, or 2 points)."""
    d = distance_point_point(c1, c2)
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return []
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h_sq = r1 * r1 - a * a
    if h_sq < -1e-12:
        return []
    h = math.sqrt(max(0.0, h_sq))
    x2 = c1[0] + a * (c2[0] - c1[0]) / d
    y2 = c1[1] + a * (c2[1] - c1[1]) / d
    rx = -(c2[1] - c1[1]) * (h / d)
    ry = (c2[0] - c1[0]) * (h / d)
    p1 = (x2 + rx, y2 + ry)
    p2 = (x2 - rx, y2 - ry)
    if h < 1e-12:
        return [p1]
    return [p1, p2]
