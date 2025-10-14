# type: ignore

import random
import webbrowser

import pygame

from core.scene_manager import Scene
from effects import screen_shake
from objects.gui import mouse, button, hint
from objects.menu import credits
from settings import *
from systems import renderer, audio, logging


class MenuScene(Scene):
    def __init__(self) -> None:
        self.logger = logging.Logger("scenes.menu")
        self.color = [255, 153, 191] if random.randint(0,10) != 1 else [random.randint(100,255) for _ in range(3)]
        super().__init__()

    def run(self):
        self.game.update_window_title("Main Menu")

        self.shaders = renderer.Renderer("crt")

        self.mouse = mouse.Mouse()

        self.audio = audio.AudioEngine()
        self.audio.play_file("assets/sounds/music/audio_menu.wav", True)

        self.font = pygame.freetype.Font("assets/fonts/pixelated.ttf", FONT_SIZE)
        self.text = "Broke Out"

        self.shake = screen_shake.ScreenShake()
        self.shake.start(15, 5)

        self.hint = hint.HintElement()

        self.titley = RENDER_HEIGHT // 2
        self.titlesize = 36

        self.credits_object = credits.Credits()
        self.credits = False

        center = self.game.window.get_rect().center

        self.menu_buttons = {
            "Play": button.Button((center[0], center[1]), [305, 51], "Play"),
            "Credits": button.Button((center[0] - 77, center[1] + 53), [151, 51], "Credits"),
            "Web": button.Button((center[0] + 77, center[1] + 53), [151, 51], "Website"),
            "Quit": button.Button((center[0], center[1] + 106), [305, 51], "Quit"),
        }
        self.credits_back_button = button.Button((95, 95), [51, 51], "ESC")

        self.mousex, self.mousey = 400, 300
        self.scroll = 0

        self.hint_opacity = 255

        self.text_rect = None
        self.egg = False

        self.game.discordrpc.set_rich_presence("Navigating in menus", f"Breakout Version {VERSION}")
        self.hint.show_hint(f"Connected to Discord", 120, 15)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.credits:
                if self.menu_buttons["Play"].get_collided():
                    self.game.scene_manager.set_active_scene("level")
                elif self.menu_buttons["Credits"].get_collided():
                    self.scroll = 0
                    self.egg = random.randint(0, 10) == 5 or DEBUG_EASTER_EGG
                    self.logger.log(f"Switching to credits with easter egg = {self.egg}")
                    self.credits = True
                elif self.menu_buttons["Web"].get_collided():
                    self.logger.log("Opening website in user's default browser")
                    webbrowser.open("https://nowewo.github.io/BrokeOut/")
                elif self.menu_buttons["Quit"].get_collided():
                    return False
                elif self.credits_back_button.get_collided():
                    self.logger.log("Disabling credits")
                    self.credits = False
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll += event.y * 25

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.credits:
                    self.logger.log("Disabling credits")
                    self.credits = False
                if event.key == pygame.K_SPACE:
                    self.game.scene_manager.set_active_scene("menu", False)
        return True

    def compute_surface_offset(self):
        if pygame.mouse.get_focused():
            self.mousex, self.mousey = pygame.mouse.get_pos()
        else:
            if self.mousex > self.game.window.get_rect().center[0]:
                self.mousex += (self.game.window.get_rect().center[0] - self.mousex) * 0.1
            if self.mousey > self.game.window.get_rect().center[1]:
                self.mousey += (self.game.window.get_rect().center[1] - self.mousey) * 0.1
            if self.mousex < self.game.window.get_rect().center[0]:
                self.mousex -= (self.mousex - self.game.window.get_rect().center[0]) * 0.1
            if self.mousey < self.game.window.get_rect().center[1]:
                self.mousey -= (self.mousey - self.game.window.get_rect().center[1]) * 0.1

    def update(self):
        if self._get_ticks() % 26 == 0:
            self.shaders.set_curvature(0.4)

        if (self.text_rect != None):
            if self.text_rect.center[1] > 100:
                self.titley += (100 - self.titley) * 0.1

        if self.titlesize < 50:
            self.titlesize += (51 - self.titlesize) * 0.1

        if not DEBUG_DISABLE_OFFSET:
            self.compute_surface_offset()

        target_min = -200 if not self.egg else -1
        target_max = -25

        if self.scroll < target_min:
            self.scroll += (target_min - self.scroll) * 0.1
        elif self.scroll > target_max:
            self.scroll += (target_max - self.scroll) * 0.1

        self.hint.update()

    def draw(self):
        shake = self.shake.get_offset()

        bg = [c // 3 for c in self.color]
        self.game.window.fill(bg)

        self.surface = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA, 32)

        if not self.credits:
            # Display main menu
            [self.menu_buttons[element].draw(self.surface, self.color) for element in self.menu_buttons]
        else:
            # Credits surface
            self.credits_object.draw(self)
            pygame.draw.rect(self.surface, (bg[0], bg[1], bg[2], 51), (0, 0, RENDER_WIDTH, 131))

            self.credits_back_button.draw(self.surface, self.color)

        # Title element ("Broke Out")
        self.text_rect = self.font.get_rect(self.text, size=self.titlesize)
        self.text_rect.center = (self.surface.get_rect().center[0], self.titley)

        self.font.render_to(self.surface, self.text_rect, self.text, self.color, size=self.titlesize)

        # Bottom text
        self.text_rect = self.font.get_rect(f"(c) 2025-2026 Broke Team - Version {VERSION} ({RELEASE_STATE})", size=12)
        self.text_rect.center = (self.surface.get_rect().center[0], RENDER_HEIGHT - 15)

        self.font.render_to(self.game.window, self.text_rect,
                            f"(c) 2025-2026 Broke Team - Version {VERSION} ({RELEASE_STATE})", self.color, size=12)

        background = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA, 32)

        for line in range(17):
            for column in range(19):
                pygame.draw.rect(background, (self.color[0], self.color[1], self.color[2],  25), (-25 + (column * 51), -40 + (line * 51) - (self._get_ticks()//4)%50, 45, 45))

        self.hint.draw()

        self.game.window.blit(background,
                              (1 + ((self.mousex - 400) // 25) + shake[0], 1 + ((self.mousey - 300) // 20) + shake[1]))

        self.game.window.blit(background,
                              (1 + ((self.mousex - 400) // 20) + shake[0], 1 + ((self.mousey - 300) // 20) + shake[1]))
        self.game.window.blit(self.surface,
                              (1 + ((self.mousex - 400) // 10) + shake[0], 1 + ((self.mousey - 300) // 10) + shake[1]))

        self.mouse.draw()

        self.shaders.render_frame()
