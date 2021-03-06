import sys
from math import sin, cos, pi

import pygame

from .settings import COLOR0, COLOR1, COLOR2, COLOR3


def sinInterpolation(start, end, steps=30):
    d = end - start
    for i in range(steps):
        yield start + d * sin((float(i) / float(steps - 1)) * pi * 0.5)


class Header(object):
    def __init__(self, x, y, text, color=COLOR1):
        self.x = x
        self.y = y
        self._text = text
        self._color = color
        self.font = pygame.font.Font(None, 54)
        self.render()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.render()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.render()

    def render(self):
        self.image = self.font.render(self._text, True, self._color)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def draw(self, display):
        display.blit(self.image, self.rect)


class RotatingMenu(object):
    def __init__(
        self,
        main,
        x,
        y,
        w,
        h,
        arc=pi * 2.0,
        defaultAngle=0.0,
        wrap=True,
        headerText="Spam",
        backText="Back",
        items={},
        on_selection=None,
    ):
        """
        @param x:
            The horizontal center of this menu in pixels.
        
        @param y:
            The vertical center of this menu in pixels.
        
        @param arc:
            The arc in radians which the menu covers. pi*2 is a full circle.
        
        @param defaultAngle:
            The angle at which the selected item is found.
        
        @param wrap:
            Whether the menu should select the first item after the last one
            or stop.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.arc = arc
        self.defaultAngle = defaultAngle
        self.wrap = wrap

        self.rotation = 0
        self.rotationTarget = 0
        self.rotationSteps = []  # Used for interpolation

        self.header = Header(x, y - w / 4.0, headerText)

        self.items = []
        self.selectedItem = None
        self.selectedItemNumber = 0

        for k, v in items.items():
            if type(v) == dict:
                # We make a sub-menu, a way to come back and a way to reach it
                sub = RotatingMenu(
                    main,
                    x,
                    y,
                    w,
                    h,
                    arc,
                    defaultAngle,
                    wrap=wrap,
                    headerText=k,
                    backText=backText,
                    items=v,
                    on_selection=on_selection,
                )
                sub.add_item(MenuItem(backText, lambda: on_selection(self)))
                self.add_item(MenuItem(k, lambda: on_selection(sub)))
            else:
                self.add_item(MenuItem(k, v))

        # Respond to events
        main.bind("quit", sys.exit)
        main.bind("keyDown", self.onKeyPress)

    def onKeyPress(self, key, mod):
        if key == pygame.K_UP or key == pygame.K_RETURN:
            self.selectedItem.function(
                *self.selectedItem.args, **self.selectedItem.kwargs
            )
        elif key == pygame.K_LEFT:
            self.selectItem(self.selectedItemNumber + 1)
        elif key == pygame.K_RIGHT:
            self.selectItem(self.selectedItemNumber - 1)

    def add_item(self, item):
        self.items.append(item)
        if len(self.items) == 1:
            self.selectedItem = item

        self.selectItemImmediately(len(self.items) // 2)
        return item

    def selectItem(self, itemNumber):
        if self.wrap == True:
            if itemNumber > len(self.items) - 1:
                itemNumber = 0
            if itemNumber < 0:
                itemNumber = len(self.items) - 1
        else:
            itemNumber = min(itemNumber, len(self.items) - 1)
            itemNumber = max(itemNumber, 0)

        self.selectedItem.deselect()
        self.selectedItem = self.items[itemNumber]
        self.selectedItem.select()

        self.selectedItemNumber = itemNumber

        self.rotationTarget = -self.arc * (itemNumber / float(len(self.items)))

        self.rotationSteps = sinInterpolation(self.rotation, self.rotationTarget, 60)

    def selectItemImmediately(self, itemNumber):
        self.selectedItem.deselect()
        self.selectedItem = self.items[itemNumber]
        self.selectedItem.select()

        self.selectedItemNumber = itemNumber

        self.rotation = -self.arc * (itemNumber / float(len(self.items)))

        self.rotate(self.rotation)

    def rotate(self, angle):
        for i in range(len(self.items)):
            item = self.items[i]
            n = i / float(len(self.items))
            rot = self.defaultAngle + angle + self.arc * n

            item.x = self.x + cos(rot) * self.w / 2.0
            item.y = self.y + sin(rot) * self.h / 2.0

    def update(self):
        if self.rotationSteps:
            try:
                self.rotation = self.rotationSteps.__next__()
                self.rotate(self.rotation)
            except StopIteration:
                pass

    def draw(self, display):
        display.fill((255, 255, 255))
        self.header.draw(display)
        for item in self.items:
            item.rect.center = item.x, item.y
            display.blit(item.image, item.rect)


class MenuItem(object):
    def __init__(self, text="Spam", function=None, args=[], kwargs={}):
        self._text = text
        self.defaultColor = COLOR1
        self.selectedColor = COLOR3
        self._color = self.defaultColor

        self.function = function
        self.args = args
        self.kwargs = kwargs

        self.x = 0.0  # RotatingMenu instances will edit these
        self.y = 0.0

        self.font = pygame.font.Font(None, 28)

        self.render()

    def select(self):
        self.color = self.selectedColor

    def deselect(self):
        self.color = self.defaultColor

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.render()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.render()

    def render(self):
        self.image = self.font.render(self._text, True, self._color)
        self.rect = self.image.get_rect()
