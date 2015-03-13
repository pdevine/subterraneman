import os
import sys
import pygame

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.insert(0, libdir)

import parselevel

from pygame.locals import *

class LevelViewer:
    def __init__(self, scren):
        self.screen = screen

        self.tiles = parselevel.ParseLevel().sprites

        self.tile_sprites = pygame.sprite.Group()
        for tile in self.tiles:
            self.tile_sprites.add(tile)

        self.bg = pygame.Surface((1600, 5000))
        self.done = False
        self.x_pos = 0
        self.y_pos = 0

        self.tile_sprites.draw(self.bg)

        pygame.key.set_repeat(100, 40)
        self.joy = None
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()

    def run(self):
        while not self.done:
            self.draw()
            self.handleEvents()

    def draw(self):
        rect = pygame.Rect(self.x_pos, self.y_pos, 800, 600)
        self.screen.blit(self.bg, self.screen.get_rect(), rect)
        pygame.display.flip()

    def handleEvents(self):
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == USEREVENT:
                nextFrame = True
            elif event.type == KEYDOWN:
                if event.key == K_DOWN:
                    self.y_pos += 10
                elif event.key == K_UP:
                    self.y_pos -= 10
                elif event.key == K_RIGHT:
                    self.x_pos += 10
                elif event.key == K_LEFT:
                    self.x_pos -= 10
                elif event.key == K_q:
                    self.done = True
            elif event.type == JOYAXISMOTION:
                x = self.joy.get_axis(0)
                if x > 0.5:
                    self.x_pos += 10
                elif x < -0.5:
                    self.x_pos -= 10

                y = self.joy.get_axis(1)
                if y > 0.5:
                    self.y_pos += 10
                elif y < -0.5:
                    self.y_pos -= 10
                #print y


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    LevelViewer(screen).run()

