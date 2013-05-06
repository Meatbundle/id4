import procgame
from procgame import *
import locale
import random
import sys
from LightSequencer import *

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

class LeftOrbit(game.Mode):
    """Independence Day Attract Mode"""
    def __init__(self, game, priority):
        self.player = self.game.current_player()
        super(LeftOrbit, self).__init__(game, priority)

    def sw_leftOrbTop_active(self, sw):
        if self.game.lastSwitch == 'leftOrbBottom':
            self.player.f18hits += 1
            self.game.coils.leftControlGate.pulsed_patter(on_time=10, off_time=10, run_time=500, now=True)        #open control gate for .5 seconds, ball should end up in pops
            if self.player.f18hits >= f18hitsrequired:
                #start mode
                self.game.modes.add(self.game.f18Attack)
                self.game.modes.f18Attack.startMode(self.game)
            else:
                #play advance animation depending on how many hits have been achieved
                #play sound
                self.player.addPoints(250000)       #points

        self.game.lastSwitch = 'leftOrbTop'

    def sw_leftOrbBottom_active(self, sw):
        self.game.lastSwitch = 'leftOrbBottom'
        self.player.addPoints(10000)
        #play sound??
