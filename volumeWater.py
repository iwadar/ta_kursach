_VOLUME_MAX = 1000
_VOLUME_MIN = 0
_VOLUME_MIDDLE = 500
_VOLUME_HIGH = 700
_VOLUME_STEP_ADD = 300
_VOLUME_STEP_REMOVE = 100

class VolumeWater:
    __curVolume = 0
    def __init__(self, curVolume = 700) -> None:
        self.__curVolume = curVolume

    """
    На вход: сколько ml хотят забрать
    Выход: сколько может дать
    """
    def giveWater(self, needVolume: int):
        if self.__curVolume - needVolume < 0:
            giveVolume = self.__curVolume
            self.__curVolume = 0
            return giveVolume
        else:
            self.__curVolume -= needVolume
            return needVolume
    
    """
    На вход: сколько ml вливают
    Выход: текущий объем
    """
    def takeWater(self, takeVolume: int):
        self.__curVolume += takeVolume
        if self.__curVolume > _VOLUME_MAX:
            self.__curVolume = _VOLUME_MAX
        return self.__curVolume
    
    """
    Выход: сколько ml нужно долить, чтобы был max
    """
    def howVolumeNeedToMax(self):
        return _VOLUME_MAX - self.__curVolume
    
    def getCurrentVolume(self):
        return self.__curVolume
    

v = VolumeWater()
print(v.howVolumeNeedToMax())