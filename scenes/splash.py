#type: ignore

from core.scene_manager import Scene
from systems import renderer

from settings import *

import pygame
import pygame.freetype


class SplashScene(Scene):
    # noinspection PyDefaultArgument
    def __init__(self, color=[0, 0, 0]) -> None:
        super().__init__()
        self.color = color

        self.shaders = renderer.Renderer()
        self.fadeout = 0
        self.text_opacity = 0

        self.font = pygame.freetype.Font("assets/fonts/pixelated.ttf", FONT_SIZE)
        self.text = "Made with love by Broke Team"
        self.text_color = [255, 255, 255]

        self.song_played = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def update(self):
        if self.text_opacity < 255 and self._get_ticks() > 60:
            self.text_opacity += (255 - self.text_opacity) * 0.1
            if not self.song_played:
                self.text = "Made with love by Broke Team"
                self.song_played = True
                pygame.mixer.music.load("assets/sounds/sfx/splash.mp3")
                pygame.mixer.music.play()
        if self._get_ticks() > 120:
            self.text = "(c) • 2025-2026"
        if self._get_ticks() == 180: self.text_opacity = 0
        if self._get_ticks() > 180:
            self.fadeout += (255 - self.fadeout) * 0.03
            self.text_color = [255, 153, 191]
            indice = (self._get_ticks() - 180) // 4
            self.text = "Broke Out"[0:int(indice)]
        if self._get_ticks() > 220:
            self.game.scene_manager.set_active_scene(self.game.menu_scene)

    def draw(self):
        self.game.window.fill(self.color)

        surface = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA)

        overlay = pygame.Rect(
            0, 0,
            RENDER_WIDTH, RENDER_HEIGHT
        )
        pygame.draw.rect(surface, (255 // 3, 153 // 3, 191 // 3, self.fadeout), overlay, 0)

        text_rect = self.font.get_rect(self.text, size=36)
        text_rect.center = surface.get_rect().center

        self.font.render_to(surface, text_rect, self.text,
                            (self.text_color[0], self.text_color[1], self.text_color[2], self.text_opacity), size=36)

        self.game.window.blit(surface, (0, 0))

        self.shaders.render_frame()
