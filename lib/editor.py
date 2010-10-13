#!/usr/bin/env python
import sys
from math import cos, sin, pi, hypot

import pygame

import render
from level import Level
from geometry import getDirection, pointOnSegment, pointOnCircle, Circle, Capsule, Rectangle, Arc

class Line:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        
        self.subdivisions = 3.0
        
        dx = x1 - x0
        dy = y1 - y0
        self.length = hypot(dx, dy)
        self.segmentLength = self.length / self.subdivisions
        
        self.rect = pygame.Rect(x0, y0, x1, y1)
        self.rect.normalize()
    
    def pointDistance(self, x, y):
        return pointOnSegment(x, y, self.x0, self.y0, self.x1, self.y1)
    
    def snapToPoint(self, x, y):
        distance = hypot(x - self.x0, y - self.y0)
        decrement = distance % self.segmentLength
        if decrement < self.segmentLength / 2.0:
            snapDistance = distance - decrement
        else:
            snapDistance = distance - decrement + self.segmentLength
        x = self.x0 + (self.x1 - self.x0) / self.length * snapDistance
        y = self.y0 + (self.y1 - self.y0) / self.length * snapDistance
        return x, y
    
    def draw(self, display):
        pygame.draw.line(display, COLOR4, (self.x0, self.y0), (self.x1, self.y1))
        
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        for i in range(int(self.subdivisions) + 1):
            x = self.x0 + dx * (i / self.subdivisions)
            y = self.y0 + dy * (i / self.subdivisions)
            pygame.draw.circle(display, COLOR4, (x, y), 2)

class Circle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 0.0
        self.subdivisions = 2.0
        r = self.radius = (unit * self.subdivisions) / (pi * 2.0)
        
        self.rect = pygame.Rect(self.x - r, self.y - r, self.x + r, self.y + r)
    
    def snap(self, x, y):
        direction = getDirection(self.x, self.y, x, y)
        increment = pi * 2 / self.subdivisions
        decrement = direction % increment
        if decrement < increment / 2.0:
            snapDirection = direction - decrement
        else:
            snapDirection = direction - decrement + increment
        x = self.x + cos(snapDirection) * self.radius
        y = self.y + sin(snapDirection) * self.radius
        return x, y
    
    def pointDistance(self, x, y):
        return sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
    
    def draw(self, display):
        pygame.draw.circle(display, COLOR4, (self.x, self.y), self.radius, 1)
        
        for i in range(self.subdivisions):
            direction = self.direction + (i / self.subdivisions) * pi * 2
            x = self.x + cos(direction) * self.outRadius
            y = self.y + sin(direction) * self.outRadius
            pygame.draw.circle(display, COLOR4, (x, y), 2)

