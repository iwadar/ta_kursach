import arcade
import arcade.gui
from datetime import timedelta
from state import *

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



class WateringPlantWindow(arcade.Window):    


    def __init__(self):
        self.total_time = 35940.0
        self.prev_time = 35940.0
        self.state = State(self.total_time)
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
        self.stop_watering = arcade.gui.UIFlatButton(text="Прекратить полив", width=WIDTH_BUTTOM)
        self.g_box.add(self.stop_watering.with_space_around(bottom=20, right=SPACE_RIGHT_BUTTOM))
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
            text="Заполненность водного резервуара: 700 ml",
            start_x=LEVEL_X + 60,
            start_y=LEVEL_Y - 212,
            color=arcade.color.GREEN,
            font_size=20,
            anchor_x="right",
            multiline=True,
            width=100
        )

        self.state_text = arcade.Text(
            text="Состояние: Выключено",
            start_x=LEVEL_X - 100,
            start_y=LEVEL_Y,
            color=arcade.color.ARSENIC,
            font_size=20,
            anchor_x="right",
            # multiline=True,
            # width=100
        )

        ############ SPRITE ##############

        self.flower = arcade.Sprite('img/plants.png', 0.35)
        self.flower.center_x = IRRIGATOR_X - 140
        self.flower.center_y = IRRIGATOR_Y - 70

        self.irrigator = arcade.Sprite('img/irrigator.png', 0.5)
        self.irrigator.center_x = IRRIGATOR_X
        self.irrigator.center_y = IRRIGATOR_Y

        self.switch_off = arcade.Sprite('img/off.png', 0.1)
        self.switch_off.center_x = BUTTOM_ON_X
        self.switch_off.center_y = BUTTOM_ON_Y

        self.watering = arcade.Sprite('img/watering.png', 0.1)
        self.setupWateringParam(0, 0)

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
        self.off_buttom.off_click = self.on_click_off
        self.watering_buttom.on_click = self.on_click_watering
        self.stop_watering.on_click = self.on_click_stop
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

    def setupWateringParam(self, alpha, change_y):
        self.watering.center_x = self.flower.center_x
        self.watering.center_y = self.flower.center_y + 120
        self.watering.alpha = alpha
        self.watering.change_y = change_y

    def setupOnOffSprite(self, filename):
        self.switch_off = arcade.Sprite(filename, 0.1)
        self.switch_off.center_x = BUTTOM_ON_X
        self.switch_off.center_y = BUTTOM_ON_Y

    
    """
    Состояние вкл/выкл
    """
    def on_click_on(self, event):
        self.setupOnOffSprite('img/on.png')
        self.state.currentState = StateEnum.On
        self.state.stateWait(self.total_time)

    def on_click_off(self, event):
        self.state.currentState = StateEnum.Off
        self.setupOnOffSprite('img/off.png')


    def on_click_watering(self, event):
        if self.state.currentState == StateEnum.Off:
            return
        self.setupWateringParam(255, -2)
    
    def on_click_stop(self, event):
        if self.state.currentState == StateEnum.Off:
            return
        self.setupWateringParam(0, 0)

    def on_click_fixed(self, event):
        if self.state.currentState == StateEnum.Off:
            return
        pass

    def on_click_add_water(self, event):
        if self.state.currentState == StateEnum.Off:
            return
        pass

    def on_draw(self):
        self.clear()
        self.ground.draw()
        self.flower.draw()
        self.irrigator.draw()
        self.switch_off.draw()
        self.timer_text.draw()
        self.humidity_text.draw()
        self.volume_text.draw()
        self.state_text.draw()
        self.watering.draw()
        self.error.draw()
        self.noWater.draw()
        self.manager.draw()

    def update(self, delta_time: float):
        self.switch_off.update()
        self.total_time += delta_time * COEFFICIENT_TIME
        td = timedelta(seconds=self.total_time)
        x = str(td).split('.')
        self.timer_text.text = f"{x[0]}"
        self.watering.update()
        if self.watering.center_y < 255:
            self.setupWateringParam(255, -2)
        if self.total_time - self.prev_time > _WAIT_TIME and self.state.currentState == StateEnum.Wait:
            curHumididty = self.state.stateWait(self.total_time)
            self.humidity_text.text = f"Уровень влажности почвы: {int(curHumididty)}%"
            self.prev_time = self.total_time
            





WateringPlantWindow()
arcade.run()