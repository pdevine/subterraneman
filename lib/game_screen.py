import events
import pygame
from pygame.locals import *
import data
from logging import info as log_info, debug as log_debug
from player import Player
from parselevel import ParseLevel
from scrollGroup import ScrollSpriteGroup
from scroll_bgmanager import BackgroundManager
from effects import eManager

import cutscenes

class SimpleSprite(pygame.sprite.Sprite):
	def __init__(self, name, pos):
		pygame.sprite.Sprite.__init__(self)

		self.image = data.pngs[name]

		self.rect = self.image.get_rect()
		self.rect.topleft = pos

class Lava(SimpleSprite):
	ANIM_SPEED = 100
	def __init__(self):
		SimpleSprite.__init__(self, 'lava', (0,0) )
		self.speed = 4
		self.counter = self.ANIM_SPEED
		self.displayRect = self.rect.move(0,0)
		self.rect.inflate_ip( 10,10 )
		self.updateCounter = 0
	def Start( self, pos ):
		self.rect.topleft = pos
	def GetKillLine(self):
		return self.rect.top + 10
	def update( self, timeChange ):
		if self.rect.top < 0:
			log_info( "Lava past the top!!!" )
			self.kill()
			return
		self.counter -= timeChange
		self.updateCounter += 1
		if self.updateCounter >= 4:
			self.updateCounter = 0
			#print 'moving lava to', self.rect.top
			self.counter = self.ANIM_SPEED
			self.rect.top -= self.speed

	def NotifyDirtyScreen(self, bgManager):
		screenRect = bgManager.GetOffsetScreenRect()
		self.rect.centerx = screenRect.centerx
		

class GameScreen:
	def __init__(self, screen, display, level=1):
		self.screen = screen
		self.display = display

		self.isDone = False
		self.isStarted = False
		self.nextDisplayer = None
		self.keydown = False

		self.level = level

	def Start( self ):
		self.level = Player.levelAchieved
		level = ParseLevel( self.level )
		self.tile_sprites = pygame.sprite.Group()
		for tile in level.sprites:
			self.tile_sprites.add( tile )

		self.event_sprites = pygame.sprite.Group()
		for event in level.events:
			self.event_sprites.add( event )

		#self.enemies = level.enemies

		background = pygame.Surface( (level.width, level.height) )
		off_black = (40,10,0)
		background.fill( off_black )
		self.tile_sprites.draw( background )
		#self.enemy_sprites.draw( background )

		self.bgManager = BackgroundManager( self.screen, background )

		self.lavaGroup = ScrollSpriteGroup( self.bgManager )
		self.terrainGroup = ScrollSpriteGroup( self.bgManager )
		self.fuelGroup = ScrollSpriteGroup( self.bgManager )
		self.effectsGroup = ScrollSpriteGroup( self.bgManager )
		self.avatarGroup = ScrollSpriteGroup( self.bgManager )

		pos = self.bgManager.rect.bottomleft
		pos = (pos[0], pos[1] - 20)
		self.lava = Lava()
		self.lava.Start( pos )
		self.lavaGroup.add( self.lava )

		events.AddListener( self )
		self.avatar = Player.avatar
		self.avatar.NewLevel(self.bgManager, level.sprites,
				     level.events, level.enemies, 
				     self.fuelGroup,
				     self.lava)
		self.avatar.Show( level.startPosition )
		self.avatarGroup.add( self.avatar )

		for enemy in level.enemies:
			self.terrainGroup.add( enemy )

		for fuel in level.fuels:
			self.fuelGroup.add( fuel )

		self.isDone = False
		self.isStarted = True
		self.deathPause = 2000
		self.inDeathPause = False
		self.bgManager.BlitSelf( self.screen )
		self.display.flip()

		eManager.Start( self.effectsGroup )
		data.oggs['game_song'].play( -1 )

	def Finish( self ):
		self.lavaGroup.empty()
		self.terrainGroup.empty()
		self.fuelGroup.empty()
		self.effectsGroup.empty()
		self.avatarGroup.empty()
		events.RemoveListener( self )
		self.isDone = True
		self.isStarted = False
		data.oggs['game_song'].fadeout( 1200 )
		eManager.Finish()

	def On_AvatarDeath(self, event):
		log_debug( 'setting death cutscene' )
		self.nextDisplayer = cutscenes.Death(self)
		self.inDeathPause = True

	def On_LevelCompletedEvent(self, event):
		nextLevel = self.level + 1
		log_debug( 'setting next cutscene %d'%nextLevel )
		self.nextDisplayer = cutscenes.GetNext(self, nextLevel)
		#print self, 'just set nextD to ', self.nextDisplayer
		self.Finish()

	def On_KeyDown(self, event):
		if event.key == K_q:
			self.keydown = True

	def On_KeyUp(self, event):
		if event.key == K_q:
			self.keydown = False
			self.Finish()

	def Tick(self, timeChange):
		if not self.isStarted:
			log_info( 'starting' )
			self.Start()
		elif self.inDeathPause:
			self.deathPause -= timeChange
			if self.deathPause < 0:
				self.Finish()

		#clear
		self.terrainGroup.clear( self.screen )
		self.fuelGroup.clear( self.screen )
		self.effectsGroup.clear( self.screen )
		self.avatarGroup.clear( self.screen )
		self.lavaGroup.clear( self.screen )


		#update
		events.ConsumeEventQueue()
		self.avatarGroup.update( timeChange ) #must go first!
		if not self.inDeathPause:
			self.fuelGroup.update( timeChange )
			self.terrainGroup.update( timeChange )
			self.lavaGroup.update( timeChange )
		self.effectsGroup.update( timeChange )
		events.ConsumeEventQueue()

		#draw
		changedRects = self.avatarGroup.draw(self.screen)
		changedRects += self.terrainGroup.draw(self.screen)
		changedRects += self.effectsGroup.draw(self.screen)
		changedRects += self.fuelGroup.draw(self.screen)
		changedRects += self.lavaGroup.draw(self.screen)
		self.display.update( changedRects )


