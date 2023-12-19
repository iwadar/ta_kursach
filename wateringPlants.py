import arcade
import arcade.gui
from datetime import timedelta

from humidity import *
from volumeWater import *
from timing import *
from error import *
from enum import Enum


_VOLUME_LOW = 100
_VOLUME_MIN = 0
_HUMIDITY_LEVEL_LOW = 30
_HUMIDITY_LEVEL_OPTIMAL = 70
_HUMIDITY_LEVEL_MAX = 100


StateEnum = Enum('StateEnum', ['On', 'Off', 'CheckSystem', 'Watering', 'Wait', 'Error', 'NoWater'])

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
START_WATERING = 380
IRRIGATOR_X = 450
IRRIGATOR_Y = 320
SPACE_RIGHT_BUTTOM = 30
WIDTH_BUTTOM = 150
BUTTOM_ON_X = 100
BUTTOM_ON_Y = 530
COEFFICIENT_TIME = 10

LEVEL_X = 900
LEVEL_Y = BUTTOM_ON_Y
_WAIT_TIME = 15
_SPEED_CHANGE_Y = -7
_VOLUME_HIGH = 700


class WateringPlantWindow(arcade.Window):    

    currentState = None
    humidity = []
    volume = None
    timing = None  
    error = None
    isHappened = False
    isClickWatering = False
    isAddNoWaterButton = False
    isAddErrorButton = False
    paddingNoWater = None
    paddingError = None

    def __init__(self):
        self.total_time = 35880.0
        self.prev_time = self.total_time
        self.humidity.append(Humidity(self.total_time, curHumedity=20, seconds=60))
        self.humidity.append(Humidity(self.total_time, seconds=10))
        self.durationWatering = [0.0] * len(self.humidity)
        self.volume = VolumeWater(1000)
        self.timing = Timing()
        self.errorState = Error()
        self.currentState = StateEnum.Off
        self.prevState = self.currentState
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title='Watering Plants')
        arcade.set_background_color(arcade.color.ANTIQUE_WHITE)
        self.ground = arcade.create_rectangle_filled(center_x=SCREEN_WIDTH/2.5, center_y=SCREEN_HEIGHT/1.7, width=800, height=450, color=arcade.color.IVORY)

        ################# BUTTOM ##############################
        self.managerNeedButton = arcade.gui.UIManager()
        self.managerNeedButton.enable()
        
        self.g_box = arcade.gui.UIBoxLayout(vertical=False, )
        self.on_buttom = arcade.gui.UIFlatButton(text="Включить", width=WIDTH_BUTTOM)
        self.g_box.add(self.on_buttom.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM))
        self.off_buttom = arcade.gui.UIFlatButton(text="Выключить", width=WIDTH_BUTTOM)
        self.g_box.add(self.off_buttom.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM))
        self.watering_1_buttom = arcade.gui.UIFlatButton(text="Полить", width=WIDTH_BUTTOM)
        self.g_box.add(self.watering_1_buttom.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM, ))


        ############ SPRITE ##############
        self.flowers = []
        self.flowers.append(arcade.Sprite('img/plants.png', 0.35))
        self.flowers[0].center_x = IRRIGATOR_X - 210
        self.flowers[0].center_y = IRRIGATOR_Y - 70

        self.flowers.append(arcade.Sprite('img/flower2.png', 0.35))
        self.flowers[1].center_x = IRRIGATOR_X - 20
        self.flowers[1].center_y = IRRIGATOR_Y - 70

        self.irrigator = arcade.Sprite('img/irrigator2.png', 0.5)
        self.irrigator.center_x = IRRIGATOR_X
        self.irrigator.center_y = IRRIGATOR_Y

        self.switch_off = arcade.Sprite('img/off.png', 0.1)
        self.switch_off.center_x = BUTTOM_ON_X
        self.switch_off.center_y = BUTTOM_ON_Y

        self.watering = []
        self.watering.append(arcade.Sprite('img/watering.png', 0.1))
        self.watering.append(arcade.Sprite('img/watering.png', 0.1))
        self.setupWateringParam(alpha=255, change_y=0, duration=0)

        self.error = arcade.Sprite('img/error.png', 0.2)
        self.error.alpha = 0
        self.error.center_x = IRRIGATOR_X + 205
        self.error.center_y = IRRIGATOR_Y - 65

        self.noWater = arcade.Sprite('img/noWater.png', 0.2)
        self.noWater.alpha = 0
        self.noWater.center_x = IRRIGATOR_X + 205
        self.noWater.center_y = IRRIGATOR_Y - 65

        ############ LEVEL ###############

        self.timer_text = arcade.Text(
            text="00:00:00",
            start_x=LEVEL_X,
            start_y=LEVEL_Y,
            color=arcade.color.ARSENIC,
            font_size=25,
            anchor_x="left",
        )

        self.label = arcade.Text(
            text="",
            start_x=BUTTOM_ON_X + 370,
            start_y=LEVEL_Y,
            color=arcade.color.ARSENIC,
            font_size=19,
            anchor_x="right",
        )
        
        self.humidity_text = []
        
        self.humidity_text.append(arcade.Text(
            text="",
            start_x=self.flowers[0].center_x + 75,
            start_y=self.flowers[0].center_y + 250,
            color=arcade.color.YELLOW_ORANGE,
            font_size=20,
            anchor_x="right",
            multiline=True,
            width=100
        ))

        self.humidity_text.append(arcade.Text(
            text="",
            start_x=self.flowers[1].center_x + 75,
            start_y=self.flowers[1].center_y + 250,
            color=arcade.color.YELLOW_ORANGE,
            font_size=20,
            anchor_x="right",
            multiline=True,
            width=100
        ))
        
        self.volume_text = arcade.Text(
            text="",
            start_x=LEVEL_X + 60,
            start_y=LEVEL_Y - 52,
            color=arcade.color.RED,
            font_size=20,
            anchor_x="right",
            multiline=True,
            width=100
        )


        ############ BUTTOM_FUNC ##############
        self.on_buttom.on_click = self.on_click_on
        self.off_buttom.on_click = self.on_click_off
        self.watering_1_buttom.on_click = self.on_click_watering

        self.managerNeedButton.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="left",
                anchor_y="bottom",
                align_x=90,
                align_y=20,
                child=self.g_box)
        )

    def setupWateringParam(self, alpha, change_y, duration, number = -1):
        if number >= 0:
            self.watering[number].center_x = self.flowers[number].center_x
            self.watering[number].center_y = self.flowers[number].center_y + 120
            self.watering[number].alpha = alpha
            self.watering[number].change_y = change_y
            self.durationWatering[number] = duration
        else:
            i = 0
            for watering, flower in zip(self.watering, self.flowers):
                watering.center_x = flower.center_x
                watering.center_y = flower.center_y + 120
                watering.alpha = alpha
                watering.change_y = change_y
                self.durationWatering[i] = duration
                i += 1

    def setupOnOffSprite(self, filename):
        self.switch_off = arcade.Sprite(filename, 0.1)
        self.switch_off.center_x = BUTTOM_ON_X
        self.switch_off.center_y = BUTTOM_ON_Y
    
    """
    Состояние Сломалось оборудование
    """
    def stateError(self):
        if self.currentState == StateEnum.On:
            self.error.alpha = 255
        self.currentState = StateEnum.Error
        print('Current state: {}'.format(self.currentState.name))

    """
    Состояние Нет воды
    """
    def stateNoWater(self):
        if self.currentState == StateEnum.On:
            self.noWater.alpha = 255
        self.currentState = StateEnum.NoWater
        print('Current state: {}'.format(self.currentState.name))

    """
    Состояние Проверка системы
    """
    def stateCheckSystem(self):
        memberState = self.currentState
        self.currentState = StateEnum.CheckSystem
        print('Current state: {}'.format(self.currentState.name))
        if memberState == StateEnum.NoWater and self.volume.getCurrentVolume() > _VOLUME_MIN:
            self.noWater.alpha = 0
        elif memberState == StateEnum.Error:
            self.error.alpha = 0
        elif self.volume.getCurrentVolume() <= _VOLUME_MIN:
            self.stateNoWater()
        elif (self.isHappened and self.volume.getCurrentVolume() > _VOLUME_MIN):
            self.stateError()
        elif self.errorState.isError():
            self.stateError()
        self.isHappened = False

    """
    Состояние Полив
    """
    def stateWatering(self, levelWatering, numberFlower = -1):
        self.currentState = StateEnum.Watering
        print('Current state: {}'.format(self.currentState.name))
        waterToPlants = 0
        if numberFlower >= 0:
            mlToAdd = self.humidity[numberFlower].howMlNeedToGoodHumidity(levelWatering)
            waterToPlants = self.volume.giveWater(mlToAdd)
            self.setupWateringParam(alpha=255, change_y=_SPEED_CHANGE_Y, duration=waterToPlants/100, number=numberFlower)
            self.humidity[numberFlower].addHumedity(waterToPlants)
            if waterToPlants < mlToAdd or self.errorState.isError():
                self.isHappened = True
        else:
            for i, humidity in enumerate(self.humidity):
                mlToAdd = humidity.howMlNeedToGoodHumidity(levelWatering)
                waterToPlants = self.volume.giveWater(mlToAdd)
                self.setupWateringParam(alpha=255, change_y=_SPEED_CHANGE_Y, duration=waterToPlants/100, number=i)
                humidity.addHumedity(waterToPlants)
                if waterToPlants < mlToAdd:
                    self.isHappened = True
            if self.errorState.isError():
                self.isHappened = True
    
    """
    Состояние Ожидание
    """
    def stateWait(self, nowState = StateEnum.Wait):
        if nowState == StateEnum.Watering:
            self.stateWatering(_HUMIDITY_LEVEL_MAX)
        if nowState != StateEnum.Wait:
            self.stateCheckSystem()
        curHumidityList = [0.0] * len(self.humidity)
        for i, humidity in enumerate(self.humidity):
            curHumidityList[i] = humidity.checkLevelHumedity(self.total_time)
        if self.currentState != StateEnum.NoWater and self.currentState != StateEnum.Error:
            self.currentState = StateEnum.Wait
            print('Current state: {}'.format(self.currentState.name))
            i = -1
            for curHumidity, humidity in zip(curHumidityList, self.humidity):
                i = i + 1
                if curHumidity < _HUMIDITY_LEVEL_LOW or (self.timing.checkTimeToWatering(self.total_time, isDone=(i + 1 == len(self.humidity))) and curHumidity < _HUMIDITY_LEVEL_OPTIMAL):
                    self.stateWatering(_HUMIDITY_LEVEL_OPTIMAL, i)
                    curHumidityList[i] = humidity.checkLevelHumedity(self.total_time)
                    self.stateCheckSystem()
                    if self.currentState != StateEnum.NoWater and self.currentState != StateEnum.Error:
                        self.currentState = StateEnum.Wait
        return curHumidityList
    """
    Состояние вкл/выкл
    """
    def on_click_on(self, event):
        if self.currentState == StateEnum.Off:
            self.setupOnOffSprite('img/on.png')
            self.currentState = StateEnum.On
            print('Current state: {}'.format(self.currentState.name))
            for i, humidity in enumerate(self.humidity):
                self.textColor(int(humidity.checkLevelHumedity(self.total_time)), self.volume.getCurrentVolume(), i)
            self.label.text = "Уровень влажности"
            self.stateWait(StateEnum.On)

    def on_click_off(self, event):
        if self.currentState != StateEnum.Off:
            self.currentState = StateEnum.Off
            self.setupOnOffSprite('img/off.png')
            self.setupWateringParam(0, 0, 0)
            self.noWater.alpha = 0
            self.error.alpha = 0
            for text in self.humidity_text:
                text.text = ""
            self.volume_text.text = ""
            self.label.text = ""
            # self.textColor(int(self.humidity.checkLevelHumedity(self.total_time)), self.volume.getCurrentVolume())
            print('Current state: {}'.format(self.currentState.name))

    def on_click_watering(self, event):
        if self.currentState == StateEnum.Off or self.currentState == StateEnum.NoWater or self.currentState == StateEnum.Error:
            return
        curHumidity = self.stateWait(nowState=StateEnum.Watering)

    def on_click_fixed(self, event):
        if self.currentState != StateEnum.Error:
            return
        curHumidity = self.stateWait(nowState=StateEnum.Error)


    def on_click_add_water(self, event):
        if self.currentState == StateEnum.Off or self.currentState == StateEnum.Error:
            return
        needToMax = self.volume.howVolumeNeedToMax()
        self.volume.takeWater(needToMax)
        if self.currentState == StateEnum.NoWater:
            self.stateWait(nowState=StateEnum.NoWater)
        else:
            self.volume_text.text = f"Заполненность водного резервуара: {self.volume.getCurrentVolume()} ml"
            self.volume_text.color = arcade.color.GREEN



    def on_draw(self):
        self.clear()
        self.ground.draw()
        for flower in self.flowers:
            flower.draw()
        self.irrigator.draw()
        self.switch_off.draw()
        self.timer_text.draw()
        self.label.draw()
        for text in self.humidity_text:
            text.draw()
        self.volume_text.draw()
        for watering in self.watering:
            watering.draw()
        self.error.draw()
        self.noWater.draw()
        if self.currentState == StateEnum.NoWater and not self.isAddNoWaterButton:
            self.addWater = arcade.gui.UIFlatButton(text="Налить воды", width=WIDTH_BUTTOM)
            self.addWater.on_click = self.on_click_add_water
            self.paddingNoWater = self.addWater.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM)
            self.g_box.add(self.paddingNoWater)
            self.isAddNoWaterButton = True
            self.noWater.alpha = 255
        if self.currentState == StateEnum.Error and not self.isAddErrorButton:
            self.fixed = arcade.gui.UIFlatButton(text="Починить", width=WIDTH_BUTTOM)
            self.fixed.on_click = self.on_click_fixed
            self.paddingError = self.fixed.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM)
            self.g_box.add(self.paddingError)
            self.isAddErrorButton = True
            self.error.alpha = 255
        if self.currentState != StateEnum.NoWater and self.isAddNoWaterButton:
            self.g_box.remove(self.paddingNoWater)
            self.isAddNoWaterButton = False
            self.noWater.alpha = 0
        if self.currentState != StateEnum.Error and self.isAddErrorButton:
            self.g_box.remove(self.paddingError)
            self.isAddErrorButton = False
            self.error.alpha = 0
        self.managerNeedButton.draw()

        # self.managerNoWater.draw()

    def textColor(self, humidity, volume, number = 0):
        color = None
        if humidity <= _HUMIDITY_LEVEL_LOW:
            color = arcade.color.RED
        elif humidity < _HUMIDITY_LEVEL_OPTIMAL:
            color = arcade.color.YELLOW_ORANGE
        elif humidity >= _HUMIDITY_LEVEL_OPTIMAL:
            color = arcade.color.KELLY_GREEN
        self.humidity_text[number].text = f"{humidity}%"
        self.humidity_text[number].color = color

        if volume <= _VOLUME_LOW:
            color = arcade.color.RED
        elif volume < _VOLUME_HIGH:
            color = arcade.color.YELLOW_ORANGE
        elif volume >= _VOLUME_HIGH:
            color = arcade.color.KELLY_GREEN
        self.volume_text.text = f"Заполненность водного резервуара: {volume} ml"
        self.volume_text.color = color

    def update(self, delta_time: float):
        self.switch_off.update()
        for watering in self.watering:
            watering.update()
        self.noWater.update()
        self.error.update()
        self.total_time += delta_time * COEFFICIENT_TIME
        td = timedelta(seconds=self.total_time)
        x = str(td).split('.')
        self.timer_text.text = f"{x[0]}"




        for i, duration in enumerate(self.durationWatering):
            if duration > 0:
                self.durationWatering[i] -= delta_time * (COEFFICIENT_TIME / 2)
                if self.watering[i].center_y < 255:
                    self.setupWateringParam(alpha=255, change_y=_SPEED_CHANGE_Y, duration=self.durationWatering[i], number=i)
            else:                
                self.setupWateringParam(alpha=0, change_y=0, duration=0, number=i)



        # if self.durationWatering[0] > 0:
        #     self.durationWatering[0] -= delta_time * (COEFFICIENT_TIME / 2)
        #     if self.watering[0].center_y < 255:
        #         self.setupWateringParam(alpha=255, change_y=_SPEED_CHANGE_Y, duration=self.durationWatering[0], number=0)
        # else:
        #     self.setupWateringParam(alpha=0, change_y=0, duration=0, number=0)

        # if self.durationWatering[1] > 0:
        #     self.durationWatering[1] -= delta_time * (COEFFICIENT_TIME / 2)
        #     print(self.durationWatering[1])
        #     if self.watering[1].center_y < 255:
        #         self.setupWateringParam(alpha=255, change_y=_SPEED_CHANGE_Y, duration=self.durationWatering[1], number=1)
        # else:
        #     self.setupWateringParam(alpha=0, change_y=0, duration=0, number=1)

        if self.total_time - self.prev_time > _WAIT_TIME and self.currentState == StateEnum.Wait:
            curHumidity = self.stateWait()
            for i, humidity in enumerate(curHumidity):
                self.textColor(int(humidity), self.volume.getCurrentVolume(), i)
            self.prev_time = self.total_time
        elif self.total_time - self.prev_time > _WAIT_TIME and (self.currentState == StateEnum.Error or self.currentState == StateEnum.NoWater):
            for i, humidity in enumerate(self.humidity):
                self.textColor(int(humidity.checkLevelHumedity(self.total_time)), self.volume.getCurrentVolume(), i)
            self.prev_time = self.total_time


WateringPlantWindow()
arcade.run()