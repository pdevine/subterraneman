import pygame
from pygame.locals import *
import menu_screen
from logging import info as log_info, root
import events
from inspect import isclass
from player import Player
from effects import eManager
import data


RESOLUTION = (800,600)
TARGET_FPS = 40

def main():

	try:
                import psyco
                psyco.full()
        except Exception, e:
                log_info( "no psyco for you!"+ str(e) )


	try:
		import sys
		if 'debug' in sys.argv[1]:
			root.setLevel(0)
	except Exception, e:
		root.setLevel(100)
			

	pygame.init()
	screen = pygame.display.set_mode(RESOLUTION)
	pygame.display.set_caption( 'Subterraneman: Jeopardy Below' )
	pygame.display.set_icon(data.pngs["icon"])



	clock = pygame.time.Clock()

	if pygame.joystick.get_count():
		joystick = pygame.joystick.Joystick(0)
		joystick.init()

	pygame.event.clear()

	displayer = menu_screen.MainMenu(screen, pygame.display)
	Player.Start()

	oldfps = TARGET_FPS
	while True:
		timeChange = clock.tick(TARGET_FPS)
		newfps = int( clock.get_fps() )
		if newfps < (TARGET_FPS-2) and not eManager._fpsThrottle:
			log_info( 'throttling the effects due to low FPS' )
			log_info( 'FPS:' + str(newfps) )
			eManager.Throttle()

		remainingEvents = pygame.event.get()
		for event in remainingEvents:
			if event.type == QUIT:
                                return
#                        elif event.type == KEYDOWN and event.key == K_ESCAPE:
#                                return
                        elif event.type == KEYDOWN:
                        	#print 'firing key down'
				events.Fire( 'KeyDown', event )
			elif event.type == KEYUP:
				events.Fire( 'KeyUp', event )
                        elif event.type == MOUSEBUTTONDOWN:
                                events.Fire( 'MouseDown', event )
                        elif event.type == MOUSEBUTTONUP:
                                events.Fire( 'MouseUp', event )
			elif event.type == JOYBUTTONDOWN:
				#print "firing joy down"
				events.Fire( 'JoyButtonDown', event )
			elif event.type == JOYBUTTONUP:
				events.Fire( 'JoyButtonUp', event )
			elif event.type == JOYAXISMOTION:
				#print "firing joy motion"
				events.Fire( 'JoyMotion', event )

	
		#log_info( 'calling tick' )
		displayer.Tick( timeChange )

		if displayer.isDone:
			log_info( 'displayer is done' )
			displayer = displayer.nextDisplayer
			#print 'got disp', displayer
			if not displayer:
				log_info( 'no next displayer. quitting' )
				return

			if isclass( displayer ):
				displayer = displayer(screen, pygame.display)


if __name__ == '__main__':
	main()
