"""this mode handles the jackpots for the F18 Attack mode, which is started by shooting the loops a certain number of times.
It starts with the right loop being lit, then alternates between loops with each successful loop shot. This is a 2 ball MB.
Balls can be locked in the alien head, which doubles the value of the jackpot for one jackpot. Ball is kicked out of vuk
after successful shot, and the alien head reopens after 5 seconds for a relock of the ball."""

import procgame
from procgame import *
import locale
import random
import sys
from LightSequencer import *

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

class F18Attack(game.Mode):
    """Independence Day Attract Mode"""
    def __init__(self, game, priority):
        super(F18Attack, self).__init__(game, priority)

    def startMode(self, game):
        self.player = self.game.current_player()
        self.player.f18Started = True
        #setup animations
        #play light show
        #play sound clip


    def sw_leftOrbTop_active(self, sw):
        if self.game.lastSwitch == 'leftOrbBottom':     #make sure we came from bottom to top
            self.game.coils.rightControlGate.pulsed_patter(on_time=10, off_time=10, run_time=500, now=True)        #open control gates for .5 seconds
            self.game.coils.leftControlGate.pulsed_patter(on_time=10, off_time=10, run_time=500, now=True)        #open control gates for .5 seconds
            if self.game.player.nextLoop == 'left':     #if this is correct loop, score jackpot
                if self.player.ballLocked == True:      #is a ball locked in the tunnel? if so, jackpot is doubled
                    self.player.addPoints(self.player.f18JackpotValue * 2)
                    self.game.coils.vuk.pulse(25)       #pulse vuk to eject ball
                    #open alien head after delay
                    #anim for double jackpot
                else:
                    self.player.addPoints(self.player.f18JackpotValue)
                    #anim for jackpot
                #playsound (same sound for jack or double jack)
                self.player.nextLoop = 'right'
                self.player.f18HitsForComplete -= 1
        self.game.lastSwitch = 'leftOrbTop'
        return game.switchStop

    def sw_leftOrbBottom_active(self, sw):
        self.game.lastSwitch = 'leftOrbBottom'
        self.player.addPoints(self.game.switchPoints)                #points for switch closure
        #play intro to loop sound
        return game.switchStop

    def sw_rightOrbTop_active(self, sw):
        if self.game.lastSwitch == 'rightOrbBottom':     #make sure we came from bottom to top
            self.game.coils.rightControlGate.pulsed_patter(on_time=10, off_time=10, run_time=500, now=True)        #open control gates for .5 seconds
            self.game.coils.leftControlGate.pulsed_patter(on_time=10, off_time=10, run_time=500, now=True)        #open control gates for .5 seconds
            if self.player.nextLoop == 'right':     #if this is correct loop, score jackpot
                if self.player.ballLocked == True:      #is a ball locked in the tunnel? if so, jackpot is doubled
                    self.player.addPoints(self.player.f18JackpotValue * 2)
                    self.game.coils.vuk.pulse(25)       #pulse vuk to eject ball
                    #open alien head after delay
                    #anim for double jackpot
                else:
                    self.player.addPoints(self.player.f18JackpotValue)
                    #anim for jackpot
                #playsound (same sound for jack or double jack)
                self.player.nextLoop = 'left'
                self.player.f18HitsForComplete -= 1
        self.game.lastSwitch = 'rightOrbTop'
        return game.switchStop

    def sw_rightOrbBottom_active(self, sw):
        self.game.lastSwitch = 'rightOrbBottom'
        self.player.addPoints(self.game.switchPoints)                #points for switch closure
        #play intro to loop sound
        return game.switchStop

    def sw_vukSideEnter_active(self, sw):
        #if all ready a ball in vuk, eject it
        if self.player.ballLocked == True:
            self.game.coils.vuk.pulse(25)
            #play anim that ball is locked
        else:
            self.player.ballLocked = True
        self.game.lastSwitch = 'vukSideEnter'
        #play sound
        #close alien head

    def mode_stopped(self):
        self.player.f18hitsRequired = (self.game.f18HitsToStart * 2)    #next time will take 2x as many shots to start mode. change to setting
        self.player.nextLoop = 'right'                 #reset loop to start with for jackpot
        if self.player.f18HitsForCompete <= 0:                      #we have completed this mode
            self.player.f18Complete = True
