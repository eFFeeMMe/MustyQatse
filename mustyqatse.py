import sys
from math import pi
from random import choice

import pygame

from src import text
from src.menu import RotatingMenu
from src.event import EventHandler
from src.game import Game
from src.editor import Editor

class Main(EventHandler):
    def __init__(self):
        pygame.init()
        
        self.display = pygame.display.set_mode((960, 540))
        self.clock = pygame.time.Clock()
        
        #Then the custom event handling
        self.events = [      #Arguments:
            'keyDown',         #unicode, key, mod
            'keyUp',           #key, mod
            'mouseMotion',     #pos, rel, buttons
            'mouseButtonDown', #pos, button
            'mouseButtonUp',   #pos, button
            'quit',            #no variables
            ]
        
        self.register(*self.events)
        
        #Then the main menu
        noAction = lambda: None
        menuItems = {
            "Exit": self.on_menu_exit,
            "Options": {
                "Resolution": noAction,
                "FPS Limit": noAction,
            },
            "Start": self.on_menu_game,
            "Levels": noAction,
            "Editor": {
                "New Level": noAction,
                "Load Level": noAction,
            },
        }
        
        self.menu = RotatingMenu(self, x=480, y=270, w=700, h=400, arc=pi, defaultAngle=pi/2., wrap=False, headerText="Mustyqatse", items=menuItems, on_selection=self.menu_select, backText="Back")
        
        self.context = self.menu
    
    def update(self):
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                self.emit('keyDown', e.key, e.mod)
            elif e.type == pygame.KEYUP:
                self.emit('keyUp', e.key, e.mod)
            elif e.type == pygame.MOUSEMOTION:
                self.emit('mouseMotion', e.pos, e.rel, e.buttons)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.emit('mouseButtonDown', e.pos, e.button)
            elif e.type == pygame.MOUSEBUTTONUP:
                self.emit('mouseButtonUp', e.pos, e.button)
            elif e.type == pygame.QUIT:
                self.emit('quit')
            
        self.context.update()
        self.context.draw(self.display)
        
        pygame.display.flip()
        self.clock.tick(60) #Limit FPS
    
    #Menu
    def menu_select(self, menu):
        self.context = menu
    
    def on_menu_game(self):
        game = Game(self)
        game.win = self.win
        game.lose = self.lose
        self.context = game
        game.start()
    
    def menuLevels(self):
        pass
    
    def menuEditor(self):
        editor = Editor(self)
        editor.back = self.menuBack
        self.context = editor
    
    def on_menu_exit(self):
        return sys.exit()
    
    #Options Menu
    def optionsResolution(self):
        pass
    
    def optionsFPSLimit(self):
        pass
    
    #Game
    def win(self):
        self.context = self.menu
        self.menu.header.text = choice(text.on_win)
    
    def lose(self):
        self.context = self.menu
        self.menu.header.text = choice(text.on_lose)

if __name__ == "__main__":
    main = Main()
    while True:
        main.update()