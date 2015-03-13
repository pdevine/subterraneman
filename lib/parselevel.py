import os.path
import string
import pygame
import tile
import fireball
from avatar import Fuel

class ParseLevel:
    levels = ["level1", "levelA", "level2", "level3", "level4"]

    def parseFile(self, level=1):
        levIndex = (level-1) % len(self.levels)
        filename = os.path.join("levels", self.levels[levIndex])
        f = open(filename + ".sjb", 'r')
        lines = f.readlines()
        f.close()

        tileSprite = 0
        x = 0
        ycount = 0
        maxXcount = 0

        self.startPosition = (0, 0)
        self.sprites = []
        self.events = []
        self.enemies = []
        self.fuels = []

        for y in range(len(lines)):
            line = lines[y]
            line = line.rstrip()
            if line[0] == "#":
                continue

            for x in range(len(line)):
                pos = (x * tile.TILE_X, ycount * tile.TILE_Y)
                if line[x] == "x":
                    if x > 0 and x < len(line)-1 and line[x+1] == ' ':
                        self.sprites.append(tile.Tile(pos, "tile1"))
                    elif x > 0 and line[x-1] == ' ':
                        self.sprites.append(tile.Tile(pos, "tile3"))
                    elif y > 1 and lines[y-1][x] == ' ':
                        self.sprites.append(tile.Tile(pos, "tile4"))
                    elif y < len(lines)-1 and len(lines[y+1])-1 >= x \
                       and lines[y+1][x] == ' ':
                            self.sprites.append(tile.Tile(pos, "tile2"))
                    else:
                        self.sprites.append(tile.Tile(pos, "tilex"))
                    tileSprite += 1
                elif line[x] == "s":
                    self.startPosition = pos
                elif line[x] == "o":
                    self.events.append(tile.Tile(pos, "event", "out"))
                elif line[x] == "l":
                    self.events.append(tile.Tile(pos, "event", "lava"))
                elif line[x] == "f":
                    self.enemies.append(fireball.Fireball(pos, 18))
                elif line[x] == "F":
                    self.enemies.append(fireball.Fireball(pos, 30))
                elif line[x] == "g":
                    self.fuels.append(Fuel(pos))


            maxXcount = max(maxXcount, x)
            ycount += 1

        self.width = maxXcount * tile.TILE_X
        self.height = ycount * tile.TILE_Y


    def __init__(self, level=1):
        self.parseFile(level)

    def getSprites(self):
        return self.sprites

    def getEvents(self):
        return self.events


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    ParseLevel()
    pass


