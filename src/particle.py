import pygame

from .menu import sinInterpolation
from .settings import COLOR0, COLOR1, COLOR2, COLOR3


class ParticleSystem:
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
    def __init__(
        self, x, y, life=30, startRadius=16, startColor=COLOR2, endColor=COLOR0
    ):
        self.x = x
        self.y = y
        self.radius = startRadius
        self.color = list(startColor)

        self.startRadius = startRadius
        self.startColor = startColor
        self.endColor = endColor

        self.life = life
        self.alphaSteps = sinInterpolation(0, 1, life)

    def update(self):
        try:
            a = self.alphaSteps.__next__()
            self.radius = self.startRadius + self.startRadius * a
            for i in 0, 1, 2:
                self.color[i] = self.startColor[i] * (1 - a) + self.endColor[i] * a
        except StopIteration:
            pass

    def draw(self, display):
        pygame.draw.circle(
            display, self.color, (int(self.x), int(self.y)), int(self.radius), 1
        )


class Text:
    def __init__(self, x, y, text, life=30, color=COLOR3):
        self.x = x
        self.y = y

        self.life = life

        self.image = pygame.font.Font(None, 12).render(text, True, color)

    def update(self):
        self.y -= 0.5

    def draw(self, display):
        display.blit(self.image, (self.x, self.y))
