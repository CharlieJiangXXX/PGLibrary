#
# MIT License
#
# Copyright (c) 2022 cjiang. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import math

import pygame
from typing import Union, Sequence, Callable, Type
from pygame.mask import from_surface
import operator
from PGLib.PGGlobal import *


class PGScene:
    pass


class PGObject(pygame.sprite.DirtySprite):
    def __init__(self, parent: Type[PGScene], x: int = 0, y: int = 0, img: pygame.Surface = None) -> None:
        super().__init__()
        self._parent = parent
        self.dirty = 2
        self._clickAction = None
        self._hoverAction = None
        if not img:
            self.image = pygame.Surface((0, 0), pygame.SRCALPHA)
            self._origImage = None
            self._imageSet = False
        else:
            self.image = img.convert_alpha()
            self._origImage = img
            self._imageSet = True

        self.rect = self.image.get_rect(topleft=(x, y))
        self._posChanges = []

        self._angle = 0
        self._angleChanges = []

        self._scale = 1
        self._scaleChanges = []

        self._alpha = 255
        self._alphaChanges = []

        if self._parent:
            self._parent.add_object(self)

    def update(self, *args, **kwargs) -> None:
        return

    @property
    def img(self) -> pygame.Surface:
        return self.image

    @img.setter
    def img(self, img: pygame.Surface) -> None:
        img = img.convert_alpha()
        if not self._imageSet:
            self._origImage = img
            self._imageSet = True
        self.image = img
        self.rect = img.get_rect(center=self.rect.center)

    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, angle: float):
        self._angle = angle
        self.img = pygame.transform.rotozoom(self._origImage, -self._angle, 1)

    def normalize_angle(self):
        self._angle %= 360

    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, factor: float) -> None:
        self._scale = factor
        self.img = pygame.transform.smoothscale(self._origImage, (self._origImage.get_width() * factor,
                                                                  self._origImage.get_height() * factor))

    @property
    def alpha(self) -> int:
        return self._alpha

    @alpha.setter
    def alpha(self, alpha: int) -> None:
        if alpha < 0:
            alpha = 0
        self.image.set_alpha(alpha)
        self._origImage.set_alpha(alpha)
        self._imageSet = True
        self._alpha = alpha

    # Animations
    # TO-DO: speed customization, unification with delay, inertia

    def fade(self, alpha: int) -> None:
        self._alphaChanges.append(alpha)

    def _test_fade(self) -> None:
        if not self._alphaChanges:
            return
        if self._alphaChanges[0] == self.alpha:
            self._alphaChanges.pop(0)
            return

        if self.alpha > self._alphaChanges[0]:
            self.alpha = self.alpha - 8 if self._alphaChanges[0] < self.alpha - 8 else self._alphaChanges[0]
        elif self.alpha < self._alphaChanges[0]:
            self.alpha = self.alpha + 8 if self._alphaChanges[0] > self.alpha + 8 else self._alphaChanges[0]

    def zoom(self, factor: float):
        self._scaleChanges.append(factor)

    def _test_zoom(self) -> None:
        if not self._scaleChanges:
            return
        if self._scaleChanges[0] == self.scale:
            self._scaleChanges.pop(0)
            return

        if self.scale > self._scaleChanges[0]:
            self.scale = self.scale - 0.2 if self._scaleChanges[0] < self.scale - 0.2 else self._scaleChanges[0]
        elif self.scale < self._scaleChanges[0]:
            self.scale = self.scale + 0.2 if self._scaleChanges[0] > self.scale + 0.2 else self._scaleChanges[0]

    def rotate(self, angle: float) -> None:
        self._angleChanges.append(angle)

    def _test_rotate(self) -> None:
        if not self._angleChanges:
            return
        if self._angleChanges[0] == self.angle:
            self._angleChanges.pop(0)
            self.normalize_angle()
            return

        if self.angle > self._angleChanges[0]:
            self.angle = self.angle - 3 if self._angleChanges[0] < self.angle - 3 else self._angleChanges[0]
        if self.angle < self._angleChanges[0]:
            self.angle = self.angle + 3 if self._angleChanges[0] > self.angle + 3 else self._angleChanges[0]

    def move(self, pos: tuple[int, int], time: float = 1) -> None:
        dx, dy = tuple(map(lambda x, y: (x - y) / (clock.get_fps() * time), pos, self.rect.topleft))
        dx = math.ceil(dx) if dx > 0 else math.floor(dx)
        dy = math.ceil(dy) if dy > 0 else math.floor(dy)
        self._posChanges.append((pos, dx, dy))


    def _test_move(self) -> None:
        if not self._posChanges:
            return
        if self._posChanges[0][0] == self.pos:
            self._posChanges.pop(0)
            return

        if self.pos != self._posChanges[0][0]:
            dx = self._posChanges[0][1]
            dy = self._posChanges[0][2]
            x = self._posChanges[0][0][0]
            y = self._posChanges[0][0][1]
            temp_x = self.pos[0] + dx
            temp_y = self.pos[1] + dy
            if (dx < 0 and temp_x < x) or (dx > 0 and temp_x > x):
                temp_x = x
            if (dy < 0 and temp_y < y) or (dy > 0 and temp_y > y):
                temp_y = y
            self.pos = (temp_x, temp_y)

    @property
    def pos(self) -> (int, int):
        return self.rect.x, self.rect.y

    @pos.setter
    def pos(self, pos: tuple[int, int]) -> None:
        self.rect.topleft = pos

    def set_pos_prop(self, x: float, y: float) -> None:
        self.pos = (int((pygame.display.get_surface().get_width() - self.rect.width) * x),
                    int((pygame.display.get_surface().get_height() - self.rect.height) * y))

    def connect_click(self, action: Callable) -> None:
        if callable(action):
            self._clickAction = action

    def connect_hover(self, action: Callable) -> None:
        if callable(action):
            self._hoverAction = action

    # @function _on_click
    # @abstract Click action to be override in subclasses.
    # @discussion Should a subclass have a click action that all its subclasses will
    #             inherit, it must override this function in addition to setting
    #             @self._clickAction.

    def on_click(self) -> None:
        if self._clickAction:
            self._clickAction()

    # @function _on_hover
    # @abstract Hover action to be override in subclasses.
    # @discussion Should a subclass have a hover action that all its subclasses will
    #             inherit, it must override this function in addition to setting
    #             @self._hoverAction.

    def on_hover(self) -> None:
        if self._hoverAction:
            self._hoverAction()

    def collidepoint(self, p: tuple[int, int]) -> bool:
        mask = from_surface(self.image)
        try:
            mask.get_at((p[0] - self.pos[0], p[1] - self.pos[1]))
            return True
        except IndexError:
            return False

    def process_events(self, event: pygame.event.Event) -> None:
        return


class PGGroup(pygame.sprite.LayeredDirty):
    def __init__(self, *sprites: Union[PGObject, Sequence[PGObject]]) -> None:
        super().__init__(*sprites)

    def process_events(self, event: pygame.event.Event) -> None:
        if not self.sprites():
            return

        for s in reversed(self.get_sprites_from_layer(self.get_top_layer())):
            if not isinstance(s, PGObject):
                continue

            if event.type == pygame.MOUSEBUTTONDOWN | pygame.MOUSEMOTION:
                # Collision is still not accurate
                if s.collidepoint(pygame.mouse.get_pos()):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        s.on_click()
                        return
                    elif event.type == pygame.MOUSEMOTION:
                        s.on_hover()
                        return

            s.process_events(event)

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        for s in self.sprites():
            s._test_fade()
            s._test_rotate()
            s._test_zoom()
            s._test_move()
