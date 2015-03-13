import pygame
import os
import data

TILE_X = 40
TILE_Y = 40

class Tile(pygame.sprite.Sprite):
    def __init__(self, position=(0,0), type="tile1", event=None):
        pygame.sprite.Sprite.__init__(self)

        (x, y) = position

        self.image = data.pngs[type]
        self.rect = pygame.Rect(x, y, TILE_X, TILE_Y)
        self.event = event

    def __str__(self):
        return 'Tile(%d,%d)' % self.rect.topleft

    def update(self):
        pass

if __name__ == "__main__":
    pass
