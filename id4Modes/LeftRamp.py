import procgame
from procgame import *
import locale
import random
import sys
from LightSequencer import *

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

class LeftRamp(game.Mode):
    """Handles regular play for the left ramp"""
    def __init__(self, game, priority):
        self.game = game
        self.player = self.game.current_player()
        super(LeftRamp, self).__init__(game, priority)

    def sw_leftRampExit_active(self, sw):
        if self.player.nextRamp == 'either' or self.player.nextRamp == 'left':
            self.player.lRampHits += 1
            self.player.nextRamp = 'right'

        if (self.player.lRampHits + self.player.rRampHits) >= self.player.rampHitsRequired:
            #start mode
            #self.game.modes.add(self.game.alienAttack)
            #self.game.modes.alienAttack.startMode(self.game)
            pass
        else:
            #play animation depending on how many hits have been achieved
            #play sound
            self.player.addPoints(250000)       #points

        self.game.lastSwitch = 'leftRampExit'

    def sw_leftRampEnter_active(self, sw):
        if self.game.lastSwitch == 'leftRampEnter':          #shot was unsuccessful
            #play rollback sound
            pass
        else:
            #play enter sound
            pass

        self.game.lastSwitch = 'leftRampEnter'
        self.player.addPoints(10000)
        
