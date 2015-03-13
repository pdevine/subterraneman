import events
import pygame
from pygame.locals import *
import data

black_rect = pygame.Surface( (800, 80) )
black_rect.fill( (0,0,0) )

from cutscenes import Cutscene, Dialogue

white = (255,255,255)
w = white
lblue = (100,100,255)
chop = (156,132,152)
subt = (0,55,152)

class IntroScreen(Cutscene):
	def __init__(self, screen, display):
		background = data.pngs['intro_background']

		dialogues = [
		 Dialogue( 'The planet Dirt.', w ),
		 Dialogue( 'Long ago, Zebu, leader of the Diantologists',w),
		 Dialogue( 'captured his enemies, the Bormons,', w ),
		 Dialogue( 'and brought them here to extract their souls.',w ),
		]

		Cutscene.__init__(self, screen, display, background, dialogues)
		self.nextDisplayer = Intro2

class Intro2(Cutscene):
	def __init__(self, screen, display):
		# volcano image goes here
		background = data.pngs['intro_background_1']

		dialogues = [
		 Dialogue( 'Zebu\'s method of extraction was ingenious.', w ),
		 Dialogue( 'Place the Bormons in a giant magical volcano', w ),
		 Dialogue( 'and use its awesome destructive powers', w ),
		 Dialogue( 'to do his ill will.', w ),
		]
		Cutscene.__init__(self, screen, display, background, dialogues)
		self.nextDisplayer = Intro3

class Intro3(Cutscene):
	def __init__(self, screen, display):
		# sjb and chopper dude image go here
		background = data.pngs['intro_background_2']

		dialogues = [
		 Dialogue( 'Subterraneman, being a dude, tried to', w ),
		 Dialogue( 'halt the nefarious plot.', w ),
		 Dialogue( 'And you went in to save him...', w ),
		 Dialogue( 'Subterraneman! What happened?', chop ),
		 Dialogue( '...dude.', subt ),
		 Dialogue( "You're hurt!", chop ),
		 Dialogue( '...take my prop... dude.', subt ),
		 Dialogue( '...run.  ...there is no time.', subt ),
		 Dialogue( "Diantologist spirits... and below...!", subt ),
		 Dialogue( "Subterraneman?", chop ),
		 Dialogue( "...jeopardy below...  uuugh...*", subt ),
		 Dialogue( "no... SUBTERRANEMAN!", chop ),
		]

		Cutscene.__init__(self, screen, display, background, dialogues)
		#avoid circular import
		from menu_screen import MainMenu
		self.nextDisplayer = MainMenu

