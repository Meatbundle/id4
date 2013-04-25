class id4Player(object):
  """Represents a player in the game.
	The game maintains a collection of players in :attr:`GameController.players`."""
	score = 0
	name = None
	extra_balls = 0
	game_time = 0

	def __init__(self, name):
		super(Player, self).__init__()
		self.name = name
