from procgame import *
import procgame
import locale
import random
import sys
import os
import yaml
import pygame
import uuid
from datetime import *
from Effect import *

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

#setup file structure
curr_file_path = os.path.dirname(os.path.abspath( __file__ ))

class LightSequencer(game.Mode):
    """this class automates the playing of lights in several different patterns"""
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
        if lightTime > 255:
            print "lightTime too high, setting to 255"
            lightTime = 255
        
        for key in self.lampLists:
            if key[listName]:
                self.temp = key[listName]
                self.tempName = 'list' + str(uuid.uuid1())
                self.tempDelay = (float(length)/self.maxY)
                self.tempEffect = Effect(self.tempName, self.temp, length, lightTime, repeat, self.tempDelay)

                if overwrite:
                    for x in self.sequences:                   #delete the queue
                        self.cancel_delayed(x)
                    self.sequences = ()
                    self.runtime = 0

                self.sequences.append(self.tempEffect.name)
                self.effects.append(self.tempEffect)
                self.tempDelay = self.runtime
                self.runtime += length * (repeat + 1)

                if effect == 'topToBottom':
                    self.effects[-1].point1.y = self.maxY
                    self.delayed_name = self.delay(name=self.effects[-1].name, event_type=None, delay=self.tempDelay, handler=self.topToBottom, param=self.effects[-1])
                elif effect == 'bottomToTop':
                    self.effects[-1].point1.y = 0
                    self.delayed_name = self.delay(name=self.effects[-1].name, event_type=None, delay=self.tempDelay, handler=self.bottomToTop, param=self.effects[-1])
                elif effect == 'leftToRight':
                    self.effects[-1].point1.x = 0
                    self.delayed_name = self.delay(name=self.effects[-1].name, event_type=None, delay=self.tempDelay, handler=self.leftToRight, param=self.effects[-1])
                elif effect == 'rightToLeft':
                    self.effects[-1].point1.x = self.maxX
                    self.delayed_name = self.delay(name=self.effects[-1].name, event_type=None, delay=self.tempDelay, handler=self.rightToLeft, param=self.effects[-1])
                elif effect == 'diagBottomLeftToRight':
                    self.effects[-1].point1.x = 0
                    self.effects[-1].point1.y = 1
                    self.effects[-1].point2.x = 1
                    self.effects[-1].point2.y = 0
                    self.delayed_name = self.delay(name=self.effects[-1].name, event_type=None, delay=self.tempDelay, handler=self.diagBottomLeftToRight, param=self.effects[-1])
                elif effect == 'diagBottomRightToLeft':
                    self.effects[-1].point1.x = self.maxX - 2
                    self.effects[-1].point1.y = 0
                    self.effects[-1].point2.x = self.maxX
                    self.effects[-1].point2.y = 2
                    self.delayed_name = self.delay(name=self.effects[-1].name, event_type=None, delay=self.tempDelay, handler=self.diagBottomRightToLeft, param=self.effects[-1])
                    print "running diagBottomRightToLeft"
                elif effect == 'blink':
                    self.blink(self.effects[-1])
                else:
                    print "Not a good effect"
                    del self.sequences[-1]
                    del self.effects[-1]
                    self.runtime -= length * (repeat + 1)
            else:
                print "No lampList found with that name"

    def topToBottom(self, effect):
        '''Starts at top of playfield and lights all lamps from top to bottom for effect.lightTime millisceonds, then repeats if required'''
        self.counter = 0
        #process lamps that haven't been processed yet
        for key in effect.lampList:
            if key.processed == False:
                self.counter += 1
                if key.y > effect.point1.y:
                    key.processed = True
                    self.game.lamps[key.name].pulse(effect.lightTime)
                    self.runtime -=  effect.delay
                    
                    #remove all below on final version
                    self.drawLight(key.name, effect, self.red)

        #test to see if any lights are left and if not, do we need to repeat?
        if self.counter == 0:                                #if true, all lamps have been processed this go around
            for key in effect.lampList:
                key.processed = False      #reset flag
            if effect.repeat > 0:
                effect.repeat -= 1
                effect.point1.y = self.maxY
                self.topToBottom(effect)
            else:
                for key in self.sequences:
                    if key ==  effect.name:
                        self.sequences.remove(key)
                for key in self.effects:
                    if key ==  effect.name:
                        self.effects.remove(key)
        else:
            self.delayed_name = self.delay(name= effect.name, event_type=None, delay= effect.delay, handler=self.topToBottom, param= effect)
            effect.point1.y -= 1

    def bottomToTop(self, effect):
        '''Starts at top of playfield and lights all lamps from bottom to top for effect.lightTime millisceonds, then repeats if required'''
        self.counter = 0
        #process lamps that haven't been processed yet
        for key in effect.lampList:
            if key.processed == False:
                self.counter += 1
                if key.y < effect.point1.y:
                    key.processed = True
                    self.game.lamps[key.name].pulse(effect.lightTime)
                    self.runtime -=  effect.delay

                    #remove all below on final version
                    self.drawLight(key.name, effect, self.red)

        #test to see if any lights are left and if not, do we need to repeat?
        if self.counter == 0:                                #if true, all lamps have been processed this go around
            for key in effect.lampList:
                key.processed = False      #reset flag
            if effect.repeat > 0:
                effect.repeat -= 1
                effect.point1.y = 0
                self.bottomToTop(effect)
            else:
                for key in self.sequences:
                    if key ==  effect.name:
                        self.sequences.remove(key)
                for key in self.effects:
                    if key ==  effect.name:
                        self.effects.remove(key)
        else:
            self.delayed_name = self.delay(name= effect.name, event_type=None, delay= effect.delay, handler=self.bottomToTop, param= effect)
            effect.point1.y += 1

    def rightToLeft(self, effect):
        '''Starts at top of playfield and lights all lamps from top to bottom for effect.lightTime millisceonds, then repeats if required'''
        self.counter = 0
        #process lamps that haven't been processed yet
        for key in effect.lampList:
            if key.processed == False:
                self.counter += 1
                if key.x > effect.point1.x:
                    key.processed = True
                    self.game.lamps[key.name].pulse(effect.lightTime)
                    self.runtime -=  effect.delay

                    #remove all below on final version
                    self.drawLight(key.name, effect, self.red)

        #test to see if any lights are left and if not, do we need to repeat?
        if self.counter == 0:                                #if true, all lamps have been processed this go around
            for key in effect.lampList:
                key.processed = False      #reset flag
            if effect.repeat > 0:
                effect.repeat -= 1
                effect.point1.x = self.maxX
                self.rightToLeft(effect)
            else:
                for key in self.sequences:
                    if key ==  effect.name:
                        self.sequences.remove(key)
                for key in self.effects:
                    if key ==  effect.name:
                        self.effects.remove(key)
        else:
            self.delayed_name = self.delay(name= effect.name, event_type=None, delay= effect.delay, handler=self.rightToLeft, param= effect)
            effect.point1.x -= 1
    
    def leftToRight(self, effect):
        '''Starts at top of playfield and lights all lamps from top to bottom for effect.lightTime millisceonds, then repeats if required'''
        self.counter = 0
        #process lamps that haven't been processed yet
        for key in effect.lampList:
            if key.processed == False:
                self.counter += 1
                if key.x < effect.point1.x:
                    key.processed = True
                    self.game.lamps[key.name].pulse(effect.lightTime)
                    self.runtime -=  effect.delay

                    #remove all below on final version
                    self.drawLight(key.name, effect, self.red)

        #test to see if any lights are left and if not, do we need to repeat?
        if self.counter == 0:                                #if true, all lamps have been processed this go around
            for key in effect.lampList:
                key.processed = False      #reset flag
            if effect.repeat > 0:
                effect.repeat -= 1
                effect.point1.x = 0
                self.leftToRight(effect)
            else:
                for key in self.sequences:
                    if key ==  effect.name:
                        self.sequences.remove(key)
                for key in self.effects:
                    if key ==  effect.name:
                        self.effects.remove(key)
        else:
            self.delayed_name = self.delay(name= effect.name, event_type=None, delay= effect.delay, handler=self.leftToRight, param= effect)
            effect.point1.x += 1

    def diagBottomLeftToRight(self, effect):
        '''Starts at bottom left of playfield and lights diagonally up towards upper right of playfield'''
        self.counter = 0
        #process lamps that haven't been processed yet
        for key in effect.lampList:
            if key.processed == False:
                self.counter += 1
                #calculate determinate. if at or less than 0, line is past lamp and should light it
                d = self.determinate(effect.point1, effect.point2, key.x, key.y)
                if d == 0:
                    key.processed = True
                    self.game.lamps[key.name].pulse(effect.lightTime)
                    self.runtime -=  effect.delay

                    #remove all below on final version
                    self.drawLight(key.name, effect, self.red)

        #test to see if any lights are left and if not, do we need to repeat?
        if self.counter == 0:                                #if true, all lamps have been processed this go around
            for key in effect.lampList:
                key.processed = False      #reset flag
            if effect.repeat > 0:
                effect.repeat -= 1
                effect.point1.x = 0
                effect.point1.y = 1
                effect.point2.x = 1
                effect.point2.y = 0
                self.diagBottomLeftToRight(effect)
            else:
                for key in self.sequences:
                    if key ==  effect.name:
                        self.sequences.remove(key)
                for key in self.effects:
                    if key ==  effect.name:
                        self.effects.remove(key)
        else:
            self.delayed_name = self.delay(name= effect.name, event_type=None, delay= effect.delay, handler=self.diagBottomLeftToRight, param= effect)
            #iterate point1 from (0,1) to (0,maxY) then to (maxX, maxY)
            if effect.point1.y > self.maxY:
                effect.point1.x += 1
            else:
                effect.point1.y += 1
            #iterate point2 from (1,0) to (1,maxX) then to (maxX, maxY)
            if effect.point2.x > self.maxX:
                effect.point2.y += 1
            else:
                effect.point2.x += 1

    def diagBottomRightToLeft(self, effect):
        '''Starts at bottom left of playfield and lights diagonally up towards upper right of playfield'''
        print "diagBottomRightToLeft"
        self.counter = 0
        self.litLamp = False
        #process lamps that haven't been processed yet
        for key in effect.lampList:
            if key.processed == False:
                self.counter += 1
                #calculate determinate. if at or less than 0, line is past lamp and should light it
                d = self.determinate(effect.point1, effect.point2, key.x, key.y)
                if d == 0:
                    self.litLamp = True
                    key.processed = True
                    self.game.lamps[key.name].pulse(effect.lightTime)
                    self.runtime -=  effect.delay

                    #remove all below on final version
                    self.drawLight(key.name, effect, self.red)

        #test to see if any lights are left and if not, do we need to repeat?
        if self.counter == 0:                                #if true, all lamps have been processed this go around
            for key in effect.lampList:
                key.processed = False      #reset flag
            if effect.repeat > 0:
                effect.repeat -= 1
                effect.point1.x = self.maxX - 2
                effect.point1.y = 0
                effect.point2.x = self.maxX
                effect.point2.y = 2
                self.diagBottomRightToLeft(effect)
            else:
                for key in self.sequences:
                    if key ==  effect.name:
                        self.sequences.remove(key)
                for key in self.effects:
                    if key ==  effect.name:
                        self.effects.remove(key)
        else:
            #iterate point1 from (maxX, 0) to (0,0) then to (0, maxY)
            if effect.point1.x <=0:
                effect.point1.y += 1
            else:
                effect.point1.x -= 1
            #iterate point2 from (maxX,1) to (maxX,maxX) then to (0,maxY)
            if effect.point2.y > self.maxY:
                effect.point2.x -= 1
            else:
                effect.point2.y += 1

            if self.litLamp:
                self.delayed_name = self.delay(name= effect.name, event_type=None, delay= effect.delay, handler=self.diagBottomRightToLeft, param= effect)
            else:
                self.delayed_name = self.delay(name=effect.name, event_type=None, delay = 0, handler = self.diagBottomRightToLeft, param = effect)

    def blink(self, effect):
        """blinks all the lights as many times as repeat is set to, with delay set by length"""
        for key in effect.lampList:
            
            self.game.lamps[key.name].pulse(effect.lightTime)

            #delete after
            self.drawLight(key.name, effect, self.red)

        if effect.repeat > 0:
            effect.repeat -= 1
            self.delayed_name = self.delay(name= effect.name, event_type=None, delay= effect.delay, handler=self.blink, param= effect)
        else:
            for key in self.sequences:
                    if key ==  effect.name:
                        self.sequences.remove(key)
            for key in self.effects:
                if key ==  effect.name:
                    self.effects.remove(key)

    def determinate(self, p, q, rx, ry):
        '''function calculates a determinate between two endpoints of a line and a middle point to see if point is on the line
            if d is close to zero, point is on the line'''
        print p.x, p.y, q.x, q.y, rx, ry
        d = ((q.x-p.x)*(ry-p.y)-(q.y-p.y)*(rx-p.x))
        return d

    #delete this function for final build
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

    #delete this function for final build
    def drawLight(self, Name, effect, color):
        for key in effect.lampList:
            if key.name == Name:
                time = datetime.now()
                key.timestamp = (time.second * 1000 + time.microsecond / 1000)
                pygame.draw.circle(self.screen, color, (key.x * 20, (self.maxY * 20 - key.y * 20)), 8, 0)
                self.recolor_name = self.delay(name=key, event_type=None, delay=effect.lightTime/1000, handler=self.recolor, param=effect)
        pygame.display.flip()

    #delete this function and references for final build
    def recolor(self,effect):
        for key in effect.lampList:
            now = datetime.now()
            now = (now.second * 1000 + now.microsecond / 1000)        #convert to milliseconds
            if (now-key.timestamp) >= float(effect.lightTime) and key.timestamp != 0:
                pygame.draw.circle(self.screen, self.white, (key.x * 20, (self.maxY * 20 - key.y * 20)), 8, 0)
                key.timestamp = 0

    def mode_started(self):
        pass

    def mode_topmost(self):
        pass

    def mode_stopped(self):
        pass

    def mode_tick(self):
        pass
