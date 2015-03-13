from avatar import Avatar
import events

class Player:
	'''This is a singleton that should always be around from program start
	until program end.'''
	avatar = None
	levelAchieved = 1

	@classmethod
	def Start(self):
		self.avatar = Avatar()
		events.AddListener( self )
		self.levelAchieved = 1

	@classmethod
	def On_AvatarDeath(self, avatar):
		pass
	@classmethod
	def On_LevelCompletedEvent(self, event):
		self.levelAchieved += 1
