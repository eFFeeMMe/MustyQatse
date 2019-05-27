"""Defines a few primitives."""

import itertools

from math import sqrt, hypot, sin, cos, pi, atan2

def minmax(data):
    """returns (min(data), max(data)) but faster if comparisons are slow"""
    it = iter(data)
    try:
        lo = hi = next(it)
    except StopIteration:
        raise ValueError('minmax() arg is an empty sequence')
    for x in it:
        if x < lo:
            lo = x
        if x > hi:
            hi = x
    return lo, hi

def minmax_wat(data): #waht??
    return min(data), max(data)

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
    if d < 0.:
        d = 0.
    elif d > 1.:
        d = 1.
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



class Circle(object):
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
            return ((self.x - x) / distance * penetration,
                    (self.y - y) / distance * penetration)
        return None, None
    
    def get_aabb(self):
        return self.x - self.r, self.y - self.r, self.r * 2., self.r * 2.

class Capsule(object):
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
            return ((Px - x) / distance * penetration,
                    (Py - y) / distance * penetration)
        return None, None
    
    def get_aabb(self):
        return (min(self.x0, self.x1) - self.r,
                min(self.y0, self.y1) - self.r,
                abs(self.x1 - self.x0) + self.r * 2.,
                abs(self.y1 - self.y0) + self.r * 2.)

class Polygon(object):
    def __init__(self, *points):
        self.points = points
        self.edges = [(points[i][0], points[i][1],
            points[i+1][0], points[i+1][1]) for i in range(-1, len(points)-1)]
        self.aabb = self.get_aabb()
    
    def hit(self, x, y):
        """en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm"""
        collision = False
        for Ax, Ay, Bx, By in self.edges:
            if Ay == By: #horizontal edge, doesn't matter because the
                continue #test ray is also horizontal.
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
                return ((Px - x) / distance * penetration,
                        (Py - y) / distance * penetration)
        
        if self.hit(x, y):
            return x, y
        
        return None, None
    
    def get_aabb(self):
        x0, x1 = minmax(p[0] for p in self.points)
        y0, y1 = minmax(p[1] for p in self.points)
        return x0, y0, x1 - x0, y1 - y0

class Rectangle(Polygon):
    def __init__(self, x, y, w, h):
        Polygon.__init__(self, (x, y), (x, y+h), (x+w, y+h), (x+w, y))

class Arc(object):
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
        
        #We sanitize angle values, but take into account their
        #"before-sanitation order" to preserve the expected swept area.
        #This procedure will also highlight whether degree zero is swept by
        #the arc, making it problematic.
        #TODO check if this works, it looks suspicious
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
        
        #Problems arise when the arc sweeps degree 0.
        #We make a special case for that.
        def normal(x, y):
            a = atan2(y - self.y, x - self.x)
            return self.angle0 < a < self.angle1
        def special(x, y):
            a = atan2(y - self.y, x - self.x)
            return a < self.angle0 or a > self.angle1
            
        self.angular_condition = special if self._special else normal
        
        self.aabb = self.get_aabb()
    
    def hit(self, x, y):
        if self.r0 ** 2 < (x - self.x)**2 + (y - self.y)**2 < self.r1 ** 2:
            if self.angular_condition(x, y):
                return True
        else:
            return False
    
    def hit_circle(self, x, y, r):
        if self.angular_condition(x, y):
            #Curved borders
            square_distance = (x - self.x) ** 2 +  (y - self.y) ** 2
            if (self.r0 - r) ** 2 < square_distance < (self.r1 + r) ** 2:
                distance = sqrt(square_distance)
                if distance > (self.r0 + self.r1) / 2.: #Outer border
                    penetration = self.r1 + r - distance
                else: #Inner border
                    penetration = self.r0 - r - distance
                return ((self.x - x) / distance * penetration,
                        (self.y - y) / distance * penetration)
        else:
            #Sides
            pass
        
        return None, None
    
    def get_aabb(self):
        """Returns x, y, w, h. CRAPPY, doesn't always work"""
        Ax = self.x + cos(self.angle0) * self.r0
        Ay = self.y + sin(self.angle0) * self.r0
        Bx = self.x + cos(self.angle0) * self.r1
        By = self.y + sin(self.angle0) * self.r1
        Cx = self.x + cos(self.angle1) * self.r1
        Cy = self.y + sin(self.angle1) * self.r1
        Dx = self.x + cos(self.angle1) * self.r0
        Dy = self.y + sin(self.angle1) * self.r0
        #Middle of the arc
        Ex = self.x + cos((self.angle0 + self.angle1) / 2.) * self.r1
        Ey = self.y + sin((self.angle0 + self.angle1) / 2.) * self.r1
        
        top = min(Ay, By, Cy, Dy, Ey)
        bottom = max(Ay, By, Cy, Dy, Ey)
        left = min(Ax, Bx, Cx, Dx, Ex)
        right = max(Ax, Bx, Cx, Dx, Ex)
        
        return left, top, right - left, bottom - top