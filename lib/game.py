from math import sqrt, hypot, sin, cos, pi

import pygame

from geometry import getDirection, pointOnLine, Circle, Capsule, Rectangle, Arc
import render
import particle
from event import EventHandler
from level import Level
from quadtree import QuadTree
from menu import sinInterpolation

#Dynamics constants
GRAVITY = 0.04
FRICTION = 0.003

#Graphics constants
COLOR0 = 255, 255, 255
COLOR1 = 255, 127, 0
COLOR2 = 255, 0, 0
COLOR3 = 0, 0, 0

class GUI:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        self.score = 0
        self.balls = 0
        
        self.updateImage()
    
    def updateImage(self):
        self.scoreImage = render.string("Score: %i" %self.score, COLOR1)
        self.ballsImage = render.string("Balls: %i" %self.balls, COLOR1)
    
    def draw(self, display):
        display.blit(self.scoreImage, (self.x, self.y))
        display.blit(self.ballsImage, (self.x, self.y+30))

class Ball:
    maxBumps = 64
    def __init__(self, x, y, radius):
        self.bumps = 0
        
        self.geom = geom = Circle(x, y, radius)
        geom.xPrev = x
        geom.yPrev = y
        
        self.rect = geom.rect
        self.image = render.silhouette(geom, COLOR3, True)
    
    def accelerate(self, multiplier):
        geom = self.geom
        geom.xPrev = geom.xPrev - (geom.x - geom.xPrev) * multiplier
        geom.yPrev = geom.yPrev - (geom.y - geom.yPrev) * multiplier
    
    def accelerateInDirection(self, direction, acceleration):
        self.geom.xPrev -= cos(direction) * acceleration
        self.geom.yPrev -= sin(direction) * acceleration
    
    def accelerateTowardsPoint(self, x, y, acceleration):
        dx = x - self.geom.x
        dy = y - self.geom.y
        dist = sqrt(dx ** 2 + dy ** 2)
        self.geom.xPrev -= (dx / dist) * acceleration
        self.geom.yPrev -= (dy / dist) * acceleration
    
    def update(self):
        geom = self.geom
        geom.x, geom.xPrev = geom.x * (2 - FRICTION) - geom.xPrev * (1 - FRICTION), geom.x
        geom.y, geom.yPrev = geom.y * (2 - FRICTION) - geom.yPrev * (1 - FRICTION), geom.y
        geom.yPrev -= GRAVITY
        
        self.rect.center = geom.x, geom.y

class Emitter:
    def __init__(self, x, y, radius=12):
        self.geom = Circle(x, y, radius)
        self.rect = self.geom.rect
        self.image = render.silhouette(self.geom, COLOR3, True)

class Catcher:
    def __init__(self, x, y, inRadius, outRadius, angle0, angle1):
        geom = self.geom = Arc(x, y, inRadius, outRadius, angle0, angle1)
        geom.xPrev = x
        geom.yPrev = y
        
        self.fix = 0.1
        
        self.rect = geom.rect
        self.image = render.silhouette(geom, COLOR3, True)
    
    def update(self):
        geom = self.geom
        geom.x = geom.x * (1 - self.fix) + pygame.mouse.get_pos()[0] * self.fix
        self.rect.centerx = geom.x

