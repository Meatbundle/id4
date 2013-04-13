import procgame
from procgame import *
import locale
import random
import sys

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

class Attract(game.Mode):
    """Independence Day Attract Mode"""
    def __init__(self, game, priority):
        super(Attract, self).__init__(game, priority)
        #setup animation and text layers for attract mode

    def mode_started(self):
        # Turn on the GIs
        self.game.gi_control("ON")
        '''
        ## lampshows for attract mode
        lampshows = [
            self.game.assets.lamp_topToBottom,
            self.game.assets.lamp_bottomToTop,
            self.game.assets.lamp_topToBottom,
            self.game.assets.lamp_bottomToTop,
            self.game.assets.lamp_fanRight,
            self.game.assets.lamp_fanLeft,
            self.game.assets.lamp_fanRight,
            self.game.assets.lamp_fanLeft,
            self.game.assets.lamp_colors,
            self.game.assets.lamp_colors,
            self.game.assets.lamp_rightToLeft,
            self.game.assets.lamp_leftToRight,
            self.game.assets.lamp_rightToLeft,
            self.game.assets.lamp_leftToRight,
            self.game.assets.lamp_starShots,
            self.game.assets.lamp_starShots,
            self.game.assets.lamp_starShots,
        ]
        self.game.schedule_lampshows(lampshows,True)

        # run an initial pass on the animation loop
        self.run_animation_loop()
        # then kick off the timer to run it after that
        self.timer_countdown()

    def run_animation_loop(self):
        # grab the current index
        indexA = self.myIndex
        # increment the index for the next round
        if self.myIndex < len(self.layers) - 1:
            self.myIndex += 1
        else:
            self.myIndex = 0
        # and use it to grab the second frame
        indexB = self.myIndex
        frameA = self.layers[indexA]
        frameB = self.layers[indexB]

        # new type for the rolling weed animation
        if frameB['type'] == "NONE":
            # tumble weed wipe bits
            anim = self.game.assets.dmd_tumbleweedAttract
            weedFront = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False,frame_time=4)
            weedFront.composite_op = "blacksrc"
            weedBack = self.splash
            tumbleweedWipe = dmd.GroupedLayer(128,32,[weedBack,weedFront])
            weedWait = len(anim.frames) / 15.0
            self.layer = tumbleweedWipe
            self.game.sound.play(self.game.assets.sfx_tumbleWind)
        # two versions of the transition creation to cover if a direction is needed or not
        elif frameB['direction'] != False:
            self.transition = ep.EP_Transition(self,frameA['layer'],frameB['layer'],frameB['type'],frameB['direction'])
        else:
            self.transition = ep.EP_Transition(self,frameA['layer'],frameB['layer'],frameB['type'])

        # reset the timer to 3 for the next go around
        self.timer = 3

    def timer_countdown(self):
        # looping timer to control the animation speed of attract mode
        # can be hurried to the next step by flipper buttons
        self.timer -= 1
        #print "ATTRACT TIMER: " + str(self.timer)
        if (self.timer == 0):
            self.run_animation_loop()
        # come back to the timer - after cancelling any existing delay, just to be sure
        self.cancel_delayed('slideshow_timer')
        self.delay('slideshow_timer', event_type=None, delay=1, handler=self.timer_countdown)

'''
    def sw_flipperLwL_active(self,sw):
        # if going left - bump the index down
        if self.flipperOK:
            self.myIndex -= 2
            self.flipper_action()

    def sw_flipperLwR_active(self,sw):
        if self.flipperOK:
            self.flipper_action()
    '''
    def flipper_action(self):
        if self.slowFlipper:
            self.flipperOK = False
            self.delay(delay=1,handler=self.flip_again)
        # page the attract animation
        self.run_animation_loop()
        # if noisy, play a noise and count it
        attractSounds = 'Yes' == self.game.user_settings['Gameplay (Feature)']['Attract Mode Sounds']
        if self.noisy and attractSounds:
            # play a sound
            self.play_random()
            # increment the count
            self.soundCount += 1
            print "SOUND COUNT: " + str(self.soundCount) + " OF " + str(self.NOISY_COUNT)
            # check if we're done now
            if self.soundCount >= self.NOISY_COUNT:
                # turn the noisy flag off
                self.noisy = False
                # reset the sound count
                self.soundCount = 0
                # delay a re-enable
                self.delay("Noisy",delay=self.NOISY_DELAY,handler=self.noisy_again)

    def flip_again(self):
        self.flipperOK = True
    def noisy_again(self):
        self.noisy = True

    # random sound routine
    def play_random(self,loops=0, max_time=0, fade_ms=0):
        """ """
        if not self.game.sound.enabled: return
        # pick a random key
        key = random.choice(self.game.sound.sounds.keys())
        if len(self.game.sound.sounds[key]) > 0:
            random.shuffle(self.game.sound.sounds[key])
        self.game.sound.sounds[key][0].play(loops,max_time,fade_ms)
        return self.game.sound.sounds[key][0].get_length()
    '''
        
    def mode_topmost(self):
        pass

    def mode_stopped(self):
        pass

    def mode_tick(self):
        pass

    def sw_exit_active(self, sw):
        return True

    # Start button starts a game if the trough is full.  Otherwise it
    # initiates a ball search.
    # This is probably a good place to add logic to detect completely lost balls.
    # Perhaps if the trough isn't full after a few ball search attempts, it logs a ball
    # as lost?

    def sw_startButton_active(self, sw):
        # if both flipper buttons are pressed, power down
        if self.game.switches.flipperLwR.is_active() and self.game.switches.flipperLwL.is_active() and self.game.buttonShutdown:
            sys.exit(69)
        else:
            print "Attract start button got pressed"
            # If the trough is full start a game - if the end of game delay isn't active
            if not self.game.endBusy:
                if self.game.trough.is_full() or self.game.switches.shooterLane.is_active():
                    # kill the lampshow
                    self.game.lampctrl.stop_show()
                    # kill the music in case the 'end of game' song is playing
                    self.stop_music()
                    # Initialize game
                    self.game.start_game()
                else:
                    print "BALL SEARCH"
                    self.game.ball_search.perform_search(1)

	def sw_enter_active(self, sw):
	 	  for lamp in self.game.lamps:
	 	  		lamp.disable()
	 	  self.game.modes.add(self.game.service)
	 	  return true
	 	  
	def sw_left_active(self, sw):
	 	  volume = self.game.sound.volume_down()
	 	  print ("Volume Down : " + str(volume))
	 	  return true
	 	  
	def sw_right_active(self, sw):
	 	  volume = self.game.sound.volume_up()
	 	  print("Volume Up : " + str(volume))
	 	  return true
	 	  
    '''
    def generate_score_frames(self):
        # This big mess generates frames for the attract loop based on high score data.
        # Read the categories
        for category in self.game.highscore_categories:
            title = None # just pre-sets to make the IDE happy
            initLine1 = None
            scoreLine1 = None

            for index, score in enumerate(category.scores):
                score_str = locale.format("%d", score.score, True) # Add commas to the score.

                ## Here's where we make some junk
                ## For the standard high scores
                if category.game_data_key == 'ClassicHighScoreData':
                    ## score 1 is the grand champion, gets its own frame
                    if index == 0:
                        title = ep.EP_TextLayer(128/2, 1, self.game.assets.font_9px_az, "center", opaque=False).set_text("GRAND CHAMPION",color=ep.YELLOW)
                        initLine1 = ep.EP_TextLayer(5, 13, self.game.assets.font_12px_az, "left", opaque=False).set_text(score.inits,color=ep.GREEN)
                        scoreLine1 = dmd.TextLayer(124, 17, self.game.assets.font_7px_bold_az, "right", opaque=False).set_text(score_str)
                        # combine the parts together
                        combined = dmd.GroupedLayer(128, 32, [title, initLine1, scoreLine1])
                        # add it to the stack
                        self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})
                    ## for the second and 4th names set the title and score line 1
                    if index == 1 or index == 3:
                        title = ep.EP_TextLayer(128/2, 1, self.game.assets.font_9px_az, "center", opaque=False).set_text("HIGHEST SCORES",color=ep.ORANGE)
                        initLine1 = ep.EP_TextLayer(5, 12, self.game.assets.font_7px_bold_az, "left", opaque=False).set_text(str(index) + ")" + score.inits,color=ep.BROWN)
                        scoreLine1 = ep.EP_TextLayer(124, 12, self.game.assets.font_7px_bold_az, "right", opaque=False).set_text(score_str,color=ep.BROWN)
                    ## for the other 2 we ad the second line and make a new layer
                    if index == 2 or index == 4:
                        initLine2 = ep.EP_TextLayer(5, 21, self.game.assets.font_7px_bold_az, "left", opaque=False).set_text(str(index) + ")" + score.inits,color=ep.BROWN)
                        scoreLine2 = ep.EP_TextLayer(124, 21, self.game.assets.font_7px_bold_az, "right", opaque=False).set_text(score_str,color=ep.BROWN)
                        combined = dmd.GroupedLayer(128, 32, [title, initLine1, scoreLine1, initLine2, scoreLine2])
                        # add it to the stack
                        self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_NORTH})

                # generate screens for marshall multiball
                if category.game_data_key == 'MarshallHighScoreData' and self.marshallValue == 'Enabled':
                    backdrop = dmd.FrameLayer(opaque=False,frame=self.game.assets.dmd_marshallHighScoreFrame.frames[0])
                    text = str(index+1) + ") " + score.inits + " " + score_str
                    initsLine = dmd.TextLayer(64,22,self.game.assets.font_7px_az,"center",opaque=False).set_text(text)
                    scoreLine = ep.EP_TextLayer(64,14,self.game.assets.font_5px_AZ, "center", opaque=False).set_text("OLD TIME PINBALL",color=ep.GREY)
                    combined = dmd.GroupedLayer(128,32,[backdrop,initsLine,scoreLine])
                    # add it to the stack
                    self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_WIPE,'direction':ep.EP_Transition.PARAM_EAST})

                # generate a screen for the quickdraw high score champ
                if category.game_data_key == 'QuickdrawChampHighScoreData':
                    backdrop = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_quickdrawStill.frames[0])
                    title = ep.EP_TextLayer(80, 2, self.game.assets.font_5px_bold_AZ, "center", opaque=False).set_text("QUICKDRAW CHAMP",color=ep.ORANGE)
                    initLine1 = dmd.TextLayer(80, 7, self.game.assets.font_12px_az, "center", opaque=False).set_text(score.inits)
                    scoreLine1 = ep.EP_TextLayer(80, 22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str + " KILLS",color=ep.RED)
                    combined = dmd.GroupedLayer(128, 32, [backdrop, title, initLine1, scoreLine1])
                    self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})

                # Generate a screen for the showdown champ
                if category.game_data_key == 'ShowdownChampHighScoreData':
                    backdrop = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_dudeShotFullBody.frames[0])
                    backdrop.set_target_position(40,0)
                    title = ep.EP_TextLayer(44, 2, self.game.assets.font_5px_bold_AZ, "center", opaque=False).set_text("SHOWDOWN CHAMP",color=ep.ORANGE)
                    initLine1 = dmd.TextLayer(44, 7, self.game.assets.font_12px_az, "center", opaque=False).set_text(score.inits)
                    scoreLine1 = ep.EP_TextLayer(44, 22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str + " KILLS",color=ep.RED)
                    combined = dmd.GroupedLayer(128, 32, [backdrop, title, initLine1, scoreLine1])
                    self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})

                # Generate a screen for the ambush champ
                if category.game_data_key == 'AmbushChampHighScoreData':
                    backdrop = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_dudeShoots.frames[1])
                    backdrop.set_target_position(-49,0)
                    title = ep.EP_TextLayer(80, 2, self.game.assets.font_5px_bold_AZ, "center", opaque=False).set_text("AMBUSH CHAMP",color=ep.ORANGE)
                    initLine1 = dmd.TextLayer(80, 7, self.game.assets.font_12px_az, "center", opaque=False).set_text(score.inits)
                    scoreLine1 = ep.EP_TextLayer(80, 22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str + " KILLS",color=ep.RED)
                    combined = dmd.GroupedLayer(128, 32, [backdrop, title, initLine1, scoreLine1])
                    self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})

                # Generate a screen for the Tumbleweed Rustler
                if category.game_data_key == 'TumbleweedChampHighScoreData':
                    backdrop = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_tumbleweedLeft.frames[7])
                    backdrop.set_target_position(32,0)
                    title = ep.EP_TextLayer(51, 2, self.game.assets.font_5px_bold_AZ, "center", opaque=False).set_text("TUMBLEWEED RUSTLER",color=ep.ORANGE)
                    initLine1 = dmd.TextLayer(44, 7, self.game.assets.font_12px_az, "center", opaque=False).set_text(score.inits)
                    scoreLine1 = ep.EP_TextLayer(44, 22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str + " WEEDS",color=ep.RED)
                    combined = dmd.GroupedLayer(128, 32, [backdrop,title, initLine1, scoreLine1])
                    self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})

                # Generate a screen for the Town Drunk
                if category.game_data_key == 'TownDrunkHighScoreData':
                    backdrop = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_dmbIdle.frames[1])
                    title = ep.EP_TextLayer(80, 2, self.game.assets.font_5px_bold_AZ, "center", opaque=False).set_text("TOWN DRUNK",color=ep.ORANGE)
                    initLine1 = dmd.TextLayer(80, 7, self.game.assets.font_12px_az, "center", opaque=False).set_text(score.inits)
                    scoreLine1 = ep.EP_TextLayer(80, 22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str + " BEERS",color=ep.RED)
                    combined = dmd.GroupedLayer(128, 32, [backdrop, title, initLine1, scoreLine1])
                    self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})

                # Generate a screen for the Town Drunk
                if category.game_data_key == 'UndertakerHighScoreData':
                    backdrop = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_tombstone.frames[0])
                    title = ep.EP_TextLayer(44, 2, self.game.assets.font_5px_bold_AZ, "center", opaque=False).set_text("UNDERTAKER",color=ep.ORANGE)
                    initLine1 = dmd.TextLayer(44, 7, self.game.assets.font_12px_az, "center", opaque=False).set_text(score.inits)
                    scoreLine1 = ep.EP_TextLayer(44, 22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str + " KILLS",color=ep.RED)
                    combined = dmd.GroupedLayer(128, 32, [backdrop, title, initLine1, scoreLine1])
                    self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})

                # Generate a screen for the Bounty Hunter
                if category.game_data_key == 'BountyHunterHighScoreData':
                    backdrop = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_wantedPoster.frames[0])
                    title = ep.EP_TextLayer(64, 2, self.game.assets.font_5px_bold_AZ, "center", opaque=False).set_text("BOUNTY HUNTER",color=ep.ORANGE)
                    initLine1 = dmd.TextLayer(44, 7, self.game.assets.font_12px_az, "center", opaque=False).set_text(score.inits)
                    scoreLine1 = ep.EP_TextLayer(44, 22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str + " BARTS",color=ep.RED)
                    combined = dmd.GroupedLayer(128, 32, [backdrop, title, initLine1, scoreLine1])
                    self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})

                # Generate a screen for the Combo Champ
                if category.game_data_key == 'ComboChampHighScoreData':
                    backdrop = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_starsBorder.frames[0])
                    title = ep.EP_TextLayer(64, 2, self.game.assets.font_5px_bold_AZ, "center", opaque=False).set_text("COMBO CHAMP",color=ep.ORANGE)
                    initLine1 = dmd.TextLayer(64, 7, self.game.assets.font_12px_az, "center", opaque=False).set_text(score.inits)
                    scoreLine1 = ep.EP_TextLayer(64, 22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str + "-WAY COMBO",color=ep.RED)
                    combined = dmd.GroupedLayer(128, 32, [backdrop, title, initLine1, scoreLine1])
                    self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})

                # Generate a screen for the motherlode champ
                if category.game_data_key == 'MotherlodeChampHighScoreData':
                    backdrop = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_multiballFrame.frames[0])
                    title = ep.EP_TextLayer(64, 2, self.game.assets.font_5px_bold_AZ, "center", opaque=False).set_text("MOTHERLODE CHAMP",color=ep.ORANGE)
                    initLine1 = dmd.TextLayer(64, 7, self.game.assets.font_12px_az, "center", opaque=False).set_text(score.inits)
                    scoreLine1 = ep.EP_TextLayer(64, 22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str,color=ep.RED)
                    combined = dmd.GroupedLayer(128, 32, [backdrop, title, initLine1, scoreLine1])
                    self.layers.append({'layer':combined,'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})

                # Generate a screen for last call
                if category.game_data_key == 'LastCallHighScoreData':
                    backdrop = dmd.FrameLayer(opaque = False, frame=self.game.assets.dmd_bartender.frames[0])
                    title = ep.EP_TextLayer(80,2, self.game.assets.font_5px_bold_AZ, "center",opaque=False).set_text("LAST CALL CHAMP",color=ep.ORANGE)
                    initLine1 = dmd.TextLayer(80,7, self.game.assets.font_12px_az, "center",opaque=False).set_text(score.inits)
                    scoreLine1 = ep.EP_TextLayer(80,22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str,color=ep.RED)
                    combined = dmd.GroupedLayer(128,32,[backdrop,title,initLine1,scoreLine1])
                    self.layers.append({'layer':combined, 'type':ep.EP_Transition.TYPE_PUSH,'direction':ep.EP_Transition.PARAM_SOUTH})

                # Generate a screen for moonlight Champ
                if category.game_data_key == 'MoonlightHighScoreData':
                    backdrop = dmd.FrameLayer(opaque = False, frame=self.game.assets.dmd_moonIntro.frames[10])
                    title = ep.EP_TextLayer(74,2, self.game.assets.font_5px_bold_AZ, "center", opaque = False).set_text("MOONLIGHT CHAMP",color=ep.ORANGE)
                    title.composite_op = "blacksrc"
                    initLine1 = ep.EP_TextLayer(74,7, self.game.assets.font_12px_az, "center",opaque=False).set_text(score.inits,color=ep.CYAN)
                    initLine1.composite_op = "blacksrc"
                    scoreLine1 = ep.EP_TextLayer(74,22, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text(score_str,color=ep.RED)
                    scoreLine1.composite_op = "blacksrc"
                    combined = dmd.GroupedLayer(128,32,[backdrop,title,initLine1,scoreLine1])
                    self.layers.append({'layer':combined, 'type':ep.EP_Transition.TYPE_CROSSFADE,'direction':False})
    '''

    def mode_stopped(self):
        pass
