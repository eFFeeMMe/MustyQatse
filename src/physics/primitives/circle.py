from math import sqrt


class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.aabb = self.get_aabb()

    def hit(self, x, y):
        if (x - self.x) ** 2 + (y - self.y) ** 2 < self.r ** 2:
            return True
        return False

    def hit_circle(self, x, y, r):
        square_distance = (x - self.x) ** 2 + (y - self.y) ** 2
        if square_distance < (self.r + r) ** 2:
            distance = sqrt(square_distance)
            penetration = self.r + r - distance
            return (
                (self.x - x) / distance * penetration,
                (self.y - y) / distance * penetration,
            )
        return None, None

    def get_aabb(self):
        return self.x - self.r, self.y - self.r, self.r * 2.0, self.r * 2.0
