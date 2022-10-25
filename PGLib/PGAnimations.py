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

from PGLib.PGObject import *


# @class PGAnimation
# @abstract Base class for all animations
#

class PGAnimation:
    def __init__(self, target: PGObject or None, all_screen: bool = False):
        self._screen = pygame.display.get_surface()
        self._allScreen = all_screen
        self._target = None
        self.set_target(target)
        self._group = PGGroup()
        self._group.add(PGObject())
        self._group.sprites()[0].set_rect(self._target.get_rect())

    def save_screen(self):
        self._screen = pygame.display.get_surface()

    def set_target(self, target: PGObject) -> None:
        if self._allScreen:
            self._target = PGObject()
            self._target.set_rect(self._screen.get_rect())
            self._target.set_img(self._screen)
        else:
            self._target = target

    def get_target(self) -> PGObject:
        assert self._allScreen, "Cannot get target!"
        return self._target

    def get_rect(self):
        return self._group.sprites()[0].rect

    def get_size(self) -> tuple[int, int]:
        return self._group.sprites()[0].rect.size

    def effect_in(self, *args, **kwargs):
        return

    def effect_out(self, *args, **kwargs):
        return


class PGFader(PGAnimation):
    def __init__(self, target: PGObject or None, delay: int = 30):
        super().__init__(target, False) if target else super().__init__(None, True)

        self._alpha = 0
        self._fading = False
        self._delay = delay
        img = pygame.Surface(self.get_size(), pygame.SRCALPHA)
        img.fill((0, 0, 0))
        self._group.sprites()[0].set_img(img)

    def _draw(self):
        if self._fading:
            self._group.sprites()[0].image.set_alpha(self._alpha)
        pygame.display.update(self.get_rect())
        pygame.time.delay(self._delay)

    def effect_in(self, trans: int = 20):
        if self._fading:
            return
        self._fading = True
        self._alpha = 0
        while self._alpha < trans:
            self._alpha += 8
            self._draw()
        self._fading = False

    def effect_out(self, trans: int = 20):
        if self._fading:
            return
        self._fading = True
        self._alpha = trans
        while self._alpha > 0:
            self._alpha -= 8
            self._draw()
        self._fading = False


class PGZoomer(PGAnimation):
    def __init__(self, screen: pygame.Surface, obj: pygame.Surface, bg: pygame.Surface, x: int, y: int):
        super().__init__(screen, obj, x, y)
        self._newObj = self.get_obj()
        self._centerX = x + self._obj.get_width() / 2
        self._centerY = y + self._obj.get_height() / 2
        self._orig = bg

    def change_size(self, target_size: (int, int)):
        self._newObj = pygame.transform.smoothscale(self._obj, target_size)
        rect = pygame.Rect(0, 0, target_size[0], target_size[1])
        rect.centerx = self._centerX
        rect.centery = self._centerY
        self._screen.blit(self._newObj, rect)
        pygame.display.update()

    def zoom(self):
        while self._newObj.get_width() < self._obj.get_width() * 2 \
                and self._newObj.get_height() < self._obj.get_height() * 2:
            self.change_size((self._newObj.get_width() + 10, self._newObj.get_height() + 10))
            print(self._newObj.get_width(), self._newObj.get_height())
        self.reset()