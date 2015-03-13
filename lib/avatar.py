import pygame
from pygame.locals import *
import data
import events
import math
from logging import debug as log_debug

GRAVITY_ACCEL = 4
HORIZ_AIR_FRICTION = 0.08
HORIZ_GROUND_FRICTION = 0.2
RIGHT = 1
LEFT = -1

MAX_FUELED_POWER = 10
MAX_UNFUELED_POWER = 5
FULL_FUEL_TANK = 600

def clamp( src, _min, _max ):
	return min( max( src, _min ), _max )

		
def ApplyHorizFriction( velocity, friction ):
	'''This function modifies the velocity variable'''
	if abs(velocity[0]) < 1:
		velocity[0] = 0
	elif velocity[0] < 0:
		velocity[0] += friction
	elif velocity[0] > 0:
		velocity[0] -= friction

class Animation:
	SPEED = 100
	def __init__(self, fname, flip=False):
		self.images = [
		               data.pngs[fname+'_0'],
		               data.pngs[fname+'_1'],
		               data.pngs[fname+'_2'],
		              ]
		if flip:
			self.images = [ pygame.transform.flip(i, True, False) 
			                for i in self.images ]
		self.current = 0
		self.countDown = Animation.SPEED

	def update( self, timeChange ):
		self.countDown -= timeChange
		if self.countDown < 0:
			self.countDown = Animation.SPEED
			self.current += 1
			self.current %= len( self.images )

		return self.images[ self.current ]

class Fuel(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self)
		self.animation = Animation('fuel')

		self.image = self.animation.update(0)
		self.rect = self.image.get_rect()
		self.rect.topleft = pos
		self.displayRect = self.rect.move(0,0) #copy

	def update(self, timeChange):
		self.image = self.animation.update( timeChange )

	def NotifyDirtyScreen(self, bgManager):
		pass


