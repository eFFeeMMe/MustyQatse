from math import sqrt, hypot, sin, cos, pi, atan2

import pygame

from .physics.geometry import point_on_line, Circle, Capsule, Rectangle, Arc
from .physics.quadtree import QuadTree
from .render import (
    COLOR0,
    COLOR1,
    COLOR2,
    COLOR3,
    COLOR4,
    render_level,
    render_silhouette,
    render_silhouette_multisampled,
    render_string
)
from .particle import Explosion, ParticleSystem, Text
from .event import EventHandler
from .menu import sinInterpolation
from . import settings

if settings.ANTIALIASING:
    render_silhouette = render_silhouette_multisampled

#Dynamics constants
GRAVITY = 0.04
FRICTION = 0.003

class GUI(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
        self.score = 0
        self.balls = 0
    
    @property
    def score(self):
        return self._score
    @score.setter
    def score(self, x):
        self._score = x
        self.score_image = render_string("Score: %i" %self.score, COLOR1)
    
    @property
    def balls(self):
        return self._balls
    @balls.setter
    def balls(self, x):
        self._balls = x
        self.balls_image = render_string("Balls: %i" %self.balls, COLOR1)
    
    def draw(self, display):
        display.blit(self.score_image, (self.x, self.y))
        display.blit(self.balls_image, (self.x, self.y+30))

class Block:
    def __init__(self, geom):
        self.touched = False
        self.geom = geom
        self.rect = pygame.Rect(geom.aabb)
        self._image = render_silhouette(geom, COLOR1)
        self._hitImage = render_silhouette(geom, COLOR2)
    
    @property
    def image(self):
        return self._hitImage if self.touched else self._image

    def touch(self):
        self.touched = True

class Level:
    def __init__(self, x=0, y=0, w=960, h=540):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
        self.plans = set()
        self.blocks = set()
        
        self.planTree = QuadTree(boundingRect=(x, y, x+w, y+h))
        self.quadTree = QuadTree(boundingRect=(x, y, x+w, y+h))
    
    def save(self):
        pass
    
    def load(self):
        self.startingBalls = 12
        self.blocks |= set(Block(Circle(480 - 192 + 384/16*i, 250 + i%2*24, 16.0)) for i in range(16))
        
        n = 9
        r0 = 48.
        r1 = 48. + 16.
        self.blocks |= set(Block(Arc(300., 128., r0, r1, i*pi/n, pi/n*(i+.9))) for i in range(n))
        self.blocks |= set(Block(Arc(480., 80.,  r0, r1, i*pi/n, pi/n*(i+.9))) for i in range(n))
        self.blocks |= set(Block(Arc(660., 128., r0, r1, i*pi/n, pi/n*(i+.9))) for i in range(n))
        
        self.blocks |= set(Block(Capsule(32.+48.*i, 360., 48.+48.*i, 360., 8.)) for i in range(12))
        self.blocks |= set(Block(Rectangle(32.+48.*i, 400., 24., 16.)) for i in range(13))
        
        for block in self.blocks:
            self.quadTree.insert(block)

class Ball(object):
    max_bumps = 64
    def __init__(self, x, y, r):
        self.bumps = 0
        
        self.geom = geom = Circle(x, y, r)
        geom.xp = x
        geom.yp = y
        
        self.rect = pygame.Rect(geom.aabb)
        self.image = render_silhouette(geom, COLOR3)
    
    def accelerate(self, multiplier):
        geom = self.geom
        geom.xp = geom.xp - (geom.x - geom.xp) * multiplier
        geom.yp = geom.yp - (geom.y - geom.yp) * multiplier
    
    def accelerateInDirection(self, direction, acceleration):
        self.geom.xp -= cos(direction) * acceleration
        self.geom.yp -= sin(direction) * acceleration
    
    def accelerateTowardsPoint(self, x, y, acceleration):
        dx = x - self.geom.x
        dy = y - self.geom.y
        dist = sqrt(dx ** 2 + dy ** 2)
        self.geom.xp -= (dx / dist) * acceleration
        self.geom.yp -= (dy / dist) * acceleration
    
    def update(self):
        geom = self.geom
        
        #Verlet integration
        geom.x, geom.xp = geom.x * (2. - FRICTION) - geom.xp * (1. - FRICTION), geom.x
        geom.y, geom.yp = geom.y * (2. - FRICTION) - geom.yp * (1. - FRICTION), geom.y
        
        geom.yp -= GRAVITY
        
        self.rect.center = geom.x, geom.y

class Emitter:
    def __init__(self, x, y, r=12):
        self.geom = Circle(x, y, r)
        self.rect = pygame.Rect(self.geom.aabb)
        self.image = render_silhouette(self.geom, COLOR3)
    
    def draw(self, display):
        display.blit(self.image, self.rect)
        geom = self.geom
        mx, my = pygame.mouse.get_pos()
        direction = atan2(my - geom.y, mx - geom.x)
        x = int(geom.x + cos(direction) * (geom.r + 1.))
        y = int(geom.y + sin(direction) * (geom.r + 1.))
        pygame.draw.line(display, COLOR0, (geom.x, geom.y), (x, y), 5)

class Catcher:
    def __init__(self, x, y, r0, r1, angle0=-pi*.75, angle1=-pi*.25):
        geom = self.geom = Arc(x, y, r0, r1, angle0, angle1)
        geom.xp = x
        geom.yp = y
        
        self.fix = .1
        
        self.rect = pygame.Rect(geom.aabb)
        self.image = render_silhouette(geom, COLOR3)
    
    def update(self):
        geom = self.geom
        geom.x = geom.x * (1. - self.fix) + pygame.mouse.get_pos()[0] * self.fix
        self.rect.centerx = geom.x
    
    def draw(self, display):
        display.blit(self.image, self.rect)

class Game(EventHandler):
    def __init__(self, main):
        self.score = 0
        self.multiplier = 1.0
        self.avaibleBalls = 10
        
        self.GUI = GUI(50, 50)
        
        self.particleSystem = ParticleSystem()
        
        self.level = Level()
        
        self.emitter = Emitter(320, 24)
        self.catcher = Catcher(320, 540, 84, 100)
        
        #Containers
        self.balls = set()
        
        #Event responses
        main.bind('quit', self.lose)
        main.bind('mouseButtonDown', self.onMousePress)
    
    def onMousePress(self, pos, button):
        if button == 1:
            self.launchBall()
    
    def start(self):
        self.level = Level()
        self.level.load()
        
        self.score = 0
        self.multiplier = 1.0
        self.avaibleBalls = self.level.startingBalls
        
        self.GUI.score = self.score
        self.GUI.balls = self.avaibleBalls
        
        self.balls.clear()
        self.particleSystem.clear()
    
    def launchBall(self):
        if self.avaibleBalls > 0:
            self.avaibleBalls -= 1
            x, y = pygame.mouse.get_pos()
            b = Ball(self.emitter.geom.x, self.emitter.geom.y, 12)
            b.accelerateTowardsPoint(x, y, 2.8)
            self.balls.add(b)
        self.newTurn()
    
    def win(self): #Will be overridden with main module methods
        pass
    
    def lose(self): #Will be overridden with main module methods
        pass
    
    def winCondition(self):
        return len(self.level.blocks) == 0
    
    def loseCondition(self):
        return self.avaibleBalls == 0 and len(self.balls) == 0
    
    def newTurn(self):
        self.multiplier = 1.0
        
        blocksToRemove = set(b for b in self.level.blocks if b.touched)
        self.level.blocks -= blocksToRemove
        
        if self.winCondition():
            self.win()
        elif self.loseCondition():
            self.lose()
        
        for block in blocksToRemove:
            self.particleSystem.add(Explosion(block.rect.centerx, block.rect.centery, 18))
        if self.level.blocks and blocksToRemove:
            self.level.quadTree = QuadTree(items=self.level.blocks)
        
        self.GUI.balls = self.avaibleBalls
    
    def addScore(self):
        self.score += 100. * self.multiplier
        self.multiplier += .5
        self.GUI.score = int(self.score)
    
    def updateDynamics(self):
        for ball in self.balls:
            ball.update()
            bg = ball.geom
            
            #Level walls
            if bg.x < bg.r or bg.x + bg.r > self.level.w:
                bg.x, bg.xp = bg.xp, bg.x
            
            #Block collisions
            for block in self.level.quadTree.hit(ball.rect):
                dx, dy = block.geom.hit_circle(bg.x, bg.y, bg.r)
                if dx is not None:
                    #Depenetrate
                    #bg.x -= dx
                    #bg.y -= dy
                    #bg.xp -= dx
                    #bg.yp -= dy
                    
                    #Bounce
                    px, py = point_on_line(bg.xp, bg.yp, bg.x, bg.y, bg.x - dx, bg.y - dy)
                    bg.xp = px * 2. - bg.xp
                    bg.yp = py * 2. - bg.yp
                    bg.xp, bg.x = bg.x, bg.xp
                    bg.yp, bg.y = bg.y, bg.yp
                    
                    #Gameplay
                    ball.bumps += 1
                    if not block.touched:
                        block.touch()
                        self.addScore()
                    #    self.particleSystem.add(Text(px, py, "x%i" %int(self.multiplier)))
                    #self.particleSystem.add(Explosion(px, py))
            
            if self.catcher.rect.colliderect(ball.rect):
                if self.catcher.geom.hit_circle(bg.x, bg.y, bg.r)[0] is not None:
                    px, py = point_on_line(bg.xp, bg.yp, bg.x, bg.y, self.catcher.geom.x, self.catcher.geom.y)
                    bg.xp = px * 2. - bg.xp
                    bg.yp = py * 2. - bg.yp
                    
                    bg.xp, bg.x = bg.x, bg.xp #Invert motion
                    bg.yp, bg.y = bg.y, bg.yp
                    
                    self.particleSystem.add(Explosion(ball.geom.x, ball.geom.y, 7))
    
    def update(self):
        self.updateDynamics()
        
        #Update game logic
        self.catcher.update()
        self.particleSystem.update()
        
        deadBalls = set()
        for ball in self.balls:
            if ball.geom.y > self.level.h + ball.geom.r:
                deadBalls.add(ball)
            elif ball.bumps > ball.max_bumps:
                deadBalls.add(ball)
        for ball in deadBalls:
            self.particleSystem.add(Explosion(ball.geom.x, ball.geom.y, 18))
        self.balls -= deadBalls
        if deadBalls and len(self.balls) == 0:
            self.newTurn()
    
    def draw(self, display):
        display.fill(COLOR0)
        
        render_level(display, self.level)
        
        self.emitter.draw(display)
        self.catcher.draw(display)
        
        for ball in self.balls:
            display.blit(ball.image, ball.rect)
        
        self.particleSystem.draw(display)
        
        self.GUI.draw(display)
