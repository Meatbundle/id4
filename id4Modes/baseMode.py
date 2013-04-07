
import main

class baseMode(game.Mode):
	"""docstring for baseMode"""
	def __init__(self, game):
		super(baseMode, self).__init__(game, 2)
		self.tilt_layer = dmd.TextLayer(128/2, 7, font_jazz18, "center").set_text("TILT!")
		self.layer = None # Presently used for tilt layer
		self.ball_starting = True

	def mode_started(self):

		# Disable any previously active lamp
		for lamp in self.game.lamps:
			lamp.disable()

		# Turn on the GIs
		# Some games don't have controllable GI's (ie Stern games)
		#self.game.lamps.gi01.pulse(0)
		#self.game.lamps.gi02.pulse(0)
		#self.game.lamps.gi03.pulse(0)
		#self.game.lamps.gi04.pulse(0)

		# Enable the flippers
		self.game.enable_flippers(enable=True)

		# Put the ball into play and start tracking it.
		# self.game.coils.trough.pulse(40)
		self.game.trough.launch_balls(1, self.ball_launch_callback)

		# Enable ball search in case a ball gets stuck during gameplay.
		self.game.ball_search.enable()

		# Reset tilt warnings and status
		self.times_warned = 0;
		self.tilt_status = 0

		# In case a higher priority mode doesn't install it's own ball_drained
		# handler.
		self.game.trough.drain_callback = self.ball_drained_callback

		# Each time this mode is added to game Q, set this flag true.
		self.ball_starting = True

	def ball_launch_callback(self):
		if self.ball_starting:
			self.game.ball_save.start_lamp()
	
	def mode_stopped(self):
		
		# Ensure flippers are disabled
		self.game.enable_flippers(enable=False)

		# Deactivate the ball search logic so it won't search due to no 
		# switches being hit.
		self.game.ball_search.disable()

	def ball_drained_callback(self):
		if self.game.trough.num_balls_in_play == 0:
			# End the ball
			self.finish_ball()


	def finish_ball(self):

		# Turn off tilt display (if it was on) now that the ball has drained.
		if self.tilt_status and self.layer == self.tilt_layer:
			self.layer = None

		self.end_ball()

	def end_ball(self):
		# Tell the game object it can process the end of ball
		# (to end player's turn or shoot again)
		self.game.end_ball()

	def sw_startButton_active(self, sw):
		if self.game.ball == 1:
			p = self.game.add_player()
			self.game.set_status(p.name + " added!")

	def sw_shooterR_open_for_1s(self,sw):
		if self.ball_starting:
			self.ball_starting = False
			ball_save_time = 10
			self.game.ball_save.start(num_balls_to_save=1, time=ball_save_time, now=True, allow_multiple_saves=False)
		#else:
		#	self.game.ball_save.disable()

	# Note: Game specific item
	# Set the switch name to the launch button on your game.
	# If manual plunger, remove the whole section.
	def sw_fireR_active(self, sw):
		if self.game.switches.shooterR.is_active():
			self.game.coils.shooterR.pulse(50)
		

	# Allow service mode to be entered during a game.
	def sw_enter_active(self, sw):
		self.game.modes.add(self.game.service_mode)
		return True

	def sw_tilt_active(self, sw):
		if self.times_warned == 2:
			self.tilt()
		else:
			self.times_warned += 1
			#play sound
			#add a display layer and add a delayed removal of it.
			self.game.set_status("Tilt Warning " + str(self.times_warned) + "!")

	def tilt(self):
		# Process tilt.
		# First check to make sure tilt hasn't already been processed once.
		# No need to do this stuff again if for some reason tilt already occurred.
		if self.tilt_status == 0:
			
			# Display the tilt graphic
			self.layer = self.tilt_layer

			# Disable flippers so the ball will drain.
			self.game.enable_flippers(enable=False)

			# Make sure ball won't be saved when it drains.
			self.game.ball_save.disable()
			#self.game.modes.remove(self.ball_save)

			# Make sure the ball search won't run while ball is draining.
			self.game.ball_search.disable()

			# Ensure all lamps are off.
			for lamp in self.game.lamps:
				lamp.disable()

			# Kick balls out of places it could be stuck.
			if self.game.switches.shooterR.is_active():
				self.game.coils.shooterR.pulse(50)
			if self.game.switches.shooterL.is_active():
				self.game.coils.shooterL.pulse(20)
			self.tilt_status = 1
			#play sound
			#play video