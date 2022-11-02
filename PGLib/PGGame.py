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

from PGLib.PGButtons import *
from PGLib.PGGlobal import *


class PGScene:
    pass


# @class PGGame
# @abstract Major game flow management.
# @discussion This class handles game initialization, manages all @SSScene objects, and
#             contains the main game loop. All scenes are placed into a list, @self._scenes,
#             but only one scene (the one latest added) will be active. The events and
#             updates of it are then invoked in the game loop, which should be called outside
#             to start the game.

class PGGame:
    def __init__(self, fps: int = 60) -> None:
        # Initialize Display
        pygame.init()
        pygame.display.init()

        self._monitorWidth = pygame.display.Info().current_w
        self._monitorHeight = pygame.display.Info().current_h
        self._screen = pygame.display.set_mode((self._monitorWidth / 2, self._monitorHeight / 2),
                                               pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
        self._fps = fps

        # Start with SSMenu
        self._scenes = []
        self._activeScene = None
        self._prevActiveScene = None
        self._transitionOutComplete = True
        self._transitionInComplete = True

    @property
    def screen(self) -> pygame.Surface:
        return self._screen

    # @function add_scene
    # @abstract Appends a new scene to @self._scenes and activate it.
    # @param scene The scene to add.

    def add_scene(self, scene: PGScene) -> None:
        self._scenes.append(scene)

    # @function remove_scene
    # @abstract Remove a specified scene and activate the topmost one.
    # @param scene The scene to remove.

    def remove_scene(self, scene: PGScene, trans_in: str = "fade", trans_out: str = "fade") -> None:
        self._scenes.remove(scene)
        if scene == self._activeScene:
            self.set_active_scene_index(len(self._scenes) - 1, trans_in, trans_out)

    # set_level
    # eliminate all scenes above @level and activate it thereafter

    def set_active_scene(self, scene: PGScene, trans_in: str = "fade", trans_out: str = "fade") -> None:
        assert scene, "Scene must be valid!"
        assert scene in self._scenes, "Scene must be contained!"
        if self._activeScene:
            self._activeScene.transition_out_method = trans_out
            self._transitionOutComplete = False
        self._prevActiveScene = self._activeScene
        self._activeScene = scene
        self._activeScene.transition_in_method = trans_in
        self._transitionInComplete = False

    def set_active_scene_index(self, index: int = 0, trans_in: str = "fade", trans_out: str = "fade") -> None:
        self.set_active_scene(self._scenes[index], trans_in, trans_out)

    # main game loop
    # processes & updates the active scene every frame

    def _game_loop(self) -> None:
        while True:
            for event in pygame.event.get():
                if self._activeScene:
                    self._activeScene.process_events(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.VIDEORESIZE:
                    self._screen = pygame.display.set_mode((event.w, event.h),
                                                           pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)

            scene = self._activeScene
            if not scene:
                return

            if not self._transitionOutComplete:
                scene = self._prevActiveScene
                self._transitionOutComplete = scene.transition_out()
                if self._transitionOutComplete:
                    if not self._activeScene.background_set():
                        self._activeScene.background = self._screen.copy()
                        self._activeScene.update_background()
                    continue  # Do not update after transition out is complete to prevent "flashing"
            elif not self._transitionInComplete:
                self._transitionInComplete = scene.transition_in()

            scene.update()
            scene.draw()
            clock.tick(self._fps)

    def start(self):
        self._game_loop()


# @class PGScene
# @abstract Base class for all scene objects in the game.
# @discussion This class provides base APIs to be invoked by SSGame and overridden
#             by subclasses. All subclass buttons should eventually be added to
#             @self._buttons and sprites to @self._sprites so that they may be
#             centrally updated. Note that when transitioning to a new scene, the
#             PGAnimations utilities could be employed for visual effects. In addition,
#             a previous scene should ONLY activate a new scene, as the completion
#             would be handled from within.

class PGScene:
    def __init__(self, game: PGGame, bg: pygame.Surface = None):
        self._game = game
        self._game.add_scene(self)
        self._screen = self._game.screen
        self._objects = PGGroup()
        self._transitionInMethod = "none"
        self._transitionOutMethod = "none"
        self._veil = None
        self._background = None
        self._backgroundSet = False
        self.background = bg
        self.update_background()

    @property
    def transition_in_method(self) -> str:
        return self._transitionInMethod

    @transition_in_method.setter
    def transition_in_method(self, method: str) -> None:
        self._transitionInMethod = method

    @property
    def transition_out_method(self) -> str:
        return self._transitionOutMethod

    @transition_out_method.setter
    def transition_out_method(self, method: str) -> None:
        self._transitionOutMethod = method

    @property
    def group(self) -> PGGroup:
        return self._objects

    def add_object(self, obj: PGObject):
        self._objects.add(obj)

    def remove_object(self, obj: PGObject):
        self._objects.remove(obj)

    # TO-DO: Handle dynamic background support

    @property
    def background(self) -> pygame.Surface:
        return self._background

    @background.setter
    def background(self, bg: pygame.Surface = None) -> None:
        if bg:
            self._background = bg
            self._backgroundSet = True
        else:
            self._background = pygame.Surface(self._screen.get_size()).convert_alpha()
            self._background.fill((0, 0, 0))

    def background_set(self) -> bool:
        return self._backgroundSet

    def update_background(self) -> None:
        self._objects.clear(self._screen, self._background)

    @property
    def game(self) -> PGGame:
        return self._game

    # @function activate
    # @abstract Sets the current scene as active in the game.

    def activate(self, trans_in: str = "fade", trans_out: str = "fade") -> None:
        self._game.set_active_scene(self, trans_in, trans_out)

    # @function finish
    # @abstract Entirely remove the scene from the game.

    def finish(self, trans_in: str = "fade", trans_out: str = "fade") -> None:
        self._game.remove_scene(self, trans_in, trans_out)

    # @function process_events
    # @abstract Process all pygame events of its objects.
    # @discussion This must be overridden if other objects have events as well.

    def process_events(self, event: pygame.event.Event) -> None:
        self._objects.process_events(event)

    # @function update
    # @abstract Update all objects in the scene.
    # @discussion Must be overridden if there are other objects (such as fader, background).

    def update(self) -> None:
        self._objects.update()

    def draw(self) -> None:
        pygame.display.update(self._objects.draw(self._screen))

    @staticmethod
    def fit_image(img_path: str, size: (int, int)) -> pygame.Surface:
        return pygame.transform.smoothscale(pygame.image.load(img_path), size)

    #
    # TO-DO: Enhance with decorators
    #

    def transition_in(self) -> bool:
        if self._transitionInMethod == "fade":
            res = self._transition_fade_alpha(True, 255)
        elif self._transitionInMethod == "fade_alpha":
            res = self._transition_fade_alpha(True, 200)
        elif self._transitionInMethod == "zoom":
            res = self._transition_in_zoom()
        else:
            return True
        if res:
            self._veil.kill()
            self._veil = None
        return res

    def _transition_fade_alpha(self, is_in: bool, alpha: int) -> bool:
        if not self._veil:
            veil_img = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
            veil_img.fill((0, 0, 0))
            self._veil = PGObject(self, 0, 0, img=veil_img)
            self._veil.alpha = alpha if is_in else 0
            self._veil.fade(0 if is_in else alpha)
            return False

        if is_in:
            return self._veil.alpha == 0
        return self._veil.alpha == alpha

    def _transition_in_zoom(self) -> bool:
        if not self._veil:
            self._veil = PGObject(self, 0, 0, img=self._screen.convert_alpha().copy())
            self._veil.scale = 0.01
            for s in self._objects.sprites():
                s.alpha = 0
            self._veil.zoom(1)
            return False

        if self._veil.scale == 1:
            for s in self._objects.sprites():
                s.alpha = 255
            return True
        return False

    def transition_out(self) -> bool:
        if self._transitionOutMethod == "fade":
            res = self._transition_fade_alpha(False, 255)
        elif self._transitionOutMethod == "fade_alpha":
            res = self._transition_fade_alpha(False, 200)
        elif self._transitionOutMethod == "zoom":
            return True
        else:
            return True
        if res:
            self._veil.kill()
            self._veil = None
        return res
