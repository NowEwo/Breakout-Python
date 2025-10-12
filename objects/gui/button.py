#type: ignore

from objects import prototype

from settings import FONT_SIZE

import pygame
import pygame.freetype

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
    
    def draw(self, surface):

        mouse = pygame.mouse.get_pos()
        button = pygame.Rect(
            (self.pos),
            (self.size)
        )
        self.text_rect = self.font.get_rect(self.text, size = FONT_SIZE-10)
        button.center = self.text_rect.center = self.pos

        pygame.draw.rect(surface, ( , 153 if button.collidepoint(mouse) else 255), button, 0)
        self.font.render_to(surface, self.text_rect, self.text, (85, 51, 57), size = FONT_SIZE-10)
