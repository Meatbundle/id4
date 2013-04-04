##Independence Day Remake
##
## A P-ROC Project by Zachary Stauffer, Copyright 2012
## Built on the PyProcGame Framework from Adam Preble and Gerry Stellenberg
##
## Starter script
## shamelessly cribbed from Koen Hetzels's Bride of Pinbot 2.0 and 

#from procgame import *
import locale
import yaml
import sys

import logging
logging.basicConfig(level=logging.WARN, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# Import the actual game script
from game import *
import os

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

# the config file
curr_file_path = os.path.dirname(os.path.abspath( __file__ ))
yaml_path = curr_file_path + "/config/id4.yaml"

def main():
    # Load up the config file
    config = yaml.load(open(yaml_path, 'r'))
    # set a variable for the machine type
    machineType = config['PRGame']['machineType']

    config = 0
    game = None
    fakePinProc = true#(len(sys.argv) >= 1 and 'fakepinproc' in sys.argv)
    #recording = (len(sys.argv) > 1 and 'record' in sys.argv)
    #playback = (len(sys.argv) > 1 and 'playback' in sys.argv)

    #if playback:
    #    # this covers if fakepinproc was not specified
    #    fakePinProc = True

    try:
        # create the game object
        game = id4Game(machineType,fakePinProc)
        # set the game's config path
        game.yamlpath = yaml_path
        # fire off the setup
        game.setup()
        # then run that sucker
        game.run_loop()
    finally:
        del game

if __name__ == '__main__': main()


