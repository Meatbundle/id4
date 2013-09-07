class id4Player(object):
    """Represents a player in the game.
    The game maintains a collection of players in :attr:`GameController.players`."""
    score = 0
    name = None
    extra_balls = 0
    game_time = 0

    hurrytargs = {'top':False, 'mid': False, 'bottom': False}		#flags for if hurryup targets have been hit or not
    standuptargs = {'left':False, 'mid': False, 'right': False}		#same for standup targets
    a51targs = {'top':False, 'mid': False, 'bottom': False}			#ditto for area 51 targets

    lastShot = 'none'           #for combo tracking

    lRampHits = 0               #how many times left ramp has been hit
    rRampHits = 0               #how many times right ramp has been hit
    rampsReady = False          #is mode ready to be started
    rampHitsRequired = 0		#how many rampHits are required to start mode
    rampStarted = False         #has player started the ramp mode
    rampCompleted = False		#has player completed the ramp mode
    rampHitsForComplete = 0		#how many ramps until mode is completed
    nextRamp = 'either'          #which ramp to hit to advance ramp modes

    f18hits = 0                 #hits that qualified to start independence mode
    f18Ready = False            #is mode ready to be started
    f18hitsRequired = 6         #num hits required to start mode
    f18Started = False          #has player started mode
    f18Complete = False         #has player completed mode
    f18hitsForComplete = 10     #how many hits to complete mode
    f18JackpotValue = 5000000   #base jackpot value
    nextLoop = 'right'          #which loop to hit next to advance mode
    ballLocked = False          #is ball locked in tunnel to double jackpot?

    a51completions = 0          #how many times target bank has been completed
    a51Ready = False            #a51 MB ready
    a51CompletionsReq = 0		#how many completions until MB is ready
    a51Started = False          #has the mode been started
    a51Complete = False         #is mode completed
    a51JacksForComplete = 0		#how many jackpots until mode is completed

    hurryupReady = False		#is hurryup ready
    hurryupValue = 10000000		#what is initial value of hurryup
    hurryupPoints = 250000		#how many points added to value per bumper hit

    numHitsSuperJets = 50		#how many hits until superjets starts

    jackpotsLit = list()		#list of str of which jackpots are lit ('leftRamp', 'rightRamp', 'leftLoop',
                            #	'rightLoop', 'centerRamp', 'alienHead', 'a51shot')
    def __init__(self, name):
        super(Player, self).__init__()
        self.name = name
