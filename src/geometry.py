#!/usr/bin/env python
from pygame import Rect #used for primitives

from math import hypot, sin, cos, pi, atan2

def dot(Ax, Ay, Bx, By):
    """Dot product of two vectors in 2d"""
    return Ax * Bx + Ay * By

def getDirection(Ax, Ay, Bx, By):
    """Direction from A to B in radians"""
    return atan2(By - Ay, Bx - Ax)

def pointOnLine(Px, Py, Ax, Ay, Bx, By):
    """Point projection on a line. Readable version. Pretty Straightforward."""
    Vx = Px - Ax
    Vy = Py - Ay
    Cx = Bx - Ax
    Cy = By - Ay
    d = dot(Vx, Vy, Cx, Cy) / (Cx ** 2 + Cy ** 2)
    return Ax + Cx * d, Ay + Cy * d

def pointOnSegment(Px, Py, Ax, Ay, Bx, By):
    """Point projection on a line. Readable version. Pretty Straightforward."""
    Vx = Px - Ax
    Vy = Py - Ay
    Cx = Bx - Ax
    Cy = By - Ay
    d = dot(Vx, Vy, Cx, Cy) / (Cx ** 2 + Cy ** 2)
    d = max(0, min(1, d))
    return Ax + Cx * d, Ay + Cy * d

def pointOnCircle(Px, Py, Cx, Cy, Cr):
    dx = Px - Cx
    dy = Py - Cy
    distance = hypot(dx, dy)
    return Cx + Cr / distance * dx, Cy + Cr / distance * dy

def circleFromRect(rect):
    yb = rect.top
    a, b = rect.size
    y = yb + (4 * a**2 + b**2) / (8 * a)
    r = (4 * a**2 + b**2) / (8 * a)
    return rect.centerx, y, r

def trilateration(Ax, Ay, Bx, By, Cx, Cy):
    """Returns the circle which intersects A B and C"""
    raise NotImplementedError

"""Primitives

"""

class Circle(object):
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.rect = Rect(x - radius, y - radius, radius * 2.0, radius * 2.0)
    
    def collidePoint(self, x, y):
        if (x - self.x)**2 + (y - self.y)**2 <= self.radius**2:
            return True
        return False
    
    def collideCircle(self, x, y, radius):
        if (x - self.x)**2 + (y - self.y)**2 <= (self.radius + radius)**2:
            return True, self.x, self.y
        return False, self.x, self.y

class Capsule(object):
    def __init__(self, x0, y0, x1, y1, radius):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.radius = radius
        self.rect = Rect(min(x0, x1) - self.radius, min(y0, y1) - self.radius,
                         abs(x1 - x0) + self.radius*2, abs(y1 - y0) + self.radius*2)
    
    def collidePoint(self, x, y):
        px, py = pointOnSegment(x, y, self.x0, self.y0, self.x1, self.y1)
        if hypot(x - px, y - py) <= self.radius:
            return True
        return False
    
    def collideCircle(self, x, y, radius):
        px, py = pointOnSegment(x, y, self.x0, self.y0, self.x1, self.y1)
        if hypot(x - px, y - py) <= self.radius + radius:
            return True, px, py
        return False, px, py

