#type: ignore

from objects import prototype
from settings import *

import pygame

class Mouse(prototype.Entity):
    def __init__(self) -> None:
        super().__init__()
    
    def draw(self):
        if pygame.mouse.get_focused():
            mousex, mousey = pygame.mouse.get_pos()
            cursor = pygame.Rect(
                int(mousex-7),
                int(mousey-7),
                15-1,15-1
            )
            pygame.draw.rect(self.game.window, (255, 153, 191, 109), cursor, 0)