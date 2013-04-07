
class Attract(game.Mode):
    """docstring for AttractMode"""
    def __init__(self, game):
        super(Attract, self).__init__(game, 1)
        self.press_start = dmd.TextLayer(128/2, 7, font_jazz18, "center", opaque=True).set_text("Press Start")
        self.proc_banner = dmd.TextLayer(128/2, 7, font_jazz18, "center", opaque=True).set_text("pyprocgame")
        self.game_title = dmd.TextLayer(128/2, 7, font_jazz18, "center", opaque=True).set_text("Starter")
        self.splash = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(dmd_path+'Splash.dmd').frames[0])
        self.layer = dmd.ScriptedLayer(128, 32, [{'seconds':2.0, 'layer':self.splash}, {'seconds':2.0, 'layer':self.proc_banner}, {'seconds':2.0, 'layer':self.game_title}, {'seconds':2.0, 'layer':self.press_start}, {'seconds':2.0, 'layer':None}])

    def mode_topmost(self):
        pass

    def mode_started(self):
        # Blink the start button to notify player about starting a game.
        self.game.lamps.startButton.schedule(schedule=0x00ff00ff, cycle_seconds=0, now=False)
        # Turn on minimal GI lamps
        # Some games don't have controllable GI's (ie Stern games)
        #self.game.lamps.gi01.pulse(0)
        #self.game.lamps.gi02.disable()


    def mode_stopped(self):
        pass
        
    def mode_tick(self):
        pass

    # Enter service mode when the enter button is pushed.
    def sw_enter_active(self, sw):
        for lamp in self.game.lamps:
            lamp.disable()
        self.game.modes.add(self.game.service_mode)
        return True

    def sw_exit_active(self, sw):
        return True

    # Outside of the service mode, up/down control audio volume.
    def sw_down_active(self, sw):
        volume = self.game.sound.volume_down()
        self.game.set_status("Volume Down : " + str(volume))
        return True

    def sw_up_active(self, sw):
        volume = self.game.sound.volume_up()
        self.game.set_status("Volume Up : " + str(volume))
        return True

    # Start button starts a game if the trough is full.  Otherwise it
    # initiates a ball search.
    # This is probably a good place to add logic to detect completely lost balls.
    # Perhaps if the trough isn't full after a few ball search attempts, it logs a ball
    # as lost?    
    def sw_startButton_active(self, sw):
        if self.game.trough.is_full:
            # Remove attract mode from mode queue - Necessary?
            self.game.modes.remove(self)
            # Initialize game    
            self.game.start_game()
            # Add the first player
            self.game.add_player()
            # Start the ball.  This includes ejecting a ball from the trough.
            self.game.start_ball()
        else: 
            
            self.game.set_status("Ball Search!")
            self.game.ball_search.perform_search(5)
        return True