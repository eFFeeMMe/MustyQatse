from math import sin, cos, pi, atan2, sqrt, hypot


class Arc:
    def __init__(self, x, y, r0, r1, angle0, angle1):
        """Arc centered in (x, y), sweeps ccw angle0 to angle1,
        r0 internal radius, r1 external radius.
        
        """
        self.x = x
        self.y = y
        if r0 > r1:
            r0, r1 = r1, r0
        self.r0 = r0
        self.r1 = r1

        # We sanitize angle values, but take into account their
        # "before-sanitation order" to preserve the expected swept area.
        # This procedure will also highlight whether degree zero is swept by
        # the arc, making it problematic.
        # TODO check if this works, it looks suspicious
        saneAngle0 = angle0 - (pi * 2) * int(angle0 / (pi * 2))
        saneAngle1 = angle1 - (pi * 2) * int(angle1 / (pi * 2))

        if angle0 < angle1:
            if saneAngle0 < saneAngle1:
                self._special = False
                self.angle0 = saneAngle0
                self.angle1 = saneAngle1
            else:
                self._special = True
                self.angle0 = saneAngle1
                self.angle1 = saneAngle0
        else:
            if saneAngle0 < saneAngle1:
                self._special = True
                self.angle0 = saneAngle0
                self.angle1 = saneAngle1
            else:
                self._special = True
                self.angle0 = saneAngle1
                self.angle1 = saneAngle0

        # Problems arise when the arc sweeps degree 0.
        # We make a special case for that.
        def normal(x, y):
            a = atan2(y - self.y, x - self.x)
            return self.angle0 < a < self.angle1

        def special(x, y):
            a = atan2(y - self.y, x - self.x)
            return a < self.angle0 or a > self.angle1

        self.angular_condition = special if self._special else normal

        self.aabb = self.get_aabb()

    def hit(self, x, y):
        if self.r0 ** 2 < (x - self.x) ** 2 + (y - self.y) ** 2 < self.r1 ** 2:
            if self.angular_condition(x, y):
                return True
        else:
            return False

    def hit_circle(self, x, y, r):
        if self.angular_condition(x, y):
            # Curved borders
            square_distance = (x - self.x) ** 2 + (y - self.y) ** 2
            if (self.r0 - r) ** 2 < square_distance < (self.r1 + r) ** 2:
                distance = sqrt(square_distance)
                if distance > (self.r0 + self.r1) / 2.0:  # Outer border
                    penetration = self.r1 + r - distance
                else:  # Inner border
                    penetration = self.r0 - r - distance
                return (
                    (self.x - x) / distance * penetration,
                    (self.y - y) / distance * penetration,
                )
        else:
            # Sides
            pass

        return None, None

    def get_aabb(self):
        """Samples a few points, returns their AABB. Crappy at best."""
        Ax = self.x + cos(self.angle0) * self.r0
        Ay = self.y + sin(self.angle0) * self.r0
        Bx = self.x + cos(self.angle0) * self.r1
        By = self.y + sin(self.angle0) * self.r1
        Cx = self.x + cos(self.angle1) * self.r1
        Cy = self.y + sin(self.angle1) * self.r1
        Dx = self.x + cos(self.angle1) * self.r0
        Dy = self.y + sin(self.angle1) * self.r0
        # Middle of the arc
        Ex = self.x + cos((self.angle0 + self.angle1) / 2.0) * self.r1
        Ey = self.y + sin((self.angle0 + self.angle1) / 2.0) * self.r1

        top = min(Ay, By, Cy, Dy, Ey)
        bottom = max(Ay, By, Cy, Dy, Ey)
        left = min(Ax, Bx, Cx, Dx, Ex)
        right = max(Ax, Bx, Cx, Dx, Ex)

        return left, top, right - left, bottom - top
