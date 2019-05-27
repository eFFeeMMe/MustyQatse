from math import hypot


def point_on_line(Px, Py, Ax, Ay, Bx, By):
    """Point projection on a line."""
    ABx = Bx - Ax
    ABy = By - Ay
    d = ((Px - Ax) * ABx + (Py - Ay) * ABy) / (ABx ** 2 + ABy ** 2)
    return Ax + ABx * d, Ay + ABy * d


def point_on_segment(Px, Py, Ax, Ay, Bx, By):
    """Point projection on a segment."""
    ABx = Bx - Ax
    ABy = By - Ay
    d = ((Px - Ax) * ABx + (Py - Ay) * ABy) / (ABx ** 2 + ABy ** 2)
    if d < 0.0:
        d = 0.0
    elif d > 1.0:
        d = 1.0
    return Ax + ABx * d, Ay + ABy * d


def point_on_circle(Px, Py, Cx, Cy, Cr):
    """Point projection on a circle."""
    dx = Px - Cx
    dy = Py - Cy
    distance = hypot(dx, dy)
    return Cx + Cr / distance * dx, Cy + Cr / distance * dy


def trilateration(Ax, Ay, Bx, By, Cx, Cy):
    """Returns the circle which intersects A B and C"""
    raise NotImplementedError

