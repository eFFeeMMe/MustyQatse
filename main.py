import sys
from math import pi
from random import choice

import pygame

from lib import menu
from lib.game import Game
#from lib.editor import Editor
from lib import text

class Main:
    def __init__(self):
        pygame.init()
        text.loadLanguage("en-US")
        
        self.display = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        
        noAction = lambda: "huh"
        
        m = {
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
        
        self.menu = menu.createFromDictionary(m, self.menuSelect, "Back",
                         320, 240, 270, pi, pi/2.0, False, "Mustyqatse")
        
        #self.editor = Editor()
        #self.editor.back = self.menuBack
        
        self.game = Game()
        self.game.win = self.win
        self.game.lose = self.lose
        
        self.context = self.menu
        
        #Loop
        while True:
            events = pygame.event.get()
            
            self.context.update(events)
            
            self.context.draw(self.display)
            
            pygame.display.flip() #Show the updated scene
            self.clock.tick(90) #Wait a little to keep the fps steady
    
    #Menu
    def menuSelect(self, menu):
        self.context = menu
    
    def menuGame(self):
        self.context = self.game
        self.game.start()
    
    def menuLevels(self):
        pass
    
    def menuEditor(self):
        pass#self.context = self.editor
    
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
        
        self.menu.header.text = choice(text.getSection("WinStrings"))
        self.menu.header.redrawText()
        #self.menuItem2.text = text.getString("Menu", "continue")
        #self.menuItem2.redrawText()
        #self.menuItem0.text = text.getString("Menu", "exitWin")
        #self.menuItem0.redrawText()
    
    def lose(self):
        self.context = self.menu
        
        self.menu.header.text = choice(text.getSection("LoseStrings"))
        self.menu.header.redrawText()
        #self.menuItem2.text = text.getString("Menu", "continue")
        #self.menuItem2.redrawText()
        #self.menuItem0.text = text.getString("Menu", "exitLose")
        #self.menuItem0.redrawText()

if __name__ == "__main__":
    Main()
