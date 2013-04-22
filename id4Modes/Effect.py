class Point():
    def __init__(self, X, Y):
        self.x = X
        self.y = Y

class LightKey():
    def __init__(self, timeStamp, Name):
        self.timestamp = timeStamp
        self.name = Name
        
class Effect():
    def __init__(self, Name, LampList, RemoveList, Length, LightTime, Repeat, Delay):
        """setup defaults"""
        self.point1 = Point(0, 0)
        self.point2 = Point(0, 0)
        self.name = Name
        self.lampList = LampList
        self.lampListRemove = RemoveList
        self.length = Length
        self.lightTime = LightTime
        self.repeat = Repeat
        self.delay = Delay

        self.lightKeys = list()