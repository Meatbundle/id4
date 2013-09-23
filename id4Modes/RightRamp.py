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
        super(RightRamp, self).__init__(game, priority)

    def sw_rightRampExit_active(self, sw):
        if self.player.combo > 1:               #combo timer is active
            self.player.addPoints(combo*1000000)
            self.player.combo += 1
            self.player.cancel_delayed(self.player.comboDelayFunction)
            self.player.comboDelayFunction = delay(name='comboDelayFunction', event_type=None, delay=5, handler='self.player.comboDone()', param=None)

        if self.player.nextRamp == 'either' or self.player.nextRamp == 'right':
            self.player.rRampHits += 1
            self.player.nextRamp = 'left'

        if (self.player.rRampHits+self.player.lRampHits) >= self.player.rampHitsRequired:
            #start mode
            #self.game.modes.add(self.game.alienAttack)
            #self.game.modes.alienAttack.startMode(self.game)
            pass
        else:
            #play animation depending on how many hits have been achieved
            #play sound
            self.player.addPoints(250000)       #points
            #light up correct light based on how many hits have been achieved
            #light light
        self.game.lastSwitch = 'rightRampExit'

    def sw_rightRampEnter_active(self, sw):
        if self.game.lastSwitch == 'rightRampEnter':          #shot was unsuccessful
            #play rollback sound
            pass
        else:
            #play enter sound
            pass

        self.game.lastSwitch = 'rightRampEnter'
        self.player.addPoints(10000)
