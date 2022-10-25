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

import pygame
from typing import Union, Sequence, Callable, Type


class PGScene:
    pass


class PGObject(pygame.sprite.DirtySprite):
    def __init__(self, parent: Type[PGScene] = None, x: int = 0, y: int = 0) -> None:
        super().__init__()
        self._parent = parent
        self.dirty = 1
        self._clickAction = None
        self._hoverAction = None
        self._origImage = None
        self._center = None
        self._x = x
        self._y = y
        if self._parent:
            self._parent.add_object(self)

    def set_x(self, x: int = 0):
        self._x = x
        self.rect.x = x

    def set_y(self, y: int = 0):
        self._y = y
        self.rect.y = y

    def move(self, pos: tuple[int, int]):
        self._center = (pos[0] + self.get_rect().width // 2, pos[0] + self.get_rect().height // 2)
        self.rect.topleft = pos
        self.set_x(self.get_rect().x)
        self.set_y(self.get_rect().y)
        self.dirty = 1

    def update(self) -> None:
        return

    def get_img(self) -> pygame.Surface:
        return self.image

    def set_img(self, img: pygame.Surface) -> None:
        img = img.convert()
        if not self._origImage:
            self._origImage = img
        if not isinstance(self._center, tuple):
            self._center = (self._x + img.get_rect().center[0], self._y + img.get_rect().center[1])
        self.set_rect(img.get_rect(center=self._center))
        self.image = img
        self.dirty = 1

    def rotate(self, angle: float):
        self.set_img(pygame.transform.rotozoom(self._origImage, angle, 1))

    def scale(self, factor: float):
        self.set_img(pygame.transform.smoothscale(self.image, (self.image.get_width() * factor,
                                                               self.image.get_height() * factor)))

    def set_alpha(self, alpha: int) -> None:
        if alpha < 0:
            alpha = 0
        self.image.set_alpha(alpha)

    def set_rect(self, rect: pygame.rect.Rect) -> None:
        self.rect = rect

    def get_rect(self) -> pygame.rect.Rect:
        return self.rect

    def get_pos(self) -> (int, int):
        return self.rect.x, self.rect.y

    def set_pos(self, x: int, y: int) -> None:
        self.rect.topleft = (x, y)
        self.dirty = 1

    def set_pos_prop(self, x: float, y: float) -> None:
        self.set_pos(int((pygame.display.get_surface().get_width() - self.get_rect().width) * x),
                     int((pygame.display.get_surface().get_height() - self.get_rect().height) * y))

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
                x, y = pygame.mouse.get_pos()
                if s.rect.collidepoint(x, y):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        s.on_click()
                        return
                    elif event.type == pygame.MOUSEMOTION:
                        s.on_hover()
                        return

            s.process_events(event)
