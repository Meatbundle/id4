from procgame import *
import procgame
import locale
import random
import sys
import os
import yaml
import pygame
import uuid
import time
from Effect import *

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

#setup file structure
curr_file_path = os.path.dirname(os.path.abspath( __file__ ))

class LightSequencer(game.Mode):
    """Independence Day Attract Mode"""
    def __init__(self, game, priority):
        super(LightSequencer, self).__init__(game, priority)
        self.minX = 0
        self.minY = 0
        self.maxX = self.game.config['PRLampConfig']['maxX']            #width of playfield in inches
        self.maxY = self.game.config['PRLampConfig']['maxY']            #height of playfield in inches
        self.lampLists = list()                                         #list of all lampLists that LightSequencer can use
        self.sequences = list()                                         #list of delay functions that we can cancel via cancel_delayed if necessary
        self.effects = list()                                           #list of different Effect objects for storing data between calls
        self.runtime = 0                                                #how long until all of currently queued modes are done
        self.loadAll()                                                  #loads all of the lampLists

        '''Everything under this comment is temporary and will be removed when no longer needed'''
        self.counter = 0
        self.black = (0,0,0)
        self.white = (255,255,255)
        self.red = (255,0,0)
        self.drawLights()
        self.play('test', 'TopToBottom', False, 2, 25, 0)
       


    def loadAll(self):
        """Loads all desired lamp lists and stores them in self.lampLists"""
        self.test = self.loadList('testList.yaml'); self.lampLists.append(self.test)
        
    def loadList(self, listName):
        """loads a particular lamp list given by listName"""
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
        return self.lamp_data

    def play(self, listName, effect, overwrite, length, lightTime, repeat=0):
        """docstring
        this function plays a certain effect
        listName: list of lamps to be used for effect. should already be loaded
        effect: which light effect is desired
        overwrite: if true, all other queued effects are cancelled and this one played immediately
        length: how long the sequencer should take to finish the effect (in seconds)
        lightTime: how long each lamp should stay lit once lit (in milliseconds, cannot be greater than 255 and will be set to 255 if passed value is higher)
        repeat: how many times to repeat the effect."""
        for key in self.lampLists:
            if key[listName]:
                self.temp = key[listName]
                self.temp2 = key[listName]
                self.tempName = 'list' + str(uuid.uuid1())
                self.tempDelay = (float(length)/self.maxY)
                self.tempEffect = Effect(self.tempName, self.temp, self.temp2, length, lightTime, repeat, self.tempDelay)

                if overwrite:
                    for x in self.sequences:                   #delete the queue
                        self.cancel_delayed(x)
                    self.sequences = ()
                    self.runtime = 0

                self.sequences.append(self.tempEffect.name)
                self.effects.append(self.tempEffect)
                self.runtime += length * (repeat + 1)

                if effect == 'TopToBottom':
                    self.effects[-1].point1.y = self.maxY
                    self.TopToBottom(self.effects[-1])
                else:
                    print "Not a good effect"
                    del self.sequences[-1]
                    del self.effects[-1]
                    self.runtime -= length * (repeat + 1)
            else:
                print "No lampList found with that name"

    def TopToBottom(self, effect):
        self.counter += 1
        tempList = list()
        if len(effect.lampListRemove) > 0 and effect.repeat == 0:
            for key, value in effect.lampListRemove.iteritems():
                for y, val in effect.lampListRemove[key].iteritems():
                    if val > effect.point1.y:
                        tempList.append(key)
            if len(tempList) > 0:
                for key in tempList:
                    if key in effect.lampListRemove:
                        self.drawLight(key, effect, self.red)
                        del effect.lampListRemove[key]
            self.runtime -=  effect.delay
            effect.point1.y -= 1
            self.delayed_name = self.delay(name= effect.name, event_type=None, delay= effect.delay, handler=self.TopToBottom, param= effect)
        elif len(effect.lampListRemove) <= 0 and effect.repeat > 0:                               #we finished the show, check repeat
            effect.lampListRemove = effect.lampList
            effect.repeat -= 1
            self.TopToBottom(effect)
        else:
            for key in self.sequences:
                if key ==  effect.name:
                    self.sequences.remove(key)
            for key in self.effects:
                if key ==  effect.name:
                    self.effects.remove(key)

    def drawLights(self):
        """test method to draw pattern of lights to make sure they are doing what they are supposed to"""
        self.screen = pygame.display.set_mode((self.maxX * 20, self.maxY * 20))

        self.screen.fill(self.black)
        #pygame.draw.line(self.screen, self.red, (0, 0), (self.maxX * 10, self.maxY * 10))
        for key in self.lampLists:
            if  key['test']:
                for lamp in key['test'].values():
                    pygame.draw.circle(self.screen, self.white, (lamp['x'] * 20, (self.maxY * 20 - lamp['y'] * 20)), 8, 0)
        pygame.display.flip()

    def drawLight(self, key, effect, color):
        if key in effect.lampList:
            effect.lightKeys.append(LightKey(time.time(), key))
            pygame.draw.circle(self.screen, color, (effect.lampList[key]['x'] * 20, (self.maxY * 20 - effect.lampList[key]['y'] * 20)), 8, 0)
            self.recolor_name = self.delay(name=str(time.time()), event_type=None, delay=effect.lightTime/1000, handler=self.recolor, param=effect)
        pygame.display.flip()

    def recolor(self,effect):
        foo = list()
        for key in effect.lightKeys:
            self.tempTime = float(time.time()) - float(self.random)
            if time.time() - self.tempTime >= effect.lightTime/1000:
                pygame.draw.circle(self.screen, self.white, (effect.lampList[key]['x'] * 20, (self.maxY * 20 - effect.lampList[key]['y'] * 20)), 8, 0)
                foo.append(key)
        for key in foo:
            if key in effect.turnOnLights:
                del effect.turnOnLights[key]

    def mode_started(self):
        pass

    def mode_topmost(self):
        pass

    def mode_stopped(self):
        pass

    def mode_tick(self):
        pass