class Game(EventHandler):
    def __init__(self):
        self.score = 0
        self.multiplier = 1.0
        self.avaibleBalls = 10
        
        self.GUI = GUI(50, 50)
        
        self.particleSystem = particle.System()
        
        self.level = Level()
        
        self.emitter = Emitter(320, 24)
        self.catcher = Catcher(320, 540, 84, 100, -pi*0.75, -pi*0.25)
        
        #Containers
        self.balls = set()
    
    def start(self):
        self.level = Level()
        self.level.load()
        
        self.score = 0
        self.multiplier = 1.0
        self.avaibleBalls = self.level.startingBalls
        
        self.GUI.score = self.score
        self.GUI.balls = self.avaibleBalls
        self.GUI.updateImage()
        
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
            self.particleSystem.add(particle.Explosion(block.rect.centerx, block.rect.centery, 18))
        if self.level.blocks and blocksToRemove:
            self.level.quadTree = QuadTree(items=self.level.blocks)
        
        self.GUI.balls = self.avaibleBalls
        self.GUI.updateImage()
    
    def addScore(self):
        self.score += 1.0 * self.multiplier
        self.multiplier += 0.5
        self.GUI.score = int(self.score)
        self.GUI.updateImage()
    
    def updateDynamics(self):
        for ball in self.balls:
            ball.update()
            ballG = ball.geom
            if ballG.x < ballG.radius or ballG.x + ballG.radius > self.level.w:
                ballG.x, ballG.xPrev = ballG.xPrev, ballG.x
            for block in self.level.quadTree.hit(ball.rect):
                collision, cx, cy = block.geom.collideCircle(ballG.x, ballG.y, ballG.radius)
                if collision:
                    #Dynamics
                    px, py = pointOnLine(ballG.xPrev, ballG.yPrev, ballG.x, ballG.y, cx, cy)
                    ballG.xPrev = px * 2.0 - ballG.xPrev
                    ballG.yPrev = py * 2.0 - ballG.yPrev
                    
                    ballG.xPrev, ballG.x = ballG.x, ballG.xPrev
                    ballG.yPrev, ballG.y = ballG.y, ballG.yPrev
                    
                    #Gameplay
                    ball.bumps += 1
                    if not block.touched:
                        block.touch()
                        self.addScore()
                        self.particleSystem.add(particle.Text(px, py, "x%i" %int(self.multiplier)))
                    self.particleSystem.add(particle.Explosion(px, py))
            
            if self.catcher.rect.colliderect(ball.rect):
                if self.catcher.geom.collideCircle(ballG.x, ballG.y, ballG.radius)[0]:
                    px, py = pointOnLine(ballG.xPrev, ballG.yPrev, ballG.x, ballG.y, self.catcher.geom.x, self.catcher.geom.y)
                    ballG.xPrev = px * 2.0 - ballG.xPrev
                    ballG.yPrev = py * 2.0 - ballG.yPrev
                    
                    ballG.xPrev, ballG.x = ballG.x, ballG.xPrev #Invert motion
                    ballG.yPrev, ballG.y = ballG.y, ballG.yPrev
                    
                    self.particleSystem.add(particle.Explosion(ball.geom.x, ball.geom.y, 7))
    
    def update(self, events):
        #Handle events
        for event in events:
            if event.type == pygame.QUIT:
                self.lose()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.launchBall()
        
        self.updateDynamics()
        
        #Update game logic
        self.catcher.update()
        self.particleSystem.update()
        
        deadBalls = set()
        for ball in self.balls:
            if ball.geom.y > self.level.h + ball.geom.radius:
                deadBalls.add(ball)
            elif ball.bumps > ball.maxBumps:
                deadBalls.add(ball)
        for ball in deadBalls:
            self.particleSystem.add(particle.Explosion(ball.geom.x, ball.geom.y, 18))
        self.balls -= deadBalls
        if deadBalls and len(self.balls) == 0:
            self.newTurn()
    
    def draw(self, display):
        display.fill(COLOR0)
        
        render.level(display, self.level)
        
        display.blit(self.emitter.image, self.emitter.rect)
        geom = self.emitter.geom
        direction = getDirection(geom.x, geom.y, *pygame.mouse.get_pos())
        x = int(geom.x + cos(direction) * (geom.radius + 1.0))
        y = int(geom.y + sin(direction) * (geom.radius + 1.0))
        pygame.draw.line(display, COLOR0, (geom.x, geom.y), (x, y), 5)
        
        display.blit(self.catcher.image, self.catcher.rect)
        for ball in self.balls:
            display.blit(ball.image, ball.rect)
        
        self.particleSystem.draw(display)
        
        self.GUI.draw(display)
