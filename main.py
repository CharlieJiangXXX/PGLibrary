import pygame

from PGLib.PGGame import *


class TestScene(PGScene):
    def __init__(self, game: PGGame):
        bg = pygame.Surface(game.screen.get_size(), pygame.SRCALPHA)
        bg.fill((50, 50, 100))
        super().__init__(game, bg)
        self._button1 = PGTextButton(self, 0, 0, "googoo")
        self._button1.connect_click(self.func1)
        self._button2 = PGTextButton(self, 50, 50, "byebye")
        self._button2.connect_click(self.func2)
        self._button3 = PGTextButton(self, 200, 200, "hihihi")
        self._button3.connect_click(self.func3)
        self._button4 = PGTextButton(self, 400, 400, "leave")
        self._button4.connect_click(self.func4)

    def func1(self):
        self._button1.fade(150)
        self._button1.fade(255)

    def func2(self):
        self._button2.move((0, 300), 5)

    def func3(self):
        self._button3.fade(150)
        self._button3.fade(255)
        self._button3.zoom(2)
        self._button3.zoom(1)

    def func4(self):
        Scene2(self.game).activate(trans_in="none", trans_out="fade_alpha")


class Scene2(PGScene):
    def __init__(self, game: PGGame):
        super().__init__(game)
        self._button1 = PGTextButton(self, 0, 0, "googoo")
        self._button1.connect_click(self.finish, "fade_alpha", "none")


game = PGGame()
TestScene(game).activate()
game.start()
