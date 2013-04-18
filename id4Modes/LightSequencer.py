import procgame
from procgame import *
import locale
import random
import sys

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

#setup file structure
curr_file_path = os.path.dirname(os.path.abspath( __file__ ))

class LightSequencer(game.Mode, priority):
    """Independence Day Attract Mode"""
    def __init__(self, game, priority):
        super(LightSequencer, self).__init__(game, priority)
        self.minX = 0
        self.minY = 0
        self.maxX = self.game.config['PRLampConfig']['maxX']            #width of playfield in inches
        self.maxY = self.game.config['PRLampConfig']['maxY']            #height of playfield in inches
        self.lampLists = list()                                         #list of all lampLists that LightSequencer can use
        self.loadAll()                                                  #loads all of the lampLists
        

    def loadAll(self):
        """Loads all desired lampLists and stores them in lampLists"""
        self.test = loadList(self, testList); lampLists.append(self.test)

    def loadList(self, listName):
        self.filename = curr_file_path + "/lampLists/" + listName
        self.lamp_data = {}
        if os.path.exists(self.filename):
            self.lamp_data = yaml.load(open(self.filename, 'r'))
            # check that we got something
            if self.lamp_data:
                print "Found settings. All good"
            else:
                print "No data in lampList"
                self.lamp_data = {}
        else:
            print "No such lampList"
        return

    def mode_started(self):
        pass

    def mode_topmost(self):
        pass

    def mode_stopped(self):
        pass

    def mode_tick(self):
        pass

    def mode_stopped(self):
        pass