class Editor: #In MVC terms, Level is the model, Editor is the control
    def __init__(self):
        self.planMode = PlanMode(self)
        self.objectMode = ObjectMode(self)
        self.mode = self.planMode
        
        self.step = 0
        self.preview = None
        
        self.mx = 0
        self.my = 0
        self.mb = 0 #mouse button
        
        self.snap = True
        
        self.selectionBias = [Line, Circle] #Which gets selected when in doubt
        
        self.hoveredPlan = None
        self.hoveredPlanPx = 0.0 #Projection position
        self.hoveredPlanPy = 0.0
        self.hoveredPlanTouched = False
    
    def getHoveredPlan(self):
        hits = self.level.planTree.hit(pygame.Rect(self.mx-2, self.my-2, 4, 4))
        if hits:
            candidates = list((self.preferenceValues[plan.__class__], plan) for plan in hits if plan.collidePoint(self.mx, self.my))
            if candidates:
                candidates.sort()
                plan = candidates[0][1]
                if plan.__class__ == Point:
                    x, y = plan.x, plan.y
                elif plan.__class__ == Line:
                    x, y = pointOnSegment(self.mx, self.my, plan.x0, plan.y0, plan.x1, plan.y1)
                elif plan.__class__ == Circle:
                    x, y = pointOnCircle(self.mx, self.my, plan.x, plan.y, plan.radius)
                self.hoveredPlan = plan
                self.hoveredPlanPx = x
                self.hoveredPlanPy = y
                self.hoveredPlanTouched = True
            else:
                self.hoveredPlanTouched = False
        else:
            self.hoveredPlanTouched = False
    
    def place(self):
        if self.mode == PLAN_TYPE_LINE:
            if self.step == 0:
                self.preview = Line(self.mx, self.my, self.mx, self.my)
                self.step = 1
            elif self.step == 1:
                self.preview.finalize()
                self.editor.level.plans.add(self.preview)
                self.editor.level.planTree.insert(self.preview)
                self.preview = None
                self.step = 0
        
        elif self.mode == PLAN_TYPE_CIRCLE:
            if self.step == 0:
                self.preview = Circle(self.mx, self.my)
                self.step = 1
            elif self.step == 1:
                self.preview.finalize()
                self.editor.level.plans.add(self.preview)
                self.editor.level.planTree.insert(self.preview)
                self.preview = None
                self.step = 0
    
    def edit(self, mx, my):
        if self.preview:
            if self.mode == PLAN_TYPE_LINE:
                self.preview.x1 = mx
                self.preview.y1 = my
            elif self.mode == PLAN_TYPE_CIRCLE:
                self.preview.direction = getDirection(self.preview.x, self.preview.y,
                                                      mx, my)
            self.preview.refresh()
    
    def remove(self, mx, my):
        if self.step == 0:
            hits = self.editor.level.planTree.hit(pygame.Rect(mx-1, my-1, 2, 2))
            for plan in hits:
                if plan.collidePoint(mx, my):
                    self.editor.level.plans.remove(plan)
                    self.editor.level.planTree.remove(plan)
                    break
        else:
            self.preview = None
            self.step = 0
    
    def mouseMove(self, mx, my):
        self.mx = mx
        self.my = my
    
    def mousePress(self, button):
        self.mb = button
        
        if button == 1:
            self.place()
        elif button == 3:
            self.remove()
    
    def place(self):
        #UNWORKING
        if self.editor.hoveredPlanTouched:
            s = self.selection
            x, y = self.mx, self.my
            cx, cy = self.editor.hoveredPlan.center
            direction  = self.editor.hoveredPlan.direction
            
            s.append(self.editor.hoveredPlanTouched)
            if len(self.selection) == 2:
                if self.mode == PLACE_TYPE_RECTANGLE:
                    block = blocks.Rectangle()
                elif self.mode == PLACE_TYPE_CIRCLE:
                    pass
                elif self.mode == PLACE_TYPE_ARC:
                    pass
    
    def remove(self):
        hits = self.editor.level.quadTree.hit(pygame.Rect(self.mx-2, self.my-2, 4, 4))
        for block in hits:
            if block.collidePoint(self.mx, self.my):
                self.editor.level.blocks.remove(block)
                self.editor.level.quadTree.remove(block)
                break #Remove only one item at a time

class EditorView:
    def __init__(self):
        self.level = Level()
    
    def update(self, events):
        #Handle events
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.mx, self.my = pygame.mouse.get_pos()
                self.getHoveredPlan()
                if self.hoveredPlanTouched:
                    if self.snap:
                        self.mx, self.my = self.hoveredPlan.snap(self.mx, self.my)
                    else:
                        self.mx = self.hoveredPlanPx
                        self.my = self.hoveredPlanPy
                self.modes[self.mode].mouseMove(self.mx, self.my)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.modes[self.mode].mousePress(event.button)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    self.mode = MODE_PLAN
                elif event.key == pygame.K_F2:
                    self.mode = MODE_OBJECT
                else:
                    self.modes[self.mode].keyPress(event.key)
            elif event.type == pygame.QUIT:
                self.back()
    
    def mouseMove(self, mx, my):
        self.edit(mx, my)
    
    def mousePress(self, button):
        if button == 1:
            self.place()
        elif button == 3:
            self.remove()
        elif button == 4:
            if self.preview:
                self.preview.subdivisions += 1
        elif button == 5:
            if self.preview and self.preview.subdivisions > 1:
                self.preview.subdivisions -= 1
    
    def keyPress(self, key):
        if key == pygame.K_F1:
            self.mode = PLAN_TYPE_LINE
        elif key == pygame.K_F2:
            self.mode = PLAN_TYPE_CIRCLE
        elif key == pygame.K_F4:
            self.mode = PLACE_TYPE_RECTANGLE
        elif key == pygame.K_F5:
            self.mode = PLACE_TYPE_CIRCLE
        elif key == pygame.K_F6:
            self.mode = PLACE_TYPE_ARC
    
    def draw(self):
        if self.preview:
            self.preview.draw(display)
            #subdivisions label
            image = self.font.render(str(self.preview.subdivisions), True, COLOR3)
            w, h = self.font.size(str(self.preview.subdivisions))
            display.blit(image, (self.mx - w, self.my - h))
        
        for block in self.level.blocks:
            block.draw(display)
        for plan in self.level.plans:
            plan.draw(display)
        
        self.modes[self.mode].draw(display)
        if self.hoveredPlanTouched:
            display.blit(self.hoveredPlan.hitImage, self.hoveredPlan.rect)
            pygame.draw.circle(display, COLOR1, (self.mx, self.my), 2)
