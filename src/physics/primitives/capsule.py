from math import sqrt

from src.physics.geometry import point_on_segment


class Capsule:
    def __init__(self, x0, y0, x1, y1, r):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.r = r
        self.aabb = self.get_aabb()

    def hit(self, x, y):
        Px, Py = point_on_segment(x, y, self.x0, self.y0, self.x1, self.y1)
        if (x - Px) ** 2 + (y - Py) ** 2 < self.r ** 2:
            return True
        return False

    def hit_circle(self, x, y, r):
        Px, Py = point_on_segment(x, y, self.x0, self.y0, self.x1, self.y1)
        square_distance = (x - Px) ** 2 + (y - Py) ** 2
        if square_distance < (self.r + r) ** 2:
            distance = sqrt(square_distance)
            penetration = self.r + r - distance
            return (
                (Px - x) / distance * penetration,
                (Py - y) / distance * penetration,
            )
        return None, None

    def get_aabb(self):
        return (
            min(self.x0, self.x1) - self.r,
            min(self.y0, self.y1) - self.r,
            abs(self.x1 - self.x0) + self.r * 2.0,
            abs(self.y1 - self.y0) + self.r * 2.0,
        )
