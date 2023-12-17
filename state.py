from humidity import *
from volumeWater import *
from timing import *
from error import *
from enum import Enum
import time

_VOLUME_LOW = 100
_HUMIDITY_LEVEL_LOW = 30
_HUMIDITY_LEVEL_OPTIMAL = 70


StateEnum = Enum('StateEnum', ['On', 'Off', 'CheckSystem', 'Watering', 'Wait', 'Error', 'NoWater'])

class State:
    currentState = None
    humidity = None
    volume = None
    timing = None  
    error = None
    isHappened = False

    def __init__(self, time) -> None:
        self.humidity = Humidity(time, 30)
        self.volume = VolumeWater()
        self.timing = Timing()
        self.error = Error()
        self.currentState = StateEnum.Off
    

    """
    Состояние Проверка системы
    """
    def stateCheckSystem(self):
        print('Current state: {}'.format(self.currentState.name))
        while (self.isHappened and self.volume.getCurrentVolume() > _VOLUME_LOW) or self.error.isError():
            self.currentState = StateEnum.CheckSystem
            self.stateError()
        while self.volume.getCurrentVolume() <= _VOLUME_LOW:
            self.currentState = StateEnum.CheckSystem
            self.stateNoWater()

    """
    Состояние Сломалось оборудование
    """
    def stateError(self):
        self.currentState = StateEnum.Error
        print('Current state: {}'.format(self.currentState.name))
        pass

    """
    Состояние Нет воды
    """
    def stateNoWater(self):
        self.currentState = StateEnum.NoWater
        print('Current state: {}'.format(self.currentState.name))
        pass

    """
    Состояние Полив
    """
    def stateWatering(self):
        self.currentState = StateEnum.Watering
        print('Current state: {}'.format(self.currentState.name))
        mlToAdd = self.humidity.howMlNeedToGoodHumidity(_HUMIDITY_LEVEL_OPTIMAL)
        waterToPlants = self.volume.giveWater(mlToAdd)
        curHumidity = self.humidity.addHumedity(mlToAdd)
        if waterToPlants < mlToAdd or self.error.isError():
            self.isHappened = True
        return curHumidity

    def stateWait(self, time):
        if self.currentState == StateEnum.On:
            self.stateCheckSystem()
        self.currentState = StateEnum.Wait
        print('Current state: {}'.format(self.currentState.name))
        curHumidity = self.humidity.checkLevelHumedity(time)
        if curHumidity < _HUMIDITY_LEVEL_LOW or self.timing.checkTimeToWatering(time):
            self.stateWatering()
            self.currentState = StateEnum.CheckSystem
            self.stateCheckSystem()
            self.currentState = StateEnum.Wait
        return curHumidity
