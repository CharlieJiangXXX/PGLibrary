#
# Released under "The BSD 3-Clause License"
#
# Copyright © 2022 cjiang. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of mosquitto nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
import math

import pygame
from typing import Union, Sequence, Callable, Type
from pygame.mask import from_surface
import operator


class PGScene:
    pass


class PGObject(pygame.sprite.DirtySprite):
    def __init__(self, parent: Type[PGScene], x: int = 0, y: int = 0, img: pygame.Surface = None) -> None:
        super().__init__()
        self._parent = parent
        self.add(parent.get_group())
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

    def update(self) -> None:
        return

    def get_img(self) -> pygame.Surface:
        return self.image

    def set_img(self, img: pygame.Surface) -> None:
        img = img.convert_alpha()
        if not self._imageSet:
            self._origImage = img
            self._imageSet = True
        self.image = img
        self.set_rect(img.get_rect(center=self.rect.center))

    def set_angle(self, angle: float):
        self._angle = angle
        self.set_img(pygame.transform.rotozoom(self._origImage, -self._angle, 1))

    def set_scale(self, factor: float):
        self._scale = factor
        self.set_img(pygame.transform.smoothscale(self._origImage, (self._origImage.get_width() * factor,
                                                                    self._origImage.get_height() * factor)))

    def set_alpha(self, alpha: int) -> None:
        if alpha < 0:
            alpha = 0
        self.image.set_alpha(alpha)
        self._origImage.set_alpha(alpha)
        self._imageSet = True
        self._alpha = alpha

    def get_alpha(self) -> int:
        return self._alpha

    # Animations
    # TO-DO: speed customization, unification with delay, inertia

    def fade(self, alpha: int) -> None:
        self._alphaChanges.append(alpha)

    def _test_fade(self) -> None:
        if not self._alphaChanges:
            return
        if self._alphaChanges[0] == self._alpha:
            self._alphaChanges.pop(0)
            return

        if self._alpha > self._alphaChanges[0]:
            self.set_alpha(self._alpha - 8 if self._alphaChanges[0] < self._alpha - 8 else self._alphaChanges[0])
        elif self._alpha < self._alphaChanges[0]:
            self.set_alpha(self._alpha + 8 if self._alphaChanges[0] > self._alpha + 8 else self._alphaChanges[0])

    def zoom(self, factor: float):
        self._scaleChanges.append(factor)

    def _test_zoom(self) -> None:
        if not self._scaleChanges:
            return
        if self._scaleChanges[0] == self._scale:
            self._scaleChanges.pop(0)
            return

        if self._scale > self._scaleChanges[0]:
            self.set_scale(self._scale - 0.2 if self._scaleChanges[0] < self._scale - 0.2 else self._scaleChanges[0])
        elif self._scale < self._scaleChanges[0]:
            self.set_scale(self._scale + 0.2 if self._scaleChanges[0] > self._scale + 0.2 else self._scaleChanges[0])

    def rotate(self, angle: float) -> None:
        self._angleChanges.append(angle)

    def _test_rotate(self) -> None:
        if not self._angleChanges:
            return
        if self._angleChanges[0] == self._angle:
            self._angleChanges.pop(0)
            return

        if self._angle > self._angleChanges[0]:
            self.set_angle(self._angle - 3 if self._angleChanges[0] < self._angle - 3 else self._angleChanges[0])
        if self._angle < self._angleChanges[0]:
            self.set_angle(self._angle + 3 if self._angleChanges[0] > self._angle + 3 else self._angleChanges[0])

    def move(self, pos: tuple[int, int]) -> None:
        dx, dy = tuple(map(operator.sub, pos, self.rect.topleft))
        dx = math.ceil(dx / 50)
        dy = math.ceil(dy / 50)
        self._posChanges.append((pos, dx, dy))

    def _test_move(self) -> None:
        if not self._posChanges:
            return
        if self._posChanges[0][0] == self.get_pos():
            self._posChanges.pop(0)
            return

        if self.get_pos() != self._posChanges[0][0]:
            dx = self._posChanges[0][1]
            dy = self._posChanges[0][2]
            x = self._posChanges[0][0][0]
            y = self._posChanges[0][0][1]
            temp_x = self.get_pos()[0] + dx
            temp_y = self.get_pos()[1] + dy
            if (dx < 0 and temp_x < x) or (dx > 0 and temp_x > x):
                temp_x = x
            if (dy < 0 and temp_y < y) or (dy > 0 and temp_y > y):
                temp_y = y
            self.set_pos((temp_x, temp_y))

    def set_rect(self, rect: pygame.rect.Rect) -> None:
        self.rect = rect

    def get_rect(self) -> pygame.rect.Rect:
        return self.rect

    def get_pos(self) -> (int, int):
        return self.rect.x, self.rect.y

    def set_pos(self, pos: tuple[int, int]) -> None:
        self.rect.topleft = pos

    def set_pos_prop(self, x: float, y: float) -> None:
        self.set_pos((int((pygame.display.get_surface().get_width() - self.get_rect().width) * x),
                     int((pygame.display.get_surface().get_height() - self.get_rect().height) * y)))

    def set_click_action(self, action: Callable) -> None:
        if callable(action):
            self._clickAction = action

    def set_hover_action(self, action: Callable) -> None:
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
            mask.get_at((p[0] - self.get_pos()[0], p[1] - self.get_pos()[1]))
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
