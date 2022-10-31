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
