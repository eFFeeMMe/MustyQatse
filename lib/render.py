#!/usr/bin/env python
import pygame

COLOR0 = 255, 255, 255
COLOR1 = 255, 127, 0
COLOR2 = 255, 0, 0
COLOR3 = 0, 0, 0
COLOR4 = 191, 191, 191
COLOR5 = 211, 211, 211

def string(s, color):
    font = pygame.font.Font(None, 28)
    return font.render(s, True, color)

def level(display, level):
    if level._prerendered == False:
        for block in level.blocks:
            block.image = silhouette(block.geom, COLOR1, True)
            block.hitImage = silhouette(block.geom, COLOR2, True)
        level._prerendered = True
    
    for plan in level.plans:
        pass
    
    for block in level.blocks:
        image = block.hitImage if block.touched else block.image
        display.blit(image, block.geom.rect)

def silhouette(shape, color, aa=False):
    rect = shape.rect
    
    hurray = list(list([0, 0, 0, 0] for i in range(rect.height)) for i in range(rect.width))
    if aa:
        for x in range(rect.width*2):
            for y in range(rect.height*2):
                if shape.collidePoint(rect.left + x / 2.0, rect.top + y / 2.0):
                    hurray[x/2][y/2][0:3] = color
                    hurray[x/2][y/2][3] += 255 / 4
    else:
        for x in range(rect.width):
            for y in range(rect.height):
                if shape.collidePoint(rect.left + x, rect.top + y):
                    hurray[x][y][0:3] = color
                    hurray[x][y][3] = 255
    
    image = pygame.Surface(rect.size, pygame.SRCALPHA, 32)
    colorArray = pygame.surfarray.pixels3d(image)
    alphaArray = pygame.surfarray.pixels_alpha(image)
    for w in range(rect.width):
        for h in range(rect.height):
            colorArray[w][h][0:3] = hurray[w][h][0:3]
            alphaArray[w][h] = hurray[w][h][3]
    
    return image
