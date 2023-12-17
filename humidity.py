_HUMIDITY_LEVEL_MAX = 100
_HUMIDITY_LEVEL_MIN = 0
_HUMIDITY_LEVEL_MIDDLE = 50
_HUMIDITY_LEVEL_HIGH = 30
_PROCENT = 1
_SEC_PER_MINUTE = 20
_ADD_HUMIDITY = 7
_ADD_ML = 100
_COEFFICIENT_PROCENT_PER_ML = _ADD_HUMIDITY / _ADD_ML
_COEFFICIENT_VAPORIZE = _PROCENT / _SEC_PER_MINUTE

class Humidity():
    __currentLevelHumidity = 50.0
    __prevTime = 0
    def __init__(self, prevTime, curHumedity = 50) -> None:
        self.__prevTime = prevTime
        self.__currentLevelHumidity = curHumedity

    """
    На вход: текущее время
    Выход: текущий уровень влажности 
    """
    def checkLevelHumedity(self, curTime: int):
        self.__currentLevelHumidity -= _COEFFICIENT_VAPORIZE * (curTime - self.__prevTime)
        self.__prevTime = curTime
        if self.__currentLevelHumidity < _HUMIDITY_LEVEL_MIN:
            self.__currentLevelHumidity = _HUMIDITY_LEVEL_MIN
        return self.__currentLevelHumidity
    
    """
    На вход: количество доливаемой воды
    Выход: текущий уровень влажности 
    """
    def addHumedity(self, mlToAdd: int):
        self.__currentLevelHumidity += _COEFFICIENT_PROCENT_PER_ML * mlToAdd
        if self.__currentLevelHumidity >= _HUMIDITY_LEVEL_MAX:
            self.__currentLevelHumidity = _HUMIDITY_LEVEL_MAX
        return self.__currentLevelHumidity
    
    """
    Вход: требуемый уровень влажности
    На выходе: сколько ml жидкости нужно добавить до требуемого уровня
    """
    def howMlNeedToGoodHumidity(self, needLevelHumidity: int):
        return int((needLevelHumidity - self.__currentLevelHumidity) * _ADD_ML / _ADD_HUMIDITY)
    
    def getCurrentHumidity(self):
        return self.__currentLevelHumidity