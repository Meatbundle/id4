from procgame import *
import locale

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

class BallSearch(game.Mode):
    def __init__(self, game, priority, countdown_time, coils=[], reset_switches=[], stop_switches=[], enable_switch_names=[]):
        super(BallSearch, self).__init__(game,priority)
        self.stop_switches = stop_switches
        self.countdown_time = countdown_time
        self.coils = coils
        self.enable_switch_names = enable_switch_names
        self.enabled = 0

        #Mode.__init__(self, game, 8)
        for switch in reset_switches:
            self.add_switch_handler(name=str(switch), event_type=str(reset_switches[switch]), delay=None, handler=self.reset)
        # The disable_switch_names identify the switches that, when closed,
        # keep the ball search from occuring.  This is typically done,
        # for instance, when a ball is in the shooter lane or held on a flipper.
        for switch in stop_switches:
            self.add_switch_handler(name=str(switch), event_type=str(stop_switches[switch]), delay=None, handler=self.stop)

    def enable(self):
        self.enabled = 1
        print "--> BALL SEARCH ENABLED <--"
        self.reset('None')

    def disable(self):
        self.stop(None)
        print "-->> BALL SEARCH DISABLED <<--"
        self.enabled = 0

    def reset(self,sw):
        self.cancel_delayed("stoppedReset")
        if self.enabled:
            # Stop delayed coil activations in case a ball search has
            # already started.
            self.cancel_delayed('search_coils')
            schedule_search = 1
            for switch in self.stop_switches:

                # Don't restart the search countdown if a ball
                # is resting on a stop_switch.  First,
                # build the appropriate function call into
                # the switch, and then call it using getattr()
                sw = self.game.switches[str(switch)]
                state_str = str(self.stop_switches[switch])
                m = getattr(sw, 'is_%s' % (state_str))
                if m():
                    #print "BALL SEARCH NULL - BALL ON STOP SWITCH"
                    schedule_search = 0
                    #print "Rescheduling a check in 2 seconds"
                    self.delay("stoppedReset",delay=2,handler=self.reset,param="Ding")

            if schedule_search:
                self.cancel_delayed(name='ball_search_countdown')
                #print "BALL SEARCH: Scheduling new countdown"
                self.delay(name='ball_search_countdown', event_type=None, delay=self.countdown_time, handler=self.perform_search, param=0)

    def stop(self,sw):
        #print "Ball Search - Stop Switch"
        self.cancel_delayed(name='ball_search_countdown')
        # delay a reset call - so it will restart after a stop switch
        self.delay("stoppedReset",delay=2,handler=self.reset,param="Ding")

    def perform_search(self, completion_wait_time, completion_handler = None):
        # log the search in audits

        if (completion_wait_time != 0):
            self.game.set_status("Balls Missing") # Replace with permanent message
        delay = .150
        for coil in self.coils:
            self.delay(name='search_coils', event_type=None, delay=delay, handler=self.pop_coil, param=str(coil))
            delay = delay + .150

        if (completion_wait_time != 0):
            pass
        else:
            self.cancel_delayed(name='ball_search_countdown')
            self.delay(name='ball_search_countdown', event_type=None, delay=self.countdown_time, handler=self.perform_search, param=0)

    def pop_coil(self,coil):
        self.game.coils[coil].pulse()
