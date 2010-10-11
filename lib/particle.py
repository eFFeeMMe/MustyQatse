#!/usr/bin/env python
import pygame

from menu import sinInterpolation

#Graphics constants
COLOR0 = 255, 255, 255
COLOR1 = 255, 127, 0
COLOR2 = 255, 0, 0
COLOR3 = 0, 0, 0

class System:
    def __init__(self):
        self.particles = set()
    
    def add(self, particle):
        self.particles.add(particle)
    
    def clear(self):
        self.particles = set()
    
    def update(self):
        deadParticles = set()
        for particle in self.particles:
            if particle.life > 0:
                particle.update()
                particle.life -= 1
            else:
                deadParticles.add(particle)
        self.particles -= deadParticles
    
    def draw(self, display):
        for particle in self.particles:
            particle.draw(display)

class Explosion:
    def __init__(self, x, y, startRadius=16, startColor=COLOR1, endColor=COLOR0):
        self.x = x
        self.y = y
        self.radius = startRadius
        self.color = list(startColor)
        
        self.startRadius = startRadius
        self.startColor = startColor
        self.endColor = endColor
        
        self.life = 30
        self.maxLife = 30
        self.alphaSteps = sinInterpolation(0, 1, self.life)
    
    def update(self):
        a = self.alphaSteps[self.maxLife - self.life]
        self.radius = self.startRadius + self.startRadius * a
        for i in 0, 1, 2:
            self.color[i] = self.startColor[i] * (1 - a) + self.endColor[i] * a
    
    def draw(self, display):
        pygame.draw.circle(display, self.color, (self.x, self.y), self.radius, 1)

class Text:
    def __init__(self, x, y, text, color=COLOR3):
        self.x = x
        self.y = y
        
        self.life = 30
        
        self.image = pygame.font.Font(None, 12).render(text, True, color)
    
    def update(self):
        self.y -= 0.5
    
    def draw(self, display):
        display.blit(self.image, (self.x, self.y))