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

from PGLib.PGButtons import *


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
    def __init__(self, delay: int = 60) -> None:
        # Initialize Display
        pygame.init()
        pygame.display.init()

        self._monitorWidth = pygame.display.Info().current_w
        self._monitorHeight = pygame.display.Info().current_h
        self._screen = pygame.display.set_mode((self._monitorWidth / 2, self._monitorHeight / 2),
                                               pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
        self._delay = delay

        # Start with SSMenu
        self._scenes = []
        self._activeScene = None
        self._activeSceneChangeComplete = True
        self.set_active_scene(PGScene(self, transition="none"))

    def get_screen(self) -> pygame.Surface:
        return self._screen

    # @function add_scene
    # @abstract Appends a new scene to @self._scenes and activate it.
    # @param scene The scene to add.

    def add_scene(self, scene: PGScene) -> None:
        self._scenes.append(scene)

    # @function remove_scene
    # @abstract Remove a specified scene and activate the topmost one.
    # @param scene The scene to remove.

    def remove_scene(self, scene: PGScene) -> None:
        if scene != self._activeScene:
            self._scenes.remove(scene)
            return
        self.set_active_scene_index(len(self._scenes) - 1)

    # set_level
    # eliminate all scenes above @level and activate it thereafter

    def set_active_scene(self, scene: PGScene) -> None:
        assert scene, "Scene must be valid!"
        assert scene in self._scenes, "Scene must be contained!"
        if self._activeScene:
            self._activeScene.transition_out()
        self._activeScene = scene
        self._activeSceneChangeComplete = False

    def set_active_scene_index(self, index: int = 0) -> None:
        self.set_active_scene(self._scenes[index])

    # main game loop
    # processes & updates the active scene every frame

    def _game_loop(self) -> None:
        while True:
            for event in pygame.event.get():
                if self._activeScene:
                    self._activeScene.process_events(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.VIDEORESIZE:
                    self._screen = pygame.display.set_mode((event.w, event.h),
                                                           pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)

            if self._activeScene:
                if not self._activeSceneChangeComplete:
                    self._activeScene.update()
                    self._activeSceneChangeComplete = self._activeScene.transition_in()
                self._activeScene.update()
                self._activeScene.draw()
            pygame.time.delay(self._delay)

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
    def __init__(self, game: PGGame, bg: pygame.Surface = None, transition: str = "fade"):
        self._game = game
        self._game.add_scene(self)
        self._screen = self._game.get_screen()
        self._objects = PGGroup()
        self._transition = transition
        self._veil = None
        self._background = None
        self.set_background(bg)
        self.update_background()

    def get_group(self):
        return self._objects

    def add_object(self, obj: PGObject):
        self._objects.add(obj)

    def remove_object(self, obj: PGObject):
        self._objects.remove(obj)

    def set_background(self, bg: pygame.Surface = None) -> None:
        if bg:
            self._background = bg
        else:
            self._background = pygame.Surface(self._screen.get_size()).convert_alpha()
            self._background.fill((0, 0, 0))

    def update_background(self) -> None:
        self._objects.clear(self._screen, self._background)

    def get_game(self) -> PGGame:
        return self._game

    # @function activate
    # @abstract Sets the current scene as active in the game.

    def activate(self) -> None:
        self._game.set_active_scene(self)

    # @function finish
    # @abstract Entirely remove the scene from the game.

    def finish(self) -> None:
        self._game.remove_scene(self)

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

    # TO-DO: Wrap these into a transition module
    # Fade into and out of the scene

    def transition_in(self) -> bool:
        if self._transition == "fade":
            if not self._veil:
                veil_img = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
                veil_img.fill((0, 0, 0))
                self._veil = PGObject(self, 0, 0, img=veil_img)
                self._veil.fade(0)
                return False
            if self._veil.get_alpha() == 0:
                self._veil.kill()
                self._objects.remove(self._veil)
                return True
            return False
        elif self._transition == "zoom":
            return True
        return True

    def transition_out(self) -> None:
        pass
        #if self._transition == "fade":
            #fader = PGFader(delay=10)
            #fader.effect_out(255)
        #elif self._transition == "zoom":
            #PGZoomer()
