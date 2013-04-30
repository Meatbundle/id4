## Independence Day Remake
##
## A P-ROC Project by Zachary Stauffer, Copyright 2012
## Built on the PyProcGame Framework from Adam Preble and Gerry Stellenberg
##

#import logging
#logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from procgame import *
import id4Modes
import pinproc
#from assets import *
import pygame
#import highscore
import time
import datetime
import os
import yaml
import copy

curr_file_path = os.path.dirname(os.path.abspath( __file__ ))
## Define the config file locations
user_game_data_path = curr_file_path + "/config/game_data.yaml"
game_data_defaults_path = curr_file_path + "/config/game_data_template.yaml"
settings_defaults_path = curr_file_path + "/config/settings_template.yaml"
user_settings_path = curr_file_path + "/config/user_settings.yaml"
dots_path = curr_file_path + "/dots/"

## Subclass BasicGame to create the main game
class id4Game(game.BasicGame):
    def __init__(self,machineType, fakePinProc = False):
        if (fakePinProc):
            self.fakePinProc = True
            config.values['pinproc_class'] = 'procgame.fakepinproc.FakePinPROC'
        else:
            self.fakePinProc = False
        self.restart = False
       
        # used to prevent the high score entry from restarting the music
        self.soundIntro = False
        self.shutdownFlag = config.value_for_key_path(keypath='shutdown_flag',default=False)
        self.buttonShutdown = config.value_for_key_path(keypath='power_button_combo', default=False)
        self.ballsearch_coils = []
        self.ballsearch_resetSwitches = []
        self.ballsearch_stopSwitches = []

        super(id4Game, self).__init__(machineType)
        self.load_config('c:\p-roc\pyprocgame-master\games\id4\config\id4.yaml')

    def setup(self):
        # Instead of resetting everything here as well as when a user
        # initiated reset occurs, do everything in self.reset() and call it
        # now and during a user initiated reset.
        self.proc.set_dmd_color_mapping([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])

        self.reset()

    def reset(self):
        # game reset stuff - copied in
        """Reset the game state as a slam tilt might."""
        self.ball = 0
        self.old_players = []
        self.old_players = self.players[:]
        self.players = []
        self.current_player_index = 0
        self.modes.modes = []

        # software version number
        self.revision = "1"

        # basic game reset stuff, copied in

        ## init the sound
        self.sound = sound.SoundController(self)
        ## init the lamp controller
        #self.lampctrl = ep.EP_LampController(self)
        ## and a separate one for GI
        #self.GI_lampctrl = ep.EP_LampControllerGI(self)
        ## load all the assets (sound/dots)
        #self.assets = Assets(self)
        ## Set the current song for use with the music method
        #self.current_music = self.assets.music_mainTheme

        # reset score display to mine
        #self.score_display = cc_modes.ScoreDisplay(self,0)

        #self.showcase = ep.EP_Showcase(self)

        # last switch variable for tracking
        self.lastSwitch = None
        # last ramp for combo tracking
        self.lastRamp = None

        self.ballStarting = False
        self.status = None
        # squelch flag used by audio routines to turn down music without stopping it
        #self.squelched = False
        
        # status display ok ornot
        self.statusOK = False
        self.endBusy = False

        """docstring for setup"""
        # and settings Game settings
        print "Loading game settings"
        self.load_settings(settings_defaults_path, user_settings_path)

        # set the volume per the settings
        self.sound.music_offset = self.user_settings['Sound']['Music volume offset']
        print "Setting initial offset: " + str(self.sound.music_offset)
        self.volume_to_set = (self.user_settings['Sound']['Initial volume'] / 10.0)
        print "Setting initial volume: " + str(self.volume_to_set)
        self.sound.set_volume(self.volume_to_set)
        self.previousVolume = self.volume_to_set

        #self.immediateRestart = "Enabled" == self.user_settings['Gameplay (Feature)']['Fast Restart After Game']

        # Set the balls per game per the user settings
        self.balls_per_game = self.user_settings['Machine (Standard)']['Balls Per Game']
        # Flipper pulse strength
        self.flipperPulse = self.user_settings['Machine (Standard)']['Flipper Pulse']
        
        # set up the ball search
        self.setup_ball_search()

        # set up the trough mode
        trough_switchnames = ['troug1', 'trough2', 'trough3', 'trough4']
        early_save_switchnames = ['outlaneR', 'outlaneL']
        self.trough = id4Modes.Trough(self, trough_switchnames,'trough1','troughVUKOpto', early_save_switchnames, self.switches.shooterLane, self.ball_drained)
        # set the ball save callback
        self.trough.ball_save_callback = self.ball_saved

        #High Score Setup
        '''self.highscore_categories = []

        cat = highscore.HighScoreCategory()
        cat.game_data_key = 'ClassicHighScoreData'
        self.highscore_categories.append(cat)

        for category in self.highscore_categories:
            category.load_from_game(self)
        '''
        #Initialize all of the modes
        #Create the objects for the basic modes
        self.attract = id4Modes.Attract(game=self,priority=4)
        self.lightSeq = id4Modes.LightSequencer(game=self,priority=4)
        '''
        self.base = cc_modes.BaseGameMode(game=self,priority=4)
        
        # basic ramp & loop handling
        self.right_ramp = cc_modes.RightRamp(game=self,priority=10)
        self.left_ramp = cc_modes.LeftRamp(game=self,priority=10)
        self.center_ramp = cc_modes.CenterRamp(game=self,priority=10)
        self.left_loop = cc_modes.LeftLoop(game=self,priority=10)
        self.right_loop = cc_modes.RightLoop(game=self,priority=10)
        # combos should always register - so they ride above the switch block
        self.combos = cc_modes.Combos(game=self,priority=14)

        

        self.bonus_lanes = cc_modes.BonusLanes(game=self,priority=17)

        self.match = cc_modes.Match(game=self,priority=20)
        '''
        # set up an array of the modes
        # this subset is used for clearing displays on command
        self.id4Modes = [self.attract,
                         self.lightSeq]
        '''
                         self.base,
                         self.right_ramp,
                         self.right_loop,
                         self.center_ramp,
                         self.left_loop,
                         self.left_ramp,
                         self.saloon,
                         self.mine,
                         self.bad_guys,
                         self.save_polly,
                         self.skill_shot,
                         self.gm_multiball,
                         self.interrupter,
                         self.bonus_lanes,
                         self.stampede,
                         self.high_noon,
                         self.drunk_multiball,
                         self.quickdraw,
                         self.showdown,
                         self.ambush,
                         self.gunfight,
                         self.badge,
                         self.bionic,
                         self.bart,
                         self.move_your_train,
                         self.bank_robbery,
                         self.river_chase,
                         self.cva,
                         self.marshall_multiball,
                         self.moonlight]
'''
        self.id4Modes.sort(lambda x, y: y.priority - x.priority)
        # Add in the base modes that are active at start
        #self.modes.add(self.lamp_control)
        #self.modes.add(self.trough)
        #self.modes.add(self.ball_search)
        self.modes.add(self.attract)
        self.modes.add(self.lightSeq)
        #self.modes.add(self.switch_tracker)
        #self.modes.add(self.score_display)

    def start_game(self):
        # remove the attract mode
        self.modes.remove(self.attract_mode)
        # kill the attract mode song fade delay just in case
        #self.interrupter.cancel_delayed("Attract Fade")
        # tick up the audits
        #self.game_data['Audits']['Games Started'] += 1
        # tick up all the switch hit tracking by one
        '''for switch in self.game_data['SwitchHits']:
            self.game_data['SwitchHits'][switch] +=1
            print switch + " " + str(self.game_data['SwitchHits'][switch])'''
        # turn off all the ligths
        for lamp in self.lamps:
            if 'gi' not in lamp.name:
                lamp.disable()
        # run the start ball from parent
        super(id4Game,self).start_game()
        # Add the first player
        self.add_player()
        #self.order_mobs()
        # reset the music volume
        self.volume_to_set = (self.user_settings['Sound']['Initial volume'] / 10.0)
        self.sound.set_volume(self.volume_to_set)
        # load the base game mode
        self.modes.add(self.base)
        # Start the ball.  This includes ejecting a ball from the trough.
        self.start_ball()
        # add the ability to see the status
        self.statusOK = True

    def start_ball(self):
        # reset the autoplunger count
        self.trough.balls_to_autoplunge = 0
        # run the start_ball from proc.game.BasicGame
        super(id4Game, self).start_ball()
        #if len(self.players) > 1 and not self.interrupter.hush:
        #    self.interrupter.display_player_number()

    def create_player(self,name):
        player = id4Player(name)
        return player

    def game_started(self):
        self.log("GAME STARTED")
        # run the game_started from proc.game.BasicGame
        super(id4Game, self).game_started()
        # Don't start_ball() here, since Attract does that after calling start_game().

    def shoot_again(self):
        #self.interrupter.shoot_again()
        pass

    def ball_starting(self):
        # restore music, just in case
        self.restore_music()
        print "BALL STARTING - number " + str(self.ball)
        ## run the ball_starting from proc.gameBasicGame
        super(id4Game, self).ball_starting()
        self.ballStarting = True
        # turn on the GI
        self.gi_control("ON")
        # reset the pop bumper count
        #self.set_tracking('bumperHits',0)
        # reset the player bonus
        #self.set_tracking('bonus', 0)
        # enable the ball search
        self.ball_search.enable()
        # turn the flippers on
        self.enable_flippers(True)
        # reset the tilt status
        #self.set_tracking('tiltStatus',0)
        '''# reset the stack levels
        for i in range(0,7,1):
            self.set_tracking('stackLevel',False,i)'''

        # launch a ball, unless there is one in the shooter lane already
        if not self.switches.shooterLane.is_active():
            self.trough.launch_balls(1) # eject a ball into the shooter lane
        else:
            self.trough.num_balls_in_play += 1

        # if skillshot is already running for some lame reason, remove it
        if self.skill_shot in self.modes:
            self.skill_shot.unload()
        # add skill shot.
        self.modes.add(self.skill_shot)
        # and all the other modes
        self.base.load_modes()
        # update the lamps
        self.lamp_control.update()

    def ball_saved(self):
        if self.trough.ball_save_active:
            # tell interrupter jones to show the ball save
            #print "GAME THINKS THE BALL WAS SAVED"
            # the ball saved display
            #self.interrupter.ball_saved()
            # kill the skillshot if it's running
            if self.skill_shot in self.modes:
                self.skill_shot.unload()
            # if the ball was saved, we need a new one
            #self.trough.launch_balls(1)

    # Empty callback just incase a ball drains into the trough before another
     # drain_callback can be installed by a gameplay mode.
    def ball_drained(self):
        print "BALL DRAINED ROUTINE RUNNING"
        # if we're not ejecting a new ball, then it really drained
        if not self.trough.launch_in_progress:
            # New abort for Last Call
            if self.last_call in self.modes:
                self.last_call.ball_drained()
                return
         
            # Tell every mode a ball has drained by calling the ball_drained function if it exists
            if self.trough.num_balls_in_play == 0:
                # kill all the display layers
                for mode in self.id4Modes:
                    if getattr(mode, "clear_layer", None):
                        mode.clear_layer()
                print "BALL DRAINED IS KILLING THE MUSIC"
                self.sound.stop_music()

            ## and tell all the modes the ball drained no matter what
            for mode in self.modes:
                if getattr(mode, "ball_drained", None):
                    mode.ball_drained()

    def ball_ended(self):
        """Called by end_ball(), which is itself called by base.trough_changed."""
        self.log("BALL ENDED")
        # reset the tilt
        self.set_tracking('tiltStatus',0)
        # stop the music
        print "BALL ENDED IS KILLING THE MUSIC"
        # disable ball save
        self.trough.disable_ball_save()

        self.sound.stop_music()
        # unload the base add on modes
        self.base.remove_modes()

        # then call the ball_ended from proc.game.BasicGame
        self.end_ball()


    def end_ball(self):
        """Called by the implementor to notify the game that the current ball has ended."""

        self.ball_end_time = time.time()
        # Calculate ball time and save it because the start time
        # gets overwritten when the next ball starts.
        self.ball_time = self.get_ball_time()
        self.current_player().game_time += self.ball_time

        if self.current_player().extra_balls > 0:
            self.current_player().extra_balls -= 1
            #set the ball starting flag to help the trough not be SO STUPID
            self.ballStarting = True
            print "Starting extra ball - remaining extra balls:" + str(self.current_player().extra_balls)
            self.shoot_again()
            return
        if self.current_player_index + 1 == len(self.players):
            self.ball += 1
            self.current_player_index = 0
        else:
            self.current_player_index += 1
        if self.ball > self.balls_per_game:
            self.end_game()
        else:
            self.start_ball() # Consider: Do we want to call this here, or should it be called by the game? (for bonus sequence)

    def game_reset(self):
        print("RESETTING GAME")
        # save existing data for audits thus far
        self.save_game_data()
        # unload all the base modes, just in case
        self.base.remove_modes()
        # unload all the base mode
        self.modes.remove(self.base)
        # and the skillshot
        self.modes.remove(self.skill_shot)
        # throw up a message about restarting
        #self.interrupter.restarting()
        # lot the end of the game
        self.log("GAME PREMATURELY ENDED")
        # set the Balls in play to 0
        self.trough.num_balls_in_play = 0
        # restart the game
        self.start_game()


    def game_ended(self):
        self.log("GAME ENDED")
        ## call the game_ended from proc.game.BasicGame
        super(id4Game, self).game_ended()

        # remove the base game mode
        # self.modes.remove(self.base)
        # turn the flippers off
        self.enable_flippers(enable=False)

        # divert to the match before high score entry - unless last call is disabled
        '''lastCall = 'Enabled' == self.user_settings['Gameplay (Feature)']['Last Call Mode']
        if lastCall:
            self.modes.add(self.match)
            self.match.run_match()
        else:
            self.run_highscore()'''

    def run_highscore(self):
        # Remove the base mode here now instead - so that it's still available for last call
        self.modes.remove(self.base)

    def highscore_entry_ready_to_prompt(self, mode, prompt):
        '''banner_mode = game.Mode(game=self, priority=8)
        textLine1 = "GREAT JOB"
        textLine2 = (prompt.left.upper())
        textLayer1 = dmd.TextLayer(58, 5, self.assets.font_10px_AZ, "center", opaque=False).set_text(textLine1)
        textLayer1.composite_op = "blacksrc"
        textLayer2 = dmd.TextLayer(58, 18, self.assets.font_10px_AZ, "center", opaque=False).set_text(textLine2)
        textLayer2.composite_op = "blacksrc"
        combined = dmd.GroupedLayer(128,32,[textLayer1,textLayer2])
        banner_mode.layer = dmd.ScriptedLayer(width=128, height=32, script=[{'seconds':2.0, 'layer':combined}])
        banner_mode.layer.on_complete = lambda: self.highscore_banner_complete(banner_mode=banner_mode, highscore_entry_mode=mode)
        self.modes.add(banner_mode)
        # play the music - if it hasn't started yet
        if not self.soundIntro:
            self.soundIntro = True
            duration = self.sound.play(self.assets.music_highScoreLead)
            self.interrupter.delayed_music_on(wait=duration,song=self.assets.music_goldmineMultiball)'''

    def highscore_banner_complete(self, banner_mode, highscore_entry_mode):
        '''self.modes.remove(banner_mode)
        highscore_entry_mode.prompt()'''

    def highscore_entry_finished(self, mode):
        '''self.modes.remove(mode)
        # Stop the music
        self.sound.stop_music()
        # turn off the sound intro flag
        self.soundIntro = False
        # set a busy flag so that the start button won't restart the game right away
        if not self.immediateRestart:
            print "Immediate restart is disabled, killing start button"
            self.endBusy = True
        else:
            print "Immediate restart is enabled"
        # re-add the attract mode
        self.modes.add(self.attract_mode)
        # play a quote
        duration = self.sound.play(self.assets.quote_goodbye)

        # play the closing song
        self.interrupter.closing_song(duration)'''

    def setup_ball_search(self):
        # No special handlers in starter game.
        self.ball_search = id4Modes.BallSearch(self, priority=100,countdown_time=15, coils=self.ballsearch_coils,reset_switches=self.ballsearch_resetSwitches,stop_switches=self.ballsearch_stopSwitches)

    def schedule_lampshows(self,lampshows,repeat=True):
        self.scheduled_lampshows = lampshows
        self.scheduled_lampshows_repeat = repeat
        self.scheduled_lampshow_index = 0
        self.start_lampshow()

    def start_lampshow(self):
        self.lampctrl.play_show(self.scheduled_lampshows[self.scheduled_lampshow_index], False, self.lampshow_ended)

    def lampshow_ended(self):
            self.scheduled_lampshow_index = self.scheduled_lampshow_index + 1
            if self.scheduled_lampshow_index == len(self.scheduled_lampshows):
                if self.scheduled_lampshows_repeat:
                    self.scheduled_lampshow_index = 0
                    self.start_lampshow()
                else:
                    # Finished playing the lampshows and not repeating...
                    pass
            else:
                self.start_lampshow()

    def set_status(self,derp):
        self.status = derp

    '''### Player stats and progress tracking

    def set_tracking(self,item,amount,key="foo"):
        p = self.current_player()
        if key != "foo":
            p.player_stats[item][key] = amount
        else:
            p.player_stats[item] = amount

    # call from other modes to set a value
    def increase_tracking(self,item,amount=1,key="foo"):
        ## tick up a stat by a declared amount
        p = self.current_player()
        if key != "foo":
            p.player_stats[item][key] += amount
            return p.player_stats[item][key]
        else:
            p.player_stats[item] += amount
            # send back the new value for use
            return p.player_stats[item]

     # call from other modes to set a value
    def decrease_tracking(self,item,amount=1,key="foo"):
        ## tick up a stat by a declared amount
        p = self.current_player()
        if key != "foo":
            p.player_stats[item][key] -= amount
            return p.player_stats[item][key]
        else:
            p.player_stats[item] -= amount
            # send back the new value for use
            return p.player_stats[item]

    # return values to wherever
    def show_tracking(self,item,key="foo"):
      p = self.current_player()
      if key != "foo":
            return p.player_stats[item][key]
      else:
            return p.player_stats[item]

    # invert tracking only used for bonus lanes, wise? dunno
    def invert_tracking(self,item):
        p = self.current_player()
        p.player_stats[item].reverse()

    def stack_level(self,level,value,lamps=True):
        # just a routine for setting the stack level
        self.set_tracking('stackLevel',value,level)
        # that also calls a base lamp update
        if lamps:
            print "Stack set updating the lamps"
            self.lamp_control.update()
        else:
            print "Stack set not updating thh lamps"

    '''
    # score with bonus
    def addPoints(self, points):
        """Convenience method to add *points* to the current player."""
        p = self.current_player()
        p.score += points
     
    '''
    ## bonus stuff

    # extra method for adding bonus to make it shorter when used
    def add_bonus(self,points):
        p = self.current_player()
        p.player_stats['bonus'] += points
        print p.player_stats['bonus']

    def calc_time_average_string(self, prev_total, prev_x, new_value):
        prev_time_list = prev_x.split(':')
        prev_time = (int(prev_time_list[0]) * 60) + int(prev_time_list[1])
        avg_game_time = int((int(prev_total) * int(prev_time)) + int(new_value)) / (int(prev_total) + 1)
        avg_game_time_min = avg_game_time/60
        avg_game_time_sec = str(avg_game_time%60)
        if len(avg_game_time_sec) == 1:
            avg_game_time_sec = '0' + avg_game_time_sec

        return_str = str(avg_game_time_min) + ':' + avg_game_time_sec
        return return_str

    def calc_number_average(self, prev_total, prev_x, new_value):
        avg_game_time = int((prev_total * prev_x) + new_value) / (prev_total + 1)
        return int(avg_game_time)'''

    ### Standard flippers
    def enable_flippers(self, enable):
        """Enables or disables the flippers AND bumpers."""

        for flipper in self.config['PRFlippers']:
            self.logger.info("Programming flipper %s", flipper)
            main_coil = self.coils[flipper+'Main']
            self.logger.info("Enabling WPC style flipper")
            hold_coil = self.coils[flipper+'Hold']
            switch_num = self.switches[flipper].number

            drivers = []
            if enable:
                drivers += [pinproc.driver_state_pulse(main_coil.state(), self.flipperPulse)]
                drivers += [pinproc.driver_state_pulse(hold_coil.state(), 0)]
            self.proc.switch_update_rule(switch_num, 'closed_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)

            drivers = []
            if enable:
                drivers += [pinproc.driver_state_disable(main_coil.state())]
                drivers += [pinproc.driver_state_disable(hold_coil.state())]

            self.proc.switch_update_rule(switch_num, 'open_nondebounced', {'notifyHost':False, 'reloadActive':False}, drivers, len(drivers) > 0)

            if not enable:
                main_coil.disable()
                hold_coil.disable()

        self.enable_bumpers(enable)

    # controls for music volume

    def squelch_music(self):
        if not self.squelched:
            self.squelched = True
            self.previousVolume = pygame.mixer.music.get_volume()
            volume = self.previousVolume / 6
            pygame.mixer.music.set_volume(volume)

    def restore_music(self):
        if self.squelched:
            self.squelched = False
            pygame.mixer.music.set_volume(self.previousVolume)

    def music_on(self,song=None,caller="Not Specified",slice=0,execute=True):
        '''# if given a slice number to check - do that
        if slice != 0:
            stackLevel = self.show_tracking('stackLevel')
            # if there are balls in play and nothing active above the set slice, then kill the music
            if True not in stackLevel[slice:] and self.trough.num_balls_in_play != 0:
                pass
            else:
                print "Music stop called by " + str(caller) + " But passed - Busy"
                execute = False

        if execute:
            # if a song is passed, set that to the active song
            if song:
                print str(caller) + " changed song to " + str(song)
                self.current_music = song
            # if not, just re-activate the current
            else:
                print str(caller) + " restarting current song"
                # then start it up
            self.sound.play_music(self.current_music, loops=-1)'''
        pass

    # switch blocker load and unload - checks to be sure if it should do what it is told
    def switch_blocker(self,function,caller):
        '''if function == 'add':
            print "Switch Blocker Add Call from " + str(caller)
            if self.switch_block not in self.modes:
                print "Switch Blocker Added"
                self.modes.add(self.switch_block)
            else:
                print "Switch Blocker Already Present"
        elif function == 'remove':
            print "Switch Blocker Remove Call from " + str(caller)
            stackLevel = self.show_tracking('stackLevel')
            if True not in stackLevel[2:]:
                print "Switch Blocker Removed"
                self.modes.remove(self.switch_block)
            else:
                print "Switch Blocker NOT removed due to stack level"
                pass'''

    def volume_up(self):
       ''' """ """
        if not self.sound.enabled: return
        #print "Current Volume: " + str(self.sound.volume)
        setting = self.user_settings['Sound']['Initial volume']
        if setting <= 9:
            setting += 1
            #print "new math value: " + str(self.sound.volume)
            self.sound.set_volume(setting / 10.0)
            #print "10 value: " + str(self.sound.volume*10)
            #print "Int value: " + str(int(self.sound.volume*10))
        return setting'''

    def volume_down(self):
       ''' """ """
        if not self.sound.enabled: return
        #print "Current Volume: " + str(self.sound.volume)
        setting = self.user_settings['Sound']['Initial volume']
        if setting >= 2:
            setting -= 1
            #print "new math value: " + str(self.sound.volume)
            self.sound.set_volume(setting / 10.0)
            #print "10 value: " + str(self.sound.volume*10)
            #print "Int value: " + str(int(self.sound.volume*10))
        return setting'''

    def load_settings(self, template_filename, user_filename,restore=False):
        """Loads the YAML game settings configuration file.  The game settings
       describe operator configuration options, such as balls per game and
       replay levels.
       The *template_filename* provides default values for the game;
       *user_filename* contains the values set by the user.

       See also: :meth:`save_settings`
       """
        self.user_settings = {}
        self.settings = yaml.load(open(template_filename, 'r'))
        if os.path.exists(user_filename) and not restore:
            self.user_settings = yaml.load(open(user_filename, 'r'))
            # check that we got something
            if self.user_settings:
                print "Found settings. All good"
            else:
                print "Settings broken, all bad, defaulting"
                self.user_settings = {}
        #
        if restore:
            print "Restore Forced - Loading user settings skipped"

        for section in self.settings:
            for item in self.settings[section]:
                if not section in self.user_settings:
                    self.user_settings[section] = {}
                    if 'default' in self.settings[section][item]:
                        self.user_settings[section][item] = self.settings[section][item]['default']
                    else:
                        self.user_settings[section][item] = self.settings[section][item]['options'][0]
                elif not item in self.user_settings[section]:
                    if 'default' in self.settings[section][item]:
                        self.user_settings[section][item] = self.settings[section][item]['default']
                    else:
                        self.user_settings[section][item] = self.settings[section][item]['options'][0]

        if restore:
            print "Restore - Saving settings"
            self.save_settings()


    def save_settings(self):
        super(id4Game,self).save_settings(user_settings_path)

    def remote_load_settings(self,restore=False):
        self.load_settings(settings_defaults_path, user_settings_path,restore)
        
    def create_player(self, name):
		"""Instantiates and returns a new instance of the :class:`id4Player` class with the
		name *name*.
		This method is called by :meth:`add_player`.
		"""
		return id4Player(name)
