import math
_HUMIDITY_LEVEL_MAX = 100
_HUMIDITY_LEVEL_MIN = 0

class Humidity():
    __currentLevelHumidity = 0.0
    __prevTime = 0
    COEFFICIENT_PROCENT_PER_ML = 0.0
    COEFFICIENT_VAPORIZE = 0.0
    ADD_HUMIDITY = 0.0
    ADD_ML = 0.0
    def __init__(self, prevTime, curHumedity = 50, procent = 1, seconds = 5, humidity = 7, ml = 100) -> None:
        self.__prevTime = prevTime
        self.__currentLevelHumidity = curHumedity
        self.COEFFICIENT_VAPORIZE = procent / seconds
        self.COEFFICIENT_PROCENT_PER_ML = humidity / ml
        self.ADD_HUMIDITY = humidity
        self.ADD_ML = ml
        

    """
    На вход: текущее время
    Выход: текущий уровень влажности 
    """
    def checkLevelHumedity(self, curTime: int):
        temp = self.__currentLevelHumidity - self.COEFFICIENT_VAPORIZE * (curTime - self.__prevTime)
        # self.__currentLevelHumidity -= self.COEFFICIENT_VAPORIZE * (curTime - self.__prevTime)
        self.__prevTime = curTime
        if temp < _HUMIDITY_LEVEL_MIN:
            self.__currentLevelHumidity = _HUMIDITY_LEVEL_MIN
        else:
            self.__currentLevelHumidity = temp
        return self.__currentLevelHumidity
    
    """
    На вход: количество доливаемой воды
    Выход: текущий уровень влажности 
    """
    def addHumedity(self, mlToAdd: int):
        temp = math.ceil(self.__currentLevelHumidity + self.COEFFICIENT_PROCENT_PER_ML * mlToAdd)
        # self.__currentLevelHumidity += _  COEFFICIENT_PROCENT_PER_ML * mlToAdd
        # if self.__currentLevelHumidity >= _HUMIDITY_LEVEL_MAX:
        if temp >= _HUMIDITY_LEVEL_MAX:
            self.__currentLevelHumidity = _HUMIDITY_LEVEL_MAX
        else:
            self.__currentLevelHumidity = temp
        return self.__currentLevelHumidity
    
    """
    Вход: требуемый уровень влажности
    На выходе: сколько ml жидкости нужно добавить до требуемого уровня
    """
    def howMlNeedToGoodHumidity(self, needLevelHumidity: int):
        return int((needLevelHumidity - self.__currentLevelHumidity) * self.ADD_ML / self.ADD_HUMIDITY)
    
    def getCurrentHumidity(self):
        return self.__currentLevelHumidity