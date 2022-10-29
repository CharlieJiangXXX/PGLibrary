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
import pygame.font
from webcolors import name_to_rgb
from PGLib.PGObject import *


# @class PGButton
# @abstract A generic button integrated with PyGame APIs.
# @discussion This is the base class for all game buttons, be it text-based or image-based.
#             It presents onto the screen a pygame surface, the rectangle of which responds
#             to click and hover. All subclasses should fill @self._img with their custom
#             image.

    # @function __init__
    # @abstract Class constructor.
    # @param screen The main display.
    # @param x Top left x coordinate of the button.
    # @param y Top left y coordinate of the button.
    # @param img The image that will be placed onto the screen.


# @class PGTextButton(PGButton)
# @abstract Class representing simple buttons with text.
# @discussion This class takes in text and a font, which it then renders into a surface
#             that will be set to self._img in the parent class constructor.

class PGTextButton(PGObject):
    def __init__(self, parent: Type[PGScene], x: int, y: int, text: str, font: pygame.font.Font = None,
                 bg_color: str = "white", width: int = 100, height: int = 100) -> None:
        if font:
            self._font = font
        else:
            self._font = pygame.font.SysFont("Ariel", 20)
        self._bgColor = name_to_rgb(bg_color)
        self._textStr = text.strip()
        self._text = self._font.render(self._textStr, True, "white" if self.find_text_color() else "black")
        self._textSize = self._text.get_size()
        self._width = width
        self._height = height
        if self._textSize[0] > self._width:
            self._width = self._textSize[0]
        if self._textSize[1] > self._height:
            self._height = self._textSize[1]

        img = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        img.fill(bg_color)
        img.blit(self._text, (self._width / 2 - self._textSize[0] / 2, self._height / 2 - self._textSize[1] / 2))
        super().__init__(parent, x, y, img)

    # @function get_text_color
    # @abstract Determines if text should be black or white based on the background color.

    def find_text_color(self) -> bool:
        luminance = (0.299 * self._bgColor.red + 0.587 * self._bgColor.green + 0.114 * self._bgColor.blue) / 255
        if luminance > 0.5:
            # Black font
            return False
        else:
            # White font
            return True

    def on_click(self) -> None:
        super().on_click()

    def get_text(self):
        return self._textStr
