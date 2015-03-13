import pygame
from pygame.locals import *
import data
import events
from logging import debug as log_debug

GRAVITY_ACCEL = 1

def clamp( src, _min, _max ):
        return min( max( src, _min ), _max )

class Fireball(pygame.sprite.Sprite):
    def __init__(self, position=(0,0), push=80):
        pygame.sprite.Sprite.__init__(self)
        self.start_x = position[0]
        self.start_y = position[1]
        self.current_y = position[1]
        self.images = [
                        data.pngs["ghost"+"_1"],
                        data.pngs["ghost"+"_2"],
                      ]

        self.push = push
        self.velocity = 0

        self.image = self.images[0]
        self.rect = pygame.Rect(self.start_x, self.start_y, 40, 40)
        self.animationSpeed = 100
        self.countDown = self.animationSpeed
        self.current = 0
        self.displayRect = self.rect.move(0,0)


    def NotifyDirtyScreen(self, bgManager):
        pass

    def update(self, timeChange):
        self.countDown -= timeChange
        if self.countDown < 0:
            self.countDown = self.animationSpeed
            #self.current += 1
            #self.current %= len(self.images)
        self.image = self.images[self.current]

        self.velocity += GRAVITY_ACCEL
        push = 0

        if self.current_y > self.start_y:
            push = self.push
            self.current_y = self.start_y

        self.velocity -= push
        #self.velocity = clamp(self.velocity, self.push, -5)

        self.current_y += self.velocity

        self.rect.topleft = (self.start_x, self.current_y)

