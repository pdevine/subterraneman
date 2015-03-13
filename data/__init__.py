from logging import info as log_info, debug as log_debug
import pygame
import os


# DynamicCachingLoader is an **ABSTRACT** class.  It must be inherited
# from and the subclas MUST implement LoadResource( attname )
class DynamicCachingLoader(dict):
        def __init__(self):
                self._d = {}
        def __getattr__(self, attname):
                try:
                        return self.__dict__[attname]
                except KeyError: 
                        log_info( 'loader got key err' )
                        try:
                                return self._d[attname]
                        except KeyError:
                                self.LoadResource( attname )
                                return self._d[attname]

        def __getitem__(self, key):
                try:
                        return self._d[key]
                except KeyError:
                        self.LoadResource( key )
                        return self._d[key]

	def LoadResource(self, resourceName):
		raise NotImplementedError()

class PngLoader(DynamicCachingLoader):
	def LoadResource(self, resourceName):
		name = os.path.join( 'data', resourceName )
		if not name.endswith('.png'):
			name += '.png'
		try:
			image = pygame.image.load(name)
			if image.get_alpha is None:
				image = image.convert()
			else:
				image = image.convert_alpha()
		except pygame.error, message:
			log_debug( ' Cannot load image: '+ name )
			log_debug( 'Raising: '+ str(message) )
			raise

		self._d[resourceName] = image

class OggLoader(DynamicCachingLoader):
	def LoadResource(self, resourceName):
		name = os.path.join( 'data', resourceName )
		if not name.endswith('.ogg'):
			name += '.ogg'
		class NoneSound:
			def play(self): pass

		if not pygame.mixer or not pygame.mixer.get_init():
			self._d[resourceName] = NoneSound()
			return

		try:
			sound = pygame.mixer.Sound(name)
		except pygame.error, message:
			log_debug( 'Cannot load sound: '+ name)
			raise pygame.error, message
		
		self._d[resourceName] = sound


oggs = OggLoader()
pngs = PngLoader()
