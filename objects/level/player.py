#type: ignore

from objects.prototype import Entity

from core.context import GameContext

from settings import *

import pygame


class Player(Entity, GameContext):
    def __init__(self) -> None:
        super().__init__()

        self.width = PLAYER_WIDTH_MULTIPLIER * BALL_RADIUS

        self.x = (self.game.level_scene.bounds['x_min'] - self.game.level_scene.bounds['x_max']) / 2
        self.y = self.game.level_scene.bounds['y_max'] - BALL_RADIUS - 5
    
    def update(self):
        x = pygame.mouse.get_pos()[0]
        if x - self.width / 2 < self.game.level_scene.bounds['x_min']:
            self.x = self.game.level_scene.bounds['x_min'] + self.width / 2
        elif x + self.width / 2 > self.game.level_scene.bounds['x_max']:
            self.x = self.game.level_scene.bounds['x_max'] - self.width / 2
        else:
            self.x = x
    
    def draw(self):
        rect = pygame.Rect(
            int(self.x - self.width / 2 + self.game.level_scene.offset_x),
            int(self.y - BALL_RADIUS + self.game.level_scene.offset_y),
            self.width,
            2 * BALL_RADIUS
        )
        pygame.draw.rect(self.game.level_scene.surface, self.game.level_scene.color, rect, 0)