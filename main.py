import sys
from math import pi
from random import choice

import pygame

from src import text
from src.menu import createMenuFromDict
from src.event import EventHandler
from src.game import Game
from src.editor import Editor

class Main(EventHandler):
    def __init__(self):
        pygame.init()
        
        self.display = pygame.display.set_mode((640, 480))
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
            "Exit": self.menuExit,
            "Options": {
                "Resolution": noAction,
                "FPS Limit": noAction,
            },
            "Start": self.menuGame,
            "Levels": noAction,
            "Editor": {
                "New Level": noAction,
                "Load Level": noAction,
            },
        }
        
        self.menu = createMenuFromDict(self, menuItems, self.menuSelect,
                        "Back", 320, 240, 270, pi, pi/2.0, False, "Mustyqatse")
        
        self.context = self.menu
    
    def loop(self):
        while True:
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
            
            pygame.display.flip() #Show the updated scene
            self.clock.tick(60) #Wait a little to keep the fps steady
    
    #Menu
    def menuSelect(self, menu):
        self.context = menu
    
    def menuGame(self):
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
    
    def menuExit(self):
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
    main.loop()
