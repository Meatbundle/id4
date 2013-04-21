class Point():
    def __init__(self, X, Y):
        self.x = X
        self.y = Y

class Effect():
    def __init__(self, Name, LampList, Length, LightTime, Repeat, Delay):
        """setup defaults"""
        self.point1 = Point(0, 0)
        self.point2 = Point(0, 0)
        self.name = Name
        self.lampList = LampList
        self.lampListRemove = LampList
        self.length = Length
        self.lightTime = LightTime
        self.repeat = Repeat
        self.delay = Delay

        #temp vars for testiing
        self.turnOnLights = dict()                 #stores keys for lamps to draw back white on test scren

