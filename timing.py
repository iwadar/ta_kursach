_TIME_FAULT = 60

class Timing:
    __timing = {}
    def __init__(self, timing = [36000, 64800]) -> None:
        for time in timing:
            self.__timing[time] = False # время полива - 10, 18. Задано в секундах

    """
    Вход: текущее время в секундах
    Выход: если совпадает время текущее со временем в расписании, то true
    """
    def checkTimeToWatering(self, curTime, isDone):
        for time in self.__timing.keys():
            if curTime - time < _TIME_FAULT and curTime - time > 0 and not self.__timing[time]:
                self.__timing[time] = isDone
                return True
        return False
    
    def newDay(self):
        for time in self.__timing.keys():
            self.__timing[time] = False # время полива - 10, 18. Задано в секундах