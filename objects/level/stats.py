# type: ignore

import pygame
import pygame.freetype

from objects import prototype
from settings import RENDER_WIDTH, FONT_SIZE


class StatsElement(prototype.Entity):
    def __init__(self) -> None:
        self.displayed_score = 0

        self.font = pygame.freetype.Font("assets/fonts/pixelated.ttf", FONT_SIZE)

        super().__init__()

    def update(self):
        # Animate score (interpolation)
        if self.displayed_score < self.scene.score:
            diff = (self.scene.score - self.displayed_score) // 2
            self.displayed_score += max(1, diff)
        elif self.displayed_score > self.scene.score:
            diff = (self.displayed_score - self.scene.score) // 2
            self.displayed_score -= max(1, diff)

    def draw(self):
        score_text = f'score: {self.displayed_score} | Lifes: {self.scene.lives}'
        self.font.render_to(
            self.game.window,
            (31, 13),
            score_text,
            self.scene.color
        )


class ProgressBar(prototype.Entity):
    def __init__(self) -> None:
        self.progress = 0

        super().__init__()

    def update(self):
        target = int((1 - (len(self.scene.brick_group.bricks) / (9 * 14))) * RENDER_WIDTH)
        speed = 0.1

        self.progress += (target - self.progress) * speed

    def draw(self):
        self.progress_bar = pygame.Rect(
            0, 0,
            self.progress, 3
        )
        pygame.draw.rect(self.game.window, self.scene.color, self.progress_bar, 0)
