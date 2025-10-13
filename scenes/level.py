#type: ignore

from objects.level import player, ball, brick
from objects.level.stats import StatsElement, ProgressBar
from objects.gui import hint

from effects import screen_shake

from core.scene_manager import Scene
from systems import renderer, audio

from settings import *

import random

import pygame

class LevelScene(Scene):
    def __init__(self) -> None:
        super().__init__()

    def run(self):
        self.game.update_window_title("Classic Game")

        self.audio = audio.AudioEngine()
        self.audio.play_file("assets/sounds/music/audio0.opus", True)

        self.font = pygame.freetype.Font("assets/fonts/pixelated.ttf", FONT_SIZE)

        self.bounds = {
            "x_min": 0,
            "y_min": 0,
            "x_max": RENDER_WIDTH,
            "y_max": RENDER_HEIGHT
        }

        self.game_started = False
        self.lives = INITIAL_LIVES if not DEBUG_INFINITE_LIVES else -1
        self.level = 1
        self.score = 0

        self.color = [255, 153, 191]

        self.screen_shake = screen_shake.ScreenShake()
        self.offset_x, self.offset_y = 0,0

        self.player = player.Player()
        self.ball = ball.Ball()

        self.brick_group = brick.BrickGroup()
        self.brick_group.generate_bricks()
        
        self.stats = [StatsElement(), ProgressBar(), hint.HintElement()]

        self.shaders = renderer.Renderer("crt")

        pygame.mouse.set_visible(False)

        if DEBUG_GAME_AUTOSTART:
            self.ball.on_player = False
            self.ball.set_velocity_by_angle(60)
            self.game_started = True

        self.LoseMessages = [
            "Oops", "Maybe do better next time", "Actually that was fun",
            "Ew you don't play very well", "You have to touch the ball actually",
            "Stop being bad, it makes me sad", "0/20", "Lives are falling like this ball"
        ]

        self.game.discordrpc.set_rich_presence("Playing in classic mode", f"Level {self.level}")
    
    def background_color(self):
        return [c//3 for c in self.color]
    
    def reset_game(self):
        self.screen_shake.start(10, 5)

        self.brick_group.generate_bricks()

        self.color = [255, 153, 191]
        self.game_started = False
        self.level = 1
        self.lives = 3
        self.score = 0

        self.stats[2].show_hint(f"Level {self.level}", size=24)
        self.game.discordrpc.set_rich_presence("Playing in classic mode", f"Level {self.level}")

    def trigger_next_level(self):
        self.screen_shake.start(10, 5)

        self.color = [random.randint(150,255) for _ in range(3)]
        self.level += 1
        self.lives += 1

        self.stats[2].show_hint(f"Level {self.level}", size=24)
        self.game.discordrpc.set_rich_presence("Playing in classic mode", f"Level {self.level}")
    
    def trigger_lose(self):
        if self.lives != 1:
                self.stats[2].show_hint(random.choice(self.LoseMessages), size=24)
                self.lives -= 1
                self.logger.log(
                    f"Player lose this round, now having {self.lives} more lives"
                )
        else:
            self.logger.log("Player lose the game, resetting all states")
            self.reset_game()
        self.ball.on_player = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.ball.on_player:
                    self.ball.on_player = False
                    self.ball.set_velocity_by_angle(60)

                    if not self.game_started:
                        self.level = 1
                        self.game_started = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.scene_manager.set_active_scene(self.game.menu_scene)
            elif event.type == 3159:
                self.ball.gravity_enabled = not self.ball.gravity_enabled
        return True

    def update(self):
        #self.color = [random.randint(150,255) for i in range(3)]

        [i.update() for i in self.stats]
        self.brick_group.update()
        self.player.update()
        self.ball.update()
    
    def draw(self):
        self.offset_x, self.offset_y = self.screen_shake.get_offset()

        self.game.window.fill([c // 3 for c in self.color])

        self.surface = pygame.Surface(self.game.window.get_size(), pygame.SRCALPHA)

        self.brick_group.draw()
        self.player.draw()
        self.ball.draw()

        [i.draw() for i in self.stats]

        self.game.window.blit(self.surface, [self.offset_x,self.offset_y])

        self.shaders.render_frame()