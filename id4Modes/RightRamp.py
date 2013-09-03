import procgame
from procgame import *
import locale
import random
import sys
from LightSequencer import *

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

class RightRamp(game.Mode):
    """Handles regular play for the left ramp"""
    def __init__(self, game, priority):
        self.game = game
        self.player = self.game.current_player()
        self.hits = 0
        super(RightRamp, self).__init__(game, priority)

    def sw_rightRampExit_active(self, sw):
        if self.player.nextRamp == 'either' or self.player.nextRamp == 'right'
            self.hits += 1
            self.player.rampHits += 1
            self.player.nextRamp = 'right'

        if self.player.rampHits >= self.player.rampHitsRequired
            #start mode
            #self.game.modes.add(self.game.alienAttack)
            #self.game.modes.alienAttack.startMode(self.game)
            self.hits = 0
        else:
            #play animation depending on how many hits have been achieved
            #play sound
            self.player.addPoints(250000)       #points
            #light up correct light based on how many hits have been achieved
            if self.hits == 1
                #light light
                pass

        self.game.lastSwitch = 'rightRampExit'

    def sw_rightRampEnter_active(self, sw):
        if self.game.lastSwitch == 'rightRampEnter'          #shot was unsuccessful
            #play rollback sound
            pass
        else:
            #play enter sound

        self.game.lastSwitch = 'rightRampEnter'
        self.player.addPoints(10000)