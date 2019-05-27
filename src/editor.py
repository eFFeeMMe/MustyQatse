from math import cos, sin, pi, hypot

import pygame

from .render import render_string
from .game import Level
from .physics.geometry import point_on_segment, point_on_circle
from .physics.primitives import Circle, Capsule, Rectangle, Arc
from . import settings
from .settings import COLOR0, COLOR1, COLOR2, COLOR3, COLOR4


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
        return point_on_segment(x, y, self.x0, self.y0, self.x1, self.y1)

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


class Circle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 0.0
        self.subdivisions = 2.0
        r = self.r = (unit * self.subdivisions) / (pi * 2.0)

        self.rect = pygame.Rect(self.x - r, self.y - r, self.x + r, self.y + r)

    def snapToPoint(self, x, y):
        direction = getDirection(self.x, self.y, x, y)
        increment = pi * 2 / self.subdivisions
        decrement = direction % increment
        if decrement < increment / 2.0:
            snapDirection = direction - decrement
        else:
            snapDirection = direction - decrement + increment
        x = self.x + cos(snapDirection) * self.r
        y = self.y + sin(snapDirection) * self.r
        return x, y

    def pointDistance(self, x, y):
        return hypot(x - self.x, y - self.y)


def drawLine(display, line):
    pygame.draw.line(display, COLOR4, (line.x0, line.y0), (line.x1, line.y1))

    dx = line.x1 - line.x0
    dy = line.y1 - line.y0
    for i in range(int(line.subdivisions) + 1):
        x = line.x0 + dx * (i / line.subdivisions)
        y = line.y0 + dy * (i / line.subdivisions)
        pygame.draw.circle(display, COLOR4, (x, y), 2)


def drawCircle(display, circle):
    pygame.draw.circle(display, COLOR4, (circle.x, circle.y), circle.r, 1)

    for i in range(circle.subdivisions):
        direction = circle.direction + (i / circle.subdivisions) * pi * 2
        x = circle.x + cos(direction) * circle.r1
        y = circle.y + sin(direction) * circle.r1
        pygame.draw.circle(display, COLOR4, (x, y), 2)


class Editor:
    def __init__(self, main):
        # Current editing process
        self.process = None
        self.step = 0

        self.preview = None

        # Interaction modes
        self.snapModes = ["grid", "subdivision", "projection"]
        self.snapSet = [Line, Circle]
        self.selectSet = [Line, Circle]

        # Subjects of interaction.
        self.snapX = 0.0
        self.snapY = 0.0
        self.snapped = None  # a Plan
        self.hovered = None  # a Block
        self.selection = []  # a Block

        # Event handling
        # main.bind('event', callback)

    def getHoveredPlan(self):
        hits = list(
            block
            for block in self.level.quadTree.hit(
                pygame.Rect(pos[0] - 2, pos[1] - 2, 4, 4)
            )
            if (type(block) in self.selectSet)
        )
        if hits:
            candidate = hits[0]
            if candidate.hit(*pos):  # mousepos
                self.hovered = candidate
            else:
                self.hovered = None
        else:
            self.hovered = None

    def processPlanLine(self):
        if self.step == 0:
            self.preview = Line(self.mx, self.my, self.mx, self.my)
            self.step = 1
        elif self.step == 1:
            self.preview.finalize()
            self.editor.level.plans.add(self.preview)
            self.editor.level.planTree.insert(self.preview)
            self.preview = None
            self.step = 0

    def processPlanCircle(self):
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
                self.preview.direction = getDirection(
                    self.preview.x, self.preview.y, mx, my
                )
            self.preview.refresh()

    def remove(self, mx, my):
        if self.step == 0:
            hits = self.editor.level.planTree.hit(pygame.Rect(mx - 1, my - 1, 2, 2))
            for plan in hits:
                if plan.hit(mx, my):
                    self.editor.level.plans.remove(plan)
                    self.editor.level.planTree.remove(plan)
                    break
        else:
            self.preview = None
            self.step = 0

    def onMouseMotion(self, mx, my):
        self.mx = mx
        self.my = my

    def onMouseButtonDown(self, pos, button):
        if button == 1:
            self.place()
        elif button == 2:
            pass
        elif button == 3:
            self.deleteSelection()
        elif button == 4:
            pass
        elif button == 5:
            pass

    def processPlaceRect(self):
        # UNWORKING
        if self.editor.hoveredPlanTouched:
            s = self.selection
            x, y = self.mx, self.my
            cx, cy = self.editor.hoveredPlan.center
            direction = self.editor.hoveredPlan.direction

            s.append(self.editor.hoveredPlanTouched)
            if len(self.selection) == 2:
                if self.mode == PLACE_TYPE_RECTANGLE:
                    block = blocks.Rectangle()
                elif self.mode == PLACE_TYPE_CIRCLE:
                    pass
                elif self.mode == PLACE_TYPE_ARC:
                    pass

    def deleteSelection(self):
        if self.selection:
            self.level.blocks.remove(self.selection)
            self.level.quadTree.remove(self.selection)


class EditorView:
    def __init__(self):
        self.level = Level()

    def update(self, events):
        # Handle events
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
        self.keyBindings = {
            pygame.K_F1: PLAN_TYPE_LINE,
            pygame.K_F2: PLAN_TYPE_CIRCLE,
            pygame.K_F4: PLACE_TYPE_RECTANGLE,
            pygame.K_F5: PLACE_TYPE_CIRCLE,
            pygame.K_F6: PLACE_TYPE_ARC,
        }
        self.mode = self.keyBindings[key]

    def draw(self):
        if self.preview:
            self.preview.draw(display)
            # subdivisions label
            image = render_string(str(self.preview.subdivisions), COLOR3)
            w, h = self.font.size(str(self.preview.subdivisions))
            display.blit(image, (self.mx - w, self.my - h))

        for block in self.level.blocks:
            block.draw(display)
        for plan in self.level.plans:
            plan.draw(display)

        self.mode.draw(display)
        if self.hoveredPlanTouched:
            display.blit(self.hoveredPlan._hitImage, self.hoveredPlan.rect)
            pygame.draw.circle(display, COLOR1, (self.mx, self.my), 2)
