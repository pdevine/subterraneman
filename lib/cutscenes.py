import events
import pygame
from pygame.locals import *
import data
from logging import debug as log_debug
import os

black_rect = pygame.Surface( (800, 80) )
black_rect.fill( (0,0,0) )
white = (255,255,255)
red = (255,0,0)
chop = (156,132,152)
subt = (50,55,182)
time_for_dialogue = 2500

class Dialogue(pygame.sprite.Sprite):
	def __init__(self, text, color):
		global black_rect
		pygame.sprite.Sprite.__init__(self)

		self.image = black_rect.copy()
		self.rect = self.image.get_rect()
		self.rect.topleft = (0,520)

		font = pygame.font.Font( None, 40 )
		txtImage = font.render( text, True, color )
		txtRect = txtImage.get_rect()
		txtRect.centerx = self.rect.centerx
		txtRect.centery = self.rect.height//2

		self.image.blit( txtImage, txtRect )


class Cutscene:
	def __init__(self, screen, display, background, dialogues):
		self.screen = screen
		self.display = display

		self.isDone = False
		self.isStarted = False
		self.keyDown = False

		self.nextDisplayer = None

		self.spriteGroup = pygame.sprite.RenderUpdates()
		self.bg         = background

		self.dialogues = dialogues

		self.curDialogue = 0
		self.timeSinceLastDialogue = 0
		self.spriteGroup.add( self.dialogues[self.curDialogue] )

	def SetNextDisplayer( self, nextDisplayer ):
		self.nextDisplayer = nextDisplayer


	def Start( self ):
		events.AddListener( self )
		self.isDone = False
		self.isStarted = True
		self.screen.blit( self.bg, (0,0) )
		self.display.flip()

	def Finish( self ):
		self.isDone = True
		self.curDialogue = 0
		self.isStarted = False
		events.RemoveListener( self )
		#self.spriteGroup.kill()
		self.spriteGroup.empty()

	def On_KeyDown(self, event):
		self.keyDown = True

	def On_KeyUp(self, event):
		if not self.keyDown:
			return

		self.keyDown = False

		if event.key == K_q:
			self.Finish()
		else:
			self.Skip()

	def On_JoyButtonDown(self, event):
		self.keyDown = True

	def On_JoyButtonUp(self, event):
		if not self.keyDown:
			return

		self.keyDown = False
		self.Skip()

	def Skip(self):
		self.spriteGroup.remove( self.dialogues[self.curDialogue] )
		self.timeSinceLastDialogue = 0
		self.curDialogue += 1
		try:
			newDialog = self.dialogues[self.curDialogue]
		except IndexError:
			self.Finish()
			return
		self.spriteGroup.add( newDialog )

	def Tick(self, timeChange):
		if not self.isStarted:
			log_debug( 'cutscene starting' )
			self.Start()

		self.timeSinceLastDialogue += timeChange

		#clear
		self.spriteGroup.clear( self.screen, self.bg )

		#update
		events.ConsumeEventQueue()
		self.spriteGroup.update( timeChange )
		events.ConsumeEventQueue()

		#draw
		changedRects = self.spriteGroup.draw(self.screen)
		self.display.update( changedRects )

		if self.timeSinceLastDialogue > time_for_dialogue:
			self.Skip()



class Death(Cutscene):
	def __init__(self, prevDisplayer):
		dialogues = [
			     Dialogue( 'Chopper-Dude! You died!', subt ),
			     Dialogue( 'I know, dude.', chop ),
			     Dialogue( "I'm sorry I failed you.", chop ),
			     Dialogue( "Whatevs.", subt ),
			     Dialogue( "You're not mad?", chop ),
			     Dialogue( "Not my prolly, dude.", subt ),
			     Dialogue( "Wanna play some foosball?", subt ),
			    ]
		bg = data.pngs['death_background']
		Cutscene.__init__( self, prevDisplayer.screen, 
		                   prevDisplayer.display, bg, dialogues )

		from menu_screen import MainMenu
		self.nextDisplayer = MainMenu


FINAL_TEXT = [ 'That was the last level. You win.' ]

def GetNext(prevDisplayer, level):
	colors = {'white': white, 'chopperdude': chop, 'subt': subt, 'red':red}
	color = white
	screen = prevDisplayer.screen
	display = prevDisplayer.display

	try:
		bg = data.pngs['cutscene%02d' % level]
		dialogueFile = file( os.path.join('data','dialogue%02d'%level) )
		dialogues = []
		for line in dialogueFile:
			line = line.strip()
			if line.startswith('#'):
				color = colors[line[1:]]
			else:
				dialogues.append( Dialogue(line, color) )
		from game_screen import GameScreen
		nextDisplayer = GameScreen( screen, display, level )

	except Exception, ex:
		print "GOT EXCEPTION", ex
		bg = data.pngs['win_background']
		dialogues = [ Dialogue(blurb, white) for blurb in FINAL_TEXT ]

		from menu_screen import MainMenu
		nextDisplayer = MainMenu

	cs = Cutscene( screen, display, bg, dialogues )
	cs.SetNextDisplayer( nextDisplayer )
	return cs
