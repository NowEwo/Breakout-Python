from core.context import Context

import pygame

class EventHandler(Context):
    def __init__(self) -> None:
        super().__init__()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True