class Avatar(pygame.sprite.Sprite):
	angle = 0.1111 # this is approximately 20 degrees
	horizMultiplier = math.sin(angle)
	vertMultiplier = math.cos(angle)

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

                if pygame.joystick.get_count() and \
                   pygame.joystick.Joystick(0).get_init():
                        self.joystick = pygame.joystick.Joystick(0)

		self.animations = {
		             'death': Animation('char3_death'),
		             'standingRight': Animation('char3_standing'),
		             'standingLeft': Animation('char3_standing', 1),
		             'faceLeft': Animation('char3_fr', 1),
		             'faceRight': Animation('char3_fr'),
		             'fallRight': Animation('char3_fr_falling'),
		             'fallLeft': Animation('char3_fr_falling', 1),
		             'rotorLeftFaceLeft': Animation('char3_rr_fr', 1),
		             'rotorLeftFaceRight': Animation('char3_rr_fl', 1),
		             'rotorRightFaceLeft': Animation('char3_rr_fl'),
		             'rotorRightFaceRight': Animation('char3_rr_fr'),
		                  }

		self.animation = self.animations['faceRight']

		self.image = self.animation.update(0)
		self.animNeedsChange = True
		self.rect = self.image.get_rect()
		self.displayRect = self.rect.move(0,0) #copy
		
		#"Model" attributes
		self.health = 1
		self.fuel = FULL_FUEL_TANK

		#Controller attributes
		self.upPressed = False
		self.downPressed = False
		self.leftPressed = False
		self.rightPressed = False

		#Physics attributes
		self.velocity = [0,0]
		self.maxVelocity = [5,7]
		self.minVelocity = [-5,-10]
		self.facing = RIGHT
		self.rotorDir = 0
		self.walkingPower = 12
		self.maxRotorPower = MAX_FUELED_POWER
		self.idleRotorPower = 3.65
		self.rotorPower = 5
		self.flying = True

		#Level-specific attributes
		self.bgManager = None
		self.terrain   = None
		self.triggers  = None
		self.fuels     = None
		self.enemies   = None
		self.lava      = None

	def __str__(self):
		return 'Avatar(%d,%d)' % self.rect.topleft

	def NewLevel(self, bgManager, terrain, triggers, enemies, fuels, lava):
		self.bgManager = bgManager
		self.terrain   = terrain
		self.triggers  = triggers
		self.fuels     = fuels
		self.enemies   = enemies
		self.lava      = lava

	def Show( self, pos ):
		self.velocity = [0,0]
		self.health = 1
		events.AddListener( self )
		self.rect.topleft = pos	
		events.Fire( 'AvatarBirth', self )

	def Die( self ):
		if self.health == 0:
			return #already dead
		self.health = 0
		self.upPressed = 0
		self.downPressed = 0
		self.leftPressed = 0
		self.rightPressed = 0
		self.animNeedsChange = True
		events.RemoveListener( self )
		events.Fire( 'AvatarDeath', self )

	def LevelUp( self ):
		self.upPressed = 0
		self.downPressed = 0
		self.leftPressed = 0
		self.rightPressed = 0
		self.animNeedsChange = True
		events.RemoveListener( self )
		events.Fire( 'LevelCompletedEvent', self )

	def On_KeyDown(self, event):
		if event.key == K_UP:
			if not self.upPressed:
				self.animNeedsChange = True
				self.upPressed = True
				if not self.flying:
					if self.leftPressed:
						self.RotorLeft()
					elif self.rightPressed:
						self.RotorRight()
				self.flying = True
		elif event.key == K_DOWN:
			if not self.downPressed:
				self.animNeedsChange = True
				self.downPressed = True
				self.maxVelocity[1] += 3
		elif event.key == K_LEFT:
			#log_debug('left pressed')
			self.leftPressed = True
			if self.flying:
				self.RotorLeft()
			else:
				self.facing = LEFT
		elif event.key == K_RIGHT:
			#log_debug('right pressed')
			self.rightPressed = True
			if self.flying:
				self.RotorRight()
			else:
				self.facing = RIGHT
		elif event.key in (K_LCTRL, K_LSHIFT):
			self.TurnAround()

	def On_KeyUp(self, event):
		if event.key == K_UP:
			self.upPressed = False
		elif event.key == K_DOWN:
			if self.downPressed:
				self.animNeedsChange = True
				self.downPressed = False
				self.maxVelocity[1] -= 3
		elif event.key == K_LEFT:
			self.leftPressed = False
			if self.rotorDir == LEFT:
				self.RotorReturn()
		elif event.key == K_RIGHT:
			self.rightPressed = False
			if self.rotorDir == RIGHT:
				self.RotorReturn()


	def On_JoyButtonDown(self, event):
	    	if self.joystick.get_button(1):
			if not self.upPressed:
				self.upPressed = True
				if not self.flying:
					if self.leftPressed:
						self.RotorLeft()
					elif self.rightPressed:
						self.RotorRight()
				self.flying = True
		elif self.joystick.get_button(7) or \
		     self.joystick.get_button(6):
			self.TurnAround()

	def On_JoyButtonUp(self, event):
		self.upPressed = False

	def On_JoyMotion(self, event):
		axis = self.joystick.get_axis(0)
		#print axis
		if axis > 0.95:
			self.rightPressed = True
			if self.flying:
				self.RotorRight()
			else:
				self.facing = RIGHT
		elif axis < -0.95:
			self.leftPressed = True
			if self.flying:
				self.RotorLeft()
			else:
				self.facing = LEFT
		else:
			self.rightPressed = False
			self.leftPressed = False
			if self.rotorDir == RIGHT:
				self.RotorReturn()
			elif self.rotorDir == LEFT:
				self.RotorReturn()

		axis = self.joystick.get_axis(1)
		if axis > 0.95:
			if not self.downPressed:
				self.animNeedsChange = True
				self.downPressed = True
				self.maxVelocity[1] += 3
		elif self.downPressed:
				self.animNeedsChange = True
				self.downPressed = False
				self.maxVelocity[1] -= 3
			

	def update_ChangeAnimation(self):
		r = self.rotorDir
		f = self.facing

		if self.health == 0:
			self.animation = self.animations['death']
		elif not r and f == LEFT:
			if self.leftPressed:
				self.animation = self.animations['faceLeft']
			elif self.downPressed:
				self.animation = self.animations['fallLeft']
			else:
				self.animation = self.animations['standingLeft']
		elif not r and f == RIGHT:
			if self.rightPressed:
				self.animation = self.animations['faceRight']
			elif self.downPressed:
				self.animation = self.animations['fallRight']
			else:
				self.animation =self.animations['standingRight']
		elif r == LEFT and f == LEFT:
			self.animation = self.animations['rotorLeftFaceLeft']
		elif r == LEFT and f == RIGHT:
			self.animation = self.animations['rotorLeftFaceRight']
		elif r == RIGHT and f == LEFT:
			self.animation = self.animations['rotorRightFaceLeft']
		elif r == RIGHT and f == RIGHT:
			self.animation = self.animations['rotorRightFaceRight']

		self.animNeedsChange = False

	def ChangeImage(self, timeChange):
		center = self.rect.center

		self.image = self.animation.update( timeChange )

		self.rect = self.image.get_rect() #candidate for optimization
		self.rect.center = center

	def TurnAround(self):
		self.facing = -self.facing
		self.animNeedsChange = True
	
	def RotorRight(self):
		self.rotorDir = RIGHT
		self.animNeedsChange = True

	def RotorLeft(self):
		self.rotorDir = LEFT
		self.animNeedsChange = True

	def RotorReturn(self):
		#log_debug('rotor return to normal')
		self.rotorDir = 0
		self.animNeedsChange = True

	def BurnFuel(self):
		if self.fuel <= 0:
			self.fuel = 0
			self.maxRotorPower = MAX_UNFUELED_POWER
			self.minVelocity = (self.minVelocity[0], -8)
		else:
			self.fuel -= 1
			if self.fuel == 0:
				log_debug( 'OUT OF FUEL' )
				events.Fire( 'AvatarFuelEmpty', self )

	def AddFuel(self, fuel):
		fuel.kill()
		self.fuel += FULL_FUEL_TANK
		self.maxRotorPower = MAX_FUELED_POWER
		self.minVelocity = (self.minVelocity[0], -10)
		log_debug( 'GOT MORE FUEL' )
		events.Fire( 'AvatarFuelAdd', self )

	def update_LandOnTheGround(self):
		self.RotorReturn()
		self.flying = False
		if self.leftPressed:
			self.facing = LEFT
		elif self.rightPressed:
			self.facing = RIGHT
		events.Fire( 'AvatarLandOnGround', self )

	def update_StepOverSmallBumps(self, limiter):
		'''this will modify limiter.  if a small bump is found,
		it will be deleted from the limiter data structure'''
		#step over small bumps when walking
		BS = 10 #bump size
		#if not self.flying:
		movingLeft = self.velocity[0] < 0
		leftBlocker = limiter.leftSprite
		movingRight = self.velocity[0] > 0
		rightBlocker = limiter.rightSprite

		def smallDistanceBelow(blocker):
			return (self.rect.bottom - blocker.rect.top) < BS
			

		if movingLeft and limiter.leftSprite and \
		   smallDistanceBelow(limiter.leftSprite):
			self.rect.move_ip(self.velocity[0],0)
			limiter.leftSprite = None
		elif movingRight and limiter.rightSprite and \
		   smallDistanceBelow(limiter.rightSprite):
			self.rect.move_ip(self.velocity[0],0)
			limiter.rightSprite = None



	def update(self, timeChange):
		oldRect = self.rect.move(0,0)

		if self.animNeedsChange or \
		   (not self.flying and \
		    not self.leftPressed and not self.rightPressed):
			self.update_ChangeAnimation()

		self.ChangeImage( timeChange )

		vPower = 0
		hPower = 0

		isWalking = self.leftPressed or self.rightPressed


		if self.flying:
			if self.downPressed:
				#rotors are shut off
				self.rotorPower = 0
			elif self.upPressed:
				self.BurnFuel()
				#rotors are being powered
				self.rotorPower = min( self.maxRotorPower,
				                       self.rotorPower+0.5 )
			else:
				#rotors are idly spinning
				self.rotorPower = self.idleRotorPower

			if self.rotorDir:
				vPower = self.vertMultiplier * self.rotorPower
				hPower = self.horizMultiplier*self.rotorPower *\
					 self.rotorDir
			else:
				vPower = self.rotorPower
				hPower = 0
		else:
			#not flying, walking
			if isWalking:
				hPower = self.walkingPower * self.facing

		self.velocity[1] += GRAVITY_ACCEL

		#apply air friction to horizontally stabilize the dude
		if self.flying and not self.rotorDir:
			ApplyHorizFriction( self.velocity, HORIZ_AIR_FRICTION )
		elif not self.flying and not isWalking:
			ApplyHorizFriction( self.velocity, 
			                    HORIZ_GROUND_FRICTION )

		self.velocity[0] += hPower
		self.velocity[1] -= vPower

		self.velocity[0] = clamp(self.velocity[0],
			self.minVelocity[0], self.maxVelocity[0] )
		self.velocity[1] = clamp(self.velocity[1], 
			self.minVelocity[1], self.maxVelocity[1] )

		newRect = oldRect.move( *self.velocity )
		myCollideRect = newRect.inflate(-4,-4)

		trigger = pygame.sprite.spritecollide( self, self.triggers, 0 )

                if trigger:
			if trigger[0].event == "out":
				self.LevelUp()
			elif trigger[0].event == "lava":
				events.Fire( 'AvatarDeath', self )

		fuels = pygame.sprite.spritecollide( self, self.fuels, 0 )
                if fuels:
                	self.AddFuel( fuels[0] )

		#shrink down to collide with enemies, then put it back
		self.rect = myCollideRect
		trigger = pygame.sprite.spritecollide( self, self.enemies, 0 )
		self.rect = oldRect

                if trigger:
			#print "HIT THE FREAKING FIREBALL"
			self.Die()


		limiter = self.Blocked( oldRect, newRect, self.terrain )

		self.rect = newRect
		

		if limiter.bottomSprite and not self.upPressed:
			self.update_LandOnTheGround()

		self.update_StepOverSmallBumps( limiter )

		events.Fire( 'AvatarTerrainCollide', self, limiter )
		if self.upPressed:
			events.Fire( 'AvatarSmoke', self )

		#if self.rect != oldRect:
			#print "SELF:", self
			#print "BLOCKED BY:"
			#print "TOP :", limiter.topSprite
			#print "BOT :", limiter.bottomSprite
			#print "LEF :", limiter.leftSprite
			#print "RGT :", limiter.rightSprite


		if self.rect.bottom > self.lava.GetKillLine():
			self.Die()

		if self.health > 0:
			self.bgManager.NotifyPlayerSpritePos( self.rect )


	def NotifyDirtyScreen(self, bgManager):
		pass

        def Blocked( self, oldRect, newRect, spriteGroup ):
                """See if self would be blocked by sprites in spriteGroup
                if self were to move to newRect (a Rect)
                Tries to change newRect to accommodate the blockers"""
		class BoundingBox:
			def __init__(self):
				self.top = None
				self.right = None
				self.bottom = None
				self.left = None

				self.topSprite = None;
				self.rightSprite = None;
				self.bottomSprite = None;
				self.leftSprite = None;

		def isCloserToCenter( centerY, sprite, limiterSprite ):
			#print 'is ', sprite, 'closer than', limiterSprite, '?'
			#print 'to center:', centerY
			#print '??', abs(sprite.rect.centery-centerY), 'vs', 
			#print abs(limiterSprite.rect.centery-centerY), 'equals',
 			#print abs(sprite.rect.centery-centerY) <\
			       #abs(limiterSprite.rect.centery-centerY)
			return abs(sprite.rect.centery-centerY) <\
			       abs(limiterSprite.rect.centery-centerY)

		yMotion = newRect.y - oldRect.y

                limiter = BoundingBox()

                self.rect = newRect.move( 0,0 )

                colliders = pygame.sprite.spritecollide( self, spriteGroup, 0)

		self.rect = oldRect

		newCenterY = newRect.centery

                for sprite in colliders:

			#BOTTOM Limiter
			collide_top = sprite.rect.top
                        if ( limiter.bottom is None \
                           or collide_top < limiter.bottom ) \
                           and newRect.bottom > collide_top \
                           and oldRect.bottom   <= collide_top:
                                limiter.bottom       = collide_top
				limiter.bottomSprite = sprite

			#TOP Limiter
			collide_bottom = sprite.rect.bottom
                        if ( limiter.top is None \
                           or collide_bottom > limiter.top ) \
                           and newRect.top      < collide_bottom \
                           and oldRect.top       >= collide_bottom:
                                limiter.top        = collide_bottom
                                limiter.topSprite  = sprite

			#RIGHT Limiter
			collide_left = sprite.rect.left
                        if ( limiter.right is None  \
                           or ( collide_left  < limiter.right \
			      or ( collide_left == limiter.right \
			         and isCloserToCenter( newCenterY, sprite, limiter.rightSprite )
			         )
			      )
                           ) \
                           and newRect.right > collide_left \
                           and oldRect.right <= collide_left:
                                limiter.right        = collide_left
                                limiter.rightSprite  = sprite
				#print 'R collision. newrectleft:', newRect.left

			#LEFT Limiter
			#print 'candidate lefty', sprite
			collide_right = sprite.rect.right
                        if ( limiter.left is None \
                           or ( collide_right > limiter.left \
			      or ( collide_right == limiter.left \
			         and isCloserToCenter( newCenterY, sprite, limiter.leftSprite )
			         )
			      )
                           ) \
                           and newRect.left < collide_right \
                           and oldRect.left >= collide_right:
                                limiter.left       = collide_right
                                limiter.leftSprite = sprite
				#print 'L collision. newrectleft:', newRect.left

		if limiter.left:
			newRect.left = limiter.left
		if limiter.right:
			newRect.right = limiter.right
		if limiter.top:
			newRect.top = limiter.top
		if limiter.bottom:
			newRect.bottom = limiter.bottom

		if limiter.left and limiter.right:
			#print 'all colliders', [c.__str__() for c in colliders]
			#print 'L and R collision'
			#which one is closer to the Y center?
			lCenterY = limiter.leftSprite.rect.centery
			rCenterY = limiter.rightSprite.rect.centery
			#print 'L centery', lCenterY
			#print 'R centery', rCenterY
			#print 'centery', newCenterY
			if abs(lCenterY - newCenterY) < abs(rCenterY - newCenterY):
				newRect.left = limiter.left
			else:
				newRect.right = limiter.right

		return limiter

	
