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
                int(mousex-2),
                int(mousey-2),
                4,4
            )
            if DEBUG_PRECISE_MOUSE:
                pygame.draw.rect(self.game.window, [255,0,0], (mousex,0,1,RENDER_HEIGHT))
                pygame.draw.rect(self.game.window, [255,0,0], (0,mousey,RENDER_WIDTH,1))

            pygame.draw.rect(self.game.window, (255, 153, 191, 109), cursor, 0)