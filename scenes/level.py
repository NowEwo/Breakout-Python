#type: ignore

from objects.level import player
from objects.level.stats import StatsElement, ProgressBar

from core.scene_manager import Scene
from systems import renderer, audio

from settings import *

import pygame

class LevelScene(Scene):
    def __init__(self) -> None:
        super().__init__()

    def run(self):

        self.audio = audio.AudioEngine()
        self.audio.play_file("assets/sounds/music/audio0.opus", True)

        self.bounds = {
            "x_min": 0,
            "y_min": 0,
            "x_max": RENDER_WIDTH,
            "y_max": RENDER_HEIGHT
        }
        self.lives = INITIAL_LIVES
        self.score = 0

        self.color = [255, 153, 191]

        self.offset_x, self.offset_y = 0,0

        self.player = player.Player()
        self.bricks = [0 for i in range(15)]
        self.stats = [StatsElement(), ProgressBar()]

        self.shaders = renderer.Renderer("crt")

        pygame.mouse.set_visible(False)

        self.game.discordrpc.set_rich_presence("Playing in sandbox mode", f"Breakout Version {VERSION}")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.scene_manager.set_active_scene(self.game.menu_scene)
        return True

    def update(self):
        [i.update() for i in self.stats]
        self.player.update()
    
    def draw(self):
        self.game.window.fill([c // 3 for c in (255, 153, 191)])

        self.surface = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA)

        self.player.draw()

        [i.draw() for i in self.stats]

        self.game.window.blit(self.surface, [0,0])

        self.shaders.render_frame()