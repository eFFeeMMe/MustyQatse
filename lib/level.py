#!/usr/bin/env python
from math import sin, cos, pi

from quadtree import QuadTree
from geometry import Circle, Rectangle, Capsule, Arc

class Block:
    _dynamic = False
    def __init__(self, geom):
        self.touched = False
        self.geom = geom
        self.rect = geom.rect
    
    def touch(self):
        self.touched = True

class Level:
    def __init__(self, x=0, y=0, w=640, h=480):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
        self.plans = set()
        self.blocks = set()
        
        self.planTree = QuadTree(boundingRect=(x, y, x+w, y+h))
        self.quadTree = QuadTree(boundingRect=(x, y, x+w, y+h))
        
        self._prerendered = False
    
    def save(self):
        pass
    
    def load(self):
        self.startingBalls = 12
        self.blocks |= set(Block(Circle(320 - 192 + 384/16*i, 250 + i%2*24, 16.0)) for i in range(16))
        #self.blocks |= set(Block(Circle(320 - 192 + 384/16*i, 298 + i%2*24, 16.0)) for i in range(16))
        
        n = 9
        r0 = 48
        r1 = 48 + 16
        self.blocks |= set(Block(Arc(140, 128, r0, r1, pi/n*i, pi/n*(i+0.9))) for i in range(n))
        self.blocks |= set(Block(Arc(320, 80,  r0, r1, pi/n*i, pi/n*(i+0.9))) for i in range(n))
        self.blocks |= set(Block(Arc(500, 128, r0, r1, pi/n*i, pi/n*(i+0.9))) for i in range(n))
        
        self.blocks |= set(Block(Capsule(32+48.0*i, 360.0, 48+48.0*i, 360.0, 8.0)) for i in range(12))
        self.blocks |= set(Block(Rectangle(32+48.0*i, 400.0, 24.0, 16.0)) for i in range(13))
        
        for block in self.blocks:
            self.quadTree.insert(block)
