#type: ignore

from objects.prototype import Entity

from core.context import GameContext

from settings import *

import pygame


class Player(Entity, GameContext):
    def __init__(self) -> None:
        super().__init__()

        self.width = PLAYER_WIDTH_MULTIPLIER * BALL_RADIUS

        self.x = (self.scene.bounds['x_min'] - self.scene.bounds['x_max']) / 2
        self.y = self.scene.bounds['y_max'] - BALL_RADIUS - 5

        self.autoplay = DEBUG_AUTOPLAY

    def collides_with_ball(self, ball):
        """Check collision with ball"""
        vertical = abs(self.y - ball.y) < 2 * BALL_RADIUS
        horizontal = abs(self.x - ball.x) < self.width / 2 + BALL_RADIUS
        return vertical and horizontal
    
    def update(self):
        x = pygame.mouse.get_pos()[0] if not self.autoplay else self.scene.ball.x
        if x - self.width / 2 < self.scene.bounds['x_min']:
            self.x = self.scene.bounds['x_min'] + self.width / 2
        elif x + self.width / 2 > self.scene.bounds['x_max']:
            self.x = self.scene.bounds['x_max'] - self.width / 2
        else:
            self.x = x
    
    def draw(self):
        rect = pygame.Rect(
            int(self.x - self.width / 2 + self.scene.offset_x),
            int(self.y - BALL_RADIUS + self.scene.offset_y),
            self.width,
            2 * BALL_RADIUS
        )
        pygame.draw.rect(self.scene.surface, self.scene.color, rect, 0)