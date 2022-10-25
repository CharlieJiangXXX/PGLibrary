import time

from PGLib.PGGame import *


class TestScene(PGScene):
    def __init__(self, game: PGGame):
        super().__init__(game)
        self._button1 = PGTextButton(self, 0, 0, "googoo")
        self._button1.set_click_action(self.func1)
        self._button2 = PGTextButton(self, 50, 50, "byebye")
        self._button2.set_click_action(self.func2)
        self._button3 = PGTextButton(self, 200, 200, "hihihi")
        self._button3.set_click_action(self.func1)

    @staticmethod
    def func1():
        print("hi")

    def func2(self):
        self._button2.move((100, 100))
        #self._button2.rotate(30)
        print("hi")


game = PGGame()
scene = TestScene(game)
game.add_scene(scene)
game.start()
