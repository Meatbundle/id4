"""This file contains different classes for use in the LightSequencer class"""

class Point():
    def __init__(self, X, Y):
        self.x = X
        self.y = Y

class LampList():
    def __init__(self, TimeStamp, Name, X, Y, Processed=False):
        self.timestamp = TimeStamp
        self.name = Name
        self.processed = Processed
        self.x = X
        self.y = Y

class Effect():
    def __init__(self, Name, lamplist, Length, LightTime, Repeat, Delay):
        """setup defaults"""
        self.point1 = Point(0, 0)
        self.point2 = Point(0, 0)
        self.name = Name
        self.lampList = list()
        self.length = Length
        self.lightTime = LightTime
        self.repeat = Repeat
        self.delay = Delay
        self.loadLamps(lamplist)

    def loadLamps(self, lamplist):
        for key in lamplist:
            self.temp = LampList(0, key, lamplist[key]['x'], lamplist[key]['y'], False)
            self.lampList.append(self.temp)

class Light():
    """class to hold the status and schedule of a light. schedule is only used if status is set to custom, else default schedules are used in code"""
    def __init__(self, Name, Status, Schedule=0xFFFFFFFF):
        self.name = Name
        self.status = Status
        self.schedule = Schedule



