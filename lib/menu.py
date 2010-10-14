import sys
from math import sin, cos, pi

import pygame

HALF_PI = pi / 2.0

#Graphics constants
COLOR0 = 255, 255, 255
COLOR1 = 255, 127, 0
COLOR2 = 255, 0, 0
COLOR3 = 0, 0, 0

def sinInterpolation(start, end, steps=30):
    values = [start]
    delta = end - start
    for i in range(1, steps):
        n = HALF_PI * (i / float(steps - 1))
        values.append(start + delta * sin(n))
    return values

def createMenuFromDict(main, dictionary, onSelection, backText, x, y, radius,
                   arc=pi*2.0, defaultAngle=0.0, wrap=True, headerText="Spam"):
    """Creates a tree of menus from a tree of dictionaries.
    
    dictionary: string:function or string:dictionary pairs
    onSelection: the function to call on entering a subMenu
    backText: the string that appears on the menu item to go back
    """
    menu = RotatingMenu(main, x, y, radius, arc, defaultAngle, wrap, headerText)
    for k, v in dictionary.items():
        if type(v) == dict:
            #We make a sub-menu, a way to come back and a way to reach it
            sub = createMenuFromDict(main, v, onSelection, backText, x, y, radius, arc, defaultAngle, wrap, k)
            sub.addItem(MenuItem(backText, lambda: onSelection(menu)))
            menu.addItem(MenuItem(k, lambda: onSelection(sub)))
        else:
            menu.addItem(MenuItem(k, v))
    return menu

class Header:
    def __init__(self, x, y, text, color=COLOR1):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        
        self.font = pygame.font.Font(None, 38)
        self.image = self.font.render(self.text, True, self.color)
        size = self.font.size(self.text)
        
        self.xOffset = size[0] / 2
        self.yOffset = size[1] / 2
    
    def redrawText(self):
        self.image = self.font.render(self.text, True, self.color)
        size = self.font.size(self.text)
        self.xOffset = size[0] / 2
        self.yOffset = size[1] / 2
    
    def draw(self, display):
        display.blit(self.image, (self.x-self.xOffset, self.y-self.yOffset))

class RotatingMenu:
    def __init__(self, main, x, y, radius, arc=pi*2, defaultAngle=0, wrap=True, headerText="Spam"):
        """
        @param x:
            The horizontal center of this menu in pixels.
        
        @param y:
            The vertical center of this menu in pixels.
        
        @param radius:
            The radius of this menu in pixels(note that this is the size of
            the circular path in which the elements are placed, the actual
            size of the menu may vary depending on item sizes.
        
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
        self.radius = radius
        self.arc = arc
        self.defaultAngle = defaultAngle
        self.wrap = wrap
        
        self.rotation = 0
        self.rotationTarget = 0
        self.rotationSteps = [] #Used for interpolation
        
        self.header = Header(320, 80, headerText)
        
        self.items = []
        self.selectedItem = None
        self.selectedItemNumber = 0
        
        #Respond to events
        main.bind('quit', sys.exit)
        main.bind('keyDown', self.onKeyPress)
    
    def onKeyPress(self, key, mod):
        if key == pygame.K_UP or key == pygame.K_RETURN:
            self.selectedItem.function(*self.selectedItem.args,
                                       **self.selectedItem.kwargs)
        elif key == pygame.K_LEFT:
            self.selectItem(self.selectedItemNumber + 1)
        elif key == pygame.K_RIGHT:
            self.selectItem(self.selectedItemNumber - 1)
    
    def addItem(self, item):
        self.items.append(item)
        if len(self.items) == 1:
            self.selectedItem = item
        
        self.selectItemImmediately(len(self.items) // 2)
        return item
    
    def selectItem(self, itemNumber):
        if self.wrap == True:
            if itemNumber > len(self.items) - 1: itemNumber = 0
            if itemNumber < 0: itemNumber = len(self.items) - 1
        else:
            itemNumber = min(itemNumber, len(self.items) - 1)
            itemNumber = max(itemNumber, 0)
        
        self.selectedItem.deselect()
        self.selectedItem = self.items[itemNumber]
        self.selectedItem.select()
        
        self.selectedItemNumber = itemNumber
        
        self.rotationTarget = - self.arc * (itemNumber / float(len(self.items)))
        
        self.rotationSteps = sinInterpolation(self.rotation,
                                              self.rotationTarget, 60)
    
    def selectItemImmediately(self, itemNumber):
        self.selectedItem.deselect()
        self.selectedItem = self.items[itemNumber]
        self.selectedItem.select()
        
        self.selectedItemNumber = itemNumber
        
        self.rotation = - self.arc * (itemNumber / float(len(self.items)))
        
        self.rotate(self.rotation)
    
    def rotate(self, angle):
        """@param angle: The angle in radians by which the menu is rotated.
        """
        for i in range(len(self.items)):
            item = self.items[i]
            n = i / float(len(self.items))
            rot = self.defaultAngle + angle + self.arc * n
            
            item.x = self.x + cos(rot) * self.radius
            item.y = self.y + sin(rot) * self.radius / 2.0
    
    def update(self):
        if len(self.rotationSteps) > 0:
            self.rotation = self.rotationSteps.pop(0)
            self.rotate(self.rotation)
    
    def draw(self, display):
        display.fill((255,255,255))
        self.header.draw(display)
        for item in self.items:
            item.draw(display)

class MenuItem:
    def __init__(self, text="Spam", function=None, args=[], kwargs={}):
        self.text = text
        
        self.function = function
        self.args = args
        self.kwargs = kwargs
        
        self.defaultColor = COLOR1
        self.selectedColor = COLOR3
        self.color = self.defaultColor
        
        self.x = 0
        self.y = 0 #The menu will edit these
        
        self.font = pygame.font.Font(None, 28)
        self.image = self.font.render(self.text, True, self.color)
        size = self.font.size(self.text)
        self.xOffset = size[0] / 2
        self.yOffset = size[1] / 2
    
    def select(self):
        """Just visual stuff"""
        self.color = self.selectedColor
        self.redrawText()
    
    def deselect(self):
        """Just visual stuff"""
        self.color = self.defaultColor
        self.redrawText()
    
    def redrawText(self):
        self.image = self.font.render(self.text, True, self.color)
        size = self.font.size(self.text)
        self.xOffset = size[0] / 2
        self.yOffset = size[1] / 2
    
    def draw(self, display):
        display.blit(self.image, (self.x-self.xOffset, self.y-self.yOffset))
