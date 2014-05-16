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
    for plan in level.plans:
        pass
    
    for block in level.blocks:
        image = block.hitImage if block.touched else block.image
        display.blit(image, block.rect)

def silhouette(shape, color):
    x0, y0, w, h = (int(val) for val in shape.aabb)
    image = pygame.Surface((w, h), pygame.SRCALPHA, 32)
    colorArray = pygame.surfarray.pixels3d(image)
    alphaArray = pygame.surfarray.pixels_alpha(image)
    for x in range(w):
        for y in range(h):
            if shape.hit(x0 + x, y0 + y):
                colorArray[x][y] = color
                alphaArray[x][y] = 255
    
    return image

def silhouette_multisampled(shape, color):
    x0, y0, w, h = (int(val) for val in shape.aabb)
    image = pygame.Surface((w, h), pygame.SRCALPHA, 32)
    colorArray = pygame.surfarray.pixels3d(image)
    alphaArray = pygame.surfarray.pixels_alpha(image)
    for x in range(w*2):
        for y in range(h*2):
            if shape.hit(x0 + x / 2., y0 + y / 2.):
                hurray[x//2][y//2][0:3] = color
                hurray[x//2][y//2][3] += 255 // 4
    
    return image