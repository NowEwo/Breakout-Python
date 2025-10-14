# type: ignore

import pygame
import pygame.freetype

from objects import prototype
from settings import FONT_SIZE


class Button(prototype.Entity):
    def __init__(self, pos, size, text, onclick=None) -> None:
        self.font = pygame.freetype.Font("assets/fonts/pixelated.ttf", FONT_SIZE)
        self.size = self.base_size = size
        self.text = text
        self.pos = pos

        self.onclick = onclick
        super().__init__()

    def get_collided(self):
        button = pygame.Rect(
            (self.pos),
            (self.size)
        )
        return button.collidepoint(pygame.mouse.get_pos())

    def draw(self, surface, color=(255, 153, 191)):
        mouse = pygame.mouse.get_pos()
        button = pygame.Rect(
            (self.pos),
            (self.size)
        )
        self.text_rect = self.font.get_rect(self.text, size=FONT_SIZE - 10)
        button.center = self.text_rect.center = self.pos

        pygame.draw.rect(surface, (color[0], color[1], color[2], 109 if button.collidepoint(mouse) else 209), button, 0)
        self.font.render_to(surface, self.text_rect, self.text, [c // 3 for c in color], size=FONT_SIZE - 10)
