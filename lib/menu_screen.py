import events
import pygame
from pygame.locals import *
import data
from game_screen import GameScreen
from intro_screen import IntroScreen

class SimpleSprite(pygame.sprite.Sprite):
	def __init__( self, name, pos, move=False, speed=0 ):
		pygame.sprite.Sprite.__init__(self)

		self.image = data.pngs[name]

		self.rect = self.image.get_rect()
		self.rect.topleft = pos

		self.move = move
		self.speed = speed

	def update( self, timeChange ):
		if self.move:
			self.rect.left -= self.speed

			if self.rect.right < 0:
				self.rect.left = 800


class SimpleButton(pygame.sprite.Sprite):
	def __init__(self, name, pos, callback):
		pygame.sprite.Sprite.__init__(self)

		self.name = name
		self.callback = callback

		font = pygame.font.Font( None, 90 )
		#self.upImage = font.render( name, True, (230, 55, 152) )
		self.upImage = font.render( name, True, (205, 55, 152) )

		font = pygame.font.Font( None, 70 )
		self.downImage = font.render( name, True, (0, 55, 152) )

		#self.upImage = data.pngs[name+'_up']
		#self.downImage = data.pngs[name+'_down']

		self.image = self.upImage
		self.rect = self.image.get_rect()
		self.rect.topleft = pos

	def Press(self):
		self.image = self.downImage
	def Release(self):
		self.image = self.upImage

class Animation(pygame.sprite.Sprite):
	SPEED = 100
	BOUNCE = 1300

        def __init__(self, fname, pos):
		pygame.sprite.Sprite.__init__(self)

                self.images = [
                               data.pngs[fname+'_0'],
                               data.pngs[fname+'_1'],
                               data.pngs[fname+'_2'],
                              ]

		self.image = self.images[0]
		self.rect = self.image.get_rect()
		self.rect.topleft = pos
                self.current = 0
                self.countDown = Animation.SPEED
		self.bounceDir = 0
		self.bounceCount = 0

        def update( self, timeChange ):
                self.countDown -= timeChange
                if self.countDown < 0:
                        self.countDown = Animation.SPEED
                        self.current += 1
                        self.current %= len( self.images )

		
		self.bounceCount -= timeChange
		if self.bounceCount < 0:
			self.bounceCount = Animation.BOUNCE
			if self.bounceDir == -1:
				self.bounceDir = 1
			else:
				self.bounceDir = -1

		self.rect.bottom -= self.bounceDir
                self.image = self.images[ self.current ]


class MainMenu:
	def __init__(self, screen, display):
		self.screen = screen
		self.display = display

		if pygame.joystick.get_count() and \
		   pygame.joystick.Joystick(0).get_init():
			self.joystick = pygame.joystick.Joystick(0)

		pos = (130, 150)

		self.animations = {
			'rotorRightFaceRight': Animation('char3-big_rr_fr', pos),
		}

		self.animation = self.animations['rotorRightFaceRight']

		self.isDone = False
		self.isStarted = False
		self.nextDisplayer = GameScreen
		self.spriteGroup = pygame.sprite.OrderedUpdates()
		#self.spriteGroup = pygame.sprite.RenderUpdates()
		self.bg         = data.pngs['cloud_background']

		self.cloud1 = SimpleSprite( 'cloud1', (350, 350), True, 3 )
		self.spriteGroup.add( self.cloud1 )

		self.cloud2 = SimpleSprite( 'cloud2', (570, 150), True, 2 )
		self.spriteGroup.add( self.cloud2 )

		self.spriteGroup.add( self.animation )

		cx,cy = screen.get_rect().center
		self.choices = [
		                SimpleButton( 'start game', (cx+10,cy-60),
		                              self.Callback_Level ),
		                SimpleButton( 'intro', (cx+10,cy), 
		                              self.Callback_Intro ),
		                SimpleButton( 'exit', (cx+10,cy+100), 
		                              self.Callback_Quit ),
		               ]

		self.curChoice = 0
		for choice in self.choices:
			self.spriteGroup.add( choice )

		self.UpdateCursor()

		self.downPressed = False
		self.upPressed = False



	def Start( self ):
		events.AddListener( self )
		self.isDone = False
		self.isStarted = True
		self.screen.blit( self.bg, (0,0) )
		self.display.flip()

	def Finish( self ):
		self.isDone = True
		self.isStarted = False
		events.RemoveListener( self )

	def Callback_Quit(self):
		self.nextDisplayer = None
		self.Finish()

	def Callback_Intro(self):
		self.nextDisplayer = IntroScreen
		self.Finish()

	def Callback_Level(self):
		self.nextDisplayer = GameScreen
		self.Finish()

	def On_MouseDown(self, event):
		#should be doing this with pointcollide on a spritegroup...
		#but i'm lazy so...
		for s in self.choices:
			#print 'rect', s.rect, 'point', event.pos
			if s.rect.collidepoint( event.pos ):
				s.Press()

	def On_MouseUp(self, event):
		for s in self.choices:
			if s.rect.collidepoint( event.pos ) and \
			   s.image == s.downImage:
				s.callback()
			s.Release()
		self.UpdateCursor()


	def On_KeyDown(self, event):
		if event.key in (K_RETURN, K_SPACE):
			self.choices[self.curChoice].Press()
		elif event.key in (K_UP, K_RIGHT):
	                data.oggs['doomp'].play()
			self.curChoice -= 1
		elif event.key in (K_DOWN, K_LEFT):
	                data.oggs['doomp'].play()
			self.curChoice += 1

		self.curChoice %= len( self.choices )
		self.UpdateCursor()

	def On_KeyUp(self, event):
		if event.key not in (K_RETURN, K_SPACE):
			return

		self.choices[self.curChoice].Release()
		self.choices[self.curChoice].callback()

	def On_JoyButtonDown(self, event):
		if self.joystick.get_button(1):
			self.choices[self.curChoice].Press()

		self.curChoice %= len( self.choices )
		self.UpdateCursor()

	def On_JoyButtonUp(self, event):
		self.choices[self.curChoice].Release()
		self.choices[self.curChoice].callback()

	def On_JoyMotion(self, event):
                axis = self.joystick.get_axis(1)
                if axis > 0.99:
			if not self.downPressed:
	                	data.oggs['doomp'].play()
				self.curChoice += 1
				self.downPressed = True
                elif axis < -0.99:
			if not self.upPressed:
	                	data.oggs['doomp'].play()
				self.curChoice -= 1
				self.upPressed = True
                else:
			self.upPressed = False
			self.downPressed = False

		self.curChoice %= len( self.choices )
		self.UpdateCursor()


	def UpdateCursor(self):
		for choice in self.choices:
			choice.image = choice.downImage

		self.choices[self.curChoice].image = self.choices[self.curChoice].upImage

	def Tick(self, timeChange):
		if not self.isStarted:
			#print 'starting'
			self.Start()
		#clear
		self.spriteGroup.clear( self.screen, self.bg )

		#update
		events.ConsumeEventQueue()
		self.spriteGroup.update( timeChange )
		events.ConsumeEventQueue()

		#draw
		changedRects = self.spriteGroup.draw(self.screen)
		self.display.update( changedRects )

