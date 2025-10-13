#type: ignore

from core.scene_manager import Scene
from systems import renderer

from settings import *

import pygame
import pygame.freetype


class DevelopmentScene(Scene):
    # noinspection PyDefaultArgument
    def __init__(self) -> None:
        self.color = (159, 0, 0)
        self.shaders = renderer.Renderer()

        super().__init__()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def update(self):
        pass

    def draw(self):
        self.game.window.fill(self.color)

        surface = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA)

        # DO DEV THINGS

        self.game.window.blit(surface, (0, 0))

        self.shaders.render_frame()
