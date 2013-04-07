# Setup logging first thing in case any of the modules log something as they start:
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

import sys
sys.path.append(sys.path[0]+'/../..') # Set the path so we can find procgame.  We are assuming (stupidly?) that the first member is our directory.
import procgame
import pinproc
from procgame import *
from threading import Thread
from random import *
import string
import time
import locale
import math
import copy
import yaml
from modes import *

locale.setlocale(locale.LC_ALL, "") # Used to put commas in the score.


dmd_path = "../shared/dmd/"
sound_path = "../shared/sound/"
font_tiny7 = dmd.font_named("04B-03-7px.dmd")
font_jazz18 = dmd.font_named("Jazz18-18px.dmd")

class Game(game.BasicGame):
	"""docstring for Game"""
	def __init__(self, machine_type):
		super(Game, self).__init__(machine_type)
		self.sound = procgame.sound.SoundController(self)
		self.lampctrl = procgame.lamps.LampController(self)
		self.settings = {}

	def save_settings(self):
		#self.write_settings(user_settings_path)
		pass
		
	def setup(self):
		"""docstring for setup"""
		self.load_config(self.yamlpath)
		#self.load_settings(settings_path, user_settings_path)

		self.setup_ball_search()

		# Instantiate basic game features
		self.attract_mode = modes.attract(self)
		self.base_game_mode = modes.basemode(self)
		# Note - Game specific item:
		# The last parameter should be the name of the game's ball save lamp
		self.ball_save = procgame.modes.BallSave(self, self.lamps.drainShield, 'shooterR')

		trough_switchnames = []
		# Note - Game specific item:
		# This range should include the number of trough switches for 
		# the specific game being run.  In range(1,x), x = last number + 1.
		for i in range(1,7):
			trough_switchnames.append('trough' + str(i))
		early_save_switchnames = ['outlaneR', 'outlaneL']

		# Note - Game specific item:
		# Here, trough6 is used for the 'eject_switchname'.  This must
		# be the switch of the next ball to be ejected.  Some games
		# number the trough switches in the opposite order; so trough1
		# might be the proper switchname to user here.
		self.trough = procgame.modes.Trough(self,trough_switchnames,'trough6','trough', early_save_switchnames, 'shooterR', self.drain_callback)
	
		# Link ball_save to trough
		self.trough.ball_save_callback = self.ball_save.launch_callback
		self.trough.num_balls_to_save = self.ball_save.get_num_balls_to_save
		self.ball_save.trough_enable_ball_save = self.trough.enable_ball_save

		# Setup and instantiate service mode
		self.sound.register_sound('service_enter', sound_path+"menu_in.wav")
		self.sound.register_sound('service_exit', sound_path+"menu_out.wav")
		self.sound.register_sound('service_next', sound_path+"next_item.wav")
		self.sound.register_sound('service_previous', sound_path+"previous_item.wav")
		self.sound.register_sound('service_switch_edge', sound_path+"switch_edge.wav")
		self.sound.register_sound('service_save', sound_path+"save.wav")
		self.sound.register_sound('service_cancel', sound_path+"cancel.wav")
		self.service_mode = procgame.service.ServiceMode(self,100,font_tiny7,[])

		# Setup fonts
		self.fonts = {}
		self.fonts['tiny7'] = font_tiny7
		self.fonts['jazz18'] = font_jazz18

		# Instead of resetting everything here as well as when a user
		# initiated reset occurs, do everything in self.reset() and call it
		# now and during a user initiated reset.
		self.reset()

	def reset(self):
		# Reset the entire game framework
		super(Game, self).reset()

		# Add the basic modes to the mode queue
		self.modes.add(self.attract_mode)
		self.modes.add(self.ball_search)
		self.modes.add(self.ball_save)
		self.modes.add(self.trough)

		# Make sure flippers are off, especially for user initiated resets.
		self.enable_flippers(enable=False)

	# Empty callback just incase a ball drains into the trough before another
	# drain_callback can be installed by a gameplay mode.
	def drain_callback(self):
		pass
		
	def ball_starting(self):
		super(Game, self).ball_starting()
		self.modes.add(self.base_game_mode)
		
	def ball_ended(self):
		self.modes.remove(self.base_game_mode)
		super(Game, self).ball_ended()
		
	def game_ended(self):
		super(Game, self).game_ended()
		self.modes.remove(self.base_game_mode)
		self.set_status("Game Over")
		self.modes.add(self.attract_mode)
		
	def set_status(self, text):
		self.dmd.set_message(text, 3)
		print(text)
	
	def extra_ball(self):
		p = self.current_player()
		p.extra_balls += 1

	def setup_ball_search(self):
		# No special handlers in starter game.
		special_handler_modes = []
		# self.ball_search = procgame.modes.BallSearch(self, priority=100, \
                                     countdown_time=10, coils=self.ballsearch_coils, \
                                     reset_switches=self.ballsearch_resetSwitches, \
                                     stop_switches=self.ballsearch_stopSwitches, \
                                     special_handler_modes=special_handler_modes)
		
def main():
	if len(sys.argv) < 2:
		print("Usage: %s <yaml>"%(sys.argv[0]))
		return
	else:
		yamlpath = sys.argv[1]
		if yamlpath.find('.yaml', 0) == -1:
			print("Usage: %s <yaml>"%(sys.argv[0]))
			return

	config = yaml.load(open(yamlpath, 'r'))
	machine_type = config['PRGame']['machineType']
	config = 0
	game = None
	try:
	 	game = Game(machine_type)
		game.yamlpath = yamlpath
		game.setup()
		game.run_loop()
	finally:
		del game

if __name__ == '__main__': main()
