import arcade
import arcade.gui
from datetime import timedelta
# from state import *

from humidity import *
from volumeWater import *
from timing import *
from error import *
from enum import Enum
from time import sleep
from threading import Thread


_VOLUME_LOW = 100
_HUMIDITY_LEVEL_LOW = 30
_HUMIDITY_LEVEL_OPTIMAL = 70
_VOLUME_MIN = 0
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


def sleepSomeSeconds(timeToSleep):
    sleep(timeToSleep)

class WateringPlantWindow(arcade.Window):    

    currentState = None
    humidity = None
    volume = None
    timing = None  
    error = None
    isHappened = False
    isClickWatering = False
    durationWatering = 0

    def __init__(self):
        self.total_time = 35940.0
        self.prev_time = 35940.0
        # self.state = State(self.total_time)
        self.humidity = Humidity(self.total_time)
        self.volume = VolumeWater(100)
        self.timing = Timing()
        self.errorState = Error()
        self.currentState = StateEnum.Off
        self.prevState = self.currentState
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title='Watering Plants')
        arcade.set_background_color(arcade.color.ANTIQUE_WHITE)
        self.ground = arcade.create_rectangle_filled(center_x=SCREEN_WIDTH/2.5, center_y=SCREEN_HEIGHT/1.7, width=800, height=450, color=arcade.color.GUPPIE_GREEN)

        ################# BUTTOM ##############################
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        
        self.g_box = arcade.gui.UIBoxLayout(vertical=False)
        self.on_buttom = arcade.gui.UIFlatButton(text="Включить", width=WIDTH_BUTTOM)
        self.g_box.add(self.on_buttom.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM))
        self.off_buttom = arcade.gui.UIFlatButton(text="Выключить", width=WIDTH_BUTTOM)
        self.g_box.add(self.off_buttom.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM))
        self.watering_buttom = arcade.gui.UIFlatButton(text="Полить", width=WIDTH_BUTTOM)
        self.g_box.add(self.watering_buttom.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM))
        self.fixed = arcade.gui.UIFlatButton(text="Починить", width=WIDTH_BUTTOM)
        self.g_box.add(self.fixed.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM))
        self.addWater = arcade.gui.UIFlatButton(text="Налить воды", width=WIDTH_BUTTOM)
        self.g_box.add(self.addWater.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM))

        ############ LEVEL ###############

        self.timer_text = arcade.Text(
            text="00:00:00",
            start_x=BUTTOM_ON_X + 50,
            start_y=BUTTOM_ON_Y - 12,
            color=arcade.color.ARSENIC,
            font_size=25,
            anchor_x="left",
        )
        self.humidity_text = arcade.Text(
            text="Уровень влажности почвы: 50%",
            start_x=LEVEL_X + 60,
            start_y=LEVEL_Y,
            color=arcade.color.YELLOW_ORANGE,
            font_size=20,
            anchor_x="right",
            multiline=True,
            width=100
        )
        self.volume_text = arcade.Text(
            text="Заполненность водного резервуара: 100 ml",
            start_x=LEVEL_X + 60,
            start_y=LEVEL_Y - 212,
            color=arcade.color.RED,
            font_size=20,
            anchor_x="right",
            multiline=True,
            width=100
        )

        # self.state_text = arcade.Text(
        #     text="Состояние: Выключено",
        #     start_x=LEVEL_X - 100,
        #     start_y=LEVEL_Y,
        #     color=arcade.color.ARSENIC,
        #     font_size=20,
        #     anchor_x="right",
        #     # multiline=True,
        #     # width=100
        # )

        ############ SPRITE ##############

        self.flower = arcade.Sprite('img/plants.png', 0.35)
        self.flower.center_x = IRRIGATOR_X - 143
        self.flower.center_y = IRRIGATOR_Y - 70

        self.irrigator = arcade.Sprite('img/irrigator.png', 0.5)
        self.irrigator.center_x = IRRIGATOR_X
        self.irrigator.center_y = IRRIGATOR_Y

        self.switch_off = arcade.Sprite('img/off.png', 0.1)
        self.switch_off.center_x = BUTTOM_ON_X
        self.switch_off.center_y = BUTTOM_ON_Y

        self.watering = arcade.Sprite('img/watering.png', 0.1)
        self.setupWateringParam(0, 0, 0)

        self.error = arcade.Sprite('img/error.png', 0.2)
        self.error.alpha = 0
        self.error.center_x = IRRIGATOR_X + 128
        self.error.center_y = IRRIGATOR_Y - 65

        self.noWater = arcade.Sprite('img/noWater.png', 0.2)
        self.noWater.alpha = 0
        self.noWater.center_x = IRRIGATOR_X + 130
        self.noWater.center_y = IRRIGATOR_Y - 65

        ############ BUTTOM_FUNC ##############
        self.on_buttom.on_click = self.on_click_on
        self.off_buttom.on_click = self.on_click_off
        self.watering_buttom.on_click = self.on_click_watering
        self.fixed.on_click = self.on_click_fixed
        self.addWater.on_click = self.on_click_add_water

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="left",
                anchor_y="bottom",
                align_x=45,
                align_y=20,
                child=self.g_box)
        )

    def setupWateringParam(self, alpha, change_y, duration):
        self.watering.center_x = self.flower.center_x
        self.watering.center_y = self.flower.center_y + 120
        self.watering.alpha = alpha
        self.watering.change_y = change_y
        self.durationWatering = duration

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
    def stateWatering(self, levelWatering):
        self.currentState = StateEnum.Watering
        print('Current state: {}'.format(self.currentState.name))
        mlToAdd = self.humidity.howMlNeedToGoodHumidity(levelWatering)
        waterToPlants = self.volume.giveWater(mlToAdd)
        self.setupWateringParam(255, _SPEED_CHANGE_Y, duration=waterToPlants//100)
        curHumidity = self.humidity.addHumedity(waterToPlants)
        if waterToPlants < mlToAdd or self.errorState.isError():
            self.isHappened = True
        return curHumidity
    
    """
    Состояние Ожидание
    """
    def stateWait(self, nowState = StateEnum.Wait):
        if nowState == StateEnum.Watering:
            self.stateWatering(_HUMIDITY_LEVEL_MAX)
        if nowState != StateEnum.Wait:
            self.stateCheckSystem()
        
        curHumidity = self.humidity.checkLevelHumedity(self.total_time)
        if self.currentState != StateEnum.NoWater and self.currentState != StateEnum.Error:
            self.currentState = StateEnum.Wait
            print('Current state: {}'.format(self.currentState.name))
            if curHumidity < _HUMIDITY_LEVEL_LOW or self.timing.checkTimeToWatering(self.total_time):
                self.stateWatering(_HUMIDITY_LEVEL_OPTIMAL)
                curHumidity = self.humidity.checkLevelHumedity(self.total_time)
                self.stateCheckSystem()
                if self.currentState != StateEnum.NoWater and self.currentState != StateEnum.Error:
                    self.currentState = StateEnum.Wait
        return curHumidity
    """
    Состояние вкл/выкл
    """
    def on_click_on(self, event):
        self.setupOnOffSprite('img/on.png')
        self.currentState = StateEnum.On
        print('Current state: {}'.format(self.currentState.name))
        self.stateWait(StateEnum.On)

    def on_click_off(self, event):
        self.currentState = StateEnum.Off
        self.setupOnOffSprite('img/off.png')
        self.setupWateringParam(0, 0, 0)
        self.noWater.alpha = 0
        self.error.alpha = 0
        self.textColor(int(self.humidity.checkLevelHumedity(self.total_time)), self.volume.getCurrentVolume())
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
        self.flower.draw()
        self.irrigator.draw()
        self.switch_off.draw()
        self.timer_text.draw()
        self.humidity_text.draw()
        self.volume_text.draw()
        # self.state_text.draw()
        self.watering.draw()
        self.error.draw()
        self.noWater.draw()
        self.manager.draw()

    def textColor(self, humidity, volume):
        color = None
        if humidity <= _HUMIDITY_LEVEL_LOW:
            color = arcade.color.RED
        elif humidity < _HUMIDITY_LEVEL_OPTIMAL:
            color = arcade.color.YELLOW_ORANGE
        elif humidity >= _HUMIDITY_LEVEL_OPTIMAL:
            color = arcade.color.GREEN
        self.humidity_text.text = f"Уровень влажности почвы: {humidity}%"
        self.humidity_text.color = color

        if volume <= _VOLUME_LOW:
            color = arcade.color.RED
        elif volume < _VOLUME_HIGH:
            color = arcade.color.YELLOW_ORANGE
        elif volume >= _VOLUME_HIGH:
            color = arcade.color.GREEN
        self.volume_text.text = f"Заполненность водного резервуара: {volume} ml"
        self.volume_text.color = color

    def update(self, delta_time: float):
        self.switch_off.update()
        self.watering.update()
        self.noWater.update()
        self.error.update()
        self.total_time += delta_time * COEFFICIENT_TIME
        td = timedelta(seconds=self.total_time)
        x = str(td).split('.')
        self.timer_text.text = f"{x[0]}"
        if self.durationWatering > 0:
            # self.volume_text.text = f"Заполненность водного резервуара: {self.volume.getCurrentVolume()} ml"
            self.durationWatering -= delta_time * (COEFFICIENT_TIME / 2)
            if self.watering.center_y < 255:
                self.setupWateringParam(255, _SPEED_CHANGE_Y, self.durationWatering)
        else:
            self.setupWateringParam(0, 0, 0)
        if self.total_time - self.prev_time > _WAIT_TIME and self.currentState == StateEnum.Wait:
            curHumididty = self.stateWait()
            self.textColor(int(curHumididty), self.volume.getCurrentVolume())
            # self.humidity_text.text = f"Уровень влажности почвы: {int(curHumididty)}%"
            # self.volume_text.text = f"Заполненность водного резервуара: {self.volume.getCurrentVolume()} ml"
            self.prev_time = self.total_time
        elif self.total_time - self.prev_time > _WAIT_TIME and (self.currentState == StateEnum.Error or self.currentState == StateEnum.NoWater):
            # self.volume_text.text = f"Заполненность водного резервуара: {self.volume.getCurrentVolume()} ml"
            # self.humidity_text.text = f"Уровень влажности почвы: {int(self.humidity.getCurrentHumidity())}%"
            self.textColor(int(self.humidity.checkLevelHumedity(self.total_time)), self.volume.getCurrentVolume())
            # print('here')
            self.prev_time = self.total_time
            if self.currentState == StateEnum.NoWater:
                self.noWater.alpha = 255
            elif self.currentState == StateEnum.Error:
                self.error.alpha = 255


WateringPlantWindow()
arcade.run()