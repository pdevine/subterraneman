import events
import pygame
import random
import data
from avatar import LEFT, RIGHT

ROT_DROP = 6 # how many pixels below the top of the avatar rect the rotor looks
NUM_SPARKS = 3
NUM_SMOKES = 1


def vectorSum( v1, v2 ):
	return [ v1[0]+v2[0], v1[1]+v2[1] ]

class EffectManager:
	def __init__(self):
		self._fpsThrottle = False
		self._throttleCountdown = 100
		
	def Start(self, spriteGroup):
		self.spriteGroup = spriteGroup
		events.AddListener( self )
		self.scrapeSounds = [ data.oggs['scrape01'],
		                      data.oggs['scrape02'],
		                      data.oggs['scrape03'], ]
		self.curSound = 0
		self.playingScrape = False
		self.sparkCount = 0

	def Finish( self ):
		events.RemoveListener( self )

	def Throttle(self):
		self._throttleCountdown = 100
		self._fpsThrottle = True
	def CheckThrottle(self):
		if not self._fpsThrottle:
			return False
		self._throttleCountdown -= 1
		if self._throttleCountdown < 0:
			self._fpsThrottle = False
		return True


	def On_AvatarLandOnGround(self, avatar):
		self.playingScrape = False

	def On_AvatarTerrainCollide(self, avatar, colliders):
		'''accepts a reference to the avatar and a "colliders" data
		structure that looks like this
		colliders.
		colliders.topSprite
		colliders.rightSprite
		colliders.bottomSprite
		colliders.leftSprite
		'''
		if self.CheckThrottle():
			return

		#if abs(avatar.velocity[1]) > 1:
			#print 'he is going up. cut out'
			#return #only spark if he's stopped

		sparkDirection = None
		r = avatar.rotorDir
		f = avatar.facing
		aRect = avatar.rect

		if not r:
			if not colliders.topSprite:
				#print 'no top sprite. cutting out'
				return
			sparkDirection = Spark.down
			sparkPosition = aRect.midtop
		elif (r == LEFT and f == LEFT) \
		  or (r == LEFT and f == RIGHT):
			if not colliders.leftSprite:
				return
			sparkDirection = Spark.right
			sparkPosition = (aRect.left , aRect.top + ROT_DROP)
		elif (r == RIGHT and f == LEFT) \
		  or (r == RIGHT and f == RIGHT):
			if not colliders.rightSprite:
				return
			sparkDirection = Spark.left
			sparkPosition = (aRect.right, aRect.top + ROT_DROP)

		self.sparkCount += 1
		if self.sparkCount > 40:
			self.playingScrape = False
			self.sparkCount = 0	

		sparks = []
		for i in range(NUM_SPARKS):
			spark = Spark()
			adjustment = [random.randint(-3,3),random.randint(-3,3)]
			velocity = vectorSum( sparkDirection, adjustment )
			spark.add( self.spriteGroup, sparkPosition, velocity )

		#play sound if not already playing
		if not self.playingScrape:
			self.playingScrape = 1
			self.curSound += 1
			self.curSound %= len( self.scrapeSounds )
			self.scrapeSounds[ self.curSound ].play()

	def On_AvatarSmoke(self, avatar):
		if self.CheckThrottle():
			return
		if not avatar.flying:
			return

		if avatar.fuel <= 0:
			smokeClass = BlackSmoke
		else:
			smokeClass = Smoke

		r = avatar.rotorDir
		f = avatar.facing
		aRect = avatar.rect

		smokePosition = aRect.midbottom
		if (not r and f == LEFT ) \
		  or ( not r and f == RIGHT ):
			smokeDirection = Smoke.down
		elif (r == LEFT and f == LEFT) \
		  or (r == LEFT and f == RIGHT):
			smokeDirection = Smoke.right
			smokePosition = (aRect.centerx , aRect.bottom-ROT_DROP)
		elif (r == RIGHT and f == LEFT) \
		  or (r == RIGHT and f == RIGHT):
			smokeDirection = Smoke.left
			smokePosition = (aRect.centerx, aRect.bottom-ROT_DROP)

		smokePosition = ( smokePosition[0]+random.randint(-5,5),
		                  smokePosition[1] )


		smokes = []
		for i in range(NUM_SMOKES):
			smoke = smokeClass()
			adjustment = [random.randint(-1,1),random.randint(0,3)]
			velocity = vectorSum( smokeDirection, adjustment )
			smoke.add( self.spriteGroup, smokePosition, velocity )


eManager = EffectManager() #SINGLETON - TODO: do this in a less ugly way

class Spark(pygame.sprite.Sprite):
	white = (255,255,255)
	red = (255,0,0)
	yellow = (255,255,0)
	colors = [ white, red, yellow ]
	lifetimeRange = (100,800)
	down = [0,5]
	up = [0,-1]
	left = [-5,0]
	right = [5,0]
	size = (2,2)

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface( self.size )
		self.image.fill( random.choice( self.colors ) )
		self.rect = self.image.get_rect()
		self.displayRect = self.rect.move(0,0)

		self.lifetime = random.randint( *self.lifetimeRange )

	def add( self, spriteGroup, position, velocity ):
		pygame.sprite.Sprite.add(self, spriteGroup)
		self.rect.center = position
		self.velocity = velocity

	def update(self, timeChange):
		self.lifetime -= timeChange
		if self.lifetime < 0:
			self.kill()
			return

		self.rect.move_ip( *self.velocity )

	def NotifyDirtyScreen(self, bgManager):
		pass

class Smoke(Spark):
	size = (4,4)
	white = (255,255,255)
	grey1 = (210,210,200)
	grey2 = (100,100,100)
	colors = [ white, grey1, grey2 ]
	lifetimeRange = (200,3000)
	down = [0,1]
	up = [0,-1]
	left = [-0.1,0]
	right = [0.1,0]

class BlackSmoke(Smoke):
	grey2 = (60,60,60)
	colors = [ grey2 ]
	lifetimeRange = (200,1000)