class Rectangle(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = Rect(x, y, w, h)
    
    def collidePoint(self, x, y):
        if self.x <= x < self.x + self.w and self.y <= y < self.y + self.h:
            return True
    
    def collideCircle(self, x, y, radius):
        ax = self.x - radius < x < self.x + self.w + radius
        ay = self.y < y < self.y + self.h
        bx = self.x < x < self.x + self.w
        by = self.y - radius < y < self.y + self.h + radius
        if bx and ay:
            return True, self.x + self.w / 2.0, self.y + self.h / 2.0
        elif ax and ay:
            if x > self.x + self.w / 2.0:
                return True, self.x + self.w, y
            else:
                return True, self.x, y
        elif bx and by:
            if y > self.y + self.h / 2.0:
                return True, x, self.y + self.h
            else:
                return True, x, self.y
        elif x < self.x and y < self.y:
            if hypot(x - self.x, y - self.y) < radius:
                return True, self.x, self.y
            else:
                return False, 0, 0
        elif x > self.x + self.w and y < self.y:
            if hypot(x - self.x - self.w, y - self.y) < radius:
                return True, self.x + self.w, self.y
            else:
                return False, 0, 0
        elif x > self.x + self.w and y > self.y + self.h:
            if hypot(x - self.x - self.w, y - self.y - self.h) < radius:
                return True, self.x + self.w, self.y + self.h
            else:
                return False, 0, 0
        elif x < self.x and y > self.y + self.h:
            if hypot(x - self.x, y - self.y - self.h) < radius:
                return True, self.x, self.y + self.h
            else:
                return False, 0, 0
        else:
            return False, 0, 0

class Arc(object):
    def __init__(self, x, y, inRadius, outRadius, angle0, angle1):
        """Makes an Arc surface with center(not barycenter!) in (x, y).
        
        The surface is swept anti-clockwise from angle0 to angle1.
        """
        self.x = x
        self.y = y
        self.inRadius = min(inRadius, outRadius)
        self.outRadius = max(inRadius, outRadius)
        
        #We sanitize angle values, but take into account their
        #"before-sanitation order" to preserve the expected swept area.
        #This procedure will also highlight whether degree zero is swept by
        #the arc, making it problematic.
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
        if self._special:
            self.collidePoint = self.collidePointSpecial
            self.collideCircle = self.collideCircleSpecial
        
        self.rect = Rect(self.getRectangle())
        self.rect.normalize()
    
    def collidePoint(self, x, y):
        if self.inRadius**2 <= (x - self.x)**2 + (y - self.y)**2 <= self.outRadius**2:
            if self.angle0 <= getDirection(self.x, self.y, x, y) <= self.angle1:
                return True
        return False
    
    def collidePointSpecial(self, x, y):
        if self.inRadius**2 <= (x - self.x)**2 + (y - self.y)**2 <= self.outRadius**2:
            d = getDirection(self.x, self.y, x, y)
            if d <= self.angle0 or d >= self.angle1:
                return True
        return False
    
    def collideCircle(self, x, y, radius):
        distance = hypot(x - self.x, y - self.y)
        if self.inRadius - radius <= distance <= self.outRadius + radius:
            u = radius / distance / 2.0
            if self.angle0 <= getDirection(self.x, self.y, x, y) <= self.angle1:
                return True, self.x, self.y
        return False, self.x, self.y
    
    def collideCircleSpecial(self, x, y, radius):
        distance = hypot(x - self.x, y - self.y)
        if self.inRadius - radius <= distance <= self.outRadius + radius:
            u = radius / distance / 2.0
            d = getDirection(self.x, self.y, x, y)
            if d < self.angle0 or d > self.angle1:
                return True, self.x, self.y
        return False, self.x, self.y
    
    def getRectangle(self):
        """Returns x, y, w, h"""
        ax = self.x + cos(self.angle0) * self.inRadius
        ay = self.y + sin(self.angle0) * self.inRadius
        bx = self.x + cos(self.angle0) * self.outRadius
        by = self.y + sin(self.angle0) * self.outRadius
        cx = self.x + cos(self.angle1) * self.outRadius
        cy = self.y + sin(self.angle1) * self.outRadius
        dx = self.x + cos(self.angle1) * self.inRadius
        dy = self.y + sin(self.angle1) * self.inRadius
        #Middle of the arc
        ex = self.x + cos((self.angle0 + self.angle1) / 2.0) * self.outRadius
        ey = self.y + sin((self.angle0 + self.angle1) / 2.0) * self.outRadius
        
        top = min(ay, by, cy, dy, ey)
        bottom = max(ay, by, cy, dy, ey)
        left = min(ax, bx, cx, dx, ex)
        right = max(ax, bx, cx, dx, ex)
        
        return left, top, right - left, bottom - top
