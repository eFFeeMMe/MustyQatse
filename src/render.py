#!/usr/bin/env python
import pygame

COLOR0 = 255, 255, 255
COLOR1 = 255, 127, 0
COLOR2 = 255, 0, 0
COLOR3 = 0, 0, 0
COLOR4 = 191, 191, 191
COLOR5 = 211, 211, 211


def render_string(s, color):
    font = pygame.font.Font(None, 28)
    return font.render(s, True, color)


def render_level(display, level):
    for plan in level.plans:
        pass

    for block in level.blocks:
        display.blit(block.image, block.rect)


def render_silhouette(shape, color):
    x0, y0, w, h = (int(val) for val in shape.aabb)
    surface = pygame.Surface((w, h), pygame.SRCALPHA, 32)
    colorArray = pygame.surfarray.pixels3d(surface)
    alphaArray = pygame.surfarray.pixels_alpha(surface)
    for x in range(w):
        for y in range(h):
            if shape.hit(x0 + x, y0 + y):
                colorArray[x][y] = color
                alphaArray[x][y] = 255

    return surface


def render_silhouette_multisampled(shape, color):
    x0, y0, w, h = (int(val) for val in shape.aabb)
    surface = pygame.Surface((w, h), pygame.SRCALPHA, 32)
    colorArray = pygame.surfarray.pixels3d(surface)
    alphaArray = pygame.surfarray.pixels_alpha(surface)
    for x in range(w * 2):
        for y in range(h * 2):
            if shape.hit(x0 + x / 2.0, y0 + y / 2.0):
                colorArray[x // 2][y // 2][0:3] = color
                alphaArray[x // 2][y // 2][3] += 255 // 4

    return surface
