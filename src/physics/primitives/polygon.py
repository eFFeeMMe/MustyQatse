from math import sqrt

from src.physics.geometry import point_on_segment


class Polygon:
    def __init__(self, *points):
        self.points = points
        self.edges = [
            (points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
            for i in range(-1, len(points) - 1)
        ]
        self.aabb = self.get_aabb()

    def hit(self, x, y):
        """en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm"""
        collision = False
        for Ax, Ay, Bx, By in self.edges:
            if Ay == By:
                # horizontal edge, doesn't matter: the test ray is also horizontal
                continue
            else:
                Cx = ((y - Ay) * (Bx - Ax)) / (By - Ay) + Ax
                if Cx > x and (Ax <= Cx <= Bx or Bx <= Cx <= Ax):
                    collision = not collision

        return collision

    def hit_circle(self, x, y, r):
        for Ax, Ay, Bx, By in self.edges:
            Px, Py = point_on_segment(x, y, Ax, Ay, Bx, By)
            square_distance = (x - Px) ** 2 + (y - Py) ** 2
            if square_distance < r ** 2:
                distance = sqrt(square_distance)
                penetration = r - distance
                return (
                    (Px - x) / distance * penetration,
                    (Py - y) / distance * penetration,
                )

        if self.hit(x, y):
            return x, y

        return None, None

    def get_aabb(self):
        x0 = min(p[0] for p in self.points)
        x1 = max(p[0] for p in self.points)
        y0 = min(p[1] for p in self.points)
        y1 = max(p[1] for p in self.points)
        return x0, y0, x1 - x0, y1 - y0
